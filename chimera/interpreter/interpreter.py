# SPDX-License-Identifier: AGPL-3.0-or-later
"""Command interpreter for the console."""

from dataclasses import dataclass
from typing import List, Optional, Callable, Dict
from chimera.interpreter.parser import CommandParser, ParsedCommand


@dataclass
class CommandResult:
    """Result of command execution."""
    output: str = ""
    success: bool = True
    new_prompt: Optional[str] = None


class CommandInterpreter:
    """Interprets and executes console commands."""

    def __init__(self):
        self.parser = CommandParser()
        self._commands: Dict[str, Callable] = {}
        self._variables: Dict[str, str] = {}
        self._history: List[str] = []
        self._plugin_mode: Optional[str] = None
        self._recording: List[str] = []

        self._register_builtins()

    def _register_builtins(self):
        """Register built-in commands."""
        self._commands["help"] = self._cmd_help
        self._commands["clear"] = self._cmd_clear
        self._commands["history"] = self._cmd_history
        self._commands["vars"] = self._cmd_vars
        self._commands["plugins"] = self._cmd_plugins
        self._commands["exit"] = self._cmd_exit
        self._commands["new"] = self._cmd_new
        self._commands["cr"] = self._cmd_cr
        self._commands["cancel"] = self._cmd_cancel
        self._commands["ui"] = self._cmd_ui
        self._commands["sys"] = self._cmd_sys
        self._commands["net"] = self._cmd_net
        self._commands["data"] = self._cmd_data
        self._commands["plugin"] = self._cmd_plugin
        self._commands["host"] = self._cmd_host
        self._commands["wait"] = self._cmd_wait
        self._commands["log"] = self._cmd_log

    def execute(self, command_str: str) -> CommandResult:
        """Execute a command string."""
        parsed = self.parser.parse(command_str)
        
        if not parsed.command:
            return CommandResult()

        self._history.append(command_str)

        if parsed.command in self._commands:
            return self._commands[parsed.command](parsed)

        return CommandResult(
            output=f"未知命令: {parsed.command}",
            success=False
        )

    def get_command_names(self) -> List[str]:
        """Get list of available command names."""
        return list(self._commands.keys())

    # Built-in commands
    def _cmd_help(self, parsed: ParsedCommand) -> CommandResult:
        help_text = """可用命令:
  help          - 显示帮助
  clear         - 清屏
  history       - 显示历史
  vars          - 显示变量
  plugins       - 列出插件
  exit          - 退出
  new <name>    - 新建插件
  cr            - 导出插件
  cancel        - 取消录制
  
扩展命令:
  ui <action>   - UI 操作
  sys <action>  - 系统操作
  net <action>  - 网络操作
  data <action> - 数据操作
  plugin <act>  - 插件操作
  host <action> - 宿主操作
  wait <ms>     - 等待
  log <msg>     - 日志"""
        return CommandResult(output=help_text)

    def _cmd_clear(self, parsed: ParsedCommand) -> CommandResult:
        return CommandResult(output="\033[2J\033[H", new_prompt=self._get_prompt())

    def _cmd_history(self, parsed: ParsedCommand) -> CommandResult:
        lines = [f"  {i+1}: {cmd}" for i, cmd in enumerate(self._history[-50:])]
        return CommandResult(output="\n".join(lines) if lines else "无历史记录")

    def _cmd_vars(self, parsed: ParsedCommand) -> CommandResult:
        if not self._variables:
            return CommandResult(output="无变量")
        lines = [f"  {k} = {v}" for k, v in self._variables.items()]
        return CommandResult(output="\n".join(lines))

    def _cmd_plugins(self, parsed: ParsedCommand) -> CommandResult:
        return CommandResult(output="插件列表功能需在宿主中使用")

    def _cmd_exit(self, parsed: ParsedCommand) -> CommandResult:
        return CommandResult(output="退出控制台")

    def _cmd_new(self, parsed: ParsedCommand) -> CommandResult:
        if not parsed.args:
            return CommandResult(output="用法: new <插件名>", success=False)
        name = parsed.args[0]
        self._plugin_mode = name
        self._recording = []
        return CommandResult(output=f"开始录制插件: {name}", new_prompt=f"[{name}] >")

    def _cmd_cr(self, parsed: ParsedCommand) -> CommandResult:
        if not self._plugin_mode:
            return CommandResult(output="请先使用 new <name> 开始录制", success=False)
        
        script = "\n".join(self._recording)
        self._recording = []
        
        return CommandResult(
            output=f"插件 {self._plugin_mode} 已导出\n脚本:\n{script}",
            new_prompt=">"
        )

    def _cmd_cancel(self, parsed: ParsedCommand) -> CommandResult:
        self._plugin_mode = None
        self._recording = []
        return CommandResult(output="已取消录制", new_prompt=">")

    def _cmd_ui(self, parsed: ParsedCommand) -> CommandResult:
        if self._plugin_mode:
            self._recording.append(f"ui {parsed.raw}")
        return CommandResult(output=f"UI: {parsed.args}")

    def _cmd_sys(self, parsed: ParsedCommand) -> CommandResult:
        if self._plugin_mode:
            self._recording.append(f"sys {parsed.raw}")
        return CommandResult(output=f"SYS: {parsed.args}")

    def _cmd_net(self, parsed: ParsedCommand) -> CommandResult:
        if self._plugin_mode:
            self._recording.append(f"net {parsed.raw}")
        return CommandResult(output=f"NET: {parsed.args}")

    def _cmd_data(self, parsed: ParsedCommand) -> CommandResult:
        if self._plugin_mode:
            self._recording.append(f"data {parsed.raw}")
        return CommandResult(output=f"DATA: {parsed.args}")

    def _cmd_plugin(self, parsed: ParsedCommand) -> CommandResult:
        return CommandResult(output=f"PLUGIN: {parsed.args}")

    def _cmd_host(self, parsed: ParsedCommand) -> CommandResult:
        return CommandResult(output=f"HOST: {parsed.args}")

    def _cmd_wait(self, parsed: ParsedCommand) -> CommandResult:
        if self._plugin_mode:
            self._recording.append(f"wait {parsed.raw}")
        return CommandResult(output=f"WAIT: {parsed.args}")

    def _cmd_log(self, parsed: ParsedCommand) -> CommandResult:
        msg = " ".join(parsed.args)
        return CommandResult(output=f"LOG: {msg}")

    def _get_prompt(self) -> str:
        if self._plugin_mode:
            return f"[{self._plugin_mode}] >"
        return ">"
