# Neuroslice

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-360/)

A Python package for brain tumor segmentation using YOLO models on MRI FLAIR data.

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
- [Contributing](#contributing)
- [Citation](#citation)

## Description

Neuroslice provides automated brain tumor bounding box detection using pre-trained YOLO models. It uses FLAIR images to segment slice wise the image, though an option to afterwards create a cuboid is available.
The package supports three slice orientations (coronal, sagittal, and axial) as well as combinations of them.
Models are automatically downloaded from [Hugging Face](https://huggingface.co/anamatoso/neuroslice) when first used.

## Installation

You can install Neuroslice using pip:

```bash
pip install neuroslice
```

For development installation:

```bash
git clone https://github.com/anamatoso/neuroslice.git
cd neuroslice
pip install -e .
```

## Usage

### Command Line Interface

Basic usage with default settings (coronal direction, union mode):

```bash
neuroslice input.nii.gz output_mask.nii.gz
```

Specify slice direction and processing mode:

```bash
neuroslice input.nii.gz output_mask.nii.gz --axis 2 --mode cuboid --verbose
```

Use the combination of diferent orientations:

```bash
neuroslice input.nii.gz output_mask.nii.gz --axis 0,1
```

**Arguments:**

Mandatory:

- `input`: Path to input NIfTI file (.nii or .nii.gz)
- `output`: Path to output mask NIfTI file

Optional:

- `--direction`: Slice axis (RAS) - 0 (sagittal), 1 (coronal, default), 2 (axial)
- `--mode`: Processing mode - `union` (default) or `cuboid` (bounding box)
- `--verbose`: Print detailed statistics

### Python API

**Generate a tumor mask:**

```python
from neuroslice import predict_mask
import nibabel as nib

# Generate mask from NIfTI file
mask = predict_mask("input.nii.gz", axis=2, verbose=True)

# Save the mask
nifti = nib.load("input.nii.gz")
output = nib.Nifti1Image(mask.astype("uint8"), nifti.affine, nifti.header)
nib.save(output, "output_mask.nii.gz")
```

**Convert mask to bounding cuboid:**

```python
from neuroslice import mask2cuboid

cuboid_mask = mask2cuboid(mask)
```

**Combine multiple masks:**

```python
from neuroslice import unite_masks

combined = unite_masks(mask1, mask2, mask3)

```

**Advanced usage with direct predict function:**

```python
from neuroslice import predict, predict_multi_axis
import nibabel as nib

# Load your data
nifti = nib.load("input.nii.gz")
data = nifti.get_fdata()

# Generate mask with custom axis 
mask = predict(data, axis=0, mode="union", verbose=True)

mask_cuboid = predict_multi_axis(data, axis=[0,1], mode="cuboid"):
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
If you want to ask for changes, create an issue detailing what you want changed and someone will look into it.

More information on how to contribute can be found in the documentation.

## Citation

If you use Neuroslice in your research, please cite:

TBD

<!-- ```bibtex
@software{neuroslice,
  title = {Neuroslice: Brain Tumor Segmentation using YOLO},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/neuroslice}
}
``` -->
