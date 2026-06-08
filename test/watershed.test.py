import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from skimage import io, color, filters, segmentation
from skimage.feature import peak_local_max


def segment_with_watershed(image_path):
    # 1. Charger l'image
    try:
        image = io.imread(image_path)
    except FileNotFoundError:
        print(f"Erreur : Impossible de trouver '{image_path}'.")
        return

    # Convertir en niveaux de gris si c'est une image RGB
    gray = color.rgb2gray(image) if image.ndim == 3 else image

    # 2. Binarisation (Séparer l'avant-plan de l'arrière-plan)
    # Otsu calcule automatiquement le meilleur seuil pour séparer les pixels clairs/sombres
    seuil = filters.threshold_otsu(gray)

    # IMPORTANT : Si tes objets sont sombres sur un fond clair,
    # change cette ligne en : masque_binaire = gray < seuil
    masque_binaire = gray > seuil

    # 3. Calcul de la distance au fond (Distance Transform)
    # Calcule la distance de chaque pixel de l'objet par rapport au bord le plus proche.
    # Les valeurs les plus élevées seront au centre exact des objets.
    distance = ndi.distance_transform_edt(masque_binaire)

    # 4. Trouver les marqueurs (les pics locaux de la distance)
    # min_distance empêche d'avoir trop de marqueurs très proches (évite la sur-segmentation)
    coords = peak_local_max(distance, min_distance=10, labels=masque_binaire)

    # Créer un masque vide et y placer les marqueurs
    mask_coords = np.zeros(distance.shape, dtype=bool)
    mask_coords[tuple(coords.T)] = True
    markers, _ = ndi.label(mask_coords)

    # 5. Algorithme Watershed
    # On utilise l'inverse de la distance (-distance) pour que les centres soient les "vallées"
    labels_watershed = segmentation.watershed(-distance, markers, mask=masque_binaire)

    # 6. Création de l'overlay coloré
    # bg_label=0 garde le fond transparent
    overlay_couleurs = color.label2rgb(labels_watershed, image=image, alpha=0.4, bg_label=0)

    # --- Affichage des résultats ---
    fig, ax = plt.subplots(1, 3, figsize=(18, 6), sharex=True, sharey=True)

    ax[0].imshow(image, cmap='gray' if image.ndim == 2 else None)
    ax[0].set_title('1. Image Originale')
    ax[0].axis('off')

    # Affichage de la carte de distance pour comprendre comment Watershed se guide
    ax[1].imshow(distance, cmap='magma')
    ax[1].set_title('2. Transformée de Distance\n(Les centres sont brillants)')
    ax[1].axis('off')

    ax[2].imshow(overlay_couleurs)
    ax[2].set_title('3. Segmentation Watershed\n(Masques en couleurs)')
    ax[2].axis('off')

    plt.tight_layout()
    plt.show()


# --- Lancer le code avec ton image ---
chemin_image = "/Users/armyabakouan/UQAC/RESEARCH/experiments/web/sam2/backend/app_test_compile/test/testdata/NW22A-8-C-5_mod-RL_comp-na_rot-0.png"
segment_with_watershed(chemin_image)