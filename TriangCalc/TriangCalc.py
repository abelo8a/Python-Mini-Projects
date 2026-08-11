import math
import matplotlib.pyplot as plt


def get_positive_float(prompt_message):
    """Solicita un número flotante y valida que sea mayor a cero."""
    while True:
        try:
            value = float(input(prompt_message))
            if value > 0:
                return value
            print('Input a valid number (must be greater than 0)')
        except ValueError:
            print('Input a valid number')


def plot_triangle(cathetus_a, cathetus_b, angle_a, angle_b):
    """Genera una gráfica del triángulo rectángulo con información de los ángulos."""
    # Coordenadas de los tres vértices: (0,0), (Base, 0), (0, Altura)
    x = [0, cathetus_a, 0, 0]
    y = [0, 0, cathetus_b, 0]

    plt.figure(figsize=(6, 5))
    plt.plot(x, y, marker='o', color='b', linestyle='-', linewidth=2)
    plt.fill(x, y, color='skyblue', alpha=0.4)  # Rellenar el triángulo

    # Etiquetas de los lados
    plt.text(cathetus_a / 2, -0.06 * cathetus_b, f'A = {cathetus_a:.2f}', ha='center', va='top', fontsize=10,
             weight='bold')
    plt.text(-0.06 * cathetus_a, cathetus_b / 2, f'B = {cathetus_b:.2f}', ha='right', va='center', fontsize=10,
             weight='bold')
    plt.text(cathetus_a / 2, cathetus_b / 2, f'H', ha='left', va='bottom', fontsize=10, weight='bold', color='darkblue')

    # Etiquetas de los ángulos en los vértices correspondientes
    plt.text(0.03 * cathetus_a, 0.03 * cathetus_b, '90°', ha='left', va='bottom', fontsize=9, color='red',
             weight='bold')
    plt.text(cathetus_a * 0.85, 0.03 * cathetus_b, f'{angle_a:.1f}°', ha='right', va='bottom', fontsize=9,
             color='purple', weight='bold')
    plt.text(0.03 * cathetus_a, cathetus_b * 0.85, f'{angle_b:.1f}°', ha='left', va='top', fontsize=9, color='purple',
             weight='bold')

    plt.title('Triángulo Rectángulo Resultante')
    plt.xlabel('Eje X (Cateto A)')
    plt.ylabel('Eje Y (Cateto B)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.gca().set_aspect('equal', adjustable='box')  # Mantiene la proporción visual real

    print("\n[INFO] Cerrar la ventana del gráfico para continuar en la consola...")
    plt.show()


def show_values(cathetus_a, cathetus_b, hypotenuse):
    """Muestra los resultados matemáticos calculados de geometría y trigonometría."""
    # Fórmulas de Perímetro y Área
    perimeter = cathetus_a + cathetus_b + hypotenuse
    area = (cathetus_a * cathetus_b) / 2

    # Cálculo de ángulos internos usando funciones trigonométricas inversas (Arctan)
    # math.degrees() transforma los radianes nativos de Python a grados tradicionales
    angle_right = 90.0
    angle_a = math.degrees(math.atan2(cathetus_b, cathetus_a))
    angle_b = 180.0 - angle_right - angle_a  # La suma interna siempre da 180°

    print(f"\n" + "=" * 40)
    print(f"  RESULTADOS DEL TRIÁNGULO")
    print(f"" + "=" * 40)
    print(f"• Cateto A:     {cathetus_a:.2f}")
    print(f"• Cateto B:     {cathetus_b:.2f}")
    print(f"• Hipotenusa:   {hypotenuse:.2f}")
    print(f"-" * 40)
    print(f"• Perímetro:    {perimeter:.2f}")
    print(f"• Área:         {area:.2f}")
    print(f"-" * 40)
    print(f"• Ángulo Recto (C): {angle_right:.2f}°")
    print(f"• Ángulo opuesto a B (α): {angle_a:.2f}°")
    print(f"• Ángulo opuesto a A (β): {angle_b:.2f}°")
    print(f"=" * 40)

    # Llamar a la función gráfica pasando los nuevos parámetros de ángulos
    plot_triangle(cathetus_a, cathetus_b, angle_a, angle_b)


# Mensajes de los prompts
msg_a = 'Input the size of Cathetus A: '
msg_b = 'Input the size of Cathetus B: '
msg_h = 'Input the size of the Hypotenuse: '

print('\nCalculate the Hypotenuse (H), Cathetus A (A) or Cathetus B (B)')

while True:
    option = input('\nPress either H, A, B or E to Exit + Enter key: ').strip().lower()

    match option:
        case "h":
            cathetus_a = get_positive_float(msg_a)
            cathetus_b = get_positive_float(msg_b)
            hypotenuse = math.hypot(cathetus_a, cathetus_b)
            show_values(cathetus_a, cathetus_b, hypotenuse)

        case "a" | "b":
            is_option_a = (option == "a")
            known_cathetus = get_positive_float(msg_b if is_option_a else msg_a)

            while True:
                hypotenuse = get_positive_float(msg_h)
                if hypotenuse > known_cathetus:
                    break
                print("Error: The Hypotenuse must be larger than the Cathetus.")

            calculated_cathetus = math.sqrt((hypotenuse ** 2) - (known_cathetus ** 2))

            cathetus_a = calculated_cathetus if is_option_a else known_cathetus
            cathetus_b = known_cathetus if is_option_a else calculated_cathetus
            show_values(cathetus_a, cathetus_b, hypotenuse)

        case "e":
            print("Exiting program...")
            break

        case _:
            print('Input a valid option')
