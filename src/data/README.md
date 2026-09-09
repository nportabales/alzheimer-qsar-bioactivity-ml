# Dataset Information

The bioactivity data used in this project is sourced from the **ChEMBL Database**:
- **Target:** Human Acetylcholinesterase (AChE) — Target ID: `CHEMBL220`[cite: 36]
- **Assay Type:** Potency measurement (`Standard Type == 'IC50'`)[cite: 36]
- **Measurement Units:** Nanomolar (`Standard Units == 'nM'`)[cite: 36]
- **Initial raw entries:** 9,731 chemical records[cite: 36]

### Data File
Place your downloaded and curated dataset in this directory with the path:
`data/datos_alzheimer.csv`

The CSV is expected to contain the following core columns:
- `Molecule ChEMBL ID`
- `Smiles`
- `Standard Type`
- `Standard Value`
- `Standard Units`
