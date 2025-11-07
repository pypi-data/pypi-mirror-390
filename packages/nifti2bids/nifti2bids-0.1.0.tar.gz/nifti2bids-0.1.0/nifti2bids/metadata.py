"""Utility functions to extract metadata."""

import datetime, os, re
from typing import Any, Literal, Optional

import nibabel as nib, numpy as np

from ._exceptions import SliceAxisError, DataDimensionError
from ._decorators import check_all_none
from .io import load_nifti, get_nifti_header
from .logging import setup_logger

LGR = setup_logger(__name__)


@check_all_none(parameter_names=["nifti_file_or_img", "nifti_header"])
def determine_slice_axis(
    nifti_file_or_img: Optional[str | nib.nifti1.Nifti1Image] = None,
    nifti_header: Optional[nib.nifti1.Nifti1Header] = None,
) -> int:
    """
    Determine the slice axis.

    Uses "slice_end" plus one to determine the likely slice axis.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`, default=None
        Path to the NIfTI file or a NIfTI image. Must be specified
        if ``nifti_header`` is None.

    nifti_header: :obj:`Nifti1Header`, default=None
        Path to the NIfTI file or a NIfTI image. Must be specified
        if ``nifti_file_or_img`` is None.

    Returns
    -------
    int
        A number representing the slice axis.
    """
    kwargs = {"nifti_file_or_img": nifti_file_or_img, "nifti_header": nifti_header}
    slice_end, hdr = get_hdr_metadata(
        **kwargs, metadata_name="slice_end", return_header=True
    )
    if not slice_end or np.isnan(slice_end):
        raise ValueError("'slice_end' metadata field not set.")

    n_slices = int(slice_end) + 1
    dims = np.array(hdr.get_data_shape()[:3])

    return np.where(dims == n_slices)[0][0]


def _is_numeric(value: Any) -> bool:
    """
    Check if value is a number.
    """
    return isinstance(value, (float, int))


def _to_native_numeric(value):
    """
    Ensures numpy floats and integers are converted
    to regular Python floats and integers.
    """
    return float(value) if isinstance(value, np.floating) else int(value)


@check_all_none(parameter_names=["nifti_file_or_img", "nifti_header"])
def get_hdr_metadata(
    metadata_name: str,
    nifti_file_or_img: Optional[str | nib.nifti1.Nifti1Image] = None,
    nifti_header: Optional[nib.nifti1.Nifti1Header] = None,
    return_header: bool = False,
) -> Any | tuple[Any, nib.nifti1.Nifti1Header]:
    """
    Get metadata from a NIfTI header.

    Parameters
    ----------
    metadata_name: :obj:`str`
        Name of the metadata field to return.

    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`, default=None
        Path to the NIfTI file or a NIfTI image. Must be specified
        if ``nifti_header`` is None.

    nifti_header: :obj:`Nifti1Header`, default=None
        Path to the NIfTI file or a NIfTI image. Must be specified
        if ``nifti_file_or_img`` is None.

    return_header: :obj:`bool`
        Returns the NIfTI header

    Returns
    -------
    Any or tuple[Any, nibabel.nifti1.Nifti1Header]
        If ``return_header`` is False, only returns the associated
        value of the metadata. If ``return_header`` is True returns
        a tuple containing the assoicated value of the metadata
        and the NIfTI header.
    """
    hdr = nifti_header if nifti_header else get_nifti_header(nifti_file_or_img)
    metadata_value = hdr.get(metadata_name)
    metadata_value = (
        _to_native_numeric(metadata_value)
        if _is_numeric(metadata_value)
        else metadata_value
    )

    return metadata_value if not return_header else (metadata_value, hdr)


def get_n_volumes(nifti_file_or_img: str | nib.nifti1.Nifti1Image) -> int:
    """
    Get the number of volumes from a 4D NIftI image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    Returns
    -------
    int
        The number of volumes in img.
    """
    img = load_nifti(nifti_file_or_img)

    if is_3d_img(img):
        raise DataDimensionError("Image is 3D not 4D.")

    return img.get_fdata().shape[-1]


def get_n_slices(
    nifti_file_or_img: str | nib.nifti1.Nifti1Image,
    slice_axis: Optional[Literal["x", "y", "z"]] = None,
) -> int:
    """
    Gets the number of slices from the header of a NIfTI image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    slice_axis: :obj:`Literal["x", "y", "z"]` or :obj:`None`, default=None
        Axis the image slices were collected in. If None,
        determines the slice axis using metadata ("slice_end")
        from the NIfTI header.

    Returns
    -------
    int
        The number of slices.
    """
    slice_dim_map = {"x": 0, "y": 1, "z": 2}

    hdr = get_nifti_header(nifti_file_or_img)
    if slice_axis:
        n_slices = hdr.get_data_shape()[slice_dim_map[slice_axis]]
        if slice_end := get_hdr_metadata(nifti_header=hdr, metadata_name="slice_end"):
            if not np.isnan(slice_end) and n_slices != slice_end + 1:
                raise SliceAxisError(slice_axis, n_slices, slice_end)

        slice_dim_indx = slice_dim_map[slice_axis]
    else:
        slice_dim_indx = determine_slice_axis(nifti_header=hdr)

    reversed_slice_dim_map = {v: k for v, k in slice_dim_map.items()}

    n_slices = hdr.get_data_shape()[slice_dim_indx]
    LGR.info(
        f"Number of slices based on "
        f"{reversed_slice_dim_map.get(slice_dim_indx)}: {n_slices}"
    )

    return _to_native_numeric(n_slices)


