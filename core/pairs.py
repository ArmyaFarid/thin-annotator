from data.data_types import Pairs, unique_preserve_order
from data.resolver import resolve_acquired_images_from_db


def get_pairs(pairs_code: str, sample_id: str) -> Pairs:
    acquired = resolve_acquired_images_from_db(pairs_code, sample_id)

    return Pairs(
        pairs_code=pairs_code,
        sample_id=sample_id,
        acquired_images=acquired,
        polarized_filter_types=unique_preserve_order([a.polarized_filter_type for a in acquired]),
        rotations=unique_preserve_order([a.rotation for a in acquired]),
        gammas=unique_preserve_order([a.gamma for a in acquired]),
    )
