# SPDX-License-Identifier: AGPL-3.0-or-later
"""Chimera Installer - Downloads Python and installs Chimera."""

import os
import sys
import json
import zipfile
import shutil
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QProgressBar,
    QTextEdit, QGroupBox, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont


PYTHON_VERSION = "3.12.7"
PYTHON_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-amd64.exe"
CHIMERA_SOURCE = Path(__file__).parent.parent


class DownloadThread(QThread):
    """Thread for downloading files."""
    progress = Signal(int, str)
    finished = Signal(bool, str)

    def __init__(self, url: str, output: Path):
        super().__init__()
        self.url = url
        self.output = output

    def run(self):
        try:
            import urllib.request
            self.progress.emit(0, f"下载中: {self.url}")

            def reporthook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, int(block_num * block_size * 100 / total_size))
                    self.progress.emit(percent, f"下载中... {percent}%")

            urllib.request.urlretrieve(self.url, str(self.output), reporthook)
            self.finished.emit(True, str(self.output))
        except Exception as e:
            self.finished.emit(False, str(e))


class InstallerWindow(QMainWindow):
    """Installer window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chimera 安装程序")
        self.setMinimumSize(600, 500)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Chimera 安装程序")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #0078d4;")
        layout.addWidget(title)

        subtitle = QLabel("插件化桌面宿主应用程序")
        subtitle.setStyleSheet("font-size: 14px; color: #666666;")
        layout.addWidget(subtitle)

        # Install location
        group = QGroupBox("安装设置")
        group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #cccccc; border-radius: 4px; padding: 10px; }")
        group_layout = QVBoxLayout(group)

        loc_layout = QHBoxLayout()
        loc_label = QLabel("安装位置:")
        self.install_path = QLineEdit(str(Path("D:/Chimera")))
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._browse_folder)
        loc_layout.addWidget(loc_label)
        loc_layout.addWidget(self.install_path)
        loc_layout.addWidget(browse_btn)
        group_layout.addLayout(loc_layout)

        self.download_python_cb = QCheckBox("自动下载 Python (如果未安装)")
        self.download_python_cb.setChecked(True)
        group_layout.addWidget(self.download_python_cb)

        self.create_shortcut_cb = QCheckBox("创建桌面快捷方式")
        self.create_shortcut_cb.setChecked(True)
        group_layout.addWidget(self.create_shortcut_cb)

        layout.addWidget(group)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("准备安装")
        self.status_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.status_label)

        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(150)
        self.log.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0; font-family: Consolas;")
        layout.addWidget(self.log)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.install_btn = QPushButton("安装")
        self.install_btn.setMinimumWidth(120)
        self.install_btn.setStyleSheet("background-color: #0078d4; color: white; padding: 10px 20px;")
        self.install_btn.clicked.connect(self._start_install)
        btn_layout.addWidget(self.install_btn)

        layout.addLayout(btn_layout)

        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QGroupBox { background-color: white; }
            QLineEdit { padding: 8px; border: 1px solid #cccccc; border-radius: 4px; }
            QPushButton { padding: 8px 16px; border: 1px solid #cccccc; border-radius: 4px; }
            QPushButton:hover { background-color: #e0e0e0; }
        """)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择安装位置", self.install_path.text())
        if folder:
            self.install_path.setText(folder)

    def _log(self, msg: str):
        self.log.append(msg)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def _start_install(self):
        self.install_btn.setEnabled(False)
        self._log("开始安装...")

        install_dir = Path(self.install_path.text())
        install_dir.mkdir(parents=True, exist_ok=True)

        self._log(f"安装目录: {install_dir}")

        # Copy files
        self.status_label.setText("复制文件...")
        self.progress_bar.setValue(10)
        self._log("复制 Chimera 文件...")

        dest_chimera = install_dir / "Chimera-py"
        if dest_chimera.exists():
            shutil.rmtree(dest_chimera)
        shutil.copytree(str(CHIMERA_SOURCE), str(dest_chimera), ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"))
        self.progress_bar.setValue(30)

        # Download Python
        if self.download_python_cb.isChecked():
            self._download_python(install_dir)
        else:
            self._finish_install(install_dir)

    def _download_python(self, install_dir: Path):
        self.status_label.setText("检查 Python...")
        self._log("检查 Python 是否已安装...")

        python_dir = install_dir / "python"
        python_exe = python_dir / "python.exe"

        if python_exe.exists():
            self._log("Python 已存在，跳过下载")
            self._finish_install(install_dir)
            return

        self.status_label.setText("下载 Python...")
        self._log(f"下载 Python {PYTHON_VERSION}...")

        installer_path = install_dir / "python_installer.exe"
        self.downloader = DownloadThread(PYTHON_URL, installer_path)
        self.downloader.progress.connect(self._on_download_progress)
        self.downloader.finished.connect(lambda ok, msg: self._on_python_downloaded(ok, msg, install_dir, installer_path))
        self.downloader.start()

    def _on_download_progress(self, percent: int, msg: str):
        self.progress_bar.setValue(30 + int(percent * 0.4))
        self.status_label.setText(msg)
        self._log(msg)

    def _on_python_downloaded(self, ok: bool, msg: str, install_dir: Path, installer_path: Path):
        if not ok:
            self._log(f"下载失败: {msg}")
            self._finish_install(install_dir)
            return

        self._log("安装 Python...")
        self.status_label.setText("安装 Python...")

        python_dir = install_dir / "python"
        try:
            subprocess.run([
                str(installer_path),
                "/quiet",
                f"TargetDir={python_dir}",
                "Include_launcher=0",
                "Include_test=0",
                "PrependPath=0",
            ], check=True, capture_output=True)
            self._log("Python 安装成功")
            installer_path.unlink(missing_ok=True)
        except Exception as e:
            self._log(f"Python 安装失败: {e}")

        self._finish_install(install_dir)

    def _finish_install(self, install_dir: Path):
        self.progress_bar.setValue(100)
        self.status_label.setText("安装完成!")
        self._log("安装完成!")
        self._log(f"安装位置: {install_dir}")
        self._log("")
        self._log("启动方式:")
        self._log(f"  {install_dir}\\Chimera-py\\run.bat")

        # Create run.bat
        bat_path = install_dir / "Chimera-py" / "run.bat"
        python_exe = install_dir / "python" / "python.exe"
        if not python_exe.exists():
            python_exe = "python"

        bat_content = f'@echo off\n"{python_exe}" -m chimera.app\n'
        bat_path.write_text(bat_content, encoding="utf-8")
        self._log(f"已创建启动脚本: {bat_path}")

        # Create desktop shortcut
        if self.create_shortcut_cb.isChecked():
            self._create_shortcut(install_dir)

        self.install_btn.setEnabled(True)
        self.install_btn.setText("完成")

    def _create_shortcut(self, install_dir: Path):
        try:
            desktop = Path(os.path.expanduser("~/Desktop"))
            shortcut_path = desktop / "Chimera.lnk"

            bat_path = install_dir / "Chimera-py" / "run.bat"

            # Create shortcut using PowerShell
            ps_cmd = f'''
            $ws = New-Object -ComObject WScript.Shell
            $shortcut = $ws.CreateShortcut("{shortcut_path}")
            $shortcut.TargetPath = "{bat_path}"
            $shortcut.WorkingDirectory = "{install_dir / 'Chimera-py'}"
            $shortcut.Description = "Chimera - Plugin-based desktop host"
            $shortcut.Save()
            '''
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
            self._log(f"已创建桌面快捷方式: {shortcut_path}")
        except Exception as e:
            self._log(f"创建快捷方式失败: {e}")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = InstallerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
