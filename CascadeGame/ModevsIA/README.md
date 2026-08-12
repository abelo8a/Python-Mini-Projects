# 🥊 Bloques Game - Modo Versus (Humano vs. IA Avanzada)

Esta versión transforma el laboratorio de pruebas en un **entorno competitivo interactivo en tiempo real**. El sistema permite al usuario enfrentarse directamente a la Inteligencia Artificial Avanzada (`AdvHeuristic`) en una simulación de juego en espejo basada en una semilla de tablero idéntica y justa.

## 🚀 Características Clave del Modo Versus

*   **Sincronización Espejo de Matrices:** Al iniciar una nueva partida, el motor lógico clona exactamente la misma cuadrícula aleatoria de 10x10 para el `MyArray_Humano` y el `MyArray_Bot`. Ambos competidores inician con la misma distribución de polígonos.
*   **Lienzo Dual Extendido:** El widget gráfico de visualización se expande horizontalmente a **740 píxeles** para renderizar ambos tableros vectoriales de forma simultánea e independiente en la misma ventana de **PyQt6**.
*   **Aislamiento de Eventos del Mouse:** Mapeo preciso de coordenadas a través de eventos `mousePressEvent` restringidos únicamente a las columnas de la cuadrícula izquierda. El usuario juega de forma manual mediante clics, mientras que el tablero derecho responde estrictamente a los hilos de la IA.
*   **Panel de Control en Espejo:** Rediseño completo del panel derecho en dos columnas de datos en paralelo. Permite auditar en vivo quién está tomando mejores decisiones estratégicas en tres métricas fundamentales:
    *   **Puntos:** Puntuación exponencial acumulada en la partida.
    *   **Eliminados:** Contador acumulativo de fichas destruidas.
    *   **Restantes:** Cantidad de bloques vivos (la partida termina cuando se agotan los movimientos).

## 🧠 El Desafío contra la IA Avanzada

Mientras juegas de forma manual en el lado izquierdo, un temporizador del sistema (`QTimer`) activa el ciclo autónomo del Bot del lado derecho cada **1,000 milisegundos**. 

La IA utiliza la lógica de **Búsqueda Prospectiva (Look-Ahead Heuristic)**, simulando en memoria el impacto de sus jugadas para penalizar bloques huérfanos y premiar la conectividad cromática. El juego termina cuando ambos se quedan sin movimientos válidos, calculando al ganador basándose en la puntuación más alta.

## 🛠️ Requisitos y Ejecución

1. **Instala la librería gráfica:**
   ```bash
   pip install PyQt6
   ```

2. **Ejecuta el script del Modo Versus:**
   ```bash
   python CascadeGameVersus.py
   ```

3. **Cómo Jugar:**
   * Haz clic en el menú superior `Archivo -> Nuevo Juego`.
   * Comienza a romper grupos de 2 o más bloques adyacentes en el tablero de la izquierda.
   * Observa las decisiones de la IA en la derecha e intenta optimizar tus grupos para superar su puntuación.

## 🔬 Metodología de Desarrollo

Este entorno interactivo competitivo fue co-creado mediante **Pair Programming guiado por Inteligencia Artificial**. El autor dirigió el flujo del diseño en espejo de las matrices, la duplicidad estructural de las etiquetas de puntuación y la captura de clics del usuario. La IA actuó como copiloto técnico para resolver problemas de colisión de memoria y garantizar la estabilidad del sistema mediante operaciones lineales de suma de listas (`* ceros_necesarios`) en las físicas de gravedad.
