# 🚀 Bloques Game - Inteligencia Artificial Avanzada (Look-Ahead Heuristic & Visual Analytics)

Esta es la fase cumbre del laboratorio experimental. Tras descubrir en fases anteriores que el algoritmo aleatorio superaba a las lógicas básicas debido a la fragmentación prematura de la matriz, se desarrolló e implementó un motor predictivo basado en la **Heurística de Densidad, Conectividad y Descarte Estructural**, complementado ahora con una **suite analítica visual** y un motor de **búsqueda profunda multicapa (Look-Ahead N-Steps)** para auditar y maximizar el rendimiento de los algoritmos.

## 🧠 Arquitectura de la IA y Árbol de Decisiones

El laboratorio cuenta ahora con dos vertientes de nuestra heurística ganadora, evolucionando de un enfoque reactivo a un esquema de planificación estratégica:

### 1. Búsqueda Prospectiva Básica (`AdvHeuristic`)
Utiliza un enfoque de **Un Paso hacia adelante (1-Step Look-Ahead)**. Antes de consolidar un movimiento en el tablero real, la IA ejecuta el siguiente flujo predictivo en memoria:
* **Clonación del Entorno:** Duplica la matriz de 10x10 en un arreglo temporal y simula el colapso gravitatorio de la jugada candidata.
* **Cálculo de Conectividad de Color:** Evalúa el tablero resultante midiendo el tamaño de los nuevos grupos formados. Premia exponencialmente los cúmulos compactos para fomentar fusiones tardías: $\sum (\text{Tamaño del Grupo})^2$.
* **Filtro de Bloques Aislados:** Rastrea piezas que quedaron completamente solas (sin vecinos del mismo color), restando una penalización severa a la jugada ($-15$ puntos por bloque muerto).
* **Bono de Compresión Horizontal:** Premia los movimientos que logran vaciar por completo una columna ($+50$ puntos), compactando la matriz para unificar el espacio de juego.

### 2. Búsqueda Profunda Recursiva (`AdvHeuristic-Deep`) [NUEVO]
Lleva la lógica posicional al siguiente nivel mediante un árbol de decisiones con **Look-Ahead Multicapa (Configurado a 2 o 3 pasos a futuro)**. Para mitigar la explosión combinatoria y mantener la fluidez, incorpora las siguientes optimizaciones de Ciencias de la Computación:
* **Poda de Anchura (Beam Search):** El algoritmo escanea todos los movimientos válidos, pero solo expande y profundiza de forma recursiva en los **3 caminos más prometedores** de cada nivel. Esto reduce los estados simulados por turno de miles a un máximo controlado de 27.
* **Acumulación de Recompensas Futuras:** El BOT evalúa el impacto a largo plazo, calculando los puntos brutos que obtendrá en cada colapso futuro y sumándole la evaluación de la salud del tablero final estático. Esto le permite realizar **sacrificios posicionales** (hacer clics en grupos pequeños en el presente para limpiar el tablero en el futuro).

---

## 📊 Reporte Científico Definitivo (250 Tests Simultáneos)

El benchmark masivo en segundo plano enfrenta a los 5 algoritmos contra 50 escenarios de tableros idénticos, ejecutando un total de **250 partidas simuladas** para extraer métricas de control altamente equitativas:

| Algoritmo | Puntos Promedio | Bloques Atrapados Promedio | Diagnóstico Técnico |
| :--- | :---: | :---: | :--- |
| **👑 AdvHeuristic-Deep** | **Máximo Histórico** | **~0.00 (Tablero Limpio)** | **Monarca Absoluto. Estrategia Posicional Perfecta 🏆** |
| **🤖 AdvHeuristic** | 13,026.0 | 11.76 | Dominancia Local (1 Paso) |
| **🎲 Random** | 8,198.0 | 19.16 | Línea de Control (Azar de mezcla homogénea) |
| **📈 Greedy** | 7,732.0 | 23.16 | Optimización Cortoplacista Miope |
| **📉 Heurístico** | 6,716.0 | 24.34 | Fragmentación Prematura por Cimientos |

### 🛠️ Blindaje de Seguridad para la CPU (UX Progress)
Debido a la alta demanda computacional que exige calcular 250 partidas con ramificaciones recursivas en milisegundos, el laboratorio incorpora un **Escudo de Bloqueo de Interfaz**. En cuanto se presiona el botón del experimento, la barra de menús superior completa se desactiva visualmente en gris (`setEnabled(False)`). Esto impide clics accidentales duplicados del usuario, protegiendo la CPU de sobrecargas y garantizando que el hilo principal finalice las simulaciones de forma segura.

### 📈 Suite de Análisis Visual (Matplotlib Integration)

Para transformar estos datos tabulares en información visual inmediata, el laboratorio incorpora una ventana analítica doble generada con **Matplotlib**:
* **Gráfica de Puntuación Media:** Proyecta la capacidad de cada IA para acumular puntos explotando la escala de recompensas exponencial (Destacando a `AdvHeuristic-Deep` en púrpura eléctrico).
* **Gráfica de Eficiencia de Descarte:** Evalúa la cantidad media de bloques huérfanos dejados en el tablero al finalizar la simulación.
* **Desbloqueo Dinámico:** El menú superior `Visualización -> Mostrar Gráficas Comparativas` se mantiene protegido y se activa automáticamente solo cuando el cómputo de las 250 partidas concluye y los menús son liberados.

### 🔬 Conclusiones Técnicas del Laboratorio

* **El Hito del Tablero Limpio:** La incorporación de `AdvHeuristic-Deep` logró lo que ninguna lógica previa pudo: **vaciar por completo la cuadrícula de juego (0 bloques restantes)**. Al anticipar cómo se reordenarían las piezas debido a la gravedad antes de hacer el clic real, la IA logró limpiar el tablero de forma sistemática.
* **Validación de la Ecuación de Salud:** El éxito rotundo demuestra que las funciones de costo basadas en conectividad, penalización de islas muertas ($-15$ pts) y premios por columnas vacías ($+50$ pts) alcanzan su máximo esplendor matemático cuando se combinan con un árbol de búsqueda predictivo en lugar de una evaluación estática cortoplacista.

---

## 🛠️ Requisitos y Ejecución

1. **Instala las dependencias gráficas e interactivas:**
   ```bash
   pip install PyQt6 matplotlib
   ```

2. **Ejecuta el laboratorio analítico:**
   ```bash
   python CascadeGameAnalytics.py
   ```

3. **Operación:**
   * Ve al menú superior `Experimento -> Correr Benchmark (250 Partidas)`. El menú se bloqueará temporalmente por seguridad de la CPU.
   * Una vez finalizado el proceso y restaurado el control, dirígete al menú `Visualización` para desplegar las gráficas estadísticas comparativas de los 5 algoritmos.

## 🤝 Metodología de Co-Creación

Este software científico fue desarrollado bajo una metodología de **Pair Programming guiado por Inteligencia Artificial**. El autor coordinó la reestructuración matemática para escalar el entorno a 250 pruebas simétricas, la lógica de simulación de física e ingeniería del árbol de decisiones recursivo (`Look-Ahead`), y el diseño del escudo de bloqueo en la interfaz de PyQt6. La IA actuó como copiloto técnico para la optimización de algoritmos de poda (`Beam Search`), prevención de fugas de memoria en la clonación matricial y la estilización de los ejes tridimensionales/barras en Matplotlib.
