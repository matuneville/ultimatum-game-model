from genome import Genome, World
from ultimatum import Ultimatum
import numpy as np
import random

def apply_neural_network_propose(agente, vecino, genome):
    input = []
    hist_propuesto = agente.hist_propuesto[vecino.id]
    ultimos_3 = hist_propuesto[-3:]
    for i in range(len(ultimos_3)):
        input.append(ultimos_3[i][0])
        input.append(ultimos_3[i][1])
    result_softmax = genome.apply_network(input)
    chosen_index = random.choices(range(len(result_softmax)), weights=result_softmax, k=1)[0]
    return chosen_index + 1

def apply_neural_network_accept(agente, vecino, valor, genome):
    input = []
    input.append(valor)
    hist_recibido = agente.hist_recibido[vecino.id]
    ultimos_3 = hist_recibido[-3:]
    for i in range(len(ultimos_3)):
        input.append(ultimos_3[i][0])
        input.append(ultimos_3[i][1])
    result_softmax = genome.apply_network(input)
    # print(result_softmax)
    chosen_index = random.choices(range(len(result_softmax)), weights=result_softmax, k=1)[0]
    if chosen_index == 0:
        return True 
    else:
        return False

def strategy_propose(genome):
    strategy = lambda agente, vecino : apply_neural_network_propose(agente, vecino, genome)
    return strategy

def strategy_accept(genome):
    strategy = lambda agente, vecino, valor : apply_neural_network_accept(agente, vecino, valor, genome)
    return strategy

