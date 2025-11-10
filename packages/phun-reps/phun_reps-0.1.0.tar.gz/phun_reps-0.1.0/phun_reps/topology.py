import numpy as np
import os
from ase.visualize import view
from ase import Atoms
import juliacall


# Initialize Julia module
jl = juliacall.newmodule("TopologyforMOFs")
jl.seval("using CrystalNets")
jl.CrystalNets.toggle_warning(False)
jl.CrystalNets.toggle_export(False)


def create_supercell(coordinates, pbc, replication_factors):
    """
    Generate a supercell by replicating the input coordinates along the lattice vectors.
    
    Parameters:
        coordinates (np.ndarray): Atomic coordinates of the unit cell.
        pbc (np.ndarray): Periodic boundary condition vectors (cell lengths).
        replication_factors (tuple): Number of repetitions along each axis (nx, ny, nz).
    
    Returns:
        np.ndarray: Coordinates of the expanded supercell.
    """
    lattice_vectors = np.array([
        [pbc[0], 0, 0],
        [0, pbc[1], 0],
        [0, 0, pbc[2]]
    ])

    nx, ny, nz = replication_factors
    supercell_coords = [
        coord + i * lattice_vectors[0] + j * lattice_vectors[1] + k * lattice_vectors[2]
        for i in range(nx)
        for j in range(ny)
        for k in range(nz)
        for coord in coordinates
    ]

    return np.unique(np.array(supercell_coords), axis=0)


def create_ase_structure(coordinates, pbc, view_structure=False):
    """
    Create an ASE Atoms object from coordinates and periodic boundary conditions.
    
    Parameters:
        coordinates (np.ndarray): Atomic positions.
        pbc (np.ndarray): Lattice vectors or cell lengths.
        view_structure (bool): If True, open ASE GUI to visualize the structure.
    
    Returns:
        Atoms: ASE Atoms object representing the structure.
    """
    atoms = Atoms(positions=coordinates, symbols='Zn' * len(coordinates), pbc=True, cell=pbc[:3])
    if view_structure:
        view(atoms)
    return atoms

def extract_coordinates_from_VTF(filename, supercell=None, wrap_pbc=False):
    """
    Extract atomic coordinates and periodic boundary conditions from a VTF file.
    
    Parameters:
        filename (str): Path to the VTF file.
        supercell (tuple or None): Optional replication factors to create a supercell.
        wrap_pbc (bool): If True, filter coordinates to lie within the unit cell.
    
    Returns:
        tuple: (coordinates, pbc) as numpy arrays. Coordinates may be expanded if supercell is provided.
    """

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return None

    ordered_start = False
    coordinates = []
    pbc = None

    for line in lines:
        line = line.strip()
        if line.startswith('pbc'):
            pbc = list(map(float, line.split()[1:]))
        if line == 'ordered':
            ordered_start = True
            continue
        if ordered_start:
            try:
                coords = list(map(float, line.split()))
                coordinates.append(coords)
            except ValueError:
                break

    coordinates = np.array(coordinates)
    pbc = np.array(pbc) if pbc is not None else None

    if wrap_pbc and pbc is not None:
        coordinates = np.array([coord for coord in coordinates if all(0 <= coord[i] < pbc[i] for i in range(3))])

    if supercell is None:
        return coordinates, pbc
    else:
        return create_supercell(coordinates, pbc, supercell), pbc


def find_vtf_files(export_folder, clustering, file_basename):
    """
    Find all VTF files in the export folder matching a given clustering type and file basename.
    
    Parameters:
        export_folder (str): Folder containing VTF files.
        clustering (str): Clustering type used (e.g., 'SingleNodes').
        file_basename (str): Base name of the original CIF file.
    
    Returns:
        list: Paths to matching VTF files.
    """

    vtf_files = []
    search_path = os.path.join(export_folder, export_folder)
    if not os.path.exists(search_path):
        print(f"Error: Directory '{search_path}' does not exist.")
        return []

    search_pattern = f"subnet_{clustering}_{file_basename}_"
    for root, _, files in os.walk(search_path):
        for file in files:
            if file.startswith(search_pattern) and file.endswith(".vtf"):
                vtf_files.append(os.path.join(root, file))
    return vtf_files


def get_point_cloud(filename, export_folder, clustering='input', supercell=None, wrap_pbc=False, structure="MOF"):
    """
    Extract atomic coordinates and PBCs from VTF files via CrystalNets.jl.

    Parameters:
        filename (str): Input CIF file.
        export_folder (str): Folder to save outputs.
        clustering (str): Topology clustering ('input', 'SingleNodes', 'Standard', 'AllNodes', 'PE', 'PEM').
        supercell (tuple|None): Supercell replication.
        wrap_pbc (bool): Wrap coordinates by PBC.
        structure (str): 'MOF' or 'Zeolite'.

    Returns:
        coordinates (np.ndarray), pbc (np.ndarray), result (str|None)
    """

    if not os.path.isfile(filename):
        raise FileNotFoundError(f"File '{filename}' not found.")
    if not os.path.isdir(export_folder):
        os.makedirs(export_folder)

    file_basename = os.path.basename(filename)[:-4]

    structure_types = {'MOF': jl.StructureType.MOF, 'Zeolite': jl.StructureType.MOF}
    if structure not in structure_types:
        raise ValueError("Invalid structure. Options: 'MOF', 'Zeolite'")

    clustering_options = {
        'SingleNodes': jl.Clustering.SingleNodes,
        'Standard': jl.Clustering.Standard,
        'AllNodes': jl.Clustering.AllNodes,
        'PE': jl.Clustering.PE,
        'PEM': jl.Clustering.PEM
    }

    if clustering == 'input':
        options = jl.CrystalNets.Options(
            structure=structure_types[structure],
            export_input=export_folder,
            export_subnets=False
        )
        jl.determine_topology(filename, options)
        vtf_file = [f"{export_folder}/{export_folder}/{clustering}_{file_basename}.vtf"]
        result = None
    elif clustering in clustering_options:
        options = jl.CrystalNets.Options(
            structure=structure_types[structure],
            clusterings=[clustering_options[clustering]],
            export_input=False,
            export_subnets=export_folder
        )
        result = str(jl.determine_topology(filename, options)).split(": ", 1)[1]
    
        vtf_file = find_vtf_files(export_folder, clustering, file_basename)
    else:
        raise ValueError(f"Invalid clustering option: {clustering}")

    # Extract coordinates from all VTF files
    coordinates = None
    pbc = None
    if not vtf_file:
        print("No VTF files found.")
    else:
        for file in vtf_file:
            coord, pbc_file = extract_coordinates_from_VTF(file, supercell, wrap_pbc)
            if coordinates is None:
                coordinates = coord
            else:
                coordinates = np.vstack((coordinates, coord))
            pbc = pbc_file

    return coordinates, pbc, result


