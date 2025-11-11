from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest
import SimpleITK as sitk

import stl2mask.mask2stl as mask2stl_module

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import CliRunner
    from pytest_mock import MockerFixture


def _make_mask_image(values: np.ndarray) -> sitk.Image:
    image = sitk.GetImageFromArray(values.astype(np.uint8))
    image.SetSpacing((0.5, 0.5, 0.5))
    image.SetOrigin((1.0, 2.0, 3.0))
    image.SetDirection((1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0))
    return image


def test_mask2stl_without_reference_image(tmp_path: Path, mocker: MockerFixture) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    output_path = tmp_path / "mesh.stl"

    mask_image = _make_mask_image(np.array([[[0, 255], [0, 0]], [[0, 0], [0, 0]]]))

    read_mesh_mock = mocker.patch.object(mask2stl_module, "read_image", return_value=mask_image)
    mask_to_mesh_mock = mocker.patch.object(mask2stl_module, "mask_to_mesh", return_value=mocker.sentinel.mesh)
    transform_mesh_mock = mocker.patch.object(mask2stl_module, "transform_mesh")
    save_mesh_mock = mocker.patch.object(mask2stl_module, "save_mesh")

    mask2stl_module.mask2stl(mask_path, None, output_path, iso_value=64.0)

    assert read_mesh_mock.call_count == 1
    assert read_mesh_mock.call_args.args == (mask_path,)

    assert mask_to_mesh_mock.call_count == 1
    assert mask_to_mesh_mock.call_args.args == (mask_image, 64.0)

    assert transform_mesh_mock.call_count == 0

    assert save_mesh_mock.call_count == 1
    assert save_mesh_mock.call_args.args == (mocker.sentinel.mesh, output_path)


def test_mask2stl_with_reference_image(tmp_path: Path, mocker: MockerFixture) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    image_path = tmp_path / "image.nii.gz"
    output_path = tmp_path / "mesh.stl"

    mask_image = _make_mask_image(np.array([[[0, 255]], [[0, 0]]]))
    reference_image = sitk.Image(1, 1, 2, sitk.sitkUInt8)
    reference_image.SetOrigin((5.0, 6.0, 7.0))

    def fake_read_image(path: Path) -> sitk.Image:
        if path == mask_path:
            return mask_image
        if path == image_path:
            return reference_image
        msg = f"Unexpected path {path}"
        raise AssertionError(msg)

    read_image_mock = mocker.patch.object(mask2stl_module, "read_image", side_effect=fake_read_image)
    mask_to_mesh_mock = mocker.patch.object(mask2stl_module, "mask_to_mesh", return_value=mocker.sentinel.mesh)
    transform_mesh_mock = mocker.patch.object(mask2stl_module, "transform_mesh")
    save_mesh_mock = mocker.patch.object(mask2stl_module, "save_mesh")

    mask2stl_module.mask2stl(mask_path, image_path, output_path, iso_value=None)

    assert read_image_mock.call_count == 2  # noqa: PLR2004
    assert read_image_mock.call_args_list[0].args == (mask_path,)
    assert read_image_mock.call_args_list[1].args == (image_path,)

    assert mask_to_mesh_mock.call_count == 1
    assert mask_to_mesh_mock.call_args.args == (mask_image, None)

    assert transform_mesh_mock.call_count == 1
    assert transform_mesh_mock.call_args.args == (mocker.sentinel.mesh, mask_image, reference_image)

    assert save_mesh_mock.call_count == 1
    assert save_mesh_mock.call_args.args == (mocker.sentinel.mesh, output_path)


def test_mask2stl_rejects_non_binary_mask(tmp_path: Path, mocker: MockerFixture) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    output_path = tmp_path / "mesh.stl"
    mask_image = _make_mask_image(np.array([[[0, 1, 2]]]))

    read_image_mock = mocker.patch.object(mask2stl_module, "read_image")
    read_image_mock.return_value = mask_image

    with pytest.raises(ValueError, match="binary image"):
        mask2stl_module.mask2stl(mask_path, None, output_path)


