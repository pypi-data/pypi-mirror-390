# corelogic/analisis_ratio.py

class AnalisisRatio:
    """
    Evaluación de la Salud Financiera: Clase dedicada al cálculo de ratios clave 
    de liquidez y solvencia. Permite evaluar la capacidad de una empresa para 
    cubrir sus obligaciones a corto plazo.
    """
    def __init__(self, activos_corrientes: float, pasivos_corrientes: float, inventario: float):
        """
        Inicializa la clase con los datos contables primarios.
        
        :param activos_corrientes: Activos que se esperan convertir en efectivo en un año (o ciclo operativo).
        :param pasivos_corrientes: Obligaciones que vencen en un año.
        :param inventario: Valor total del inventario.
        """
        # Atributos privados: Aplicamos la Encapsulación estricta.
        self.__activos_corrientes = activos_corrientes
        self.__pasivos_corrientes = pasivos_corrientes
        self.__inventario = inventario

    def ratio_liquidez_corriente(self) -> float:
        """
        Calcula el Ratio de Liquidez Corriente (Current Ratio).
        
        Mide la capacidad de la empresa para pagar sus pasivos corrientes 
        usando sus activos corrientes. Un valor > 1.0 es generalmente deseable.
        
        :returns: El valor del Ratio de Liquidez Corriente.
        :raises ZeroDivisionError: Si los Pasivos Corrientes son cero, lo que imposibilita el cálculo.
        """
        if self.__pasivos_corrientes == 0:
             # Control explícito de la división por cero, como exige la arquitectura.
             raise ZeroDivisionError("Los Pasivos Corrientes no pueden ser cero para calcular ratios de liquidez.")
             
        return self.__activos_corrientes / self.__pasivos_corrientes

    def ratio_prueba_acida(self) -> float:
        """
        Calcula el Ratio de Prueba Ácida (Quick Ratio).
        
        Es una medida de liquidez más estricta, ya que excluye el Inventario 
        (el activo menos líquido) de los activos corrientes.
        
        :returns: El valor del Ratio de Prueba Ácida.
        :raises ZeroDivisionError: Si los Pasivos Corrientes son cero.
        """
        if self.__pasivos_corrientes == 0:
            # Esta excepción fue validada rigurosamente en la fase de pruebas (Pytest).
            raise ZeroDivisionError("Los Pasivos Corrientes no pueden ser cero para calcular ratios de liquidez.")
            
        return (self.__activos_corrientes - self.__inventario) / self.__pasivos_corrientes