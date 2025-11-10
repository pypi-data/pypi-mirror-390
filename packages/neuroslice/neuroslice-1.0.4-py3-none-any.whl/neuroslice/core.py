""" Core functions for NeuroSlice. """
import cv2
import nibabel as nib
import numpy as np
from tqdm import tqdm
from ultralytics import YOLO
import pathlib
from .utils import download_model


def mask2cuboid(mask: np.ndarray) -> np.ndarray:
    """Convert a binary mask to its bounding cuboid mask.

    Args:
        mask (numpy.ndarray): 3D binary mask.

    Returns:
        numpy.ndarray: 3D binary mask of the bounding cuboid.
    """

    if np.sum(mask) == 0:
        return mask

    coords = np.argwhere(mask)
    minx, miny, minz = coords.min(axis=0)
    maxx, maxy, maxz = coords.max(axis=0)
    new_mask = np.zeros_like(mask)
    new_mask[minx:maxx + 1, miny:maxy + 1, minz:maxz + 1] = 1
    return new_mask


def unite_masks(*masks: np.ndarray) -> np.ndarray:
    """Combine multiple binary masks into one using union or cuboid.

    Args:
        *masks (numpy.ndarray): Multiple binary masks to combine.

    Returns:
        numpy.ndarray: Union of the binary masks listed.
    """
    result = masks[0].astype(bool)
    for mask in masks[1:]:
        result |= mask.astype(bool)
    return result.astype(np.uint8)


def predict(data: np.ndarray, axis: int, verbose: bool = False) -> np.ndarray:
    """Generate a binary tumor mask from a 3D image array using a trained YOLO model.

    Args:
        data (numpy.ndarray): 3D image array (e.g., FLAIR image).
        axis (int): Axis along which to slice the 3D image (0: sagittal, 1: coronal, 2: axial).
        verbose (bool): Whether to print statistics.

    Returns:
        numpy.ndarray: Binary mask of detected tumor regions.
    """

    assert axis in [0, 1, 2], "Axis must be 0 (sagittal), 1 (coronal), or 2 (axial)."

    # Load the YOLO model
    model_path = download_model(axis, verbose)
    model = YOLO(model_path)

    # Initialize binary mask with same shape as input
    binary_mask = np.zeros_like(data, dtype=np.uint8)
    n_slices = data.shape[axis]

    # Process each slice
    for i in tqdm(range(n_slices), desc=f"Detecting tumors in axis={axis}", disable=not verbose):
        # Extract slice
        if axis == 0:
            slice_data = data[i, :, :]
        elif axis == 1:
            slice_data = data[:, i, :]
        else:
            slice_data = data[:, :, i]

        # Normalize slice to 0-255 for YOLO input
        slice_min, slice_max = np.min(slice_data), np.max(slice_data)
        if slice_max - slice_min == 0:
            continue  # Skip empty slices
        normalized_slice = ((slice_data - slice_min) / (slice_max - slice_min) * 255).astype(
            np.uint8)

        # Convert to BGR format for YOLO (expects 3-channel image)
        slice_bgr = cv2.cvtColor(normalized_slice, cv2.COLOR_GRAY2RGB)

        # Run YOLO prediction
        results = model.predict(slice_bgr, verbose=False)
        if len(results) == 0 or len(results[0].boxes) == 0:
            continue

        # Process detections
        h, w = slice_data.shape
        for box in results[0].boxes:
            # Get bounding box in YOLO format (normalized)
            x_center, y_center, width, height = box.xywhn[0].tolist()

            # Convert to pixel coordinates
            x1 = int((x_center - width / 2) * w)
            y1 = int((y_center - height / 2) * h)
            x2 = int((x_center + width / 2) * w)
            y2 = int((y_center + height / 2) * h)

            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            # Directly fill per-box region
            if axis == 0:
                binary_mask[i, y1:y2, x1:x2] = 1
            elif axis == 1:
                binary_mask[y1:y2, i, x1:x2] = 1
            else:
                binary_mask[y1:y2, x1:x2, i] = 1

    if verbose:
        # Print statistics
        tumor_voxels = np.sum(binary_mask)
        total_voxels = binary_mask.size
        tumor_percentage = (tumor_voxels / total_voxels) * 100

        print("Segmentation complete!")
        print(f"   Total voxels: {total_voxels:,}")
        print(f"   Tumor voxels: {tumor_voxels:,}")
        print(f"   Tumor percentage: {tumor_percentage:.2f}%")

    return binary_mask


def predict_multi_axis(data: np.ndarray, axes: list, verbose: bool = False):
    """Generate a binary tumor mask from a 3D image array using a trained
    YOLO model along multiple axes.

    Args:
        data (numpy.ndarray): 3D image array (e.g., FLAIR image).
        axes (list of int): List of axes along which to slice the
        3D image (0: sagittal, 1: coronal, 2: axial).
        verbose (bool): Whether to print statistics.

    Returns:
        numpy.ndarray: Combined binary mask of detected tumor regions.
    """
    masks = []
    for axis in axes:
        if verbose:
            print(f"Processing axis {axis}...")
        mask = predict(data, axis, verbose)
        masks.append(mask)

    combined_mask = unite_masks(*masks)

    return combined_mask


def predict_mask(nifti_path: str, axis: int | list, verbose: bool = False):
    """Generate a binary tumor mask from a 3D NIfTI image using a trained YOLO model.

    Args:
        nifti_path (str): Path to the input NIfTI file (e.g., FLAIR image).
        axis (int or list of int): Axis or list of axes along which to slice
        the 3D image (0: sagittal, 1: coronal, 2: axial).
        verbose (bool): Whether to print statistics.

    Returns:
        numpy.ndarray: Binary mask of detected tumor regions.
    """

    if isinstance(nifti_path, pathlib.Path):
        nifti_path = str(nifti_path)

    # Load the NIfTI image
    nifti = nib.load(nifti_path)
    data = nifti.get_fdata()

    # Predict the binary mask
    if verbose:
        print("Generating tumor mask...")

    if isinstance(axis, list):
        binary_mask = predict_multi_axis(data, axis, verbose=verbose)
    else:
        binary_mask = predict(data, axis, verbose)

    return binary_mask
