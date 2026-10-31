# Reproduction instructions and scope

Run commands from the repository root. Create a virtual environment using the recorded Python 3.13.5 where practical. Analysis needs only `numpy==2.1.3`; simulation additionally needs the versions in `requirements.txt`. The original Windows platform and broader original environment are recorded in `configs/recorded_environment.json`. Python wheels and transitive dependencies are not fully locked; no other platform's exact behavior is asserted.

## Evidence-only path

Run `python scripts/verify_release.py`, then `python scripts/analyze.py --out .runs/analysis`. Use a new output directory. Expect 144 seed-condition rows, 0/16 qpos-only flips, maximum coordinate discrepancy 0.0007038157109165166 m, maximum score perturbation 0.00003388700127388011 m, minimum reference candidate margin 0.012356339325469942 m, exact complete-state controls and 1,424 matching repeat-array hashes. This is recalculation from stored traces, not new simulation.

## Simulation path

Review `LICENSE_AND_DATA_AUDIT.md`. Run `python scripts/fetch_upstream.py` to acquire the pinned external code/assets into ignored `.cache/ar2s`. `--verify-only` checks an existing download without network writes. Nothing is executed by acquisition. External notices are retained in that download. No full visual pipeline, CUDA toolkit, VLM, API key, DROID shard or raw image/video dataset is needed.

Run `python scripts/run_experiment.py --workspace .runs/reproduce --stage confirm`, followed by the same command with `--stage repeat`. The wrapper copies the exact original scripts, seven scene inputs and verified external files to an isolated layout. It refuses to overwrite an existing stage. The original source expects a relative `work/native` and `outputs/jiang-yip-native-validation` layout; those names are historical portable layout labels, not machine paths.

Each stage produces 448 NPZ files, a protocol, measurement/summary JSON, a model audit and a locally compiled model. Compare numeric arrays, dtype and shapes rather than NPZ ZIP metadata. To check a fresh stage against the historical byte hashes, run:

```sh
python scripts/analyze.py --raw .runs/reproduce/outputs/jiang-yip-native-validation/JIANG_RAW_RESULTS/confirm --out .runs/fresh-analysis
python scripts/analyze.py --raw .runs/reproduce/outputs/jiang-yip-native-validation/JIANG_RAW_RESULTS/repeat --out .runs/repeat-analysis
```

These checks intentionally fail on byte differences rather than silently applying an undocumented tolerance. Report the platform, dependency versions and observed metric differences if they fail.

## Archived versus portable code

`experiments/original/contact_experiment.py` and `contact_common.py` are byte-identical to the executed scripts. `contact_feasibility.py` is also preserved exactly as scene/tape construction evidence. It is **not** the normal reproduction entry point: it runs exploratory geometry probes and expects the original numeric DROID export. The exact already-generated scene inputs are included, so no exploratory run is required. Its independent target tape uses the credited zero-based DROID action frame 40.

The historical mixed Jiang/Yip analyzer depended on both research tracks and private preservation guards. It is not bundled or misrepresented as a portable entry point. `scripts/analyze.py` is a new contact-only publication analysis that recalculates the reported quantities directly from the frozen raw evidence. It does not change any experimental result. The release audit compares these calculations with the original records.

`data/raw/confirm` contains the full 448-file numeric confirmation payload (~195.7 MB). To avoid duplicate data, the historical repeat payload is represented by `provenance/historical_repeat_arrays.json`: 1,424 C-order byte hashes, each with dtype and shape, independently computed from the separately executed repeat. Original MJB files, third-party code/assets, raw DROID recordings, private logs and other research tracks are excluded. All delivered binary formats are explained in `data/README.md`.
