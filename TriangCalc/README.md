# 📐 Triangle Calculator & Visualizer

Una aplicación interactiva de consola escrita en Python para resolver, registrar y visualizar triángulos rectángulos a partir de sus componentes conocidos (Teorema de Pitágoras y Trigonometría).

## ✨ Características Principales

*   **Cálculo flexible:** Resuelve el triángulo ingresando la Hipotenusa, el Cateto A o el Cateto B.
*   **Resultados completos:** Calcula automáticamente hipotenusa/catetos faltantes, perímetro, área y los ángulos internos en grados.
*   **Visualización gráfica:** Genera y despliega dinámicamente un gráfico bidimensional del triángulo resultante con sus etiquetas correspondientes.
*   **Historial persistente:** Guarda un registro detallado de cada cálculo con fecha y hora en un archivo local (`historial_triangulos.txt`).
*   **Validación robusta:** Maneja errores de entrada (strings, valores negativos) y valida reglas geométricas (la hipotenusa siempre debe ser mayor que los catetos).

## 🚀 Tecnologías Utilizadas

*   **Python 3.10+** (Utiliza estructuras modernas como `match-case`).
*   **Matplotlib** (Para la renderización gráfica del triángulo).
*   **Math** & **Datetime** (Módulos nativos estándar).

## 📦 Requisitos e Instalación

1. **Clona este repositorio:**
   ```bash
   git clone https://github.com
   cd triangle-calculator
   ```

2. **Instala las dependencias necesarias:**
   Este proyecto requiere `matplotlib` para la parte gráfica. Puedes instalarlo ejecutando:
   ```bash
   pip install matplotlib
   ```

## 🛠️ Cómo Ejecutar el Programa

Inicia la aplicación ejecutando el script principal desde tu terminal:

```bash
python TriangCalc.py
```

### Opciones del Menú:
*   `H`: Calcular la **Hipotenusa** ingresando ambos catetos.
*   `A` / `B`: Calcular un **Cateto faltante** ingresando el cateto conocido y la hipotenusa.
*   `V`: **Ver el historial** de cálculos almacenados directamente en la consola.
*   `E`: **Salir** del programa de forma segura.

## 📊 Ejemplo de Salida (Archivo de Historial)

Cada vez que realizas un cálculo exitoso, el sistema genera de forma automática una entrada estructurada en `historial_triangulos.txt` similar a esta:

```text
====================================================
REGISTRO DE CÁLCULO: 2026-08-11 15:45:23
====================================================
• Cateto A:              3.00
• Cateto B:              4.00
• Hipotenusa:            5.00
----------------------------------------------------
• Perímetro:             12.00
• Área:                  6.00
----------------------------------------------------
• Ángulo Recto (C):      90.00°
• Ángulo opuesto a B (α): 53.13°
• Ángulo opuesto a A (β): 36.87°
====================================================
```
