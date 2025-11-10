# PHuN representations
This is a fun and computationally efficient Python package for computing persistent homology using nets (PHuN) representations of nanoporous materials. It enables the extraction of topological information for use as machine learning descriptors.

## Installation Guide

### Prerequisites

**PHuN** requires the [CrystalNets.jl](https://coudertlab.github.io/CrystalNets.jl/dev/python/) Julia interface, which is used to identify and extract the topological nets of nanoporous materials.

### Install phun_reps using pip
```bash
pip install phun_reps
```
This package was built and tested with Python 3.10.13,
and will automatically install its dependencies:
`ase==3.26.0`, `Cython==3.2.0`, `juliacall==0.9.28`, `pandas==2.3.3`, and `ripser==0.6.12`.

## Usage

**PHuN** provides tools to compute persistent homology diagrams for nanoporous materials using either:

* Atomic coordinates

* Topological nets derived from CrystalNets.jl.

It integrates with [Ripser](https://ripser.scikit-tda.org/en/latest/) to compute persistence diagrams and can extract topological descriptors for machine learning.

**PHuN** can be used to:

* Generate persistent diagrams/images from CIF files

* Visualize persistence diagrams/images

* Extract topological descriptors (persistent image features and persistent statistics features) that can be used for machine learning

For a complete example of usage, see the Example Usage section below.

## Example Usage 

### Initial setup 

```python
# Folder containing .cif files to process
folder = "test-cif"

# Folder where CrystalNets.jl outputs will be saved
# Default is /tmp if not specified
export_folder = "/tmp"

# Clustering option for CrystalNets.jl
# Determines how topological nets are identified
clustering = 'SingleNodes'
```

### Load .cif files
```python
import phun_reps.calc_presistent_diagram as cp
# Load .cif files from the specified folder
files = cp.get_cif_files(folder)
```

### Build dataset

```python
import phun_reps.calc_presistent_diagram as cp
# Build dataset:
# - Uses CrystalNets.jl to identify topological nets based on clustering option. If ACPH features are wanted, set clustering to 'input'
dataset, top_nets, names = cp.build_dataset(files, export_folder, clustering)
```

### Compute persistent diagrams
```python
import phun_reps.calc_presistent_diagram as cp
# Compute persistent homology diagrams from the dataset
diagrams_tuples = cp.get_persistent_diagrams(
    dataset, names, top_nets,
    maxdim=2, coeff=2,
    save_file=f"diagrams_{folder}_{clustering}.pkl"
)
```
### Extract persistent image features from diagrams using persim
```python
import phun_reps.feature_extraction as fe
image_features_df = fe.get_persistent_image_features(
    diagrams_tuples,
    output_image_size=(30, 30),
    savefig=True,
    export_folder="test_images"
)
```
### Extract statistical features from persistent diagrams

```python
import phun_reps.feature_extraction as fe
stats_features_df = fe.get_persistent_stats_features(diagrams_tuples)
```


