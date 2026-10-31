from pathlib import Path
import sys,json,hashlib
import numpy as np,h5py,trimesh,mujoco
W=Path(__file__).parent.resolve();ROOT=Path.cwd();P=ROOT/'outputs'/'jiang-yip-native-validation'
UP=ROOT/'work'/'continuation'/'sources'/'ar2s'
sys.path.insert(0,str(UP))
from ar2s.droid_sim.scene.config import SceneConfig,SceneObject,GroundSpec,CameraSpec,FoundationPoseDir
from ar2s.droid_sim.scene.robot_scene_sim import RobotSceneSim
def prepare(root,pos=(2.,0.,.04),size=(.04,.04,.04),ground_z=0.,q=None,grip=None):
 root.mkdir(parents=True,exist_ok=True)
 raw=ROOT/'work'/'continuation'/'official_flat_robot.h5'
 with h5py.File(raw,'r') as f:
  rq=f['joint_position'][:];rg=f['gripper_position'][:]
 if q is None:q=rq
 if grip is None:grip=rg
 with h5py.File(root/'robot.h5','w') as f:f['joint_position']=q;f['gripper_position']=grip
 trimesh.creation.box(extents=size).export(root/'cube.obj');np.save(root/'scale.npy',np.ones(3))
 poses=np.repeat(np.eye(4)[None],len(q),axis=0);poses[:,:3,3]=pos
 np.savez(root/'poses.npz',poses=poses,frame_indices=np.arange(len(q),dtype=np.int32))
 np.savez(root/'extrinsics.npz',cam_mat_0=np.eye(4));np.savez(root/'intrinsics.npz',cam_K_0=np.array([[500,0,320],[0,500,240],[0,0,1]]))
 (root/'scene_spec.json').write_text(json.dumps(dict(position=pos,size=size,ground_z=ground_z),indent=2),encoding='utf-8')
 return config(root)
def config(root):
 d=json.loads((root/'scene_spec.json').read_text(encoding='utf-8'))
 return SceneConfig('independent_robot_contact',str(root/'robot.h5'),[SceneObject('cube',str(root/'cube.obj'),str(root/'scale.npy'),FoundationPoseDir(str(root/'poses.npz')),mass=.05,friction=(.5,.005,.0001))],GroundSpec('GROUND',offset=-d['ground_z']),CameraSpec((0,),0,str(root/'extrinsics.npz'),str(root/'intrinsics.npz'),(640,480)))
def full(s):
 flag=mujoco.mjtState.mjSTATE_INTEGRATION;x=np.empty(mujoco.mj_stateSize(s.model,flag));mujoco.mj_getState(s.model,s.data,x,flag);return x
def restore(s,x,frame):
 mujoco.mj_setState(s.model,s.data,x,mujoco.mjtState.mjSTATE_INTEGRATION);s.sim_frame=int(frame);s.sim_time=s.sim_frame*s.frame_dt;s._sensor_traj=[];mujoco.mj_forward(s.model,s.data)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
