# Copyright (c) 2025 Armya BAKOUAN.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file in the root directory of this source tree.

from data.loader_image import init_thin_section_fov_images

from core.task_manager import get_task_snapshot
from system.pickers import pick_folder_sub


def pick_folder_and_init_section_fov_images():
    path = pick_folder_sub()
    thin_section_id , fov_id , image_count = init_thin_section_fov_images(path)
    annotations = get_task_snapshot(path,None)
    return {"pairsCode": thin_section_id,"image_count":image_count, "sampleId": fov_id, "annotations": annotations}