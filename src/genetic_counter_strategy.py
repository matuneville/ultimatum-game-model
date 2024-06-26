from genome import Genome, World
from ecologico import Ecologico
from ultimatum import Ultimatum
import numpy as np
import random
import math

def apply_neural_network_propose(agente, vecino, genome):
    input = []
    hist_propuesto = agente.hist_propuesto[vecino.id]
    ultimos_2 = hist_propuesto[-2:]
    for i in range(len(ultimos_2)):
        input.append(ultimos_2[i][0])
        input.append(ultimos_2[i][1])
    input.reverse()
    while len(input) < 4:
        input.append(0)

    result = genome.apply_network(input)
    if result < 1:
        return 1
    if result > 10:
        return 10
    return round(result)

    """
    result_softmax = genome.apply_network(input)
    chosen_index = random.choices(range(len(result_softmax)), weights=result_softmax, k=1)[0]
    return chosen_index + 1
    """

def apply_neural_network_accept(agente, vecino, valor, genome):
    value = [valor]
    history = []
    hist_recibido = agente.hist_recibido[vecino.id]
    ultimos_2 = hist_recibido[-2:]
    for i in range(len(ultimos_2)):
        history.append(ultimos_2[i][0])
        history.append(ultimos_2[i][1])
    
    history.reverse()
    while len(history) < 4:
        history.append(0)
    
    result = genome.apply_network(value + history)
    if result < 0:
        return False 
    else:
        return True
    """
    result_softmax = genome.apply_network(value + history)
    # print(result_softmax)

    chosen_index = random.choices(range(len(result_softmax)), weights=result_softmax, k=1)[0]
    if chosen_index == 0:
        return True 
    else:
        return False
    """

def strategy_propose(genome):
    strategy = lambda agente, vecino : apply_neural_network_propose(agente, vecino, genome)
    return strategy

def strategy_accept(genome):
    strategy = lambda agente, vecino, valor : apply_neural_network_accept(agente, vecino, valor, genome)
    return strategy

class Genetico_counter:
    def __init__(self, n_turnos_por_generacion, n_generaciones, genomas, mutaciones, n_agentes, target, bool_ecosystem, n_generaciones_ecologico=50, n_agentes_ecologico = 100, topologia=[], stop_when_extint=[]):
        self.n_turnos_por_generacion = n_turnos_por_generacion
        self.n_generaciones = n_generaciones
        self.genomas = genomas
        self.fitness_genomas = []
        self.mutaciones = mutaciones
        self.species_member_count = [n_agentes]
        self.mejor_fitness = 0
        self.target = target
        self.bool_ecosystem = bool_ecosystem

        self.n_generaciones_ecologico = n_generaciones_ecologico 
        self.n_agentes_ecologico = n_agentes_ecologico
        self.topologia = topologia
        self.stop_when_extint = stop_when_extint
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
    def generacion_single_strategy(self, genomas):
        # toma una lista de genomas
        # devuelve el fitness calculado de cada genoma

        self.fitness_genomas = []

        for genoma in genomas:
            ultimatum = Ultimatum([(0, 1)], 2)
            
            ultimatum.agentes[0].estrategia_proponer = strategy_propose(genoma[0])
            ultimatum.agentes[0].estrategia_aceptar = strategy_accept(genoma[1])

            ultimatum.agentes[1].estrategia_proponer = self.target[0]
            ultimatum.agentes[1].estrategia_aceptar = self.target[1]
            
            # self.setup_generacion(genomas)

            for i in range(self.n_turnos_por_generacion):
                ultimatum.turno()

            ultimatum.calculate_fitness()

            self.fitness_genomas.append(ultimatum.agentes[0].media_negociaciones)

        if self.mutaciones['speciation']:
            self.update_fitness_by_species(self.genomas, self.fitness_genomas)

        # print(self.fitness_genomas)
        return self.fitness_genomas
    
    def generacion_ecosystem(self, genomas):

        self.fitness_genomas = []

        agentes_totales = 0
        for key, value in self.target.items():
            agentes_totales += value[2]
        
        agentes_extra = self.n_agentes_ecologico - agentes_totales
        

        for genoma in genomas:
            estrategias = self.target
            estrategias["genetica"] = (strategy_propose(genoma[0]), strategy_accept(genoma[1]), agentes_extra)

            ecologico = Ecologico(self.n_turnos_por_generacion, self.n_generaciones_ecologico, estrategias, self.n_agentes_ecologico, self.topologia, ["genetica"])
            ecologico.competir()

            trayectoria_fitness = ecologico.fitness_estrategias_por_generacion['genetica']
            
            fitness_promedio = np.mean(trayectoria_fitness)
            self.fitness_genomas.append(fitness_promedio*math.log(len(trayectoria_fitness)))
            # print(f"Salió un genoma con fitness {fitness_promedio}")
        
        if self.mutaciones['speciation']:
            self.update_fitness_by_species(self.genomas, self.fitness_genomas)

        return self.fitness_genomas


    def assign_species(self, genomes):
        c1 = self.mutaciones['c1_distance']
        c2 = self.mutaciones['c2_distance']
        c3 = self.mutaciones['c3_distance']

        cota_especiacion = self.mutaciones['cota_especiacion']

        species_representatives = []
        species_member_count = []
        genome_species = []
        

        for i in range(len(genomes)):
            for j in range(len(species_representatives)):
                # Calculate distances
                distancia_proponer = genomes[i][0].genetic_distance(species_representatives[j][0], c1, c2, c3)
                distancia_aceptar = genomes[i][1].genetic_distance(species_representatives[j][1], c1, c2, c3)
                
                # Check if the genome should be assigned to the current species representative
                if distancia_proponer + distancia_aceptar < cota_especiacion:
                    genome_species.append(j)  # Assign the genome to species j
                    species_member_count[j] += 1  # Increment the species member count
                    break  # Break out of the inner loop and continue with the next i
                
            else:
                # This else block executes if the inner loop did not break,
                # meaning the genome did not fit into any existing species
                
                species_representatives.append(genomes[i])  # Add this genome as a new species representative
                species_member_count.append(1)  # Initialize the member count for this new species
                
                genome_species.append(len(species_representatives) - 1)  # Assign this genome to the new species
                self.species_member_count = species_member_count
        return genome_species, species_member_count


    def update_fitness_by_species(self, genomes, fitnesses):
        genome_species, species_member_count = self.assign_species(genomes)

        updated_fitnesses = []

        for i in range(len(fitnesses)):
            species = genome_species[i]
            member_count = species_member_count[species]
            updated_fitness = fitnesses[i]/member_count
            updated_fitnesses.append(updated_fitness)
    
        self.fitness_genomas = updated_fitnesses

        return updated_fitnesses


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

        self.mejor_fitness = sorted_fitness[0]
        # Update the original arrays if needed
        genomas = sorted_genomas
        # print(f"El fitness del primero es {sorted_fitness[0]}")
        # print(f"El fitness del treinta es {sorted_fitness[29]}")
        # print(f"El fitness del sesenta es {sorted_fitness[59]}")
        
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
        mod = 10
        if self.bool_ecosystem:
            mod = 1

        for i in range(self.n_generaciones):
            if self.bool_ecosystem:
               self.generacion_ecosystem(self.genomas) 
            else: 
                self.generacion_single_strategy(self.genomas)
            self.reproduccion(self.mutaciones)

            if i % mod == 0:
                print(f"generación {i} concluida.")
                print(f"Mejor fitness: {self.mejor_fitness}")
                print(f"Poblaciones: {self.species_member_count}")
        
        return 
    
    
    
