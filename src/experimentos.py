from ecologico import Ecologico
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics
from sklearn.metrics import r2_score

class Experimentos:
    def __init__(self, turnos, n_generaciones, n_agentes):
        self.n_turnos_por_generacion = turnos 
        self.n_generaciones = n_generaciones
        self.n_agentes = n_agentes


    def contar_ganador_n_veces(self, n_simulaciones, topologia, estrategias):
        eco = Ecologico(self.n_turnos_por_generacion, self.n_generaciones, estrategias, self.n_agentes, topologia)

        resultados_win = {estrat:0 for estrat in estrategias.keys()}
        for _ in range(n_simulaciones):
            historial_estrategias, _ = eco.competir()
            for estrat, value in historial_estrategias[-1].items():
                resultados_win[estrat] += value[2] / eco.n_agentes # value[2] es cantidad de agentes
            
        return resultados_win

    def graficar_proporcion_ganadores(self, cantidad_simulaciones, topologia, estrategias): 
        # Simulaciones
        result_wins_denso = self.contar_ganador_n_veces(cantidad_simulaciones, topologia, estrategias)

        # Calcular los porcentajes
        total_simulaciones = sum(result_wins_denso.values())
        porcentajes = [value / total_simulaciones * 100 for value in result_wins_denso.values()]

        # Crear un gráfico de pastel
        fig, ax = plt.subplots(figsize=(4, 4))

        wedges, texts = ax.pie(
            x=list(result_wins_denso.values()), 
            explode=[0.025] * len(estrategias),
            shadow=True, 
            labels=None
        )

        # Agregar leyenda
        ax.legend(
            wedges, 
            [f"{label} ({porcentaje:.1f}%)" for label, porcentaje in zip(result_wins_denso.keys(), porcentajes)],
            title="Estrategias", 
            loc="center left", 
            bbox_to_anchor=(1, 0, 0.5, 1)
        )

        ax.set_title(f'Proporción de Ganadores en {cantidad_simulaciones} simulaciones', loc='center')
        plt.show()


    # Evalúa para qué cantidad de agentes cambia la proporción en estrategias ganadoras
    # Las estrategias son tuplas de proponer y aceptar
    def criticalidad_ganador_dos_estrategias(self, estrategia_1, estrategia_2, topologia, 
                                             simulaciones, min_e1, max_e1, granularidad):
        
        i = min_e1

        cantidades_iniciales_e1 = []
        proporciones_ganadoras_e1 = []

        while i <= max_e1:
            estrategias = {
                "estrategia_1": (estrategia_1[0], estrategia_1[1], i),
                "estrategia_2": (estrategia_2[0], estrategia_2[1], self.n_agentes - i)
            }

            cantidades_iniciales_e1.append(i)
            proporcion_ganadora_e1 = self.contar_ganador_n_veces(simulaciones, topologia, estrategias)["estrategia_1"]
            proporciones_ganadoras_e1.append(proporcion_ganadora_e1 / simulaciones * 100)
            
            # print(f"Calculado para {i} agentes.")
            i += granularidad

        plt.figure(figsize=(10, 6))
        plt.plot(cantidades_iniciales_e1, proporciones_ganadoras_e1, marker='o', linestyle='-', color='b')

        plt.title('Proporción de Ganadores de Estrategia 1 vs Cantidades Iniciales de Estrategia 1')
        plt.xlabel('Cantidades Iniciales de Estrategia 1')
        plt.ylabel('Proporciones Ganadoras de Estrategia 1 (%)')
        plt.ylim(0, 100)
        plt.grid(True)
        plt.show()

    import statistics

    def obtener_variables_macroscopicas(self, estrategias, topologia):
        entorno = Ecologico(self.n_turnos_por_generacion, 1, estrategias, self.n_agentes, topologia)
        entorno.competir()
        ofertas = []
        for agente in entorno.ultimatum.agentes:
            for vecino_id, sus_ofertas in agente.hist_propuesto.items():
                for oferta in sus_ofertas:
                    ofertas.append(oferta)  # Append the offer to the list of offers
        
        # Extract the offered values
        valores_ofrecidos = [oferta[0] for oferta in ofertas]
        
        # Calculate median and mean of offered values
        mediana_ofrecida = statistics.median(valores_ofrecidos) if valores_ofrecidos else 0
        media_ofrecida = statistics.mean(valores_ofrecidos) if valores_ofrecidos else 0
        
        # Get the offers less than 5
        ofertas_menores_a_5 = [oferta for oferta in ofertas if oferta[0] < 5]
        
        # Get the percentage of offers less than 5 that were rejected
        rechazos_menores_a_5 = [oferta for oferta in ofertas_menores_a_5 if not oferta[1]]
        porcentaje_rechazos_menores_a_5 = (len(rechazos_menores_a_5) / len(ofertas_menores_a_5)) * 100 if ofertas_menores_a_5 else 0
        
        return mediana_ofrecida, media_ofrecida, porcentaje_rechazos_menores_a_5

    def obtener_variables_macroscopicas_rango(self, estrategia1, estrategia2, topologia, cantidad_inicial_e1, cantidad_final_e1, granularidad):
        medianas_ofrecidas = []
        medias_ofrecidas = []
        porcentajes_rechazos = []
        porcentajes_agentes_e1 = []

        i = cantidad_inicial_e1
        while i <= cantidad_final_e1:
            estrategias = {
                "A": (estrategia1[0], estrategia1[1], i),
                "B": (estrategia2[0], estrategia2[1], self.n_agentes - i)
            }
            mediana, media, porcentaje = self.obtener_variables_macroscopicas(estrategias, topologia)
            medianas_ofrecidas.append(mediana)
            medias_ofrecidas.append(media)
            porcentajes_rechazos.append(porcentaje)
            porcentajes_agentes_e1.append((i / self.n_agentes) * 100)  # Porcentaje de agentes con estrategia 1

            i += granularidad

        # Gráfico 1: Media y Mediana ofrecida
        plt.figure(figsize=(10, 5))
        plt.plot(porcentajes_agentes_e1, medias_ofrecidas, label='Media Ofrecida')
        plt.plot(porcentajes_agentes_e1, medianas_ofrecidas, label='Mediana Ofrecida')
        plt.xlabel('Porcentaje de Agentes con Estrategia 1')
        plt.ylabel('Valor Ofrecido')
        plt.title('Media y Mediana Ofrecida según Porcentaje de Agentes con Estrategia 1')
        plt.legend()
        plt.grid(True)
        plt.show()

        # Gráfico 2: Porcentaje de Rechazos de Ofertas Menores a 5
        plt.figure(figsize=(10, 5))
        plt.plot(porcentajes_agentes_e1, porcentajes_rechazos, label='Porcentaje de Rechazos (< 5)')
        plt.xlabel('Porcentaje de Agentes con Estrategia 1')
        plt.ylabel('Porcentaje de Rechazos')
        plt.title('Porcentaje de Rechazos de Ofertas Menores a 5 según Porcentaje de Agentes con Estrategia 1')
        plt.legend()
        plt.grid(True)
        plt.show()


    def graficar_evolucion_poblacional(self, estrategias, topologia, añadir_media_poblacional=False):
        entorno = Ecologico(self.n_turnos_por_generacion, self.n_generaciones, estrategias, self.n_agentes, topologia)
        historial_estrategias, vecinos_fitness = entorno.competir()
        data = [{key: value[2] for key, value in dic.items()} for dic in historial_estrategias]

        df = pd.DataFrame(data)

        if añadir_media_poblacional:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)
        else:
            fig, ax1 = plt.subplots(figsize=(8, 4))

        end = None
        
        for estrategia in df.columns:
            ax1.plot(df.index, df[estrategia], marker='', label=estrategia)
            if end is None:  # Solo si aún no hemos encontrado un n_agentes
                idx_n = df[estrategia][df[estrategia] == entorno.n_agentes].index
                if not idx_n.empty:
                    end = idx_n[0]
                    
        if end is None:
            end = entorno.n_generaciones

        ax1.set_xlim([0, end+1])
        ax1.set_xlabel('Generación')
        ax1.set_ylabel('Agentes por estrategia')
        ax1.set_title('Evolución de Ultimatum ecológico')
        ax1.legend()
        ax1.grid(True)

        if añadir_media_poblacional:
            df_medias = pd.DataFrame({"Media_puntos": entorno.media_total_de_puntos_por_generacion})
            ax2.plot(df_medias.index, df_medias['Media_puntos'], marker='', color='r')
            ax2.set_ylabel('Media de puntos')
            ax2.set_xlabel('Generación')
            ax2.legend(['Media de puntos'])
            ax2.grid(True)
            ax2.set_title('Media de puntaje poblacional')
                

        plt.tight_layout()
        plt.show()


    def graficar_puntos_ganados_array_estrategias(self, array_estrategias, topologia, añadir_fitted=False):
        # Para mostrar que igual es un óptimo global que haya 100 estrategias ratas
        puntos_ganados = []
        agentes_iniciales = []

        for i, estrategia in enumerate(array_estrategias):
            entorno = Ecologico(self.n_turnos_por_generacion, 1, estrategia, self.n_agentes, topologia)
            entorno.competir()
            agentes = entorno.ultimatum.agentes
            puntos_totales = sum(agente.dinero_ganado for agente in agentes)
            
            agentes_iniciales.append(i)
            puntos_ganados.append(puntos_totales)

        plt.figure(figsize=(10, 6))
        plt.scatter(agentes_iniciales, puntos_ganados, marker='o', color='white',
                    edgecolor='blue', alpha=0.8,label='Puntos por estrategia 2')

        if añadir_fitted:
            # hacemos regresion polinomica, no pude con scikit learn, le pedi a gpt
            z = np.polyfit(agentes_iniciales, puntos_ganados, 2)
            p = np.poly1d(z)
            plt.plot(agentes_iniciales, p(agentes_iniciales), linestyle='--', color='C1', label='Ajuste polinómico')

            # agrego r squared y rmse
            y_pred = p(agentes_iniciales)
            r2 = r2_score(puntos_ganados, y_pred)
            rmse = np.sqrt(np.mean((puntos_ganados - y_pred)**2)) # raiz de la media de los cuadrados de los errores
            
            plt.text(0.1, 0.85, f'R² = {r2:.4f}\nRMSE = {rmse:.4f}', transform=plt.gca().transAxes, fontsize=12)

        plt.title('Puntos ganados con más y menos agentes')
        plt.xlabel('Agentes con la estrategia 2')
        plt.ylabel('Puntos ganados en el ecosistema')
        plt.legend()
        plt.grid(True)
        plt.show()


    def puntos_segun_presencia_de_dos_estrategias(self, estrategia_1, estrategia_2, topologia, añadir_fitted=False):
        array_estrategias = []
        for i in range(self.n_agentes + 1):
            estrategias = {
                "Estrategia 1" : (estrategia_1[0], estrategia_1[1], self.n_agentes - i),
                "Estrategia 2" : (estrategia_2[0], estrategia_2[1], i)
            }
            array_estrategias.append(estrategias)

        self.graficar_puntos_ganados_array_estrategias(array_estrategias, topologia, añadir_fitted)