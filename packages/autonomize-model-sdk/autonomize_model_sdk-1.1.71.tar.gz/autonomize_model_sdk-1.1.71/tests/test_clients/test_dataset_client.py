from unittest.mock import MagicMock

import pytest

from modelhub.clients.dataset_client import DatasetClient
from modelhub.core import ModelhubCredential


@pytest.fixture
def mock_credential():
    """Create a mock ModelhubCredential."""
    credential = MagicMock(spec=ModelhubCredential)
    credential.get_token.return_value = "dummy-token"
    credential._modelhub_url = "http://dummy"
    return credential


# Fixture for a DatasetClient instance.
@pytest.fixture
def dataset_client(mock_credential):
    # Create client with mock credential
    client = DatasetClient(
        credential=mock_credential, client_id="1"
    )
    return client


def test_list_datasets(monkeypatch, dataset_client):
    # Simulate a GET call that returns a list of datasets.
    fake_data = [{"id": "1", "name": "dataset1"}, {"id": "2", "name": "dataset2"}]
    monkeypatch.setattr(
        dataset_client,
        "get",
        lambda endpoint, **kwargs: (
            {"data": fake_data} if endpoint == "datasets" else {}
        ),
    )
    result = dataset_client.list_datasets()
    assert result == fake_data


def test_get_dataset_by_name(monkeypatch, dataset_client):
    fake_dataset = {"id": "1", "name": "dataset1", "versions": []}
    monkeypatch.setattr(
        dataset_client,
        "get",
        lambda endpoint, **kwargs: (
            {"data": fake_dataset} if endpoint == "datasets/dataset1" else {}
        ),
    )
    result = dataset_client.get_dataset_by_name("dataset1")
    assert result == fake_dataset


def test_get_dataset_versions(monkeypatch, dataset_client):
    fake_versions = [{"version_id": 1}, {"version_id": 2}]
    monkeypatch.setattr(
        dataset_client,
        "get",
        lambda endpoint, **kwargs: (
            {"data": {"versions": fake_versions}} if endpoint == "datasets/1" else {}
        ),
    )
    result = dataset_client.get_dataset_versions("1")
    assert result == fake_versions


def test_get_signed_url(monkeypatch, dataset_client):
    fake_signed_url = "http://signed.url"
    # Override post to simulate a response that contains the signed URL.
    monkeypatch.setattr(
        dataset_client,
        "post",
        lambda endpoint, json, **kwargs: {"data": {"signedUrl": fake_signed_url}},
    )
    result = dataset_client.get_signed_url(
        "1", "path/to/file.csv", version=1, is_read=True
    )
    assert result == fake_signed_url


def test_load_dataset_multiple_nested_directories(monkeypatch, dataset_client):
    """
    Test that load_dataset raises an error when multiple nested directories are found
    and no directory is provided.
    """
    # Simulate a dataset retrieved by get_dataset_by_name.
    fake_dataset = {
        "id": "1",
        "versions": [
            {
                "version_id": 1,
                "files": [
                    {"file_path": "data1/splitA/file1.csv", "version_id": 1},
                    {"file_path": "data2/splitA/file2.csv", "version_id": 1},
                ],
            }
        ],
    }
    # Override get_dataset_by_name so that load_dataset uses our fake dataset.
    monkeypatch.setattr(
        dataset_client,
        "get_dataset_by_name",
        lambda name: fake_dataset if name == "dataset1" else None,
    )
    # Override get_signed_url to return a predictable string.
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    # Override _load_dataset_by_format to simply return its input.
    monkeypatch.setattr(
        dataset_client,
        "_load_dataset_by_format",
        lambda split_file_urls: split_file_urls,
    )
    # With files from two different parent directories ("data1" and "data2"),
    # _check_nested_directories will return multiple directories.
    with pytest.raises(ValueError, match="Multiple nested directories found"):
        dataset_client.load_dataset("dataset1", version=1, split=None, directory=None)


