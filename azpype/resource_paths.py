from pathlib import Path
import platform
import stat


def _assets_root() -> Path:
    pkg_dir = Path(__file__).resolve().parent
    return pkg_dir / 'assets'


def get_azcopy_path() -> str:
    system = platform.system()
    machine = platform.machine()
    base = _assets_root() / 'bin'
    if system == 'Darwin':
        path = base / 'azcopy_darwin_amd64_10.18.1' / 'azcopy'
    elif system == 'Windows':
        path = base / 'azcopy_windows_amd64_10.18.1' / 'azcopy.exe'
    elif system == 'Linux':
        if machine == 'x86_64':
            path = base / 'azcopy_linux_amd64_10.18.1' / 'azcopy'
        elif machine == 'aarch64':
            path = base / 'azcopy_linux_arm64_10.18.1' / 'azcopy'
        else:
            raise RuntimeError(f'Unsupported Linux architecture: {machine}')
    else:
        raise RuntimeError(f'Unsupported platform: {system}')

    if system != 'Windows':
        try:
            mode = path.stat().st_mode
            path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except FileNotFoundError:
            pass
    return str(path)


def ensure_user_config() -> Path:
    src = _assets_root() / 'config_templates' / 'copy_config.yaml'
    dst_dir = Path.home() / '.azpype'
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / 'copy_config.yaml'
    if not dst.exists() and src.exists():
        dst.write_bytes(src.read_bytes())
    return dst
