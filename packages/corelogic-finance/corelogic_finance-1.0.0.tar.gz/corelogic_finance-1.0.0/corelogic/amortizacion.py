# corelogic/amortizacion.py
import pandas as pd
import numpy_financial as np 

class Amortizacion:
    """
    Simulación y Gestión de Deuda: Clase especializada en generar planes 
    de amortización (tablas de pago) para préstamos de cuota fija.

    Asegura la precisión matemática en el cálculo del Principal, Intereses 
    y Balance restante para cada período.
    """
    def __init__(self, principal: float, tasa_anual: float, periodos_meses: int):
        """
        Inicializa la clase con los parámetros del préstamo.
        
        Aplica la Encapsulación estricta (__atributo) para proteger los 
        datos de entrada, en línea con nuestra arquitectura CoreLogic.
        
        :param principal: Monto total del préstamo a amortizar.
        :param tasa_anual: Tasa de interés nominal anual (ej: 0.05 para 5%).
        :param periodos_meses: Duración total del préstamo en meses.
        """
        self._validar_periodos(periodos_meses)

        # Atributos privados (__): Garantizan la inmutabilidad y encapsulación.
        self.__principal = principal
        self.__tasa_anual = tasa_anual
        self.__periodos_meses = periodos_meses

    def _validar_periodos(self, periodos: int):
        """
        [Método Interno de Validación] Verifica que el número de períodos sea válido.
        
        Lanza un ValueError si la duración del préstamo no es positiva.
        """
        if periodos <= 0:
            raise ValueError("El número de periodos (meses) debe ser positivo.") 

    def _convertir_tasa_periodica(self) -> float:
        """
        [Método Interno de Utilidad] Convierte la tasa anual a una tasa mensual.
        
        Es fundamental para que los cálculos de numpy-financial (PMT) operen correctamente.
        """
        return self.__tasa_anual / 12

    def calcular_pago_mensual(self) -> float:
        """
        Calcula el pago mensual (cuota fija) requerido para amortizar el préstamo. 
        
        IMPORTANTE: Devuelve el valor preciso (float sin redondear) para garantizar 
        la exactitud en la generación de la tabla de amortización. El redondeo 
        final a dos decimales se maneja al mostrar los resultados en la tabla.
        
        :returns: Pago fijo mensual como float de alta precisión.
        """
        tasa_mensual = self._convertir_tasa_periodica()
        
        # np.pmt (Payment) requiere la tasa, el número de períodos (nper) y el valor presente (pv).
        # Usamos -self.__principal porque numpy-financial opera con el flujo de efectivo.
        pago = np.pmt(tasa_mensual, self.__periodos_meses, -self.__principal)
        return pago 

    def generar_tabla_amortizacion(self) -> pd.DataFrame:
        """
        Genera el plan de pagos detallado, mostrando la distribución 
        de Intereses y Principal para cada mes.
        
        :returns: Un DataFrame de Pandas con el detalle mes a mes.
        """
        tasa_mensual = self._convertir_tasa_periodica()
        # Usamos el pago mensual preciso para minimizar los errores de redondeo acumulados.
        pago_mensual_fijo = self.calcular_pago_mensual()
        
        balance = self.__principal
        data = []
        for mes in range(1, self.__periodos_meses + 1):
            interes = balance * tasa_mensual
            
            # --- Lógica de Ajuste para el Último Mes (Crucial para la Confiabilidad) ---
            # En el último período, se ajusta el pago del principal para que sea 
            # exactamente igual al balance restante, asegurando que el balance final sea 0.00.
            if mes == self.__periodos_meses:
                principal_pagado = balance 
                pago_mensual = interes + principal_pagado # El último pago total se ajusta.
            else:
                pago_mensual = pago_mensual_fijo
                principal_pagado = pago_mensual - interes
            # --------------------------------------------------------------------------
                
            nuevo_balance = balance - principal_pagado
            
            # Los valores en el DataFrame se redondean a 2 decimales solo para presentación.
            data.append({
                'Mes': mes,
                'Pago': round(pago_mensual, 2),
                'Interes': round(interes, 2),
                'Principal': round(principal_pagado, 2),
                'Balance': round(max(0, nuevo_balance), 2)
            })
            balance = nuevo_balance

        return pd.DataFrame(data)