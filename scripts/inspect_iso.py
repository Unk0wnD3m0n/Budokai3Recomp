#!/usr/bin/env python3
"""Read-only ISO9660/PS2 ELF inventory for Budokai3Recomp V0.1.

Does NOT execute, extract to disk, upload, or modify game data.
Pure standard library. Supported: 2048-byte-per-sector ISO9660 disc images.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

SECTOR = 2048
TARGET_SERIAL = "SLES-53346"
MAX_METADATA_FILE = 64 * 1024 * 1024  # memory ceiling; no bulk export


class ISOError(Exception):
    """Error parsing an unsupported or malformed optical image."""


class ISO9660:
    def __init__(self, path: Path):
        self.path = path
        self.file = path.open("rb")
        try:
            self.length = path.stat().st_size
            if self.length < 18 * SECTOR:
                raise ISOError("El archivo es demasiado pequeño para ser una ISO9660.")
            pvd = self.read_at(16 * SECTOR, SECTOR)
            if pvd[:1] != b"\x01" or pvd[1:6] != b"CD001":
                raise ISOError("Formato ISO9660 no encontrado (se esperan sectores de 2048 bytes).")
            self.label = pvd[40:72].decode("ascii", errors="replace").strip()
            self.root = self._record(pvd, 156)
            if not self.root["is_dir"]:
                raise ISOError("El directorio raíz ISO9660 es inválido.")
        except Exception:
            self.file.close()
            raise

    def close(self):
        self.file.close()

    def read_at(self, offset: int, size: int) -> bytes:
        if offset < 0 or size < 0 or offset + size > self.length:
            raise ISOError("Intento de lectura fuera del tamaño de la ISO.")
        self.file.seek(offset)
        result = self.file.read(size)
        if len(result) != size:
            raise ISOError("No se pudo leer la imagen del disco por completo.")
        return result

    @staticmethod
    def _record(data: bytes, start: int) -> dict:
        if start >= len(data):
            raise ISOError("Registro ISO9660 fuera de rango.")
        record_size = data[start]
        if record_size < 34 or start + record_size > len(data):
            raise ISOError("Registro de directorio ISO9660 inválido.")
        d = data[start:start + record_size]
        name_length = d[32]
        if name_length + 33 > len(d):
            raise ISOError("Nombre de archivo ISO9660 inválido.")
        name_bytes = d[33:33 + name_length]
        name = ("." if name_bytes == b"\x00" else ".." if name_bytes == b"\x01"
                else name_bytes.decode("ascii", errors="replace"))
        return {
            "name": name,
            "lba": int.from_bytes(d[2:6], "little"),
            "size": int.from_bytes(d[10:14], "little"),
            "is_dir": bool(d[25] & 0x02),
        }

    def root_entries(self) -> list[dict]:
        root_length = self.root["size"]
        if root_length > MAX_METADATA_FILE:
            raise ISOError("El directorio raíz supera el límite del analizador.")
        data = self.read_at(self.root["lba"] * SECTOR, root_length)
        entries = []
        offset = 0
        while offset < len(data):
            length = data[offset]
            if length == 0:
                offset = (offset // SECTOR + 1) * SECTOR
                continue
            rec = self._record(data, offset)
            if rec["name"] not in (".", ".."):
                entries.append(rec)
            offset += length
        return entries

    def read_entry(self, entry: dict) -> bytes:
        if entry["is_dir"] or entry["size"] > MAX_METADATA_FILE:
            raise ISOError("No es un archivo pequeño regular que podamos analizar.")
        return self.read_at(entry["lba"] * SECTOR, entry["size"])


def normalize_name(name: str) -> str:
    return name.upper().split(";", 1)[0]


def parse_elf(data: bytes) -> dict:
    if len(data) < 52 or data[:4] != b"\x7fELF":
        raise ISOError("El ejecutable BOOT2 no tiene cabecera ELF válida.")
    elf_class, elf_endian = data[4], data[5]
    if elf_class != 1 or elf_endian not in (1, 2):
        raise ISOError("Se esperaba ELF de 32 bits, little-endian o big-endian.")
    endian = "<" if elf_endian == 1 else ">"
    e_type, machine, version, entry, phoff, shoff, flags, ehsize, phentsize, phnum, shentsize, shnum, shstrndx = struct.unpack_from(
        endian + "HHIIIIIHHHHHH", data, 16)
    return {
        "format": "ELF32",
        "endianness": "little" if elf_endian == 1 else "big",
        "machine_id": machine,
        "machine": "MIPS" if machine == 8 else "other",
        "entry_point": f"0x{entry:08X}",
        "program_headers": phnum,
        "section_headers": shnum,
        "elf_type": e_type,
        "file_sha256": hashlib.sha256(data).hexdigest(),
    }


def analyze(path: Path) -> dict:
    iso = ISO9660(path)
    try:
        entries = iso.root_entries()
        indexed = {normalize_name(e["name"]): e for e in entries}
        system = indexed.get("SYSTEM.CNF")
        if system is None:
            raise ISOError("No existe SYSTEM.CNF en el directorio raíz.")
        text = iso.read_entry(system).decode("latin-1", errors="replace")
        match = re.search(r"(?im)^\s*BOOT2\s*=\s*cdrom0:\\?([^\r\n;]+)", text)
        if not match:
            raise ISOError("SYSTEM.CNF no contiene BOOT2 con formato conocido.")
        filename = match.group(1).strip().replace("/", "\\").split("\\")[-1]
        boot = indexed.get(normalize_name(filename))
        if boot is None:
            raise ISOError(f"El ejecutable BOOT2 {filename!r} no está en la raíz.")
        exe = iso.read_entry(boot)
        elf = parse_elf(exe)
        code = re.fullmatch(r"([A-Z]{4})_(\d{3})\.(\d{2})", normalize_name(filename))
        serial = f"{code.group(1)}-{code.group(2)}{code.group(3)}" if code else "unknown"
        region = "Europe/PAL" if serial.startswith(("SLES", "SCES")) else (
            "USA/NTSC-U" if serial.startswith(("SLUS", "SCUS")) else (
            "Japan/NTSC-J" if serial.startswith(("SLPS", "SLPM", "SCPS")) else "unknown"))
        return {
            "project": "Budokai3Recomp",
            "tool_version": "0.1.0",
            "target_serial": TARGET_SERIAL,
            "detected_serial": serial,
            "target_serial_match": serial == TARGET_SERIAL,
            "region": region,
            "iso9660_label": iso.label,
            "iso_bytes": iso.length,
            "boot2": filename,
            "elf_bytes": boot["size"],
            "elf": elf,
            "root_entry_count": len(entries),
            "warning": "Solo inspección de metadatos: NO demuestra compatibilidad con recompilación.",
        }
    finally:
        iso.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspeccionar ISO PS2 sin modificarla")
    parser.add_argument("iso", type=Path, help="Ruta local a tu ISO (sectores 2048 bytes)")
    parser.add_argument("--report", type=Path, help="Guardar metadatos como JSON local")
    args = parser.parse_args(argv)
    try:
        result = analyze(args.iso)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, ISOError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print("Budokai3Recomp — inspección local V0.1.0")
    print(f"Serie detectada: {result['detected_serial']} | Región: {result['region']}")
    print(f"Objetivo SLES-53346: {'COINCIDE' if result['target_serial_match'] else 'NO COINCIDE'}")
    print(f"BOOT2: {result['boot2']} | ELF: {result['elf']['machine']} ({result['elf']['format']})")
    print(f"Punto de entrada: {result['elf']['entry_point']} | SHA256 ELF: {result['elf']['file_sha256']}")
    if args.report:
        print(f"Informe local: {args.report}")
    print(result['warning'])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
