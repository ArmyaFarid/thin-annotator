# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from typing import Iterable

from data.csv_queries import load_pairs_csv


def resolve_videos(node_ids: Iterable[str], required: bool = False):
    """
    Resolve videos given node ids.
    """
    from data.store import get_videos

    all_videos = get_videos()
    return [
        all_videos[nid] if required else all_videos.get(nid, None) for nid in node_ids
    ]


def resolve_images(node_ids: Iterable[str], required: bool = False):
    """
    Resolve images given node ids.
    """
    from data.store import get_images

    all_images = get_images()
    return [
        all_images[nid] if required else all_images.get(nid, None) for nid in node_ids
    ]


def resolve_acquired_images(pair_code: str):
    from data.data_types import AcquiredImage, PolarizedFilterType

    grouped = load_pairs_csv()
    rows = grouped.get(pair_code, [])

    from data.store import get_images

    all_images = get_images()

    acquired = []

    for row in rows:
        try:
            acquired.append(
                AcquiredImage(
                    polarized_filter_type=PolarizedFilterType(row["polirized_filter_type"]),
                    gamma=int(row["gamma"]) if row["gamma"] else None,
                    acquisition_label=row.get("angle"),
                    image=all_images[row["image"]],
                )
            )
        except KeyError as e:
            print(f"KeyError for row: {row}, missing key: {e}")
        except ValueError as e:
            print(f"ValueError for row: {row}, maybe invalid int conversion: {e}")
        except Exception as e:
            print(f"Unexpected error for row: {row}: {e}")

    return acquired

def resolve_thin_section_image_pairs(node_ids: Iterable[str], required: bool = False):
    raise NotImplementedError