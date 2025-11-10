import numpy as np
import os
import pickle
from ripser import Rips
import phun_reps.topology as tp
import matplotlib.pyplot as plt

def get_cif_files(folder, limit=None):
    """
    Return a list of .cif files in the specified folder.

    Parameters:
        folder (str): Directory to search for .cif files.
        limit (int or None): Maximum number of files to return; None returns all files.

    Returns:
        list: Paths to .cif files.
    """

    directory = os.fsencode(folder)
    cif_files = [
        os.path.join(folder, os.fsdecode(f))
        for f in os.listdir(directory)
        if os.fsdecode(f).endswith(".cif")
    ]
    if limit is None:
        return cif_files
    return cif_files[:limit]

def process_single_data(data, filename=None, net=None, maxdim=2, coeff=2):
    """
    Compute persistence diagrams for a single point cloud dataset.

    Parameters:
        data (np.ndarray): Point cloud coordinates.
        filename (str, optional): Name of the source file.
        net (str, optional): Topological net label.
        maxdim (int): Maximum homology dimension.
        coeff (int): Field coefficient for persistent homology.

    Returns:
        tuple: D0, D1, D2 persistence diagrams, filename, and net.
    """
    rips = Rips(maxdim=maxdim, coeff=coeff, verbose=False)
    dgms = rips.fit_transform(data)

    D0_dgm = dgms[0][:-1]  # Remove infinite value in H0
    D1_dgm = dgms[1]
    D2_dgm = dgms[2] if len(dgms) > 2 else np.array([[0, 0]])

    return D0_dgm, D1_dgm, D2_dgm, filename, net


def calc_persistent_diagrams(dataset, files=None, top_net=None, maxdim=2, coeff=2):
    """
    Compute persistence diagrams for a dataset of point clouds.

    Parameters:
        dataset (list): List of point cloud arrays.
        files (list, optional): Corresponding filenames.
        top_net (list, optional): Topological net labels.
        maxdim (int): Maximum homology dimension.
        coeff (int): Field coefficient.

    Returns:
        list: Tuples of persistence diagrams and metadata for each point cloud.
    """
    results = []

    for idx, data in enumerate(dataset):
        filename = files[idx] if files is not None else None
        net = top_net[idx] if top_net is not None else None
        print(f"Processing array {idx + 1}/{len(dataset)} with shape {data.shape}")

        diagram = process_single_data(data, filename, net, maxdim, coeff)

        results.append(diagram)

    print("Processing complete.")
    return results

def build_dataset(files, export_folder="/tmp", clustering='SingleNodes'):
    """
    Build a dataset of point clouds and their corresponding topological nets.

    Parameters:
        files (list): List of .cif files.
        export_folder (str): Folder to store VTF files.
        clustering (str): Topology clustering method.

    Returns:
        tuple: (dataset, top_nets, names)
            dataset (list of np.ndarray): Point clouds.
            top_nets (list of str): Predicted topological nets.
            names (list of str): Filenames.
    """
    dataset, top_nets, names = [], [], []

    for filename in files:
        # Get point cloud data
        coords, _, result = tp.get_point_cloud(filename, export_folder, clustering=clustering, structure="MOF")
        if coords is None:
            print(f"Skipping {filename} due to None result.")
            continue
        dataset.append(np.array(coords))
        top_nets.append(str(result))
        names.append(filename)

    return dataset, top_nets, names

def save_diagrams(save_file, data):
    """
    Save persistent diagrams to a pickle file.

    Parameters:
        save_file (str): Path to save pickle file.
        data (list): Persistence diagrams and metadata.
    """
    with open(save_file, "wb") as f:
        pickle.dump(data, f)
    print(f"Saved persistent diagrams to {save_file}")

def plot_persistent_diagrams(diagram_tuples, export_folder):
  
    files, nets, diagrams = zip(*(
        (t[-2], t[-1], tuple(t[:-2])) for t in diagram_tuples
    ))
    files, nets, diagrams = map(list, (files, nets, diagrams))

    os.makedirs(export_folder, exist_ok=True)

    for file, diagram in zip(files, diagrams):
        d0, d1, d2 = diagram

        # Get finite deaths safely
        finite_deaths = []
        if len(d0) > 0:
            finite_deaths.extend(d0[:, 1])
        if len(d1) > 0:
            finite_deaths.extend(d1[:, 1])
        max_death = max(finite_deaths) if finite_deaths else 1

        # ---- Plot persistence diagram ----
        fig, ax = plt.subplots(figsize=(7, 7))

        ax.set_title("Persistence Diagram", fontsize=28, fontweight="bold")
        ax.set_xlabel("Birth", fontsize=26, fontweight="bold")
        ax.set_ylabel("Death", fontsize=26, fontweight="bold")

        ax.tick_params(axis='both', labelsize=24, width=2)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight("bold")

        for spine in ax.spines.values():
            spine.set_linewidth(3)

        ax.plot([0, max_death * 1.1], [0, max_death * 1.1], "k--", linewidth=3)
    
        if len(d0) > 0:
            ax.scatter(d0[:, 0], d0[:, 1], c="#c00000", s=200, label="0D (Connected Components)")
        if len(d1) > 0:
            ax.scatter(d1[:, 0], d1[:, 1], c="#1f497d", s=200, label="1D (Loops)")
        if len(d2) > 0:
            ax.scatter(d2[:, 0], d2[:, 1], c="green", s=200, label="2D (Voids)")

        legend = ax.legend(
            fontsize=14,
            markerscale=1,
            frameon=False)
        
        for text in legend.get_texts():
            text.set_fontweight("bold")
        basename = os.path.basename(file)
        plt.tight_layout()
        plt.savefig(f"{export_folder}/{basename}_persistence_diagram.png", dpi=300)
        plt.close(fig) 
    return print(f"Saved persistent diagam plots to {export_folder}" )


def get_persistent_diagrams(dataset, names, top_nets, maxdim=2, coeff=2, save_file=None):
    """
    Plot and save persistence diagrams for H0, H1, and H2.

    Parameters:
        diagram_tuples (list): Tuples of diagrams, filenames, and nets.
        export_folder (str): Folder to save plots.

    Returns:
        None
    """
    data = calc_persistent_diagrams(dataset, names, top_nets, maxdim=2, coeff=2)
    if save_file is not None:
        save_diagrams(save_file, data)
    
    return data
