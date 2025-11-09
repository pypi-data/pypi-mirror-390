# SpawnLabs 🚀

**Intelligent platform for building, running, and maintaining autonomous systems**

SpawnLabs is designed to build, run, and autonomously maintain live systems, software, and tools - from personal projects to enterprise operations.

[![PyPI version](https://badge.fury.io/py/spawnlabs.svg)](https://badge.fury.io/py/spawnlabs)
[![Python Support](https://img.shields.io/pypi/pyversions/spawnlabs.svg)](https://pypi.org/project/spawnlabs/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install spawnlabs
```

## Quick Start

The fastest way to get started with SpawnLabs:

```bash
# Clone the Spawn UI frontend
spawn ui

# Or specify a custom directory
spawn ui --dir my-project
```

That's it! Your frontend is ready to go. 🎉

## CLI Commands

### `spawn ui`

Clone and set up the Spawn UI frontend template for rapid development.

```bash
# Basic usage - creates 'frontend' directory
spawn ui

# Custom directory
spawn ui --dir my-app

# Custom path
spawn ui --dir ./path/to/project
```

**What you get:**
- ✅ Complete frontend template
- ✅ Pre-configured build setup
- ✅ Best practices and folder structure
- ✅ Ready-to-customize components

### `spawn --version`

Check your SpawnLabs version:

```bash
spawn --version
```

### `spawn --help`

Get help and see all available commands:

```bash
spawn --help
```

## Python API

You can also use SpawnLabs directly in your Python code:

```python
from spawnlabs import spawn_ui

# Clone to default 'frontend' directory
spawn_ui()

# Clone to a custom directory
spawn_ui(target_dir="my-awesome-frontend")

# Clone from a custom repository
spawn_ui(
    target_dir="frontend",
    repo_url="https://github.com/your-org/your-repo"
)
```

## Complete Workflow Example

Here's a complete example of starting a new project:

```bash
# 1. Install SpawnLabs
pip install spawnlabs

# 2. Create your frontend
spawn ui --dir my-project

# 3. Navigate to your project
cd my-project

# 4. Install dependencies
npm install

# 5. Start developing
npm start
```

## Requirements

- **Python 3.7+** - For running SpawnLabs CLI and tools
- **Git** - For cloning repositories (install from [git-scm.com](https://git-scm.com/downloads))

## CLI Reference

```
usage: spawn [-h] [--version] {ui} ...

SpawnLabs - Intelligent platform for building, running, and maintaining
autonomous systems

options:
  -h, --help     show this help message and exit
  --version, -v  show program's version number and exit

available commands:
  {ui}           command to run
    ui           Clone and setup the Spawn UI frontend

Commands:
  ui          Clone and setup the Spawn UI frontend

Examples:
  spawn ui                          # Clone UI to 'frontend' directory
  spawn ui --dir my-app             # Clone UI to custom directory
  spawn --version                   # Show version
  spawn --help                      # Show this help message

For more information, visit: https://spawnlabs.ai
```

## What is SpawnLabs?

SpawnLabs is an **intelligent platform** that enables you to:

- **Build** - Create live systems and tools with modern templates and frameworks
- **Run** - Execute and deploy your applications seamlessly
- **Maintain** - Autonomously manage and maintain your systems

Whether you're working on personal tools or enterprise operations, SpawnLabs provides the infrastructure and tools you need to succeed.

## Features

### Current Features

- ✅ **Spawn UI** - Instantly clone and set up frontend templates
- ✅ **Python API** - Programmatic access to all SpawnLabs features
- ✅ **CLI Tools** - Powerful command-line interface for developers
- ✅ **Zero Config** - Works out of the box with sensible defaults

### Coming Soon

- 🔄 AI-powered component generation
- 🔄 Custom template management
- 🔄 Deployment automation
- 🔄 Integration with popular frameworks
- 🔄 Autonomous system maintenance

## Support & Community

- 🌐 **Website**: [spawnlabs.ai](https://spawnlabs.ai)
- 📧 **Email**: contact@spawnlabs.ai
- 🐛 **Issues**: [GitHub Issues](https://github.com/teddyoweh/spawn-frontend-temp/issues)
- 📖 **Documentation**: [spawnlabs.ai/docs](https://spawnlabs.ai/docs)

## Development

Want to contribute to SpawnLabs?

```bash
# Clone the repository
git clone https://github.com/teddyoweh/spawn-frontend-temp.git
cd spawn-frontend-temp

# Install in development mode
pip install -e .

# Test the CLI
spawn ui --version
```

## License

MIT License - see [LICENSE](LICENSE) file for details

## About

SpawnLabs is built to accelerate development with intelligent tools and autonomous systems. Our mission is to make building, running, and maintaining software systems effortless.

**Start building faster, ship better products.** ⚡

---

Made with ❤️ by the [SpawnLabs](https://spawnlabs.ai) team
