# tests/test_vpn.py
import pytest
from corelogic import VPN, TasaInvalidaError, FlujosInvalidosError
import numpy as np

# --- 1. Pruebas de Confiabilidad: Excepciones Personalizadas ---

def test_vpn_lanza_tasa_invalida_error_en_init():
    """
    [Excepción Personalizada] Verifica el lanzamiento de TasaInvalidaError si la 
    tasa de descuento es negativa, asegurando la robustez en la validación de 
    los parámetros financieros.
    """
    flujos = [-1000, 200, 300]
    tasa_negativa = -0.05
    
    with pytest.raises(TasaInvalidaError) as excinfo:
        VPN(tasa_negativa, flujos)
        
    assert "no puede ser negativa" in str(excinfo.value) # Validar el mensaje

def test_vpn_lanza_flujos_invalidos_error_en_init():
    """
    [Excepción Personalizada y Caso Límite] Verifica el lanzamiento de 
    FlujosInvalidosError si la lista de flujos de caja está vacía, un caso 
    límite crucial para la estabilidad del cálculo.
    """
    tasa = 0.10
    flujos_vacios = [] 
    
    with pytest.raises(FlujosInvalidosError) as excinfo:
        VPN(tasa, flujos_vacios)
        
    assert "no puede estar vacía" in str(excinfo.value) # Validar el mensaje

# --- 2. Pruebas Funcionales: Métodos de Instancia (VPN) ---

def test_vpn_calculo_correcto():
    """
    [Cálculo Preciso] Verifica que el cálculo del VPN coincida con un valor 
    conocido (10.83). Valida la corrección lógica donde la inversión inicial (t=0) 
    se suma por separado de los flujos descontados por numpy-financial.
    """
    # Ejemplo: Tasa 10%. Flujos: -100 (inversión inicial), 10, 20, 100
    tasa = 0.10
    flujos_ejemplo = [-100.0, 10.0, 20.0, 100.0]

    vpn_obj = VPN(tasa, flujos_ejemplo)
    resultado = vpn_obj.calcular_vpn()

    # El VPN conocido y validado es 10.83
    assert round(resultado, 2) == 10.83

# --- 3. Pruebas Funcionales: Método de Clase (TIR) ---

def test_vpn_calcular_tir_correcto():
    """
    [Cálculo Preciso] Verifica que el método de clase calcular_tir devuelva 
    el valor correcto (23.38%).
    """
    flujos = [-100.0, 50.0, 50.0, 50.0]
    
    # Llamada al método de clase sin crear una instancia
    tir_calculada = VPN.calcular_tir(flujos) 

    # La TIR para este flujo es 23.38%
    assert round(tir_calculada, 4) == 0.2338

def test_vpn_calcular_tir_lanza_value_error_sin_inversion():
    """
    [Regla de Negocio] Verifica que la TIR falle si no existe una inversión inicial 
    (flujo negativo), ya que el cálculo requiere un cambio de signo en los flujos.
    """
    flujos_sin_negativos = [10.0, 20.0, 30.0]
    
    with pytest.raises(ValueError):
        VPN.calcular_tir(flujos_sin_negativos)