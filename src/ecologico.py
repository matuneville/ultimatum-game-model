from ultimatum import Ultimatum
import random

class Ecologico:
    def __init__(self, n_turnos_por_generacion, n_generaciones, estrategias, n_agentes, topologia):
        self.n_turnos_por_generacion = n_turnos_por_generacion
        self.n_generaciones = n_generaciones
        self.estrategias = estrategias 
        self.n_agentes = n_agentes
        self.topologia = topologia 

    # estrategias es un dict que contiene:
    # - el id del par de estrategias
    # - la estrategia ofrecer
    # - la estrategia aceptar
    # - cuántos agentes la tienen


    
    def generacion(self, estrategias): # toma una lista de estrategias, devuelve la lista de estrategias actualizada

        # Setup

        ultimatum = Ultimatum(self.topologia, self.n_agentes)
        agentes = ultimatum.agentes 

        random.shuffle(agentes)

        lista_agentes_con_estrategia = {}

        start = 0
        for key, value in estrategias: 
            (estrategia_ofrecer, estrategia_aceptar, cantidad_agentes) = value
            end = start + cantidad_agentes
            agentes_con_estrategia = agentes[start:end]
            lista_agentes_con_estrategia[key] = agentes_con_estrategia

            for agente in agentes_con_estrategia:
                agente.estrategia_proponer = estrategia_ofrecer
                agente.estrategia_aceptar = estrategia_aceptar
            start = end

        # Evolve

        for i in range(self.n_turnos_por_generacion):
            ultimatum.turno()

        # Calculate new population

        ultimatum.calculate_fitness()

        fitness_total = 0
        fitness_por_estrategia = {}
        for key, value in lista_agentes_con_estrategia:
            fitness_estrategia = 0
            for agente in value:
                fitness_estrategia += agente.media_negociaciones
            fitness_total += fitness_estrategia
            fitness_por_estrategia[key] = fitness_estrategia
        
        for key,value in fitness_por_estrategia:
            fitness_por_estrategia[key] = value/fitness_total

        nuevas_estrategias = {}

        for key, value in estrategias:
            cantidad = round(self.n_agentes * fitness_por_estrategia[key])
            nuevas_estrategias[key] = (estrategias[key][0], estrategias[key][1], cantidad)

        return nuevas_estrategias




