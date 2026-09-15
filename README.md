# Chimera / 奇美拉

[English](#english) | [中文](#中文)

---

## English

A plugin-based Windows desktop host application built with Python + PySide6.

### Features
- 🔌 Plugin management - install, uninstall, enable, disable plugins
- 🎨 Theme system - dark/light theme switching
- 📝 Command console - execute commands, record plugins
- 🛒 Plugin store - online plugin installation
- 🔧 Developer tools - plugin debugging
- 🤖 AI assistant - intelligent plugin development
- 📦 Packager - package config into standalone exe

### Installation

**Option 1: Installer (Recommended)**
1. Download `ChimeraInstaller.exe`
2. Run the installer
3. Choose installation directory
4. Check "Auto download Python" if Python is not installed
5. Click Install

**Option 2: Manual**
```bash
git clone https://github.com/ee555719/Chimera-py.git
cd Chimera-py
pip install -r requirements.txt
python -m chimera.app
```

### Requirements
- Python 3.12+ (64-bit)
- Windows 10 (1809+) / Windows 11

### Plugin Development
```bash
cp -r templates/python-plugin my_plugin
# Edit plugin.json and main.py
# Package as ZIP and install
```

### License
AGPL-3.0-or-later

---

## 中文

基于插件的 Windows 桌面宿主应用程序，使用 Python + PySide6 构建。

### 功能
- 🔌 插件管理 - 安装、卸载、启用、禁用插件
- 🎨 主题系统 - 深色/浅色主题切换
- 📝 命令控制台 - 执行命令、录制插件
- 🛒 插件商店 - 在线安装插件
- 🔧 开发工具 - 插件调试和开发
- 🤖 AI 助手 - 智能辅助开发插件
- 📦 打包器 - 将配置打包成独立 exe

### 安装

**方式一：安装程序（推荐）**
1. 下载 `ChimeraInstaller.exe`
2. 运行安装程序
3. 选择安装目录
4. 如未安装 Python，勾选"自动下载 Python"
5. 点击安装

**方式二：手动安装**
```bash
git clone https://github.com/ee555719/Chimera-py.git
cd Chimera-py
pip install -r requirements.txt
python -m chimera.app
```

### 系统要求
- Python 3.12+ (64位)
- Windows 10 (1809+) / Windows 11

### 插件开发
```bash
cp -r templates/python-plugin my_plugin
# 编辑 plugin.json 和 main.py
# 打包为 ZIP 并安装
```

### 许可证
AGPL-3.0-or-later
