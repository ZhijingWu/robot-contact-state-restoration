# Robot-Contact State Restoration

**Incomplete simulator-state restoration changed contact dynamics, but changed no command choices in 16 paired seeds (0/16).** This repository reports a bounded negative decision-impact result, with the exact experimental scripts and numeric evidence.

This is **independent research by Zhijing Wu**. Official [Agentic Real2Sim](https://github.com/agentic-real2sim/agentic_real2sim) simulation components were reused at commit `880389bda289d2e78154c73ae1b6d23b7a650557`; the contact scene was independently constructed. See the [upstream paper](https://arxiv.org/abs/2607.19190) and [project](https://agentic-real2sim.github.io/). No endorsement, collaboration or authorship by the upstream authors or UCLA is implied.

## What was tested

A Franka/Robotiq simulated robot contacts an independently specified box. Sixteen paired seeds (3000–3015) perturb initial box XY by at most 1 mm per axis. After a shared 100-frame contact prefix, three scripted joint-1 continuations are compared over 36 frames. Lower terminal XY target distance is better. No external object force is applied.

MuJoCo 3.17.0 runs ten 1/600 s physics steps per 60 Hz command frame. Full restoration uses `mjSTATE_INTEGRATION` (mask 16383; 247 values in this model), with matched model/configuration, command tape and wrapper frame. Nine restoration conditions include fresh initialization, reset/prefix, full reload, independent fork and deliberate state omissions.

## Verified result

| Endpoint | Recorded value |
| --- | ---: |
| Paired seeds | 16 |
| Position-only command-choice flips | **0/16** |
| Maximum position-coordinate deviation | **0.7038 mm** |
| Maximum action-score perturbation | **0.03389 mm** |
| Minimum reference best/second-best score margin | **12.356 mm** |
| Observed reference-scored selection regret | **0 m** |
| Complete-state reset/reload/fork controls | **Exact agreement** |
| Independent-process repeat | **448 NPZ / 1,424 arrays byte-identical** |

State omissions produced measurable physical deviations. Every seed nevertheless retained the hold command as its best candidate. The coordinate discrepancy is the largest absolute XYZ component difference over all recorded candidate substeps, not Euclidean displacement. The score perturbation is an absolute change in terminal XY target distance. Regret scores the partially restored model's selected command using the reference costs.

The independent-process reproducibility claim was verified on the recorded platform. All confirmation arrays are included; the separate historical repeat is represented by its per-array dtype, shape and SHA-256 byte hashes to avoid distributing duplicate payloads. A new repeat can be run with the commands below. File/container bytes and cross-platform bitwise determinism are not claimed.

## Scientific boundaries

- This is an independent simulation study using official components and an independently constructed contact scene.
- It is **not a native converted Real2Sim episode reproduction** and **not a physical robot experiment**.
- No original framework defect or novel algorithm is claimed. Complete-state serialization is an established mechanism; the contribution is an incremental empirical finding and research discussion.
- The initial arm posture comes from a credited DROID numeric trajectory. The box, camera placeholders and subsequent scripted command tape are independent, not reconstructed correspondences to that episode.
- One geometry, narrow perturbations and three scripted candidates with well-separated scores were tested. No learned policy or physical parameter calibration was evaluated.
- Contact already exists at the checkpoint; the experiment concerns its subsequent evolution. Zero flips in 16 seeds does not establish universal equivalence.

## Read the study

- [Two-page Technical Note (PDF)](docs/technical_note.pdf) and [editable text](docs/technical_note.md)
- [Methodology](docs/methodology.md), [state contract](docs/state_contract.md), [trace schema](docs/trace_schema.md)
- [Limitations and claims](docs/limitations_and_claims.md), [historical contact results](docs/historical_contact_results.md), [native-episode boundary](docs/native_episode_status.md)
- [Aggregate JSON](results/aggregate.json), [per-seed JSON](results/per_seed.json), [per-seed CSV](results/per_seed.csv)
- [License and data audit](LICENSE_AND_DATA_AUDIT.md), [data attribution](data/ATTRIBUTION.md)

## Recompute from included evidence

The original platform used Python 3.13.5, NumPy 2.1.3 and MuJoCo 3.17.0. Only NumPy is needed for analysis; no GPU, API key, model checkpoint or paid service is needed.

```sh
python -m venv .venv
# Activate .venv using your platform's normal activation command.
python -m pip install numpy==2.1.3
python scripts/verify_release.py
python scripts/analyze.py --out .runs/analysis
```

Use a fresh `--out` directory. Analysis checks all nine conditions, recomputes the scores from raw arrays, checks exact complete-state controls, and compares all 1,424 confirmation-array byte hashes with the independently recorded repeat.

## Rerun the frozen simulation

Review [external dependency terms](LICENSE_AND_DATA_AUDIT.md) first. Upstream code and robot assets are **not bundled**. The acquisition command downloads 102 pinned, hash-verified files (~37.7 MB) directly from upstream; acquisition itself executes none of that code. Agentic Real2Sim has no repository-level license at the inspected commit. This repository does not grant permission to reuse or redistribute it.

```sh
python -m pip install -r requirements.txt
python scripts/fetch_upstream.py
python scripts/run_experiment.py --workspace .runs/reproduce --stage confirm
python scripts/run_experiment.py --workspace .runs/reproduce --stage repeat
python scripts/analyze.py --raw .runs/reproduce/outputs/jiang-yip-native-validation/JIANG_RAW_RESULTS/confirm --out .runs/recomputed
```

The last command intentionally requires the recorded exact repeat-array hashes. Numerical differences on another platform should be reported, not silently relabeled identical. Windows users can use PowerShell and the same Python commands. Original direct dependency versions and platform details are in [recorded_environment.json](configs/recorded_environment.json); this is not a complete transitive lockfile. See [reproduction instructions](docs/reproduction.md) for expected artifacts, archived code boundaries and repeat verification.

## Licensing and citation

A repository-wide license remains **unresolved**. No MIT/Apache/open-source license is asserted for the original research code or writing. [LICENSE_PROPOSAL.md](LICENSE_PROPOSAL.md) records a proposed future scope; it grants no rights. DROID-derived numeric material retains the attribution and CC BY 4.0 source terms identified in [data/ATTRIBUTION.md](data/ATTRIBUTION.md). Robot notices and dependencies retain their own external terms.

Use [CITATION.cff](CITATION.cff) to cite this independent study, and cite Agentic Real2Sim and DROID separately when using their work.

**Open question:** Under which contact, controller, and candidate-score-margin regimes does restoration error become decision-relevant?
