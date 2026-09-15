# SPDX-License-Identifier: AGPL-3.0-or-later
"""Command-line interface for Chimera."""

import argparse
import sys
from pathlib import Path

from chimera import __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="chimera",
        description="Chimera - Plugin-based desktop host application"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run Chimera application")
    run_parser.add_argument("--portable", action="store_true", help="Run in portable mode")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build standalone executable")
    build_parser.add_argument("--name", required=True, help="Output executable name")
    build_parser.add_argument("--plugins", nargs="*", help="Plugin directories to include")
    
    # Plugin commands
    plugin_parser = subparsers.add_parser("plugin", help="Plugin management")
    plugin_sub = plugin_parser.add_subparsers(dest="plugin_action")
    
    install_parser = plugin_sub.add_parser("install", help="Install a plugin")
    install_parser.add_argument("zip_file", help="Plugin ZIP file path")
    
    plugin_sub.add_parser("list", help="List installed plugins")
    
    args = parser.parse_args()
    
    if args.command == "run":
        from chimera.app import main as run_app
        if args.portable:
            import os
            os.environ["CHIMERA_PORTABLE"] = str(Path.cwd())
        run_app()
        
    elif args.command == "build":
        from chimera.packager.builder import PyInstallerBuilder, BuildConfig
        config = BuildConfig(
            name=args.name,
            plugins=[Path(p) for p in (args.plugins or [])],
        )
        builder = PyInstallerBuilder()
        result = builder.build(config, Path("dist"))
        if result:
            print(f"Build successful: {result}")
        else:
            print("Build failed")
            sys.exit(1)
            
    elif args.command == "plugin":
        from chimera.host.plugin_manager import PluginManager
        plugins_dir = Path("D:/ChimeraPlugin")
        pm = PluginManager(plugins_dir)
        
        if args.plugin_action == "install":
            from pathlib import Path
            success = pm.install_plugin(Path(args.zip_file))
            if success:
                print("Plugin installed successfully")
            else:
                print("Failed to install plugin")
                sys.exit(1)
                
        elif args.plugin_action == "list":
            plugins = pm.get_all_plugins()
            if not plugins:
                print("No plugins installed")
            else:
                for p in plugins:
                    status = "✓" if p.enabled else "✗"
                    print(f"  [{status}] {p.name} v{p.version}")
                    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
