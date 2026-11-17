#!/usr/bin/env python3
"""Create an isolated local A/B test of three suspect PS2Recomp CSV ranges.

The modified ranges are *experimental*, not validated function boundaries.
Never publish the source CSV, TOML, ELF, ISO, or generated C++.
"""
from __future__ import annotations

import csv
import io
import re
import sys
import tomllib
from pathlib import Path

# Exact original map ranges from this edition's Ghidra/PowerShell diagnostics.
# Ghidra shows two decoded instructions followed by undefined data at each start.
SUSPECTS: dict[str, tuple[int, int]] = {
    "entry_00403fc0": (0x00403FC0, 0x00421720),
    "entry_004217d0": (0x004217D0, 0x0042C020),
    "entry_0042c020": (0x0042C020, 0x0042D000),
}
PROBE_SIZE = 8


def prepare(project: Path) -> tuple[Path, Path, int]:
    """Prepare separate CSV/TOML copies. Never overwrite original files."""
    project = project.resolve()
    source_csv = project / "budokai3-functions.csv"
    source_toml = project / "budokai3-functions.toml"
    if not source_csv.is_file() or not source_toml.is_file():
        raise ValueError("Falta el CSV o TOML original en la raíz del proyecto.")

    toml_text = source_toml.read_text(encoding="utf-8-sig")
    config = tomllib.loads(toml_text)["general"]
    if not Path(config["input"]).is_file():
        raise ValueError("El ELF indicado en input no existe.")
    if Path(config["ghidra_output"]).resolve() != source_csv.resolve():
        raise ValueError("ghidra_output debe apuntar al CSV original del proyecto.")

    csv_text = source_csv.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(io.StringIO(csv_text))
    if reader.fieldnames != ["Name", "Start", "End", "Size"]:
        raise ValueError("Las columnas del CSV deben ser Name,Start,End,Size.")
    rows = list(reader)
    if any(None in row or None in row.values() for row in rows):
        raise ValueError("CSV mal formado.")

    seen: set[str] = set()
    for row in rows:
        name = row["Name"].lower()
        if name not in SUSPECTS:
            continue
        if name in seen:
            raise ValueError(f"Entrada duplicada: {name}")
        seen.add(name)
        expected_start, expected_end = SUSPECTS[name]
        start = int(row["Start"], 0)
        end = int(row["End"], 0)
        size = int(row["Size"], 10)
        if (start, end, size) != (
            expected_start, expected_end, expected_end - expected_start
        ):
            raise ValueError(f"Rango inesperado para {name}: {row!r}")
        # Controlled 8-byte probe: not a claim that the real function ends here.
        row["End"] = f"0x{start + PROBE_SIZE:08X}"
        row["Size"] = str(PROBE_SIZE)

    missing = set(SUSPECTS) - seen
    if missing:
        raise ValueError(f"Entradas no encontradas: {', '.join(sorted(missing))}")

    private = project / "output" / "private" / "v03-range-experiment"
    csv_out = private / "budokai3-functions-experiment.csv"
    toml_out = private / "budokai3-functions-experiment.toml"
    generated_out = private / "generated"
    if any(p.exists() for p in (csv_out, toml_out, generated_out)):
        raise ValueError("La prueba ya existe. No se sobrescribe output/private/v03-range-experiment.")

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=["Name", "Start", "End", "Size"],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)

    replacements = {
        "output": generated_out.as_posix(),
        "ghidra_output": csv_out.as_posix(),
    }
    for key, value in replacements.items():
        pattern = re.compile(rf"(?m)^(\s*{re.escape(key)}\s*=\s*).*$")
        toml_text, count = pattern.subn(
            lambda match: match.group(1) + f'"{value}"', toml_text
        )
        if count != 1:
            raise ValueError(f"Se esperaba una sola opción {key}= en el TOML.")
    new_config = tomllib.loads(toml_text)["general"]
    if (
        new_config["output"] != generated_out.as_posix()
        or new_config["ghidra_output"] != csv_out.as_posix()
    ):
        raise ValueError("La configuración experimental no es válida.")

    private.mkdir(parents=True, exist_ok=True)
    csv_out.write_text(buffer.getvalue(), encoding="utf-8", newline="")
    toml_out.write_text(toml_text, encoding="utf-8", newline="")
    return csv_out, toml_out, len(rows)


def main() -> int:
    project = Path(__file__).resolve().parents[1]
    try:
        csv_out, toml_out, total = prepare(project)
    except (OSError, KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"CSV experimental: {csv_out}")
    print(f"TOML experimental: {toml_out}")
    print(f"Registros CSV: {total}; entradas ajustadas: {len(SUSPECTS)}")
    for name, (start, end) in SUSPECTS.items():
        print(
            f"  {name}: 0x{start:08X}-0x{end:08X}"
            f" -> 0x{start:08X}-0x{start + PROBE_SIZE:08X}"
        )
    print("Solo prueba A/B; NO es una corrección definitiva. Originales intactos.")
    print("NO publiques CSV, TOML, ISO, ELF ni archivos CPP derivados del juego.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
