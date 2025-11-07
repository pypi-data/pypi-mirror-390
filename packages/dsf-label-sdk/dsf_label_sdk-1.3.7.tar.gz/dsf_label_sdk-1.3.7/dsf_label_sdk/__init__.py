# dsf_label_sdk/__init__.py

__version__ = '1.3.7'
__author__ = 'Jaime Alexander Jimenez'
__email__ = 'contacto@softwarefinanzas.com.co'

# Import principal
from .client import DSFLabelClient as LabelSDK  # retrocompatibilidad
from .client import DSFLabelClient
from .models import Field, Config, EvaluationResult, Job
from .exceptions import (
    LabelSDKError,
    ValidationError,
    LicenseError,
    APIError,
    RateLimitError,
    JobTimeoutError
)

__all__ = [
    'DSFLabelClient',
    'LabelSDK',
    'Field',
    'Config',
    'EvaluationResult',
    'Job',
    'LabelSDKError',
    'ValidationError',
    'LicenseError',
    'APIError',
    'RateLimitError',
    'JobTimeoutError'
]