class Genetico:
    def __init__(self, n_turnos_por_generacion, n_generaciones, genomas, n_agentes, topologia, mutaciones):
        self.n_turnos_por_generacion = n_turnos_por_generacion
        self.n_generaciones = n_generaciones
        self.genomas = genomas
        self.fitness_genomas = []
        self.n_agentes = n_agentes
        self.topologia = topologia
        self.mutaciones = mutaciones
        

        """
        GENOMAS
        Los genomas son un array que contiene los genomas de cada agente según su id.
        Cada elemento es una tupla (genoma_proponer, genoma_aceptar)
        Ordenamos los genomas al azar antes de asignarlos a los agentes.
        
        MUTACIONES
        Las mutaciones son un diccionario que describe las propiedades de la reproducción. Contiene:
        {
            n_sobrevivientes -> el numero de agentes más exitosos que pasan a la siguiente generación.
            n_mutar_pesos ->  el porcentaje de agnetes que surge de mutar los pesos de la red neuronal.
            p_mutar_peso -> la probabilidad de mutar el peso de cada nodo en los agentes a los que les mutamos los pesos
            p_gaussiana -> la probabilidad de que, al mutar los pesos, se haga con distribución gaussiana (cambiar poco los pesos) en lugar de uniforme (cambiar mucho los pesos) -> he usado 0.8
            n_nuevo_nodo -> numero de agentes a los que se añade un nodo nuevo
            n_nuevo_eje -> numero de agentes a los que se añade una nueva conexión
            n_cruces -> numero de agentes que surge de cruzar dos genomas al azar
            
            speciation -> booleano que determina si hay especiación
            c1_distance -> parámetro de especiación
            c2_distance -> parámetro de especiación
            c3_distance -> parámetro de especiación
            cota_especies -> parámetro de especiación
        }
        
        """


    def setup_generacion(self, genomas):
        ultimatum = Ultimatum(self.topologia, self.n_agentes)

        agentes = ultimatum.agentes

        # Asignar al agente i el genoma i.
        for i in range(len(agentes)):
            agentes[i].estrategia_proponer = strategy_propose(genomas[i][0])
            agentes[i].estrategia_aceptar = strategy_accept(genomas[i][1])

        return ultimatum
    
    def generacion(self, genomas):
        # toma una lista de genomas
        # devuelve el fitness calculado de cada genoma

        ultimatum = self.setup_generacion(genomas)

        for i in range(self.n_turnos_por_generacion):
            ultimatum.turno()

        ultimatum.calculate_fitness()

        self.fitness_genomas = []

        for i in range(len(genomas)):
            # Por ahora, vamos sin especiación.
            self.fitness_genomas.append(ultimatum.agentes[i].media_negociaciones)
            # Cuando calcule el genetic distance, uso la suma de ambos, no? Sí, total es una combinación lineal de distancias.

    def reproduccion(self, mutaciones):
        # Ordenar genomas por fitness
        genomas = self.genomas
        fitness_genomas = self.fitness_genomas 
        
        # Combine genomas and fitness_genomas into a list of tuples (genoma, fitness)
        combined = list(zip(genomas, fitness_genomas))

        # Sort the combined list based on the fitness value, in descending order
        sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)
        
        # Extract the sorted genomas
        sorted_genomas = [genoma for genoma, fitness in sorted_combined]
        sorted_fitness = [fitness for genoma, fitness in sorted_combined]

        # Update the original arrays if needed
        genomas = sorted_genomas

        # Quedarse con el porcentaje de fitness mayor
        n_sobrevivientes = mutaciones['n_sobrevivientes']
        sobrevivientes = genomas[:n_sobrevivientes]
        self.sobrevivientes = sobrevivientes


        # Reproducirlos mutando los pesos solamente
            # En la reproducción, trato igual a los dos genomas (proponer y aceptar) -> simplemente hago lo mismo con ambos.
        pesos_mutados = []
        for i in range(mutaciones['n_mutar_pesos']):
            genes = random.choice(sobrevivientes)
            gen_proponer = genes[0].copy().alter_weights(mutaciones['p_mutar_peso'], mutaciones['p_gaussiana'])
            gen_aceptar = genes[1].copy().alter_weights(mutaciones['p_mutar_peso'], mutaciones['p_gaussiana'])
            pesos_mutados.append((gen_proponer, gen_aceptar))
        
        nodos_agregados = []
        for i in range(mutaciones['n_nuevo_nodo']):
            # elige al azar entre proponer y aceptar
            genes = random.choice(sobrevivientes)
            gen_proponer = genes[0].copy()
            gen_aceptar = genes[1].copy()
            if random.random() > 0.5:
                gen_proponer.add_node()
            else:
                gen_aceptar.add_node()
            nodos_agregados.append((gen_proponer, gen_aceptar))


        ejes_agregados = []
        for i in range(mutaciones['n_nuevo_eje']):
            # elige al azar entre proponer y aceptar
            genes = random.choice(sobrevivientes)
            gen_proponer = genes[0].copy()
            gen_aceptar = genes[1].copy()
            if random.random() > 0.5:
                gen_proponer.add_connection()
            else:
                gen_aceptar.add_connection()
            ejes_agregados.append((gen_proponer, gen_aceptar))


        cruces = []
        for i in range(mutaciones['n_cruces']):
            # cruza ambos
            genes_1 = random.choice(sobrevivientes)
            genes_2 = random.choice(sobrevivientes)
            gen_proponer_1 = genes_1[0].copy()
            gen_aceptar_1 = genes_1[1].copy()
            gen_proponer_2 = genes_2[0].copy()
            gen_aceptar_2 = genes_2[1].copy()
            cruce_proponer = gen_proponer_1.crossing(gen_proponer_2)
            cruce_aceptar = gen_aceptar_1.crossing(gen_aceptar_2)
            cruces.append((cruce_proponer, cruce_aceptar))
        
        
        nuevos_genomas = sobrevivientes + pesos_mutados + nodos_agregados + ejes_agregados + cruces
        self.genomas = nuevos_genomas
        
        # Reordenarlos al azar
        # Vaciar el fitness
        random.shuffle(nuevos_genomas)
        self.fitness_genomas = []
   
        return # Devolver el fitness máximo?
    
    def competir(self):
        for i in range(self.n_generaciones):
            self.generacion(self.genomas)
            self.reproduccion(self.mutaciones)
            if i % 10 == 0:
                print(f"generación {i} concluida.")
        
        return 
    
