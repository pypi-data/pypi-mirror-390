import subprocess
import sys
import os
from importlib import resources

def main():
    # Locate the embedded shell script
    with resources.path("robbiejr_sc", "robbiejr.sh") as script_path:
        # Ensure it's executable
        os.chmod(script_path, 0o755)
        # Run it and pass any arguments (like --hosts etc)
        subprocess.run(["bash", str(script_path), *sys.argv[1:]])
