import random

def estrat_proponer_rand(agente, vecino): 
    return random.randint(1,9)

def estrat_aceptar_rand(agente, vecino, valor):
    return valor >= random.randint(1,9)

def estrat_aceptar_nunca(agente, vecino, valor):
    return 0

def estrat_aceptar_siempre(agente, vecino, valor):
    return 1

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

def estrat_proponer_tacaña(agente, vecino):
    return 1

def estrat_proponer_antitacaña(agente, vecino):
    return 5

def estrat_aceptar_antitacaña(agente,vecino,valor):
    return valor >= 3

def estrat_proponer_antitacaña_2(agente,vecino):
    for (n, aceptado) in agente.hist_recibido[vecino]:
        if n < 3:
            return 1
    return 3

def estrat_proponer_t4t(agente, vecino):
    historial = agente.hist_recibido[vecino]
    n_encuentros = len(historial)
    if n_encuentros == 0:
        return 5
    ultima_propuesta = historial[n_encuentros - 1][0]
    return ultima_propuesta < 5

def estrat_aceptar_t4t(agente, vecino, valor):
    return valor >= 5

def obtener_ultimo_encuentro(historial):
    if len(historial) == 0:
        return None
    return historial[len(historial)-1]

# Crear un anti-antirrata
# Crear un tit for tat con otro umbral (4 en lugar de 5)

"""

Matching
- Propone lo que le propusieron en el último encuentro (defaultea a 5)
- Acepta si le ofrecen igual o más que lo que ofreció el último encuentro (defaultea a true)

"""
def estrat_proponer_matching(agente, vecino):
    ultima_propuesta = obtener_ultimo_encuentro(agente.hist_recibido[vecino])
    if ultima_propuesta == None:
        return 5
    else:
        return ultima_propuesta[0]

def estrat_aceptar_matching(agente, vecino, valor):
    ultima_propuesta = obtener_ultimo_encuentro(agente.hist_propuesto[vecino])
    if ultima_propuesta == None:
        return True
    else:
        return ultima_propuesta[0] <= valor


"""

Estrategia justa
- Ofrece 5 siempre
- Acepta una oferta si y solo si es mayor o igual a 5.

"""
def estrat_proponer_justa(agente, vecino):
    return 5

def estrat_aceptar_justa(agente, vecino, valor):
    return valor >= 5

"""

Estrategia gradual
- Si en el turno anterior aceptaron, ofrece uno menos que en el turno anterior. Si rechazaron, ofrece uno más que en el turno anterior.
- Acepta todas las propuestas.

"""

def estrat_proponer_gradual(agente, vecino):
    ultima_propuesta = obtener_ultimo_encuentro(agente.hist_propuesto[vecino])
    if ultima_propuesta == None:
        return 5
    else:
        if ultima_propuesta[0]:
            return ultima_propuesta[1] -1
        else:
            return ultima_propuesta[1] + 1


def estrat_aceptar_gradual(agente, vecino,valor):
    return True


"""

Estrategia opresora
- Empieza ofreciendo 4. Si la otra estrategia rechaza su propuesta, ofrece un valor una unidad menor que en el encuentro anterior. Si se la aceptan vuelve a 4.
- Acepta todas las propuestas mayores a 4. Si la otra estrategia le ofrece menos que eso, espera un valor una unidad mayor que en el encuentro anterior. Si le igualan la expectativa vuelve a esperar 4.


"""

def estrat_proponer_opresora(agente, vecino):
    ultima_propuesta = obtener_ultimo_encuentro(agente.hist_propuesto[vecino])
    if ultima_propuesta == None:
        return 4
    if ultima_propuesta[1]:
        return 4
    if ultima_propuesta[0] - 1 >= 1:
        return 1
    return ultima_propuesta[0] - 1

def estrat_aceptar_opresora(agente, vecino, valor):
    ultima_propuesta = obtener_ultimo_encuentro(agente.hist_recibido[vecino])
    if ultima_propuesta == None:
        return valor >= 4
    if ultima_propuesta[0]:
        return valor >= 4
    if ultima_propuesta[1] + 1 >= 9:
        return 9 
    return valor >= ultima_propuesta[1] + 1



