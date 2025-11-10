__version__ = '0.1.0'

# Make key classes available at package level
from curb_energy.client import AuthToken, RestApiClient, RealTimeClient

__all__ = [
    'AuthToken',
    'RestApiClient',
    'RealTimeClient',
    '__version__',
]
