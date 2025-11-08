# corelogic/__init__.py

# Este archivo define la interfaz pública de la librería CoreLogic.
# Su propósito es permitir a los usuarios importar las clases de cálculo directamente
# desde el paquete principal (ej: from corelogic import VPN, Amortizacion).

# --- Módulos de Cálculo Financiero ---
# Hacemos que las clases principales estén disponibles a nivel del paquete para 
# simplificar la reutilización y la experiencia del desarrollador (DevX).
from .depreciacion import Depreciacion
from .vpn import VPN
from .amortizacion import Amortizacion
from .interes_compuesto import InteresCompuesto
from .analisis_ratio import AnalisisRatio

# --- Excepciones Personalizadas ---
# Exportamos las excepciones definidas en el diseño de arquitectura.
# Esto garantiza que los usuarios puedan capturar y manejar errores específicos 
# de la lógica de negocio de CoreLogic.
from .excepciones import TasaInvalidaError, FlujosInvalidosError, FrecuenciaInvalidaError