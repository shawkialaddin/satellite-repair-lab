import ctypes.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
from benchmark import TASKS,evaluation
from run_model_pilot import compile_candidate,check
from isolation import execute

@unittest.skipUnless(sys.platform=='linux' and shutil.which('cc') and ctypes.util.find_library('seccomp'),'Linux C compiler and libseccomp required')
class RestrictedExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work=tempfile.TemporaryDirectory();cls.root=Path(cls.work.name)
        s=cls.root/'probe.c';s.write_text('int main(void){return 0;}')
        r=subprocess.run(['cc','-static',str(s),'-o',str(cls.root/'probe')],capture_output=True)
        if r.returncode:cls.work.cleanup();raise unittest.SkipTest('static C toolchain unavailable')
    @classmethod
    def tearDownClass(cls):cls.work.cleanup()
    def compile(self,name,source):
        s=self.root/(name+'.c');b=self.root/name;s.write_text(source)
        subprocess.run(['cc','-static',str(s),'-o',str(b)],check=True,capture_output=True)
        return b
    def test_network_files_and_process_creation_denied(self):
        b=self.compile('boundaries','#include <stdio.h>\n#include <sys/socket.h>\n#include <unistd.h>\nint main(){FILE *p=fopen("/etc/passwd","r");int s=socket(2,1,0);int f=fork();printf("%d:%d:%d\\n",p==NULL,s,f);return 0;}')
        r=execute(b,[])
        self.assertEqual(r['returncode'],0)
        self.assertEqual(r['stdout'].strip(),'1:-1:-1')
    def test_runaway_is_terminated(self):
        b=self.compile('loop','int main(){volatile unsigned n=0;while(1)n++;}')
        r=execute(b,[],wall_seconds=.1)
        self.assertTrue(r['timeout']);self.assertNotEqual(r['returncode'],0)
    def test_reference_repairs_pass_and_evaluator_is_disjoint(self):
        for name,t in TASKS.items():
            with self.subTest(task=name),tempfile.TemporaryDirectory() as d:
                self.assertFalse(set(t['dev'])&set(t['accept']))
                self.assertFalse(set(evaluation(name))&set(t['dev']+t['accept']))
                b,e=compile_candidate(t['reference'],Path(d));self.assertIsNone(e)
                self.assertTrue(check(b,name,t['dev']+t['accept']+evaluation(name))['passed'])
    def test_source_contract_rejects_preprocessor_input(self):
        with tempfile.TemporaryDirectory() as d:
            b,e=compile_candidate('#include "/etc/passwd"',Path(d))
        self.assertIsNone(b);self.assertEqual(e,'source_contract_rejected')
