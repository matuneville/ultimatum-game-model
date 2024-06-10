import random

def estrat_proponer_rand(agente, vecino): 
    return random.randint(1,9)

def estrat_aceptar_rand(agente, vecino, valor):
    return random.choice([True, False])

def estrat_aceptar_nunca(agente, vecino, valor):
    return 0

def estrat_proponer_promedio(agente, vecino):
    suma_aceptadas = 0
    aceptadas = 0
    encuentros = agente.hist_propuesto[vecino.id]
    

    for encuentro in encuentros:
        if encuentro[1]:
            aceptadas += 1
            suma_aceptadas += encuentro[0]

    if len(encuentros) == 0 or aceptadas == 0:
        return 5 + random.choice([-1,+1])
    
    promedio = suma_aceptadas / aceptadas
    return promedio + random.choice([-1,+1])

def estrat_aceptar_promedio(agente, vecino, valor):
    suma_aceptadas = 0
    aceptadas = 0
    encuentros = agente.hist_propuesto[vecino.id]

    for encuentro in encuentros:
        if encuentro[1]:
            aceptadas += 1
            suma_aceptadas += encuentro[0]

    if len(encuentros) == 0 or aceptadas == 0:
        return random.choice([True, False])
    
    promedio = suma_aceptadas / aceptadas
    return valor >= promedio

def estrat_rata(agente, vecino):
    return 1

def estrat_antirrata_proponer(agente, vecino):
    return 5

def estrat_antirrata_aceptar(agente,vecino,valor):
    return valor >= 3