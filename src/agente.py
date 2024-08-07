import random
from collections import defaultdict

"""
Necesitamos:

- Estructura para representar el grafo [x]
- Elegir quiénes van a comerciar [x]
- Decisiones posibles (de cuánto ofrecer y cuándo rechazar) [x]
- Llamar a una función dummy "estrategia" que te diga qué elegir, que todavía no haga nada o te devuelva algo al azar. Después de tener la estructura lista definimos cómo encarar el tema de las estrategias) [x]
- Al final, calcular qué tan bien le fue a alguien (promedio de las nne) [x]
"""

"""
Estrategia proponer:

Input: un agente y un vecino

Cada agente puede acceder al historial de encuentros con su vecino
Cada gente puede acceder a su cantidad de vecinos
Cada agente puede acceder a su historial con otros vecinos?

Output es un número entre uno y nueve

Estrategia aceptar es igual pero el output es True o False

"""


class Agente:
    def __init__(self, id, estrategia_proponer, estrategia_aceptar, vecinos): 
        """
        ## Parametros:
            id: número asignado al agente
            estrategias: funcion que define que decisión tomar a partir de cierta información
            vecinos: lista de agentes vecinos
        """
        self.id = id
        self.estrategia_proponer = estrategia_proponer
        self.estrategia_aceptar = estrategia_aceptar
        self.vecinos = vecinos

        self.media_negociaciones = 0

        self.dinero_ganado = 0
        self.cantidad_negociaciones = 0

        self.hist_propuesto = defaultdict(list)
        self.hist_recibido  = defaultdict(list)

        """
        historial: diccionario de key: Agente vecino,
            value: lista de tupla (dinero propuesto/ofrecido, aceptado)
        """

    def __str__(self):
        return (f"Dinero Ganado: {self.dinero_ganado}\n"
                f"Cantidad de Negociaciones: {self.cantidad_negociaciones}\n"
                f"Fitness: {self.media_negociaciones}")

    def proponer(self, vecino):
        valor_ofrecido = self.estrategia_proponer(self, vecino) # elegir cuánto proponerle
        vecino_acepta = vecino.evaluar_oferta(self, valor_ofrecido) # mandarle al otro para que acepte o rechace
        
        if vecino_acepta:
            self.dinero_ganado += 10 - valor_ofrecido
        else:
            x=0 
        self.cantidad_negociaciones += 1
        self.hist_propuesto[vecino.id].append((valor_ofrecido, vecino_acepta))


    def evaluar_oferta(self, vecino, valor):
        aceptar = self.estrategia_aceptar(self, vecino, valor)
        if aceptar :
            self.dinero_ganado += valor
        else:
            x=0 
        self.cantidad_negociaciones += 1
        self.hist_recibido[vecino.id].append((valor, aceptar))
        return aceptar




