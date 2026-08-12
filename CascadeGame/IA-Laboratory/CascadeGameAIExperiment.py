import sys
import math
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QStatusBar
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QAction, QFont, QPainter, QColor, QPen, QBrush, QActionGroup


class TableroJuego(QWidget):
    def __init__(self, main_window):
        super().__init__(main_window.central_widget)
        self.main_window = main_window
        self.setGeometry(0, 0, 360, 360)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        if not self.main_window.game_active or self.main_window.modo_laboratorio:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        box_size = 36
        radius = box_size / 2
        for i in range(10):
            for c in range(10):
                lados = self.main_window.MyArray[c][i]
                if lados == 0: continue

                if (c, i) in self.main_window.bloques_seleccionados_bot:
                    painter.setPen(QPen(QColor(255, 0, 50), 4, Qt.PenStyle.DashLine))
                else:
                    if lados == 3: pen_color = QColor(3, 182, 17)
                    elif lados == 4: pen_color = QColor(255, 255, 0)
                    elif lados == 5: pen_color = QColor(18, 236, 254)
                    elif lados == 6: pen_color = QColor(238, 23, 23)
                    elif lados == 7: pen_color = QColor(255, 255, 255)
                    else: pen_color = QColor(100, 100, 100)
                    painter.setPen(QPen(pen_color, 2))

                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                center_x = (c * box_size) + radius
                center_y = (i * box_size) + radius
                points = []
                for count in range(lados + 1):
                    angle = (2 * math.pi) * count / lados
                    pt_x = int(math.sin(angle) * radius + center_x)
                    pt_y = int(math.cos(angle) * radius + center_y)
                    points.append(QPoint(pt_x, pt_y))
                painter.drawPolygon(points)
        painter.end()


class BloquesGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.MyArray = [[0 for _ in range(10)] for _ in range(10)]
        self.tot_puntos = 0
        self.puntos_eliminados_ronda = 0
        self.total_bloques_eliminados_partida = 0
        self.game_active = False
        self.modo_bot = "AdvHeuristic"  # Iniciamos con la nueva IA por defecto
        self.modo_laboratorio = False
        self.bloques_seleccionados_bot = set()
        self.timer_bot = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Bloques Game - INTELIGENCIA ARTIFICIAL AVANZADA')
        self.setFixedSize(545, 385)
        self.setStyleSheet("background-color: black; color: white;")
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.tablero = TableroJuego(self)

        # Panel derecho de control y métricas
        self.panel1 = QWidget(self.central_widget)
        self.panel1.setGeometry(362, 0, 183, 361)
        self.panel1.setStyleSheet("background-color: black; border-left: 1px solid #333;")

        font_labels = QFont('MS Sans Serif', 10, QFont.Weight.Bold)
        font_values = QFont('MS Sans Serif', 11, QFont.Weight.Bold)

        self.label3 = QLabel('Algoritmo:', self.panel1)
        self.label3.setGeometry(8, 10, 85, 20)
        self.label3.setFont(font_labels)
        self.label3.setStyleSheet("color: red; border: none;")

        self.label_modo = QLabel('AdvHeuristic', self.panel1)
        self.label_modo.setGeometry(95, 10, 85, 20)
        self.label_modo.setFont(font_values)
        self.label_modo.setStyleSheet("color: cyan; border: none;")

        self.label1 = QLabel('Puntos:', self.panel1)
        self.label1.setGeometry(8, 45, 71, 20)
        self.label1.setFont(font_labels)
        self.label1.setStyleSheet("color: red; border: none;")

        self.label2 = QLabel('0', self.panel1)
        self.label2.setGeometry(86, 45, 80, 20)
        self.label2.setFont(font_values)
        self.label2.setStyleSheet("color: yellow; border: none;")

        self.label_elim_titulo = QLabel('Eliminados:', self.panel1)
        self.label_elim_titulo.setGeometry(8, 80, 95, 20)
        self.label_elim_titulo.setFont(font_labels)
        self.label_elim_titulo.setStyleSheet("color: red; border: none;")

        self.label_elim_valor = QLabel('0', self.panel1)
        self.label_elim_valor.setGeometry(110, 80, 60, 20)
        self.label_elim_valor.setFont(font_values)
        self.label_elim_valor.setStyleSheet("color: #FF55FF; border: none;")

        self.label_rest_titulo = QLabel('Restantes:', self.panel1)
        self.label_rest_titulo.setGeometry(8, 115, 95, 20)
        self.label_rest_titulo.setFont(font_labels)
        self.label_rest_titulo.setStyleSheet("color: red; border: none;")

        self.label_rest_valor = QLabel('100', self.panel1)
        self.label_rest_valor.setGeometry(110, 115, 60, 20)
        self.label_rest_valor.setFont(font_values)
        self.label_rest_valor.setStyleSheet("color: #55FF55; border: none;")

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo - Menú Experimento para simular 50 partidas")

        # Estructuración de la barra de menús
        menu_bar = self.menuBar()
        menu_archivo = menu_bar.addMenu('Archivo')

        action_nuevo = QAction('Nuevo Juego', self)
        action_nuevo.triggered.connect(self.button1_click)
        menu_archivo.addAction(action_nuevo)

        action_salir = QAction('Salir', self)
        action_salir.triggered.connect(self.close)
        menu_archivo.addAction(action_salir)

        menu_modos = menu_bar.addMenu('Modo de Bot')
        grupo_modos = QActionGroup(self)

        # Añadimos la nueva IA Avanzada a la barra de selección
        for modo in ["AdvHeuristic", "Greedy", "Heurístico", "Random"]:
            act = QAction(modo, self, checkable=True)
            if modo == "AdvHeuristic": act.setChecked(True)
            act.triggered.connect(lambda checked, m=modo: self.cambiar_modo(m))
            grupo_modos.addAction(act)
            menu_modos.addAction(act)

        menu_lab = menu_bar.addMenu('Experimento')
        action_bench = QAction('Correr Benchmark (50 Partidas)', self)
        action_bench.triggered.connect(self.ejecutar_benchmark)
        menu_lab.addAction(action_bench)

    def cambiar_modo(self, nuevo_modo):
        self.modo_bot = nuevo_modo
        self.label_modo.setText(nuevo_modo)
        self.status_bar.showMessage(f"Modo cambiado a: {nuevo_modo}")

    def button1_click(self):
        self.label2.setText('0')
        self.label_elim_valor.setText('0')
        self.label_rest_valor.setText('100')
        self.tot_puntos = 0
        self.total_bloques_eliminados_partida = 0
        self.bloques_seleccionados_bot.clear()
        for i in range(10):
            for c in range(10):
                self.MyArray[c][i] = random.randint(3, 7)
        self.game_active = True
        self.modo_laboratorio = False
        self.status_bar.showMessage(f"IA en modo [{self.modo_bot}] activa...")
        self.tablero.update()
        if self.timer_bot is None:
            self.timer_bot = QTimer(self)
            self.timer_bot.timeout.connect(self.ejecutar_ciclo_bot)
        if not self.timer_bot.isActive():
            self.timer_bot.start(1000)

    def calcular_puntuaje(self):
        tabla_puntos = {2: 100, 3: 200, 4: 400, 5: 700, 6: 1100, 7: 1600,
                        8: 2200, 9: 2900, 10: 3700, 11: 4600, 12: 5600}
        puntos = tabla_puntos.get(self.puntos_eliminados_ronda, 0)
        if self.puntos_eliminados_ronda > 12:
            puntos = 5600 + (self.puntos_eliminados_ronda - 12) * 1200
        self.tot_puntos += puntos
        if not self.modo_laboratorio:
            self.label2.setText(str(self.tot_puntos))

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
        """Aplica gravedad y compresión horizontal a una matriz dada (real o simulada)."""
        for c in range(10):
            col_filt = [matriz[c][i] for i in range(10) if matriz[c][i] != 0]
            matriz[c] = [0] * (10 - len(col_filt)) + col_filt

        columnas_vivas = [matriz[c] for c in range(10) if any(matriz[c][i] != 0 for i in range(10))]
        columnas_vivas += [[0] * 10 for _ in range(10 - len(columnas_vivas))]
        for c in range(10):
            matriz[c] = columnas_vivas[c]

    def aplicar_fisicas_reales(self):
        self.aplicar_fisicas_en_matriz(self.MyArray)

    def contar_grupo_simulado(self, w, z, target_val, visitados, matriz=None):
        if matriz is None: matriz = self.MyArray
        if w < 0 or w > 9 or z < 0 or z > 9: return 0
        if (w, z) in visitados or matriz[w][z] != target_val: return 0
        visitados.add((w, z))
        count = 1
        count += self.contar_grupo_simulado(w - 1, z, target_val, visitados, matriz)
        count += self.contar_grupo_simulado(w + 1, z, target_val, visitados, matriz)
        count += self.contar_grupo_simulado(w, z - 1, target_val, visitados, matriz)
        count += self.contar_grupo_simulado(w, z + 1, target_val, visitados, matriz)
        return count

    def actualizar_contadores_interfaz(self):
        vivos = sum(1 for c in range(10) for i in range(10) if self.MyArray[c][i] != 0)
        self.total_bloques_eliminados_partida += self.puntos_eliminados_ronda
        if not self.modo_laboratorio:
            self.label_elim_valor.setText(str(self.total_bloques_eliminados_partida))
            self.label_rest_valor.setText(str(vivos))

    def finalizar_partida(self):
        if not self.modo_laboratorio: self.timer_bot.stop()
        atrapadas = sum(1 for c in range(10) for i in range(10) if self.MyArray[c][i] != 0)
        self.game_active = False
        if not self.modo_laboratorio:
            self.label_rest_valor.setText(str(atrapadas))
            self.status_bar.showMessage(f"Fin. Método: {self.modo_bot} | Quedaron: {atrapadas}")

    # LÓGICA DE EVALUACIÓN PREDICTIVA AVANZADA
    def evaluar_tablero_futuro(self, c_origen, i_origen, target_val):
        """Simula una jugada y devuelve una puntuación heurística basada en la salud del tablero."""
        matriz_temp = [fila[:] for fila in self.MyArray]

        # 1. Simular eliminación del grupo y aplicar físicas de gravedad en memoria
        self.puntos_eliminados_ronda = 0
        self.eliminar_recursivo_matriz(matriz_temp, c_origen, i_origen, target_val)
        self.aplicar_fisicas_en_matriz(matriz_temp)

        # 2. Analizar el tablero resultante
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

        # Ecuación de Salud de Heurística Avanzada
        score_salud = conectividad_total - (bloques_aislados * 15) + (columnas_vacias * 50)
        return score_salud

    def ejecutar_ciclo_bot(self):
        if not self.game_active: return
        movimientos_validos = []
        for c in range(10):
            for i in range(10):
                val_actual = self.MyArray[c][i]
                if val_actual != 0:
                    visitados_temp = set()
                    tamano = self.contar_grupo_simulado(c, i, val_actual, visitados_temp)
                    if tamano >= 2: movimientos_validos.append((tamano, i, c, visitados_temp))

        if not movimientos_validos:
            self.finalizar_partida()
            return

        # SELECCIÓN ESTRATÉGICA SEGÚN ALGORITMO
        if self.modo_bot == "AdvHeuristic":
            # Ejecuta la simulación predictiva para cada jugada posible y escoge el puntaje más alto
            mejor = max(movimientos_validos,
                        key=lambda x: (self.evaluar_tablero_futuro(x[2], x[1], self.MyArray[x[2]][x[1]]), x[0], x[1]))
        elif self.modo_bot == "Greedy":
            mejor = max(movimientos_validos, key=lambda x: (x[0], x[1], x[2]))
        elif self.modo_bot == "Heurístico":
            mejor = max(movimientos_validos, key=lambda x: (x[1], x[0], x[2]))
        elif self.modo_bot == "Random":
            mejor = random.choice(movimientos_validos)

        tamano_g, coord_i, coord_c, celdas_grupo = mejor
        if not self.modo_laboratorio:
            self.bloques_seleccionados_bot = celdas_grupo
            self.tablero.update()

        self.puntos_eliminados_ronda = 0
        target_val = self.MyArray[coord_c][coord_i]
        self.eliminar_recursivo_matriz(self.MyArray, coord_c, coord_i, target_val)
        self.calcular_puntuaje()
        self.aplicar_fisicas_reales()
        self.actualizar_contadores_interfaz()

        if not self.modo_laboratorio:
            self.bloques_seleccionados_bot.clear()
            self.tablero.update()

    def ejecutar_benchmark(self):
        self.status_bar.showMessage("Ejecutando experimento con IA Avanzada...")
        QApplication.processEvents()
        self.modo_laboratorio = True

        tableros_prueba = [[[random.randint(3, 7) for _ in range(10)] for _ in range(10)] for _ in range(50)]
        resultados = {"AdvHeuristic": {"puntos": [], "sobrantes": []},
                      "Greedy": {"puntos": [], "sobrantes": []},
                      "Heurístico": {"puntos": [], "sobrantes": []},
                      "Random": {"puntos": [], "sobrantes": []}}

        for algoritmo in resultados.keys():
            self.modo_bot = algoritmo
            for idx in range(50):
                self.MyArray = [fila[:] for fila in tableros_prueba[idx]]
                self.tot_puntos = 0
                self.puntos_eliminados_ronda = 0
                self.total_bloques_eliminados_partida = 0
                self.game_active = True
                while self.game_active:
                    self.ejecutar_ciclo_bot()

                sobrantes = sum(1 for c in range(10) for i in range(10) if self.MyArray[c][i] != 0)
                resultados[algoritmo]["puntos"].append(self.tot_puntos)
                resultados[algoritmo]["sobrantes"].append(sobrantes)

        reporte = "====================================================\n"
        reporte += "     REPORTE CIENTÍFICO CON IA AVANZADA (50 Tests)\n"
        reporte += "====================================================\n"
        for alg, data in resultados.items():
            prom_puntos = sum(data["puntos"]) / 50
            prom_sobrantes = sum(data["sobrantes"]) / 50
            reporte += f"🤖 Algoritmo: {alg:<14}\n"
            reporte += f"   • Promedio Puntos: {prom_puntos:.1f}\n"
            reporte += f"   • Bloques Atrapados promedio: {prom_sobrantes:.2f}\n"
            reporte += "----------------------------------------------------\n"

        with open("reporte_algoritmos.txt", "w", encoding="utf-8") as f:
            f.write(reporte)

        print("\n" + reporte)
        self.modo_laboratorio = False
        self.label_modo.setText(self.modo_bot)
        self.status_bar.showMessage("¡Benchmark finalizado! Datos guardados con éxito.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = BloquesGame()
    game.show()
    sys.exit(app.exec())