def test_load_dataset_success(monkeypatch, dataset_client):
    """
    Test a successful load_dataset call when a proper directory is specified.
    """
    fake_dataset = {
        "id": "1",
        "versions": [
            {
                "version_id": 1,
                "files": [
                    {"file_path": "dir/splitA/file1.csv", "version_id": 1},
                    {"file_path": "dir/splitA/file2.csv", "version_id": 1},
                ],
            }
        ],
    }
    monkeypatch.setattr(
        dataset_client,
        "get_dataset_by_name",
        lambda name: fake_dataset if name == "dataset1" else None,
    )
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    # Override _load_dataset_by_format to simply return its input for inspection.
    monkeypatch.setattr(
        dataset_client,
        "_load_dataset_by_format",
        lambda split_file_urls: split_file_urls,
    )
    result = dataset_client.load_dataset(
        "dataset1", version=1, split=None, directory="dir"
    )
    # With directory specified, the code uses: split_name = path_parts[-2].
    # For "dir/splitA/file1.csv", split_name becomes "splitA".
    expected = {
        "splitA": ["signed_dir/splitA/file1.csv", "signed_dir/splitA/file2.csv"]
    }
    assert result == expected


# Additional tests for _load_dataset_by_format for other formats:


def test__load_dataset_by_format_json(monkeypatch, dataset_client):
    fake_loaded = "loaded_dataset_json"

    def fake_load_dataset(format_name, data_files, **kwargs):
        assert format_name == "json"
        return fake_loaded

    monkeypatch.setattr(
        "modelhub.clients.dataset_client.load_dataset", fake_load_dataset
    )
    split_file_urls = {
        "splitA": [
            "http://example.com/data/file1.json",
            "http://example.com/data/file2.json",
        ]
    }
    result = dataset_client._load_dataset_by_format(split_file_urls)
    assert result == fake_loaded


def test__load_dataset_by_format_parquet(monkeypatch, dataset_client):
    fake_loaded = "loaded_dataset_parquet"

    def fake_load_dataset(format_name, data_files, **kwargs):
        assert format_name == "parquet"
        return fake_loaded

    monkeypatch.setattr(
        "modelhub.clients.dataset_client.load_dataset", fake_load_dataset
    )
    split_file_urls = {
        "splitA": [
            "http://example.com/data/file1.parquet",
            "http://example.com/data/file2.parquet",
        ]
    }
    result = dataset_client._load_dataset_by_format(split_file_urls)
    assert result == fake_loaded


def test__load_dataset_by_format_text(monkeypatch, dataset_client):
    fake_loaded = "loaded_dataset_text"

    def fake_load_dataset(format_name, data_files, **kwargs):
        assert format_name == "text"
        return fake_loaded

    monkeypatch.setattr(
        "modelhub.clients.dataset_client.load_dataset", fake_load_dataset
    )
    split_file_urls = {
        "splitA": [
            "http://example.com/data/file1.txt",
            "http://example.com/data/file2.txt",
        ]
    }
    result = dataset_client._load_dataset_by_format(split_file_urls)
    assert result == fake_loaded


def test__load_dataset_by_format_csv(monkeypatch, dataset_client):
    """
    Test _load_dataset_by_format for CSV files.
    """
    fake_loaded = "loaded_dataset_csv"

    def fake_load_dataset(format_name, data_files, **kwargs):
        # Verify that CSV is chosen.
        assert format_name == "csv"
        return fake_loaded

    monkeypatch.setattr(
        "modelhub.clients.dataset_client.load_dataset", fake_load_dataset
    )
    split_file_urls = {
        "splitA": [
            "http://example.com/data/file1.csv",
            "http://example.com/data/file2.csv",
        ]
    }
    result = dataset_client._load_dataset_by_format(split_file_urls)
    assert result == fake_loaded


