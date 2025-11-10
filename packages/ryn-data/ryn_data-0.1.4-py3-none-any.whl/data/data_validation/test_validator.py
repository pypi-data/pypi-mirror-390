
import os
import shutil

import cv2
import numpy as np
import pandas as pd
import pytest
import scipy.io.wavfile as wavfile

# --- Dependencies for creating test files ---
try:
    import pydicom
    from pydicom.dataset import Dataset, FileDataset
    import nibabel as nib
    MEDICAL_IMAGING_LIBS_INSTALLED = True
except ImportError:
    MEDICAL_IMAGING_LIBS_INSTALLED = False

# --- Import the code to be tested ---
from data.data_validation.validation import DirectoryValidator, ValidationReport
from data.data_validation.config import validation_config

# ==============================================================================
# Pytest Fixture: Sets up the test environment before tests run
# ==============================================================================

@pytest.fixture(scope="session")
def test_directory_and_report(tmp_path_factory):
    """
    Sets up a temporary test directory, runs the DirectoryValidator once, and
    yields the report. scope="session" makes it run only once for the entire
    test session, making it very efficient.
    """
    root_dir = tmp_path_factory.mktemp("validation_data_session")
    print(f"\n--- Setting up test directory at '{root_dir}' (once per session) ---")

    # Define and create paths
    users_path = root_dir / "landing/users"
    transactions_path = root_dir / "processed/transactions/day=1"
    images_path = root_dir / "assets/product_images"
    audio_path = root_dir / "assets/audio_files"
    numpy_path = root_dir / "landing/numpy_files"
    markdown_path = root_dir / "landing/markdown_files"
    zips_path = root_dir / "landing/zips"
    large_files_path = root_dir / "landing/large_files"
    for p in [users_path, transactions_path, images_path, audio_path, numpy_path, markdown_path, zips_path, large_files_path]:
        p.mkdir(parents=True, exist_ok=True)

    HUGE_FILE_ROWS = 2_500_000
    print(f"Generating a large CSV with {HUGE_FILE_ROWS:,} rows. This may take a moment...")
    huge_data = {
        'user_id': range(HUGE_FILE_ROWS),
        'email': [f'user_{i}@massive-data.com' for i in range(HUGE_FILE_ROWS)],
        "username": [f'user_{i}' for i in range(HUGE_FILE_ROWS)],
        'status': ['active'] * HUGE_FILE_ROWS
    }
    for i in range(15):
        huge_data[f"username{i}"]= huge_data["username"]
    huge_data["nuu"] = [None  for i in range(HUGE_FILE_ROWS)]
    huge_df = pd.DataFrame(huge_data)
    random_index = np.random.choice(huge_df.index)
    huge_df.at[random_index, "email"] = "https://hello.com"
    huge_df.at[random_index, "status"] = "http://hello.com"

    print(huge_df.at[random_index,"email"],random_index)
    huge_file_path = large_files_path / "huge_user_file.csv"
    huge_df.to_csv(huge_file_path, index=False)
    print(f"Created: {huge_file_path}")
    
    # --- Create all necessary test files ---
    pd.DataFrame({"user_id": [1]}).to_csv(users_path / "users_good.csv", index=False)
    pd.DataFrame({"comment": ["See http://malicious-site.com"]}).to_csv(users_path / "users_with_links.csv", index=False)
    pd.DataFrame({"transaction_id": ["txn_101"]}).to_parquet(transactions_path / "transactions.parquet")

    zipped_csv_data = {"username": [f'https://user_{i}.com' for i in range(5)]}
    temp_csv_path = root_dir / "temp_orders_for_zip.csv"
    pd.DataFrame(zipped_csv_data).to_csv(temp_csv_path, index=False)
    shutil.make_archive(str(zips_path / "orders_archive"), 'zip', root_dir, "temp_orders_for_zip.csv")
    os.remove(temp_csv_path)

    good_image = np.zeros((10, 10, 3), dtype=np.uint8); good_image[0, 0] = [255, 255, 255]
    cv2.imwrite(str(images_path / "product_good.jpg"), good_image)
    cv2.imwrite(str(images_path / "product_black.jpg"), np.zeros((10, 10, 3), dtype=np.uint8))
    cv2.imwrite(str(images_path / "product_white.jpg"), np.ones((10, 10, 3), dtype=np.uint8) * 255)
    (images_path / "product_corrupt.jpg").write_text("corrupt")

    sample_rate = 16000; t_good = np.linspace(0.0, 1.0, int(sample_rate * 1.0), endpoint=False)
    data_good = (np.iinfo(np.int16).max * 0.5) * np.sin(2.0 * np.pi * 440.0 * t_good)
    wavfile.write(str(audio_path / "good_audio.wav"), sample_rate, data_good.astype(np.int16))
    wavfile.write(str(audio_path / "silent_audio.wav"), sample_rate, np.zeros(sample_rate, dtype=np.int16))
    t_short = np.linspace(0.0, 0.05, int(sample_rate * 0.05), endpoint=False)
    data_short = (np.iinfo(np.int16).max * 0.5) * np.sin(2. * np.pi * 440. * t_short)
    wavfile.write(str(audio_path / "short_audio.wav"), sample_rate, data_short.astype(np.int16))
    (audio_path / "corrupt_audio.wav").write_text("corrupt")

    np.save(numpy_path / "valid_array.npy", np.array([[1, 2]])); np.save(numpy_path / "array_with_nan.npy", np.array([[1, np.nan]]))
    np.save(numpy_path / "array_with_inf.npy", np.array([[1, np.inf]])); (numpy_path / "corrupt_array.npy").write_bytes(b"corrupt")
    
    (markdown_path / "valid_doc.md").write_text("# Title"); (markdown_path / "empty_doc.md").touch()

    if MEDICAL_IMAGING_LIBS_INSTALLED:
        dicom_path = root_dir / "landing/dicom_files"
        dicom_path.mkdir(exist_ok=True)
        file_meta = pydicom.Dataset()
        file_meta.MediaStorageSOPClassUID = pydicom.uid.SecondaryCaptureImageStorage
        file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian 
        file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        ds = FileDataset(str(dicom_path / "valid_image.dcm"), {}, file_meta=file_meta, preamble=b"\0" * 128)
        ds.PatientName = "Test"
        ds.is_implicit_VR = True
        ds.save_as(str(dicom_path / "valid_image.dcm"),little_endian=True)


        (dicom_path / "corrupt_image.dcm").write_text("corrupt")

        nifti_path = root_dir / "landing/nifti_files"
        nifti_path.mkdir(exist_ok=True)
        nib.save(nib.Nifti1Image(np.zeros((8, 8, 4)), np.eye(4)), str(nifti_path / "valid_image.nii"))
        (nifti_path / "corrupt_image.nii").write_text("corrupt")

    print("--- Validation running for all tests... ---")
    validator = DirectoryValidator(config=validation_config)
    report = validator.validate(root_dir)
    yield report # Provide the pre-computed report to all tests
    print(f"\n--- Tearing down test directory '{root_dir}' (at end of session) ---")

