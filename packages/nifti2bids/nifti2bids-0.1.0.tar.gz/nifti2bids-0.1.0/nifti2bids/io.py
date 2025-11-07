"""Module for input/output operations."""

import glob, os, shutil

import nibabel as nib


def load_nifti(
    nifti_file_or_img: str | nib.nifti1.Nifti1Image,
) -> nib.nifti1.Nifti1Image:
    """
    Loads a NIfTI image.

    Loads NIfTI image when not a ``Nifti1Image`` object or
    returns the image if already loaded in.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    Returns
    -------
    nib.nifti1.Nifti1Image
        The loaded in NIfTI image.
    """
    nifti_img = (
        nifti_file_or_img
        if isinstance(nifti_file_or_img, nib.nifti1.Nifti1Image)
        else nib.load(nifti_file_or_img)
    )

    return nifti_img


def compress_image(nifti_file: str, remove_src_file: bool = False) -> None:
    """
    Compresses a ".nii" image to a ".nii.gz" image.

    Parameters
    ----------
    nifti_file: :obj:`str`
        Path to the NIfTI image.

    remove_src_file: :obj:`bool`
        Deletes the original source image file.

    Returns
    -------
    None
    """
    img = nib.load(nifti_file)
    nib.save(img, nifti_file.replace(".nii", ".nii.gz"))

    if remove_src_file:
        os.remove(nifti_file)


def glob_contents(src_dir: str, pattern: str) -> list[str]:
    """
    Use glob to get contents with specific patterns.

    Parameters
    ----------
    src_dir: :obj:`str`
        The source directory.

    ext: :obj:`str`
        The extension.

    Returns
    -------
    list[str]
        List of contents with the pattern specified by ``pattern``.
    """
    return glob.glob(os.path.join(src_dir, f"*{pattern}"))


def get_nifti_header(nifti_file_or_img):
    """
    Get header from a NIfTI image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    Returns
    -------
    nib.nifti1.Nifti1Image
        The header from a NIfTI image.
    """
    return load_nifti(nifti_file_or_img).header


def get_nifti_affine(nifti_file_or_img):
    """
    Get the affine matrix from a NIfTI image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    Returns
    -------
    nib.nifti1.Nifti1Image
        The header from a NIfTI image.
    """
    return load_nifti(nifti_file_or_img).affine


def _copy_file(src_file: str, dst_file: str, remove_src_file: bool) -> None:
    """
    Copy a file and optionally remove the source file.

    Parameters
    ----------
    src_file: :obj:`str`
        The source file to be copied

    dst_file: :obj:`str`
        The new destination file.

    remove_src_file: :obj:`bool`
        Delete the source file if True.

    Returns
    -------
    None
    """
    shutil.copy(src_file, dst_file)

    if remove_src_file:
        os.remove(src_file)
