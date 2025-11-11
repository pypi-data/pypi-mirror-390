"""Convert segmentations in mesh format to binary masks."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from traceback import format_exc
from typing import TYPE_CHECKING, Literal, NoReturn

import click
import meshlib.mrmeshnumpy as mn
import meshlib.mrmeshpy as mm
import numpy as np
import SimpleITK as sitk

from stl2mask.helpers import matrix3f, read_image, read_mesh, save_mask

if TYPE_CHECKING:
    from numpy.typing import NDArray

__all__ = ["stl2mask"]

# Configure logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

logger = logging.getLogger(__name__)

Coordinate = tuple[float, float, float]

MAXIMUM_MASK_VALUE = 255


def voxelize_mesh(
    mesh: mm.Mesh, image: sitk.Image, threshold: float = 0.0, offset: float = 0.5, mask_value: int = 255
) -> NDArray[np.uint8]:
    """Convert a mesh to a binary mask.

    `mesh` must be a segmentation of a structure in `image`. The coordinate system of the mask
    will be the same as the image.
    First, for every point in the image space, the distance to the mesh is calculated. This distance
    map is then thresholded to create the mask. Positive distances are outside the mesh, negative
    distances are inside the mesh.

    Parameters
    ----------
    mesh : mm.Mesh
        The input mesh.
    image : sitk.Image
        The image for which the mask is created.
    threshold : float, optional
        Threshold for the distance map. Voxels with a distance less than or equal to this value are
        considered inside the mesh. Defaults to 0.0.
    offset : float, optional
        Offset to apply to the origin of the distance volume in terms of voxel size. This can help
        with alignment issues. Defaults to 0.5.
    mask_value : int, optional
        Value to set the mask voxels to. Must be between 1 and 255. Defaults to 255.

    Returns
    -------
    np.ndarray
        The binary mask as a 3D UInt8 array. The mask has the same size as `image`. Voxels inside the mesh
        are set to `mask_value`, voxels outside the mesh are set to 0.

    """
    if not 1 <= mask_value <= MAXIMUM_MASK_VALUE:
        msg = f"mask_value must be between 1 and 255, got {mask_value}"
        raise ValueError(msg)

    # Get the transform based on the orientation of the image. The transform is defined around the image origin.
    transform = mm.AffineXf3f.xfAround(matrix3f(image.GetDirection()), mm.Vector3f(*image.GetOrigin()))
    transformed_mesh = mm.copyMesh(mesh)

    # Apply the inverse transform to get the mesh in a 'normally' oriented coordinate system
    transformed_mesh.transform(transform.inverse())

    origin = mm.Vector3f(*image.GetOrigin())
    voxel_size = mm.Vector3f(*image.GetSpacing())

    params = mm.MeshToDistanceVolumeParams()
    params.vol.origin = origin + offset * voxel_size
    params.vol.voxelSize = voxel_size
    params.vol.dimensions = mm.Vector3i(*image.GetSize())
    params.dist.signMode = mm.SignDetectionMode.HoleWindingRule

    volume = mm.meshToDistanceVolume(transformed_mesh, params)
    distances = mn.getNumpy3Darray(volume)

    voxels = np.zeros(distances.shape, dtype=np.uint8)
    voxels[distances <= np.float64(threshold)] = mask_value

    return voxels


def mask_to_image(mask: np.ndarray, reference_image: sitk.Image) -> sitk.Image:
    """Convert a binary mask to a SimpleITK Image.

    Parameters
    ----------
    mask : np.ndarray
        The binary mask.
    reference_image : sitk.Image
        Image with the target coordinate system of the mask.

    Returns
    -------
    sitk.Image
        The mask as a SimpleITK Image.

    """
    # Swap axes because the NumPy axis order (z-y-x) is different from the SimpleITK axis order (x-y-z)
    result = sitk.GetImageFromArray(np.swapaxes(mask, 0, 2))

    # Copy metadata including coordinate system from the reference image
    result.CopyInformation(reference_image)

    logger.debug("Reference direction: %s", reference_image.GetDirection())
    logger.debug("Result direction: %s", result.GetDirection())

    return result


def stl2mask(
    mesh_path: Path,
    image_path: Path,
    output_path: Path,
    threshold: float = 0.0,
    offset: float = 0.5,
    mask_value: int = 255,
) -> None:
    """Convert a segmentation in mesh format to a binary mask for a given image.

    The reference image is used to create a grid, on which a distance map to the mesh is calculated.
    This map has negative values for points inside the mesh and positive values for points outside the mesh.
    The distance map is converted to a binary mask by thresholding it at the given threshold value.

    The offset parameter can be used to shift the origin of the coordinate system by a fraction of the voxel size.

    Parameters
    ----------
    mesh_path : Path
        Path to the input mesh file.
    image_path : Path
        Path to the reference image file.
    output_path : Path
        Path to the output mask file.
    threshold : float, optional
        Threshold for the distance map. Voxels with a distance less than or equal to this value are
        considered inside the mesh. Defaults to 0.0.
    offset : float, optional
        Offset to apply to the origin of the distance volume in terms of voxel size. This can help
        with alignment issues. Defaults to 0.5.
    mask_value : int, optional
        Value to set the mask voxels to. Must be between 1 and 255. Defaults to 255.

    """
    logger.debug("Reading mesh from %s", mesh_path)
    mesh = read_mesh(mesh_path)

    logger.debug("Reading reference image from %s", image_path)
    image = read_image(image_path)
    logger.debug("Image dimensions: %s, spacing: %s", image.GetSize(), image.GetSpacing())

    logger.debug("Voxelizing mesh with threshold=%.2f, offset=%.2f, mask_value=%d", threshold, offset, mask_value)
    mask = voxelize_mesh(mesh, image, threshold, offset, mask_value)
    mask_image = mask_to_image(mask, image)

    logger.debug("Saving mask to %s", output_path)
    save_mask(mask_image, output_path)


@click.command()
@click.argument(
    "mesh",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
)
@click.argument(
    "image",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, resolve_path=True, path_type=Path),
    default=None,
    help=(
        "Output file path. If not provided, the output file will be created in the same directory "
        "as the mesh file with the same name and a different suffix."
    ),
)
@click.option(
    "--suffix",
    "-s",
    type=str,
    default=".nii.gz",
    show_default=True,
    help="Suffix for the output file if --output is not provided. Must be a valid file suffix for SimpleITK.",
)
@click.option(
    "--threshold",
    "-t",
    type=float,
    default=0.0,
    show_default=True,
    help=(
        "Threshold for the distance map. Voxels with a distance less than or "
        "equal to this value are considered inside the mesh."
    ),
)
@click.option(
    "--offset",
    "-f",
    type=float,
    default=0.5,
    show_default=True,
    help=(
        "Offset to apply to the origin of the distance volume in terms of voxel size. "
        "This can help with alignment issues."
    ),
)
@click.option(
    "--mask-value",
    "-m",
    type=click.IntRange(1, 255),
    default=255,
    show_default=True,
    help="Value to set the mask voxels to.",
)
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="INFO",
    show_default=True,
    help="Set the logging level.",
)
def cli(
    mesh: Path,
    image: Path,
    output: Path | None = None,
    suffix: str = ".nii.gz",
    threshold: float = 0.0,
    offset: float = 0.5,
    mask_value: int = 255,
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO",
) -> NoReturn:
    """Convert a segmentation MESH to a binary mask for a given IMAGE."""
    # Configure logging level based on user input
    logging.getLogger().setLevel(log_level)

    if not suffix.startswith("."):
        msg = "Suffix must start with a dot (e.g. .nii.gz)"
        raise click.BadParameter(msg)

    if output is None:
        output = mesh.with_suffix(suffix)
    elif not output.suffix:
        output = output.with_suffix(suffix)
    elif output.suffix != suffix:
        msg = "⚠️ Output suffix does not match provided suffix. Ignoring provided suffix."
        click.secho(msg, fg="yellow")

    try:
        stl2mask(
            mesh_path=mesh,
            image_path=image,
            output_path=output,
            threshold=threshold,
            offset=offset,
            mask_value=mask_value,
        )
    except RuntimeError as e:
        click.secho(f"❌ {e}", fg="red")
        logger.debug("Full traceback: %s", format_exc())
        sys.exit(1)

    click.secho(f"✅ Mask written to {output}", fg="green")
    sys.exit(0)


if __name__ == "__main__":
    cli()
