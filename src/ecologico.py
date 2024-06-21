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
        estrategias es un dict de key: nombre de la estrategia, y value:
            - la estrategia ofrecer
            - la estrategia aceptar
            - cuántos agentes la tienen
        """

    def setup_generacion(self, estrategias):
        ultimatum = Ultimatum(self.topologia, self.n_agentes)

        agentes = ultimatum.agentes.copy()
        agentes = np.random.permutation(agentes)

        start = 0
        # Agarra el dict de estrategias, que contiene cuantos agentes adoptan cada estrategia, 
        # y reparte las estrategias al azar entre los agentes
        for key, (estrategia_ofrecer, estrategia_aceptar, cantidad_agentes) in estrategias.items(): 
            end = int(start + cantidad_agentes) # start - end = cantidad de agentes siempre

            agentes_con_estrategia = agentes[start:end]

            for agente in agentes_con_estrategia:
                agente.estrategia_proponer = estrategia_ofrecer
                agente.estrategia_aceptar = estrategia_aceptar
            start = end

            # Lista_agentes_con_estrategia es un dict va a rastrear qué agentes tienen cada estrategia
            # La clave es el nombre de la estrategia, y el valor es un array de agentes.
            self.lista_agentes_con_estrategia[key] = agentes_con_estrategia
        
        # self.lista_agentes_con_estrategia = lista_agentes_con_estrategia
        return ultimatum
    
    def generacion(self, estrategias): 
        """
        Toma una lista de estrategias y devuelve el porcentaje del fitness total por estrategia luego de generar n turnos en el modelo.
        """

        ultimatum = self.setup_generacion(estrategias)

        # Evolve
        for i in range(self.n_turnos_por_generacion):
            ultimatum.turno()

        # Calculate new population
        ultimatum.calculate_fitness()

        # Acá ya tenemos el fitness de cada agente.
        # Para calcular el fitness de la estrategia A, lo que hacemos es:
        # Sumar el fitness de todos los agentes con estrategia A
        # Dividirlo por el total de puntos sumados por TODOS los agentes que jugaron
        # Este valor lo vamos a usar para actualizar las poblaciones. 
        # El valor que calculamos será la cantidad de agentes que use la estrategia A en la próxima generación.
        # Esto está tomado de Robert Axelrod.

        # Fitness agregado de todos los agentes del juego
        fitness_total = 0

        # Nuevo diccionario, que va a tener el nombre de la estrategia y el fitness de la estrategia
        fitness_por_estrategia = {}

        for nombre_estrategia, value in self.lista_agentes_con_estrategia.items():
            fitness_estrategia = 0
            for agente in value:
                fitness_estrategia += agente.media_negociaciones
            
            fitness_total += fitness_estrategia
            fitness_por_estrategia[nombre_estrategia] = fitness_estrategia
        
        porcentaje_fitness_total_por_estrategia = {}

        for key,value in fitness_por_estrategia.items():
            porcentaje_fitness_total_por_estrategia[key] = value/fitness_total
        
        return porcentaje_fitness_total_por_estrategia


    def reasignar_estrategias(self, estrategias, porcentaje_fitness_total_por_estrategia):
        """
        Actualizo self.estrategias en base al resultado de la funcion self.generacion.
        Conceptualmente, actualizo las poblaciones según qué tan bien le fue a cada estrategia.
        """
        nuevas_estrategias = {} # nombre_estrategia -> estrategia_proponer, estrategia_aceptar, cantidad_agentes

        cantidad_agentes = 0

        nombres_estrategias = list(estrategias.keys())

        for key in nombres_estrategias:
            cantidad = round(self.n_agentes * porcentaje_fitness_total_por_estrategia[key], 0)
            cantidad_agentes += cantidad
            nuevas_estrategias[key] = (estrategias[key][0], estrategias[key][1], cantidad) # 

        diferencia = cantidad_agentes - self.n_agentes

        # Aca sorteo estrategias en los agentes restantes sin estrategias asignadas (por problemas de redondeo)
        while(diferencia > 0):
            clave = random.choice(nombres_estrategias)
            if(nuevas_estrategias[clave][2] > 0):
                estrategia_list = list(nuevas_estrategias[clave])
                estrategia_list[2] += 1
                nuevas_estrategias[clave] = tuple(estrategia_list)                
                diferencia -= 1

        while(diferencia < 0):
            clave = random.choice(nombres_estrategias)
            if(nuevas_estrategias[clave][2] < 100):
                estrategia_list = list(nuevas_estrategias[clave])
                estrategia_list[2] += 1
                nuevas_estrategias[clave] = tuple(estrategia_list)
                diferencia += 1
            
        return nuevas_estrategias

    def print_poblaciones(self, estrategias):
        for key, value in estrategias.items():
            print(f"#Agentes con {key}: {estrategias[key][2]}")
        print("\n")

    def competir(self):
        estrategias = self.estrategias
        historial_estrategias = [estrategias]

        for i in range(self.n_generaciones):
            resultados = self.generacion(estrategias)
            estrategias = self.reasignar_estrategias(estrategias, resultados)
            historial_estrategias.append(estrategias)
        
        return historial_estrategias
