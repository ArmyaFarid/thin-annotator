import matplotlib.pyplot as plt
from skimage import io, segmentation, color, graph
from skimage.util import img_as_float

def superpixel_merging(image_path, n_segments=200, seuil_fusion=0.08):
    # 1. Charger l'image de l'utilisateur
    try:
        image = img_as_float(io.imread(image_path))
    except FileNotFoundError:
        print(f"Erreur : Impossible de trouver l'image au chemin '{image_path}'.")
        print("Vérifiez que le chemin est correct et que le fichier existe.")
        return

    # 2. Topologie de base (SLIC)
    # Utilisation de n_segments=200 comme tu l'as indiqué
    segments_slic = segmentation.slic(image, n_segments=n_segments, compactness=20, start_label=1)

    # 3. Création du Graphe d'Adjacence (RAG)
    rag = graph.rag_mean_color(image, segments_slic)

    # 4. Fusion des composants (Merging)
    # Fusion des régions adjacentes selon la similarité de couleur
    segments_fusionnes = graph.cut_threshold(segments_slic, rag, thresh=seuil_fusion)

    # 5. Création des rendus visuels
    rendu_moyen = color.label2rgb(segments_fusionnes, image, kind='avg')
    masques_couleurs = color.label2rgb(segments_fusionnes, image, alpha=0.3, bg_label=-1)

    # --- Affichage des résultats ---
    fig, ax = plt.subplots(1, 3, figsize=(18, 6), sharex=True, sharey=True)

    # Image 1 : La topologie SLIC sur l'image originale
    ax[0].imshow(segmentation.mark_boundaries(image, segments_slic))
    ax[0].set_title(f'Topologie SLIC\n({n_segments} superpixels)')
    ax[0].axis('off')

    # Image 2 : Masques fusionnés (Couleurs moyennes)
    ax[1].imshow(rendu_moyen)
    ax[1].set_title(f'Objets Fusionnés (RAG)\n(Seuil: {seuil_fusion})')
    ax[1].axis('off')

    # Image 3 : Masques de segmentation en couleurs (Overlay)
    ax[2].imshow(masques_couleurs)
    ax[2].set_title('Masques en couleurs (Overlay)')
    ax[2].axis('off')

    plt.tight_layout()
    plt.show()

# --- Lancer le code avec ton image ---
chemin_image = "/Users/armyabakouan/Documents/ThinAnnotatorData/DOSSIER_LAMES/NW22A-8-C/15/NW22A-8-C-15_mod-RL.png"

# Tu peux ajuster le seuil_fusion (ex: 0.05 pour fusionner moins, 0.15 pour fusionner plus)
superpixel_merging(image_path=chemin_image, n_segments=200, seuil_fusion=0.08)