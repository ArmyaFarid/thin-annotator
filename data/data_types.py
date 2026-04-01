# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Optional

import strawberry
from app_conf import API_URL
from data.resolver import resolve_images, resolve_videos, resolve_acquired_images, resolve_thin_section_image_pairs
from dataclasses_json import dataclass_json
from strawberry import relay

def unique_preserve_order(values):
    seen = set()
    result = []
    for v in values:
        if v not in seen:
            seen.add(v)
            result.append(v)
    return result


@strawberry.type
class Video(relay.Node):
    """Core type for video."""

    code: relay.NodeID[str]
    path: str
    poster_path: Optional[str]
    width: int
    height: int

    @strawberry.field
    def url(self) -> str:
        return f"{API_URL}/{self.path}"

    @strawberry.field
    def poster_url(self) -> str:
        return f"{API_URL}/{self.poster_path}"

    @classmethod
    def resolve_nodes(
        cls,
        *,
        info: relay.PageInfo,
        node_ids: Iterable[str],
        required: bool = False,
    ):
        return resolve_videos(node_ids, required)
    

@strawberry.type
class Image(relay.Node):
    """Core type for image."""

    code: relay.NodeID[str]  # unique ID
    path: str                 # image file path
    width: int
    height: int
    thumbnail_path: Optional[str] = None  # optional thumbnail

    @strawberry.field
    def url(self) -> str:
        return f"{API_URL}/{self.path}"

    @strawberry.field
    def thumbnail_url(self) -> Optional[str]:
        if self.thumbnail_path:
            return f"{API_URL}/{self.thumbnail_path}"
        return None

    @classmethod
    def resolve_nodes(
        cls,
        *,
        info: relay.PageInfo,
        node_ids: Iterable[str],
        required: bool = False,
    ):
        """
        Resolve multiple images by node IDs.
        Implement your backend logic in `resolve_images`.
        """
        return resolve_images(node_ids, required)

@strawberry.enum
class PolarizedFilterType(Enum):
    PPL = "PPL"                  # Plane Polarized Light
    XPL = "XPL"                  # Cross Polarized Light (default angle)
    # RL = "RL"                    # Reflected Light
    # FL = "FL"                    # Fluorescence
    XPL_GAMMA = "XPL_GAMMA"
    OTHER = "OTHER"


@strawberry.type
class AcquiredImage:
    """
    Links an Image to its acquisition context (modality, angle, settings).
    This is the 'typed slot' in a ThinSectionImagePairs set.
    """
    polarized_filter_type: PolarizedFilterType
    gamma : Optional[int]
    acquisition_label: Optional[str]
    image: Image



@strawberry.type
class ThinSectionImagePairs(relay.Node):
    """
    A set of co-registered images for a single thin section sample.
    Each image is associated with a specific acquisition
    (XPL at angle, PPL, XPL with gamma, etc.).
    """

    code: relay.NodeID[str]           # unique ID for this image set
    sample_id: str                     # thin section sample this set belongs to
    label: Optional[str] = None        # human-readable name for this set
    description: Optional[str] = None  # extended notes / metadata

    _acquired_cache: Optional[List[AcquiredImage]] = None

    _polarized_filter_types: Optional[List[PolarizedFilterType]] = None

    _gammas : Optional[List[int]] = None


    @strawberry.field
    def acquired_images(self) -> List[AcquiredImage]:
        """
        All images in this set, each linked to their acquisition context.
        Order is preserved (e.g. XPL-0deg → XPL-45deg → XPL-90deg → PPL).
        """
        if self._acquired_cache is None:
            self._acquired_cache = resolve_acquired_images(self.code)
            # compute types at the same time
            self._polarized_filter_types = [resolved_acquired_image.polarized_filter_type for resolved_acquired_image in self._acquired_cache]
            self._gammas = [resolved_acquired_image.gamma for resolved_acquired_image in self._acquired_cache]
        return self._acquired_cache

    @strawberry.field
    def image_by_acquisition(
        self, acquisition_type: PolarizedFilterType
    ) -> Optional[Image]:
        """
        Convenience: fetch a single image by acquisition type.
        Returns the first match if multiple images share the same type.
        """
        for entry in resolve_acquired_images(self.code):
            if entry.polarized_filter_type == acquisition_type:
                return entry.image
        return None

    @strawberry.field
    def polarized_filter_types(self) -> List[PolarizedFilterType]:
        """
        Returns the list of acquisition types available in this set.
        Useful for clients to know which modalities exist before fetching images.
        """
        if self._polarized_filter_types is None:
            # resolve images to compute types
            _ = self.acquired_images()
        return unique_preserve_order(self._polarized_filter_types)

    @strawberry.field
    def gammas(self) -> List[Optional[int]]:
        if self._gammas is None:
            _ = self.acquired_images()
        return unique_preserve_order(self._gammas)

    @classmethod
    def resolve_nodes(
        cls,
        *,
        info: relay.PageInfo,
        node_ids: Iterable[str],
        required: bool = False,
    ):
        """
        Relay global node lookup — resolves ThinSectionImagePairs by their global IDs.
        Implement backend logic in `resolve_thin_section_image_pairs`.
        """
        return resolve_thin_section_image_pairs(node_ids, required)

@strawberry.type
class RLEMask:
    """Core type for Onevision GraphQL RLE mask."""

    size: List[int]
    counts: str
    order: str


@strawberry.type
class RLEMaskForObject:
    """Type for RLE mask associated with a specific object id."""

    object_id: int
    rle_mask: RLEMask


@strawberry.type
class RLEMaskListOnFrame:
    """Type for a list of object-associated RLE masks on a specific video frame."""

    frame_index: int
    rle_mask_list: List[RLEMaskForObject]


@strawberry.input
class StartSessionInput:
    path: str
    pairs_code : strawberry.ID


@strawberry.type
class StartSession:
    session_id: str


@strawberry.input
class PingInput:
    session_id: str


@strawberry.type
class Pong:
    success: bool


@strawberry.input
class CloseSessionInput:
    session_id: str


@strawberry.type
class CloseSession:
    success: bool


@strawberry.input
class AddPointsInput:
    session_id: str
    frame_index: int
    clear_old_points: bool
    object_id: int
    labels: List[int]
    points: List[List[float]]
    bboxes: List[List[float]]


@strawberry.input
class AddPointsImageInput:
    session_id: str
    image_path: str
    object_id: int
    labels: List[int]
    points: List[List[float]]
    bboxes: List[List[float]]

@strawberry.input
class ClearPointsInFrameInput:
    session_id: str
    frame_index: int
    object_id: int


@strawberry.input
class ClearPointsInVideoInput:
    session_id: str


@strawberry.type
class ClearPointsInVideo:
    success: bool


@strawberry.input
class RemoveObjectInput:
    session_id: str
    object_id: int


@strawberry.input
class PropagateInVideoInput:
    session_id: str
    start_frame_index: int


@strawberry.input
class CancelPropagateInVideoInput:
    session_id: str


@strawberry.type
class CancelPropagateInVideo:
    success: bool


@strawberry.type
class SessionExpiration:
    session_id: str
    expiration_time: int
    max_expiration_time: int
    ttl: int
