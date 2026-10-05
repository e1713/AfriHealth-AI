import io
import tempfile
import unittest
from pathlib import Path

from validate_and_prep import (
    PROJECT_DIRECTORIES,
    create_project_directories,
    find_wav_files,
    format_duration_distribution,
    run_validation,
)


class AudioPreparationTests(unittest.TestCase):
    def test_directory_setup_creates_expected_sibling_folders(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            directories = create_project_directories(root)

            self.assertEqual(set(directories), set(PROJECT_DIRECTORIES))
            self.assertTrue(all(path.is_dir() for path in directories.values()))
            self.assertTrue(all(path.parent == root for path in directories.values()))

    def test_wav_discovery_is_recursive_and_case_insensitive(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            raw_audio = Path(temporary_directory) / "raw_audio"
            nested = raw_audio / "batch-1"
            nested.mkdir(parents=True)
            upper_case = nested / "CS-01.WAV"
            lower_case = raw_audio / "CS-02.wav"
            ignored = raw_audio / "notes.txt"
            upper_case.touch()
            lower_case.touch()
            ignored.touch()

            self.assertEqual(
                find_wav_files(raw_audio),
                sorted([upper_case, lower_case], key=lambda path: path.as_posix().casefold()),
            )

    def test_duration_distribution_reports_summary_statistics(self):
        self.assertEqual(
            format_duration_distribution([1.0, 3.0, 5.0]),
            "Duration distribution (seconds): min=1.00, median=3.00, "
            "mean=3.00, max=5.00",
        )
        self.assertIn("unavailable", format_duration_distribution([]))

    def test_run_reports_empty_dataset_and_creates_directories(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = io.StringIO()
            result = run_validation(Path(temporary_directory), output=output)

            self.assertEqual(result, 1)
            self.assertIn("No WAV files found", output.getvalue())
            self.assertTrue(
                all(
                    (Path(temporary_directory) / directory).is_dir()
                    for directory in PROJECT_DIRECTORIES
                )
            )


if __name__ == "__main__":
    unittest.main()