def test__load_dataset_by_format_unsupported(monkeypatch, dataset_client):
    """
    Test that _load_dataset_by_format raises ValueError for unsupported file formats.
    """
    # Provide file URLs with unsupported extension.
    split_file_urls = {
        "splitA": [
            "http://example.com/data/file1.unsupported",
            "http://example.com/data/file2.unsupported",
        ]
    }
    with pytest.raises(ValueError, match="Unsupported file format"):
        dataset_client._load_dataset_by_format(split_file_urls)


# Tests for _collect_split_file_urls


def test__collect_split_file_urls(monkeypatch, dataset_client):
    """
    Test _collect_split_file_urls to ensure it categorizes files correctly.
    """
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    files = [
        {"file_path": "dir/splitA/file1.csv", "version_id": 1},
        {"file_path": "dir/splitA/file2.csv", "version_id": 1},
        {"file_path": "dir/splitB/file3.csv", "version_id": 1},
    ]
    result = dataset_client._collect_split_file_urls(
        "dataset1", files, split=None, directory="dir"
    )
    expected = {
        "splitA": ["signed_dir/splitA/file1.csv", "signed_dir/splitA/file2.csv"],
        "splitB": ["signed_dir/splitB/file3.csv"],
    }
    assert result == expected


def test__collect_split_file_urls_directory_filter(monkeypatch, dataset_client):
    """
    Test that if a directory is specified, files whose file_path do not start with that directory are skipped.
    """
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    files = [
        {"file_path": "dirA/splitA/file1.csv", "version_id": 1},
        {"file_path": "dirB/splitA/file2.csv", "version_id": 1},  # should be skipped
    ]
    result = dataset_client._collect_split_file_urls(
        "dataset1", files, split=None, directory="dirA"
    )
    expected = {"splitA": ["signed_dirA/splitA/file1.csv"]}
    assert result == expected


def test__collect_split_file_urls_with_split_filter(monkeypatch, dataset_client):
    """
    Test that if a split filter is provided, only files matching that split are returned.
    """
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    files = [
        {"file_path": "dir/splitA/file1.csv", "version_id": 1},
        {"file_path": "dir/splitB/file2.csv", "version_id": 1},
    ]
    result = dataset_client._collect_split_file_urls(
        "dataset1", files, split="splitA", directory="dir"
    )
    expected = {"splitA": ["signed_dir/splitA/file1.csv"]}
    assert result == expected


def test__collect_split_file_urls_missing_split(monkeypatch, dataset_client):
    """
    Test that if a split filter is provided and no file matches that split, a ValueError is raised.
    """
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    files = [
        {"file_path": "dir/splitA/file1.csv", "version_id": 1},
        {"file_path": "dir/splitA/file2.csv", "version_id": 1},
    ]
    with pytest.raises(ValueError, match="Split splitB not found in the dataset."):
        dataset_client._collect_split_file_urls(
            "dataset1", files, split="splitB", directory="dir"
        )


def test__collect_split_file_urls_no_directory(monkeypatch, dataset_client):
    """
    Test that when no directory is specified, the code uses the alternative branch
    (using path_parts[-3]) to compute the split name.
    """
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    # For example, for "root/splitA/file1.csv":
    # file_path.split('/') == ["root", "splitA", "file1.csv"]
    # With directory=None, split_name = path_parts[-3] == "root".
    files = [
        {"file_path": "root/splitA/file1.csv", "version_id": 1},
        {"file_path": "root/splitA/file2.csv", "version_id": 1},
        {"file_path": "root/splitB/file3.csv", "version_id": 1},
    ]
    result = dataset_client._collect_split_file_urls(
        "dataset1", files, split=None, directory=None
    )
    expected = {
        "root": [
            "signed_root/splitA/file1.csv",
            "signed_root/splitA/file2.csv",
            "signed_root/splitB/file3.csv",
        ]
    }
    assert result == expected


def test__check_nested_directories(dataset_client):
    """
    Test _check_nested_directories returns all unique parent directories.
    """
    files = [
        {"file_path": "dir/splitA/file1.csv"},
        {"file_path": "dir/splitA/file2.csv"},
        {"file_path": "dir/subdir/splitB/file3.csv"},
    ]
    result = dataset_client._check_nested_directories(files)
    expected = ["dir", "dir/subdir"]
    assert set(result) == set(expected)


