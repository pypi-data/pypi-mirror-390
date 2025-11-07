from importlib.resources import files
from pathlib import Path

__version__ = "0.1.4"

def data_root() -> Path:
    return Path(files("conformal_clip_data") / "data")

def textile_simulated_root() -> Path:
    return data_root() / "textile_images" / "simulated"

def nominal_dir() -> Path:
    return textile_simulated_root() / "nominal"

def local_dir() -> Path:
    return textile_simulated_root() / "local"

def global_dir() -> Path:
    return textile_simulated_root() / "global"
