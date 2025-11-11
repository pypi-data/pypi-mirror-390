"""Helper functions for STL to mask conversion."""

from __future__ import annotations

from typing import TYPE_CHECKING

import meshlib.mrmeshpy as mm
import SimpleITK as sitk

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["matrix3f", "read_image", "read_mesh", "save_mask"]


def matrix3f(x: tuple[float, ...]) -> mm.Matrix3f:
    """Create a 3x3 float matrix.

    Params
    ------
    x, y, z : list[float]
        Matrix elements.

    Returns
    -------
    mrmeshpy.Matrix3f
        Meshlib 3x3 float matrix.

    """
    matrix = mm.Matrix3f()
    matrix.x = mm.Vector3f(*x[:3])
    matrix.y = mm.Vector3f(*x[3:6])
    matrix.z = mm.Vector3f(*x[6:])

    return matrix


def read_image(image_path: Path) -> sitk.Image:
    """Read an image using SimpleITK."""
    try:
        image = sitk.ReadImage(str(image_path))
    except RuntimeError as e:
        msg = f"Failed to read image {image_path}. Is the file type supported by SimpleITK?"
        raise RuntimeError(msg) from e

    return image


def read_mesh(mesh_path: Path) -> mm.Mesh:
    """Read a mesh using meshlib."""
    try:
        mesh = mm.loadMesh(mesh_path)
    except RuntimeError as e:
        msg = f"Failed to read mesh {mesh_path}. Is the file type supported by meshlib?"
        raise RuntimeError(msg) from e

    return mesh


def save_mask(mask_image: sitk.Image, output_path: Path) -> None:
    """Save a SimpleITK Image to a file."""
    try:
        sitk.WriteImage(mask_image, str(output_path))
    except RuntimeError as e:
        msg = f"Failed to write mask image to {output_path}."
        raise RuntimeError(msg) from e


def save_mesh(mesh: mm.Mesh, output_path: Path) -> None:
    """Save a meshlib Mesh to a file."""
    try:
        mm.saveMesh(mesh, output_path)
    except RuntimeError as e:
        msg = f"Failed to write mesh to {output_path}. Is the file type supported by meshlib?"
        raise RuntimeError(msg) from e
