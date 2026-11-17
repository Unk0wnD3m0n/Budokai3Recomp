#!/usr/bin/env python3
"""Opt-in, private boot diagnostics for an existing Budokai3Recomp full build.

Enables AGRESSIVE_LOGS only for ps2_runtime.cpp, not generated game files.
Reconfigures and incrementally rebuilds existing CMake build.
Never edits, uploads, or distributes original ISO, ELF, or generated game code.
"""
from __future__ import annotations
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / "output" / "private" / "v03-full-build"
WRAPPER = PRIVATE / "wrapper"
BUILD = PRIVATE / "build"
LOGS = PRIVATE / "logs"
CMAKE = WRAPPER / "CMakeLists.txt"
MARKER = "# [budokai3-v04-boot-diag]"
SNIPPET = r'''
# [budokai3-v04-boot-diag] Enable 120-tick heartbeat only for ps2_runtime.cpp.
# Never set the global aggressive-logs option: that recompiles game sources.
set_source_files_properties(
    "${UPSTREAM}/ps2xRuntime/src/lib/ps2_runtime.cpp"
    TARGET_DIRECTORY ps2_runtime
    PROPERTIES COMPILE_DEFINITIONS "AGRESSIVE_LOGS=1"
)
'''
EXE = BUILD / "upstream" / "ps2xRuntime" / "Release" / "ps2EntryRunner.exe"


def run_logged(cmd: list[str], name: str, *, show_all: bool = False) -> int:
    LOGS.mkdir(parents=True, exist_ok=True)
    output = LOGS / name
    print("\n>", subprocess.list2cmdline(cmd), flush=True)
    print("Log local:", output, flush=True)
    count = 0
    with output.open("w", encoding="utf-8", errors="replace") as log:
        try:
            proc = subprocess.Popen(cmd, cwd=PRIVATE, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True,
                                    errors="replace", bufsize=1)
        except OSError as exc:
            print("No se pudo iniciar:", exc)
            return 1
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                log.write(line)
                log.flush()
                count += 1
                important = (
                    "[run:tick]" in line or "Starting execution" in line
                    or "Error during" in line or "ELF file loaded" in line
                    or "No exact recompiled" in line or "fatal" in line.lower()
                    or "error" in line.lower() or "warning" in line.lower()
                    or "Building CXX" in line
                )
                if show_all or important:
                    print(line.rstrip()[:700], flush=True)
                elif count % 250 == 0:
                    print("Procesadas", count, "lineas.", flush=True)
            status = proc.wait()
        except KeyboardInterrupt:
            print("Interrumpido.")
            proc.terminate()
            proc.wait()
            return 130
    print("CODIGO_DE_SALIDA:", status, flush=True)
    if status:
        print("Ultimas 25 lineas:")
        for line in output.read_text(encoding="utf-8", errors="replace").splitlines()[-25:]:
            print(line[:650])
    return status


def main() -> int:
    print("=== BUDOKAI 3: DIAGNOSTICO INCREMENTAL DE ARRANQUE ===", flush=True)
    if sys.platform != "win32":
        print("Solo Windows.")
        return 2
    if not CMAKE.is_file() or not EXE.is_file():
        print("Falta el build v03 existente o ps2EntryRunner.exe.")
        return 2
    cfg = ROOT / "output" / "private" / "v03-range-experiment" / "budokai3-functions-experiment.toml"
    try:
        elf = Path(tomllib.loads(cfg.read_text(encoding="utf-8-sig"))["general"]["input"])
    except (OSError, ValueError, KeyError) as exc:
        print("No pude obtener el ELF desde el TOML:", exc)
        return 2
    if not elf.is_file():
        print("No existe el ELF:", elf)
        return 2
    cmake_source = CMAKE.read_text(encoding="utf-8")
    if MARKER not in cmake_source:
        CMAKE.write_text(cmake_source.rstrip() + "\n" + SNIPPET + "\n", encoding="utf-8")
    print("Activando el heartbeat de PC/DMA/GS solo en el runtime.", flush=True)
    print("Reutilizando los 45171 archivos ya compilados.", flush=True)
    if run_logged(["cmake", "-S", str(WRAPPER), "-B", str(BUILD)], "diag-configure.log"):
        print("Error configurando CMake.")
        return 1
    if run_logged(["cmake", "--build", str(BUILD), "--config", "Release",
                   "--target", "ps2EntryRunner", "--parallel", "4"], "diag-build.log"):
        print("Error en la compilacion incremental.")
        return 1
    print("\nEl EXE se ejecutara. Dejale trabajar unos segundos y CIERRA la ventana fucsia.")
    print("Mira diag-boot.log y las lineas [run:tick] pc=... dma=... gif=... gsw=...")
    return run_logged([str(EXE), str(elf)], "diag-boot.log", show_all=True)


if __name__ == "__main__":
    raise SystemExit(main())
