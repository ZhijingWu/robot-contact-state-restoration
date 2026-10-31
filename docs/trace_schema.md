# Raw trace schema

All arrays use float64 unless generated as native image float32/uint8. Indices below are zero-based. `mjSTATE_INTEGRATION` layout is determined by the pinned API and component sizes in `model_audit.json`; use the API rather than assuming offsets in its 247-value array.

## Contact candidate NPZ

`trace` has one row per 1/600 s physics substep, 360 rows for each 36-frame candidate.

| Columns | Quantity | Unit |
| --- | --- | --- |
| 0 | MuJoCo time after the step | s |
| 1:23 | qpos, 22 elements | Robot joint rad; object XYZ m and wxyz quaternion |
| 1:8 | First seven arm qpos | rad |
| 16:19 | Object XYZ | m |
| 19:23 | Object quaternion wxyz | unitless |
| 23:44 | qvel, 21 elements | Robot rad/s; free-body linear m/s and angular rad/s |
| 44 | Number of robot-object contacts in that substep | count |
| 45 | Sum of robot-object contact normal forces | N |

`contacts` is variable-length, ten columns: substep index, geom1 ID, geom2 ID, signed contact distance (m), contact-frame force components 0–2 (N), and world contact position XYZ (m). IDs resolve through `model_audit.json`; only robot-object contacts are included. Data are read after `mj_step`, with the solved constraint/contact configuration of that step. Sum normal-force×dt is a scalar normal-impulse sum, not net Cartesian impulse.

`score` is terminal Euclidean object XY error in metres. The candidate indices 0/1/2 correspond to joint-1 increments -0.06/0/+0.06 rad. Checkpoint NPZ saves integration state, qpos, qvel, exact target, frame 100, initial XY jitter, common prefix trace and prefix contact array. Robot final configuration and object final pose can be read from the final trace row. `geometry_inspection.json` records FK inspection, not a native object reconstruction.

