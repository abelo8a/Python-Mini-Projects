import sys
import math
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QStatusBar
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QAction, QFont, QPainter, QColor, QPen, QBrush, QActionGroup


class TableroDoble(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window.central_widget)
        self.main_window = main_window
        # Ventana extendida a lo ancho para albergar dos tableros de 360px + un margen intermedio
        self.setGeometry(0, 0, 740, 360)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        if not self.main_window.game_active: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        box_size = 36
        radius = box_size / 2

        # -----------------------------------------------------------------
        # RENDERIZADO DEL TABLERO IZQUIERDO (JUGADOR HUMANO)
        # -----------------------------------------------------------------
        for i in range(10):
            for c in range(10):
                lados = self.main_window.MyArray_Humano[c][i]
                if lados == 0: continue

                painter.setPen(QPen(self.obtener_color_figura(lados), 2))
                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))

                center_x = (c * box_size) + radius
                center_y = (i * box_size) + radius
                self.dibujar_poligono(painter, center_x, center_y, radius, lados)

        # -----------------------------------------------------------------
        # RENDERIZADO DEL TABLERO DERECHO (INTELIGENCIA ARTIFICIAL)
        # -----------------------------------------------------------------
        offset_bot = 380  # Desplazamiento horizontal para separar los tableros
        for i in range(10):
            for c in range(10):
                lados = self.main_window.MyArray_Bot[c][i]
                if lados == 0: continue

                # Si el bot tiene un grupo seleccionado para destruir, lo dibuja parpadeando en rojo
                if (c, i) in self.main_window.bloques_seleccionados_bot:
                    painter.setPen(QPen(QColor(255, 0, 50), 3, Qt.PenStyle.DashLine))
                else:
                    painter.setPen(QPen(self.obtener_color_figura(lados), 2))

                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))

                center_x = (c * box_size) + radius + offset_bot
                center_y = (i * box_size) + radius
                self.dibujar_poligono(painter, center_x, center_y, radius, lados)

        painter.end()

    def obtener_color_figura(self, lados):
        if lados == 3:
            return QColor(3, 182, 17)  # Triángulo Verde
        elif lados == 4:
            return QColor(255, 255, 0)  # Cuadrado Amarillo
        elif lados == 5:
            return QColor(18, 236, 254)  # Pentágono Cian
        elif lados == 6:
            return QColor(238, 23, 23)  # Hexágono Rojo
        elif lados == 7:
            return QColor(255, 255, 255)  # Heptágono Blanco
        return QColor(100, 100, 100)

    def dibujar_poligono(self, painter, cx, cy, r, lados):
        points = []
        for count in range(lados + 1):
            angle = (2 * math.pi) * count / lados
            pt_x = int(math.sin(angle) * r + cx)
            pt_y = int(math.cos(angle) * r + cy)
            points.append(QPoint(pt_x, pt_y))
        painter.drawPolygon(points)

    # DETECCIÓN DE CLICS EXCLUSIVA PARA EL LADO DEL JUGADOR
    def mousePressEvent(self, event):
        if not self.main_window.game_active: return

        click_x = event.position().x()
        click_y = event.position().y()

        col = int(click_x // 36)
        fila = int(click_y // 36)

        # Validación geométrica: El humano solo puede hacer clic entre las columnas 0 y 9
        if 0 <= col < 10 and 0 <= fila < 10:
            self.main_window.procesar_jugada_humano(col, fila)


class BloquesGame(QMainWindow):
    def __init__(self):
        super().__init__()
        # Inicialización de matrices dobles independientes
        self.MyArray_Humano = [[0 for _ in range(10)] for _ in range(10)]
        self.MyArray_Bot = [[0 for _ in range(10)] for _ in range(10)]

        # Estructuras de datos para el Jugador Humano
        self.puntos_humano = 0
        self.bloques_eliminados_humano = 0
        self.humano_activo = False

        # Estructuras de datos para la Inteligencia Artificial
        self.puntos_bot = 0
        self.bloques_eliminados_bot = 0
        self.bot_activo = False
        self.modo_bot = "AdvHeuristic"  # Utiliza tu IA con Look-Ahead

        # Control global del juego
        self.puntos_eliminados_ronda = 0
        self.game_active = False
        self.modo_laboratorio = False
        self.bloques_seleccionados_bot = set()
        self.timer_bot = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Bloques Game - MODO VERSUS (HUMANO VS BOT)')
        # Ventana ensanchada para dar espacio al segundo tablero y al panel extendido
        self.setFixedSize(935, 385)
        self.setStyleSheet("background-color: black; color: white;")
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.tablero = TableroDoble(self)

        # Panel lateral extendido con división en espejo
        self.panel1 = QWidget(self.central_widget)
        self.panel1.setGeometry(742, 0, 193, 361)
        self.panel1.setStyleSheet("background-color: black; border-left: 1px solid #333;")

        font_titulo = QFont('MS Sans Serif', 11, QFont.Weight.Bold)
        font_subtitulos = QFont('MS Sans Serif', 9, QFont.Weight.Bold)
        font_valores = QFont('MS Sans Serif', 10, QFont.Weight.Bold)

        # 1. Encabezados de Columna
        self.label_col_humano = QLabel('HUMANO', self.panel1)
        self.label_col_humano.setGeometry(10, 10, 80, 20)
        self.label_col_humano.setFont(font_titulo)
        self.label_col_humano.setStyleSheet("color: #55FF55; border: none;")

        self.label_col_bot = QLabel('BOT (IA)', self.panel1)
        self.label_col_bot.setGeometry(105, 10, 80, 20)
        self.label_col_bot.setFont(font_titulo)
        self.label_col_bot.setStyleSheet("color: cyan; border: none;")

        # Línea divisoria horizontal
        self.linea1 = QWidget(self.panel1)
        self.linea1.setGeometry(5, 35, 180, 1)
        self.linea1.setStyleSheet("background-color: #333;")

        # 2. SECCIÓN DE PUNTUACIÓN
        self.lbl_puntos_t = QLabel('PUNTOS', self.panel1)
        self.lbl_puntos_t.setGeometry(10, 45, 170, 15)
        self.lbl_puntos_t.setFont(font_subtitulos)
        self.lbl_puntos_t.setStyleSheet("color: red; border: none;")

        self.lbl_puntos_humano = QLabel('0', self.panel1)
        self.lbl_puntos_humano.setGeometry(10, 65, 80, 20)
        self.lbl_puntos_humano.setFont(font_valores)
        self.lbl_puntos_humano.setStyleSheet("color: yellow; border: none;")

        self.lbl_puntos_bot = QLabel('0', self.panel1)
        self.lbl_puntos_bot.setGeometry(105, 65, 80, 20)
        self.lbl_puntos_bot.setFont(font_valores)
        self.lbl_puntos_bot.setStyleSheet("color: yellow; border: none;")

        # 3. SECCIÓN DE BLOQUES ELIMINADOS (ACUMULATIVO)
        self.lbl_elim_t = QLabel('ELIMINADOS', self.panel1)
        self.lbl_elim_t.setGeometry(10, 100, 170, 15)
        self.lbl_elim_t.setFont(font_subtitulos)
        self.lbl_elim_t.setStyleSheet("color: red; border: none;")

        self.lbl_elim_humano = QLabel('0', self.panel1)
        self.lbl_elim_humano.setGeometry(10, 120, 80, 20)
        self.lbl_elim_humano.setFont(font_valores)
        self.lbl_elim_humano.setStyleSheet("color: #FF55FF; border: none;")

        self.lbl_elim_bot = QLabel('0', self.panel1)
        self.lbl_elim_bot.setGeometry(105, 120, 80, 20)
        self.lbl_elim_bot.setFont(font_valores)
        self.lbl_elim_bot.setStyleSheet("color: #FF55FF; border: none;")

        # 4. SECCIÓN DE BLOQUES RESTANTES EN TABLERO
        self.lbl_rest_t = QLabel('RESTANTES', self.panel1)
        self.lbl_rest_t.setGeometry(10, 155, 170, 15)
        self.lbl_rest_t.setFont(font_subtitulos)
        self.lbl_rest_t.setStyleSheet("color: red; border: none;")

        self.lbl_rest_humano = QLabel('100', self.panel1)
        self.lbl_rest_humano.setGeometry(10, 175, 80, 20)
        self.lbl_rest_humano.setFont(font_valores)
        self.lbl_rest_humano.setStyleSheet("color: #55FF55; border: none;")

        self.lbl_rest_bot = QLabel('100', self.panel1)
        self.lbl_rest_bot.setGeometry(105, 175, 80, 20)
        self.lbl_rest_bot.setFont(font_valores)
        self.lbl_rest_bot.setStyleSheet("color: #55FF55; border: none;")

        # Barra de estado inferior
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo - Presiona Archivo -> Nuevo para desafiar a la IA")

        # Barra de Menús Básica
        menu_bar = self.menuBar()
        menu_archivo = menu_bar.addMenu('Archivo')

        action_nuevo = QAction('Nuevo Juego', self)
        action_nuevo.triggered.connect(self.button1_click)
        menu_archivo.addAction(action_nuevo)

        action_salir = QAction('Salir', self)
        action_salir.triggered.connect(self.close)
        menu_archivo.addAction(action_salir)

    def button1_click(self):
        # Reiniciar métricas de ambos bandos
        self.puntos_humano = 0
        self.bloques_eliminados_humano = 0
        self.puntos_bot = 0
        self.bloques_eliminados_bot = 0

        self.lbl_puntos_humano.setText('0')
        self.lbl_puntos_bot.setText('0')
        self.lbl_elim_humano.setText('0')
        self.lbl_elim_bot.setText('0')
        self.lbl_rest_humano.setText('100')
        self.lbl_rest_bot.setText('100')

        self.bloques_seleccionados_bot.clear()

        # IMPORTANTE: Clonar el mismo tablero inicial usando una sola semilla aleatoria
        for i in range(10):
            for c in range(10):
                figura_aleatoria = random.randint(3, 7)
                self.MyArray_Humano[c][i] = figura_aleatoria
                self.MyArray_Bot[c][i] = figura_aleatoria

        self.game_active = True
        self.humano_activo = True
        self.bot_activo = True

        self.status_bar.showMessage("¡Partida Iniciada! Demuestra que puedes ganarle a la IA.")
        self.tablero.update()

        # Disparar el temporizador del BOT cada 1 segundo (1000ms)
        if self.timer_bot is None:
            self.timer_bot = QTimer(self)
            self.timer_bot.timeout.connect(self.ejecutar_ciclo_bot)
        if not self.timer_bot.isActive():
            self.timer_bot.start(1000)

    def calcular_puntuaje_ronda(self, bloques_rotos):
        tabla_puntos = {2: 100, 3: 200, 4: 400, 5: 700, 6: 1100, 7: 1600,
                        8: 2200, 9: 2900, 10: 3700, 11: 4600, 12: 5600}
        puntos = tabla_puntos.get(bloques_rotos, 0)
        if bloques_rotos > 12:
            puntos = 5600 + (bloques_rotos - 12) * 1200
        return puntos

    # -----------------------------------------------------------------
    # LÓGICA EXCLUSIVA DEL JUGADOR HUMANO
    # -----------------------------------------------------------------
    def procesar_jugada_humano(self, col, fila):
        if not self.game_active or not self.humano_activo: return

        target_val = self.MyArray_Humano[col][fila]
        if target_val == 0: return

        # Contar cuántos bloques contiguos hay del mismo tipo
        visitados_temp = set()
        tamano_grupo = self.contar_grupo_simulado(col, fila, target_val, visitados_temp, self.MyArray_Humano)

        # Regla: Solo se pueden eliminar grupos de 2 o más bloques
        if tamano_grupo >= 2:
            self.puntos_eliminados_ronda = 0
            self.eliminar_recursivo_matriz(self.MyArray_Humano, col, fila, target_val)

            # Actualizar estadísticas del Humano
            self.puntos_humano += self.calcular_puntuaje_ronda(tamano_grupo)
            self.bloques_eliminados_humano += tamano_grupo

            self.aplicar_fisicas_en_matriz(self.MyArray_Humano)
            self.actualizar_interfaz_versus()
            self.tablero.update()

            # Verificar si el humano se quedó sin movimientos válidos
            if not self.tiene_movimientos_validos(self.MyArray_Humano):
                self.humano_activo = False
                self.status_bar.showMessage("El Humano se ha quedado sin movimientos.")
                self.verificar_fin_del_juego()

    # -----------------------------------------------------------------
    # LÓGICA RECURSIVA Y FÍSICAS DE MATRIZ CORREGIDAS
    # -----------------------------------------------------------------
    def eliminar_recursivo_matriz(self, matriz, w, z, target_val):
        if w < 0 or w > 9 or z < 0 or z > 9: return
        if matriz[w][z] != target_val: return
        matriz[w][z] = 0
        self.puntos_eliminados_ronda += 1
        self.eliminar_recursivo_matriz(matriz, w - 1, z, target_val)
        self.eliminar_recursivo_matriz(matriz, w + 1, z, target_val)
        self.eliminar_recursivo_matriz(matriz, w, z - 1, target_val)
        self.eliminar_recursivo_matriz(matriz, w, z + 1, target_val)

    def aplicar_fisicas_en_matriz(self, matriz):
        # 1. Aplicar gravedad vertical
        for c in range(10):
            col_filt = [matriz[c][i] for i in range(10) if matriz[c][i] != 0]
            ceros_necesarios = 10 - len(col_filt)
            # SOLUCIÓN: Suma de listas segura para evitar cierres inesperados
            matriz[c] = [0] * ceros_necesarios + col_filt

        # 2. Desplazamiento horizontal de columnas vacías
        columnas_vivas = []
        for c in range(10):
            if any(matriz[c][i] != 0 for i in range(10)):
                columnas_vivas.append(matriz[c])

        # Completar el vacío derecho con columnas de ceros
        columnas_vaciadas = 10 - len(columnas_vivas)
        for _ in range(columnas_vaciadas):
            columnas_vivas.append([0] * 10)

        for c in range(10):
            matriz[c] = columnas_vivas[c]

    def contar_grupo_simulado(self, w, z, target_val, visitados, matriz):
        if w < 0 or w > 9 or z < 0 or z > 9: return 0
        if (w, z) in visitados or matriz[w][z] != target_val: return 0
        visitados.add((w, z))
        count = 1
        count += self.contar_grupo_simulado(w - 1, z, target_val, visitados, matriz)
        count += self.contar_grupo_simulado(w + 1, z, target_val, visitados, matriz)
        count += self.contar_grupo_simulado(w, z - 1, target_val, visitados, matriz)
        count += self.contar_grupo_simulado(w, z + 1, target_val, visitados, matriz)
        return count

    def tiene_movimientos_validos(self, matriz):
        for c in range(10):
            for i in range(10):
                val = matriz[c][i]
                if val != 0:
                    visitados_temp = set()
                    if self.contar_grupo_simulado(c, i, val, visitados_temp, matriz) >= 2:
                        return True
        return False

    def evaluar_tablero_futuro(self, c_origen, i_origen, target_val):
        matriz_temp = [fila[:] for fila in self.MyArray_Bot]
        self.puntos_eliminados_ronda = 0
        self.eliminar_recursivo_matriz(matriz_temp, c_origen, i_origen, target_val)
        self.aplicar_fisicas_en_matriz(matriz_temp)

        visitados_globales = set()
        conectividad_total = 0
        bloques_aislados = 0
        columnas_vacias = 0

        for c in range(10):
            if all(matriz_temp[c][i] == 0 for i in range(10)):
                columnas_vacias += 1
                continue
            for i in range(10):
                val = matriz_temp[c][i]
                if val != 0 and (c, i) not in visitados_globales:
                    visitados_grupo = set()
                    tam_grupo = self.contar_grupo_simulado(c, i, val, visitados_grupo, matriz_temp)
                    visitados_globales.update(visitados_grupo)
                    if tam_grupo == 1:
                        bloques_aislados += 1
                    else:
                        conectividad_total += (tam_grupo * tam_grupo)

        return conectividad_total - (bloques_aislados * 15) + (columnas_vacias * 50)

    # -----------------------------------------------------------------
    # CONTROL DE CICLO DEL BOT AUTOMÁTICO
    # -----------------------------------------------------------------
    def ejecutar_ciclo_bot(self):
        if not self.game_active or not self.bot_activo: return

        movimientos_validos = []
        for c in range(10):
            for i in range(10):
                val_actual = self.MyArray_Bot[c][i]
                if val_actual != 0:
                    visitados_temp = set()
                    tamano = self.contar_grupo_simulado(c, i, val_actual, visitados_temp, self.MyArray_Bot)
                    if tamano >= 2:
                        movimientos_validos.append((tamano, i, c, visitados_temp))

        if not movimientos_validos:
            self.bot_activo = False
            self.status_bar.showMessage("La IA se ha quedado sin movimientos.")
            self.verificar_fin_del_juego()
            return

        # IA Avanzada con look-ahead
        mejor = max(movimientos_validos,
                    key=lambda x: (self.evaluar_tablero_futuro(x[2], x[1], self.MyArray_Bot[x[2]][x[1]]), x[1], x[2]))

        tamano_g, coord_i, coord_c, celdas_grupo = mejor
        self.bloques_seleccionados_bot = celdas_grupo
        self.tablero.update()

        self.puntos_eliminados_ronda = 0
        target_val = self.MyArray_Bot[coord_c][coord_i]
        self.eliminar_recursivo_matriz(self.MyArray_Bot, coord_c, coord_i, target_val)

        self.puntos_bot += self.calcular_puntuaje_ronda(tamano_g)
        self.bloques_eliminados_bot += tamano_g

        self.aplicar_fisicas_en_matriz(self.MyArray_Bot)
        self.actualizar_interfaz_versus()

        self.bloques_seleccionados_bot.clear()
        self.tablero.update()

    # -----------------------------------------------------------------
    # REFRESCO DE INTERFAZ Y FINALIZACIÓN
    # -----------------------------------------------------------------
    def actualizar_interfaz_versus(self):
        vivos_h = sum(1 for c in range(10) for i in range(10) if self.MyArray_Humano[c][i] != 0)
        vivos_b = sum(1 for c in range(10) for i in range(10) if self.MyArray_Bot[c][i] != 0)

        self.lbl_puntos_humano.setText(str(self.puntos_humano))
        self.lbl_puntos_bot.setText(str(self.puntos_bot))
        self.lbl_elim_humano.setText(str(self.bloques_eliminados_humano))
        self.lbl_elim_bot.setText(str(self.bloques_eliminados_bot))
        self.lbl_rest_humano.setText(str(vivos_h))
        self.lbl_rest_bot.setText(str(vivos_b))

    def verificar_fin_del_juego(self):
        if not self.humano_activo and not self.bot_activo:
            self.timer_bot.stop()
            self.game_active = False

            if self.puntos_humano > self.puntos_bot:
                resultado = "¡Felicidades! Le ganaste a la IA Avanzada. 🏆"
            elif self.puntos_humano < self.puntos_bot:
                resultado = "La IA Avanzada ha ganado esta partida. 🤖"
            else:
                resultado = "¡Empate perfecto de puntuación! 🤝"

            self.status_bar.showMessage(f"FIN DEL JUEGO. {resultado}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = BloquesGame()
    game.show()
    sys.exit(app.exec())
