# MIT License
#
# Copyright (c) 2023 Clivern
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json
import subprocess
import shutil
import sys


class Venv:
    """Virtual Environment Manager"""

    def __init__(self, base_dir="~/.venvs"):
        self.base_dir = os.path.expanduser(base_dir)
        self.envs_file = os.path.join(self.base_dir, "envs.json")
        self.create_base_dir()
        self.envs = self.load_envs()

    def create_base_dir(self):
        """Create the base directory for virtual environments if it doesn't exist."""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def get_current_env_activate(self):
        """
        Get the activation script path for the virtual environment
        corresponding to the current directory name.
        """
        current_dir = os.path.basename(os.getcwd()).lower()

        if current_dir not in self.envs:
            print(f"No environment found for the current directory '{current_dir}'.")
            return None

        env_dir = self.envs[current_dir]
        activate_script = (
            os.path.join(env_dir, "Scripts", "activate")
            if os.name == "nt"
            else os.path.join(env_dir, "bin", "activate")
        )

        if not os.path.exists(activate_script):
            print(f"Activation script not found for environment '{current_dir}'.")
            return None

        return print(activate_script)

    def load_envs(self):
        """Load environments from a JSON file."""
        if os.path.exists(self.envs_file):
            with open(self.envs_file, "r") as f:
                return json.load(f)
        return {}

    def save_envs(self):
        """Save environments to a JSON file."""
        with open(self.envs_file, "w") as f:
            json.dump(self.envs, f)

    def create_env(self, name):
        """Create a new virtual environment."""
        if name in self.envs:
            print(f"Environment '{name}' already exists.")
            return

        env_dir = os.path.join(self.base_dir, name)
        subprocess.run([sys.executable, "-m", "venv", env_dir])
        self.envs[name] = env_dir
        self.save_envs()
        print(f"Environment '{name}' created at {env_dir}.")

    def activate_env(self, name):
        """Provide instructions to activate an existing virtual environment."""
        if name not in self.envs:
            print(f"Environment '{name}' does not exist.")
            return

        env_dir = self.envs[name]
        activate_script = (
            os.path.join(env_dir, "Scripts", "activate")
            if os.name == "nt"
            else os.path.join(env_dir, "bin", "activate")
        )

        print(f"To activate the environment '{name}', run:")
        print(f"source {activate_script}" if os.name != "nt" else f"{activate_script}")

    def list_envs(self):
        """List all available virtual environments."""
        if not self.envs:
            print("No virtual environments found.")
            return

        print("Available virtual environments:")
        for name in self.envs.keys():
            print(f"- {name}")

    def remove_env(self, name):
        """Remove a virtual environment by deleting its directory and removing it from the config."""
        if name not in self.envs:
            print(f"Environment '{name}' does not exist.")
            return

        # Remove the directory
        env_dir = self.envs[name]
        shutil.rmtree(env_dir)

        # Remove from the config
        del self.envs[name]
        self.save_envs()

        print(f"Environment '{name}' has been removed.")

    def get_env_info(self, name):
        """Get information about how to activate a specified virtual environment."""
        if name not in self.envs:
            print(f"Environment '{name}' does not exist.")
            return

        env_dir = self.envs[name]
        activate_script = (
            os.path.join(env_dir, "Scripts", "activate")
            if os.name == "nt"
            else os.path.join(env_dir, "bin", "activate")
        )

        print(f"Information for environment '{name}':")
        print(
            f"- Activation command: {'source ' + activate_script if os.name != 'nt' else activate_script}"
        )
