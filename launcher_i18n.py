import json
import os
import subprocess
import sys

from system.filesystem import get_writable_dir

LANGUAGES = ("en", "fr")

STRINGS = {
    "en": {
        "window_title": "ThinAnnotator Control Panel",
        "server_stopped": "Server stopped",
        "server_loading": "Loading ThinAnnotator models...",
        "server_running": "Running on http://127.0.0.1:7263",
        "server_crashed": "Server crashed (exit {code})",
        "server_timeout": "Timeout: Server took too long",
        "check_logs": "Check terminal logs for details.",
        "tried_for": "Tried for {seconds}s. Try restarting.",
        "loading_models": "Loading SAM2 models{dots}",
        "start_server": "Start Server",
        "stop_server": "Stop Server",
        "open_annotator": "Open Annotator",
        "open_docs": "Open Docs",
        "generate_dataset": "Generate Thin-COCO dataset",
        "exit": "Exit Entirely",
        "dataset_title": "Generate Thin-COCO Dataset",
        "source_folder": "Source Folder:",
        "select_source": "Select Source Folder",
        "destination_folder": "Destination Folder:",
        "select_destination": "Select Destination Folder",
        "browse": "Browse",
        "zip_option": "Compress as .zip archive (Slower but saves space)",
        "preparing": "Preparing...",
        "waiting": "Waiting...",
        "error": "Error",
        "select_both": "Please select both folders.",
        "success": "Success",
        "dataset_done": "Thin-COCO dataset generated successfully!\n\nSaved to:\n{path}",
        "generation_error": "Generation Error",
        "generate": "Generate",
        "step.SCANNING": "Scanning dataset",
        "step.JSON_FILES_COMPUTING": "Reading annotations",
        "step.ZIPPING": "Writing ZIP archive",
        "step.COPYING": "Copying uncompressed images",
        "step.FINALIZING": "Finalizing dataset",
    },
    "fr": {
        "window_title": "Panneau de contrôle ThinAnnotator",
        "server_stopped": "Serveur arrêté",
        "server_loading": "Chargement des modèles ThinAnnotator...",
        "server_running": "Actif sur http://127.0.0.1:7263",
        "server_crashed": "Le serveur a planté (code {code})",
        "server_timeout": "Délai dépassé : le serveur a mis trop de temps",
        "check_logs": "Consultez les journaux du terminal.",
        "tried_for": "Essai pendant {seconds} s. Essayez de redémarrer.",
        "loading_models": "Chargement des modèles SAM2{dots}",
        "start_server": "Démarrer le serveur",
        "stop_server": "Arrêter le serveur",
        "open_annotator": "Ouvrir l'annotateur",
        "open_docs": "Ouvrir la documentation",
        "generate_dataset": "Générer le jeu de données Thin-COCO",
        "exit": "Quitter",
        "dataset_title": "Générer le jeu de données Thin-COCO",
        "source_folder": "Dossier source :",
        "select_source": "Sélectionner le dossier source",
        "destination_folder": "Dossier de destination :",
        "select_destination": "Sélectionner le dossier de destination",
        "browse": "Parcourir",
        "zip_option": "Compresser en archive .zip (plus lent, mais prend moins de place)",
        "preparing": "Préparation...",
        "waiting": "En attente...",
        "error": "Erreur",
        "select_both": "Veuillez sélectionner les deux dossiers.",
        "success": "Succès",
        "dataset_done": "Jeu de données Thin-COCO généré avec succès !\n\nEnregistré dans :\n{path}",
        "generation_error": "Erreur de génération",
        "generate": "Générer",
        "step.SCANNING": "Analyse du jeu de données",
        "step.JSON_FILES_COMPUTING": "Lecture des annotations",
        "step.ZIPPING": "Écriture de l'archive ZIP",
        "step.COPYING": "Copie des images non compressées",
        "step.FINALIZING": "Finalisation du jeu de données",
    },
}

SETTINGS_FILE = get_writable_dir() / "launcher_settings.json"


def system_language():
    try:
        if sys.platform == "darwin":
            out = subprocess.run(["defaults", "read", "-g", "AppleLanguages"], capture_output=True, text=True, timeout=2).stdout
            first = next((line.strip(' ",()') for line in out.splitlines() if line.strip(' ",()')), "")
        elif sys.platform == "win32":
            import ctypes
            first = "fr" if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x0C else "en"
        else:
            first = os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES") or os.environ.get("LANG") or ""
    except Exception:
        first = ""
    return "fr" if first.lower().startswith("fr") else "en"


def load_language():
    try:
        saved = json.loads(SETTINGS_FILE.read_text()).get("language")
        if saved in LANGUAGES:
            return saved
    except Exception:
        pass
    return system_language()


current_language = load_language()


def set_language(code):
    global current_language
    current_language = code
    try:
        SETTINGS_FILE.write_text(json.dumps({"language": code}))
    except OSError:
        pass


def tr(key, **kwargs):
    text = STRINGS[current_language].get(key) or STRINGS["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


def step_name(action):
    key = f"step.{action}"
    return tr(key) if key in STRINGS["en"] else action
