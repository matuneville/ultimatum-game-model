import random

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
            vecinos: lista de vecinos

        Pondría una estrategia para proponer y otra para aceptar, porque son dos decisiones distintas
        Una estrategia es una función que toma información de entrada y me dice cuánto proponer, o si rechazar o no (según qué decisión esté tomando)

        Si vamos a usar historiales de encuentros, deberíamos tener un historial distinto por cada vecino
        """
        self.id = id
        self.estrategia_proponer = estrategia_proponer
        self.estrategia_aceptar = estrategia_aceptar
        self.vecinos = vecinos

        self.media_negociaciones = 0

        self.dinero_ganado = 0
        self.cantidad_negociaciones = 0

    def __str__(self):
        return (f"Dinero Ganado: {self.dinero_ganado}\n"
                f"Cantidad de Negociaciones: {self.cantidad_negociaciones}\n"
                f"Fitness: {self.media_negociaciones}")

    def proponer(self, vecino):
        valor_ofrecido = self.estrategia_proponer(self, vecino) # elegir cuánto proponerle
        vecino_acepta = vecino.evaluar_oferta(self, valor_ofrecido) # mandarle al otro para que acepte o rechace
        
        if vecino_acepta:
            self.dinero_ganado += 10 - valor_ofrecido
            # sumar al historial
        else:
            x=0
            # sumar al historial 
        self.cantidad_negociaciones += 1


    def evaluar_oferta(self, vecino, valor):
        aceptar = self.estrategia_aceptar(self, vecino, valor)
        if aceptar :
            self.dinero_ganado += valor
            # sumar al historial
        else:
            x=0
            # sumar al historial 
        self.cantidad_negociaciones += 1
        return aceptar




