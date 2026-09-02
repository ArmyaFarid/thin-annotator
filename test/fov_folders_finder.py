import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.thin_section_fov_folder_scanner import find_fov_folders

folders = find_fov_folders("/Users/armyabakouan/UQAC/RESEARCH/ThinAnnotatorData/DOSSIER_LAMES")


for folder in folders:
    print(folder)