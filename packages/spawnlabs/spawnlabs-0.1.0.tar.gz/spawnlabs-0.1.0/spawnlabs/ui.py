"""
SpawnLabs UI Module
Handles cloning and setting up the Spawn frontend
"""

import subprocess
from pathlib import Path


def spawn_ui(target_dir="frontend", repo_url="https://github.com/teddyoweh/spawn-frontend-temp"):
    """
    Clone the Spawn UI frontend repository into a specified directory.
    
    Args:
        target_dir (str): Directory name where the frontend will be cloned. Defaults to 'frontend'.
        repo_url (str): Repository URL to clone. Defaults to the Spawn frontend template.
    
    Returns:
        bool: True if successful, False otherwise
    
    Example:
        >>> from spawnlabs import spawn_ui
        >>> spawn_ui()
        >>> spawn_ui(target_dir="my-frontend")
    """
    try:
        # Convert to absolute path
        target_path = Path(target_dir).absolute()
        
        # Check if directory already exists
        if target_path.exists():
            print(f"❌ Error: Directory '{target_dir}' already exists!")
            print("   Please choose a different directory name or remove the existing one.")
            return False
        
        print("🚀 SpawnLabs - Cloning frontend UI...")
        print(f"📦 Repository: {repo_url}")
        print(f"📁 Target directory: {target_path}")
        print()
        
        # Clone the repository
        subprocess.run(
            ["git", "clone", repo_url, str(target_path)],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✅ Successfully cloned Spawn UI to '{target_dir}'!")
        print()
        print("📝 Next steps:")
        print(f"   1. cd {target_dir}")
        print("   2. Install dependencies (npm install or yarn)")
        print("   3. Start the development server")
        print()
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error cloning repository: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Error: Git is not installed or not in PATH")
        print("   Please install Git: https://git-scm.com/downloads")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

