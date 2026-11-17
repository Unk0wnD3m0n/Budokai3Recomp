# AuditSyntheticRanges.py
#@category PS2Recomp
# Read-only audit of three synthetic entries shortened for the V0.3 A/B test.
# Run via Ghidra Script Manager on the local SLES_533.46.elf program.
# Does not change the program database, write any files, or export game bytes.
#
# This report CANNOT establish that a shortened range preserves all code:
# Ghidra might not have disassembled every executable instruction.
from ghidra.program.model.address import AddressSet

RANGES = [
    ("entry_00403fc0", 0x00403fc0, 0x00421720, 0x00403fc8),
    ("entry_004217d0", 0x004217d0, 0x0042c020, 0x004217d8),
    ("entry_0042c020", 0x0042c020, 0x0042d000, 0x0042c028),
]

def summarize(iterator, limit, kind="code"):
    count = 0
    examples = []
    while iterator.hasNext():
        if monitor.isCancelled():
            raise Exception("Cancelado por el usuario")
        item = iterator.next()
        count += 1
        if len(examples) < limit:
            address = item.getEntryPoint() if kind == "function" else item.getMinAddress()
            examples.append("0x%08X" % address.getOffset())
    return count, examples

if currentProgram is None:
    print("ERROR: abre SLES_533.46.elf antes de ejecutar la auditoria.")
else:
    listing = currentProgram.getListing()
    print("=== BUDOKAI3RECOMP V0.3 - AUDITORIA DE RANGOS (SOLO LECTURA) ===")
    print("Programa: " + str(currentProgram.getName()))
    print("Numeros: instrucciones y datos YA definidos por Ghidra; no bytes examinados.")
    total_outside = 0
    for name, start, original_end, experiment_end in RANGES:
        print("")
        print(name + "  original=[0x%08X,0x%08X)  experimento=[0x%08X,0x%08X)" %
              (start, original_end, start, experiment_end))
        head = AddressSet(toAddr(start), toAddr(experiment_end - 1))
        tail = AddressSet(toAddr(experiment_end), toAddr(original_end - 1))
        head_instructions, head_samples = summarize(
            listing.getInstructions(head, True), 5)
        omitted_instructions, omitted_samples = summarize(
            listing.getInstructions(tail, True), 8)
        omitted_data, data_samples = summarize(
            listing.getDefinedData(tail, True), 5)
        omitted_functions, fn_samples = summarize(
            listing.getFunctions(tail, True), 5, "function")
        total_outside += omitted_instructions
        print("  Instrucciones dentro de los primeros 8 bytes: %d" % head_instructions)
        print("  Instrucciones definidas DESPUES de 8 bytes: %d" % omitted_instructions)
        print("  Primeras instrucciones posteriores: %s" %
              (", ".join(omitted_samples) if omitted_samples else "(ninguna reconocida)"))
        print("  Datos definidos posteriores: %d" % omitted_data)
        print("  Ejemplos de datos: %s" %
              (", ".join(data_samples) if data_samples else "(ninguno)"))
        print("  Funciones Ghidra cuyo INICIO esta despues de 8 bytes: %d" %
              omitted_functions)
        print("  Primeros inicios de funciones: %s" %
              (", ".join(fn_samples) if fn_samples else "(ninguno)"))
        if omitted_instructions > 0:
            print("  ATENCION: el rango experimental omite instrucciones reconocidas.")
        else:
            print("  SIN INSTRUCCIONES ADICIONALES DEFINIDAS; NO demuestra ausencia de codigo real.")
    print("")
    print("=== RESUMEN ===")
    print("Instrucciones reconocidas por Ghidra fuera de los 3 rangos experimentales: %d" %
          total_outside)
    print("No modificar CSV, ELF ni programa Ghidra basado solo en este informe.")
    print("No subir el ELF, CSV ni codigo generado a GitHub.")
