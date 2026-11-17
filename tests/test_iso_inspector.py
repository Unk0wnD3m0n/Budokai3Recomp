"""Only synthetic ISO9660 fixture bytes. No commercial game assets."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from inspect_iso import ISOError, analyze, parse_elf  # noqa: E402

SECTOR = 2048


def record(name: bytes, lba: int, size: int, directory: bool = False) -> bytes:
    n = 33 + len(name) + (0 if len(name) % 2 else 1)
    r = bytearray(n)
    r[0] = n
    r[2:6] = lba.to_bytes(4, "little")
    r[6:10] = lba.to_bytes(4, "big")
    r[10:14] = size.to_bytes(4, "little")
    r[14:18] = size.to_bytes(4, "big")
    r[25] = 2 if directory else 0
    r[28:30] = (1).to_bytes(2, "little")
    r[30:32] = (1).to_bytes(2, "big")
    r[32] = len(name)
    r[33:33 + len(name)] = name
    return bytes(r)


def synthetic_iso(serial: str) -> bytes:
    iso = bytearray(32 * SECTOR)
    pvd = 16 * SECTOR
    iso[pvd] = 1
    iso[pvd + 1:pvd + 6] = b"CD001"
    iso[pvd + 6] = 1
    iso[pvd + 40:pvd + 72] = b"TEST_ONLY_SYNTHETIC".ljust(32)
    root = record(b"\x00", 20, SECTOR, directory=True)
    iso[pvd + 156:pvd + 156 + len(root)] = root
    vdt = 17 * SECTOR
    iso[vdt] = 255
    iso[vdt + 1:vdt + 6] = b"CD001"
    elf_name = f"{serial[:4]}_{serial[5:8]}.{serial[8:]};1".encode("ascii")
    cnf = f"BOOT2 = cdrom0:\\{elf_name.decode()}\r\nVER = 1.00\r\n".encode("ascii")
    elf = bytearray(52)
    elf[:16] = b"\x7fELF\x01\x01\x01" + bytes(9)
    import struct
    struct.pack_into("<HHIIIIIHHHHHH", elf, 16, 2, 8, 1, 0x00100000, 52, 0, 0, 52, 32, 0, 40, 0, 0)
    directory = b"".join([
        record(b"\x00", 20, SECTOR, directory=True),
        record(b"\x01", 20, SECTOR, directory=True),
        record(b"SYSTEM.CNF;1", 21, len(cnf)),
        record(elf_name, 22, len(elf)),
    ])
    iso[20 * SECTOR:20 * SECTOR + len(directory)] = directory
    iso[21 * SECTOR:21 * SECTOR + len(cnf)] = cnf
    iso[22 * SECTOR:22 * SECTOR + len(elf)] = elf
    return bytes(iso)


class TestInspection(unittest.TestCase):
    def check(self, data: bytes):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "synthetic.iso"
            path.write_bytes(data)
            return analyze(path)

    def test_collector_serial(self):
        result = self.check(synthetic_iso("SLES-53346"))
        self.assertTrue(result["target_serial_match"])
        self.assertEqual(result["elf"]["machine"], "MIPS")
        self.assertEqual(result["elf"]["entry_point"], "0x00100000")

    def test_other_edition_is_not_marked_supported(self):
        result = self.check(synthetic_iso("SLUS-20998"))
        self.assertFalse(result["target_serial_match"])
        self.assertEqual(result["region"], "USA/NTSC-U")

    def test_reject_non_iso(self):
        with self.assertRaises(ISOError):
            self.check(bytes(32 * SECTOR))

    def test_reject_non_elf(self):
        with self.assertRaises(ISOError):
            parse_elf(bytes(100))


if __name__ == "__main__":
    unittest.main()
