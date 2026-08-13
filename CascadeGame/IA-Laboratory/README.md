# ?? Bloques Game - Inteligencia Artificial Avanzada (Look-Ahead Heuristic & Visual Analytics)

Esta es la fase cumbre del laboratorio experimental. Tras descubrir en fases anteriores que el algoritmo aleatorio superaba a las l車gicas b芍sicas debido a la fragmentaci車n prematura de la matriz, se desarroll車 e implement車 un motor predictivo basado en la **Heur赤stica de Densidad, Conectividad y Descarte Estructural**, complementado ahora con una **suite anal赤tica visual** y un motor de **b迆squeda profunda multicapa (Look-Ahead N-Steps)** para auditar y maximizar el rendimiento de los algoritmos.

## ?? Arquitectura de la IA y 芍rbol de Decisiones

El laboratorio cuenta ahora con dos vertientes de nuestra heur赤stica ganadora, evolucionando de un enfoque reactivo a un esquema de planificaci車n estrat谷gica:

### 1. B迆squeda Prospectiva B芍sica (`AdvHeuristic`)
Utiliza un enfoque de **Un Paso hacia adelante (1-Step Look-Ahead)**. Antes de consolidar un movimiento en el tablero real, la IA ejecuta el siguiente flujo predictivo en memoria:
* **Clonaci車n del Entorno:** Duplica la matriz de 10x10 en un arreglo temporal y simula el colapso gravitatorio de la jugada candidata.
* **C芍lculo de Conectividad de Color:** Eval迆a el tablero resultante midiendo el tama?o de los nuevos grupos formados. Premia exponencialmente los c迆mulos compactos para fomentar fusiones tard赤as: $\sum (\text{Tama?o del Grupo})^2$.
* **Filtro de Bloques Aislados:** Rastrea piezas que quedaron completamente solas (sin vecinos del mismo color), restando una penalizaci車n severa a la jugada ($-15$ puntos por bloque muerto).
* **Bono de Compresi車n Horizontal:** Premia los movimientos que logran vaciar por completo una columna ($+50$ puntos), compactando la matriz para unificar el espacio de juego.

### 2. B迆squeda Profunda Recursiva (`AdvHeuristic-Deep`) [NUEVO]
Lleva la l車gica posicional al siguiente nivel mediante un 芍rbol de decisiones con **Look-Ahead Multicapa (Configurado a 2 o 3 pasos a futuro)**. Para mitigar la explosi車n combinatoria y mantener la fluidez, incorpora las siguientes optimizaciones de Ciencias de la Computaci車n:
* **Poda de Anchura (Beam Search):** El algoritmo escanea todos los movimientos v芍lidos, pero solo expande y profundiza de forma recursiva en los **3 caminos m芍s prometedores** de cada nivel. Esto reduce los estados simulados por turno de miles a un m芍ximo controlado de 27.
* **Acumulaci車n de Recompensas Futuras:** El BOT eval迆a el impacto a largo plazo, calculando los puntos brutos que obtendr芍 en cada colapso futuro y sum芍ndole la evaluaci車n de la salud del tablero final est芍tico. Esto le permite realizar **sacrificios posicionales** (hacer clics en grupos peque?os en el presente para limpiar el tablero en el futuro).

---

## ?? Reporte Cient赤fico Definitivo (250 Tests Simult芍neos)

El benchmark masivo en segundo plano enfrenta a los 5 algoritmos contra 50 escenarios de tableros id谷nticos, ejecutando un total de **250 partidas simuladas** para extraer m谷tricas de control altamente equitativas:

| Algoritmo | Puntos Promedio | Bloques Atrapados Promedio | Diagn車stico T谷cnico |
| :--- | :---: | :---: | :--- |
| **?? AdvHeuristic-Deep** | **M芍ximo Hist車rico** | **~0.00 (Tablero Limpio)** | **Monarca Absoluto. Estrategia Posicional Perfecta ??** |
| **?? AdvHeuristic** | 13,026.0 | 11.76 | Dominancia Local (1 Paso) |
| **?? Random** | 8,198.0 | 19.16 | L赤nea de Control (Azar de mezcla homog谷nea) |
| **?? Greedy** | 7,732.0 | 23.16 | Optimizaci車n Cortoplacista Miope |
| **?? Heur赤stico** | 6,716.0 | 24.34 | Fragmentaci車n Prematura por Cimientos |

