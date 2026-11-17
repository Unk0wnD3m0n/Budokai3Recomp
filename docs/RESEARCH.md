# Fuentes de investigación

| Proyecto | Qué aprendemos | Limitación |
|---|---|---|
| [PS2Recomp](https://github.com/ran-j/PS2Recomp) | Análisis ELF, recompilación C++, runtime experimental | GPL-3.0; no integrado todavía |
| [Tenkaichi3Decomp](https://github.com/z3xox/Tenkaichi3Decomp) | Diseño de render, entrada y ejecución nativa | AGPL-3.0; es OTRO juego |
| [Budokai 3 GH ELF](https://github.com/TotallyNotMichael/dbz3-gh-ntsc-elf-decomp) | Investigación específica de Budokai 3 | El build NTSC Greatest Hits es distinto a SLES-53346 |

## Decisiones V0.1

- Analizador ISO9660 original, únicamente de lectura.
- No conectar a servicios ni enviar datos del usuario.
- Detectar SYSTEM.CNF, BOOT2 y ELF MIPS; registrar SHA-256 del ELF.
- No asumir compatibilidad por región o nombre coincidente.
- No integrar software de terceros antes de revisar licencias.
