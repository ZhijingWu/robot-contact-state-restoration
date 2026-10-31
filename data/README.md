# Numeric data inventory

- `raw/confirm/*.npz`: 448 compressed NumPy archives with 1,424 finite numeric arrays, loaded with `allow_pickle=False`. They contain checkpoint state, shared-prefix dynamics, candidate state/contact traces and scalar scores. No Python objects, images, videos, text instructions, collector identities or credentials are included. See [trace schema](../docs/trace_schema.md).
- `scene/robot.h5`: two numeric HDF5 datasets: the independent 80-sample robot/gripper target tape. Its initial seven arm coordinates are derived from the credited DROID action frame 40. Subsequent closure/sweep commands are independent.
- `scene/cube.obj`: generated primitive box geometry, not an upstream or DROID object mesh.
- `scene/scale.npy`: numeric unit scale.
- `scene/poses.npz`: independently specified box poses/frame indices.
- `scene/extrinsics.npz`, `scene/intrinsics.npz`: numeric initialization placeholders, not measured camera calibration.
- `scene/scene_spec.json`: independent box/ground configuration.

The Technical Note PDF is the only publication document binary. No compiled MJB, shared library, executable or third-party model is bundled. Every released file except the self-referential checksum list is hashed in `provenance/release_sha256.json`.

See [source attribution and terms](ATTRIBUTION.md) before reusing DROID-derived numeric material.
