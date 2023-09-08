import os
from pathlib import Path
import shutil
import platform

# Get the home directory in a platform independent way
home = Path.home()
dir = home / '.azpype'

# Make the directory if it does not exist
dir.mkdir(parents=True, exist_ok=True)

# Get the location of the setup.py (current script directory)
setup_dir = Path(os.path.dirname(os.path.realpath(__file__)))

# Copy all files from setup/assets/config_templates to the directory
src_dir = setup_dir / 'assets' / 'config_templates'
for file_path in src_dir.glob('*'):
    if file_path.is_file():
        shutil.copy(file_path, dir)

# Copy the azcopy file to the directory
src_file = None
if platform.system() == 'Darwin':
    src_file = setup_dir / 'assets' / 'bin' / 'azcopy_darwin_amd64_10.18.1' / 'azcopy'
elif platform.system() == 'Windows':
    src_file = setup_dir / 'assets' / 'bin' / 'azcopy_windows_amd64_10.18.1' / 'azcopy.exe'
elif platform.system() == 'Linux':
    if platform.machine() == 'x86_64':
        src_file = setup_dir / 'assets' / 'bin' / 'azcopy_linux_amd64_10.18.1' / 'azcopy'
    elif platform.machine() == 'aarch64':
        src_file = setup_dir / 'assets' / 'bin' / 'azcopy_linux_arm64_10.18.1' / 'azcopy'

if src_file is not None:
    shutil.copy(src_file, dir)