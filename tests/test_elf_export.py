"""Tests with only generated PS2-like ELF data; no commercial files."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_local_elf import export_local
from inspect_iso import ISOError
from test_iso_inspector import synthetic_iso


class TestLocalExport(unittest.TestCase):
    def test_export_original_name_and_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "synthetic.iso"
            source.write_bytes(synthetic_iso("SLES-53346"))
            result = export_local(source, root / "output/private")
            output = root / "output/private" / result["file_name"]
            self.assertEqual(result["file_name"], "SLES_533.46.elf")
            self.assertEqual(output.read_bytes()[:4], b"\x7fELF")
            self.assertEqual(result["size_bytes"], 52)

    def test_reject_other_serial(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "synthetic.iso"
            source.write_bytes(synthetic_iso("SLUS-20998"))
            with self.assertRaises(ISOError):
                export_local(source, root / "output/private")
            self.assertFalse((root / "output").exists())

    def test_never_overwrite_existing_elf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "synthetic.iso"
            source.write_bytes(synthetic_iso("SLES-53346"))
            export_local(source, root / "output/private")
            with self.assertRaises(FileExistsError):
                export_local(source, root / "output/private")


if __name__ == "__main__":
    unittest.main()
