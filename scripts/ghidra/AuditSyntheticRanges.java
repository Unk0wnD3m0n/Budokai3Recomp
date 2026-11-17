// AuditSyntheticRanges.java
// @category PS2Recomp
// @description Read-only audit of three experimentally shortened synthetic-entry ranges.
// Ghidra Java script: no Jython/PyGhidra runtime required.
// Prints detailed results to Window -> Console and shows a visible popup summary.
// Does not modify program, files, ISO, ELF, CSV or generated C++.
//
// This audit reports ONLY instructions/data already recognized by Ghidra.
// A zero count outside the eight-byte probe does NOT prove that no executable code exists.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;

public class AuditSyntheticRanges extends GhidraScript {

    private static final String[] NAMES = {
        "entry_00403fc0",
        "entry_004217d0",
        "entry_0042c020"
    };
    // {start, original_end_exclusive, experimental_end_exclusive}
    private static final long[][] RANGES = {
        {0x00403fc0L, 0x00421720L, 0x00403fc8L},
        {0x004217d0L, 0x0042c020L, 0x004217d8L},
        {0x0042c020L, 0x0042d000L, 0x0042c028L}
    };

    private String hex(Address address) {
        return String.format("0x%08X", address.getOffset());
    }

    @Override
    protected void run() throws Exception {
        if (currentProgram == null) {
            popup("Abre SLES_533.46.elf en CodeBrowser antes de ejecutar el script.");
            return;
        }

        Listing listing = currentProgram.getListing();
        println("=== Budokai3Recomp V0.3 — auditoria Ghidra (SOLO LECTURA) ===");
        println("Programa: " + currentProgram.getName());
        StringBuilder summary = new StringBuilder();
        summary.append("AUDITORIA FINALIZADA\n\n");
        int totalOutside = 0;

        for (int i = 0; i < RANGES.length; i++) {
            if (monitor.isCancelled()) {
                println("Auditoria cancelada.");
                return;
            }
            long start = RANGES[i][0];
            long originalEnd = RANGES[i][1];
            long experimentEnd = RANGES[i][2];

            AddressSet head = new AddressSet(toAddr(start), toAddr(experimentEnd - 1));
            AddressSet remainder = new AddressSet(toAddr(experimentEnd), toAddr(originalEnd - 1));

            int insideInstructions = 0;
            InstructionIterator headIterator = listing.getInstructions(head, true);
            while (headIterator.hasNext()) {
                if (monitor.isCancelled()) return;
                headIterator.next();
                insideInstructions++;
            }

            int outsideInstructions = 0;
            StringBuilder examples = new StringBuilder();
            InstructionIterator instructionIterator = listing.getInstructions(remainder, true);
            while (instructionIterator.hasNext()) {
                if (monitor.isCancelled()) return;
                Instruction instruction = instructionIterator.next();
                outsideInstructions++;
                if (outsideInstructions <= 8) {
                    if (examples.length() > 0) examples.append(", ");
                    examples.append(hex(instruction.getMinAddress()));
                }
            }

            int definedData = 0;
            DataIterator dataIterator = listing.getDefinedData(remainder, true);
            while (dataIterator.hasNext()) {
                if (monitor.isCancelled()) return;
                Data data = dataIterator.next();
                definedData++;
            }

            int functionStarts = 0;
            FunctionIterator functionIterator = listing.getFunctions(remainder, true);
            while (functionIterator.hasNext()) {
                if (monitor.isCancelled()) return;
                Function function = functionIterator.next();
                functionStarts++;
            }

            totalOutside += outsideInstructions;
            String rangeSummary = NAMES[i]
                + "\n  Instrucciones primeros 8 bytes: " + insideInstructions
                + "\n  Instrucciones posteriores: " + outsideInstructions
                + "\n  Datos definidos posteriores: " + definedData
                + "\n  Inicios de otras funciones posteriores: " + functionStarts;
            println("\n" + rangeSummary);
            println("  Primeras direcciones de instrucciones posteriores: "
                + (examples.length() > 0 ? examples.toString() : "(ninguna reconocida)"));
            summary.append(rangeSummary).append("\n\n");
        }

        summary.append("TOTAL instrucciones posteriores: ").append(totalOutside);
        summary.append("\n\nLos ceros NO prueban que no haya codigo sin desensamblar.");
        summary.append("\nMas detalles: Window > Console.");

        println("\nTOTAL instrucciones reconocidas posteriores a los 8 bytes: " + totalOutside);
        println("No modifica el programa ni los archivos. No publicar datos del juego.");
        popup(summary.toString());
    }
}
