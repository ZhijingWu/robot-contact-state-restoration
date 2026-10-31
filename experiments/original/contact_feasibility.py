from contact_common import *
with h5py.File(ROOT/'work'/'continuation'/'official_flat_robot.h5','r') as f:q0=f['joint_position'][40]
N=80;q=np.tile(q0,(N,1));g=np.zeros((N,1))
# 20 frames hold, 60 close, 48-frame joint-1 sweep, then hold, at 60Hz.
for i in range(N):
 t=i*4;g[i,0]=.7*np.clip((t-20)/60,0,1);q[i,0]+=.12*np.clip((t-80)/48,0,1)
root=W/'contact_scene';cfg=prepare(root,pos=(.595,.120,.040),size=(.04,.04,.08),q=q,grip=g)
spec=dict(scope='Independent robot-contact scene; DROID-derived initial arm posture, independent gripper/joint command tape',seeds=[0,1],cube_mass_kg=.05,cube_size_m=[.04,.04,.08],cube_position_m=[.595,.120,.040],timestep_s=1/600,frames=180,commands='hold 20 frames, gripper close to .7 over 60 frames, joint1 +.12 rad over frames80-128',external_forces=False)
(P/'JIANG_RAW_RESULTS'/'feasibility_protocol.json').write_text(json.dumps(spec,indent=2),encoding='utf-8')
def contacts(s):
 cube=s.model.body('cube').id;out=[]
 for i in range(s.data.ncon):
  c=s.data.contact[i];b1=int(s.model.geom_bodyid[c.geom1]);b2=int(s.model.geom_bodyid[c.geom2])
  if cube not in [b1,b2]:continue
  other=b2 if b1==cube else b1
  if other==0:continue
  f=np.zeros(6);mujoco.mj_contactForce(s.model,s.data,i,f)
  out.append(dict(geom1=int(c.geom1),geom2=int(c.geom2),other_body=s.model.body(other).name,dist=float(c.dist),normal_force_N=float(f[0]),pos=c.pos.tolist()))
 return out
for seed in [0,1]:
 s=RobotSceneSim(cfg,is_kinematic=False);r=np.random.default_rng(seed);adr=s.model.joint('cube_freejoint').qposadr.item();s.data.qpos[adr:adr+2]+=r.uniform(-.001,.001,2);mujoco.mj_forward(s.model,s.data)
 initial=contacts(s);tr=[];ct=[]
 for frame in range(180):
  s.sim_one_frame();cc=contacts(s);ct.extend([dict(frame=frame,time_s=float(s.data.time),**c) for c in cc]);tr.append(np.r_[s.data.time,s.data.qpos,s.data.qvel])
 a=np.asarray(tr);np.savez_compressed(P/'JIANG_RAW_RESULTS'/f'feasibility_seed{seed}.npz',trace=a)
 out=dict(seed=seed,initial_robot_object_contacts=initial,contact_samples=len(ct),first_contact_frame=ct[0]['frame'] if ct else None,contact_bodies=sorted({x['other_body'] for x in ct}),max_normal_force_N=max([x['normal_force_N'] for x in ct],default=0),object_initial_xyz=s.data.qpos[adr:adr+3].tolist() if False else [.595,.120,.040],object_final_xyz=s.data.qpos[adr:adr+3].tolist(),finite=bool(np.all(np.isfinite(a))),contacts=ct)
 (P/'JIANG_RAW_RESULTS'/f'feasibility_seed{seed}.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='contacts'}),flush=True)