def test_mask2stl_rejects_out_of_range_iso_value(tmp_path: Path, mocker: MockerFixture) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    output_path = tmp_path / "mesh.stl"
    mask_image = _make_mask_image(np.array([[[0, 255]]]))

    read_image_mock = mocker.patch.object(mask2stl_module, "read_image")
    read_image_mock.return_value = mask_image

    with pytest.raises(ValueError, match="iso value"):
        mask2stl_module.mask2stl(mask_path, None, output_path, iso_value=300.0)


def test_cli_uses_default_suffix(tmp_path: Path, runner: CliRunner, mocker: MockerFixture) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    mask_path.write_text("")

    mask2stl_mock = mocker.patch("stl2mask.mask2stl.mask2stl")

    result = runner.invoke(mask2stl_module.cli, [str(mask_path)])

    assert result.exit_code == 0
    expected_output = mask_path.with_suffix(".stl")
    assert mask2stl_mock.call_args.kwargs == {
        "mask_path": mask_path,
        "image_path": None,
        "output_path": expected_output,
        "iso_value": None,
    }
    assert str(expected_output) in result.output


def test_cli_warns_on_suffix_mismatch(tmp_path: Path, runner: CliRunner, mocker: MockerFixture) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    mask_path.write_text("")
    output_path = tmp_path / "custom.stl"

    mask2stl_mock = mocker.patch("stl2mask.mask2stl.mask2stl")

    result = runner.invoke(
        mask2stl_module.cli,
        [
            str(mask_path),
            "--output",
            str(output_path),
            "--suffix",
            ".obj",
        ],
    )

    assert result.exit_code == 0
    assert "⚠️ Output suffix does not match provided suffix" in result.output
    assert mask2stl_mock.call_args.kwargs == {
        "mask_path": mask_path,
        "image_path": None,
        "output_path": output_path,
        "iso_value": None,
    }


def test_cli_rejects_suffix_without_dot(tmp_path: Path, runner: CliRunner, mocker: MockerFixture) -> None:
    mask_path = tmp_path / "mask.nii.gz"
    mask_path.write_text("")

    mocker.patch("stl2mask.mask2stl.mask2stl", side_effect=lambda: pytest.fail("mask2stl should not be called"))

    result = runner.invoke(
        mask2stl_module.cli,
        [str(mask_path), "--suffix", "stl"],
    )

    assert result.exit_code != 0
    assert "Suffix must start with a dot" in result.output


def test_cli_sets_requested_log_level(tmp_path: Path, runner: CliRunner, mocker: MockerFixture) -> None:
    mask_path = tmp_path / "mask.nii"
    mask_path.write_text("")

    stl2mask_mock = mocker.patch("stl2mask.mask2stl.mask2stl")
    get_logger_mock = mocker.patch("stl2mask.mask2stl.logging.getLogger")
    logger_mock = mocker.Mock()
    get_logger_mock.return_value = logger_mock

    result = runner.invoke(
        mask2stl_module.cli,
        [str(mask_path), "--log-level", "DEBUG"],
    )

    assert result.exit_code == 0
    assert logger_mock.setLevel.call_args.args == ("DEBUG",)
    assert stl2mask_mock.call_count == 1


def test_cli_normalizes_log_level_case(tmp_path: Path, runner: CliRunner, mocker: MockerFixture) -> None:
    mask_path = tmp_path / "mask.nii"
    mask_path.write_text("")

    mocker.patch("stl2mask.mask2stl.mask2stl")
    get_logger_mock = mocker.patch("stl2mask.mask2stl.logging.getLogger")
    logger_mock = mocker.Mock()
    get_logger_mock.return_value = logger_mock

    result = runner.invoke(
        mask2stl_module.cli,
        [str(mask_path), "--log-level", "warning"],
    )

    assert result.exit_code == 0
    assert logger_mock.setLevel.call_args.args == ("WARNING",)
