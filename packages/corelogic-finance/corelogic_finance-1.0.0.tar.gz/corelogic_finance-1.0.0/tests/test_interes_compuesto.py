# tests/test_interes_compuesto.py
import pytest
from corelogic import InteresCompuesto, FrecuenciaInvalidaError

# --- 1. Pruebas de Confiabilidad: Excepción Personalizada ---

def test_interes_compuesto_lanza_frecuencia_invalida_error():
    """
    [Cobertura de Excepciones] Verifica el lanzamiento de la Excepción Personalizada 
    (FrecuenciaInvalidaError) si la frecuencia de capitalización no es reconocida 
    por la clase.
    """
    principal = 1000.0
    tasa_anual = 0.05 
    años = 1.0
    frecuencia_invalida = 'trimestral-invalido' # Caso de error: Frecuencia no soportada
    
    with pytest.raises(FrecuenciaInvalidaError) as excinfo:
        InteresCompuesto(principal, tasa_anual, años, frecuencia_invalida) 
        
    # Validación del mensaje que informa al usuario sobre las opciones correctas
    assert "Frecuencia inválida" in str(excinfo.value)

# --- 2. Pruebas Funcionales: Cálculo de Valor Futuro ---

def test_valor_futuro_anual_calculo_correcto():
    """
    [Cálculo Funcional] Verifica el cálculo simple con capitalización anual (n=1).
    Esperado: 1000 * (1 + 0.05/1)^(1*1) = 1050.00
    """
    interes_obj = InteresCompuesto(principal=1000.0, tasa_anual=0.05, años=1.0, frecuencia_composicion='anual')
    resultado = interes_obj.calcular_valor_futuro()
    assert resultado == 1050.00 

def test_valor_futuro_mensual_calculo_correcto():
    """
    [Cálculo Funcional] Verifica el impacto de una mayor frecuencia de capitalización (n=12).
    Asegura que el mapeo de frecuencias funcione y que el cálculo sea preciso (1051.16).
    """
    interes_obj = InteresCompuesto(principal=1000.0, tasa_anual=0.05, años=1.0, frecuencia_composicion='mensual')
    resultado = interes_obj.calcular_valor_futuro()
    assert resultado == 1051.16

# --- 3. Pruebas Funcionales: Ganancia de Intereses ---

def test_ganancia_intereses_calculo_correcto():
    """
    [Cálculo Derivado] Verifica que la ganancia de intereses totales sea correcta 
    (Valor Futuro - Principal), un método derivado clave para el análisis.
    """
    principal = 1000.0
    interes_obj = InteresCompuesto(principal=principal, tasa_anual=0.05, años=1.0, frecuencia_composicion='anual')
    # Valor Futuro = 1050.00. Ganancia esperada: 50.00
    ganancia = interes_obj.calcular_ganancia_intereses()
    assert ganancia == 50.00