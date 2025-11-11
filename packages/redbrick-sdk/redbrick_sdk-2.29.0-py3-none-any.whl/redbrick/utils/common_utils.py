"""Common utility functions."""

import os
import shutil
import hashlib
import json
from typing import List, Optional, Union, Dict

from redbrick.types import task as TaskType


def config_path() -> str:
    """Return package config path."""
    if (
        "VIRTUAL_ENV" in os.environ
        and os.environ["VIRTUAL_ENV"]
        and (conf_dir := os.path.expanduser(os.environ["VIRTUAL_ENV"]))
        and os.path.isdir(conf_dir)
    ):
        return os.path.join(conf_dir, ".redbrickai")

    return os.path.join(os.path.expanduser("~"), ".redbrickai")


def config_migration() -> None:
    """Migrate config to appropriate path (Temporary)."""
    home_dir = os.path.join(os.path.expanduser("~"), ".redbrickai")
    conf_dir = config_path()
    if home_dir != conf_dir and not os.path.isdir(conf_dir) and os.path.isdir(home_dir):
        shutil.copytree(home_dir, conf_dir)


def hash_sha256(message: Union[str, bytes]) -> str:
    """Return basic SHA256 of given message."""
    sha256 = hashlib.sha256()
    sha256.update(message.encode() if isinstance(message, str) else message)
    return sha256.hexdigest()


def get_color(
    color_hex: Optional[str] = None, class_id: Optional[int] = None
) -> List[int]:
    """Get a color from color_hex or class id."""
    if color_hex:
        color_hex = color_hex.lstrip("#")
        if len(color_hex) == 3:
            color_hex = f"{color_hex[0]}{color_hex[0]}{color_hex[1]}{color_hex[1]}{color_hex[2]}{color_hex[2]}"
        return [int(color_hex[i : i + 2], 16) for i in (0, 2, 4)]

    num = (374761397 + int(class_id or 0) * 3266489917) & 0xFFFFFFFF
    num = ((num ^ num >> 15) * 2246822519) & 0xFFFFFFFF
    num = ((num ^ num >> 13) * 3266489917) & 0xFFFFFFFF
    num = (num ^ num >> 16) >> 8
    return list(num.to_bytes(3, "big"))


def series_image_headers(series_info: Dict) -> Optional[TaskType.ImageHeaders]:
    """Get series image headers from series info."""
    # pylint: disable=import-outside-toplevel

    import numpy as np  # type: ignore

    data_type = series_info.get("dataType")
    series_headers = series_info.get("imageHeaders")

    img_headers = (
        json.loads(series_headers)
        if isinstance(series_headers, str)
        else series_headers
    )

    if not img_headers:
        return None

    headers: TaskType.ImageHeaders = {"dimensions": img_headers.get("dimensions")}

    if not data_type or data_type not in ("web", "report"):
        headers["spacing"] = img_headers.get("spacing")
        headers["origin"] = img_headers.get("origin")
        if isinstance(img_headers.get("direction"), list):
            headers["direction"] = (
                np.array(img_headers["direction"]).reshape((3, 3)).tolist()
            )

    if (
        isinstance(img_headers.get("totalFrames"), int)
        and img_headers["totalFrames"] > 1
    ):
        headers["totalFrames"] = img_headers["totalFrames"]

    try:
        if (
            (spacing := headers.get("spacing"))
            and (origin := headers.get("origin"))
            and (direction := headers.get("direction"))
        ):
            affine = np.eye(4)
            affine[:3, :3] = np.array(direction) * np.array(spacing)
            affine[:3, 3] = np.array(origin)
            headers["affine"] = affine.tolist()
    except Exception:  # pylint: disable=broad-except
        pass

    return headers
