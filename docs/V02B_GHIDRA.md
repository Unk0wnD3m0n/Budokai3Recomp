# V0.2b — Preparar el ELF para estudiar funciones

**NO subir este archivo a GitHub.** La herramienta extrae datos comerciales solo a una carpeta local y jamás transmite nada por la red.

## Requisitos

- Python 3.10+, ISO propia Collector's Edition Europa `SLES-53346`.
- Actualizar la copia local del repositorio con el ZIP de GitHub (no eliminar la carpeta antigua que contiene la ISO).
- Ejecución sin administrador.

## Paso 1: pruebas sintéticas

```powershell
python -m unittest discover -s tests -v
```

El total esperado con V0.2b es **13** pruebas.

## Paso 2: exportar SOLO en el PC del propietario

Desde PowerShell dentro del proyecto descargado:

```powershell
python .\scripts\export_local_elf.py "C:\Users\Juan\Desktop\Budokai3Recomp-main 1\DragonBall Z - Budokai 3 - Collector's Edition (Europe) (En,Ja,Fr,De,Es,It).iso" --output-dir output\private
```

Si el nombre o ubicación no coincide, sustituye la ruta. La herramienta comprueba que el BOOT2 sea `SLES_533.46`, que el ELF tenga cabecera MIPS LE32 y **se niega a sobrescribir** el archivo extraído.

Resultado esperado: archivo local `output/private/SLES_533.46.elf`, y hash SHA-256 coincidente con el reportado en V0.1. Git ignora `output/` y `*.elf`.

## Paso 3 (posterior): Ghidra y mapa de funciones

1. Instalar Ghidra **solo desde su repositorio/página oficial**.
2. Importar localmente `SLES_533.46.elf` en un proyecto privado.
3. Confirmar arquitectura MIPS R5900, endianness y punto de entrada; evaluar procesador PS2 especializado si hace falta.
4. Revisar el [flujo de Ghidra de PS2Recomp](https://github.com/ran-j/PS2Recomp/blob/main/ps2xAnalyzer/Readme.md) y sus exportadores.
5. Documentar **metadatos** sobre funciones (cantidades, direcciones, llamadas desconocidas), sin subir el binario, ni desensamblados extensos o código original.

**Advertencia:** exportar y analizar el ELF no significa tener ya un ejecutable Windows; el runtime de PS2 sigue siendo trabajo pendiente.