def get_tr(nifti_file_or_img: str | nib.nifti1.Nifti1Image) -> float:
    """
    Get the repetition time from the header of a NIfTI image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    Returns
    -------
    float
        The repetition time.
    """
    hdr = get_nifti_header(nifti_file_or_img)

    if not (tr := hdr.get_zooms()[3]):
        raise ValueError(f"Suspicious repetition time: {tr}.")

    LGR.info(f"Repetition Time: {tr}.")

    return round(_to_native_numeric(tr), 2)


def _flip_slice_order(slice_order, ascending: bool) -> list[int]:
    """
    Flip slice index order.

    Parameters
    ----------
    slice_order: :obj:`list[int]`
        List containing integer values representing the slices.

    ascending: :obj:`bool`, default=True
        If slices were collected in ascending order (True) or descending
        order (False).

    Returns
    -------
    list[int]
        The order of the slices.
    """
    return np.flip(slice_order) if not ascending else slice_order


def _create_sequential_order(n_slices: int, ascending: bool = True) -> list[int]:
    """
    Create index ordering for sequential acquisition method.

    Parameters
    ----------
    n_slices: :obj:`int`
        The number of slices.

    ascending: :obj:`bool`, default=True
        If slices were collected in ascending order (True) or descending
        order (False).

    Returns
    -------
    list[int]
        The order of the slices.
    """
    slice_order = list(range(0, n_slices))

    return _flip_slice_order(slice_order, ascending)


def _create_interleaved_order(
    n_slices: int,
    ascending: bool = True,
    interleaved_order: Literal["even_first", "odd_first"] = "odd_first",
) -> list[int]:
    """
    Create index ordering for interleaved acquisition method.

    Parameters
    ----------
    n_slices: :obj:`int`
        The number of slices.

    ascending: :obj:`bool`, default=True
        If slices were collected in ascending order (True) or descending
        order (False).

    interleaved_order: :obj:`Literal["even_first", "odd_first"]`, default="odd_first"
        If slices for interleaved acquisition were collected
        by acquiring the "even_first" or "odd_first" slices first.

    Returns
    -------
    list[int]
        The order of the slices.
    """
    if interleaved_order == "odd_first":
        slice_order = list(range(0, n_slices, 2)) + list(range(1, n_slices, 2))
    else:
        slice_order = list(range(1, n_slices, 2)) + list(range(0, n_slices, 2))

    return _flip_slice_order(slice_order, ascending)


def create_slice_timing(
    nifti_file_or_img: str | nib.nifti1.Nifti1Image,
    slice_acquisition_method: Literal["sequential", "interleaved"],
    slice_axis: Literal["x", "y", "z"] = None,
    ascending: bool = True,
    interleaved_order: Literal["even_first", "odd_first"] = "odd_first",
) -> list[float]:
    """
    Create slice timing dictionary mapping the slice index to its
    acquisition time.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    slice_acquisition_method: :obj:`Literal["sequential", "interleaved"]`
        Method used for acquiring slices.

    slice_axis: :obj:`Literal["x", "y", "z"]` or :obj:`None`, default=None
        Axis the image slices were collected in. If None,
        determines the slice axis using metadata ("slice_end")
        from the NIfTI header.

    ascending: :obj:`bool`, default=True
        If slices were collected in ascending order (True) or descending
        order (False).

    interleaved_order: :obj:`Literal["even_first", "odd_first"]`, default="odd_first"
        If slices for interleaved acquisition were collected
        by acquiring the "even_first" or "odd_first" slices first.

    Returns
    -------
    list[float]
        List containing the slice timing acquisition.
    """
    if interleaved_order not in ["odd_first", "even_first"]:
        raise ValueError(
            "``interleaved_order`` must be either 'odd_first' or 'even_first'."
        )
    slice_ordering_func = {
        "sequential": _create_sequential_order,
        "interleaved": _create_interleaved_order,
    }

    tr = get_tr(nifti_file_or_img)
    n_slices = get_n_slices(nifti_file_or_img, slice_axis)

    slice_duration = tr / n_slices
    kwargs = {"n_slices": n_slices, "ascending": ascending}

    if slice_acquisition_method == "interleaved":
        kwargs.update({"interleaved_order": interleaved_order})

    slice_order = slice_ordering_func[slice_acquisition_method](**kwargs)
    slice_timing = np.linspace(0, tr - slice_duration, n_slices)
    # Pair slice with timing then sort dict
    sorted_slice_timing = dict(
        sorted({k: v for k, v in zip(slice_order, slice_timing.tolist())}.items())
    )

    return list(sorted_slice_timing.values())


