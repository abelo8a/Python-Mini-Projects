# 🔬 Bloques Game - Laboratorio Experimental de IA

Esta es la tercera fase y versión definitiva del proyecto. El sistema evoluciona de un entorno interactivo a un **banco de pruebas automatizado (*Benchmark*)** diseñado para auditar, recopilar estadísticas y comparar de forma masiva el rendimiento de tres algoritmos diferentes de toma de decisiones.

## 🚀 Características Avanzadas (Fase 3)

*   **Motor de Simulación en Segundo Plano:** El menú superior `Experimento -> Correr Benchmark` permite ejecutar **50 partidas consecutivas por cada algoritmo** (150 partidas en total). La simulación corre en memoria a la velocidad máxima del procesador, suspendiendo el renderizado gráfico para optimizar el cómputo.
*   **Entorno de Pruebas Simétrico (Fair Testing):** Para garantizar un análisis matemáticamente justo, el sistema genera 50 matrices iniciales idénticas. Los tres algoritmos se enfrentan exactamente a los mismos escenarios aleatorios.
*   **Discriminación Anti-Bucles:** Se implementó una lógica de selección absoluta mediante la función `max()` con llaves de desempate basadas en coordenadas indexadas. Esto previene que la IA se cicle en tableros altamente simétricos, evitando desbordamientos de memoria en entornos como PyCharm.
*   **Persistencia de Analítica:** Al finalizar las 150 pruebas, el sistema procesa los promedios matemáticos y exporta automáticamente un archivo estructurado llamado `reporte_algoritmos.txt`.

## 🤖 Algoritmos Evaluados

1.  **Greedy (Codicioso):** Escanea el tablero y selecciona estrictamente el grupo de bloques adyacentes de mayor tamaño en el turno actual, buscando la recompensa exponencial inmediata.
2.  **Heurístico (Limpieza de Cimientos):** Prioriza la destrucción de los grupos válidos ubicados en las filas más bajas del tablero (eje Y profundo), intentando desestabilizar la base para provocar caídas masivas uniformes.
3.  **Random (Línea Base/Control):** Elige una combinación válida de al menos 2 bloques de forma completamente aleatoria, sirviendo como métrica de control frente a las decisiones lógicas.

---

## 📊 Reporte Estadístico del Benchmark (50 Tests)

Tras ejecutar el análisis masivo en segundo plano, se obtuvieron los siguientes resultados empíricos reales:

| Algoritmo | Promedio de Puntos | Bloques Atrapados Promedio | Eficiencia en Limpieza |
| :--- | :---: | :---: | :--- |
| **🤖 Random** | **8,468.0** | **18.20** | **Ganador Absoluto 🏆** |
| **🤖 Greedy** | 7,888.0 | 22.44 | Rendimiento Medio |
| **🤖 Heurístico** | 6,850.0 | 25.32 | Menor Eficiencia |

### 🧠 Interpretación y Conclusiones Científicas

Los datos arrojaron una anomalía de software fascinante que contradice la hipótesis inicial de diseño: **El Azar (*Random*) derrotó a ambas lógicas inteligentes.**

1.  **La Paradoja del Azar (Efecto Homogeneización):** El algoritmo *Random* resultó ser el más eficiente en este entorno. Al destruir de manera caótica grupos pequeños distribuidos uniformemente por toda la matriz de 10x10, altera constantemente la estructura de las columnas. Esto provoca un "efecto cascada continuo" que, de forma involuntaria, junta bloques dispersos hacia las fases finales del juego, maximizando el descarte y dejando solo **18.20 bloques atrapados** en promedio.
2.  **El Límite de la Heurística de Cimientos:** Forzar al bot a limpiar obsesivamente la base (filas inferiores) fragmenta la caída vertical de las columnas superiores de manera prematura. Esto impide que los bloques superiores se consoliden en cúmulos grandes antes de descender, aislando piezas individuales y elevando el estancamiento a **25.32 bloques atrapados** (el peor desempeño).
3.  **La Miopía de Greedy:** Aunque el enfoque codicioso busca los picos altos de puntuación destruyendo masas gigantescas al inicio, carece de planificación a largo plazo. Una vez agotadas las estructuras masivas iniciales, deja zonas aisladas incapaces de reconectarse entre sí.

---

## 🛠️ Requisitos y Ejecución

1. **Instala PyQt6:**
   ```bash
   pip install PyQt6
   ```

2. **Ejecuta el laboratorio:**
   ```bash
   python CascadeGameAIExperiment.py
   ```

## 🔬 Metodología de Co-Creación

Este software científico fue desarrollado bajo una metodología de **Pair Programming guiado por Inteligencia Artificial**. Como director del proyecto, coordiné el planteamiento de las variables analíticas, la detección de bucles de memoria y la interpretación de la paradoja estadística de los datos del benchmark. La IA actuó como copiloto técnico para resolver problemas de empaquetado de datos (`Starred expressions`) y estructurar los criterios de desempate en PyQt6.
