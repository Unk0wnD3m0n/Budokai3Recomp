#!/usr/bin/env python3
"""Extract PS2 BOOT2 ELF from a personal ISO for LOCAL reverse-engineering.

This tool never runs game code or connects to the Internet. Keep the
copyrighted output private; output/ is excluded from the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

from inspect_iso import ISO9660, ISOError, normalize_name, parse_elf

EXPECTED_BOOT2 = "SLES_533.46"


def find_boot2(iso: ISO9660) -> tuple[str, bytes]:
    files = {normalize_name(e["name"]): e for e in iso.root_entries()}
    cnf = files.get("SYSTEM.CNF")
    if cnf is None:
        raise ISOError("SYSTEM.CNF no encontrado en la raíz.")
    system = iso.read_entry(cnf).decode("latin-1", errors="replace")
    match = re.search(r"(?im)^\s*BOOT2\s*=\s*cdrom0:\\?([^\r\n;]+)", system)
    if match is None:
        raise ISOError("No se pudo reconocer BOOT2 en SYSTEM.CNF.")
    name = normalize_name(match.group(1).strip().replace("/", "\\").split("\\")[-1])
    if name != EXPECTED_BOOT2:
        raise ISOError(f"Edición no compatible con este experimento: {name!r}; se esperaba {EXPECTED_BOOT2}.")
    entry = files.get(name)
    if entry is None:
        raise ISOError("No se encontró el ELF indicado por BOOT2.")
    data = iso.read_entry(entry)
    elf = parse_elf(data)
    if elf["machine_id"] != 8 or elf["endianness"] != "little":
        raise ISOError("El ejecutable no es un ELF32 MIPS little-endian reconocido.")
    return name, data


def export_local(iso_path: Path, destination: Path) -> dict:
    """Create a local ELF with exclusive creation (never overwrite an existing one)."""
    if destination.exists() and not destination.is_dir():
        raise ISOError("La ruta de salida ya existe y no es una carpeta.")
    iso = ISO9660(iso_path)
    try:
        name, data = find_boot2(iso)
    finally:
        iso.close()
    destination.mkdir(parents=True, exist_ok=True)
    output = destination / f"{name}.elf"
    # Refuse accidental overwrite; do not follow an existing symlink to an output file.
    with output.open("xb") as stream:
        stream.write(data)
    return {"file_name": output.name, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extraer ELF local (NO publicarlo en GitHub)")
    parser.add_argument("iso", type=Path, help="Ruta de tu ISO propia SLES-53346")
    parser.add_argument("--output-dir", type=Path, default=Path("output/private"), help="Carpeta de salida local, ignorada por git")
    args = parser.parse_args(argv)
    try:
        result = export_local(args.iso, args.output_dir)
    except FileExistsError:
        print("ERROR: El ELF de salida ya existe; no se sobrescribió.", file=sys.stderr)
        return 2
    except (ISOError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print("Budokai3Recomp V0.2b — ELF extraído SOLO en tu PC")
    print(f"Archivo: {result['file_name']} | Bytes: {result['size_bytes']}")
    print(f"SHA-256: {result['sha256']}")
    print("NO subas el ELF, la ISO ni los archivos de juego al repositorio.")
    print("Siguiente paso: importación local en Ghidra. No es un port ejecutable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
