import json
import logging
from pathlib import Path

from app_conf import get_writable_dir

logger = logging.getLogger(__name__)

OPTIONS_FILENAME = "annotation-options.json"

# --- Hardcoded fallback -------------------------------------------------------
DEFAULT_ANNOTATION_OPTIONS = {
    "version": 1,
    "mineralGroups": [
        {"value": "tectosilicates", "label": {"fr": "Tectosilicates", "en": "Tectosilicates"}},
        {"value": "phyllosilicates", "label": {"fr": "Phyllosilicates", "en": "Phyllosilicates"}},
        {"value": "inosilicates", "label": {"fr": "Inosilicates", "en": "Inosilicates"}},
        {"value": "nesosilicates", "label": {"fr": "Nésosilicates", "en": "Nesosilicates"}},
        {"value": "cyclosilicates", "label": {"fr": "Cyclosilicates", "en": "Cyclosilicates"}},
        {"value": "sorosilicates", "label": {"fr": "Sorosilicates", "en": "Sorosilicates"}},
        {"value": "carbonates", "label": {"fr": "Carbonates", "en": "Carbonates"}},
        {"value": "oxides", "label": {"fr": "Oxydes", "en": "Oxides"}},
        {"value": "phosphates", "label": {"fr": "Phosphates", "en": "Phosphates"}},
    ],
    "minerals": [
        {"value": "qtz", "label": {"fr": "Quartz", "en": "Quartz"}, "group": "tectosilicates"},
        {"value": "kfs", "label": {"fr": "Feldspath K", "en": "K-feldspar"}, "group": "tectosilicates"},
        {"value": "plag", "label": {"fr": "Plagioclase", "en": "Plagioclase"}, "group": "tectosilicates"},
        {"value": "ms", "label": {"fr": "Muscovite", "en": "Muscovite"}, "group": "phyllosilicates"},
        {"value": "bt", "label": {"fr": "Biotite", "en": "Biotite"}, "group": "phyllosilicates"},
        {"value": "chl", "label": {"fr": "Chlorite", "en": "Chlorite"}, "group": "phyllosilicates"},
        {"value": "srp", "label": {"fr": "Serpentine", "en": "Serpentine"}, "group": "phyllosilicates"},
        {"value": "hbl", "label": {"fr": "Hornblende", "en": "Hornblende"}, "group": "inosilicates"},
        {"value": "aug", "label": {"fr": "Augite", "en": "Augite"}, "group": "inosilicates"},
        {"value": "hyp", "label": {"fr": "Hypersthène", "en": "Hypersthene"}, "group": "inosilicates"},
        {"value": "ol", "label": {"fr": "Olivine", "en": "Olivine"}, "group": "nesosilicates"},
        {"value": "grt", "label": {"fr": "Grenat", "en": "Garnet"}, "group": "nesosilicates"},
        {"value": "zrn", "label": {"fr": "Zircon", "en": "Zircon"}, "group": "nesosilicates"},
        {"value": "tur", "label": {"fr": "Tourmaline", "en": "Tourmaline"}, "group": "cyclosilicates"},
        {"value": "ep", "label": {"fr": "Épidote", "en": "Epidote"}, "group": "sorosilicates"},
        {"value": "ttn", "label": {"fr": "Titanite", "en": "Titanite"}, "group": "sorosilicates"},
        {"value": "cal", "label": {"fr": "Calcite", "en": "Calcite"}, "group": "carbonates"},
        {"value": "dol", "label": {"fr": "Dolomite", "en": "Dolomite"}, "group": "carbonates"},
        {"value": "mag", "label": {"fr": "Magnétite", "en": "Magnetite"}, "group": "oxides"},
        {"value": "ilm", "label": {"fr": "Ilménite", "en": "Ilmenite"}, "group": "oxides"},
        {"value": "hem", "label": {"fr": "Hématite", "en": "Hematite"}, "group": "oxides"},
        {"value": "ap", "label": {"fr": "Apatite", "en": "Apatite"}, "group": "phosphates"},
    ],
    "properties": {
        "relief": [
            {"value": "low", "label": {"fr": "Faible", "en": "Low"}},
            {"value": "medium", "label": {"fr": "Moyen", "en": "Medium"}},
            {"value": "high", "label": {"fr": "Élevé", "en": "High"}},
        ],
        "birefringence": [
            {"value": "low", "label": {"fr": "Faible", "en": "Low"}},
            {"value": "medium", "label": {"fr": "Moyen", "en": "Medium"}},
            {"value": "high", "label": {"fr": "Élevé", "en": "High"}},
            {"value": "very-high", "label": {"fr": "Très élevé", "en": "Very high"}},
        ],
        "cleavage": [
            {"value": "none", "label": {"fr": "Aucun", "en": "None"}},
            {"value": "indistinct", "label": {"fr": "Indistinct", "en": "Indistinct"}},
            {"value": "good", "label": {"fr": "Bon", "en": "Good"}},
            {"value": "perfect", "label": {"fr": "Parfait", "en": "Perfect"}},
        ],
        "pleochroism": [
            {"value": "none", "label": {"fr": "Aucun", "en": "None"}},
            {"value": "weak", "label": {"fr": "Faible", "en": "Weak"}},
            {"value": "strong", "label": {"fr": "Fort", "en": "Strong"}},
        ],
        "crystalSystem": [
            {"value": "cubic", "label": {"fr": "Cubique", "en": "Cubic"}},
            {"value": "tetragonal", "label": {"fr": "Tétragonal", "en": "Tetragonal"}},
            {"value": "orthorhombic", "label": {"fr": "Orthorhombique", "en": "Orthorhombic"}},
            {"value": "monoclinic", "label": {"fr": "Monoclinique", "en": "Monoclinic"}},
            {"value": "triclinic", "label": {"fr": "Triclinique", "en": "Triclinic"}},
            {"value": "hexagonal", "label": {"fr": "Hexagonal", "en": "Hexagonal"}},
        ],
    },
}

