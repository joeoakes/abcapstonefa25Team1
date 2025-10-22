from abcapstonefa25team1.backend.utils import read_write


def test_write_and_read_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    content = "Hello, utils test!"

    # Write to the file
    read_write.write_file(file_path, content)

    # Read from the file
    result = read_write.read_file(file_path)

    # Check correctness
    assert result == content