def test_get_file_extension(dataset_client):
    """
    Test that get_file_extension returns the correct file extension.
    """
    url = "http://example.com/path/to/file.csv"
    ext = dataset_client.get_file_extension(url)
    assert ext == ".csv"


def test__load_image_dataset(monkeypatch, dataset_client):
    """
    Test _load_image_dataset correctly loads and processes images.
    """
    # Mock the httpx client.get method
    mock_response = MagicMock()
    mock_response.content = b"fake_image_content"
    mock_response.raise_for_status = MagicMock()

    # Mock PIL Image
    mock_img = MagicMock()
    mock_img.mode = "RGB"
    mock_img.convert = MagicMock(return_value=mock_img)

    # Patch the httpx client.get method
    monkeypatch.setattr(dataset_client.client, "get", lambda url: mock_response)
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.PILImage.open", lambda io_bytes: mock_img
    )
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.io.BytesIO", lambda content: b"fake_bytes_io"
    )

    # Create a mock Dataset class
    mock_dataset = MagicMock()
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.Dataset.from_dict",
        lambda dict_data, features: mock_dataset,
    )

    # Create a mock DatasetDict
    mock_dataset_dict = MagicMock()
    mock_dataset_dict_constructor = MagicMock(return_value=mock_dataset_dict)
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.DatasetDict", mock_dataset_dict_constructor
    )

    # Prepare test data
    split_file_urls = {
        "train": ["http://example.com/image1.png", "http://example.com/image2.jpg"],
        "test": ["http://example.com/image3.jpeg"],
    }

    # Call the method
    result = dataset_client._load_image_dataset(split_file_urls)

    # Assert the result is the mock dataset dict
    assert result == mock_dataset_dict

    # Verify DatasetDict was called (not the imported function)
    assert mock_dataset_dict_constructor.call_count == 1


def test_collect_split_file_urls_with_version_and_split(monkeypatch, dataset_client):
    """
    Test that _collect_split_file_urls properly handles version information when collecting URLs.
    Ensures the version_id is passed correctly to get_signed_url.
    """
    # Mock specific version of files with different version IDs
    files = [
        {"file_path": "dir/splitA/file1.csv", "version_id": 1},
        {"file_path": "dir/splitA/file2.csv", "version_id": 2},
    ]

    # Create a spy function for get_signed_url
    called_with = []

    def mock_get_signed_url(dataset_id, file_path, version, **kwargs):
        called_with.append((dataset_id, file_path, version))
        return f"signed_{file_path}_v{version}"

    monkeypatch.setattr(dataset_client, "get_signed_url", mock_get_signed_url)

    # Call the method
    result = dataset_client._collect_split_file_urls(
        "dataset1", files, split=None, directory="dir"
    )

    # Assert result contains URLs with version information
    expected = {
        "splitA": ["signed_dir/splitA/file1.csv_v1", "signed_dir/splitA/file2.csv_v2"]
    }
    assert result == expected

    # Verify get_signed_url was called with correct version IDs
    assert len(called_with) == 2
    assert ("dataset1", "dir/splitA/file1.csv", 1) in called_with
    assert ("dataset1", "dir/splitA/file2.csv", 2) in called_with