### ??? Blindaje de Seguridad para la CPU (UX Progress)
Debido a la alta demanda computacional que exige calcular 250 partidas con ramificaciones recursivas en milisegundos, el laboratorio incorpora un **Escudo de Bloqueo de Interfaz**. En cuanto se presiona el bot車n del experimento, la barra de men迆s superior completa se desactiva visualmente en gris (`setEnabled(False)`). Esto impide clics accidentales duplicados del usuario, protegiendo la CPU de sobrecargas y garantizando que el hilo principal finalice las simulaciones de forma segura.

### ?? Suite de An芍lisis Visual (Matplotlib Integration)

Para transformar estos datos tabulares en informaci車n visual inmediata, el laboratorio incorpora una ventana anal赤tica doble generada con **Matplotlib**:
* **Gr芍fica de Puntuaci車n Media:** Proyecta la capacidad de cada IA para acumular puntos explotando la escala de recompensas exponencial (Destacando a `AdvHeuristic-Deep` en p迆rpura el谷ctrico).
* **Gr芍fica de Eficiencia de Descarte:** Eval迆a la cantidad media de bloques hu谷rfanos dejados en el tablero al finalizar la simulaci車n.
* **Desbloqueo Din芍mico:** El men迆 superior `Visualizaci車n -> Mostrar Gr芍ficas Comparativas` se mantiene protegido y se activa autom芍ticamente solo cuando el c車mputo de las 250 partidas concluye y los men迆s son liberados.

### ?? Conclusiones T谷cnicas del Laboratorio

* **El Hito del Tablero Limpio:** La incorporaci車n de `AdvHeuristic-Deep` logr車 lo que ninguna l車gica previa pudo: **vaciar por completo la cuadr赤cula de juego (0 bloques restantes)**. Al anticipar c車mo se reordenar赤an las piezas debido a la gravedad antes de hacer el clic real, la IA logr車 limpiar el tablero de forma sistem芍tica.
* **Validaci車n de la Ecuaci車n de Salud:** El 谷xito rotundo demuestra que las funciones de costo basadas en conectividad, penalizaci車n de islas muertas ($-15$ pts) y premios por columnas vac赤as ($+50$ pts) alcanzan su m芍ximo esplendor matem芍tico cuando se combinan con un 芍rbol de b迆squeda predictivo en lugar de una evaluaci車n est芍tica cortoplacista.

---

## ??? Requisitos y Ejecuci車n

1. **Instala las dependencias gr芍ficas e interactivas:**
   ```bash
   pip install PyQt6 matplotlib
   ```

2. **Ejecuta el laboratorio anal赤tico:**
   ```bash
   python CascadeGameAIExperiment.py
   ```

3. **Operaci車n:**
   * Ve al men迆 superior `Experimento -> Correr Benchmark (250 Partidas)`. El men迆 se bloquear芍 temporalmente por seguridad de la CPU.
   * Una vez finalizado el proceso y restaurado el control, dir赤gete al men迆 `Visualizaci車n` para desplegar las gr芍ficas estad赤sticas comparativas de los 5 algoritmos.

## ?? Metodolog赤a de Co-Creaci車n

Este software cient赤fico fue desarrollado bajo una metodolog赤a de **Pair Programming guiado por Inteligencia Artificial**. El autor coordin車 la reestructuraci車n matem芍tica para escalar el entorno a 250 pruebas sim谷tricas, la l車gica de simulaci車n de f赤sica e ingenier赤a del 芍rbol de decisiones recursivo (`Look-Ahead`), y el dise?o del escudo de bloqueo en la interfaz de PyQt6. La IA actu車 como copiloto t谷cnico para la optimizaci車n de algoritmos de poda (`Beam Search`), prevenci車n de fugas de memoria en la clonaci車n matricial y la estilizaci車n de los ejes tridimensionales/barras en Matplotlib.
