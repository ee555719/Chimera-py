# SPDX-License-Identifier: AGPL-3.0-or-later
"""Main window for Chimera application."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget, QLabel,
    QFrame, QPushButton, QSplitter, QTextEdit, QLineEdit,
    QGroupBox, QCheckBox, QComboBox, QFormLayout, QScrollArea
)
from PySide6.QtCore import Qt, QSize

from chimera.host.settings import SettingsManager
from chimera.host.theme import ThemeManager
from chimera.host.plugin_manager import PluginManager
from chimera.loader.rpc import RPCServer


class PlaceholderPage(QWidget):
    """Placeholder page for unimplemented features."""

    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        layout.addWidget(title_label)

        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("font-size: 14px; color: #888888;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        layout.addStretch()


class PluginsPage(QWidget):
    """Plugins management page."""

    def __init__(self, plugin_manager: PluginManager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        layout = QVBoxLayout(self)

        title = QLabel("插件管理")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        layout.addWidget(title)

        self.plugin_list = QListWidget()
        self.plugin_list.setStyleSheet("""
            QListWidget { background-color: #252526; border: 1px solid #3c3c3c; border-radius: 4px; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #3c3c3c; }
        """)
        layout.addWidget(self.plugin_list)

        btn_layout = QHBoxLayout()
        install_btn = QPushButton("安装插件")
        install_btn.clicked.connect(self._install_plugin)
        btn_layout.addWidget(install_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self._refresh_plugins()

    def _refresh_plugins(self):
        self.plugin_list.clear()
        plugins = self.plugin_manager.get_all_plugins()
        if not plugins:
            self.plugin_list.addItem("暂无已安装插件")
        for p in plugins:
            status = "✓ 启用" if p.enabled else "✗ 禁用"
            self.plugin_list.addItem(f"[{status}] {p.name} v{p.version} - {p.description}")

    def _install_plugin(self):
        pass


class SettingsPage(QWidget):
    """Settings page."""

    def __init__(self, settings: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings = settings
        layout = QVBoxLayout(self)

        title = QLabel("设置")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0;")
        layout.addWidget(title)

        form = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.settings.theme)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        form.addRow("主题:", self.theme_combo)

        self.store_url = QLineEdit()
        self.store_url.setText(self.settings.plugin_store_url)
        self.store_url.textChanged.connect(lambda t: setattr(self.settings, 'plugin_store_url', t))
        form.addRow("插件商店 URL:", self.store_url)

        self.verify_cb = QCheckBox()
        self.verify_cb.setChecked(self.settings.get("signature_verification", True))
        self.verify_cb.stateChanged.connect(lambda s: self.settings.set("signature_verification", s == Qt.Checked))
        form.addRow("签名验证:", self.verify_cb)

        layout.addLayout(form)
        layout.addStretch()

    def _on_theme_changed(self, theme):
        self.settings.theme = theme


class ConsolePage(QWidget):
    """Console page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        from chimera.host.console import ConsoleWidget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ConsoleWidget())


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(
        self,
        settings: SettingsManager,
        theme: ThemeManager,
        plugin_manager: PluginManager,
        rpc_server: RPCServer,
    ):
        super().__init__()
        self.settings = settings
        self.theme = theme
        self.plugin_manager = plugin_manager
        self.rpc_server = rpc_server

        self.setWindowTitle("Chimera")
        self.setMinimumSize(1200, 800)

        self._setup_ui()
        self.theme.apply_theme(self)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        self.nav_list = QListWidget()
        self.nav_list.setObjectName("nav_list")
        self.nav_list.setSpacing(2)
        sidebar_layout.addWidget(self.nav_list)

        main_layout.addWidget(sidebar)

        # Content stack
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("content_stack")
        main_layout.addWidget(self.content_stack)

        self.statusBar().showMessage("就绪")

        self._setup_navigation()

    def _setup_navigation(self):
        nav_items = [
            ("🔌 插件", "plugins"),
            ("🛒 商店", "store"),
            ("🤖 AI 助手", "ai"),
            ("⌨ 快捷键", "shortcuts"),
            ("🔧 开发工具", "devtools"),
            ("🔒 安全", "security"),
            ("⚙ 设置", "settings"),
            ("💻 控制台", "console"),
        ]

        pages = {
            "plugins": PluginsPage(self.plugin_manager, self),
            "store": PlaceholderPage("插件商店", "在线浏览和安装插件"),
            "ai": PlaceholderPage("AI 助手", "智能辅助开发插件"),
            "shortcuts": PlaceholderPage("快捷键", "管理键盘快捷键"),
            "devtools": PlaceholderPage("开发工具", "插件调试和开发"),
            "security": PlaceholderPage("安全", "权限和安全管理"),
            "settings": SettingsPage(self.settings, self),
            "console": ConsolePage(self),
        }

        for i, (label, key) in enumerate(nav_items):
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, i)
            item.setSizeHint(QSize(0, 40))
            self.nav_list.addItem(item)
            self.content_stack.addWidget(pages[key])

        self.nav_list.currentRowChanged.connect(self._on_nav_changed)

        if self.nav_list.count() > 0:
            self.nav_list.setCurrentRow(0)

    def _on_nav_changed(self, row: int):
        item = self.nav_list.item(row)
        if item:
            self.content_stack.setCurrentIndex(row)
            self.statusBar().showMessage(item.text().strip())
