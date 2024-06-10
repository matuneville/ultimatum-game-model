from ultimatum import Ultimatum
import numpy as np
import random

class Ecologico:
    def __init__(self, n_turnos_por_generacion, n_generaciones, estrategias, n_agentes, topologia):
        self.n_turnos_por_generacion = n_turnos_por_generacion
        self.n_generaciones = n_generaciones
        self.estrategias = estrategias
        self.n_agentes = n_agentes
        self.topologia = topologia
        self.lista_agentes_con_estrategia = {}

        """
        estrategias es un dict que contiene:
            -
            - la estrategia ofrecer
            - la estrategia aceptar
            - cuántos agentes la tienen
            - 
        """

    def setup_generacion(self, estrategias):
        ultimatum = Ultimatum(self.topologia, self.n_agentes)


        agentes = ultimatum.agentes.copy()
        agentes = np.random.permutation(agentes)
        
        # for i in range(5):
        #    print(ultimatum.agentes[i].id)
        #    print(agentes[i].id)

        start = 0
        for key, (estrategia_ofrecer, estrategia_aceptar, cantidad_agentes) in estrategias.items(): 
            end = int(start + cantidad_agentes) # start - end = cantidad de agentes siempre

            agentes_con_estrategia = agentes[start:end]

            for agente in agentes_con_estrategia:
                agente.estrategia_proponer = estrategia_ofrecer
                agente.estrategia_aceptar = estrategia_aceptar
            start = end

            self.lista_agentes_con_estrategia[key] = agentes_con_estrategia
        
        # self.lista_agentes_con_estrategia = lista_agentes_con_estrategia
        return ultimatum
    
    def generacion(self, estrategias): 
        # toma una lista de estrategias, devuelve el porcentaje del fitness total por estrategia
        # estrategias tiene diccionario
        # nombre_de_estrategias -> estrategia_proponer, estrategia_aceptar, q_agentes

        ultimatum = self.setup_generacion(estrategias)

        # Evolve
        for i in range(self.n_turnos_por_generacion):
            ultimatum.turno()

        # Calculate new population
        ultimatum.calculate_fitness()

        fitness_total = 0
        fitness_por_estrategia = {}

        for key, value in self.lista_agentes_con_estrategia.items():
            fitness_estrategia = 0
            for agente in value:
                fitness_estrategia += agente.media_negociaciones #
                # print(agente.id)
                # print(fitness_estrategia)
            # cantidad_agentes_con_estrategia = len(value)
            # fitness_estrategia = fitness_estrategia / cantidad_agentes_con_estrategia # Para evaluar qué tan bien le fue a la estrategia, vemos qué tan bien le fue en promedio.
            
            fitness_total += fitness_estrategia
            fitness_por_estrategia[key] = fitness_estrategia
        
        porcentaje_fitness_total_por_estrategia = {}

        for key,value in fitness_por_estrategia.items():
            porcentaje_fitness_total_por_estrategia[key] = value/fitness_total
        
        return porcentaje_fitness_total_por_estrategia


    def reasignar_estrategias(self, estrategias, porcentaje_fitness_total_por_estrategia):

        nuevas_estrategias = {} # nombre_estrategia -> estrategia_proponer, estrategia_aceptar, cantidad_agentes

        cantidad_agentes = 0

        nombres_estrategias = list(estrategias.keys())

        for key in nombres_estrategias:
            cantidad = round(self.n_agentes * porcentaje_fitness_total_por_estrategia[key], 0)
            cantidad_agentes += cantidad
            nuevas_estrategias[key] = (estrategias[key][0], estrategias[key][1], cantidad) # 

        diferencia = cantidad_agentes - self.n_agentes


        while(diferencia > 0):
            
            clave = random.choice(nombres_estrategias)
            if(nuevas_estrategias[clave][2] > 0):
                estrategia_list = list(nuevas_estrategias[clave])
                # Modify the element
                estrategia_list[2] += 1
                # Convert the list back to a tuple
                nuevas_estrategias[clave] = tuple(estrategia_list)                
                diferencia -= 1
            

        while(diferencia < 0):
            clave = random.choice(nombres_estrategias)
            if(nuevas_estrategias[clave][2] < 100):
                estrategia_list = list(nuevas_estrategias[clave])
                # Modify the element
                estrategia_list[2] += 1
                # Convert the list back to a tuple
                nuevas_estrategias[clave] = tuple(estrategia_list)
                diferencia += 1
            
        return nuevas_estrategias

    def print_poblaciones(self, estrategias):
        for key, value in estrategias.items():
            print(f"Cantidad de estrategias {key}: {estrategias[key][2]}")

    def competir(self, estrategias_iniciales):
        estrategias_asignadas = estrategias_iniciales

        self.print_poblaciones(estrategias_asignadas)

        for i in range(self.n_generaciones):
            resultados = self.generacion(estrategias_asignadas) # En principio esto lo podríamos hacer más de una vez para tener un número más robusto pero bueno, la idea de esto es evitar oscilaciones
            estrategias_asignadas = self.reasignar_estrategias(estrategias_asignadas, resultados)
            self.print_poblaciones(estrategias_asignadas)
        
        return estrategias_asignadas