# ==============================================================================
# Helper Function
# ==============================================================================

def find_result_by_filename(report: ValidationReport, filename: str):
    for result in report.results:
        if result.file_path.name == filename:
            return result
    pytest.fail(f"Result for filename '{filename}' not found in the validation report.")


# Define the list of filenames expected to pass validation
valid_file_scenarios_data = [
    "users_good.csv",
    "transactions.parquet",
    "product_good.jpg",
    "good_audio.wav",
    "valid_array.npy",
    "valid_doc.md",
]
if MEDICAL_IMAGING_LIBS_INSTALLED:
    valid_file_scenarios_data.extend(["valid_image.dcm", "valid_image.nii"])

@pytest.mark.parametrize("filename", valid_file_scenarios_data)
def test_valid_file_scenarios(test_directory_and_report, filename):
    """
    Creates a separate test case for each file that should BE VALID,
    ensuring it passed validation and has no errors.
    """
    report = test_directory_and_report
    result = find_result_by_filename(report, filename)
    
    assert result.is_valid is True, \
        f"'{filename}' was expected to be valid but it FAILED.\n" \
        f"  Errors reported: {result.errors}"

# ==============================================================================
# INDIVIDUAL Test Cases for Invalid Files
# ==============================================================================

invalid_file_scenarios_data = [
    ("users_with_links.csv", "contains_links"),
    ("product_black.jpg", "solid_color"),
    ("product_white.jpg", "solid_color"),
    ("product_corrupt.jpg", "image_loadable"),
    ("silent_audio.wav", "silent_audio"),
    ("short_audio.wav", "minimum_duration"),
    ("corrupt_audio.wav", "audio_loadable"),
    ("array_with_nan.npy", "contains_nan"),
    ("array_with_inf.npy", "contains_inf"),
    ("corrupt_array.npy", "file_read_or_parse"),
    ("empty_doc.md", "empty_file"),
    ("huge_user_file.csv", "contains_links"),
]
if MEDICAL_IMAGING_LIBS_INSTALLED:
    invalid_file_scenarios_data.extend([
        ("corrupt_image.dcm", "dicom_parse"),
        ("corrupt_image.nii", "file_read_or_parse"),
    ])

@pytest.mark.parametrize("filename, expected_check_name", invalid_file_scenarios_data)
def test_invalid_file_scenarios(test_directory_and_report, filename, expected_check_name):
    """
    Creates a separate test case for each file that should BE INVALID,
    verifying it fails with the correct error type.
    """
    report = test_directory_and_report
    result = find_result_by_filename(report, filename)
    
    assert result.is_valid is False, f"'{filename}' should be invalid but it passed."
    
    actual_check_names = [err.get('check') for err in result.errors]
    
    assert expected_check_name in actual_check_names, \
        f"'{filename}' failed, but not with the expected check type.\n" \
        f"  Expected check: '{expected_check_name}'\n" \
        f"  Actual checks: {actual_check_names}"

    
# ==============================================================================
# Special Test Case for a Feature (Zip Validation)
# ==============================================================================
def test_zip_file_content_is_validated(test_directory_and_report):
    report = test_directory_and_report
    result = find_result_by_filename(report, "temp_orders_for_zip.csv")
    
    assert result.is_valid is False, "CSV with links inside zip should have failed validation."
    actual_check_names = [err.get('check') for err in result.errors]
    assert 'contains_links' in actual_check_names