PROPERTY_KEYS = ("relief", "birefringence", "cleavage", "pleochroism", "crystalSystem")


# --- Format validation --------------------------------------------------------
def _is_option(o):
    """An option needs a string value and a label with fr + en strings."""
    return (
            isinstance(o, dict)
            and isinstance(o.get("value"), str)
            and isinstance(o.get("label"), dict)
            and isinstance(o["label"].get("fr"), str)
            and isinstance(o["label"].get("en"), str)
    )


def _is_valid_options(data):
    if not isinstance(data, dict):
        return False
    groups = data.get("mineralGroups")
    minerals = data.get("minerals")
    properties = data.get("properties")
    if not isinstance(groups, list) or not all(_is_option(g) for g in groups):
        return False
    if not isinstance(minerals, list) or not minerals:
        return False
    if not all(_is_option(m) and isinstance(m.get("group"), str) for m in minerals):
        return False
    if not isinstance(properties, dict):
        return False
    for key in PROPERTY_KEYS:
        opts = properties.get(key)
        if not isinstance(opts, list) or not opts or not all(_is_option(o) for o in opts):
            return False
    return True


# --- Public accessor ----------------------------------------------------------
def get_annotation_options():
    """Annotation option lists.

    Uses annotation-options.json from get_writable_dir() when it exists and is
    well-formed; otherwise returns DEFAULT_ANNOTATION_OPTIONS. The file is
    re-read on every call, so it can be edited without restarting the server.
    """
    path = Path(get_writable_dir()) / OPTIONS_FILENAME
    if path.is_file():
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("Cannot read %s (%s) — using defaults", path, e)
            return DEFAULT_ANNOTATION_OPTIONS
        if _is_valid_options(data):
            return data
        logger.warning("%s has an invalid format — using defaults", path)
    return DEFAULT_ANNOTATION_OPTIONS