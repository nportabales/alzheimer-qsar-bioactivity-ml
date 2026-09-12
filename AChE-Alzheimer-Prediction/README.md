# Predicting Acetylcholinesterase (AChE) Inhibitors for Alzheimer's Disease from Chemical Structure

Proyecto de *machine learning* aplicado a *drug discovery*: predicción de la actividad inhibidora de la Acetilcolinesterasa (AChE) — diana terapéutica clave en el Alzheimer — a partir de la estructura química de los compuestos.

**Autores:** Dora Díaz, Marwan El Saabi, Juan Jiménez, Nerea Portabales

---

## Resumen

Este proyecto se centra en el desarrollo de una herramienta bioinformática para el descubrimiento de fármacos contra el Alzheimer, dirigida específicamente a la inhibición de la enzima Acetilcolinesterasa (AChE). Para ello, extrajimos datos experimentales de bioactividad de la base de datos ChEMBL y aplicamos un riguroso proceso de curación basado en valores de IC50, definiendo clases activas e inactivas según criterios bibliográficos recientes. Posteriormente, transformamos las estructuras químicas en descriptores numéricos mediante Morgan Fingerprints, generando un conjunto de datos balanceado y apto para el entrenamiento de algoritmos de Machine Learning.

En la fase de modelado, implementamos y comparamos cuatro clasificadores distintos (KNN, SVM, XGBoost y Random Forest) utilizando una estrategia de validación cruzada estratificada de 5 pliegues para garantizar la robustez estadística de los resultados. El modelo Random Forest demostró ser el más eficaz, alcanzando una precisión cercana al 85%, lo que replica y valida los resultados del estado del arte científico. Esto confirma que nuestra metodología es capaz de identificar patrones estructurales complejos determinantes para la actividad biológica sin depender de software propietario.

Finalmente, para demostrar la aplicabilidad clínica del modelo más allá de las métricas teóricas, realizamos un estudio de reposicionamiento de fármacos in silico utilizando compuestos aprobados por la FDA y validados en PubChem. El sistema identificó correctamente el tratamiento estándar, Donepezilo, como activo, y descartó fármacos no relacionados como la Aspirina, demostrando una alta especificidad. Esta validación externa confirma que la herramienta desarrollada no solo es precisa matemáticamente, sino que posee una capacidad real para el cribado virtual de nuevas terapias neurodegenerativas.

---

## 1. Motivación

El cribado (*screening*) físico de millones de candidatos moleculares es lento y costoso. Este proyecto simula un flujo de trabajo de laboratorio farmacéutico moderno ("*in silico*") para predecir, de forma instantánea, si un compuesto es o no un inhibidor de AChE a partir únicamente de su estructura química (SMILES).

- **Hipótesis:** es posible usar Machine Learning para predecir la actividad biológica a partir de la estructura química.
- **Pipeline:** Data Mining (ChEMBL) → Estrategia de etiquetado → Traducción química (fingerprints) → Entrenamiento de modelos.

## 2. Datos

