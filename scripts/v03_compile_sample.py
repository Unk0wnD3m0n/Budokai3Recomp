#!/usr/bin/env python3
"""Private x64 MSVC smoke test of a small, varied sample of PS2Recomp C++ output.

Run from "x64 Native Tools Command Prompt for VS 2026":
    python scripts\v03_compile_sample.py

Compiles nine additional translation units into private .obj files.
This does not link, run, or validate the correctness of the game.
Do NOT publish generated source, object files, or these diagnostic logs.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

SAMPLE_PER_BUCKET = 3
SOURCE_RE = re.compile(r"FUN_[0-9A-Fa-f]{8}_0x[0-9A-Fa-f]+\.cpp\Z")
ALREADY_TESTED = {
    "FUN_00103018_0x103018.cpp",
    "FUN_00106898_0x106898.cpp",
    "FUN_001077B8_0x1077b8.cpp",
}


def pick_three(values: list[Path]) -> list[Path]:
    if len(values) < SAMPLE_PER_BUCKET:
        raise ValueError("Hay menos de 3 archivos en una categoría de tamaños.")
    values = sorted(values, key=lambda x: x.name.lower())
    indexes = [len(values) // 4, len(values) // 2, (3 * len(values)) // 4]
    return [values[i] for i in indexes]


def main() -> int:
    if not shutil.which("cl.exe"):
        print("ERROR: abre x64 Native Tools Command Prompt (cl.exe no está en PATH).")
        return 2

    project = Path(__file__).resolve().parents[1]
    ps2 = Path.home() / "Desktop" / "PS2Recomp"
    exp = project / "output" / "private" / "v03-range-experiment"
    generated = exp / "generated"
    private = exp / "obj-test" / "batch-v03"
    obj_dir = private / "objects"
    log_dir = private / "logs"

    includes = [
        generated,
        ps2 / "ps2xRuntime" / "include",
        ps2 / "ps2xRuntime" / "src" / "lib" / "Kernel",
        ps2 / "ps2xIOP" / "include",
    ]
    for p in includes:
        if not p.is_dir():
            print(f"ERROR: no existe el directorio requerido: {p}")
            return 2

    sources = sorted(
        (p for p in generated.glob("*.cpp")
         if SOURCE_RE.fullmatch(p.name) and p.name not in ALREADY_TESTED),
        key=lambda p: p.name.lower(),
    )
    buckets: dict[str, list[Path]] = {"small": [], "medium": [], "large": []}
    for source in sources:
        size = source.stat().st_size
        if 1024 <= size < 15_000:
            buckets["small"].append(source)
        elif 15_000 <= size < 60_000:
            buckets["medium"].append(source)
        elif 60_000 <= size <= 180_000:
            buckets["large"].append(source)

    try:
        selected = (
            pick_three(buckets["small"])
            + pick_three(buckets["medium"])
            + pick_three(buckets["large"])
        )
    except ValueError as exc:
        print(f"ERROR: {exc}")
        print({key: len(value) for key, value in buckets.items()})
        return 2

    obj_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    success = 0
    print("MSVC C++20 / x64 — muestra privada de 9 funciones")
    print("Generación:", generated)
    print("Objetos:", obj_dir)
    print("No se modifica la ISO, ELF, CSV ni el código generado.\n")

    for i, source in enumerate(selected, start=1):
        obj = obj_dir / (source.stem + ".obj")
        log = log_dir / (source.stem + ".log")
        cmd = [
            "cl.exe",
            "/nologo", "/std:c++20", "/EHsc", "/arch:AVX2", "/Od", "/c",
            "/Fo" + str(obj),
            *("/I" + str(path) for path in includes),
            str(source),
        ]
        # Never use shell=True; use one compiler invocation per translation unit.
        try:
            with log.open("w", encoding="utf-8", errors="replace") as handle:
                result = subprocess.run(
                    cmd, cwd=private, stdout=handle,
                    stderr=subprocess.STDOUT, check=False,
                    timeout=180,
                )
            obj_size = obj.stat().st_size if obj.is_file() else 0
            passed = result.returncode == 0 and obj_size > 0
            if passed:
                success += 1
            print(
                f"{i:02}/09 {'OK' if passed else 'ERROR'} "
                f"{source.name} [{source.stat().st_size} bytes C++, "
                f"{obj_size} bytes OBJ; cl={result.returncode}]"
            )
            if not passed:
                print("  Diagnóstico:", log)
                for line in log.read_text(encoding="utf-8", errors="replace").splitlines()[:12]:
                    print("  ", line)
        except subprocess.TimeoutExpired:
            print(f"{i:02}/09 TIMEOUT {source.name}; consulta {log}")

    print(f"\nRESULTADO: {success}/9 archivos objeto válidos (>0 bytes).")
    print("Esto NO demuestra que se puedan enlazar ni que el juego arranque.")
    print("NO subas a GitHub el ELF, ISO, CSV, TOML, C++ ni OBJ del juego.")
    return 0 if success == len(selected) else 1


if __name__ == "__main__":
    raise SystemExit(main())
