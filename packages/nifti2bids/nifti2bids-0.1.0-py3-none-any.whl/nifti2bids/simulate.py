"""Module for creating simulated data."""

import nibabel as nib, numpy as np

from numpy.typing import NDArray


def simulate_nifti_image(
    img_shape: tuple[int, int, int] | tuple[int, int, int, int], affine: NDArray = None
) -> nib.Nifti1Image:
    """
    Simulates a NIfTI image.

    Parameters
    ----------
    img_shape: :obj:`tuple[int, int, int]` or :obj:`tuple[int, int, int, int]`
        Shape of the NIfTI image.

    affine: :obj:`NDArray`, default=None
        The affine matrix.

        .. important::
           If None, creates an identity matrix.

    Returns
    -------
    Nifti1Image
        The NIfTI image with no header.
    """
    if affine is None:
        affine = create_affine(
            xyz_diagonal_value=1, translation_vector=np.array([0, 0, 0, 1])
        )

    return nib.Nifti1Image(np.random.rand(*img_shape), affine)


def create_affine(xyz_diagonal_value: int, translation_vector: NDArray) -> NDArray:
    """
    Generate an 4x4 affine matrix.

    Parameters
    ----------
    xyz_diagonal_value: :obj:`int`
        The value assigned to the diagonal of the affine for x, y, and z.

    translation_vector: :obj:`NDArray`
        The translation vector/shift from the origin.

    Returns
    -------
    NDArray
        The affine matrix.
    """
    affine = np.zeros((4, 4))
    np.fill_diagonal(affine[:3, :3], xyz_diagonal_value)
    affine[:, 3:] = translation_vector[:, np.newaxis]

    return affine
