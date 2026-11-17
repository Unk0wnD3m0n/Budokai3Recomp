#!/usr/bin/env python3
"""Read-only inspection of the first Budokai 3 boot-loop PC addresses.

Looks up owners in the user's PRIVATE exported CSV and prints small excerpts
from locally generated C++ files. Does not edit files or invoke a compiler.
Do not upload game-derived C++ or private CSVs/ELFs to GitHub.
"""
from __future__ import annotations
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "output" / "private" / "v03-range-experiment" / "budokai3-functions-experiment.csv"
CPP = ROOT / "output" / "private" / "v03-range-experiment" / "generated"
TARGETS = (0x0010D978, 0x0010D980, 0x0014EF40)
CONTEXT = 5
MAX_MATCHES_PER_FILE = 5


def number(value: str) -> int:
    return int(value.strip(), 0)


def source_files(name: str, start: int) -> list[Path]:
    matches = []
    for guess in (
        f"{name}_0x{start:x}.cpp",
        f"{name}_0x{start:X}.cpp",
        f"{name}.cpp",
    ):
        candidate = CPP / guess
        if candidate.is_file() and candidate not in matches:
            matches.append(candidate)
    if not matches:
        # One directory lookup if naming is different in this tool revision.
        matches = list(CPP.glob(f"*0x{start:x}.cpp"))[:4]
    return matches[:3]


def show_source(path: Path, addr: int) -> None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        print("No se pudo abrir:", exc)
        return
    print(f"  C++ privado: {path.name} ({len(lines)} lineas)")
    hex_addr = f"{addr:x}"
    pattern = re.compile(
        rf"(?:0x0*{hex_addr}\b|label_0*{hex_addr}\b|case\s+0x0*{hex_addr}\b)",
        re.IGNORECASE,
    )
    hits = [i for i, line in enumerate(lines) if pattern.search(line)]
    if not hits:
        print("  No hay coincidencia literal. Inicio del C++:")
        for i, line in enumerate(lines[:18]):
            print(f"    {i + 1:5}: {line[:230]}")
        return
    print(f"  Referencias a la direccion: {len(hits)}")
    for line_no in hits[:MAX_MATCHES_PER_FILE]:
        left = max(line_no - CONTEXT, 0)
        right = min(line_no + CONTEXT + 1, len(lines))
        print(f"    --- lineas {left+1}-{right} ---")
        for i in range(left, right):
            print(f"    {i+1:5}: {lines[i][:240]}")


def main() -> int:
    print("=== BUDOKAI 3: INSPECCION PRIVADA DE BUCLE DE ARRANQUE ===")
    print("Solo lectura; no se ejecuta CMake, MSVC, Ghidra ni el juego.")
    if not CSV.is_file() or not CPP.is_dir():
        print("Faltan el CSV experimental o los C++ privados.")
        print("CSV esperado:", CSV)
        return 2
    owners = {a: [] for a in TARGETS}
    try:
        with CSV.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                start = number(row["Start"])
                end = number(row["End"])
                if end <= start:
                    continue
                for address in TARGETS:
                    if start <= address < end:
                        owners[address].append((end-start, -start, row["Name"], start, end))
    except (OSError, KeyError, ValueError) as exc:
        print("ERROR leyendo CSV:", exc)
        return 2

    for addr in TARGETS:
        print(f"\n=== PC / destino 0x{addr:08X} ===")
        candidates = sorted(owners[addr])
        if not candidates:
            print("NINGUN rango CSV contiene esta direccion; investigar mapa y dispatch.")
            continue
        print("Rangos CSV candidatos:", len(candidates))
        for _, _, name, start, end in candidates[:4]:
            print(f"  {name} 0x{start:08X}..0x{end:08X} ({end-start} bytes)")
        _, _, name, start, end = candidates[0]
        files = source_files(name, start)
        if not files:
            print("No encontro archivo C++ para el rango mas corto.")
        for path in files:
            show_source(path, addr)
    print("\nEnvia SOLO el texto impreso por este script (NO el CPP entero).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
