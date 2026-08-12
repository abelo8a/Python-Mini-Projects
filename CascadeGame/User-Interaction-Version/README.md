# 🎮 Bloques Game - Versión Juego Base

Esta es la primera fase incremental del videojuego interactivo de bloques desarrollado en Python utilizando **PyQt6**. Esta versión establece los cimientos del proyecto, enfocándose en el motor del juego, la renderización de las figuras geométricas y el sistema de físicas en el tablero.

## 🚀 Características Principales (Fase 1)

*   **Renderizado de Polígonos con QPainter:** El tablero dibuja de forma vectorial las figuras geométricas utilizando anti-aliasing para garantizar bordes suaves. Los polígonos varían dinámicamente según sus lados (desde triángulos hasta pentágonos).
*   **Físicas de Gravedad Real:** Implementación de un sistema de colisiones por columnas. Cuando un grupo de bloques es eliminado, las figuras superiores caen de forma vertical. Si una columna se vacía por completo, todo el tablero se comprime hacia la izquierda.
*   **Control del Ciclo mediante QTimer:** La ejecución de las rondas del juego está sincronizada mediante un temporizador analítico (`QTimer`), permitiendo observar los movimientos de forma fluida segundo a segundo.
*   **Interfaz Gráfica Oscura:** Diseño estilizado en fondo negro con un panel lateral derecho para estadísticas básicas y una barra de menús integrada en la parte superior de la ventana.

## 🛠️ Mecánicas del Tablero

Al iniciar una nueva partida, el sistema genera una cuadrícula aleatoria de 10x10 que distribuye diferentes polígonos identificados por colores:
*   🟢 **Triángulos** (3 lados)
*   🟡 **Cuadrados** (4 lados)
*   🔵 **Pentágonos** (5 lados)

## 📦 Instalación y Uso

1. **Instala la librería necesaria para el entorno gráfico:**
   ```bash
   pip install PyQt6
   ```

2. **Ejecuta el script principal desde tu terminal:**
   ```bash
   python main.py
   ```

3. **Cómo operar el juego:**
   * Haz clic en el menú superior `Archivo -> Nuevo` para inicializar el tablero con figuras aleatorias.
   * La aplicación activará automáticamente el bucle del juego y la barra inferior de estado reflejará los eventos del sistema.

## 🔬 Metodología de Desarrollo y Aprendizaje

Este software fue estructurado mediante una metodología de **Pair Programming asistido por Inteligencia Artificial**. El objetivo primordial de esta fase fue dominar el flujo de ciclo de vida de una aplicación en PyQt6, la manipulación de arreglos bidimensionales en memoria (matrices de 10x10) y la recursividad para la detección y conteo de bloques adyacentes del mismo tipo.
