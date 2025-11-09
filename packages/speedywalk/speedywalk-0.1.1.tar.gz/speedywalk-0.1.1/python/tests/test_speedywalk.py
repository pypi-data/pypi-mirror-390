import speedywalk


def test_walk(tmp_path):
    """Test that walk returns an iterator of DirEntry objects."""
    # Create some test files and directories
    (tmp_path / "file1.txt").write_text("test")
    (tmp_path / "file2.txt").write_text("test")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file3.txt").write_text("test")

    # Walk the directory
    entries = list(speedywalk.walk(tmp_path))
    paths = {entry.path_str for entry in entries}

    # Check that all expected paths are present
    assert str(tmp_path / "file1.txt") in paths
    assert str(tmp_path / "file2.txt") in paths
    assert str(tmp_path / "subdir") in paths
    assert str(tmp_path / "subdir" / "file3.txt") in paths

    # Check entry properties
    for entry in entries:
        if entry.path_str.endswith("file1.txt"):
            assert entry.is_file
            assert not entry.is_dir
            assert not entry.is_symlink
        elif entry.path_str.endswith("subdir"):
            assert not entry.is_file
            assert entry.is_dir
            assert not entry.is_symlink
