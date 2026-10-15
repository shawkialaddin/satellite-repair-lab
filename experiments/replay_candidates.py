"""Re-evaluate recorded model candidates with network denied also in compiler."""
import argparse,json,socket,tempfile
from pathlib import Path
from benchmark import TASKS,evaluation
from run_model_pilot import compile_candidate,check
from isolation import block_network
p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);a=p.parse_args()
block_network()
try:socket.socket();raise RuntimeError('network self-test failed')
except PermissionError:pass
rows=[]
for row in json.loads((a.run/'runs.json').read_text()):
    name=row['task'];source=a.run/row['id']/'function.c'
    if not source.exists():continue
    with tempfile.TemporaryDirectory() as d:
        binary,error=compile_candidate(source.read_text().rstrip('\n'),Path(d))
        if error:flags=[False,False,False]
        else:flags=[check(binary,name,cases)['passed'] for cases in [TASKS[name]['dev'],TASKS[name]['accept'],evaluation(name)]]
    same=flags==[row['development_pass'],row['acceptance_pass'],row['evaluation_pass']]
    rows.append({'id':row['id'],'same_as_original':same,'development_pass':flags[0],'acceptance_pass':flags[1],'evaluation_pass':flags[2]})
result={'network_socket_denied':True,'scope':'replay compilation and all validation in a network-filtered parent; generated source unchanged','matches':all(x['same_as_original'] for x in rows),'rows':rows}
(a.run/'offline-replay.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'run':str(a.run),'candidates':len(rows),'matches':result['matches']}))
