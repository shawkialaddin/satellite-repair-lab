"""Trusted local inference worker. Its only task input is a JSON prompt on stdin."""
import argparse
import hashlib
import json
import os
import resource
import socket
import sys
import time

from isolation import block_network
from llama_cpp import Llama

p=argparse.ArgumentParser()
p.add_argument('--model',required=True)
p.add_argument('--seed',type=int,required=True)
p.add_argument('--threads',type=int,default=2)
a=p.parse_args()
request=json.load(sys.stdin)
block_network()
blocked=False
try:
    socket.socket(socket.AF_INET,socket.SOCK_STREAM)
except PermissionError:
    blocked=True
if not blocked:
    raise SystemExit('Network filter self-test failed')
start=time.monotonic()
model=Llama(model_path=a.model,n_ctx=2048,n_threads=a.threads,n_threads_batch=a.threads,
            n_batch=128,seed=a.seed,verbose=False,n_gpu_layers=0)
load_seconds=time.monotonic()-start
start=time.monotonic()
r=model.create_chat_completion(messages=request['messages'],temperature=0.2,
                               top_p=0.95,max_tokens=384,seed=a.seed)
print(json.dumps({'text':r['choices'][0]['message']['content'],
                  'finish_reason':r['choices'][0]['finish_reason'],'usage':r['usage'],
                  'load_seconds':load_seconds,'generation_seconds':time.monotonic()-start,
                  'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  'cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime + resource.getrusage(resource.RUSAGE_SELF).ru_stime,
                  'network_socket_denied':blocked,'seed':a.seed,
                  'backend':'llama-cpp-python 0.3.16','context':2048,'max_tokens':384,
                  'temperature':0.2,'top_p':0.95,'threads':a.threads}))
