import os
import sys
from app_utils import extract_combined_model_features, load_features_dict, search_similar_images, generate_rp_curve

image_db_folder = 'static/image.orig' 

def get_similar_images(file_path, model_names, topn=5, dist_metric='euclidean', specified_class=None, filename='rp_curve.png'):
    features_target = extract_combined_model_features(file_path, model_names=model_names)
    features_db = load_features_dict(model_names=model_names)
    
    images_proches, predicted_class = search_similar_images(features_target, features_db, topn=topn, dist_metric=dist_metric)
    rp_img_path = generate_rp_curve(specified_class, predicted_class, images_proches, filename)
    return images_proches, rp_img_path, predicted_class

if __name__ == "__main__":
    # Récupéerer le premier argument de la ligne de commande comme chemin de l'image

    if len(sys.argv) < 2:
        print("Usage: python app.py <image_path>")
        sys.exit(1)
    file_path = sys.argv[1]

    images_proches, rp_img_path, _ = get_similar_images(file_path, model_names=['resnet50'], topn=5, dist_metric='euclidean', specified_class=None, filename='rp_curve.png')
    print(f"[MYAPP] >> Similar Images: {images_proches}")
    print(f"[MYAPP] >> RP Curve Image Path: {rp_img_path}")