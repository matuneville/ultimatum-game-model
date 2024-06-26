from ecologico import Ecologico
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Experimentos:
    def __init__(self, turnos, n_generaciones, n_agentes):
        self.n_turnos_por_generacion = turnos 
        self.n_generaciones = n_generaciones
        self.n_agentes = n_agentes

    def set_global_parameters(turnos, generaciones, agentes):
        n_turnos_por_generacion = turnos
        n_generaciones = generaciones
        n_agentes = agentes

    def contar_ganador_n_veces(self, n_simulaciones, topologia, estrategias):
        eco = Ecologico(self.n_turnos_por_generacion, self.n_generaciones, estrategias, self.n_agentes, topologia)

        resultados_win = {estrat:0 for estrat in estrategias.keys()}
        for _ in range(n_simulaciones):
            historial_estrategias, _ = eco.competir()
            for estrat, value in historial_estrategias[-1].items():
                resultados_win[estrat] += value[2] / eco.n_agentes # value[2] es cantidad de agentes
            
        return resultados_win

    def graficar_proporcion_ganadores(self, cantidad_simulaciones, topologia, estrategias): 
        # n_turnos_por_generacion, n_generaciones, estrategias, n_agentes, topologia

        simulaciones = cantidad_simulaciones
        result_wins_denso = self.contar_ganador_n_veces(cantidad_simulaciones, topologia, estrategias)

        # Create a single pie chart
        fig, ax = plt.subplots(figsize=(4, 4))

        ax.pie(x=list(result_wins_denso.values()), explode=[0.025]*len(estrategias),
            labels=[label if value > 0 else '' for label, value in result_wins_denso.items()],
            shadow=True)
        ax.text(-1.2, -2, f"Cantidad de simulaciones: {simulaciones},\n"
                        f"con {self.n_generaciones} generaciones de {self.n_agentes} agentes,\n"
                        f"con {len(topologia)} aristas entre agentes,\n"
                        f"{self.n_turnos_por_generacion} turnos por generacion")
        ax.set_title('Proporción de Ganadores')

        plt.show()

    # Evalúa para qué cantidad de agentes cambia la proporción en estrategias ganadoras
    # Las estrategias son tuplas de proponer y aceptar
    def criticalidad_ganador_dos_estrategias(self, estrategia_1, estrategia_2, topologia, iteraciones, min_e1, max_e1, granularidad):

        
        i = min_e1

        cantidades_iniciales_e1 = []
        proporciones_ganadoras_e1 = []

        while i <= max_e1:

            estrategias = {
                "estrategia_1" : (estrategia_1[0], estrategia_1[1], i),
                "estrategia_2" : (estrategia_2[0], estrategia_2[1], self.n_agentes - i)
            }

            cantidades_iniciales_e1.append(i)
            proporcion_ganadora_e1 = self.contar_ganador_n_veces(iteraciones, topologia, estrategias)["estrategia_1"]
            proporciones_ganadoras_e1.append(proporcion_ganadora_e1)
            
            print(f"Calculado para {i} agentes.")

            i += granularidad


        plt.figure(figsize=(10, 6))
        plt.plot(cantidades_iniciales_e1, proporciones_ganadoras_e1, marker='o', linestyle='-', color='b')

        plt.title('Proporción de Ganadores de Estrategia 1 vs Cantidades Iniciales de Estrategia 1')
        plt.xlabel('Cantidades Iniciales de Estrategia 1')
        plt.ylabel('Proporciones Ganadoras de Estrategia 1')
        plt.grid(True)
        plt.show()


    def graficar_evolucion_poblacional(self, estrategias, topologia):
        entorno = Ecologico(self.n_turnos_por_generacion, self.n_generaciones, estrategias, self.n_agentes, topologia)
        historial_estrategias, vecinos_fitness = entorno.competir()
        data = [{key: value[2] for key, value in dic.items()} for dic in historial_estrategias]

        df = pd.DataFrame(data)


        plt.figure(figsize=(10, 4))
        end = None
        for estrategia in df.columns:
            plt.plot(df.index, df[estrategia], marker='.', label=estrategia)
            if end is None:  # Solo si aún no hemos encontrado un n_agentes
                idx_n = df[estrategia][df[estrategia] == entorno.n_agentes].index
                if not idx_n.empty:
                    end = idx_n[0]
                    
        if end == None:
            end = entorno.n_generaciones

        plt.xlim([0,end+1])
        plt.xlabel('Generación')
        plt.ylabel('Agentes por estrategia')
        plt.title('Evolución de Ultimatum ecológico')
        plt.legend()
        plt.grid(True)
        plt.show()