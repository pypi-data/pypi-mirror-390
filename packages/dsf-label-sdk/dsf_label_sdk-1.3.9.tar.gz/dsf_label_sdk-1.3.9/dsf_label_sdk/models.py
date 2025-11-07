# dsf_label_sdk/models.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, TYPE_CHECKING
import time
from .exceptions import JobTimeoutError, APIError

if TYPE_CHECKING:
    from .client import LabelSDK

@dataclass
class EvaluationResult:
    """Resultado de una evaluación síncrona."""
    score: float
    tier: str
    confidence_level: float = 0.65
    metrics: Optional[Dict[str, Any]] = None

@dataclass
class Job:
    """Resultado de una solicitud asíncrona."""
    job_id: str
    sdk: 'LabelSDK'
    status: str = 'queued'
    _result: Optional[List[EvaluationResult]] = None
    
    def get_status(self) -> str:
        """Refresca y devuelve el estado actual del job."""
        if self.status == 'completed' or self.status == 'failed':
            return self.status
        
        data = self.sdk.get_job_status(self.job_id)
        self.status = data.get('status', 'unknown')
        
        if self.status == 'completed':
            scores = data.get('result', {}).get('scores', [])
            self._result = [EvaluationResult(score=float(s), tier=self.sdk.tier) for s in scores]
        elif self.status == 'failed':
            raise APIError(f"Job {self.job_id} failed: {data.get('error')}")
            
        return self.status

    def wait_for_completion(self, timeout: int = 300, poll_interval: int = 5) -> List[EvaluationResult]:
        """
        Espera a que el job termine, sondeando el estado.
        Devuelve la lista de resultados o lanza una excepción.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_status()
            
            if status == 'completed':
                return self._result
            if status == 'failed':
                # La excepción se lanza dentro de get_status()
                pass 
            
            time.sleep(poll_interval)
        
        raise JobTimeoutError(f"Job {self.job_id} timed out after {timeout}s")

    def result(self) -> Optional[List[EvaluationResult]]:
        """Devuelve el resultado si ya está completado."""
        if self.status != 'completed':
            self.get_status()
        return self._result

class Config:
    def __init__(self):
        self.fields = {}
    
    def add_field(self, name: str, default: Any, weight: float = 1.0, criticality: float = 1.0, **kwargs):
        """Añade un campo a la configuración. 'prototype' puede ir en kwargs."""
        self.fields[name] = {
            'default': default,
            'weight': weight,
            'criticality': criticality,
            **kwargs
        }
        return self
    
    def to_dict(self) -> Dict:
        return self.fields
    
@dataclass
class Field:
    name: str
    default: Any
    weight: float = 1.0
    criticality: float = 1.0

    def to_dict(self) -> Dict:
        return {
            "default": self.default,
            "weight": self.weight,
            "criticality": self.criticality
        }