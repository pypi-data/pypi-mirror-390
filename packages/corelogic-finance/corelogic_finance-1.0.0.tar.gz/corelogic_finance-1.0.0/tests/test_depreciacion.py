# tests/test_depreciacion.py
import pytest
from corelogic import Depreciacion

# --- 1. Pruebas de Confiabilidad: Validación en __init__ (Casos Límite) ---

def test_depreciacion_lanza_value_error_vida_util_cero():
    """
    [Validación de Entrada] Verifica que el constructor lance ValueError si la vida 
    útil es cero o negativa, impidiendo la división por cero y aplicando el 
    Principio de Validación Interna.
    """
    costo = 10000.0
    residual = 1000.0
    vida_util_cero = 0 # Caso límite: vida_util_años <= 0 
    
    with pytest.raises(ValueError) as excinfo:
        Depreciacion(costo, residual, vida_util_cero)
        
    assert "vida útil debe ser un valor positivo" in str(excinfo.value)

def test_depreciacion_lanza_value_error_costo_menor_residual():
    """
    [Regla de Negocio] Verifica que el constructor lance ValueError si el costo 
    inicial es menor que el valor residual (un activo no se deprecia si su valor 
    residual es mayor al costo).
    """
    costo = 5000.0
    residual = 8000.0 # Caso inválido: costo_inicial < valor_residual 
    vida_util = 5
    
    with pytest.raises(ValueError) as excinfo:
        Depreciacion(costo, residual, vida_util)
        
    assert "costo inicial no puede ser menor que el valor residual" in str(excinfo.value)

# --- 2. Pruebas Funcionales: Lógica de Cálculo ---

def test_depreciacion_anual_calculo_correcto():
    """
    [Cálculo Funcional] Verifica el cálculo estándar de la depreciación anual 
    (método de Línea Recta). Esperado: (10000 - 1000) / 5 = 1800.0
    """
    dep_obj = Depreciacion(costo_inicial=10000.0, valor_residual=1000.0, vida_util_años=5)
    resultado = dep_obj.calcular_depreciacion_anual() 
    assert resultado == 1800.0

def test_valor_contable_final_igual_residual():
    """
    [Caso Límite] Verifica que el valor contable en el ÚLTIMO año de la vida útil 
    sea exactamente igual al valor residual.
    """
    costo = 10000.0
    residual = 1000.0
    vida_util = 5
    dep_obj = Depreciacion(costo, residual, vida_util)
    
    # Valor contable en el último año (año 5)
    valor_contable = dep_obj.calcular_valor_contable(vida_util) 
    assert valor_contable == residual

def test_valor_contable_depreciado_totalmente():
    """
    [Caso Límite] Verifica que el valor contable NO se deprecie más allá del 
    valor residual, incluso si el año consultado excede la vida útil (ej. año 10).
    """
    dep_obj = Depreciacion(costo_inicial=10000.0, valor_residual=1000.0, vida_util_años=5)
    
    # Valor contable después de la vida útil (ej. año 10)
    valor_contable = dep_obj.calcular_valor_contable(10) 
    assert valor_contable == 1000.0