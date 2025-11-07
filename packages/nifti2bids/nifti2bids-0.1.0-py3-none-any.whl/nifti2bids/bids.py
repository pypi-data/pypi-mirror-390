import os, json
from typing import Optional

import pandas as pd

from nifti2bids.io import _copy_file, glob_contents


def create_bids_file(
    nifti_file: str,
    subj_id: str | int,
    desc: str,
    ses_id: Optional[str | int] = None,
    task_id: Optional[str] = None,
    run_id: Optional[str | int] = None,
    dst_dir: str = None,
    remove_src_file: bool = False,
    return_bids_filename: bool = False,
) -> str | None:
    """
    Create a BIDS compliant filename with required and optional entities.

    Parameters
    ----------
    nifti_file: :obj:`str`
        Path to NIfTI image.

    sub_id: :obj:`str` or :obj:`int`
        Subject ID (i.e. 01, 101, etc).

    desc: :obj:`str`
        Description of the file (i.e., T1w, bold, etc).

    ses_id: :obj:`str` or :obj:`int` or :obj:`None`, default=None
        Session ID (i.e. 001, 1, etc). Optional entity.

    ses_id: :obj:`str` or :obj:`int` or :obj:`None`, default=None
        Session ID (i.e. 001, 1, etc). Optional entity.

    task_id: :obj:`str` or :obj:`None`, default=None
        Task ID (i.e. flanker, n_back, etc). Optional entity.

    run_id: :obj:`str` or :obj:`int` or :obj:`None`, default=None
        Run ID (i.e. 001, 1, etc). Optional entity.

    dst_dir: :obj:`str`, default=None
        Directory name to copy the BIDS file to. If None, then the
        BIDS file is copied to the same directory as

    remove_src_file: :obj:`str`, default=False
        Delete the source file if True.

    return_bids_filename: :obj:`str`, default=False
        Returns the full BIDS filename if True.

    Returns
    -------
    None or str
        If ``return_bids_filename`` is True, then the BIDS filename is
        returned.

    Note
    ----
    There are additional entities that can be used that are
    not included in this function.
    """
    bids_filename = f"sub-{subj_id}_ses-{ses_id}_task-{task_id}_" f"run-{run_id}_{desc}"
    bids_filename = _strip_none_entities(bids_filename)

    ext = f"{nifti_file.partition('.')[-1]}"
    bids_filename += f"{ext}"
    bids_filename = (
        os.path.join(os.path.dirname(nifti_file), bids_filename)
        if dst_dir is None
        else os.path.join(dst_dir, bids_filename)
    )

    _copy_file(nifti_file, bids_filename, remove_src_file)

    return bids_filename if return_bids_filename else None


def _strip_none_entities(bids_filename: str) -> str:
    """
    Removes entities with None in a BIDS compliant filename.

    Parameters
    ----------
    bids_filename: :obj:`str`
        The BIDS filename.

    Returns
    -------
    str
        BIDS filename with entities ending in None removed.

    Example
    -------
    >>> from bidsrep.io import _strip_none_entities
    >>> bids_filename = "sub-101_ses-None_task-flanker_bold.nii.gz"
    >>> _strip_none_entities(bids_filename)
        "sub-101_task-flanker_bold.nii.gz"
    """
    basename, _, ext = bids_filename.partition(".")
    retained_entities = [
        entity for entity in basename.split("_") if not entity.endswith("-None")
    ]

    return f"{'_'.join(retained_entities)}.{ext}"


def create_dataset_description(dataset_name: str, bids_version: str = "1.0.0") -> dict:
    """
    Generate a dataset description dictionary.

    Creates a dictionary containing the name and BIDs version of a dataset.

    .. versionadded:: 0.34.1

    Parameters
    ----------
    dataset_name: :obj:`str`
        Name of the dataset.

    bids_version: :obj:`str`,
        Version of the BIDS dataset.

    derivative: :obj:`bool`, default=False
        Determines if "GeneratedBy" key is added to dictionary.

    Returns
    -------
    dict
        The dataset description dictionary
    """
    return {"Name": dataset_name, "BIDSVersion": bids_version}


def save_dataset_description(dataset_description: dict[str, str], dst_dir: str) -> None:
    """
    Save a dataset description dictionary.

    Saves the dataset description dictionary as a file named "dataset_description.json" to the
    directory specified by ``output_dir``.

    Parameters
    ----------
    dataset_description: :obj:`dict`
        The dataset description dictionary.

    dst_dir: :obj:`str`
        Path to save the JSON file to.
    """
    with open(
        os.path.join(dst_dir, "dataset_description.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(dataset_description, f)


def create_participant_tsv(
    bids_dir: str, save_df: bool = False, return_df: bool = True
) -> pd.DataFrame | None:
    """
    Creates a basic participant dataframe for the "participants.tsv" file.

    Parameters
    ----------
    bids_dir: :obj:`str`
        The root of BIDS compliant directory.

    save_df: :obj:`bool`, bool=False
        Save the dataframe to the root of the BIDS compliant directory.

    return_df: :obj:`str`
        Whether or not to return the dataframe.

    Returns
    -------
    pd.DataFrame or None
        The dataframe if ``return_df`` is True.
    """
    participants = [
        os.path.basename(folder) for folder in glob_contents(bids_dir, "*sub-*")
    ]
    df = pd.DataFrame({"participant_id": participants})

    if save_df:
        df.to_csv(os.path.join(bids_dir, "participants.tsv"), sep="\t", index=None)

    return df if return_df else None
