import random

def estrat_proponer_rand(agente, vecino): 
    return random.randint(1,9)

def estrat_aceptar_rand(agente, vecino, valor):
    return random.choice([True, False])

def estrat_aceptar_nunca(agente, vecino, valor):
    return 0