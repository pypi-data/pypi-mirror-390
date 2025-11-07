import glob, os

import pandas as pd, pytest

from nifti2bids.bids import (
    create_bids_file,
    create_participant_tsv,
    create_dataset_description,
    save_dataset_description,
)


@pytest.mark.parametrize("dst_dir, remove_src_file", ([None, True], [True, False]))
def test_create_bids_file(nifti_img_and_path, tmp_dir, dst_dir, remove_src_file):
    """Test for ``create_bids_file``."""
    _, img_path = nifti_img_and_path
    dst_dir = None if not dst_dir else os.path.join(tmp_dir.name, "test")
    if dst_dir:
        os.makedirs(dst_dir)

    bids_filename = create_bids_file(
        img_path,
        subj_id="01",
        desc="bold",
        remove_src_file=remove_src_file,
        dst_dir=dst_dir,
        return_bids_filename=True,
    )
    assert bids_filename
    assert os.path.basename(bids_filename) == "sub-01_bold.nii"

    if dst_dir:
        dst_file = glob.glob(os.path.join(dst_dir, "*nii"))[0]
        assert os.path.basename(dst_file) == "sub-01_bold.nii"

        src_file = glob.glob(os.path.join(os.path.dirname(img_path), "*.nii"))[0]
        assert os.path.basename(src_file) == "img.nii"
    else:
        files = glob.glob(os.path.join(os.path.dirname(img_path), "*.nii"))
        assert len(files) == 1
        assert os.path.basename(files[0]) == "sub-01_bold.nii"


def test_create_dataset_description():
    """Test for ``create_dataset_description``."""
    dataset_desc = create_dataset_description(dataset_name="test", bids_version="1.2.0")
    assert dataset_desc.get("Name") == "test"
    assert dataset_desc.get("BIDSVersion") == "1.2.0"


def test_save_dataset_description(tmp_dir):
    """Test for ``save_dataset_description``."""
    dataset_desc = create_dataset_description(dataset_name="test", bids_version="1.2.0")
    save_dataset_description(dataset_desc, tmp_dir.name)
    files = glob.glob(os.path.join(tmp_dir.name, "*.json"))
    assert len(files) == 1
    assert os.path.basename(files[0]) == "dataset_description.json"


def test_create_participant_tsv(tmp_dir):
    """Test for ``create_participant_tsv``."""
    os.makedirs(os.path.join(tmp_dir.name, "sub-01"))
    df = create_participant_tsv(tmp_dir.name, save_df=True, return_df=True)
    assert isinstance(df, pd.DataFrame)

    filename = os.path.join(tmp_dir.name, "participants.tsv")
    assert os.path.isfile(filename)

    df = pd.read_csv(filename, sep="\t")
    assert df["participant_id"].values[0] == "sub-01"
