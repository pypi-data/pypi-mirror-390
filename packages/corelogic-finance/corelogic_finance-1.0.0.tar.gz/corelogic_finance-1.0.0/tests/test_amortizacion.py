# tests/test_amortizacion.py
import pytest
import pandas as pd
from corelogic import Amortizacion

# --- Parámetros de Pruebas ---
# Datos de prueba conocidos (Préstamo simple) para asegurar la reproducibilidad.
PRINCIPAL = 1000.00
TASA_ANUAL = 5.0 # Tasa usada: 5.0% (se convierte a tasa periódica internamente)
PERIODOS = 12   # Duración del préstamo: 1 año

# --- 1. Pruebas de Confiabilidad: Validación en __init__ (Casos Límite) ---

def test_amortizacion_lanza_value_error_periodos_cero():
    """
    [Validación de Entrada] Verifica que el constructor lance ValueError 
    si el número de periodos (meses) es 0 o negativo, en línea con el principio 
    de Validación Interna.
    """
    periodos_cero = 0
    with pytest.raises(ValueError) as excinfo:
        Amortizacion(PRINCIPAL, TASA_ANUAL, periodos_cero)
        
    assert "El número de periodos (meses) debe ser positivo" in str(excinfo.value)

# --- 2. Pruebas Funcionales: Cálculo Fijo (Precisión) ---

def test_calcular_pago_mensual_correcto():
    """
    [Cálculo Preciso] Verifica que el cálculo del pago mensual (Cuota Fija) 
    coincida con un valor financiero conocido (423.14 para este caso).
    """
    amort_obj = Amortizacion(PRINCIPAL, TASA_ANUAL, PERIODOS)
    pago_esperado = 423.14 # Valor conocido y validado
    resultado = amort_obj.calcular_pago_mensual()
    
    # Se redondea el resultado para la aserción ya que el cálculo interno usa alta precisión.
    assert round(resultado, 2) == pago_esperado

# --- 3. Prueba Crucial: Integración y Robustez (Balance Cero) ---

def test_generar_tabla_amortizacion_balance_cero_final():
    """
    PRUEBA DE CONFIABILIDAD CLAVE:
    Verifica el Caso Límite donde la última fila de la tabla de amortización 
    debe tener un balance de EXACTAMENTE 0.00. Esto valida la lógica de ajuste 
    implementada en el último pago para corregir errores de punto flotante.
    """
    amort_obj = Amortizacion(PRINCIPAL, TASA_ANUAL, PERIODOS)
    tabla: pd.DataFrame = amort_obj.generar_tabla_amortizacion()
    
    # 1. Verificar el tipo de retorno (Integración con Pandas)
    assert isinstance(tabla, pd.DataFrame)
    
    # 2. Verificar el caso límite: Balance final
    balance_final = tabla.iloc[-1]['Balance']
    assert balance_final == 0.00 # Debe ser EXACTAMENTE cero

def test_generar_tabla_amortizacion_suma_principal_igual_al_monto():
    """
    [Consistencia Matemática] Verifica que la suma total del Principal pagado 
    a lo largo de todos los periodos sea igual al monto inicial del préstamo.
    
    Utiliza pytest.approx para permitir una mínima tolerancia, crucial al sumar 
    muchos valores redondeados.
    """
    amort_obj = Amortizacion(PRINCIPAL, TASA_ANUAL, PERIODOS)
    tabla: pd.DataFrame = amort_obj.generar_tabla_amortizacion()
    
    # Sumar la columna 'Principal'
    suma_principal_pagado = tabla['Principal'].sum()
    
    # Aserción con tolerancia (abs=0.01) para el principio vs. suma
    assert suma_principal_pagado == pytest.approx(PRINCIPAL, abs=0.01)