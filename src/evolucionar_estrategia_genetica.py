from genome import Genome, World
from genetic import *

from ultimatum import Ultimatum
import copy
import random

from genetic_counter_strategy import Genetico_counter

# Para testear interacción con ecológico
from ecologico import Ecologico
from agente import Agente 
from estrategias import *

def create_a_random_adjacency_list(n, k):
    edges = set()
    
    while len(edges) < k:
        u = random.randint(0, n-1)
        v = random.randint(0, n-1)
        if u != v:
            edge = tuple(sorted((u, v)))  # Sort the tuple to avoid (u, v) and (v, u) as different
            edges.add(edge)
    
    return list(edges)

def evolucionar_estrategia_genetica():
    
    world = World()
    seed_genoma_proponer = Genome(world, 4, 1)
    seed_genoma_aceptar = Genome(world, 5, 1)

    n_agentes = 70
    genomas = []
    for i in range(n_agentes):
        copia_proponer = seed_genoma_proponer.copy()
        copia_aceptar = seed_genoma_aceptar.copy()
        genomas.append((copia_proponer, copia_aceptar))
    
    topologia = create_a_random_adjacency_list(70, 500)

    mutaciones = {
        'n_sobrevivientes' : 20,
        'n_mutar_pesos' : 30,
        'p_mutar_peso' : 0.4,
        'p_gaussiana' : 0.6,
        'n_cruces' : 10,
        'n_nuevo_nodo' : 5,
        'n_nuevo_eje' : 5,
        'speciation' : False,
        'c1_distance' : 1,
        'c2_distance' : 1,
        'c3_distance' : 0.4,
        'cota_especiacion' : 4
    }
  
    genetico = Genetico(1000, 1000, genomas, 70, topologia, mutaciones)

    genetico.competir()

    return genetico.sobrevivientes[0], genetico.sobrevivientes

def implementa_recepcion_tacaña(genoma_aceptar):
    res = True
    for i in range(1, 10):
            for bool_1 in [True, False]:
                for j in range(1, 10):
                    for bool_2 in [True, False]:
                        for k in range(1, 10):
                            res = res and not genoma_aceptar.apply_network([i, bool_1, j, bool_2, k]) <= 0
    return res

def implementa_propuesta_tacaña(genoma_proponer):
    res = True
    for i in range(1, 10):
        for bool_1 in [True, False]:
            for j in range(1, 10):
                for bool_2 in [True, False]:
                    propuesta = genoma_proponer.apply_network([i, bool_1, j, bool_2])
                    if res <= 1:
                        propuesta = 1
                    if res > 9:
                        propuesta = 9
                    propuesta = round(propuesta)
                    res = res and propuesta == 1
    return res

def implementa_estrategia_tacaña(tupla_genomas):
    return implementa_propuesta_tacaña(tupla_genomas[0]) and implementa_recepcion_tacaña(tupla_genomas[1])

def alguno_implementa_estrategia_tacaña(lista_genomas):
    for genoma in lista_genomas:
        if implementa_estrategia_tacaña(genoma):
            return True, genoma
    return False, None

def diferencias_con_recepcion_tacaña(genoma):
    res = True
    for i in range(1, 10):
            for bool_1 in [True, False]:
                for j in range(1, 10):
                    for bool_2 in [True, False]:
                        for k in range(1, 10):
                            if genoma.apply_network([i, bool_1, j, bool_2, k]) <= 0:
                                 print([i, bool_1, j, bool_2, k])
    return res

def diferencias_con_propuesta_tacaña(genoma):
    res = True
    for i in range(1, 10):
            for bool_1 in [True, False]:
                for j in range(1, 10):
                    for bool_2 in [True, False]:
                        for k in range(1, 10):
                            if genoma.apply_network([i, bool_1, j, bool_2, k]) <= 0:
                                 print([i, bool_1, j, bool_2, k])
    return res