def test__load_image_dataset_error_handling(monkeypatch, dataset_client):
    """
    Test _load_image_dataset correctly handles errors when loading images.
    """
    # Mock logger
    mock_logger = MagicMock()
    monkeypatch.setattr("modelhub.clients.dataset_client.logger", mock_logger)

    # Mock httpx client.get to raise an exception
    def mock_client_get(url):
        if url == "http://example.com/bad_image.png":
            raise Exception("Failed to load image")
        mock_resp = MagicMock()
        mock_resp.content = b"fake_image_content"
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    monkeypatch.setattr(dataset_client.client, "get", mock_client_get)

    # Mock PIL Image
    mock_img = MagicMock()
    mock_img.mode = "RGB"
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.PILImage.open", lambda io_bytes: mock_img
    )

    # Mock BytesIO
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.io.BytesIO", lambda content: b"fake_bytes_io"
    )

    # Create a mock Dataset class
    mock_dataset = MagicMock()
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.Dataset.from_dict",
        lambda dict_data, features: mock_dataset,
    )

    # Mock DatasetDict
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.DatasetDict", lambda datasets_dict: MagicMock()
    )

    # Prepare test data with a bad image URL
    split_file_urls = {
        "train": [
            "http://example.com/good_image.png",
            "http://example.com/bad_image.png",
        ]
    }

    # Call the method
    dataset_client._load_image_dataset(split_file_urls)

    # Assert error was logged
    mock_logger.error.assert_called_once()
    # The call should include the bad URL and error message
    assert "http://example.com/bad_image.png" in mock_logger.error.call_args[0][0]


def test__load_dataset_by_format_mixed_formats(monkeypatch, dataset_client):
    """
    Test _load_dataset_by_format correctly handles mixed formats.
    """
    # Mock Dataset.from_dict
    mock_dataset = MagicMock()
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.Dataset.from_dict",
        lambda dict_data: mock_dataset,
    )

    # Mock DatasetDict
    mock_dataset_dict = MagicMock()
    mock_dataset_dict_constructor = MagicMock(return_value=mock_dataset_dict)
    monkeypatch.setattr(
        "modelhub.clients.dataset_client.DatasetDict", mock_dataset_dict_constructor
    )

    # Prepare test data with mixed formats
    split_file_urls = {
        "train": [
            "http://example.com/data/file1.csv",
            "http://example.com/data/file2.json",
        ]
    }

    # Call the method
    result = dataset_client._load_dataset_by_format(split_file_urls)

    # Assert result is the mock dataset dict
    assert result == mock_dataset_dict

    # Verify DatasetDict was called
    assert mock_dataset_dict_constructor.call_count == 1


def test_load_dataset_default_version(monkeypatch, dataset_client):
    """
    Test load_dataset uses the latest version when no version is specified.
    """
    # Mock dataset with multiple versions
    fake_dataset = {
        "id": "1",
        "versions": [
            {
                "version_id": 2,  # Latest version
                "files": [
                    {"file_path": "dir/splitA/file1.csv", "version_id": 2},
                ],
            },
            {
                "version_id": 1,  # Older version
                "files": [
                    {"file_path": "dir/splitA/oldfile.csv", "version_id": 1},
                ],
            },
        ],
    }

    # Mock methods
    monkeypatch.setattr(
        dataset_client,
        "get_dataset_by_name",
        lambda name: fake_dataset if name == "dataset1" else None,
    )
    monkeypatch.setattr(
        dataset_client,
        "get_signed_url",
        lambda dataset_id, file_path, version, **kwargs: f"signed_{file_path}",
    )
    monkeypatch.setattr(
        dataset_client,
        "_load_dataset_by_format",
        lambda split_file_urls: split_file_urls,
    )

    # Call load_dataset without specifying version
    result = dataset_client.load_dataset("dataset1", directory="dir")

    # Should use the first version in the list (version 2)
    expected = {"splitA": ["signed_dir/splitA/file1.csv"]}
    assert result == expected


def test_load_dataset_version_not_found(monkeypatch, dataset_client):
    """
    Test load_dataset raises ValueError when specified version is not found.
    """
    # Mock dataset with versions
    fake_dataset = {
        "id": "1",
        "versions": [{"version_id": 1, "files": []}, {"version_id": 2, "files": []}],
    }

    # Mock get_dataset_by_name
    monkeypatch.setattr(
        dataset_client,
        "get_dataset_by_name",
        lambda name: fake_dataset if name == "dataset1" else None,
    )

    # Call load_dataset with non-existent version
    with pytest.raises(ValueError, match="Version 3 not found for dataset dataset1"):
        dataset_client.load_dataset("dataset1", version=3)
