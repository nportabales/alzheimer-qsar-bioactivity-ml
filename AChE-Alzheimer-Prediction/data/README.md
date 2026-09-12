# Datos

El CSV original (`datos_alzheimer.csv`) usado para entrenar los modelos no está incluido en este repositorio (se perdió el Excel/CSV modificado). Para regenerarlo:

1. Ve a la base de datos [ChEMBL](https://www.ebi.ac.uk/chembl/).
2. Busca el target **Acetylcholinesterase (Human)** → ID **[CHEMBL220](https://www.ebi.ac.uk/chembl/explore/target/CHEMBL220)**.
3. Desde la página del target, exporta todos los **bioactivity data points** asociados (botón "Bioactivities" → export a CSV/TSV).
4. Guarda el export como `data/raw/datos_alzheimer.csv`.
5. El script `src/train_model.py` aplica automáticamente los siguientes filtros (documentados también en la presentación, slides 6-9):
   - `Standard Type == 'IC50'`
   - `Standard Units == 'nM'`
   - Elimina filas sin `Smiles` o `Standard Value`
   - Clasifica: **Activo** si IC50 ≤ 1000 nM, **Inactivo** si IC50 ≥ 10000 nM, descarta la "zona gris" (1000-10000 nM)
   - Balanceo por undersampling de la clase mayoritaria

> Nota: según la presentación, el dataset bruto de partida tenía **9,731 registros**, quedando **8,372** tras el filtro IC50/nM y **6,366** tras eliminar la zona gris ambigua.

## Artículo(s) de referencia

Ya recuperados — ver [`../docs/references/`](../docs/references/) y la sección de Referencias en el README principal:

1. Vignaux et al. (2023) — *Validation of Acetylcholinesterase Inhibition Machine Learning Models for Multiple Species*. Chem. Res. Toxicol. 36, 188–201.
2. Sandhu et al. (2022) — *Machine learning-based modeling to predict inhibitors of acetylcholinesterase*. Molecular Diversity 26, 331–340.
