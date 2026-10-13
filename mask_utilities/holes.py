import cv2
import numpy as np


def remove_holes(mask):
    return mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def clean_mask(mask, max_hole_area=100, min_object_area=100, connectivity=8):
    """
    Fill small holes and remove small isolated objects in a binary mask.

    Args:
        mask: 2D array (bool, 0/1 or 0/255).
        max_hole_area: holes with area (pixels) below this are filled. 0 disables.
        min_object_area: objects with area (pixels) below this are removed. 0 disables.
        connectivity: 8 or 4, connectivity used for foreground objects.
                      Holes use the complementary connectivity (8 -> 4, 4 -> 8).

    Returns:
        Cleaned boolean mask, same shape as input.
    """
    m = np.asarray(mask) > 0
    if m.ndim != 2:
        raise ValueError(f"Expected a 2D mask, got shape {m.shape}")

    if max_hole_area > 0:
        hole_conn = 4 if connectivity == 8 else 8
        n, labels, stats, _ = cv2.connectedComponentsWithStats(
            (~m).astype(np.uint8), connectivity=hole_conn
        )
        areas = stats[:, cv2.CC_STAT_AREA]
        fill = areas < max_hole_area
        fill[0] = False
        border = np.unique(np.concatenate([
            labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1]
        ]))
        fill[border] = False

        m = m | fill[labels]

    if min_object_area > 0:
        n, labels, stats, _ = cv2.connectedComponentsWithStats(
            m.astype(np.uint8), connectivity=connectivity
        )
        keep = stats[:, cv2.CC_STAT_AREA] >= min_object_area
        keep[0] = False
        m = keep[labels]

    return m