# 🚀 Bloques Game - Inteligencia Artificial Avanzada (Look-Ahead Heuristic)

Esta es la fase cumbre del laboratorio experimental. Tras descubrir en fases anteriores que el algoritmo aleatorio superaba a las lógicas básicas debido a la fragmentación prematura de la matriz, se desarrolló e implementó un motor predictivo basado en la **Heurística de Densidad, Conectividad y Descarte Estructural**.

## 🧠 Arquitectura de la IA Avanzada (`AdvHeuristic`)

A diferencia de las aproximaciones *Greedy* o reactivas, este algoritmo utiliza un enfoque de **Búsqueda Prospectiva de Un Paso (1-Step Look-Ahead)**. Antes de consolidar un movimiento en el tablero real, la IA ejecuta el siguiente flujo predictivo en memoria:

1. **Clonación del Entorno:** Duplica la matriz de 10x10 en un arreglo temporal y simula el colapso gravitatorio de la jugada candidata.
2. **Cálculo de Conectividad de Color:** Evalúa el tablero resultante midiendo el tamaño de los nuevos grupos formados. Premia exponencialmente los cúmulos compactos para fomentar fusiones tardías: $\sum (\text{Tamaño del Grupo})^2$.
3. **Filtro de Bloques Aislados:** Rastrea piezas que quedaron completamente solas (sin vecinos del mismo color), restando una penalización severa a la jugada ($-15$ puntos por bloque muerto).
4. **Bono de Compresión Horizontal:** Premia los movimientos que logran vaciar por completo una columna ($+50$ puntos), compactando la matriz para unificar el espacio de juego.

---

## 📊 Reporte Científico Definitivo (50 Tests Simultáneos)

El benchmark masivo en segundo plano enfrentó a los 4 algoritmos contra 50 escenarios de tableros idénticos, arrojando las siguientes métricas de rendimiento:

| Algoritmo | Puntos Promedio | Bloques Atrapados Promedio | Diagnóstico Técnico |
| :--- | :---: | :---: | :--- |
| **🤖 AdvHeuristic** | **13,026.0** | **11.76** | **Dominancia Absoluta (Ganador) 🏆** |
| **🤖 Random** | 8,198.0 | 19.16 | Línea de Control (Azar) |
| **🤖 Greedy** | 7,732.0 | 23.16 | Optimización Cortoplacista Miope |
| **🤖 Heurístico** | 6,716.0 | 24.34 | Fragmentación por Cimientos |

### 🔬 Conclusiones Técnicas del Laboratorio

* **Victoria sobre el Azar:** La Heurística Avanzada logró superar al algoritmo *Random* incrementando el puntaje en un **58.8%** y reduciendo la ineficiencia de bloques atrapados en un **38.6%**. Esto valida que el diseño de funciones de costo que evalúan la "salud interna" del tablero mitiga el caos probabilístico.
* **El Éxito de la Ecuación de Salud:** Penalizar los bloques aislados forzó a la IA a jugar con una estrategia de preservación, manteniendo el tablero unificado e induciendo reacciones en cadena masivas que aprovecharon los multiplicadores exponenciales de puntuación en las fases finales del juego.
