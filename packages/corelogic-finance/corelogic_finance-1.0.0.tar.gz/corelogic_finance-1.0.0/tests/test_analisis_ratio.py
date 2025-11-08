# tests/test_analisis_ratio.py
import pytest
# Importamos la clase a probar directamente desde el paquete corelogic
from corelogic import AnalisisRatio

# 1. Prueba de Caso de Éxito (Verificación de la lógica)
def test_ratio_liquidez_corriente_calculo_correcto():
    """Verifica el cálculo estándar del Ratio de Liquidez Corriente (Activos/Pasivos)."""
    # Activos = 200, Pasivos = 100, Esperado = 2.0
    ratio_obj = AnalisisRatio(activos_corrientes=200.0, pasivos_corrientes=100.0, inventario=50.0)
    resultado = ratio_obj.ratio_liquidez_corriente()
    assert resultado == 2.0

# 2. Prueba de Caso de Éxito (Verificación de la lógica para Prueba Ácida)
def test_ratio_prueba_acida_calculo_correcto():
    """Verifica el cálculo estándar del Ratio de Prueba Ácida (Activos-Inv.)/Pasivos."""
    # Activos = 200, Pasivos = 100, Inventario = 50. Esperado = (200-50)/100 = 1.5
    ratio_obj = AnalisisRatio(activos_corrientes=200.0, pasivos_corrientes=100.0, inventario=50.0)
    resultado = ratio_obj.ratio_prueba_acida()
    assert resultado == 1.5

# 3. Prueba de Excepción (ZeroDivisionError en Liquidez Corriente)
def test_ratio_liquidez_corriente_lanza_zero_division_error():
    """
    Verifica que se lance ZeroDivisionError si pasivos_corrientes == 0, 
    cumpliendo el principio de manejo formal del error.
    """
    # Caso límite: Pasivos Corrientes (denominador) = 0.0
    ratio_obj = AnalisisRatio(activos_corrientes=150.0, pasivos_corrientes=0.0, inventario=50.0)
    
    # Utilizamos pytest.raises para asegurar que el método lanza la excepción correcta
    with pytest.raises(ZeroDivisionError) as excinfo:
        ratio_obj.ratio_liquidez_corriente()
        
    assert "Los Pasivos Corrientes no pueden ser cero para calcular ratios de liquidez" in str(excinfo.value)

# 4. Prueba de Excepción (ZeroDivisionError en Prueba Ácida)
def test_ratio_prueba_acida_lanza_zero_division_error():
    """
    Verifica que se lance ZeroDivisionError si pasivos_corrientes == 0 
    para el ratio de Prueba Ácida.
    """
    # Caso límite: Pasivos Corrientes (denominador) = 0.0
    ratio_obj = AnalisisRatio(activos_corrientes=150.0, pasivos_corrientes=0.0, inventario=50.0)
    
    with pytest.raises(ZeroDivisionError):

        ratio_obj.ratio_prueba_acida()