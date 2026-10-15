"""Three synthetic predicates. These are NOT real spacecraft vulnerabilities."""
import random

TASKS = {
 'length': {
  'description': 'a is declared payload length, b is actual payload length, c is opcode. Return 1 iff a equals b, a <= 32, and c <= 3; otherwise return 0.',
  'vulnerable': 'int repair(uint32_t a, uint32_t b, uint32_t c) { (void)b; (void)c; return a <= 32; }',
  'reference': 'int repair(uint32_t a, uint32_t b, uint32_t c) { return a == b && a <= 32 && c <= 3; }',
  'dev': [(1,1,0),(2,1,0),(33,33,0)],
  'accept': [(0,0,2),(3,3,3),(32,32,0),(1,1,9),(0,1,0),(31,30,0)],
 },
 'arithmetic': {
  'description': 'a and b are unsigned 32-bit segment lengths, c is an unsigned 32-bit capacity. Return 1 iff the mathematical sum a+b <= c. Unsigned wraparound must never allow an oversized sum. Otherwise return 0.',
  'vulnerable': 'int repair(uint32_t a, uint32_t b, uint32_t c) { return a + b <= c; }',
  'reference': 'int repair(uint32_t a, uint32_t b, uint32_t c) { return (uint64_t)a + b <= c; }',
  'dev': [(1,2,3),(3,4,6),(4294967295,1,0)],
  'accept': [(0,0,0),(4294967295,0,4294967295),(2147483648,2147483648,0),(9,1,10),(1,1,1)],
 },
 'authorization': {
  'description': 'a is a granted permission bitmask, b is a required permission bitmask, c is an authorization flag. Return 1 iff b != 0, every bit in b is present in a, and c equals 1. Otherwise return 0.',
  'vulnerable': 'int repair(uint32_t a, uint32_t b, uint32_t c) { (void)c; return (a & b) != 0; }',
  'reference': 'int repair(uint32_t a, uint32_t b, uint32_t c) { return b != 0 && (a & b) == b && c == 1; }',
  'dev': [(3,3,1),(1,3,1),(0,1,1)],
  'accept': [(7,3,1),(3,3,0),(7,0,1),(15,5,1),(1,1,2),(0,0,0)],
 },
}

def oracle(name, args):
    a,b,c = args
    if name == 'length': return int(a == b and a <= 32 and c <= 3)
    if name == 'arithmetic': return int(a+b <= c)
    return int(b != 0 and (a & b) == b and c == 1)

def evaluation(name):
    r=random.Random(20261016)
    if name == 'length':
        cases=[(a,b,c) for a in [0,1,31,32,33,4294967295] for b in [0,1,31,32,33] for c in [0,3,4,4294967295]]
    elif name == 'arithmetic':
        edges=[0,1,2,2147483647,2147483648,4294967294,4294967295]
        cases=[(a,b,c) for a in edges for b in edges for c in edges]
        cases += [tuple(r.randrange(2**32) for _ in range(3)) for _ in range(60)]
    else:
        cases=[(a,b,c) for a in range(8) for b in range(8) for c in [0,1,2]]
        cases += [(4294967295,2147483648,1),(2147483648,2147483649,1)]
    excluded=set(TASKS[name]['dev']+TASKS[name]['accept'])
    return sorted(set(cases)-excluded)

HARNESS = '''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <limits.h>
%s
int main(int argc,char **argv) {
 if (argc != 4) return 2;
 uint32_t x[3];
 for(int i=0;i<3;i++) {
  char *end; errno=0;
  unsigned long long v=strtoull(argv[i+1],&end,10);
  if(errno || *end || v>UINT32_MAX || argv[i+1][0]=='-') return 2;
  x[i]=(uint32_t)v;
 }
 printf("%%d\\n",repair(x[0],x[1],x[2]));
 return 0;
}
'''
