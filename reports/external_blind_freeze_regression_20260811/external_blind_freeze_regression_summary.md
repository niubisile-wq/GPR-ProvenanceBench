# External Blind Freeze Regression

Synthetic regression fixture for the blind external intake/freeze/unlock path.
This is not real blind external evidence.

- synthetic rows: 240
- prediction precedes unlock: True
- prediction SHA-256 at freeze: `11035c3b71dd31b488aaaf1bbf7ca54750a611112b00468df934119217f5eb83`
- balanced accuracy after synthetic unlock: 0.7094
- shared train/synthetic source groups: 0

Boundary: TIGPR rows are visible local data. This proves the one-shot
prediction-freeze regression path, not the external validation result.
