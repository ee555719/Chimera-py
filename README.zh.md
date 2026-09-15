# Chimera

一个基于插件的 Windows 桌面宿主应用程序。

## 功能

- 🔌 插件管理 - 安装、卸载、启用、禁用插件
- 🎨 主题系统 - 深色/浅色主题切换
- 📝 命令控制台 - 执行命令、录制插件
- 🛒 插件商店 - 在线安装插件
- 🔧 开发工具 - 调试和开发插件
- 🤖 AI 助手 - 智能辅助开发
- 📦 打包器 - 将配置打包成独立 exe

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
# 运行应用
python -m chimera.app

# 或使用命令行
chimera run

# 安装插件
chimera plugin install plugin.zip

# 列出插件
chimera plugin list

# 构建独立 exe
chimera build --name MyApp
```

## 插件开发

1. 使用模板创建插件:
   ```bash
   cp -r templates/python-plugin my_plugin
   ```

2. 编辑 `plugin.json` 和 `main.py`

3. 打包为 ZIP 文件

4. 安装到 Chimera

## 许可证

AGPL-3.0-or-later
