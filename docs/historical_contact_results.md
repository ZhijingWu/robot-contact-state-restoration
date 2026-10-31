# Jiang: contact results

**The robot contacted and moved the object. Incomplete restoration changed some contact/motion values, but changed no candidate-action choices in 16 paired seeds.** This is an independent robot-contact extension, not a native Agentic Real2Sim converted-episode reproduction. No upstream source fix was made and no algorithmic innovation is claimed.

## Confirmation and controls

Seeds 3000–3015 use ±1 mm initial XY jitter. Checkpoint is frame 100, after contact is established. Three 36-frame candidates ramp joint 1 by -0.06, 0 or +0.06 rad, using the same initial arm target and gripper target. The goal is checkpoint object XY plus 0.02 m in the positive joint-1 tangential direction (-y,x). Score is terminal Euclidean XY distance in metres. Candidates are robot commands, not learned-policy outputs. Sample count was fixed at 16 and not expanded.

| Condition | Choice flips | Max object position-coordinate difference (m) | Max score difference (m) | Max summed normal-force difference (N) |
| --- | ---: | ---: | ---: | ---: |
| fresh | 0/16 | 0 | 0 | 0 |
| supported_reset | 0/16 | 0 | 0 | 0 |
| full_reload | 0/16 | 0 | 0 | 0 |
| independent_fork | 0/16 | 0 | 0 | 0 |
| qpos_only | 0/16 | 0.000703815711 | 3.38870013e-05 | 2.78926715 |
| qpos_qvel | 0/16 | 8.19265634e-07 | 4.56991849e-08 | 0.0185658689 |
| drop_object_velocity | 0/16 | 0.000109489431 | 4.16044148e-06 | 7.11115263 |
| drop_robot_velocity | 0/16 | 0.000571101641 | 2.38919635e-05 | 3.92022506 |
| drop_warmstart | 0/16 | 8.19265634e-07 | 4.56991849e-08 | 0.0185658689 |

The full-state reload, reset/prefix and private-copy fork controls match the fresh reference **exactly**, including recorded contacts/forces/traces. The fork preserves its parent. All conditions select the same hold candidate. Minimum reference best-versus-second-best score gap is **0.0123563393 m**, far above the largest observed score perturbation and `1e-7 m` tie tolerance.

All omission conditions have observed reference-scored selection regret **0 m**. A paired bootstrap of that observed regret is [0,0], which does not prove universal equivalence. With 0/16 flips, even an IID Bernoulli interpretation under this narrow perturbation distribution has a one-sided exact 95% upper bound about **17.07%**. It is not a bound for arbitrary contact scenes.

## Causal interpretation

Velocity omission changes physical dynamics: qpos-only reaches a maximum coordinate difference **0.000703815711 m** (about 0.704 mm), while its maximum terminal score difference is only **3.38870013e-05 m** (about 0.0339 mm). Robot/gripper velocity omission produces a larger motion effect than box-velocity omission here; nonlinear interactions prevent treating those maxima as an additive decomposition. Warmstart omission gives a much smaller, nonzero difference. Do not label qpos+qvel or warmstart-only exact equivalence.

The intervention occurs during established contact. Missing velocities differ immediately at the checkpoint; motion/contact-force differences occur on subsequent substeps. Original first-contact onset is part of the common prefix, so this experiment does not test how a pre-contact omission changes onset time. It measures changed contact evolution after onset. Full restoration removes measured divergence. Reset/prefix produces the same reference.

Contact normal-impulse sums, contact geometry IDs/positions/distances, object final poses and robot configurations are retained per candidate in NPZ/JSON. Mixed-unit `trace_max_abs` combines time, state and force and is not a distance. No real-world force calibration or physical accuracy claim follows from a soft-contact simulation.

## Reproduction and evidence strength

Two geometry-feasibility seeds and two protocol-smoke seeds preceded the fixed confirmation. The smoke also had zero choice flips and was not used to tune a reversal. The new scene was not changed after its first successful contact setup. The fresh-process repeat matched **448 NPZ files / 1424 arrays bitwise**; model hash equality across processes is **True**. Runtime in the first confirmation was about 168.4 s. No larger run was launched for significance.

The earlier independent free-sliding study used different scenes, actions and endpoints. It is outside this contact-only release; no pooled comparison is made.

Classification: **INCREMENTAL EMPIRICAL FINDING**, with a negative decision endpoint and known underlying mechanics. This is sufficient for a carefully scoped Technical Note and research discussion. Next question: which contact/controller regimes and candidate score margins allow transient restoration errors to alter decisions? That question can be discussed now without claiming a new algorithm or requiring an endless search for positive results.
