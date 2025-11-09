"""
SpawnLabs CLI
Main command-line interface for SpawnLabs tools
"""

import sys
import argparse
from .ui import spawn_ui


def print_banner():
    """Print SpawnLabs banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗██████╗  █████╗ ██╗    ██╗███╗   ██╗          ║
║   ██╔════╝██╔══██╗██╔══██╗██║    ██║████╗  ██║          ║
║   ███████╗██████╔╝███████║██║ █╗ ██║██╔██╗ ██║          ║
║   ╚════██║██╔═══╝ ██╔══██║██║███╗██║██║╚██╗██║          ║
║   ███████║██║     ██║  ██║╚███╔███╔╝██║ ╚████║          ║
║   ╚══════╝╚═╝     ╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═══╝          ║
║                                                           ║
║   Intelligent Platform for Autonomous Systems            ║
║   Build • Run • Maintain                                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def ui_command(args):
    """Handle 'spawn ui' command"""
    success = spawn_ui(target_dir=args.dir)
    return 0 if success else 1


def main():
    """Main CLI entry point for 'spawn' command"""
    parser = argparse.ArgumentParser(
        prog='spawn',
        description='SpawnLabs - Intelligent platform for building, running, and maintaining autonomous systems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  ui          Clone and setup the Spawn UI frontend

Examples:
  spawn ui                          # Clone UI to 'frontend' directory
  spawn ui --dir my-app             # Clone UI to custom directory
  spawn --version                   # Show version
  spawn --help                      # Show this help message

For more information, visit: https://spawnlabs.ai
        """
    )
    
    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version=f"SpawnLabs v{__import__('spawnlabs').__version__}"
    )
    
    # Create subparsers for subcommands
    subparsers = parser.add_subparsers(
        title='available commands',
        dest='command',
        help='command to run'
    )
    
    # UI subcommand
    ui_parser = subparsers.add_parser(
        'ui',
        help='Clone and setup the Spawn UI frontend',
        description='Clone the Spawn UI frontend template to start building',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  spawn ui                          # Clone to 'frontend' directory
  spawn ui --dir my-app             # Clone to 'my-app' directory
  spawn ui --dir ./custom-path      # Clone to custom path
        """
    )
    ui_parser.add_argument(
        '--dir',
        '-d',
        default='frontend',
        help='Target directory for the frontend (default: frontend)'
    )
    ui_parser.set_defaults(func=ui_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command specified, show banner and help
    if not hasattr(args, 'func'):
        print_banner()
        parser.print_help()
        return 0
    
    # Execute the command
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())

