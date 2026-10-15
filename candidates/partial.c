#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    if (argc < 3) { puts("REJECT"); return 0; }
    unsigned long declared = strtoul(argv[1], NULL, 10);
    unsigned actual = (unsigned)(argc - 3);
    if (declared != actual || declared > 32) { puts("REJECT"); return 0; }
    printf("OK:%u\n", actual);
    return 0;
}
