# 🏁 Damas Game (Checkers) - IA Laboratory Engine v1.5

Esta sección del repositorio alberga el desarrollo de un motor interactivo avanzado para el juego de **Damas (Checkers)** en Python utilizando `PyQt6`. Diseñado bajo un enfoque de ingeniería de software estructurado, el proyecto ha evolucionado de un tablero interactivo base a un simulador que cumple de forma estricta con reglamentos de alta competencia internacional (Damas Internacionales / Españolas), incorporando sistemas asíncronos de tiempo real y un oponente automatizado (BOT Rojo).

---

## 🚀 Hitos de Ingeniería y Reglas Consolidadas

El motor gráfico y lógico de control se encuentra actualmente compilando al 100% de forma estable en PyCharm y gestiona las siguientes físicas avanzadas:

### 1. Sistema Gráfico Vectorial y Panel Analítico (`v1.1 - v1.4`)
* **Lienzo de 8x8 Estilizado:** Renderizado mediante `QPainter` con el patrón internacional de escaques crema (`#F0D9B5`) y marrón (`#B58863`) en un lienzo fijo de 400x400 píxeles.
* **Fichas con Volumen:** Dibujo de círculos vectoriales con trazos concéntricos punteados para emular el relieve plástico de las fichas de campeonato reales.
* **Panel de Métricas en Tiempo Real:** Un módulo lateral derecho gris oscuro (`#111`) de 175 píxeles que procesa dinámicamente la matriz matemática para desplegar contadores exactos de bajas (`0 / 12`) tanto para el Humano (Verde) como para el BOT (Rojo).

### 2. Rayos Vectoriales de la Reina Voladora (`v1.5`) [Punto 1]
* Rompiendo la limitación del rango fijo de una casilla, las **Reinas (Valor 3 para rojas, 4 para blancas)** lanzan un rayo continuo en las 4 direcciones diagonales.
* Permite desplazamientos libres a larga distancia (Acecho) y **capturas de largo alcance**, barriendo de forma dinámica cualquier pieza enemiga intermedia cruzada en el vector.

### 3. Capturas Múltiples Encadenadas en Zigzag (`v1.5`) [Punto 2]
* **Bloqueo de Interfaz:** Tras ejecutar un salto, si la pieza cuenta con más capturas viables, el motor no transfiere el turno. Congela la pantalla y obliga a la misma ficha a continuar el combo.
* **Regla Estricta de No-Retorno:** El algoritmo bloquea el vector inverso de procedencia. La pieza puede girar a 90 grados para continuar la racha, pero jamás regresar por su propio camino ni comer la misma pieza dos veces.

### 4. Coronación Pasiva Reglamentaria (`v1.5`)
* Si un peón blanco (2) toca la fila 0 (o uno rojo la fila 7) mediante un salto o movimiento, se corona de forma inmediata con una insignia de corona geométrica dorada brillante.
* **Nacimiento Pasivo:** Para respetar el reglamento de la FMJD, la nueva Reina se congela el resto del turno actual y "nace pasiva", activando sus poderes diagonales de largo alcance hasta el próximo turno del jugador.

### 5. Suite Asíncrona de Penalización por Omisión ("Soplado") (`v1.5`) [Puntos 3, 5 y 6]
* **Reloj de Oportunidad de 3 Segundos:** Al aterrizar una pieza en un combo viable, se activa un `QTimer` de 3s. El jugador debe encadenar el siguiente salto antes de que el reloj expire.
* **Animación de Advertencia de 2 Segundos:** Si el tiempo se agota, la interfaz bloquea el ratón. La ficha infractora y las piezas enemigas que se salvaron de ser comidas parpadean asíncronamente en color naranja/rojo brillante cada 200ms para auditar visualmente el error.
* **Soplado de la Ficha:** Al concluir la animación, la pieza del jugador es eliminada permanentemente de la matriz (`0`) y el turno pasa de forma caballerosa al BOT.

### 6. Cerebro del BOT Rojo (IA Reactiva)
* Gestión automatizada de turnos mediante un `QTimer` asíncrono con un retraso natural de 600 milisegundos para simular el tiempo de pensamiento de un humano.
* **Estrategia Greedy:** El bot escanea la matriz priorizando de forma obligatoria los saltos de captura para eliminar tus piezas blancas; si no existen, selecciona un movimiento regular táctico hacia adelante.

---

## 🎨 Arquitectura del Código (Sintaxis Blindada)

Para evitar desbordamientos visuales y errores en los portapapeles de desarrollo, la sintaxis interna fue refactorizada a estándares rigurosos de Python:
* **Uso de Tuplas Explícitas:** Las sentencias de pertenencia lógica se migraron a estructuras como `if pieza in (2, 4):` (Humanos) y `if pieza in (1, 3):` (Bots), asegurando compatibilidad nativa en el compilador de PyCharm.
* **Protección de Aproximación (Acecho):** Se rediseñó el escaneo inicial de `calcular_movimientos_validos_humano` para validar que si un jugador decide moverse de forma libre a una casilla vecina a un rival (acecho), el juego le ceda el turno limpiamente al BOT sin forzar capturas erróneas ni castigar al usuario.

---

## 📋 Requisitos y Ejecución

1. **Asegúrate de contar con la dependencia gráfica base instalada:**
   ```bash
   pip install PyQt6
   ```

2. **Ejecuta el juego desde tu terminal o IDE (PyCharm):**
   ```bash
   python DamasGame(Checkers).py
   ```

3. **Operación básica:**
   * Haz clic izquierdo sobre una pieza blanca (o reina con corona). Las casillas destino válidas se encenderán en verde indicador translúcido.
   * Si entras en estado de captura múltiple, recuerda que tienes 3 segundos en el portapapeles para efectuar el siguiente salto antes de que tu pieza sea "soplada" por omisión.

---

## 🤝 Metodología de Co-Creación

Este software fue diseñado y refinado bajo una metodología rigurosa de **Pair Programming**. El autor actuó como director estratégico del proyecto, probando el motor en tiempo real mediante partidas reales en caliente, detectando falsos positivos en los rayos de largo alcance de la reina y exigiendo un alto estándar de experiencia de usuario (UX) para las animaciones de penalización de tiempo. La IA operó como copiloto técnico encargándose de la modularización del código en bloques compactos, el cálculo de barridos en matrices diagonales y el control de relojes concurrentes sin congelar los FPS de la interfaz principal.
