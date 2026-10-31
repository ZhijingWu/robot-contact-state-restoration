"""Recompute contact-only claims from numeric NPZ arrays; no simulator required."""
from pathlib import Path
import argparse,csv,hashlib,json
import numpy as np

REPO=Path(__file__).resolve().parents[1]
def run(raw, output):
    protocol=json.loads((REPO/'configs/protocol.json').read_text())
    seeds=protocol['seeds'];conditions=protocol['conditions']
    assert seeds==list(range(3000,3016)) and len(conditions)==9
    aggregate={c:dict(paired_seeds=16,choice_flips=0,max_coordinate_discrepancy_m=0.,max_score_perturbation_m=0.,max_normal_force_sum_discrepancy_N=0.,max_reference_scored_selection_regret_m=0.,full_control_arrays_exact=True if c in ['fresh','supported_reset','full_reload','independent_fork'] else None) for c in conditions}
    records=[];margins=[]
    for seed in seeds:
        with np.load(raw/f'{seed}_checkpoint.npz',allow_pickle=False) as ck:
            target=ck['target'].copy()
            assert ck['integration'].size==247 and int(ck['frame'])==100
            assert ck['prefix_contacts'].shape[0]>0 and np.max(ck['prefix_contacts'][:,4])>0
        fresh=[]
        for a in range(3):
            with np.load(raw/f'{seed}_fresh_action{a}.npz',allow_pickle=False) as f:
                fresh.append({k:f[k].copy() for k in f.files})
        ref_scores=np.array([np.linalg.norm(f['trace'][-1,16:18]-target) for f in fresh])
        ref_winner=int(np.argmin(ref_scores));margins.append(float(np.sort(ref_scores)[1]-min(ref_scores)))
        for c in conditions:
            scores=[];coord=force=0.;exact=True
            for a in range(3):
                with np.load(raw/f'{seed}_{c}_action{a}.npz',allow_pickle=False) as f:
                    assert set(f.files)=={'trace','contacts','score'}
                    assert f['trace'].shape==(360,46)
                    assert all(np.isfinite(f[k]).all() for k in f.files)
                    s=float(np.linalg.norm(f['trace'][-1,16:18]-target))
                    assert abs(s-float(f['score']))<1e-14
                    scores.append(s)
                    coord=max(coord,float(np.max(np.abs(f['trace'][:,16:19]-fresh[a]['trace'][:,16:19]))))
                    force=max(force,float(np.max(np.abs(f['trace'][:,-1]-fresh[a]['trace'][:,-1]))))
                    exact=exact and all(f[k].dtype==fresh[a][k].dtype and f[k].shape==fresh[a][k].shape and f[k].tobytes()==fresh[a][k].tobytes() for k in f.files)
            winner=int(np.argmin(scores));flip=int(winner!=ref_winner)
            regret=float(ref_scores[winner]-min(ref_scores));score_delta=float(np.max(np.abs(np.array(scores)-ref_scores)))
            ag=aggregate[c];ag['choice_flips']+=flip
            for key,value in [('max_coordinate_discrepancy_m',coord),('max_score_perturbation_m',score_delta),('max_normal_force_sum_discrepancy_N',force),('max_reference_scored_selection_regret_m',regret)]:ag[key]=max(ag[key],value)
            if ag['full_control_arrays_exact'] is not None:ag['full_control_arrays_exact'] &= exact
            records.append(dict(seed=seed,condition=c,scores_m=scores,chosen_command_index=winner,reference_command_index=ref_winner,choice_flip=flip,max_coordinate_discrepancy_m=coord,max_score_perturbation_m=score_delta,reference_scored_selection_regret_m=regret,reference_best_second_margin_m=margins[-1]))
    repeated=json.loads((REPO/'provenance/historical_repeat_arrays.json').read_text())
    count=0
    assert len(list(raw.glob('*.npz')))==448
    for name,arrays in repeated['files'].items():
        with np.load(raw/name,allow_pickle=False) as f:
            assert set(f.files)==set(arrays)
            for k,meta in arrays.items():
                assert f[k].dtype.str==meta['dtype'] and list(f[k].shape)==meta['shape']
                assert hashlib.sha256(f[k].tobytes(order='C')).hexdigest()==meta['sha256'],(name,k)
                count+=1
    assert count==1424
    q=aggregate['qpos_only']
    assert q['choice_flips']==0 and abs(q['max_coordinate_discrepancy_m']-0.0007038157109165166)<1e-15
    assert abs(q['max_score_perturbation_m']-0.00003388700127388011)<1e-15
    assert all(aggregate[c]['full_control_arrays_exact'] for c in ['fresh','supported_reset','full_reload','independent_fork'])
    summary=dict(paired_seeds=16,seeds=seeds,conditions=aggregate,minimum_reference_candidate_margin_m=min(margins),historical_repeat=dict(npz_files=448,arrays=count,all_array_byte_hashes_match=True,repeat_payload='The independent repeat is represented by its per-array byte hashes, not duplicate NPZ payloads.'),statistics=dict(design='Paired fixed-seed comparison; no hypothesis-test significance claim.',observed_qpos_only_reference_scored_regret_m=[r['reference_scored_selection_regret_m'] for r in records if r['condition']=='qpos_only'],zero_of_16_one_sided_binomial95_upper=1-.05**(1/16),binomial_scope='Only an IID interpretation under the narrow tested perturbation distribution; not a bound over arbitrary tasks.'),units='All distances/scores in metres; force in N. Coordinate discrepancy is an absolute XYZ component maximum, not Euclidean displacement.',mujoco_state=dict(version='3.17.0',mask=16383,values=247))
    output.mkdir(parents=True,exist_ok=True)
    for name,obj in [('aggregate.json',summary),('per_seed.json',records)]:
        (output/name).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
    columns=['seed','condition','chosen_command_index','reference_command_index','choice_flip','max_coordinate_discrepancy_m','max_score_perturbation_m','reference_scored_selection_regret_m','reference_best_second_margin_m']
    with (output/'per_seed.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(records)
    print(json.dumps(dict(paired_seeds=16,rows=len(records),qpos_only=q,min_candidate_margin_m=min(margins),repeat_arrays_verified=count),indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raw',type=Path,default=REPO/'data/raw/confirm')
    ap.add_argument('--out',type=Path,required=True,help='Fresh analysis output directory; original results are not overwritten')
    a=ap.parse_args();assert not a.out.exists(),'Choose a fresh output directory'
    run(a.raw.resolve(),a.out.resolve())
