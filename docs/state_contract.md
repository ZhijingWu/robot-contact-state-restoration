# Jiang: exact state-restoration contract

The installed simulator is **MuJoCo 3.17.0**. Both its Python enum/API and [versioned simulation documentation](https://mujoco.readthedocs.io/en/3.17.0/programming/simulation.html) were checked. A 3.3.7 documentation page was an earlier discovery fetch, not the authority for this model's state signature.

## State groups and actual relevance

`mjSTATE_PHYSICS = 30` includes QPOS, QVEL, ACT and HISTORY: 43 values here. `mjSTATE_FULLPHYSICS = 8223` adds TIME and PLUGIN: 44 values. `mjSTATE_INTEGRATION = 16383` includes all available state components: **247 values** in this model. Save/restore uses `mj_stateSize`, `mj_getState` and `mj_setState`, not a hand-built qpos/qvel assumption.

| Component | Bit | Size | Scene-specific relevance |
| --- | ---: | ---: | --- |
| TIME | 1 | 1 | Captured; time aligned across omissions; no time-dependent callback in this scene |
| QPOS | 2 | 22 | Robot and box configuration; essential |
| QVEL | 4 | 21 | 15 robot/gripper and 6 free-box velocities; causally ablated separately |
| ACT | 8 | 0 | No actuator activation state; a separate +ACT experiment would duplicate +qvel |
| HISTORY | 16 | 0 | No history elements in the selected model |
| WARMSTART | 32 | 21 | Solver acceleration warmstart; small measured omission effect |
| CTRL | 64 | 8 | Captured; frame loop deterministically rewrites commands before each rollout frame |
| QFRC_APPLIED | 128 | 21 | Captured, zero; no generalized external-force intervention |
| XFRC_APPLIED | 256 | 150 | Captured, zero on all 25 bodies; no external object force |
| EQ_ACTIVE | 512 | 3 | Active gripper equality constraints; captured, not toggled |
| MOCAP_POS / MOCAP_QUAT | 1024 / 2048 | 0 / 0 | No mocap bodies |
| USERDATA | 4096 | 0 | No user data |
| PLUGIN | 8192 | 0 | No plugin state |
| PLASTIC | — | — | Not exposed by this installed state API; no plastic model element or ablation claimed |

Zero-sized fields are included by the official aggregate flag but are not presented as experimentally meaningful omissions. Controls/applied forces with fixed values are distinguished from active state mechanisms.

## Five layers of the contract

1. **Physics state:** coordinates, velocities and any model-supported activation/history state.
2. **Integration state:** official aggregate including warmstart, user controls/forces and equality activation where present.
3. **Derived quantities:** contacts, Jacobians, kinematics and force workspaces are recomputed with `mj_forward`/stepping. The raw contact list is not serialized as an independent state variable.
4. **External state/artifacts:** wrapper frame/time, exact target tape, mesh/scale/pose/camera/HDF5 inputs and diagnostic recording conventions. The command tape remains identical across paired conditions and is privately copied for forks. Sensor history is cleared as a diagnostic buffer; it does not drive this controller.
5. **Model/configuration:** compiled geometry, mass/inertia, friction, solver, actuator/equality parameters and collision masks. They are rebuilt from identical hashed inputs. `mj_setState` does not serialize arbitrary model edits.

The compiled model hash is `a5b1bbb38c8a064b60b004b1f4f86d222e9aded53838ea96e7baa9ee1d2c7fe1`. Detailed sizes/options and all input hashes are in `configs/model_audit.json`; exact scientific scripts are preserved in `experiments/original/`. Forks use separate scene files/config/model/data and preserve the parent state. Reset is the official model-rebuilding reset followed by the identical seeded prefix, with no extra friction configuration adapter needed here.

The wrapper frame is restored exactly. Its Python `sim_time` counter is reconstructed as frame×frame_dt, rather than serializing the accumulated counter's exact floating-point bits. Dynamics/target indexing in this scene use MuJoCo integration time and frame/tape, not that diagnostic counter. The conformance claim covers the recorded integration/physical/contact traces and frame-indexed controller; it is not a claim of bitwise equality of every Python wrapper field or an arbitrary closed-loop controller.

## Omissions and causal scope

The qpos-only and qpos+qvel conditions start from reset data, copy the stated fields, and align wrapper frame/time so they execute the same candidate commands. They do not introduce command-timing drift. ACT is empty. Object-only velocity, robot/gripper-only velocity and warmstart-only omissions instead retain the rest of the full checkpoint. The qpos+qvel result is close to the warmstart-only result because remaining omitted controls are overwritten and other relevant user fields retain their fixed defaults. This is specific to this frame-boundary task, not proof of universal qpos/qvel completeness.

Full capture/restore passed for the measured states. That is engineering correctness under the declared contract. The separate action-ranking result determines decision relevance; it was negative in this contact scene.
