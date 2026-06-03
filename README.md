# Eciwise IA - Predicción de rendimiento estudiantil

Servicio con arquitectura hexagonal en FastAPI que predice el rendimiento de un estudiante usando un ensamble de **XGBoost + LightGBM + CatBoost** entrenado con el CSV de entrada. Cada predicción se registra en PostgreSQL junto con el nombre del estudiante.

> **Nota de diagramas**: los diagramas en Mermaid son vectoriales. En VS Code (Markdown Preview) y en GitHub puedes hacer zoom y pan para ver el detalle con claridad.

## Arquitectura (hexagonal)

```mermaid
%%{init: {"theme": "base", "flowchart": {"curve": "linear"}} }%%
flowchart LR
  subgraph Inbound[Adapters de entrada]
    API[FastAPI /predictions]
  end

  subgraph Application[Aplicación]
    UseCase[PredictionService]
  end

  subgraph Domain[Dominio]
    Ports[Puertos\nModelPredictor\nPredictionRepository]
  end

  subgraph Outbound[Adapters de salida]
    ML[EnsemblePredictor\nXGBoost + LightGBM + CatBoost]
    DB[(PostgreSQL)]
  end

  API --> UseCase --> Ports
  Ports --> ML
  Ports --> DB
```

## Diagrama de componentes

```mermaid
%%{init: {"theme": "base", "flowchart": {"curve": "linear"}} }%%
flowchart TB
  subgraph API
    Router[Routes]
    Schemas[Request/Response Schemas]
  end

  subgraph Application
    Service[PredictionService]
  end

  subgraph ML
    Trainer[Training Pipeline]
    Ensemble[Ensemble Predictor]
    Artifacts[(Model Artifacts)]
  end

  subgraph Persistence
    Repo[Prediction Repository]
    Table[(predictions)]
  end

  Schemas --> Router --> Service
  Service --> Ensemble
  Service --> Repo
  Trainer --> Artifacts
  Ensemble --> Artifacts
  Repo --> Table
```

## Flujo de predicción

```mermaid
%%{init: {"theme": "base"}}%%
sequenceDiagram
  participant Client
  participant API
  participant Service
  participant Model
  participant DB

  Client->>API: POST /predictions
  API->>Service: valida y mapea datos
  Service->>Model: predict(features)
  Model-->>Service: GradeClass
  Service->>DB: INSERT prediction
  Service-->>API: respuesta
  API-->>Client: {name, prediction}
```

## Requisitos

- Python 3.10+
- PostgreSQL 14+ (opcional si quieres persistencia)

## Configuración rápida

1. Crear entorno virtual e instalar dependencias:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Variables de entorno (ejemplo en `.env.example`):
   ```bash
   export DB_ENABLED="true"
   export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/eciwise"
   export DATASET_PATH="./ .csv"
   export ARTIFACTS_DIR="artifacts"
   export AUTO_TRAIN="false"
   ```

3. Entrenar modelos:
   ```bash
   python scripts/train.py
   ```
   Si prefieres entrenar automáticamente al iniciar la API, define `AUTO_TRAIN=true`.

4. Ejecutar API:
   ```bash
   uvicorn app.main:app --reload
   ```

> Si quieres ejecutar sin base de datos, define `DB_ENABLED=false` y el servicio no intentará guardar predicciones.

## Dataset

El CSV debe contener las columnas:

```
Age, Gender, Ethnicity, ParentalEducation, StudyTimeWeekly, Absences, Tutoring,
ParentalSupport, Extracurricular, Sports, Music, Volunteering, GPA, GradeClass
```

> El archivo provisto en este repositorio se llama **`" .csv"`** (tiene un espacio inicial). Por defecto `DATASET_PATH` apunta a ese nombre.

## Endpoint de predicción

**POST** `/predictions`

```json
{
  "student_name": "Andrea Ruiz",
  "age": 17,
  "gender": 1,
  "ethnicity": 2,
  "parental_education": 3,
  "study_time_weekly": 12,
  "absences": 3,
  "tutoring": 0,
  "parental_support": 3,
  "extracurricular": 1,
  "sports": 1,
  "music": 0,
  "volunteering": 1,
  "gpa": 3.4
}
```

Respuesta:
```json
{
  "student_name": "Andrea Ruiz",
  "prediction": "B"
}
```

**Nota**: GPA NO se requiere en la entrada ya que es información posterior. El modelo predice basándose en características previas (hábitos, apoyo parental, actividades).

## Logging

Cada predicción se registra en logs con el nombre del estudiante y la clase predicha para facilitar depuración.

## Métricas del modelo

Al entrenar, se generan métricas completas por modelo en `artifacts/metadata.json`, incluyendo accuracy, balanced accuracy, precision/recall/F1 (micro, macro y weighted), log loss, matriz de confusión y classification report por clase.

## Esquema de base de datos

El archivo `schema.sql` incluye el esquema necesario para la tabla `predictions`.

## Estructura del proyecto

```
app/
  adapters/
    db/
    ml/
    web/
  application/
  domain/
  infrastructure/
scripts/
artifacts/
```
