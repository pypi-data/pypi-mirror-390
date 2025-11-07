import os
from pathlib import Path


def get_pretrained_folder() -> Path:
    pretrained_path = Path("/mnt/ssd1/pretrained")
    # if os.environ.get("PRETRAINED_ROOT"):
    #     pretrained_path = Path(os.environ["PRETRAINED_ROOT"])
    # else:
    #     raise ValueError("PRETRAINED_ROOT is not set")
    if pretrained_path.is_dir():
        return pretrained_path
    else:
        raise ValueError(f"PRETRAINED_ROOT is not a directory: {pretrained_path}")


def get_pretrained_ckpt_folder(model_name) -> Path:
    pretrained_folder = get_pretrained_folder()
    return pretrained_folder.joinpath(f"checkpoints/{model_name}/pretrained")


def get_ckpt_path(model_name, ckpt_version) -> Path:
    return get_pretrained_ckpt_folder(model_name).joinpath(f"{ckpt_version}.ckpt")
