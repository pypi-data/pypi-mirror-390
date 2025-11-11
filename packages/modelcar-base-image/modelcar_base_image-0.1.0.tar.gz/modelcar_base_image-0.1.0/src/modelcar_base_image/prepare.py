import os
import subprocess
import logging
from modelcar_base_image.embedded_oci_layout import copy_base_image_to_oci_layout
from modelcar_base_image.constants import ODH_MODELCAR_BASE_IMAGE, EMBEDDED_OCI_LAYOUT_DIR


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(current_dir, EMBEDDED_OCI_LAYOUT_DIR)
    
    os.makedirs(dest_dir, exist_ok=True)
    
    logger.info("Copying %s to OCI layout at %s", ODH_MODELCAR_BASE_IMAGE, dest_dir)
    try:
        result = copy_base_image_to_oci_layout(ODH_MODELCAR_BASE_IMAGE, dest_dir)
        logger.info("Successfully copied image to %s", dest_dir)
        logger.info("Command completed with return code: %s", result.returncode)
    except subprocess.CalledProcessError as e:
        logger.error("Error copying image: %s", e)
        exit(1)
