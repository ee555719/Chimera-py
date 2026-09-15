# SPDX-License-Identifier: AGPL-3.0-or-later
"""Compiler for converting recorded commands to plugin scripts."""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class CompiledPlugin:
    """Compiled plugin output."""
    main_py: str
    plugin_json: str
    library_txt: Optional[str] = None


class PluginCompiler:
    """Compiles recorded commands into a plugin package."""

    PLUGIN_TEMPLATE = '''# SPDX-License-Identifier: AGPL-3.0-or-later
"""Plugin: {name}"""

import sys
import json
from pathlib import Path

def main():
    """Plugin entry point."""
    print(json.dumps({{
        "jsonrpc": "2.0",
        "method": "plugin.ready",
        "params": {{"id": "{name}"}},
        "id": 1
    }}))
    sys.stdout.flush()
    
    # Plugin logic here
    {commands}

if __name__ == "__main__":
    main()
'''

    MANIFEST_TEMPLATE = '''{{
  "id": "{name}",
  "name": "{name}",
  "version": "0.1.0",
  "description": "A generated plugin",
  "author": "Chimera",
  "enabled": true,
  "permissions": []
}}'''

    def compile(self, name: str, commands: List[str]) -> CompiledPlugin:
        """Compile recorded commands into a plugin."""
        # Convert commands to Python code
        python_commands = self._commands_to_python(commands)
        
        main_py = self.PLUGIN_TEMPLATE.format(
            name=name,
            commands=python_commands
        )
        
        plugin_json = self.MANIFEST_TEMPLATE.format(name=name)
        
        return CompiledPlugin(
            main_py=main_py,
            plugin_json=plugin_json
        )

    def _commands_to_python(self, commands: List[str]) -> str:
        """Convert command strings to Python code."""
        lines = []
        for cmd in commands:
            parts = cmd.split()
            if not parts:
                continue
                
            action = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            if action == "ui":
                lines.append(f'    sdk.show_message("提示", "{" ".join(args)}")')
            elif action == "sys":
                lines.append(f'    sdk.run_command("{" ".join(args)}")')
            elif action == "net":
                lines.append(f'    sdk.http_get("{" ".join(args)}")')
            elif action == "data":
                lines.append(f'    sdk.write_file("data.txt", "{" ".join(args)}")')
            elif action == "wait":
                ms = args[0] if args else "1000"
                lines.append(f'    import time; time.sleep({ms}/1000)')
            elif action == "log":
                lines.append(f'    print("LOG: {" ".join(args)}")')
            else:
                lines.append(f'    # {cmd}')
                
        return "\n".join(lines) if lines else "pass"
