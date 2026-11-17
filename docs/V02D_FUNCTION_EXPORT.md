# V0.2d — Exportar el mapa de funciones desde Ghidra (solo local)

**Estado previo confirmado:** Ghidra 12.2 ha completado Auto Analyze para `SLES_533.46.elf` con Emotion Engine R5900 LE32. Reconoció 544078 instrucciones y 7328 funciones candidatas.

## Usaremos el script oficial de PS2Recomp

[ExportPS2Functions.java — ran-j/PS2Recomp](https://github.com/ran-j/PS2Recomp/blob/main/ps2xRecomp/tools/ghidra/ExportPS2Functions.java)

Documentación: [Ghidra integration PS2Recomp](https://github.com/ran-j/PS2Recomp/blob/main/ps2xAnalyzer/Readme.md).

1. Descarga el script de la fuente oficial mediante **Raw → Save As** en una carpeta independiente de los archivos del juego; conserva el nombre `ExportPS2Functions.java`. No ejecutes scripts obtenidos de terceros.
2. En Ghidra, guarda el análisis; ve a **Window → Script Manager**. Agrega la carpeta que contiene el script mediante la gestión de directorios de scripts y actualiza la lista.
3. Busca `ExportPS2Functions` en la categoría `PS2Recomp` y ejecútalo con el programa `SLES_533.46.elf` abierto.
4. El script pide **dos destinos**: primero un archivo TOML, luego un CSV. Guarda ambos **solo localmente**, por ejemplo dentro de `output/private/`.
5. Confirma en la consola de Ghidra que se exportaron funciones, etiquetas ejecutables, TOML y CSV. **No lances PS2Recomp todavía**: antes conviene revisar el CSV y los parámetros generados.

## Qué genera realmente el script

- CSV: `Name,Start,End,Size`; puede incluir nombres automáticos y objetivos sintéticos adicionales.
- TOML: información del ELF, `ghidra_output` apuntando al CSV, salida C++, listas de stubs y otros parámetros.
- La cantidad de registros del CSV puede **superar** los 7328 del gestor de funciones por etiquetas adicionales.
- Las direcciones, límites y clasificación de funciones requieren revisión antes de recompilar.

## Qué NO publicaremos

No publicar ELF, ISO, bytes del juego ni código derivado. Los reportes TOML/CSV pueden contener nombres o estructuras derivadas del juego y rutas locales; se guardan en `output/private`, que está ignorado por git. Comparte solo el número final de registros y mensajes de error, nunca rutas personales o archivos del juego.

## Siguiente prueba

Confirmar si el exportador oficial compila con Ghidra 12.2 y nuestra extensión R5900. Si da errores, no alterar los datos del juego: registrar el error de Java/Ghidra y preparar una corrección compatible respetando la licencia de PS2Recomp.
