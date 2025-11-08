# corelogic/excepciones.py

# Las excepciones personalizadas son un pilar clave en la arquitectura CoreLogic.
# Permiten a los desarrolladores clientes capturar errores específicos del dominio
# financiero/negocio, haciendo la aplicación más robusta y fácil de depurar.

class TasaInvalidaError(ValueError):
    """
    [Error de Parámetro] Se lanza cuando se proporciona una tasa de interés o 
    descuento que no es válida para el cálculo (ej. valor negativo).
    
    Aplica a clases como VPN e InteresCompuesto.
    """
    pass

class FlujosInvalidosError(ValueError):
    """
    [Error de Datos] Se lanza específicamente cuando la lista de flujos de caja 
    está vacía o no cumple con la estructura requerida para los cálculos de VPN.
    
    Asegura que el módulo VPN opere con datos válidos.
    """
    pass

class FrecuenciaInvalidaError(ValueError):
    """
    [Error de Configuración] Se lanza cuando se intenta realizar un cálculo 
    de interés compuesto con una frecuencia de capitalización no reconocida 
    (ej. 'trimestral' vs 'semestral', o un valor numérico <= 0).
    
    Aplica al módulo InteresCompuesto.
    """
    pass