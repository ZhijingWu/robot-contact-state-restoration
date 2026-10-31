# License and data audit

Audit date: 31 October 2026. Scope: every file in this independent contact-study release; external runtime dependencies are distinguished from redistributed content.

| Material | Finding | Release decision |
| --- | --- | --- |
| Original experiment wrappers, analysis and writing | Owner-authored independent research; no approved repository-wide license found | Publish with owner authorization; keep blanket license unresolved in `LICENSE_PROPOSAL.md` |
| Agentic Real2Sim simulator source | GitHub license field is null; no root LICENSE/COPYING/NOTICE at pinned commit | **Not redistributed**; immutable URLs/checksums only; dependency access is not a license grant |
| Franka Panda robot description/meshes | Asset-level Apache-2.0 notice | **Not bundled**; fetched externally with its original notice |
| Robotiq 2F-85 description/meshes | Asset-level BSD-2-Clause, ROS-Industrial notice | **Not bundled**; fetched externally with its original notice |
| DROID source numeric posture | Full-dataset CC BY 4.0 statement verified in DROID paper | Derived numeric tape/simulation traces published with attribution, source, license link and change notice |
| Original DROID raw trajectory/flat export | Source terms identified; full payload unnecessary | **Excluded**; exact source URL/hash retained |
| DROID video/images, collector and camera metadata | Not needed for this independent study | **Excluded** |
| Generated box and numeric camera/pose placeholders | Independently constructed primitive/numeric inputs | Included; explicitly not reconstructed or calibrated inputs |
| Compiled MuJoCo MJB | Embeds third-party robot geometry | **Excluded**; rebuild locally from acquired dependencies |
| NumPy/SciPy/h5py/MuJoCo/trimesh | External Python dependencies, exact direct versions recorded | Packages are not vendored or relicensed |

## Source verification

Pinned upstream commit: `880389bda289d2e78154c73ae1b6d23b7a650557`. The acquisition inventory covers 102 necessary code/robot-asset/notice files. Each cached file was checked against its pinned Git blob identity and SHA-256. No integrated visual-system third-party tree or unrelated asset is included in the publication payload. Relevant license URLs and the checked DROID paper hash are in `provenance/license_sources.json`.

The authoritative dataset license evidence is the DROID paper's statement about the **full dataset**. A Hugging Face card also listed CC BY 4.0, but the card alone was not treated as permission for every raw bucket object. Missing guessed bucket LICENSE and stale paper/catalog URLs were discovery failures, not proof that the data were unlicensed. The final citations use verified reachable sources.

## Privacy and content boundaries

The public payload contains original study scripts/docs, selected independent scene inputs, finite numeric simulation arrays, numeric results and provenance. It contains no original raw imagery/video, collector identity records, personal correspondence, CVs, credentials, access tokens, API keys, private experiment logs, local preservation baselines, machine-specific absolute paths or other research tracks. PDF metadata and extracted text were included in the scan. Numeric NPZ archives were inspected with pickling disabled; HDF5 contains only the two expected numeric datasets. Public repository URLs use HTTPS without embedded credentials.

Original historical workspaces and outreach materials remain unchanged. The publishing Git history starts from the audited staging payload; unrelated/private history is not imported.

## Remaining license limitation

The repository-wide original-material license is unresolved. This release is publicly inspectable research, not a claim that all content is open source. Source data attribution does not grant rights to the external simulator. Future downstream redistribution or relicensing needs a separately justified scope. This limitation does not justify inventing a blanket MIT/Apache license or copying unlicensed upstream software into the repository.
