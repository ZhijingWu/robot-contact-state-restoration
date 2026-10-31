"""Frozen contact confirmation. Independent robot commands, official simulator; no external force."""
from contact_common import *
import argparse,shutil,time
ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['smoke','confirm','repeat'],required=True);args=ap.parse_args()
O=P/'JIANG_RAW_RESULTS'/args.stage;O.mkdir(exist_ok=True)
seeds=[10,11] if args.stage=='smoke' else list(range(3000,3016))
root=W/'contact_scene';cfg=config(root)
conditions=['fresh','supported_reset','full_reload','independent_fork','qpos_only','qpos_qvel','drop_object_velocity','drop_robot_velocity','drop_warmstart']
protocol=dict(scope='Independent grasp/sweep contact using official RobotSceneSim; not native converted episode',seeds=seeds,checkpoint_frame=100,horizon_frames=36,actions_joint1_delta_rad=[-.06,0.,.06],gripper_target_normalized=.7,target='checkpoint object XY + .02m along positive joint1 tangential direction (-y,x)',score='terminal Euclidean XY distance to target in metres',conditions=conditions,initial_xy_jitter_m=.001,flag=int(mujoco.mjtState.mjSTATE_INTEGRATION),state_tolerance=1e-9,score_tie_tolerance_m=1e-7,paired_frame_time_and_command_tape=True,external_force=False)
(O/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
def contact_rows(s,step):
 cube=s.model.body('cube').id;rows=[]
 for i in range(s.data.ncon):
  c=s.data.contact[i];bs=[int(s.model.geom_bodyid[c.geom1]),int(s.model.geom_bodyid[c.geom2])]
  if cube not in bs or 0 in bs:continue
  f=np.zeros(6);mujoco.mj_contactForce(s.model,s.data,i,f)
  rows.append([step,int(c.geom1),int(c.geom2),float(c.dist),*f[:3],*c.pos])
 return rows
def frame_step(s,step):
 s.set_joint_targets(s.sim_frame);gi=s.profile.gripper_ctrl_index;s.data.ctrl[gi]=min(s.data.ctrl[gi],s.profile.gripper_close_cap_frac*s.profile.gripper_ctrl_scale)
 tr=[];cts=[]
 for k in range(s.steps_per_frame):
  mujoco.mj_step(s.model,s.data);cc=contact_rows(s,step+k);cts.extend(cc)
  tr.append(np.r_[s.data.time,s.data.qpos,s.data.qvel,len(cc),sum(c[4] for c in cc)])
  s._sensor_traj.append(s.data.sensordata.copy())
 s.sim_frame+=1;s.sim_time+=s.frame_dt
 return tr,cts
def prefix(s,seed):
 r=np.random.default_rng(seed);adr=s.model.joint('cube_freejoint').qposadr.item();dxy=r.uniform(-.001,.001,2);s.data.qpos[adr:adr+2]+=dxy;mujoco.mj_forward(s.model,s.data)
 tr=[];ct=[]
 for f in range(100):
  a,b=frame_step(s,f*10);tr.extend(a);ct.extend(b)
 return np.array(tr),np.array(ct).reshape(-1,10),dxy
def evaluate(s,checkpoint,target):
 scores=[];traces=[];contact_traces=[];tape=s.q_target.copy();qstart=tape[100,:].copy()
 adr=s.model.joint('cube_freejoint').qposadr.item()
 for delta in protocol['actions_joint1_delta_rad']:
  s.q_target=tape.copy()
  for k in range(36):s.q_target[100+k]=qstart;s.q_target[100+k,0]+=delta*(k+1)/36
  restore(s,checkpoint,100);tr=[];ct=[]
  for k in range(36):
   a,b=frame_step(s,k*10);tr.extend(a);ct.extend(b)
  scores.append(float(np.linalg.norm(s.data.qpos[adr:adr+2]-target)));traces.append(np.array(tr));contact_traces.append(np.array(ct).reshape(-1,10))
 s.q_target=tape
 return np.array(scores),np.array(traces),contact_traces
def model_audit(s):
 path=O/'compiled_model.mjb';mujoco.mj_saveModel(s.model,str(path))
 flags={k:dict(bit=int(v),size=int(mujoco.mj_stateSize(s.model,v))) for k,v in mujoco.mjtState.__members__.items() if k!='mjNSTATE'}
 geom=[dict(id=i,name=s.model.geom(i).name,body=s.model.body(s.model.geom_bodyid[i]).name,friction=s.model.geom_friction[i].tolist(),solref=s.model.geom_solref[i].tolist(),solimp=s.model.geom_solimp[i].tolist(),condim=int(s.model.geom_condim[i]),contype=int(s.model.geom_contype[i]),conaffinity=int(s.model.geom_conaffinity[i])) for i in range(s.model.ngeom)]
 out=dict(mujoco=mujoco.__version__,model_sha256=sha(path),state_signature=flags,solver=dict(timestep=float(s.model.opt.timestep),integrator=int(s.model.opt.integrator),solver=int(s.model.opt.solver),cone=int(s.model.opt.cone),iterations=int(s.model.opt.iterations),tolerance=float(s.model.opt.tolerance),impratio=float(s.model.opt.impratio)),sizes={x:int(getattr(s.model,x)) for x in ['nq','nv','na','nu','nhistory','neq','nmocap','nuserdata','npluginstate','nbody']},geoms=geom,scene_hashes={p.name:sha(p) for p in root.iterdir() if p.is_file()},source_commit='880389bda289d2e78154c73ae1b6d23b7a650557')
 (O/'model_audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
rows=[];start=time.time()
for seed in seeds:
 s=RobotSceneSim(cfg,is_kinematic=False)
 if seed==seeds[0]:model_audit(s)
 pt,pc,dxy=prefix(s,seed);base=full(s);qpos=s.data.qpos.copy();qvel=s.data.qvel.copy();adr=s.model.joint('cube_freejoint').qposadr.item();vadr=s.model.joint('cube_freejoint').dofadr.item()
 direction=np.array([-qpos[adr+1],qpos[adr]]);direction/=np.linalg.norm(direction);target=qpos[adr:adr+2]+.02*direction
 assert len(pc)>0 and np.max(pc[:,4])>0,('no robot-object contact',seed)
 np.savez_compressed(O/f'{seed}_checkpoint.npz',integration=base,qpos=qpos,qvel=qvel,target=target,frame=100,initial_xy_jitter=dxy,prefix_trace=pt,prefix_contacts=pc)
 # Verify contact instrumentation reproduces the official frame step exactly.
 restore(s,base,100);s.sim_one_frame();official=full(s);restore(s,base,100);frame_step(s,0);assert np.array_equal(official,full(s)),'instrumented step differs'
 reference=None;reference_scores=None
 for condition in conditions:
  fork=None
  if condition=='fresh':ck=base.copy()
  elif condition=='supported_reset':s.reset();p2,c2,_=prefix(s,seed);ck=full(s);assert np.array_equal(p2,pt) and np.array_equal(c2,pc)
  elif condition=='full_reload':ck=np.load(O/f'{seed}_checkpoint.npz')['integration']
  elif condition=='independent_fork':
   forkroot=W/'contact_fork';shutil.copytree(root,forkroot,dirs_exist_ok=True);fork=RobotSceneSim(config(forkroot),is_kinematic=False);restore(fork,base,100);ck=full(fork);parent=full(s).copy()
  elif condition in ['qpos_only','qpos_qvel']:
   mujoco.mj_resetData(s.model,s.data);s.data.qpos[:]=qpos;s.data.time=100*s.frame_dt
   if condition=='qpos_qvel':s.data.qvel[:]=qvel
   mujoco.mj_forward(s.model,s.data);ck=full(s)
  else:
   restore(s,base,100)
   if condition=='drop_object_velocity':s.data.qvel[vadr:vadr+6]=0
   elif condition=='drop_robot_velocity':s.data.qvel[:vadr]=0
   elif condition=='drop_warmstart':s.data.qacc_warmstart[:]=0
   mujoco.mj_forward(s.model,s.data);ck=full(s)
  chosen=fork if fork is not None else s
  scores,tr,cts=evaluate(chosen,ck,target)
  if reference is None:reference=tr.copy();reference_scores=scores.copy()
  initial_q_equal=bool(np.array_equal(qpos,chosen.data.qpos)) if False else True
  impulse=[float(np.sum(c[:,4])*chosen.sim_dt) for c in cts]
  for a,c in enumerate(cts):np.savez_compressed(O/f'{seed}_{condition}_action{a}.npz',trace=tr[a],contacts=c,score=scores[a])
  row=dict(seed=seed,condition=condition,checkpoint_full_state_max_abs=float(np.max(np.abs(ck-base))),scores_m=scores.tolist(),winner=int(np.argmin(scores)),rank=np.argsort(scores).tolist(),score_difference_max_m=float(np.max(np.abs(scores-reference_scores))),object_position_difference_max_m=float(np.max(np.abs(tr[:,:,1+adr:1+adr+3]-reference[:,:,1+adr:1+adr+3]))),robot_q_difference_max_rad=float(np.max(np.abs(tr[:,:,1:8]-reference[:,:,1:8]))),trace_max_abs=float(np.max(np.abs(tr-reference))),normal_impulse_sum_Ns=impulse,contact_counts=[len(c) for c in cts],first_prefix_contact_time_s=float(pt[int(pc[0,0]),0]),initial_xy_jitter=dxy.tolist(),parent_preserved=bool(np.array_equal(parent,full(s))) if fork is not None else None)
  assert np.all(np.isfinite(tr)) and np.all(np.isfinite(scores))
  rows.append(row)
 print(json.dumps(dict(seed=seed,reference_scores_m=reference_scores.tolist(),qpos_only_scores_m=next(r['scores_m'] for r in rows if r['seed']==seed and r['condition']=='qpos_only'),elapsed_s=time.time()-start)),flush=True)
(O/'measurements.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
summary={}
for c in conditions:
 rr=[r for r in rows if r['condition']==c];refs={r['seed']:r for r in rows if r['condition']=='fresh'}
 summary[c]=dict(n=len(rr),winner_flips=sum(r['winner']!=refs[r['seed']]['winner'] for r in rr),max_score_difference_m=max(r['score_difference_max_m'] for r in rr),max_object_position_difference_m=max(r['object_position_difference_max_m'] for r in rr),max_robot_q_difference_rad=max(r['robot_q_difference_max_rad'] for r in rr),max_trace_difference_mixed_units=max(r['trace_max_abs'] for r in rr))
(O/'summary.json').write_text(json.dumps(dict(status='COMPLETED',stage=args.stage,runtime_s=time.time()-start,conditions=summary),indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
