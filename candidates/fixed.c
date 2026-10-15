#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
static int number(const char *s, unsigned long *v) {
    char *end;
    if (!s[0] || s[0] == '-' || s[0] == '+') return 0;
    errno = 0; *v = strtoul(s, &end, 10);
    return !errno && !*end;
}
int main(int argc, char **argv) {
    unsigned long declared, opcode, value;
    if (argc < 3 || !number(argv[1], &declared) || !number(argv[2], &opcode)) {
        puts("REJECT"); return 0;
    }
    if (declared > 32 || declared != (unsigned long)(argc - 3) || opcode > 3) {
        puts("REJECT"); return 0;
    }
    for (int i = 3; i < argc; i++) {
        if (!number(argv[i], &value) || value > 255) { puts("REJECT"); return 0; }
    }
    printf("OK:%lu\n", declared);
    return 0;
}