- **Fuente:** [ChEMBL](https://www.ebi.ac.uk/chembl/), target *Acetylcholinesterase (Human)* — [CHEMBL220](https://www.ebi.ac.uk/chembl/explore/target/CHEMBL220).
- **Filtrado:** se retuvieron únicamente ensayos IC50 en unidades nanomolares (nM).
- **Etiquetado (clases):**
  - **Activo (1):** IC50 ≤ 1000 nM
  - **Inactivo (0):** IC50 ≥ 10000 nM
  - Se descartó la "zona gris" (1000–10000 nM) para evitar ruido en el modelo.
- **Balanceo:** *undersampling* aleatorio de la clase mayoritaria para obtener un dataset 50/50.

| Etapa | Nº de compuestos |
|---|---|
| Registros brutos (ChEMBL 2025) | 9,731 |
| Tras filtro IC50 + nM | 8,372 |
| Tras eliminar zona gris | 6,366 |
| Tras balanceo (2,480 por clase) | 4,960 |

> ⚠️ El CSV original no está incluido en este repositorio (ver [`data/README.md`](data/README.md) para instrucciones de cómo regenerarlo desde ChEMBL).

## 3. Ingeniería de características

- **Fingerprints de Morgan (ECFP4)** vía RDKit: cada molécula (SMILES) se traduce a un vector binario de 1024 bits.
- **Selección de features:** ranking ANOVA F-score, con análisis de sensibilidad sobre distintos valores de *k* (20, 50, 300, 700 y todas). Se seleccionó **k = 300**, el punto donde el rendimiento se estabiliza (mismo accuracy que con 700+ features, pero con entrenamiento más rápido y modelo más simple e interpretable).

## 4. Modelos y validación

Se compararon 4 algoritmos con validación cruzada estratificada de 5 folds:

- K-Nearest Neighbors (KNN)
- Support Vector Machine (SVM, kernel RBF)
- Random Forest
- XGBoost

**Resultado:** Random Forest obtuvo el mayor accuracy medio y la mayor estabilidad, además de la menor tasa de falsos negativos (crítico para no descartar fármacos potenciales) y un AUC de **0.96** en la curva ROC.

## 5. Validación externa

Se reentrenó el Random Forest sobre el dataset balanceado completo (300 features) y se incorporó un detector de *leakage* para distinguir memorización de predicción real:

- **Controles positivos:** Donepezilo (0.98) y Galantamina (0.78) — correctamente identificados como activos y detectados como parte del dataset de entrenamiento.
- **Control negativo:** Aspirina, correctamente predicha como nueva e inactiva (0.18).
- **Candidatos experimentales rechazados correctamente** (Vignaux et al.): Serdemetán (0.28), Vesatolimod (0.35).
- **Nueva predicción activa:** Demecarium (0.6650) — inhibidor potente ausente del set de entrenamiento.

## 6. Limitaciones

- **Sesgo de prevalencia:** el dataset balanceado 50/50 optimiza el aprendizaje pero infla la confianza del modelo respecto a cribados reales, donde los compuestos activos son <1%. Sería necesaria una calibración antes de cualquier despliegue real.
- **Caso Tacrina:** un falso negativo con un derivado de Tacrina reveló que los fingerprints de Morgan (2D) no capturan la estructura 3D de andamiajes híbridos. Trabajo futuro: incorporar descriptores 3D para ampliar el dominio de aplicabilidad del modelo.

## 7. Conclusiones

Random Forest (k=300) predice la inhibición de AChE con >90% de accuracy, validado científicamente mediante curación rigurosa de datos, balanceo de clases y salvaguardas anti-*leakage*. El resultado es un motor de *Targeted Virtual Screening* para *drug discovery* que identificó correctamente un nuevo compuesto activo (Demecarium) y rechazó candidatos débiles.

---

## Estructura del repositorio

```
AChE-Alzheimer-Prediction/
├── README.md                  <- este archivo
├── requirements.txt
├── src/
│   └── train_model.py         <- pipeline completo (carga, limpieza, features, modelos)
├── data/
│   ├── README.md              <- cómo regenerar el dataset desde ChEMBL
│   └── raw/                   <- (vacío) coloca aquí datos_alzheimer.csv
├── docs/
│   └── references/            <- PDFs de los 2 artículos de referencia
├── results/                   <- gráficas generadas (accuracy, ROC, matriz de confusión)
└── presentation/
    └── PRESENTACION_FINAL.pptx
```

## Cómo ejecutar

```bash
pip install -r requirements.txt
python src/train_model.py
```

## Referencias

1. Vignaux, P. A.; Lane, T. R.; Urbina, F.; Gerlach, J.; Puhl, A. C.; Snyder, S. H.; Ekins, S. **Validation of Acetylcholinesterase Inhibition Machine Learning Models for Multiple Species.** *Chem. Res. Toxicol.* **2023**, *36*, 188–201. [DOI: 10.1021/acs.chemrestox.2c00283](https://doi.org/10.1021/acs.chemrestox.2c00283)
   - Fuente de la estrategia de validación externa (controles positivos/negativos): los compuestos Serdemetán y Vesatolimod usados como candidatos débiles en la validación externa (slide 21) proceden de la Tabla 8 de este artículo.
2. Sandhu, H.; Kumar, R. N.; Garg, P. **Machine learning-based modeling to predict inhibitors of acetylcholinesterase.** *Molecular Diversity* **2022**, *26*, 331–340. [DOI: 10.1007/s11030-021-10223-5](https://doi.org/10.1007/s11030-021-10223-5)
   - Referencia para la comparación de algoritmos (SVM, k-NN, Random Forest) y el umbral de actividad de 1 µM/1000 nM usado para la clasificación activo/inactivo.

Los PDFs de ambos artículos están disponibles en [`docs/references/`](docs/references/).

## Próximos pasos (hacia el TFG/thesis)

- [x] Recuperar el artículo(s) de referencia.
- [ ] Recuperar el Excel/CSV original y añadirlo a `data/`.
- [ ] Incorporar descriptores 3D para mejorar la detección de andamiajes híbridos (caso Tacrina).
- [ ] Calibrar las probabilidades del modelo para escenarios de prevalencia real (<1% de activos).
- [ ] Ampliar la validación externa con más compuestos de referencia.
