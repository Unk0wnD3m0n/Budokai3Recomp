#!/usr/bin/env python3
"""Read-only V0.2a ELF32 memory-map inspection for your local PS2 ISO.

Never writes or exports copyrighted game bytes. Output is metadata only.
This is NOT a recompiler, disassembler, or function-map extractor.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path

from inspect_iso import ISO9660, ISOError, normalize_name, parse_elf

PT_LOAD = 1
PF_X = 1
PF_W = 2
PF_R = 4
MAX_HEADERS = 2048


def _hex(n: int) -> str:
    return f"0x{n:08X}"


def find_elf(iso: ISO9660) -> tuple[str, bytes]:
    indexed = {normalize_name(e["name"]): e for e in iso.root_entries()}
    cnf = indexed.get("SYSTEM.CNF")
    if not cnf:
        raise ISOError("No se encontró SYSTEM.CNF en la raíz de la ISO.")
    raw_cnf = iso.read_entry(cnf).decode("latin1", errors="replace")
    match = re.search(r"(?im)^\s*BOOT2\s*=\s*cdrom0:\\?([^\r\n;]+)", raw_cnf)
    if not match:
        raise ISOError("No se pudo reconocer BOOT2 en SYSTEM.CNF.")
    name = match.group(1).strip().replace("/", "\\").split("\\")[-1]
    record = indexed.get(normalize_name(name))
    if not record:
        raise ISOError(f"No se encontró el BOOT2 {name!r} en la raíz.")
    return name, iso.read_entry(record)


def analyze_elf_layout(data: bytes) -> dict:
    basic = parse_elf(data)
    if basic["machine_id"] != 8:
        raise ISOError("El archivo no indica arquitectura MIPS (e_machine=8).")
    endian = "<" if basic["endianness"] == "little" else ">"
    (
        e_type, e_machine, e_version, e_entry, phoff, shoff,
        flags, ehsize, phentsize, phnum, shentsize, shnum, shstrndx
    ) = struct.unpack_from(endian + "HHIIIIIHHHHHH", data, 16)
    if ehsize < 52 or ehsize > len(data):
        raise ISOError("Tamaño de cabecera ELF32 inválido.")
    if phnum > MAX_HEADERS or shnum > MAX_HEADERS:
        raise ISOError("Número excesivo de cabeceras ELF; se aborta.")
    if phnum and (phentsize < 32 or phoff + phentsize * phnum > len(data)):
        raise ISOError("Tabla de segmentos ELF fuera de rango o mal formada.")
    if shnum and (shentsize < 40 or shoff + shentsize * shnum > len(data)):
        raise ISOError("Tabla de secciones ELF fuera de rango o mal formada.")

    segments = []
    for index in range(phnum):
        off = phoff + index * phentsize
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack_from(
            endian + "IIIIIIII", data, off
        )
        if p_filesz and p_offset + p_filesz > len(data):
            raise ISOError(f"Segmento {index} excede el archivo ELF.")
        if p_type == PT_LOAD and p_filesz > p_memsz:
            raise ISOError(f"Segmento LOAD {index}: filesz mayor que memsz.")
        segments.append({
            "index": index,
            "type": "PT_LOAD" if p_type == PT_LOAD else p_type,
            "file_offset": _hex(p_offset),
            "virtual_address": _hex(p_vaddr),
            "physical_address": _hex(p_paddr),
            "file_bytes": p_filesz,
            "memory_bytes": p_memsz,
            "permissions": "".join(char if p_flags & bit else "-" for char, bit in (("R", PF_R), ("W", PF_W), ("X", PF_X))),
            "alignment": p_align,
        })
    sections = []
    for index in range(shnum):
        off = shoff + index * shentsize
        sh_name, sh_type, sh_flags, sh_addr, sh_offset, sh_size, sh_link, sh_info, sh_align, sh_entsize = struct.unpack_from(
            endian + "IIIIIIIIII", data, off
        )
        if sh_type != 8 and sh_size and sh_offset + sh_size > len(data):
            raise ISOError(f"Sección {index} excede el archivo ELF.")
        sections.append({
            "index": index,
            "type": sh_type,
            "virtual_address": _hex(sh_addr),
            "size_bytes": sh_size,
            "flags": _hex(sh_flags),
        })
    executable_loads = [s for s in segments if s["type"] == "PT_LOAD" and "X" in s["permissions"]]
    entry_in_exec = any(int(s["virtual_address"], 16) <= e_entry < int(s["virtual_address"], 16) + s["memory_bytes"] for s in executable_loads)
    return {
        "elf": basic,
        "elf_flags": _hex(flags),
        "program_header_offset": _hex(phoff),
        "section_header_offset": _hex(shoff),
        "entry_in_executable_load_segment": entry_in_exec,
        "load_segment_count": sum(s["type"] == "PT_LOAD" for s in segments),
        "executable_segment_count": len(executable_loads),
        "segments": segments,
        "sections": sections,
        "limitations": [
            "Los segmentos no identifican límites de funciones.",
            "No se ha recompilado, ejecutado ni desensamblado código.",
            "Las direcciones mostradas dependen de esta edición y ELF concreto.",
        ],
    }


def analyze_iso(path: Path) -> dict:
    iso = ISO9660(path)
    try:
        name, elf = find_elf(iso)
        info = analyze_elf_layout(elf)
        return {
            "tool": "Budokai3Recomp / V0.2a",
            "boot2": name,
            "expected_edition": "SLES-53346 (PS2 Collector's Edition Europe)",
            **info,
        }
    finally:
        iso.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mapear los segmentos ELF32 desde la ISO de PS2 (solo lectura)")
    parser.add_argument("iso", type=Path, help="Ruta de la ISO local (no se subirá a ningún sitio)")
    parser.add_argument("--report", type=Path, default=Path("reporte-v02-local.json"), help="Informe JSON local")
    args = parser.parse_args(argv)
    try:
        result = analyze_iso(args.iso)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, ISOError, ValueError, struct.error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print("Budokai3Recomp — V0.2a / mapa de memoria")
    print(f"BOOT2: {result['boot2']} | Punto de entrada: {result['elf']['entry_point']}")
    print(f"Segmentos LOAD: {result['load_segment_count']} | Ejecutables: {result['executable_segment_count']}")
    print(f"El punto de entrada cae en LOAD ejecutable: {result['entry_in_executable_load_segment']}")
    for s in result["segments"]:
        if s["type"] == "PT_LOAD":
            print(f"  LOAD {s['index']}: VA {s['virtual_address']}, bytes {s['memory_bytes']}, permisos {s['permissions']}")
    print(f"Informe JSON local: {args.report}")
    print("AVISO: esto NO recompila el juego ni localiza funciones automáticamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
