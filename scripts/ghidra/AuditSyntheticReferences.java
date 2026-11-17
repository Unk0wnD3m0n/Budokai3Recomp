// AuditSyntheticReferences.java
// @category PS2Recomp
// @description Read-only Ghidra XREF audit of excluded tails in the V0.3 A/B test.
// No database modification. No binary, code or reference data exported to files.
// A reference to data is normal and NOT by itself evidence of missing executable code.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;

public class AuditSyntheticReferences extends GhidraScript {

    private static final String[] NAMES = {
        "entry_00403fc0",
        "entry_004217d0",
        "entry_0042c020"
    };
    // {experimental_end_exclusive, original_end_exclusive}
    private static final long[][] EXCLUDED = {
        {0x00403fc8L, 0x00421720L},
        {0x004217d8L, 0x0042c020L},
        {0x0042c028L, 0x0042d000L}
    };

    private String hex(Address address) {
        return String.format("0x%08X", address.getOffset());
    }

    @Override
    protected void run() throws Exception {
        if (currentProgram == null) {
            popup("Abre SLES_533.46.elf antes de ejecutar este script.");
            return;
        }
        ReferenceManager manager = currentProgram.getReferenceManager();
        StringBuilder summary = new StringBuilder("AUDITORIA DE REFERENCIAS\n");
        summary.append("Datos = referencias normales; flujo = requieren investigar.\n\n");

        int allFlow = 0;
        int allData = 0;
        println("=== BUDOKAI3RECOMP V0.3 - XREF A REGIONES EXCLUIDAS ===");
        println("Programa: " + currentProgram.getName());

        for (int i = 0; i < EXCLUDED.length; i++) {
            if (monitor.isCancelled()) return;
            long start = EXCLUDED[i][0];
            long end = EXCLUDED[i][1];
            AddressSet excludedSet = new AddressSet(toAddr(start), toAddr(end - 1));
            AddressIterator destinations = manager.getReferenceDestinationIterator(excludedSet, true);

            int addressesWithReferences = 0;
            int flowRefs = 0;
            int dataRefs = 0;
            int otherRefs = 0;
            StringBuilder examples = new StringBuilder();

            while (destinations.hasNext()) {
                if (monitor.isCancelled()) return;
                Address target = destinations.next();
                addressesWithReferences++;
                ReferenceIterator incoming = manager.getReferencesTo(target);
                while (incoming.hasNext()) {
                    if (monitor.isCancelled()) return;
                    Reference reference = incoming.next();
                    if (reference.getReferenceType().isFlow()) {
                        flowRefs++;
                        if (flowRefs <= 10) {
                            if (examples.length() > 0) examples.append(", ");
                            examples.append(hex(reference.getFromAddress()));
                            examples.append("->");
                            examples.append(hex(target));
                        }
                    } else if (reference.getReferenceType().isData()) {
                        dataRefs++;
                    } else {
                        otherRefs++;
                    }
                }
            }

            allFlow += flowRefs;
            allData += dataRefs;
            String item = NAMES[i] + "\n"
                + "  Direcciones con XREF: " + addressesWithReferences + "\n"
                + "  XREF de FLUJO (branch/call): " + flowRefs + "\n"
                + "  XREF de DATOS: " + dataRefs + "\n"
                + "  Otras XREF: " + otherRefs;
            println("\n" + item);
            println("  Primeras referencias de flujo: "
                + (examples.length() == 0 ? "(ninguna)" : examples.toString()));
            summary.append(item).append("\n\n");
        }

        summary.append("TOTAL XREF DE FLUJO: ").append(allFlow);
        summary.append("\nTOTAL XREF DE DATOS: ").append(allData);
        summary.append("\n\nNota: Ghidra puede no detectar referencias indirectas.");
        summary.append("\nSi hay referencias de flujo, revisar en Console.");
        println("\nTOTAL: FLOW=" + allFlow + ", DATA=" + allData);
        println("Auditoria solo lectura. No publicar el ELF ni el CSV.");
        popup(summary.toString());
    }
}
