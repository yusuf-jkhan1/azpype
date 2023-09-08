# import requests
# from pathlib import Path
# import platform
# import traceback
# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# def download_file(url, target_path):
#     response = requests.get(url, stream=True, verify=False)
#     response.raise_for_status()
#     with open(target_path, 'wb') as file:
#         for chunk in response.iter_content(chunk_size=8192): 
#             file.write(chunk)

# # def main():
# print("Post-install Script Starting ...")
# try:
#     home = Path.home()
#     dir = home / '.azpype'
#     dir.mkdir(parents=True, exist_ok=True)
#     print("Azpype directory created at: ", dir)

#     config_template_base_url = "https://github.com/yusuf-jkhan1/azpype/blob/main/setup/assets/config_templates"
#     config_template_files = ["copy_config.yaml"]  # Add more when/if needed

#     for config_file in config_template_files:
#         download_file(f"{config_template_base_url}/{config_file}?raw=true", dir / config_file)

#     binary_base_url = "https://github.com/yusuf-jkhan1/azpype/blob/main/setup/assets/bin"
#     binary_name = None

#     if platform.system() == 'Darwin':
#         binary_name = 'azcopy_darwin_amd64_10.18.1/azcopy'
#     elif platform.system() == 'Windows':
#         binary_name = 'azcopy_windows_amd64_10.18.1/azcopy.exe'
#     elif platform.system() == 'Linux':
#         if platform.machine() == 'x86_64':
#             binary_name = 'azcopy_linux_amd64_10.18.1/azcopy'
#         elif platform.machine() == 'aarch64':
#             binary_name = 'azcopy_linux_arm64_10.18.1/azcopy'
    
#     print("Detected Platform: ", platform.system())
#     if binary_name:
#         print(f"Downloading AzCopy binary: {binary_name}")
#         download_file(f"{binary_base_url}/{binary_name}?raw=true", dir / binary_name.split('/')[-1])

# except Exception as e:
#     print(f"An error occurred: {e}")
#     traceback.print_exc()

# if __name__ == "__main__":
#     main()

import os
from pathlib import Path
import shutil
import platform

home = Path.home()
dir = home / '.azpype'

dir.mkdir(parents=True, exist_ok=True)

setup_dir = Path(os.path.dirname(os.path.realpath(__file__)))

src_dir = setup_dir / 'assets' / 'config_templates'
for file_path in src_dir.glob('*'):
    if file_path.is_file():
        shutil.copy(file_path, dir)

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