def is_3d_img(nifti_file_or_img: str | nib.nifti1.Nifti1Image) -> bool:
    """
    Determines if ``nifti_file_or_img`` is a 3D image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    Returns
    -------
    bool
        True if ``nifti_file_or_img`` is a 3D image.
    """
    return len(get_nifti_header(nifti_file_or_img).get_zooms()) == 3


def get_scanner_info(
    nifti_file_or_img: str | nib.nifti1.Nifti1Image,
) -> tuple[str, str]:
    """
    Determines the manufacturer and model name of scanner.

    .. important::
        Assumes this information is in the "descrip" of the NIfTI
        header, which can contain any information.


    Parameters
    ----------
    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`
        Path to the NIfTI file or a NIfTI image.

    Returns
    -------
    tuple[str, str]
        The manufacturer and model name for the scanner.
    """
    if not (
        scanner_info := get_hdr_metadata(
            nifti_file_or_img=nifti_file_or_img,
            metadata_name="descrip",
            return_header=False,
        )
    ):
        raise ValueError("No scanner information in NIfTI header.")

    scanner_info = str(scanner_info.astype(str)).rstrip(" ")
    manufacturer_name, _, model_name = scanner_info.partition(" ")

    return manufacturer_name, model_name


def is_valid_date(date_str: str, date_fmt: str) -> bool:
    """
    Determine if a string is a valid date based on format.

    Parameters
    ----------
    date_str: :obj:`str`
        The string to be validated.

    date_fmt:
        The expected format of the date.

    Return
    ------
    bool
        True if ``date_str`` has the format specified by ``date_fmt``

    Example
    -------
    >>> from nifti2bids.metadata import is_valid_date
    >>> is_valid_date("241010", "%y%m%d")
        True
    """
    try:
        datetime.datetime.strptime(date_str, date_fmt)
        return True
    except ValueError:
        return False


def get_date_from_filename(filename: str, date_fmt: str) -> str | None:
    """
    Get date from filename.

    Extracts the date from the name a file.

    Parameters
    ----------
    filename: :obj:`str`
        The absolute path or name of file.

    date_fmt:
        The expected format of the date.

    Returns
    -------
    str or None:
        A string if a valid date based on specified ``date_fmt`` is detected
        or None if no valid date is detected.

    Example
    -------
    >>> from nifti2bids.metadata import get_date_from_filename
    >>> get_date_from_filename("101_240820_mprage_32chan.nii", "%y%m%d")
        "240820"
    """
    split_pattern = "|".join(map(re.escape, ["_", "-", " "]))

    basename = os.path.basename(filename)
    split_basename = re.split(split_pattern, basename)

    date_str = None
    for part in split_basename:
        if is_valid_date(part, date_fmt):
            date_str = part
            break

    return date_str


def get_entity_value(filename: str, entity: str) -> str | None:
    """
    Gets entity value of a BIDS compliant filename.

    Parameters
    ----------
    filename: :obj:`str`
        Filename to extract entity from.

    entity: :obj:`str`
        The entity key (e.g. "sub", "task")

    Returns
    -------
    str or None
        The entity value.

    Example
    -------
    >>> from nifti2bids.metadata import get_entity_value
    >>> get_entity_value("sub-01_task-flanker_bold.nii.gz", "task")
        "flanker"
    """
    basename = os.path.basename(filename)
    match = re.search(rf"{entity}-([^_\.]+)", basename)

    return match.group(1) if match else None


def infer_task_from_image(
    nifti_file_or_img: str | nib.nifti1.Nifti1Image, volume_to_task_map: dict[int, str]
) -> str:
    """
    Infer the task based on the number of volumes in a 4D NIfTI image.

    Parameters
    ----------
    nifti_file_or_img: :obj:`str` or :obj:`Nifti1Image`, default=None
        Path to the NIfTI file or a NIfTI image.

    volume_to_task_map: :obj:`dict[int, str]`
        A mapping of the number of volumes for each taskname.

    Returns
    -------
    str
        The task name.

    Example
    -------
    >>> from nifti2bids.io import simulate_nifti_image
    >>> from nifti2bids.metadata import infer_task_from_image
    >>> img = simulate_nifti_image((100, 100, 100, 260))
    >>> volume_to_task_map = {300: "flanker", 260: "nback"}
    >>> infer_task_from_image(img, volume_to_task_map)
        "nback"
    """
    n_volumes = get_n_volumes(nifti_file_or_img)

    return volume_to_task_map.get(n_volumes)
