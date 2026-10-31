# Velocity Omission Perturbs Contact Dynamics Without Changing Command Selection

Zhijing Wu, Sichuan University | Independent simulation study | 31 October 2026

## 1. Motivation

Physics-based world models need reliable simulation state, but a physically measurable error need not change a planner's decision. Agentic Real2Sim motivates checking that distinction at the model-to-decision interface. An earlier independent free-sliding test used external force candidates; it did not establish the consequence of restoration error during robot-object contact.

## 2. Research question

When a robot contacts an object, can an incomplete state restore alter contact evolution, object motion, or the selected candidate command? The experiment tests that question without assuming an upstream defect.

## 3. Experimental setup

We reused unchanged RobotSceneSim (commit 880389bda289d2e78154c73ae1b6d23b7a650557), MuJoCo 3.17.0, and the official Franka Panda / Robotiq 2F-85 assets. The contact scene is independently constructed: a 0.04 x 0.04 x 0.08 m, 0.05 kg box rests on a plane. A verified public DROID export supplies the initial arm posture; gripper closure and joint-1 sweep commands are independent. No external object force is applied.

Sixteen paired seeds (3000-3015) vary initial box XY within +/-1 mm. After a 100-frame contact prefix, three scripted joint-1 continuations ramp by -0.06, 0, or +0.06 rad over 36 frames. The score is terminal XY distance to a target 0.02 m along the positive tangential direction from the checkpoint. The controller runs at 60 Hz with ten 1/600 s physics steps per frame.

## 4. State-restoration conditions

Fresh initialization plus prefix is compared with supported reset plus the same prefix, full save/reload, a private-copy fork, and deliberate omissions. Full restore uses mjSTATE_INTEGRATION (mask 16383; 247 values here), under matched model/configuration, command tape and wrapper frame. Position-only restore keeps command timing matched. Additional omissions separate robot/gripper velocity, object velocity and warmstart; empty activation/history/plugin components are not counted as separate meaningful ablations.

## 5. Quantitative results

The complete-state controls agree exactly. Position-only restoration changes contact and motion, but every seed retains the same best command.

| Condition | Max coordinate deviation (mm) | Max score change (mm) | Choice flips |
| --- | ---: | ---: | ---: |
| Supported reset + prefix | 0 | 0 | 0/16 |
| Full integration save/reload | 0 | 0 | 0/16 |
| Independent private-copy fork | 0 | 0 | 0/16 |
| Position-only restoration | 0.7038 | 0.03389 | 0/16 |

Fresh-process repeat: 448 NPZ files / 1,424 arrays bitwise identical.

## 6. Interpretation

The maximum physical coordinate deviation is measurable, whereas the largest score perturbation is small relative to the minimum reference best-versus-second-best gap of 12.356 mm. All 16 seeds select the hold continuation, with zero observed reference-scored selection regret. Regret compares the reference cost of the partially restored model's chosen command with the minimum reference cost; it is not the difference between the two simulated trajectories' terminal errors.

Velocity omissions affect contact evolution after onset; the common prefix already contains contact. Robot/gripper-velocity omission has a larger motion effect than object-only omission in this scene. Warmstart omission is small but nonzero. Numerical divergence therefore does not establish decision failure. This is an incremental empirical finding / research discussion, not a state-restoration algorithm or evidence of an Agentic Real2Sim defect.

## 7. Limitations

This is an independent simulation study using official components. It is not a complete native converted Real2Sim episode, a physical robot experiment, or a learned-policy evaluation. The scene, object correspondence and command sequence are independent. Only one contact geometry, narrow initial perturbations and three scripted candidates with well-separated scores were tested. Soft-contact parameters are not calibrated to a physical object. Camera placeholders were not used to validate perception.

The full-state claim concerns the MuJoCo integration vector under an equal model. Model/configuration and external artifacts are separate parts of the contract. The wrapper frame is restored; its diagnostic time counter is reconstructed from frame and dt. Derived contacts are recomputed. Zero flips in 16 seeds does not prove general equivalence, and this contact task cannot be statistically pooled with the different earlier free-sliding scene.

## 8. Open research question

The controlled negative result can support a concrete discussion now. The next step is to identify regimes where restoration error crosses a decision margin, rather than tune this scene or expand its sample merely to obtain a reversal. A complete native converted episode would enable a more direct Real2Sim test.

Focused sources:
- [Agentic Real2Sim v5](https://arxiv.org/html/2607.19190v5)
- [GRIP v2, environment isolation](https://arxiv.org/html/2503.05020v2)
- [MuJoCo 3.17.0 simulation-state APIs](https://mujoco.readthedocs.io/en/3.17.0/programming/simulation.html)
- [ManiSkill state management](https://maniskill.readthedocs.io/en/latest/user_guide/tutorials/custom_tasks/advanced.html)
- [robosuite environment lifecycle](https://robosuite.ai/docs/modules/environments.html)

**Under which contact, controller, and candidate-score-margin regimes does restoration error become decision-relevant?**
