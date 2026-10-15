"""Regenerate descriptive counts from recorded model and workload outputs."""
import collections
import json
import statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    out={}
    for name,label in [('model-pilot','0.5B'),('model-pilot-1.5b','1.5B')]:
        p=ROOT/'results'/name
        rows=json.loads((p/'runs.json').read_text())
        groups=collections.defaultdict(list)
        for row in rows:
            base_seed=row['id'].split('-seed')[1].split('-')[0]
            groups[(row['task'],base_seed)].append(row)
        out[label]={
            'attempts':len(rows),'trials':len(groups),
            'build_pass':sum(r['status']=='evaluated' for r in rows),
            'valid_trials':sum(any(r['evaluation_pass'] for r in group) for group in groups.values()),
            'accepted_B1':sum(r['development_pass'] for r in rows),
            'accepted_B2':sum(r['development_pass'] and r['acceptance_pass'] for r in rows),
            'harmful_B1':sum(r['development_pass'] and not r['evaluation_pass'] for r in rows),
            'harmful_B2':sum(r['development_pass'] and r['acceptance_pass'] and not r['evaluation_pass'] for r in rows),
            'inference_wall_median':statistics.median(r['total_inference_wall_seconds'] for r in rows),
            'inference_wall_range':[min(r['total_inference_wall_seconds'] for r in rows),max(r['total_inference_wall_seconds'] for r in rows)],
            'peak_rss_MiB_range':[min(r['peak_rss_kib'] for r in rows)/1024,max(r['peak_rss_kib'] for r in rows)/1024],
            'unique_function_outputs':len({r['function_sha256'] for r in rows})}
    mission=json.loads((ROOT/'results/mission-pilot.json').read_text())
    out['mission']={p:{'misses':[r['deadline_misses'] for r in mission['runs'] if r['policy']==p],
                      'jobs_per_repeat':60,'repeats':3,
                      'validation_finish_seconds':[r['validation']['validation_finish_seconds'] for r in mission['runs'] if r['policy']==p and r['validation']]} for p in ['B0','B2','B3']}
    (ROOT/'results/study-summary.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v.get('valid_trials') for k,v in out.items() if k!='mission'}))
if __name__=='__main__':main()
