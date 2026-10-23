# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#
# Modifications Copyright (c) 2025 Armya BAKOUAN -- see NOTICE for details.

from extensions import db
from models import FOVAsset


def resolve_acquired_images_from_db(thin_section_id: str , fov_id: str):
    from data.data_types import AcquiredImage, PolarizedFilterType , Image

    fov_assets = db.session.execute(db.select(FOVAsset).filter_by(thin_section_id=thin_section_id,fov_id=fov_id)).scalars().all()

    acquired = []

    for row in fov_assets:
        try:
            image = Image(
                code=row.id,
                path=row.image_path,
                width=row.width,
                height=row.height,
                thumbnail_path=row.thumbnail_path,
            )
            acquired.append(
                AcquiredImage(
                    polarized_filter_type=PolarizedFilterType(row.lighting_modality),
                    gamma=int(row.gamma),
                    acquisition_label=row.stage_angle,
                    image=image,
                    rotation=row.stage_angle,
                )
            )
        except KeyError as e:
            print(f"KeyError for row: {row}, missing key: {e}")
        except ValueError as e:
            print(f"ValueError for row: {row}, maybe invalid int conversion: {e}")
        except Exception as e:
            print(f"Unexpected error for row: {row}: {e}")

    return acquired
