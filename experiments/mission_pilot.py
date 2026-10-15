"""Measured host CPU contention, not a spacecraft or RTOS timing model."""
import argparse
import json
import multiprocessing as mp
import os
import platform
import random
import time
from pathlib import Path

def burn(seconds):
    end=time.process_time()+seconds
    n=1
    while time.process_time()<end:
        n=(n*1664525+1013904223)&0xffffffff
    return n

def validator(start,cpu,delay,queue):
    os.sched_setaffinity(0,{cpu})
    target=start+delay
    if target>time.monotonic():time.sleep(target-time.monotonic())
    began=time.monotonic()
    for _ in range(20):
        burn(0.008)
        time.sleep(0.012)
    queue.put({'validation_start_seconds':began-start,'validation_finish_seconds':time.monotonic()-start,'validation_jobs':20})

def trial(policy,cpu):
    original=os.sched_getaffinity(0);os.sched_setaffinity(0,{cpu})
    try:
        period=.020;slots=60;start=time.monotonic()+.060
        queue=mp.Queue();worker=None
        if policy!='B0':
            worker=mp.Process(target=validator,args=(start,cpu,.6 if policy=='B3' else 0,queue));worker.start()
        jobs=[]
        for i in range(slots):
            release=start+i*period
            delay=release-time.monotonic()
            if delay>0:time.sleep(delay)
            began=time.monotonic()
            demand=.014 if i<30 else .005
            burn(demand)
            finish=time.monotonic();deadline=release+period
            jobs.append({'slot':i,'demand_cpu_seconds':demand,'release':release-start,'start':began-start,'finish':finish-start,'deadline_missed':finish>deadline,'lateness_seconds':max(0,finish-deadline)})
        validation=None
        if worker:
            worker.join(timeout=5)
            if worker.is_alive():worker.kill();worker.join();raise RuntimeError('validator timeout')
            if worker.exitcode:raise RuntimeError('validator failed')
            validation=queue.get(timeout=1)
        return {'policy':policy,'mission_jobs':jobs,'deadline_misses':sum(j['deadline_missed'] for j in jobs),'max_lateness_seconds':max(j['lateness_seconds'] for j in jobs),'validation':validation}
    finally:os.sched_setaffinity(0,original)

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    cpu=min(os.sched_getaffinity(0));order=[(repeat,pol) for repeat in range(3) for pol in ['B0','B2','B3']]
    random.Random(20261016).shuffle(order)
    result={'measurement':'actual host wall/CPU timing; synthetic periodic mission and validation workload','cpu':cpu,'platform':platform.platform(),'period_seconds':.020,'mission_demands_seconds':[.014,.005],'policy':'B3 defers validation 0.6 seconds into lower-demand phase','inference_included':False,'runs':[]}
    for repeat,policy in order:
        row=trial(policy,cpu);row['repeat']=repeat;result['runs'].append(row)
        print(policy,repeat,row['deadline_misses'],row['validation'],flush=True)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
