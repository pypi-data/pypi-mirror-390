# dsf_label_sdk/client.py
import os
import requests
import time
import logging
import json
import numpy as np
import uuid 
import io
from typing import Dict, List, Any, Optional, Union
from . import __version__
from .exceptions import ValidationError, APIError, JobTimeoutError
from .models import Config, EvaluationResult, Job
from google.cloud import storage # Mantener para tipos si es necesario, pero no se usa para auth aquí.

logger = logging.getLogger(__name__)

TIER_LIMITS = {
    'community': {'batch': 100},
    'professional': {'batch': 1000},
    'enterprise': {'batch': 10000}
}

class DSFLabelClient:
    # Usamos el dominio estable
    BASE_URL = 'https://dsf-label-api-new.vercel.app/api' 
    
    def __init__(self, license_key: Optional[str] = None, tier: str = 'community', timeout: int = 60):
        if tier not in TIER_LIMITS:
            raise ValidationError(f"Invalid tier: {tier}")
        
        self.license_key = license_key
        self.tier = tier
        self.timeout = timeout
        self.base_url = self.BASE_URL
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'DSF-Label-SDK/{__version__}'
        })
    
    # ⛔ FUNCIÓN ELIMINADA: _upload_to_gcs ya no existe. El cliente no necesita GCS. ⛔

    def _prepare_payload(self, data_points: List[Dict[str, Any]], config: Dict) -> Dict[str, Any]:
        """Prepara el JSON body para la API"""
        fields = list(config.keys())
        sample = data_points[0] if data_points else {}
        
        has_embedding_keys = any(f"embedding_{f}" in sample for f in fields)
        is_vector = any(isinstance(sample.get(f), (list, np.ndarray)) for f in fields if f in sample)
        
        if has_embedding_keys:
            embeddings_batch = [{f: dp[f"embedding_{f}"] for f in fields} for dp in data_points]
            prototypes_batch = [{f: dp[f"prototype_{f}"] for f in fields} for dp in data_points]
            logger.info("Format: embedding_X/prototype_X")
        elif is_vector:
            embeddings_batch = [{f: dp[f] for f in fields if f in dp} for dp in data_points]
            # Extraer prototipos de la config
            prototypes_batch = [{f: config[f].get('prototype', []) for f in fields} for _ in data_points]
            logger.info("Format: vectors")
        else:
            raise ValidationError("Unknown format. Expected embeddings with 'embedding_X' keys or vector fields")
        
        # Devolvemos el payload completo (que ahora llamaremos 'data')
        return {
            "embeddings_batch": embeddings_batch,
            "prototypes_batch": prototypes_batch,
            "config": config,
            "license_key": self.license_key,
            "tier": self.tier
        }

    def batch_evaluate(
        self, 
        data_points: List[Dict[str, Any]], 
        config: Optional[Union[Dict, Config]] = None,
        mode: str = 'sync'
    ) -> Union[List[EvaluationResult], Job]:
        """
        Envía un lote para evaluación.
        mode='sync': Espera y devuelve resultados (rápido, pero con timeouts).
        mode='async': Envía el payload pesado al Gateway (/api/enqueue) para 
                      procesamiento asíncrono vía GCS, evitando timeouts y el error 413.
        """
        
        # Convertir config si es instancia de Config
        if isinstance(config, Config):
            config = config.to_dict()

        # Validar límites del tier (solo para modo síncrono)
        batch_limit = TIER_LIMITS[self.tier]['batch']
        if len(data_points) > batch_limit and mode == 'sync':
            raise ValidationError(
                f"Batch ({len(data_points)}) exceeds {self.tier} limit for sync mode ({batch_limit}). "
                "Use mode='async'."
            )

        t0 = time.time()
        # full_payload contiene {embeddings_batch, prototypes_batch, config, license_key, tier}
        full_payload = self._prepare_payload(data_points, config)

        try:
            # 🚀 MODO ASÍNCRONO (Cliente Liviano: El SDK envía el payload COMPLETO a Vercel)
            if mode == 'async' and self.tier in ['professional', 'enterprise']:
                
                # 1️⃣ Llamada al Gateway de Datos Pesados (/api/enqueue)
                endpoint = f"{self.base_url}/enqueue"
                
                # 🛑 CAMBIO CRÍTICO: Envía full_payload (pesado) directamente a Vercel.
                # Vercel (api/index.py) ahora tiene la lógica de GCS.
                resp = self.session.post(
                    endpoint, 
                    json=full_payload, # <-- Envía el payload entero, Vercel lo subirá a GCS.
                    timeout=60 
                )
                
                resp.raise_for_status()

                # 2️⃣ Vercel devuelve solo el Job ID 
                job_data = resp.json()
                logger.info(
                    f"Async job {job_data.get('job_id')} enqueued in {time.time() - t0:.2f}s"
                )
                return Job(
                    job_id=job_data["job_id"],
                    sdk=self,
                    status=job_data.get("status", "queued"),
                )

            # ⚙️ MODO SÍNCRONO (lotes pequeños -> eval directa)
            else:
                api_payload = full_payload
                # El modo síncrono llama a /evaluate en index.py, 
                # que hace proxy directo a Cloud Run.
                endpoint = f"{self.base_url}/evaluate" 
                resp = self.session.post(endpoint, json=api_payload, timeout=self.timeout)
                resp.raise_for_status()

                scores = resp.json().get("scores", [])
                logger.info(f"Sync evaluation completed in {time.time() - t0:.2f}s")
                return [EvaluationResult(score=float(s), tier=self.tier) for s in scores]

        except requests.exceptions.HTTPError as e:
            try:
                data = e.response.json()
            except Exception:
                data = {"error": e.response.text}
            raise APIError(f"API Error {e.response.status_code}: {data.get('error')}")

        except Exception as e:
            raise APIError(f"Evaluation failed: {e}")

    
    def get_job_status(self, job_id: str) -> Dict:
        """Consulta el estado de un job asíncrono"""
        try:
            endpoint = f"{self.base_url}/status/{job_id}"
            resp = self.session.get(endpoint, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            try: data = e.response.json()
            except: data = {'error': e.response.text}
            raise APIError(f"API Error {e.response.status_code}: {data.get('error')}")
        except Exception as e:
            raise APIError(f"Status check failed: {e}")

    def create_config(self) -> Config:
        return Config()
    
    def close(self):
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
