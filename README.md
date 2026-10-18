# API de detección de fraude aduanero

Proyecto final de **MLOps y Analítica en la Nube** (Maestría en Ciencia de Datos, Universidad EAN) · José Carlos Ríos Castro.

API FastAPI que recibe una declaración de importación y consulta el modelo `workspace.aduanas.modelo_fraude_aduanero` (alias `@champion`, versión 3), servido en Databricks Model Serving por el endpoint `aduanas-fraude`. Se despliega en Azure Container Apps con GitHub Actions en cada push a `main`.

Dataset: [Bangladesh Customs Fraud Detection (Kaggle)](https://www.kaggle.com/datasets/mehreenrahman/customs-dataset).

**URL pública:** https://api-aduanas-fraude.nicefield-d64c8f5a.westus.azurecontainerapps.io

## Probar la API

Salud:

```bash
curl https://api-aduanas-fraude.nicefield-d64c8f5a.westus.azurecontainerapps.io/health
```

Predicción (Linux, macOS o Git Bash):

```bash
curl -X POST "https://api-aduanas-fraude.nicefield-d64c8f5a.westus.azurecontainerapps.io/predecir" \
  -H "Content-Type: application/json" \
  -d '{"Port_of_Entry":"Chittagong Sea Port","Declared_HS_Code":42021900,"Country_of_Origin":"CN","Country_of_Departure":"CN","Declared_Weight_KG":26.2,"Declared_Value_BDT":18683.96,"Scanned_Weight_KG":26.45,"TTI_Rate":89.32}'
```

Predicción (Windows CMD o Anaconda Prompt):

```
curl -X POST "https://api-aduanas-fraude.nicefield-d64c8f5a.westus.azurecontainerapps.io/predecir" -H "Content-Type: application/json" -d "{\"Port_of_Entry\":\"Chittagong Sea Port\",\"Declared_HS_Code\":42021900,\"Country_of_Origin\":\"CN\",\"Country_of_Departure\":\"CN\",\"Declared_Weight_KG\":26.2,\"Declared_Value_BDT\":18683.96,\"Scanned_Weight_KG\":26.45,\"TTI_Rate\":89.32}"
```

Respuesta esperada: `{"predictions":[1], ...}` (1 = probable fraude, 0 = sin indicios).

> La primera consulta tras un periodo sin uso tarda más por el arranque en frío del endpoint (unos 40 segundos en la prueba del 18 de octubre de 2026). Las siguientes responden en menos de un segundo.

## Variables de entrada

| Variable | Tipo | Descripción |
|---|---|---|
| `Port_of_Entry` | texto | Puerto de entrada |
| `Declared_HS_Code` | entero | Partida arancelaria declarada |
| `Country_of_Origin` | texto, opcional | País de origen |
| `Country_of_Departure` | texto, opcional | País de salida |
| `Declared_Weight_KG` | decimal > 0 | Peso declarado (kg) |
| `Declared_Value_BDT` | decimal > 0 | Valor declarado (takas) |
| `Scanned_Weight_KG` | decimal, opcional | Peso escaneado (kg) |
| `TTI_Rate` | decimal ≥ 0 | Carga tributaria total (%) |

## Archivos

- `main.py`: API FastAPI con validación Pydantic.
- `Dockerfile` y `requirements.txt`: imagen del contenedor.
- `.github/workflows/deploy.yml`: despliegue en 5 pasos con 5 secretos.
- `aduanas.html`: página web opcional para usar el modelo desde el navegador.
