# V0.2a — Mapa de memoria del ELF (solo lectura)

Nuestra primera prueba V0.1 reconoció `SLES-53346`, MIPS ELF32, punto de entrada `0x00100008`.

## Cómo ejecutar V0.2a

Desde PowerShell abierto en la raíz del proyecto descargado desde GitHub:

```powershell
python .\scripts\inspect_elf_layout.py ".\DragonBall Z - Budokai 3 - Collector's Edition (Europe) (En,Ja,Fr,De,Es,It).iso" --report reporte-v02-local.json
```

Si la ISO está en otra carpeta, sustituir la ruta. **Nunca subir el juego ni el informe sin revisarlo.**

## Qué calcula

- Cabeceras ELF32 de programa y sección.
- Segmentos `PT_LOAD`, tamaño en archivo y RAM, direcciones virtuales y físicas.
- Permisos de memoria `R/W/X` y alineación.
- Comprobación limitada: si el punto de entrada pertenece a un segmento ejecutable.
- SHA-256 del ELF para distinguir builds (no publicar el ELF).
- Informe local JSON de metadatos, no de código.

## Qué NO calcula

- No determina los límites de las funciones ni nombres reales.
- No interpreta el vector unit, DMA, llamadas de hardware ni audio.
- No recompila ni ejecuta instrucciones.
- La validación es sintáctica; requiere corroboración con Ghidra.

## Criterio de avance

1. `python -m unittest discover -s tests -v` pasa sin usar datos comerciales.
2. El script se ejecuta con la ISO propia y arroja información coherente con V0.1.
3. El usuario comparte **solo** el resumen de la terminal; no se suben archivos comerciales.

**Siguiente V0.2b:** evaluar Ghidra y el exportador de funciones de [PS2Recomp](https://github.com/ran-j/PS2Recomp), comprobando licencias y limitaciones.
