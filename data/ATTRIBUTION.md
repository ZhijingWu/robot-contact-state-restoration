# DROID attribution and changes

Source: **Alexander Khazatsky, Karl Pertsch, Suraj Nair, et al. (2024), DROID: A Large-Scale In-the-Wild Robot Manipulation Dataset.** [Paper](https://arxiv.org/abs/2403.12945), [official dataset documentation](https://droid-dataset.github.io/droid/the-droid-dataset.html).

The paper explicitly states that the full DROID dataset is released under **Creative Commons Attribution 4.0 International (CC BY 4.0)**: [license](https://creativecommons.org/licenses/by/4.0/), [legal code](https://creativecommons.org/licenses/by/4.0/legalcode). This dataset statement, rather than the unrelated policy-code MIT license or a third-party mirror's card, is the basis for numeric source reuse. The checked paper hash is in `provenance/license_sources.json`.

Only the seven arm coordinates from zero-based frame 40 of a public raw trajectory initialize this independent study. The exact original object generation, source URL and trajectory checksum are in `provenance/droid_source.json`. The source is the RAIL successful trajectory recorded 2023-04-17 at 14:48:05. Original trajectory, imagery, video, episode/collector metadata and the full flat export are not redistributed here.

Changes: an independently specified box, contact layout, camera placeholders, gripper closure, joint-1 sweep and continuation tape replace the original interaction. The published numeric target tape and simulation traces reflect those changes. They are not native DROID contact labels, reconstructed DROID objects, or measured physical robot outcomes. Credit to DROID does not imply endorsement or collaboration.

Source rights under CC BY 4.0 remain applicable to DROID-derived numeric material. No blanket repository license or permission over upstream simulator code/assets is asserted. See `LICENSE_AND_DATA_AUDIT.md` for the unresolved original-material license and external dependencies.
