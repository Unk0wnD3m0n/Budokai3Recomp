#!/usr/bin/env python3
"""Informe local, de solo lectura, de Budokai3Recomp/OpenCode.

Lee metadatos de archivos, git status (sin diffs de contenido) y extractos
acotados de logs. No ejecuta el juego, no compila, no cambia codigo, no sube
ningun archivo. El reporte se guarda solo en output/private/.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
import os
import re
import subprocess
import sys

BASE = Path.home() / "Desktop" / "Budokai3Recomp-main"
PS2 = Path.home() / "Desktop" / "PS2Recomp"
PRIVATE = BASE / "output" / "private"
FULL = PRIVATE / "v03-full-build"
LOGS = FULL / "logs"
EXE = FULL / "build" / "upstream" / "ps2xRuntime" / "Release" / "ps2EntryRunner.exe"
REPORT = PRIVATE / "reporte_estado_opencode.txt"
IMPORTANT = (
    "ps2xRuntime/src/lib/Kernel/Stubs/SIF.cpp",
    "ps2xRuntime/src/lib/Kernel/Stubs/SIF.h",
    "ps2xRuntime/src/lib/Kernel/Syscalls/Deci2.cpp",
    "ps2xRuntime/src/lib/Kernel/Syscalls/RPC.cpp",
    "ps2xRuntime/src/lib/ps2_runtime.cpp",
    "ps2xRuntime/src/lib/ps2_iop_host.cpp",
    "ps2xIOP/src/emulator/services/iop_rpc.cpp",
    "ps2xIOP/src/emulator/services/iop_rpc.h",
    "ps2xIOP/src/emulator/iop_emulator.cpp",
)
TAGS = re.compile(
    r"\[run:tick\]|\[(?:sceSif|iop:|ps2xIOP|Deci2Call|rpc|cdvd|sif|dma|gs|gif|vif)"
    r"|Starting execution|ELF file loaded|error|fatal|failed|warning|CODIGO_DE_SALIDA"
    r"|Build succeeded|Build FAILED|succeeded|no fotograma",
    re.IGNORECASE,
)
PC = re.compile(r"\[run:tick\].*?\bpc=(0x[0-9a-fA-F]+)")
SKIP_DIRS = {
    ".git", ".vs", ".idea", "__pycache__", "node_modules", "out", "build",
    "bin", "obj", "generated", "Release", "Debug", "CMakeFiles", ".cache",
}


def stamp(path: Path) -> str:
    try:
        s = path.stat()
        return f"{datetime.fromtimestamp(s.st_mtime):%Y-%m-%d %H:%M:%S} | {s.st_size:,} bytes"
    except OSError:
        return "no existe"


def command(args: list[str], *, timeout: int = 10) -> list[str]:
    try:
        p = subprocess.run(args, capture_output=True, text=True,
                           errors="replace", timeout=timeout)
        if p.returncode:
            return [f"Error de comando (codigo {p.returncode}); no se modifico nada."]
        return (p.stdout or "(sin cambios)").splitlines()
    except (OSError, subprocess.TimeoutExpired):
        return ["No disponible."]


def log_tail(path: Path, bytes_limit: int = 1_500_000) -> list[str]:
    try:
        with path.open("rb") as file:
            file.seek(0, 2)
            size = file.tell()
            file.seek(max(0, size - bytes_limit))
            data = file.read(bytes_limit)
        # Omit the possibly cut first line for a truncated file.
        if size > bytes_limit:
            pos = data.find(b"\n")
            data = data[pos + 1:] if pos >= 0 else b""
        return data.decode("utf-8", errors="replace").splitlines()
    except OSError:
        return []


def safe(line: str) -> str:
    # Keep technical log lines and guest PCs, but avoid copying huge blobs.
    line = line.replace(str(Path.home()), "%USERPROFILE%")
    return line.strip()[:420]


def recent_sources(root: Path, subdirs: tuple[str, ...], limit: int = 28) -> list[tuple[float, str, str]]:
    found: list[tuple[float, str, str]] = []
    for subdir in subdirs:
        folder = root / subdir
        if not folder.is_dir():
            continue
        for d, dirs, files in os.walk(folder):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for name in files:
                if not name.endswith((".cpp", ".h", ".hpp", ".c", ".py", ".cmake", ".txt")):
                    continue
                path = Path(d) / name
                try:
                    s = path.stat()
                    found.append((s.st_mtime, str(path.relative_to(root)), f"{s.st_size:,} bytes"))
                except OSError:
                    pass
    return sorted(found, reverse=True)[:limit]


def build_report() -> list[str]:
    out = [
        "BUDAKAI3RECOMP - ESTADO LOCAL DE OPENCODE",
        f"Generado: {datetime.now():%Y-%m-%d %H:%M:%S}",
        "Solo lectura de codigo/logs; no se ejecuto ni compilo el juego.",
        "NOTA: sube solo este TXT; nunca subas ISO, ELF, CPP generados ni objetos.",
        "",
        "== RUTAS Y EXE ==",
        f"Proyecto encontrado: {BASE.is_dir()}",
        f"PS2Recomp encontrado: {PS2.is_dir()}",
        f"EXE: {stamp(EXE)}",
        f"Wrapper CMake: {stamp(FULL / 'wrapper' / 'CMakeLists.txt')}",
        "",
        "== FUENTES CRITICAS Y ULTIMA MODIFICACION ==",
    ]
    for name in IMPORTANT:
        out.append(f"{name} :: {stamp(PS2 / name)}")

    out.extend(["", "== ESTADO GIT (SOLO NOMBRES, SIN CODIGO) =="])
    for label, folder in (("Budokai3Recomp", BASE), ("PS2Recomp", PS2)):
        out.append(f"[{label}]")
        out.extend(command(["git", "-C", str(folder), "status", "--short",
                            "--untracked-files=no"])[:85])
        out.append("git diff --stat:")
        out.extend(command(["git", "-C", str(folder), "diff", "--stat"])[:65])

    out.extend(["", "== FUENTES MODIFICADAS RECIENTEMENTE =="])
    for label, folder, dirs in (
        ("PS2Recomp", PS2, ("ps2xRuntime/src", "ps2xIOP/src")),
        ("Budokai3Recomp scripts", BASE, ("scripts",)),
        ("Wrapper privado", FULL, ("wrapper",)),
    ):
        out.append(f"[{label}]")
        found = recent_sources(folder, dirs)
        for ts, rel, size in found:
            out.append(f"{datetime.fromtimestamp(ts):%Y-%m-%d %H:%M:%S} | {size} | {rel}")
        if not found:
            out.append("(sin fuentes encontradas)")

    out.extend(["", "== LOGS RECIENTES: TAMAÑOS Y FECHAS =="])
    try:
        all_logs = sorted((p for p in LOGS.glob("*.log") if p.is_file()),
                          key=lambda p: p.stat().st_mtime, reverse=True)
    except OSError:
        all_logs = []
    for path in all_logs[:24]:
        out.append(f"{path.name} :: {stamp(path)}")
    if not all_logs:
        out.append("No hay .log en el directorio esperado.")

    out.extend(["", "== ANALISIS DE LOS ULTIMOS 8 LOGS =="])
    for path in all_logs[:8]:
        lines = log_tail(path)
        hits = [safe(s) for s in lines if TAGS.search(s)]
        pcs = [m.group(1) for s in lines if (m := PC.search(s))]
        out.append(f"--- {path.name} ---")
        out.append(f"Lineas leidas (cola maxima 1.5 MB): {len(lines)}")
        out.append(f"Lineas con eventos: {len(hits)}")
        out.append(f"Heartbeats: {len(pcs)}")
        if pcs:
            out.append(f"PC primer/ultimo heartbeat: {pcs[0]} / {pcs[-1]}")
            out.append("PC mas frecuentes: " +
                       ", ".join(f"{pc}={n}" for pc, n in Counter(pcs).most_common(6)))
        out.extend(hits[-24:] if hits else ["(sin eventos reconocibles)"])
        if len(hits) == 0 and lines:
            out.extend(["Ultimas 6 lineas:", *[safe(x) for x in lines[-6:]]])

    out.extend(["", "== BACKUPS (SOLO METADATOS) =="])
    backup_roots = [PRIVATE / "backups", FULL / "backups", PS2 / "backups"]
    for root in backup_roots:
        if root.is_dir():
            all_files = [p for p in root.rglob("*") if p.is_file()]
            out.append(f"{root.name} ({root.parent.name}): {len(all_files)} archivos")
            for p in sorted(all_files, key=lambda q: q.stat().st_mtime, reverse=True)[:8]:
                out.append(f"  {p.name}: {stamp(p)}")
    if not any(x.is_dir() for x in backup_roots):
        out.append("No se encontraron backups en las tres rutas comunes.")

    out.extend(["", "FIN DEL REPORTE",
                "Este reporte no incluye datos binarios del juego ni el contenido de los CPP.",
                "Si contiene rutas personales, puedes ocultarlas antes de compartirlo."])
    return out


def main() -> int:
    if not BASE.is_dir():
        print("No encontre Budokai3Recomp-main en el Escritorio.")
        return 2
    PRIVATE.mkdir(parents=True, exist_ok=True)
    lines = build_report()
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Reporte guardado en:")
    print(REPORT)
    print(f"Lineas: {len(lines)}")
    print("Adjunta este unico archivo TXT al chat para revisar el ultimo avance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
