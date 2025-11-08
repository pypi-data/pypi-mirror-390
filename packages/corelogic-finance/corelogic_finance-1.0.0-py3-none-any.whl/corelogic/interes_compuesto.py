# corelogic/interes_compuesto.py
from .excepciones import FrecuenciaInvalidaError

class InteresCompuesto:
    """
    Proyección de Inversiones: Clase especializada en calcular el Valor Futuro (FV) 
    de una inversión sujeta a interés compuesto, manejando diversas frecuencias de 
    capitalización. Es fundamental para la planificación financiera a largo plazo.
    """
    # [Atributo de Clase] Mapeo de frecuencias de composición a sus valores numéricos (n).
    FRECUENCIAS = {
        'anual': 1,
        'semestral': 2,
        'trimestral': 4,
        'mensual': 12,
        'diaria': 365
    }

    def __init__(self, principal: float, tasa_anual: float, años: float, frecuencia_composicion: str):
        """
        Inicializa la clase con los parámetros de la inversión.
        
        :param principal: Cantidad inicial invertida o prestada (P).
        :param tasa_anual: Tasa de interés nominal anual (r), como decimal (ej: 0.05).
        :param años: Número de años que durará la inversión (t).
        :param frecuencia_composicion: Cadena que indica la frecuencia de capitalización 
                                       (ej: 'mensual', 'semestral').
        """
        self._validar_frecuencia(frecuencia_composicion) # Aplica validación interna
        
        # Atributos privados (__): Encapsulación de datos esenciales.
        self.__principal = principal
        self.__tasa_anual = tasa_anual
        self.__años = años
        self.__frecuencia_composicion = frecuencia_composicion

    def _validar_frecuencia(self, frecuencia: str):
        """
        [Método Interno de Validación] Verifica que la frecuencia proporcionada sea una 
        opción reconocida en el diccionario FRECUENCIAS.
        
        :raises FrecuenciaInvalidaError: Si la frecuencia no se encuentra en el mapeo.
        """
        if frecuencia not in self.FRECUENCIAS:
            # Lanza la excepción personalizada, indicando al usuario las opciones válidas.
            raise FrecuenciaInvalidaError(
                f"Frecuencia inválida: '{frecuencia}'. Debe ser una de {list(self.FRECUENCIAS.keys())}"
            )

    def calcular_valor_futuro(self) -> float:
        """
        Calcula el Valor Futuro (Future Value, FV) final de la inversión.
        
        Fórmula utilizada: FV = P * (1 + r/n)^(n*t)
        
        :returns: El monto total acumulado, redondeado a dos decimales.
        """
        # Mapeamos la frecuencia para obtener 'n' (periodos de composición por año)
        n = self.FRECUENCIAS[self.__frecuencia_composicion] 
        
        r = self.__tasa_anual 
        t = self.__años 
        p = self.__principal 
        
        # Implementación directa de la fórmula de Interés Compuesto.
        valor_futuro = p * (1 + r / n)**(n * t)
        return round(valor_futuro, 2)

    def calcular_ganancia_intereses(self) -> float:
        """
        Calcula la ganancia total generada por intereses (Interés Compuesto Total).
        
        :returns: La diferencia entre el Valor Futuro y el Principal inicial.
        """
        return self.calcular_valor_futuro() - self.__principal