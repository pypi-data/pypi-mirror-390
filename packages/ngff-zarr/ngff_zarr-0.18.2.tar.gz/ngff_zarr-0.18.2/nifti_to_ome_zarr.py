#!/usr/bin/env python3
"""
NIfTI to OME-Zarr Converter

This script loads a NIfTI file using nibabel, extracts spatial metadata,
displays information with rich, and converts to OME-Zarr format using ngff-zarr.

Date: September 30, 2025
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Tuple, Optional

import numpy as np
import nibabel as nib
import dask.array as da
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Import ngff-zarr modules
from ngff_zarr import NgffImage, to_multiscales, to_ngff_zarr
from ngff_zarr.rfc4 import AnatomicalOrientation, AnatomicalOrientationValues


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert NIfTI files to OME-Zarr format",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Input NIfTI file (.nii or .nii.gz)"
    )
    parser.add_argument(
        "--output-v04",
        type=Path,
        default=Path("output_v04.ome.zarr"),
        help="Output OME-Zarr v0.4 path (default: output_v04.ome.zarr)"
    )
    parser.add_argument(
        "--output-v05",
        type=Path,
        default=Path("output_v05.ome.zarr"),
        help="Output OME-Zarr v0.5 path with sharding (default: output_v05.ome.zarr)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        nargs="+",
        help="Chunk sizes for each dimension (defaults to image shape // 4)"
    )
    return parser.parse_args()


def load_nifti_image(input_path: Path):
    """Load NIfTI image using nibabel."""
    console = Console()

    if not input_path.exists():
        console.print(f"[red]Error: File {input_path} does not exist[/red]")
        sys.exit(1)

    try:
        img = nib.load(str(input_path))
        console.print(f"[green]Successfully loaded NIfTI file: {input_path}[/green]")
        return img
    except Exception as e:
        console.print(f"[red]Error loading NIfTI file: {e}[/red]")
        sys.exit(1)

def decompose_affine_with_shear(affine):
    # Affine top-left 3x3: linear (rotation, scale, shear), last column: translation
    matrix = affine[:3, :3]
    translation = affine[:3, 3]

    # Extract scale: norm of each column (preserves axis order)
    scale = np.linalg.norm(matrix, axis=0)

    # Normalize columns to remove scale for shear/orientation steps
    normed_matrix = matrix / scale

    # Shear extraction (per scipy/ITK/transforms3d conventions)
    shear_xy = np.dot(normed_matrix[:, 0], normed_matrix[:, 1])
    y_orth = normed_matrix[:, 1] - shear_xy * normed_matrix[:, 0]
    shear_y = np.linalg.norm(y_orth)
    shear_xz = np.dot(normed_matrix[:, 0], normed_matrix[:, 2])
    shear_yz = np.dot(normed_matrix[:, 1], normed_matrix[:, 2])
    z_orth = normed_matrix[:, 2] - shear_xz * normed_matrix[:, 0] - shear_yz * normed_matrix[:, 1]
    shear_z = np.linalg.norm(z_orth)

    shear = np.array([shear_xy, shear_xz, shear_yz])

    # Orthonormal rotation/orientation: Gram-Schmidt
    x = normed_matrix[:, 0]
    y = y_orth / shear_y
    z = z_orth / shear_z
    orientation = np.stack([x, y, z], axis=1)

    # Compose explicit scale and shear matrices
    scale_matrix = np.diag(scale)
    shear_matrix = np.array([[1, shear_xy, shear_xz],
                             [0,     1,   shear_yz],
                             [0,     0,      1    ]])

    # The "remaining affine" is shear * orientation
    remaining_affine_matrix = orientation @ shear_matrix

    return {
        "translation": translation,
        "scale": scale,                # pixel spacing in x,y,z order
        "shear": shear,                # [shear_xy, shear_xz, shear_yz]
        "orientation": orientation,    # rotation (orthonormal, columns x y z)
        "remaining_affine": remaining_affine_matrix
    }


def extract_spatial_metadata(img) -> Tuple[Dict[str, float], Dict[str, float], np.ndarray]:
    """Extract translation, scale, and orientation from NIfTI spatial metadata."""
    # Get the affine transformation matrix
    affine = img.affine

    # Use axis-preserving decomposition
    decomposition = decompose_affine_with_shear(affine)

    # Get image dimensions
    shape = img.shape

    # Create scale and translation dictionaries for spatial dimensions
    if len(shape) >= 3:
        # NIfTI uses RAS+ coordinate system, but array indexing is in reverse order
        # The affine maps from voxel coordinates (i,j,k) to world coordinates (x,y,z)
        # Array dimensions are typically (z,y,x) or (t,z,y,x)
        spatial_dims = ['x', 'y', 'z']  # World coordinate order
        scale_dict = {dim: float(decomposition["scale"][i]) for i, dim in enumerate(spatial_dims)}
        translation_dict = {dim: float(decomposition["translation"][i]) for i, dim in enumerate(spatial_dims)}

        # Add time dimension if 4D
        if len(shape) == 4:
            scale_dict['t'] = 1.0
            translation_dict['t'] = 0.0
    else:
        raise ValueError(f"Image must have at least 3 dimensions, got {len(shape)}")

    return scale_dict, translation_dict, affine

def display_image_info(img, scale_dict: Dict[str, float],
                      translation_dict: Dict[str, float], affine: np.ndarray):
    """Display comprehensive image information using Rich."""
    console = Console()

    # Create pixel buffer information table
    pixel_table = Table(title="Pixel Buffer Information")
    pixel_table.add_column("Property", style="cyan")
    pixel_table.add_column("Value", style="green")

    pixel_table.add_row("Shape", str(img.shape))
    pixel_table.add_row("Data Type", str(img.get_fdata().dtype))
    pixel_table.add_row("Size (bytes)", str(img.get_fdata().nbytes))
    pixel_table.add_row("Min Value", f"{np.min(img.get_fdata()):.6f}")
    pixel_table.add_row("Max Value", f"{np.max(img.get_fdata()):.6f}")
    pixel_table.add_row("Mean Value", f"{np.mean(img.get_fdata()):.6f}")

    # Create spatial metadata table
    spatial_table = Table(title="Spatial Metadata")
    spatial_table.add_column("Dimension", style="cyan")
    spatial_table.add_column("Scale (Spacing)", style="yellow")
    spatial_table.add_column("Translation (Origin)", style="magenta")

    for dim in scale_dict.keys():
        spatial_table.add_row(
            dim.upper(),
            f"{scale_dict[dim]:.6f}",
            f"{translation_dict[dim]:.6f}"
        )

    # Get detailed affine decomposition for display
    decomposition = decompose_affine_with_shear(affine)

    # Display affine matrix and decomposition
    affine_text = Text()
    affine_text.append("Affine Transformation Matrix:\n", style="bold")
    affine_text.append(str(affine))
    affine_text.append("\n\nDecomposition:\n", style="bold")
    affine_text.append(f"Translation (world coordinates): {decomposition['translation']}\n")
    affine_text.append(f"Scale (voxel sizes): {decomposition['scale']}\n")
    affine_text.append(f"Orientation matrix:\n{decomposition['orientation']}")

    # Display all information
    console.print(Panel(pixel_table, title="[bold blue]NIfTI Image Analysis[/bold blue]"))
    console.print(Panel(spatial_table, title="[bold blue]Spatial Information[/bold blue]"))
    console.print(Panel(affine_text, title="[bold blue]Coordinate Transformation[/bold blue]"))

def create_ngff_image(img, scale_dict: Dict[str, float],
                     translation_dict: Dict[str, float], chunk_size: Optional[list] = None) -> NgffImage:
    """Create NgffImage with RAS anatomical orientation."""
    console = Console()

    # Get image data as numpy array
    data = img.get_fdata()

    # Determine chunk size if not provided
    if chunk_size is None:
        chunk_size = [min(1, 128) for s in data.shape]
    elif len(chunk_size) != len(data.shape):
        console.print(f"[yellow]Warning: Chunk size length ({len(chunk_size)}) doesn't match image dimensions ({len(data.shape)}). Using default.[/yellow]")
        chunk_size = [min(1, 128) for s in data.shape]

    # Create Dask array from numpy array
    dask_array = da.from_array(data, chunks=chunk_size)

    # Define dimension names based on image shape
    if len(data.shape) == 3:
        dims = ['x', 'y', 'z']
    elif len(data.shape) == 4:
        dims = ['x', 'z', 'y', 't']
    else:
        raise ValueError(f"Unsupported number of dimensions: {len(data.shape)}")

    # Create anatomical orientations for spatial dimensions (RAS)
    axes_orientations = {}
    if 'x' in dims:
        axes_orientations['x'] = AnatomicalOrientation(value=AnatomicalOrientationValues.left_to_right)
    if 'y' in dims:
        axes_orientations['y'] = AnatomicalOrientation(value=AnatomicalOrientationValues.posterior_to_anterior)
    if 'z' in dims:
        axes_orientations['z'] = AnatomicalOrientation(value=AnatomicalOrientationValues.inferior_to_superior)

    # Create NgffImage
    ngff_img = NgffImage(
        data=dask_array,
        dims=dims,
        scale=scale_dict,
        translation=translation_dict,
        name="nifti_converted_image",
        axes_orientations=axes_orientations
    )

    console.print(f"[green]Created NgffImage with dimensions: {dims}[/green]")
    console.print(f"[green]Chunk size: {chunk_size}[/green]")
    console.print("[green]RAS anatomical orientation applied to spatial axes[/green]")

    return ngff_img


def write_ome_zarr_outputs(ngff_img: NgffImage, output_v04: Path, output_v05: Path):
    """Generate multiscales and write OME-Zarr outputs."""
    console = Console()

    # Generate multiscales
    console.print("[blue]Generating multiscales...[/blue]")
    multiscales = to_multiscales(ngff_img)

    # Write OME-Zarr v0.4
    console.print(f"[blue]Writing OME-Zarr v0.4 to {output_v04}...[/blue]")
    to_ngff_zarr(
        store=str(output_v04),
        multiscales=multiscales,
        version="0.4"
    )
    console.print(f"[green]OME-Zarr v0.4 written successfully to {output_v04}[/green]")

    # Write OME-Zarr v0.5 with sharding
    console.print(f"[blue]Writing OME-Zarr v0.5 with sharding to {output_v05}...[/blue]")
    to_ngff_zarr(
        store=str(output_v05),
        multiscales=multiscales,
        version="0.5",
        chunks_per_shard=2,  # Use sharding with 2 chunks per shard
        enabled_rfcs=[4]  # Enable RFC 4 for anatomical orientation
    )
    console.print(f"[green]OME-Zarr v0.5 with sharding written successfully to {output_v05}[/green]")


def main():
    """Main function to orchestrate the conversion process."""
    console = Console()

    # Parse command line arguments
    args = parse_arguments()

    console.print(Panel(
        f"[bold cyan]NIfTI to OME-Zarr Converter[/bold cyan]\n\n"
        f"Input: {args.input_file}\n"
        f"Output v0.4: {args.output_v04}\n"
        f"Output v0.5: {args.output_v05}",
        title="Conversion Settings"
    ))

    # Load NIfTI image
    img = load_nifti_image(args.input_file)

    # Extract spatial metadata
    scale_dict, translation_dict, affine = extract_spatial_metadata(img)

    # Display image information
    display_image_info(img, scale_dict, translation_dict, affine)

    # Create NgffImage with RAS orientation
    ngff_img = create_ngff_image(img, scale_dict, translation_dict, args.chunk_size)

    # Write OME-Zarr outputs
    write_ome_zarr_outputs(ngff_img, args.output_v04, args.output_v05)

    console.print(Panel(
        "[bold green]Conversion completed successfully![/bold green]",
        title="Success"
    ))


if __name__ == "__main__":
    main()