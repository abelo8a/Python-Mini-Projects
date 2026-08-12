# 🎮 Bloques Game - Modo Multi-Algoritmo & Monitoreo

Esta es la segunda fase incremental del videojuego interactivo de bloques escrito en Python y **PyQt6**. En esta versión, el proyecto evoluciona de un juego estático a un **entorno predictivo multi-algoritmo**, permitiendo al usuario cambiar en tiempo real la estrategia de toma de decisiones del Bot mediante la interfaz gráfica.

## 🚀 Nuevas Características (Fase 2)

*   **Menú Dinámico de IA:** Incorporación de la pestaña `Modo de Bot` en la barra superior para alternar entre tres lógicas de juego de forma instantánea.
*   **Monitoreo Analítico Lateral:** El panel derecho ha sido rediseñado para incluir métricas precisas de rendimiento:
    *   **Algoritmo:** Muestra el modo de juego activo en color cian.
    *   **Puntos:** Puntuación acumulada con base en la escala de recompensas exponencial.
    *   **Eliminados:** Contador acumulativo histórico de todos los bloques destruidos en la partida.
    *   **Restantes:** Contador en tiempo real de los bloques vivos en el tablero (la partida ideal busca llevar este número a 0).
*   **Motor Discriminador Anti-Bucles:** Optimización del ciclo de la IA mediante un sistema de desempate por coordenadas para evitar bucles infinitos en tableros altamente simétricos.

## 🤖 Algoritmos de Toma de Decisiones Incluidos

El usuario puede evaluar el comportamiento y la eficiencia de tres lógicas distintas:

1.  **Greedy (Codicioso):** La IA escanea el tablero y prioriza estrictamente destruir el grupo de bloques adyacentes más grande disponible. Busca maximizar los puntos rápidos por jugada.
2.  **Heurístico (Limpieza de Cimientos):** La IA prioriza romper los grupos que se encuentran en las filas inferiores del tablero (eje Y más profundo). El objetivo es desestabilizar la base para generar grandes reacciones en cadena debido a las físicas de gravedad.
3.  **Random (Azar):** El Bot elige un grupo válido de bloques completamente de forma aleatoria. Funciona como una métrica de control (línea base) para demostrar la inteligencia de los otros dos modos.

## 🛠️ Tecnologías y Módulos Utilizados

*   **Python 3.10+** (Aprovechamiento de asignaciones y desempaquetado de secuencias corregido).
*   **PyQt6 (QtWidgets, QtCore, QtGui):** Manejo de la interfaz de ventanas, menús de exclusión mutua (`QActionGroup`), temporizadores analíticos (`QTimer`) y renderizado vectorial de polígonos (`QPainter`).

## 📦 Instalación y Uso

1. **Asegúrate de tener instalada la librería de interfaz gráfica:**
   ```bash
   pip install PyQt6
   ```

2. **Ejecuta el programa desde tu terminal:**
   ```bash
   python CascadeGameBot.py
   ```

3. **Cómo operar el laboratorio:**
   * Dirígete al menú superior `Modo de Bot` y selecciona cualquiera de las tres estrategias (puedes cambiarlo a mitad de una partida).
   * Haz clic en `Archivo -> Nuevo Juego` para generar un tablero aleatorio con 5 polígonos diferentes (del triángulo al heptágono) y observa cómo responde el bot segundo a segundo.

## 🔬 Metodología de Desarrollo

Este software fue co-creado mediante **Pair Programming asistido por Inteligencia Artificial**. La estructura lógica, la detección de errores de desbordamiento en memoria y el planteamiento de los criterios de desempate algorítmicos fueron dirigidos por el autor, utilizando la IA como copiloto técnico para la resolución de errores de sintaxis (`Starred expressions`) y optimización de jerarquías en PyQt6.
