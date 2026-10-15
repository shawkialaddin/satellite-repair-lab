"""Preliminary matched-candidate experiment. Synthetic cases, no flight claims."""
import argparse
import hashlib
import json
import os
import platform
import re
import resource
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from benchmark import TASKS,HARNESS,oracle,evaluation
from isolation import execute,block_network

ROOT=Path(__file__).resolve().parents[1]

def sha(s): return hashlib.sha256(s.encode()).hexdigest()

def compile_candidate(text, work):
    # Keep only a single model-supplied function. This is an input contract,
    # NOT a hardened compiler sandbox. Compilation uses trusted host tools.
    text=text.strip()
    if text.startswith('```'):
        text=re.sub(r'^```[^\n]*\n','',text)
        text=re.sub(r'\n```\s*$','',text)
    if len(text)>8000 or '#' in text or re.search(r'\b(asm|__asm__|__asm|include|system|execve|fork)\b',text):
        return None, 'source_contract_rejected'
    if not re.match(r'^int\s+repair\s*\(',text): return None,'source_contract_rejected'
    source=work/'candidate.c'; binary=work/'candidate'
    source.write_text(HARNESS % text)
    try:
        r=subprocess.run(['cc','-static','-std=c11','-O0','-Wall','-Wextra',str(source),'-o',str(binary)],
                         capture_output=True,text=True,timeout=15,env={'PATH':'/usr/bin:/bin','LC_ALL':'C'}, preexec_fn=block_network)
        if r.returncode: return None,r.stderr[:4000]
        return binary,None
    except subprocess.TimeoutExpired: return None,'compile_timeout'

def check(binary,name,cases):
    failures=[]
    for args in cases:
        r=execute(binary,args)
        if r['returncode']!=0 or r['stdout'].strip()!=str(oracle(name,args)):
            failures.append({'args':args,'expected':oracle(name,args),**r})
    return {'passed':not failures,'cases':len(cases),'failures':failures[:10],'failed_cases':len(failures)}

def child_limits():
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(90,)*2)
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    block_network()

def main():
    p=argparse.ArgumentParser();p.add_argument('--model',type=Path,required=True)
    p.add_argument('--python',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    if (a.output/'protocol.json').exists():
        p.error('Output already contains a protocol; select a fresh directory')
    protocol={'study':'exploratory synthetic pilot, not main study','tasks':list(TASKS),'seeds':[11,22,33],
              'max_attempts':2,'generation_wall_limit_seconds':120,'generation_address_space_limit_bytes':3*1024**3,
              'cpu_limit_seconds':90,'model':json.loads((a.model.parent/'model.json').read_text()),
              'comparison':'identical generated candidates, B1 dev, B2 dev+accept, B3 B2+synthetic load defer',
              'evaluation_feedback_to_model':False,'acceptance_feedback_to_model':False,
              'stopping_rule':'stop task/seed when development checks pass, otherwise at two attempts',
              'environment':{'platform':platform.platform(),'cpus':os.cpu_count(),'python':sys.version,
              'compiler':subprocess.check_output(['cc','--version'],text=True).splitlines()[0]},
              'limitations':['synthetic cases','no target spacecraft','no full compiler sandbox','no energy measurements','not preregistered externally']}
    (a.output/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    rows=[]
    for name,task in TASKS.items():
      for seed in protocol['seeds']:
        messages=[{'role':'system','content':'You repair a C function. Return only the complete int repair(uint32_t a, uint32_t b, uint32_t c) function. No Markdown, headers, main, or explanations. uint32_t and uint64_t are already defined.'},
                  {'role':'user','content':task['description']+'\nBuggy function:\n'+task['vulnerable']+'\nVisible development examples (arguments -> expected):\n'+ '\n'.join(str(x)+' -> '+str(oracle(name,x)) for x in task['dev'])}]
        for attempt in range(1,3):
          ident=f'{name}-seed{seed}-attempt{attempt}';folder=a.output/ident;folder.mkdir(exist_ok=True)
          request={'messages':messages};(folder/'prompt.json').write_text(json.dumps(request,indent=2)+'\n')
          command=[a.python,str(ROOT/'experiments/local_infer.py'),'--model',str(a.model.resolve()),'--seed',str(seed+attempt-1)]
          start=time.monotonic()
          with (folder/'inference.stderr').open('w') as err:
            proc=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,
                                  close_fds=True,start_new_session=True,preexec_fn=child_limits)
            try:
              stdout,_=proc.communicate(json.dumps(request),timeout=120)
            except subprocess.TimeoutExpired:
              os.killpg(proc.pid,signal.SIGKILL);stdout,_=proc.communicate()
          row={'id':ident,'task':name,'trial_seed':seed,'seed':seed,'attempt':attempt,'generation_returncode':proc.returncode,'total_inference_wall_seconds':time.monotonic()-start}
          (folder/'inference.stdout').write_text(stdout)
          if proc.returncode!=0:
            row.update({'status':'generation_failed','development_pass':False,'acceptance_pass':False,'evaluation_pass':False})
            rows.append(row);(a.output/'runs.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True);break
          try: response=json.loads(stdout)
          except json.JSONDecodeError:
            row.update({'status':'invalid_inference_json','development_pass':False,'acceptance_pass':False,'evaluation_pass':False});rows.append(row);break
          (folder/'response.json').write_text(json.dumps(response,indent=2)+'\n')
          text=response['text'];(folder/'function.c').write_text(text+'\n')
          row.update({k:v for k,v in response.items() if k!='text'});row['function_sha256']=sha(text)
          with tempfile.TemporaryDirectory() as d:
            binary,error=compile_candidate(text,Path(d))
            if error:
              row.update({'status':'build_failed','build_error':error,'development_pass':False,'acceptance_pass':False,'evaluation_pass':False})
              feedback='Compilation or output contract failed: '+error
            else:
              dev=check(binary,name,task['dev']);accept=check(binary,name,task['accept']);ev=check(binary,name,evaluation(name))
              row.update({'status':'evaluated','development_pass':dev['passed'],'acceptance_pass':accept['passed'],'evaluation_pass':ev['passed'],
                          'development':dev,'acceptance':accept,'evaluation':ev})
              feedback='Development test failures: '+json.dumps(dev['failures'])
          row['policies']={'B1': 'accept' if row['development_pass'] else 'reject',
                           'B2': 'accept' if row['development_pass'] and row['acceptance_pass'] else 'reject',
                           'B3_light':'accept' if row['development_pass'] and row['acceptance_pass'] else 'reject',
                           'B3_busy':'defer' if row['development_pass'] and row['acceptance_pass'] else 'reject'}
          rows.append(row);(a.output/'runs.json').write_text(json.dumps(rows,indent=2)+'\n')
          print(json.dumps({k:v for k,v in row.items() if k not in ['development','acceptance','evaluation']}),flush=True)
          if row['development_pass']: break
          messages += [{'role':'assistant','content':text},{'role':'user','content':feedback+'\nReturn only the corrected function.'}]
    print('COMPLETE',len(rows),flush=True)
if __name__=='__main__': main()
