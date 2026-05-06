from pathlib import Path

# Mapping dictionary for the compensator
COMP_LOGIC = {
    "add": 1,
    "sous": -1,
    "na": 0
}

def parse_fov_filename(filename):
    # Remove extension (.bmp)
    stem = Path(filename).stem
    # Split by underscore
    parts = stem.split("_")
    # metadata will look like: {'mod': 'XPL', 'comp': 'add', 'rot': '45'}
    metadata = {}
    for p in parts:
        if '-' in p:
            k, v = p.split('-', 1)
            metadata[k] = v
        else:
            metadata['sample_id'] = p

    return {
        "thin_section_id": metadata.get('sample_id'),
        "lighting_modality": metadata.get('mod'),
        "gamma": COMP_LOGIC.get(metadata.get('comp'), 0),
        "stage_angle": int(metadata.get('rot', 0))
    }