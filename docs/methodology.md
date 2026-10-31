# Methodology

The exact frozen experiment is `experiments/original/contact_experiment.py`, with its original `contact_common.py`. Their preserved SHA-256 identities are in `provenance/original_scripts.json`. The publication wrapper only creates an isolated filesystem layout and launches that code. It does not change the model, controller, seeds, omissions, horizon, scoring or candidate selection.

The box is 0.04 × 0.04 × 0.08 m, mass 0.05 kg, nominal position (0.595, 0.120, 0.040) m, friction (0.5, 0.005, 0.0001). Initial arm coordinates are DROID raw action frame 40. Eighty independent target-tape samples describe a hold, closure to normalized 0.7 and joint-1 sweep. The official simulator interpolates its 15 Hz target tape to its 60 Hz frame loop. Identity camera sidecars initialize the simulator and are not calibrated perception evidence.

Each confirmation seed 3000–3015 applies independent uniform initial XY jitter within ±0.001 m per axis. A common 100-frame prefix establishes force-producing robot-object contact. Its 247-value integration checkpoint, frame number, qpos/qvel, target and prefix traces are saved. A scalar normal-contact force must be positive for every prefix. The instrumented frame step is checked against the official `sim_one_frame` implementation by exact integration-state equality.

The three candidates ramp arm joint 1 by −0.06, 0 or +0.06 rad over 36 frames; all share the same timing and other command targets. The target is checkpoint object XY plus 0.02 m along normalized (−y,x). Score is terminal Euclidean XY distance to that target in metres. The selected candidate is the first `argmin`, with all actual reference margins well above the declared 1e−7 m tie scale. No tie-break-driven reversal was observed.

## Nine conditions

1. `fresh`: saved integration checkpoint after a fresh seeded prefix; reference.
2. `supported_reset`: official reset/model rebuild, then identical seeded prefix.
3. `full_reload`: reload saved full integration vector.
4. `independent_fork`: private scene/config/model/data copy with full checkpoint; original parent preserved.
5. `qpos_only`: reset data, copy positions and align physics time/frame; velocities and warmstart are omitted.
6. `qpos_qvel`: additionally copy velocities; residual omissions are not claimed equivalent to full state.
7. `drop_object_velocity`: full checkpoint with only free-box velocities zeroed.
8. `drop_robot_velocity`: full checkpoint with only robot/gripper velocities zeroed.
9. `drop_warmstart`: full checkpoint with solver acceleration warmstart zeroed.

Controls are rewritten by the frame controller. Applied generalized/body forces remain zero. No actuator activation, history, mocap, user-data or plugin state exists in this particular model. See the component-by-component [state contract](state_contract.md).

## Endpoints and uncertainty

Physical discrepancy is an absolute component maximum in object XYZ over the same candidate substeps. Score perturbation is an absolute terminal cost difference. A command-choice flip compares paired `argmin` indices. Reference-scored regret is the reference cost of the omission-selected command minus the minimum reference cost. These quantities are not interchangeable.

No superiority or algorithmic novelty hypothesis is supported. Observed regret is zero for each seed. For perspective only, an IID Bernoulli interpretation of 0/16 has one-sided exact 95% upper bound `1 - 0.05**(1/16)` (approximately 17.07%) under this narrow perturbation distribution. It is not a bound over other controllers, geometries or tasks.

Two geometry-feasibility and two protocol-smoke seeds preceded the fixed confirmation; their results are not pooled with the 16 confirmation seeds. The original geometry and fixed sample count were not expanded to obtain a choice reversal. Publication verification repeats this frozen protocol, without introducing a new experimental condition.
