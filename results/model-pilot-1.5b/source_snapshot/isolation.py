"""Linux seccomp helpers. Fail closed if filtering cannot be installed.

The C execution profile is for statically linked, stdin/stdout-only programs.
The compiler is trusted and is NOT filesystem isolated by this module.
"""
import ctypes
import errno
import os
import resource
import signal
import subprocess
import tempfile
import time
from pathlib import Path

_LIB = None

def _lib():
    global _LIB
    if _LIB is None:
        s = ctypes.CDLL('libseccomp.so.2', use_errno=True)
        s.seccomp_init.argtypes = [ctypes.c_uint32]
        s.seccomp_init.restype = ctypes.c_void_p
        s.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
        s.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
        s.seccomp_syscall_resolve_name.restype = ctypes.c_int
        s.seccomp_load.argtypes = [ctypes.c_void_p]
        s.seccomp_release.argtypes = [ctypes.c_void_p]
        _LIB = s
    return _LIB

def _filter(names, allowlist=False):
    s = _lib()
    allowed, denied = 0x7fff0000, 0x50000 | errno.EPERM
    ctx = s.seccomp_init(denied if allowlist else allowed)
    if not ctx:
        raise RuntimeError('seccomp_init failed')
    try:
        for name in names:
            number = s.seccomp_syscall_resolve_name(name.encode())
            if number >= 0 and s.seccomp_rule_add(ctx, allowed if allowlist else denied, number, 0) != 0:
                raise RuntimeError('seccomp rule failed: ' + name)
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.prctl(38, 1, 0, 0, 0) != 0 or s.seccomp_load(ctx) != 0:
            raise RuntimeError('seccomp install failed')
    finally:
        s.seccomp_release(ctx)

def block_network():
    # Denies new network endpoints and connection/data syscalls; close_fds and a
    # sanitized launch environment are also needed when launching a subprocess.
    _filter(['socket', 'socketpair', 'connect', 'accept', 'accept4', 'bind',
             'listen', 'sendto', 'sendmsg', 'sendmmsg', 'recvfrom', 'recvmsg',
             'recvmmsg', 'io_uring_setup'])

def static_profile(memory_mb=128, cpu_seconds=1):
    resource.setrlimit(resource.RLIMIT_AS, (memory_mb * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))
    _filter(['read', 'write', 'close', 'exit', 'exit_group', 'brk', 'mmap',
             'mprotect', 'munmap', 'arch_prctl', 'set_tid_address',
             'set_robust_list', 'rseq', 'prlimit64', 'getrandom', 'futex',
             'newfstatat', 'fstat', 'readlink', 'execve', 'clock_gettime'], True)

def execute(binary, args, wall_seconds=1):
    """Restrict candidate to no opens, sockets, process creation or file mutation.

    execve remains allowed for initial launch; subsequent executed code inherits
    the same policy. This is not a formal confinement proof or kernel defense.
    """
    _lib()  # Resolve the shared library before fork.
    start = time.monotonic()
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        proc = subprocess.Popen([str(Path(binary).resolve()), *map(str, args)],
                                stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                close_fds=True, start_new_session=True,
                                env={'LC_ALL': 'C'}, preexec_fn=static_profile)
        timeout = False
        try:
            proc.wait(timeout=wall_seconds)
        except subprocess.TimeoutExpired:
            timeout = True
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        out.seek(0)
        err.seek(0)
        return {'returncode': proc.returncode, 'stdout': out.read(4096).decode(errors='replace'),
                'stderr': err.read(4096).decode(errors='replace'), 'timeout': timeout,
                'wall_seconds': time.monotonic() - start}
