"""Convert binary masks to segmentations in mesh format."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from traceback import format_exc
from typing import Literal, NoReturn, cast

import click
import meshlib.mrmeshnumpy as mn
import meshlib.mrmeshpy as mm
import numpy as np
import SimpleITK as sitk

from stl2mask.helpers import matrix3f, read_image, save_mesh

__all__ = ["mask2stl"]

# Configure logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

logger = logging.getLogger(__name__)


def copy_mask_origin_and_direction(mesh: mm.Mesh, mask: sitk.Image) -> None:
    """Apply the mask's direction and origin to the mesh in place.

    Parameters
    ----------
    mesh : mm.Mesh
        The mesh to transform.
    mask : sitk.Image
        The mask image (for original mesh coordinate system).

    """
    mask_direction = np.array(mask.GetDirection()).reshape(3, 3)
    rotation_meshlib = mm.AffineXf3f.linear(matrix3f(tuple(mask_direction.flatten())))
    mesh.transform(rotation_meshlib)

    translation = mm.Vector3f(*mask.GetOrigin())
    transform = mm.AffineXf3f.translation(translation)
    mesh.transform(transform)


def mask_to_mesh(mask: sitk.Image, iso_value: float | None = None) -> mm.Mesh:
    """Convert a binary mask to a mesh using the dual marching cubes algorithm.

    Parameters
    ----------
    mask : sitk.Image
        The binary mask image.
    iso_value : float, optional
        Iso-value for mesh extraction. If None, the mean of the minimum and maximum
        values in the mask is used.

    """
    volume = mn.simpleVolumeFrom3Darray(sitk.GetArrayFromImage(mask).swapaxes(0, 2).astype(np.float64))
    grid = mm.simpleVolumeToDenseGrid(volume)

    if iso_value is None:
        mask_min = np.min(sitk.GetArrayViewFromImage(mask))
        mask_max = np.max(sitk.GetArrayViewFromImage(mask))
        iso_value = cast("float", (mask_min + mask_max) / 2)

    settings = mm.GridToMeshSettings()
    settings.voxelSize = mm.Vector3f(*mask.GetSpacing())
    settings.isoValue = iso_value

    mesh = mm.gridToMesh(grid, settings)

    copy_mask_origin_and_direction(mesh, mask)

    return mesh


def transform_mesh(mesh: mm.Mesh, mask: sitk.Image, image: sitk.Image) -> None:
    """Apply the image's direction, origin, and spacing to the mesh in place.

    Parameters
    ----------
    mesh : mm.Mesh
        The mesh to transform.
    mask : sitk.Image
        The mask image (for original mesh coordinate system).
    image : sitk.Image
        The reference image (for target coordinate system).

    """
    origins_equal = np.allclose(np.array(image.GetOrigin()), np.array(mask.GetOrigin()))
    directions_equal = np.allclose(np.array(image.GetDirection()), np.array(mask.GetDirection()))

    if not directions_equal:
        image_direction = np.array(image.GetDirection()).reshape(3, 3)
        mask_direction = np.array(mask.GetDirection()).reshape(3, 3)

        rotation = image_direction @ np.linalg.inv(mask_direction)
        rotation_meshlib = mm.AffineXf3f.linear(matrix3f(tuple(rotation.flatten())))

        mesh.transform(rotation_meshlib)

    if not origins_equal:
        translation = mm.Vector3f(*image.GetOrigin()) - mm.Vector3f(*mask.GetOrigin())
        transform = mm.AffineXf3f.translation(translation)
        mesh.transform(transform)


MAX_MASK_VALUES = 2


def mask2stl(mask_path: Path, image_path: Path | None, output_path: Path, iso_value: float | None = None) -> None:
    """Convert a binary mask to a mesh and save it to a file.

    The mask contour is extracted using the dual marching cubes algorithm, based
    on the specified iso value. If no iso value is provided, half the maximum
    value in the mask is used. If a reference image is provided, the mesh is
    transformed to the coordinate system of the reference image.

    Parameters
    ----------
    mask_path : Path
        Path to the binary mask image.
    image_path : Path
        Path to the reference image (for coordinate system).
    output_path : Path
        Path to save the output mesh.
    iso_value : float, optional
        Iso-value for mesh extraction. If None, the mean of the minimum and maximum
        values in the mask is used.

    """
    logger.debug("Reading mask from %s", mask_path)
    mask = read_image(mask_path)
    logger.debug("Mask dimensions: %s, spacing: %s", mask.GetSize(), mask.GetSpacing())

    mask_values = np.unique(sitk.GetArrayViewFromImage(mask))
    if mask_values.size > MAX_MASK_VALUES:
        msg = f"The input mask should be a binary image with at most two different values. Got {mask_values.tolist()}."
        raise ValueError(msg)

    if iso_value is not None and (iso_value <= np.min(mask_values) or iso_value >= np.max(mask_values)):
        msg = f"The iso value should be between the minimum and maximum values in the mask. Got {iso_value}."
        raise ValueError(msg)

    image = read_image(image_path) if image_path else None
    if image is not None:
        logger.debug("Using reference image from %s", image_path)

    logger.debug("Converting mask to mesh using iso-value: %s", iso_value if iso_value is not None else "auto")
    mesh = mask_to_mesh(mask, iso_value)

    if image is not None:
        logger.debug("Transforming mesh to reference image coordinate system")
        transform_mesh(mesh, mask, image)

    logger.debug("Saving mesh to %s", output_path)
    save_mesh(mesh, output_path)


@click.command()
@click.argument("mask", type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path))
@click.option(
    "--image",
    "-i",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
    default=None,
    help=(
        "Path to the reference image for coordinate system transformation. "
        "Only needed if the mask and image are in different coordinate systems."
    ),
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, resolve_path=True, path_type=Path),
    required=False,
    help=(
        "Path to save the output mesh. If not provided, the output file will be created in the same "
        "directory as the mask file with the same name and a different suffix."
    ),
)
@click.option(
    "--suffix",
    "-s",
    type=str,
    default=".stl",
    show_default=True,
    help="Suffix for the output mesh file if --output is not provided.",
)
@click.option(
    "--iso-value",
    "-v",
    type=float,
    default=None,
    help=(
        "Iso-value for mesh extraction. If not provided, the mean of the minimum and "
        "maximum values in the mask is used."
    ),
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
    mask: Path,
    image: Path | None,
    output: Path,
    suffix: str = ".stl",
    iso_value: float | None = None,
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO",
) -> NoReturn:
    """Convert a binary MASK to a mesh."""
    # Configure logging level based on user input
    logging.getLogger().setLevel(log_level)

    if not suffix.startswith("."):
        msg = "Suffix must start with a dot (e.g. .stl)"
        raise click.BadParameter(msg)

    if output is None:
        output = mask.with_suffix(suffix)
    elif not output.suffix:
        output = output.with_suffix(suffix)
    elif output.suffix != suffix:
        msg = "⚠️ Output suffix does not match provided suffix. Ignoring provided suffix."
        click.secho(msg, fg="yellow")

    try:
        mask2stl(mask_path=mask, image_path=image, output_path=output, iso_value=iso_value)
    except (RuntimeError, ValueError) as e:
        click.secho(f"❌ {e}", fg="red")
        logger.debug("Full traceback: %s", format_exc())
        sys.exit(1)

    click.secho(f"✅ Mesh written to {output}", fg="green")
    sys.exit(0)
