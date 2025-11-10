import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from persim import PersistenceImager
import os

def get_max_birth_persistence(all_diagrams):
    """
    Compute the minimum and maximum of birth and persistence 
    across all H1 and H2 persistence diagrams.
    
    Parameters:
        all_diagrams (list): List of persistence diagrams for each structure.
    
    Returns:
        tuple: (max_birth, min_birth, max_persistence, min_persistence)
    """
    max_birth = max_persistence = 0
    min_birth = min_persistence = np.inf

    for diagrams in all_diagrams:
        for diagram in diagrams[1:]:  # H1 and H2
            if len(diagram) > 0:
                births = diagram[:, 0]
                persistences = diagram[:, 1] - diagram[:, 0]
                max_birth = max(max_birth, np.max(births))
                max_persistence = max(max_persistence, np.max(persistences))
                min_birth = min(min_birth, np.min(births))
                min_persistence = min(min_persistence, np.min(persistences))

    return max_birth, min_birth, max_persistence, min_persistence


def create_persistent_images(diagrams, pimgr, save_path=None):
    """
    Transform d1 and d2 persistence diagrams into persistent images.
    
    Optionally save the images as PNG plots.

    Parameters:
        diagrams (tuple): d0, d1, d2 persistence diagrams.
        pimgr (PersistenceImager): Persistence image transformer.
        save_path (str, optional): File path to save the plotted images.
    
    Returns:
        tuple: (flattened image array, d1 feature length, d2 feature length)
    """

    d0_dgm, d1_dgm, d2_dgm = diagrams
    d1_img = pimgr.transform(d1_dgm, skew=True)
    d2_img = pimgr.transform(d2_dgm, skew=True)

    if save_path:
        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        pimgr.plot_image(d1_img, ax=axs[0])
        axs[0].set_title("H1 Persistent Image")
        pimgr.plot_image(d2_img, ax=axs[1])
        axs[1].set_title("H2 Persistent Image")
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

    img_array = np.vstack([d1_img, d2_img]).ravel()
    return img_array, len(np.vstack(d1_img).ravel()), len(np.vstack(d2_img).ravel())


def calc_persistence_statistics(diagrams):
    """
    Calculate statistical features from a persistence diagram.
    
    Computes number of points, total, mean, variance, max, and min persistence.

    Parameters:
        diagrams (np.ndarray): A single persistence diagram.
    
    Returns:
        dict: Statistical features keyed by homology dimension (D0, D1, D2).
    """
    feature_dict = {}
    for i, dgm in enumerate(diagrams):
        if len(dgm) == 0:
            vals = [0] * 6
        else:
            persistences = dgm[:, 1] - dgm[:, 0]
            vals = [
                len(persistences),
                np.sum(persistences),
                np.mean(persistences),
                np.var(persistences),
                np.max(persistences),
                np.min(persistences)
            ]
        keys = [f'D{i}_num_points', f'D{i}_total_persistence', f'D{i}_mean_persistence',
                f'D{i}_variance_persistence', f'D{i}_max_persistence', f'D{i}_min_persistence']
        feature_dict.update(dict(zip(keys, vals)))
    return feature_dict

def get_persistent_stats_features(diagrams_tuples):
    """
    Extract statistical features from a set of persistence diagrams.

    Parameters:
        diagrams_tuples (list): Each tuple contains diagrams, filename, and topological net.

    Returns:
        pd.DataFrame: Statistics features for all diagrams, with columns for file name and topological net.
    """

    files, nets, diagrams = zip(*((t[-2], t[-1], tuple(t[:-2])) for t in diagrams_tuples))
    files, nets, diagrams = map(list, (files, nets, diagrams))

    all_features = []
    for diagram in diagrams:
        features = calc_persistence_statistics(diagram)
        all_features.append(features)

    stats_features_df = pd.DataFrame(all_features)

    stats_features_df['Name'] = files
    stats_features_df['Topological Net'] = nets
    return stats_features_df


def calc_persistent_image_features(all_diagrams, filenames, export_folder=None, output_image_size=(50, 50), savefig=False):
    """
    Calculate persistent image features for a set of diagrams.
    
    Optionally saves persistent images for each diagram.

    Parameters:
        all_diagrams (list): List of persistence diagrams for each structure.
        filenames (list): List of corresponding filenames.
        export_folder (str, optional): Folder to save images if savefig=True.
        output_image_size (tuple): Size of output images in pixels.
        savefig (bool): Whether to save the images.
    
    Returns:
        tuple: (image feature arrays, D1 feature length, D2 feature length)
    """

    # Calculate birth and persistence ranges based on all diagrams
    max_birth, min_birth, max_persistence, min_persistence = get_max_birth_persistence(all_diagrams)
    print(f"Max birth: {max_birth}, Min birth: {min_birth}, Max persistence: {max_persistence}, Min persistence: {min_persistence}")

    width, height = output_image_size

    # Determine pixel size for persistence images
    pixel_size = min((max_birth - min_birth) / width, (max_persistence - min_persistence) / height)

    # Create PersistenceImager instance, set birth and persistence ranges based on Max/Min values
    pimgr = PersistenceImager(
        pixel_size=pixel_size,
        birth_range=(min_birth, max_birth),
        pers_range=(min_persistence, max_persistence)
    )

    image_features = []
    for idx, diagram in enumerate(all_diagrams):
        basename = os.path.basename(filenames[idx])
        save_path = f"{export_folder}/{basename}_persistent_image.png" if savefig else None
        # Calculate persistent image features for D1 and D2
        features, D1_length, D2_length = create_persistent_images(diagram, pimgr, save_path=save_path)
        image_features.append(features)

    return image_features, D1_length, D2_length

def get_persistent_image_features(diagrams_tuple, output_image_size=(50, 50), savefig=False, export_folder=None):
    """
    Extract persistent image features from persistence diagrams and save to a DataFrame.
    
    Parameters:
        diagrams_tuple (list): Tuples of diagrams, filename, and topological net.
        output_image_size (tuple): Size of persistent images in pixels.
        savefig (bool): Whether to save persistent images.
        export_folder (str, optional): Folder to save images if savefig=True.

    Returns:
        pd.DataFrame: Persistent image features with filename and topological net columns.
    """

    files, nets, diagrams = zip(*(
    (t[-2], t[-1], tuple(t[:-2])) for t in diagrams_tuple))

    files, nets, diagrams = map(list, (files, nets, diagrams))
    
    # Calculate persistent image features
    image_features, H1_length, H2_length = calc_persistent_image_features(diagrams, files, output_image_size=output_image_size, export_folder=export_folder, savefig=savefig)
    
    # Write out image features to a dataframe
    image_features = np.array(image_features)
    Image_column_names = [f'D1_image_feature_{i+1}' for i in range(H1_length)]
    Image_column_names += [f'D2_image_feature_{i+1}' for i in range(H2_length)]
    image_features_df = pd.DataFrame(image_features, columns=Image_column_names)
    image_features_df['Name'] = files
    image_features_df['Topological Net'] = nets
    return image_features_df