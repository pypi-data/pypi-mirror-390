# corelogic/depreciacion.py

class Depreciacion:
    """
    Gestión de Activos y Contabilidad: Proporciona métodos precisos para el 
    cálculo de la depreciación de activos fijos, esencial para estados financieros
    y planificación fiscal, utilizando el método de línea recta.
    """
    def __init__(self, costo_inicial: float, valor_residual: float, vida_util_años: int):
        """
        Inicializa la clase con los parámetros del activo.
        
        Aplica el Principio de Validación Interna: Los datos son validados antes 
        de ser almacenados para garantizar la integridad de la clase.
        
        :param costo_inicial: Costo original de adquisición del activo.
        :param valor_residual: Valor de reventa o desecho del activo al final de su vida útil.
        :param vida_util_años: Número de años durante los cuales se depreciará el activo.
        """
        # La validación es lo primero
        self._validar_datos(costo_inicial, valor_residual, vida_util_años)

        # Encapsulación estricta de atributos principales (__)
        self.__costo_inicial = costo_inicial
        self.__valor_residual = valor_residual
        self.__vida_util_años = vida_util_años

    def _validar_datos(self, costo_inicial: float, valor_residual: float, vida_util_años: int):
        """
        [Método Interno de Validación] Asegura que los datos de entrada cumplen con 
        las reglas de negocio y los casos límite.
        
        :raises ValueError: Si la vida útil no es positiva o si el costo inicial es menor al valor residual.
        """
        if vida_util_años <= 0:
            raise ValueError("La vida útil debe ser un valor positivo (años > 0).")
        if costo_inicial < valor_residual:
            raise ValueError("El costo inicial no puede ser menor que el valor residual.")

    def calcular_depreciacion_anual(self) -> float:
        """
        Calcula el monto fijo de depreciación anual (método de línea recta).
        
        Fórmula: (Costo Inicial - Valor Residual) / Vida Útil en Años.
        
        :returns: La cantidad monetaria de depreciación por año.
        """
        # El cálculo utiliza los atributos privados (encapsulados)
        return (self.__costo_inicial - self.__valor_residual) / self.__vida_util_años

    def calcular_valor_contable(self, año: int) -> float:
        """
        Calcula el valor contable (Book Value) del activo en un año específico.
        
        :param año: El año (1, 2, 3...) para el cual se desea el valor contable.
        :returns: El valor contable del activo.
        :raises ValueError: Si el año proporcionado no es positivo.
        """
        if año <= 0:
            raise ValueError("El año debe ser un valor positivo.")
            
        # Un activo no puede depreciarse por debajo de su valor residual.
        if año >= self.__vida_util_años:
            # Si el año excede o es igual a la vida útil, el valor contable es el valor residual
            return self.__valor_residual 
        
        depreciacion_acumulada = self.calcular_depreciacion_anual() * año
        
        # Valor Contable = Costo Inicial - Depreciación Acumulada
        return self.__costo_inicial - depreciacion_acumulada