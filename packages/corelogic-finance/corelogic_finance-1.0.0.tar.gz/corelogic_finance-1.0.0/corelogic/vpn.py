# corelogic/vpn.py
import numpy_financial as npf 
from .excepciones import TasaInvalidaError, FlujosInvalidosError

class VPN:
    """
    Evaluación de Proyectos de Capital: Clase fundamental para la toma de 
    decisiones de inversión. Calcula el Valor Presente Neto (VPN) y la Tasa 
    Interna de Retorno (TIR), indicadores clave para determinar la viabilidad 
    financiera de un proyecto.
    """
    def __init__(self, tasa_descuento: float, flujos_caja: list):
        """
        Inicializa la clase con los parámetros del proyecto.
        
        :param tasa_descuento: Tasa de costo de capital o tasa de retorno requerida (como decimal).
        :param flujos_caja: Lista de flujos de caja del proyecto, donde el primer 
                            elemento (índice 0) es la inversión inicial (negativa).
        """
        self._validar_flujos(tasa_descuento, flujos_caja) # Delegación de la validación

        # Atributos privados (__): Encapsulación de los datos del proyecto.
        self.__tasa_descuento = tasa_descuento
        self.__flujos_caja = flujos_caja

    def _validar_flujos(self, tasa: float, flujos: list):
        """
        [Método Interno de Validación] Asegura que la tasa y la lista de flujos sean válidos.
        
        Lanza excepciones personalizadas (TasaInvalidaError, FlujosInvalidosError) 
        para una gestión de errores específica en la arquitectura CoreLogic.
        """
        if tasa < 0:
            raise TasaInvalidaError("La tasa de descuento no puede ser negativa.")
        if not flujos:
            raise FlujosInvalidosError("La lista de flujos de caja no puede estar vacía.")

    def calcular_vpn(self) -> float:
        """
        Calcula el Valor Presente Neto (VPN).
        
        Aplica la corrección lógica necesaria: la función npf.npv calcula solo el 
        Valor Presente de los flujos futuros (t=1, t=2...), por lo que la inversión 
        inicial (t=0) debe sumarse por separado.
        
        :returns: El VPN del proyecto, redondeado a dos decimales.
        """
        # Desglose de flujos para la función npf.npv, que espera flujos a partir de t=1.
        inversion_inicial = self.__flujos_caja[0]
        flujos_futuros = self.__flujos_caja[1:]
        
        # 1. Valor Presente de los flujos futuros (excluyendo t=0)
        vpn_flujos_futuros = npf.npv(self.__tasa_descuento, flujos_futuros)
        
        # 2. VPN final = Inversión Inicial (t=0) + VP de flujos futuros
        return round(inversion_inicial + vpn_flujos_futuros, 2)

    @classmethod
    def calcular_tir(cls, flujos: list) -> float:
        """
        Calcula la Tasa Interna de Retorno (TIR).
        
        La TIR es la tasa de descuento que hace que el VPN sea igual a cero.
        Este método se ofrece como un método de clase para facilitar cálculos 
        rápidos sin necesidad de inicializar un objeto VPN.
        
        :param flujos: Lista de flujos de caja (incluyendo la inversión inicial negativa en t=0).
        :returns: La TIR como un valor decimal (ej: 0.15 para 15%).
        :raises ValueError: Si la lista de flujos no tiene flujos tanto positivos como negativos.
        """
        # Validación: La TIR solo es calculable si existe al menos un cambio de signo en los flujos.
        if not flujos or sum(f > 0 for f in flujos) == 0 or sum(f < 0 for f in flujos) == 0:
             raise ValueError("Flujos deben contener valores positivos y negativos para calcular la TIR.")
             
        # npf.irr maneja la lista de flujos completa (incluyendo t=0) correctamente.
        return npf.irr(flujos)