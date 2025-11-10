""" Command-line interface for NeuroSlice. """
import argparse
import os
import sys

import nibabel as nib

from .core import mask2cuboid, predict, predict_multi_axis


def main():
    """ Main function for NeuroSlice CLI. """
    def parse_axis(value: str):
        """Parse axis as either a single int or comma-separated list of ints"""
        if ',' in value:
            axis = [int(x.strip()) for x in value.split(',')]
        else:
            axis = int(value)
        return axis

    parser = argparse.ArgumentParser(
        description="Neuroslice: Brain tumor segmentation using YOLO"
    )
    parser.add_argument(
        "input",
        type=str,
        help="Path to input NIfTI file (.nii or .nii.gz)"
    )
    parser.add_argument(
        "output",
        type=str,
        help="Path to output mask NIfTI file"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="union",
        choices=["union", "cuboid"],
        help="Processing mode: union or cuboid (bounding box)"
    )
    parser.add_argument(
        "--axis",
        type=parse_axis,
        default=1,
        help="Slice direction for single-direction mode (default: 1 = coronal) or multiple \
        axes as comma-separated list (e.g., 1,2)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed statistics"
    )

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        return 1

    # Load NIfTI for later saving
    nifti = nib.load(args.input)
    data = nifti.get_fdata()

    # Generate mask
    if isinstance(args.axis, list):
        mask = predict_multi_axis(data, args.axis, args.verbose)
    else:
        mask = predict(data, args.axis, args.verbose)

    if args.mode == "cuboid":
        mask = mask2cuboid(mask)

    # Save output
    output_nifti = nib.Nifti1Image(mask.astype("uint8"), nifti.affine, nifti.header)
    nib.save(output_nifti, args.output)
    if args.verbose:
        print(f"Mask saved to: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
