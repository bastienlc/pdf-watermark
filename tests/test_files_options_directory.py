"""
Test FilesOptions behavior with directory inputs and the add_directory_to_files function.
"""

import os
import tempfile
from pathlib import Path

import pytest

from pdf_watermark.options import FilesOptions, add_directory_to_files


class TestAddDirectoryToFiles:
    """Test the standalone add_directory_to_files function."""

    def test_add_directory_to_files_flat_structure(self):
        """Test function with a flat directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test PDF files
            input_dir = os.path.join(temp_dir, "input")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(input_dir)

            # Create some test PDF files
            pdf_files = ["file1.pdf", "file2.PDF", "file3.pdf"]
            non_pdf_files = ["file.txt", "image.png"]

            for pdf_file in pdf_files:
                Path(os.path.join(input_dir, pdf_file)).touch()

            for non_pdf_file in non_pdf_files:
                Path(os.path.join(input_dir, non_pdf_file)).touch()

            # Call the function
            input_files, output_files = add_directory_to_files(input_dir, output_dir)

            # Verify results
            assert len(input_files) == 3  # Only PDF files
            assert len(output_files) == 3
            assert len(input_files) == len(output_files)

            # Check that all returned files are PDFs
            for input_file in input_files:
                assert input_file.endswith((".pdf", ".PDF"))
                assert os.path.exists(input_file)

            # Check output directory was created
            assert os.path.exists(output_dir)

    def test_add_directory_to_files_recursive_structure(self):
        """Test function with a recursive directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested directory structure
            input_dir = os.path.join(temp_dir, "input")
            output_dir = os.path.join(temp_dir, "output")

            # Create structure: input/subdir1/subdir2/
            subdir1 = os.path.join(input_dir, "subdir1")
            subdir2 = os.path.join(subdir1, "subdir2")
            os.makedirs(subdir2)

            # Create PDF files at different levels
            test_files = [
                (input_dir, "root.pdf"),
                (subdir1, "sub1.pdf"),
                (subdir2, "sub2.PDF"),
                (subdir2, "another.pdf"),
            ]

            for directory, filename in test_files:
                Path(os.path.join(directory, filename)).touch()

            # Call the function
            input_files, output_files = add_directory_to_files(input_dir, output_dir)

            # Verify results
            assert len(input_files) == 4
            assert len(output_files) == 4

            # Check that all files are accounted for
            expected_input_files = {
                os.path.join(input_dir, "root.pdf"),
                os.path.join(subdir1, "sub1.pdf"),
                os.path.join(subdir2, "sub2.PDF"),
                os.path.join(subdir2, "another.pdf"),
            }
            assert set(input_files) == expected_input_files

            # Check output paths mirror input structure
            for input_file, output_file in zip(input_files, output_files):
                rel_path = os.path.relpath(input_file, input_dir)
                expected_output = os.path.join(output_dir, rel_path)
                assert output_file == expected_output

    def test_add_directory_to_files_invalid_directory(self):
        """Test function with invalid directory input."""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_dir = os.path.join(temp_dir, "does_not_exist")
            output_dir = os.path.join(temp_dir, "output")

            with pytest.raises(
                ValueError, match="Directory argument must be a directory"
            ):
                add_directory_to_files(non_existent_dir, output_dir)

    def test_add_directory_to_files_empty_directory(self):
        """Test function with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "input")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(input_dir)

            input_files, output_files = add_directory_to_files(input_dir, output_dir)

            assert input_files == []
            assert output_files == []
            # Output directory is only created when files are found
            assert not os.path.exists(output_dir)


class TestFilesOptionsWithDirectories:
    """Test FilesOptions validation and integration behavior with directory inputs."""

    def test_files_options_directory_output_none_vs_separate(self):
        """Test FilesOptions with directory input: output=None vs separate output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test directory structure
            input_dir = os.path.join(temp_dir, "input")
            output_dir = os.path.join(temp_dir, "output")
            os.makedirs(input_dir)

            # Create test PDF files
            Path(os.path.join(input_dir, "file1.pdf")).touch()
            Path(os.path.join(input_dir, "file2.PDF")).touch()

            # Test case 1: output=None (in-place modification)
            files_options_inplace = FilesOptions(
                file=os.path.relpath(input_dir, os.getcwd()),
                output=None,
                dry_run=False,
                workers=1,
            )

            # Input and output should be the same (in-place)
            assert (
                files_options_inplace.input_files == files_options_inplace.output_files
            )
            assert len(files_options_inplace.input_files) == 2

            # Test case 2: separate output directory
            files_options_separate = FilesOptions(
                file=os.path.relpath(input_dir, os.getcwd()),
                output=os.path.relpath(output_dir, os.getcwd()),
                dry_run=False,
                workers=1,
            )

            # Input and output should be different
            assert (
                files_options_separate.input_files
                != files_options_separate.output_files
            )
            assert len(files_options_separate.input_files) == 2
            assert len(files_options_separate.output_files) == 2

            # Verify output paths are in output directory
            for output_file in files_options_separate.output_files:
                assert output_dir in output_file

    def test_files_options_directory_validation_errors(self):
        """Test FilesOptions validation with invalid directory combinations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "input")
            os.makedirs(input_dir)
            Path(os.path.join(input_dir, "test.pdf")).touch()

            # Test: directory input with PDF file output (should fail)
            with pytest.raises(
                ValueError, match="Output must be a directory when input is a directory"
            ):
                FilesOptions(
                    file=os.path.relpath(input_dir, os.getcwd()),
                    output="output.pdf",
                    dry_run=False,
                    workers=1,
                )
