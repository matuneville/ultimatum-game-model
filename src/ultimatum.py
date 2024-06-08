import random
from agente import Agente

"""
Necesitamos:

- Estructura para representar el grafo
- Elegir quiénes van a comerciar
- Decisiones posibles (de cuánto ofrecer y cuándo rechazar)
- Llamar a una función dummy "estrategia" que te diga qué elegir, que todavía no haga nada o te devuelva algo al azar. Después de tener la estructura lista definimos cómo encarar el tema de las estrategias)
- Al final, calcular qué tan bien le fue a alguien (promedio de las nne)
"""

def estrategia_proponer_dummy(agente, vecino):
    return random.randint(1,9)

def estrategia_aceptar_dummy(agente, vecino, valor):
    return random.choice([True, False])

class Ultimatum:

    def __init__(self, lista_aristas, n):
        """
        """
        self.n = n
        self.lista_aristas = lista_aristas
        self.agentes = self.setup(lista_aristas, n)


    def setup(self, lista_aristas, n): 
        agentes = []
        for i in range(n):
            agentes.append(Agente(i,estrategia_proponer_dummy, estrategia_aceptar_dummy, []))
            
        for (id_1, id_2) in lista_aristas:
            agentes[id_2].vecinos.append(agentes[id_1])
            agentes[id_1].vecinos.append(agentes[id_2])

        return agentes

    def turno(self): 
        (vecino_id, propone_id) = random.choice(self.lista_aristas)
        propone = self.agentes[propone_id]
        vecino = self.agentes[vecino_id]

        # propone = random.choice(self.agentes)
        # vecino = random.choice(propone.vecinos)
        propone.proponer(vecino)
    
    def calculate_fitness(self):
        for agente in self.agentes:
            if(agente.cantidad_negociaciones > 0):
                agente.media_negociaciones = round(agente.dinero_ganado / agente.cantidad_negociaciones, 2)

    
