#include <stdio.h>
#include <stdlib.h>
/* Synthetic telemetry parser: [declared payload size, opcode, payload...].
   This fixture has logical input-validation defects, no intentional unsafe reads. */
int main(int argc, char **argv) {
    if (argc < 3) { puts("REJECT"); return 0; }
    unsigned declared = (unsigned)strtoul(argv[1], NULL, 10);
    unsigned opcode = (unsigned)strtoul(argv[2], NULL, 10);
    unsigned actual = (unsigned)(argc - 3);
    (void)declared; (void)opcode;
    printf("OK:%u\n", actual);
    return 0;
}
