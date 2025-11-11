import logging
import shutil
import subprocess
import typing
import os

from modelcar_base_image.constants import EMBEDDED_OCI_LAYOUT_DIR
from pathlib import Path


logger = logging.getLogger(__name__)


def copy_base_image_to_oci_layout(base_image: str, dest: typing.Union[str, os.PathLike]):
    """
    Copy a base image to OCI layout using skopeo.
    
    Args:
        base_image: The source base image reference
        dest: The destination OCI layout directory
    
    Returns:
        The result of the subprocess.run call
    """
    if isinstance(dest, os.PathLike):
        dest = str(dest)
    return subprocess.run(["skopeo", "copy", "--multi-arch", "all", "docker://"+base_image, "oci:"+dest+":latest"], check=True)


def embedded_oci_layout(
    target_path: typing.Union[str, os.PathLike]
) -> None:
    """
    Create an oci-layout from the embedded modelcar base image.
    The embedded modelcar base image is sourced from the ODH_MODELCAR_BASE_IMAGE constant.
    
    Args:
        typing.Union[str, os.PathLike]: Directory where the oci-layout will be created
    """
    import modelcar_base_image
    package_root = Path(modelcar_base_image.__file__).parent  # modelcar_base_image/ directory in installed package
    embedded_path = package_root / EMBEDDED_OCI_LAYOUT_DIR
    
    if not embedded_path.exists():
        raise FileNotFoundError(f"Embedded data directory {embedded_path} not found")
    
    target_path = Path(target_path).expanduser().resolve()
    target_path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(embedded_path, target_path, dirs_exist_ok=True)
