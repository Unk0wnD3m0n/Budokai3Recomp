#!/usr/bin/env python3
"""Attempt to build all private Budokai3Recomp V0.3 C++ sources with PS2Recomp runtime.
Run in x64 Native Tools Command Prompt: python scripts\v03_build_full.py
Creates a separate local CMake build. Never uploads game binaries or generated C++.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib
import re

PROJECT = Path(__file__).resolve().parents[1]
UPSTREAM = Path.home() / "Desktop" / "PS2Recomp"
EXPERIMENT = PROJECT / "output" / "private" / "v03-range-experiment"
GAME = EXPERIMENT / "generated"
PRIVATE = PROJECT / "output" / "private" / "v03-full-build"
WRAPPER = PRIVATE / "wrapper"
BUILD = PRIVATE / "build"
LOGS = PRIVATE / "logs"

def execute(command, filename):
    LOGS.mkdir(parents=True, exist_ok=True)
    log = LOGS / filename
    print("\nCOMANDO:", subprocess.list2cmdline(command), flush=True)
    print("LOG:", log, flush=True)
    count = 0
    with log.open("w", encoding="utf-8", errors="replace") as saved:
        try:
            process = subprocess.Popen(command, cwd=PRIVATE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True,
                                       errors="replace", bufsize=1)
            for line in process.stdout:
                saved.write(line)
                count += 1
                if re.search(r"fatal error|error C\d+|error LNK\d+|CMake Error|error MSB\d+|Build FAILED|Configuring done|Generating done", line, re.I):
                    print(line.rstrip()[:550], flush=True)
                elif count % 500 == 0:
                    print("Procesadas", count, "lineas del log", flush=True)
            code = process.wait()
        except OSError as exc:
            print("Fallo al iniciar:", exc)
            return False
    print("CODIGO_DE_SALIDA:", code, flush=True)
    if code:
        print("=== ULTIMAS 35 LINEAS ===")
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines()[-35:]:
            print(line[:550])
        print("Enviame solo los errores de este log, no los archivos del juego.")
    return code == 0

def main():
    print("=== BUDOKAI3RECOMP - COMPILACION COMPLETA EXPERIMENTAL ===", flush=True)
    if sys.platform != "win32":
        print("ERROR: Ejecutar en Windows.")
        return 2
    if not shutil.which("cmake") or not shutil.which("cl.exe"):
        print("ERROR: usa x64 Native Tools Command Prompt.")
        return 2
    if not (UPSTREAM / "CMakeLists.txt").is_file():
        print("ERROR: PS2Recomp no existe en", UPSTREAM)
        return 2
    if not (UPSTREAM / "ps2xRuntime" / "CMakeLists.txt").is_file():
        print("ERROR: falta ps2xRuntime.")
        return 2
    if not (GAME / "register_functions.cpp").is_file():
        print("ERROR: falta registro de funciones del juego.")
        return 2
    for header in ("ps2_recompiled_functions.h", "ps2_recompiled_stubs.h"):
        if not (GAME / header).is_file():
            print("ERROR: falta", header)
            return 2
    count = sum(1 for _ in GAME.glob("*.cpp"))
    if count != 45171:
        print("ERROR: se esperaban 45171 C++, hay", count)
        return 2
    try:
        config = tomllib.loads((EXPERIMENT / "budokai3-functions-experiment.toml").read_text(encoding="utf-8-sig"))
        elf = Path(config["general"]["input"])
    except (OSError, KeyError, ValueError, tomllib.TOMLDecodeError) as exc:
        print("ERROR: TOML", exc)
        return 2
    if not elf.is_file():
        print("ERROR: ELF no encontrado", elf)
        return 2

    WRAPPER.mkdir(parents=True, exist_ok=True)
    cmake = r'''cmake_minimum_required(VERSION 3.21)
project(Budokai3RecompFullAttempt LANGUAGES C CXX)
set(PS2X_BUILD_RECOMP OFF CACHE BOOL "" FORCE)
set(PS2X_BUILD_RUNTIME ON CACHE BOOL "" FORCE)
set(PS2X_BUILD_ANALYZER OFF CACHE BOOL "" FORCE)
set(PS2X_BUILD_TEST OFF CACHE BOOL "" FORCE)
set(PS2X_BUILD_STUDIO OFF CACHE BOOL "" FORCE)
set(PS2X_ENABLE_DEBUG_UI OFF CACHE BOOL "" FORCE)
set(PS2X_ENABLE_FFMPEG OFF CACHE BOOL "" FORCE)
set(PS2X_ENABLE_RUNNER_UNITY_BUILD ON CACHE BOOL "" FORCE)
set(PS2X_RUNNER_UNITY_BUILD_BATCH_SIZE 16 CACHE STRING "" FORCE)
set(PS2X_ENABLE_RUNNER_PCH ON CACHE BOOL "" FORCE)
set(PS2X_ENABLE_AGRESSIVE_LOGS OFF CACHE BOOL "" FORCE)
set(PS2X_ENABLE_RUNTIME_LOGS ON CACHE BOOL "" FORCE)
set(PS2X_SHOW_WINDOWS_CONSOLE ON CACHE BOOL "" FORCE)

set(UPSTREAM "@UPSTREAM@")
set(GENERATED "@GENERATED@")
add_subdirectory("@UPSTREAM@" "@{CMAKE_BINARY_DIR}/upstream")
if(NOT TARGET ps2EntryRunner)
  message(FATAL_ERROR "No esta el target ps2EntryRunner")
endif()
get_target_property(_sources ps2EntryRunner SOURCES)
set(_filtered)
set(_removed 0)
foreach(_src IN LISTS _sources)
  get_filename_component(_filename "@{_src}" NAME)
  if(_filename STREQUAL "register_functions.cpp")
    math(EXPR _removed "@{_removed}+1")
  else()
    list(APPEND _filtered "@{_src}")
  endif()
endforeach()
if(NOT _removed EQUAL 1)
  message(FATAL_ERROR "Registro de ejemplo inesperado: @{_removed}")
endif()
set_property(TARGET ps2EntryRunner PROPERTY SOURCES "@{_filtered}")
file(GLOB _game_cpp CONFIGURE_DEPENDS "@{GENERATED}/*.cpp")
list(LENGTH _game_cpp _n)
if(NOT _n EQUAL 45171)
  message(FATAL_ERROR "C++ del juego: @{_n} / 45171")
endif()
target_sources(ps2EntryRunner PRIVATE @{_game_cpp})
target_include_directories(ps2EntryRunner BEFORE PRIVATE "@{GENERATED}")
if(MSVC)
  target_compile_options(ps2EntryRunner PRIVATE /bigobj)
  target_link_options(ps2EntryRunner PRIVATE /INCREMENTAL:NO)
endif()
message(STATUS "Integrados @{_n} C++ del juego en ps2EntryRunner")
'''
    cmake = cmake.replace("@{", "$" + "{")
    cmake = cmake.replace("@UPSTREAM@", UPSTREAM.resolve().as_posix())
    cmake = cmake.replace("@GENERATED@", GAME.resolve().as_posix())
    (WRAPPER / "CMakeLists.txt").write_text(cmake, encoding="utf-8")
    PRIVATE.mkdir(parents=True, exist_ok=True)
    print("Integrando", count, "C++ (SIN moverlos ni borrar archivos).", flush=True)
    if not execute(["cmake", "-S", str(WRAPPER), "-B", str(BUILD),
                    "-G", "Visual Studio 18 2026", "-A", "x64"], "configure.log"):
        return 1
    if not execute(["cmake", "--build", str(BUILD), "--config", "Release",
                    "--target", "ps2EntryRunner", "--parallel", "4"], "build.log"):
        return 1
    exes = list(BUILD.rglob("ps2EntryRunner.exe"))
    if not exes:
        print("ERROR: compilacion termino sin encontrar ps2EntryRunner.exe")
        return 1
    exe = next((e for e in exes if "Release" in e.parts), exes[0])
    launch = PRIVATE / "LANZAR_BUDOKAI3_EXPERIMENTAL.cmd"
    launch.write_text(
        '@echo off\n'
        'echo PRUEBA EXPERIMENTAL, SIN GARANTIA DE JUEGO FUNCIONAL.\n'
        f'"{exe}" "{elf}"\n'
        'echo CODIGO_DE_SALIDA=%ERRORLEVEL%\n'
        'pause\n', encoding="utf-8")
    print("\nEXE:", exe)
    print("LANZADOR:", launch)
    print("El runtime es experimental; puede fallar al arrancar el juego.")
    print("NO subas ISO, ELF, CSV, TOML ni C++/OBJ derivados del juego.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
