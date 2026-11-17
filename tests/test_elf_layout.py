"""V0.2a ELF32 layout tests using synthetic, copyright-free fixture bytes."""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from inspect_iso import ISOError
from inspect_elf_layout import analyze_elf_layout


def fixture(*, bad_segment=False, entry=0x00100008, with_section=True):
    elf = bytearray(256)
    elf[:16] = b"\x7fELF\x01\x01\x01" + bytes(9)
    phoff = 52
    shoff = 84 if with_section else 0
    # standard 52-byte ELF32 header
    struct.pack_into("<HHIIIIIHHHHHH", elf, 16, 2, 8, 1, entry, phoff, shoff, 0, 52, 32, 1, 40, 1 if with_section else 0, 0)
    # PT_LOAD: code loaded at 0x00100000, 32 bytes file, 64 bytes mem
    # The wrong-offset case deliberately overruns file boundaries.
    struct.pack_into("<IIIIIIII", elf, phoff, 1, 240 if bad_segment else 128, 0x00100000, 0x00100000, 32, 64, 5, 16)
    if with_section:
        # SHT_PROGBITS (section header is optional)
        struct.pack_into("<IIIIIIIIII", elf, shoff, 0, 1, 6, 0x00100000, 128, 32, 0, 0, 16, 0)
    return bytes(elf)


class TestELFLayout(unittest.TestCase):
    def test_valid_load_and_entry(self):
        data = analyze_elf_layout(fixture())
        self.assertEqual(data["load_segment_count"], 1)
        self.assertEqual(data["executable_segment_count"], 1)
        self.assertTrue(data["entry_in_executable_load_segment"])
        self.assertEqual(data["segments"][0]["permissions"], "R-X")
        self.assertEqual(data["sections"][0]["size_bytes"], 32)

    def test_entry_outside_executable_segment(self):
        data = analyze_elf_layout(fixture(entry=0x00200000))
        self.assertFalse(data["entry_in_executable_load_segment"])

    def test_missing_section_headers_supported(self):
        data = analyze_elf_layout(fixture(with_section=False))
        self.assertEqual(data["sections"], [])
        self.assertEqual(data["load_segment_count"], 1)

    def test_reject_segment_outside_elf(self):
        with self.assertRaises(ISOError):
            analyze_elf_layout(fixture(bad_segment=True))

    def test_reject_non_mips_elf(self):
        elf = bytearray(fixture())
        elf[18:20] = (3).to_bytes(2, "little")
        with self.assertRaises(ISOError):
            analyze_elf_layout(bytes(elf))

    def test_reject_truncated_header_table(self):
        elf = bytearray(fixture())
        elf[28:32] = (250).to_bytes(4, "little")
        with self.assertRaises(ISOError):
            analyze_elf_layout(bytes(elf))


if __name__ == "__main__":
    unittest.main()
