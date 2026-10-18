# API FastAPI que recibe una declaración de importación y consulta el endpoint aduanas-fraude de Databricks
# Proyecto final MLOps · Dataset Kaggle: Bangladesh Customs Fraud Detection
import os
from typing import Optional

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

# Credenciales: se inyectan como variables de entorno en Azure (nunca escritas en el código)
DATABRICKS_URL = os.getenv("DATABRICKS_URL")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

app = FastAPI(
    title="API Fraude Aduanero",
    description="Predice si una declaración de importación es probable fraude (1) o no (0)",
)

# Permite que un frontend en otro dominio llame a la API
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# Las 8 columnas de la firma del modelo registrado en el NB02 — ni más ni menos.
# Los nombres son los del dataset original. Las variables derivadas (exceso de peso,
# subvaloración, triangulación…) las calcula el propio modelo con aduanas_features.py.
class Declaracion(BaseModel):
    model_config = ConfigDict(extra="forbid")  # rechaza (422) cualquier campo que no sea de la firma

    Port_of_Entry: str = Field(..., min_length=1, description="Puerto de entrada")
    Declared_HS_Code: int = Field(..., ge=0, le=99999999, description="Partida arancelaria declarada")
    Country_of_Origin: Optional[str] = Field(None, description="País de origen (opcional)")
    Country_of_Departure: Optional[str] = Field(None, description="País de salida (opcional)")
    Declared_Weight_KG: float = Field(..., gt=0, description="Peso declarado en kg")
    Declared_Value_BDT: float = Field(..., gt=0, description="Valor declarado en takas (BDT)")
    Scanned_Weight_KG: Optional[float] = Field(None, gt=0, description="Peso escaneado en kg (vacío si no hubo escaneo)")
    TTI_Rate: float = Field(..., ge=0, le=1000, description="Tasa arancelaria total (%)")


@app.get("/health")
def health():
    # Verifica que la API está viva y que tiene configuradas las credenciales
    return {"status": "ok", "databricks_configurado": bool(DATABRICKS_URL and DATABRICKS_TOKEN)}


@app.post("/predecir")
def predecir(dec: Declaracion):
    if not (DATABRICKS_URL and DATABRICKS_TOKEN):
        raise HTTPException(status_code=500, detail="Faltan DATABRICKS_URL o DATABRICKS_TOKEN")

    # Databricks exige el formato dataframe_records
    payload = {"dataframe_records": [dec.model_dump()]}

    try:
        r = requests.post(
            DATABRICKS_URL,
            headers={"Authorization": f"Bearer {DATABRICKS_TOKEN}"},
            json=payload,
            timeout=230,  # margen para el arranque en frío (Container Apps corta a los 240 s)
        )
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Databricks tardó demasiado (arranque en frío). Intente de nuevo.")

    if r.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Error de Databricks: {r.text}")

    pred = int(r.json()["predictions"][0])  # 1 = probable fraude, 0 = sin indicios
    return {
        "predictions": [pred],
        "resultado": "Probable fraude 🚩" if pred == 1 else "Sin indicios de fraude ✅",
    }
