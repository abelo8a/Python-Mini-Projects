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


def plot_triangle(cathetus_a, cathetus_b):
    """Genera una gráfica del triángulo rectángulo."""
    # Coordenadas de los tres vértices: (0,0), (Base, 0), (0, Altura)
    # Asignamos Cateto A a la base (X) y Cateto B a la altura (Y)
    x = [0, cathetus_a, 0, 0]
    y = [0, 0, cathetus_b, 0]

    plt.figure(figsize=(6, 5))
    plt.plot(x, y, marker='o', color='b', linestyle='-', linewidth=2)
    plt.fill(x, y, color='skyblue', alpha=0.4)  # Rellenar el triángulo

    # Etiquetas de los lados
    plt.text(cathetus_a / 2, -0.05 * cathetus_b, f'A = {cathetus_a:.2f}', ha='center', va='top', fontsize=10,
             weight='bold')
    plt.text(-0.05 * cathetus_a, cathetus_b / 2, f'B = {cathetus_b:.2f}', ha='right', va='center', fontsize=10,
             weight='bold')
    plt.text(cathetus_a / 2, cathetus_b / 2, f'H', ha='left', va='bottom', fontsize=10, weight='bold', color='darkblue')

    plt.title('Triángulo Rectángulo Resultante')
    plt.xlabel('Eje X (Cateto A)')
    plt.ylabel('Eje Y (Cateto B)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.gca().set_aspect('equal', adjustable='box')  # Mantiene la proporción visual real

    print("\n[INFO] Cerrar la ventana del gráfico para continuar en la consola...")
    plt.show()


def show_values(cathetus_a, cathetus_b, hypotenuse):
    """Muestra los resultados matemáticos calculados."""
    # Fórmulas de Perímetro y Área
    perimeter = cathetus_a + cathetus_b + hypotenuse
    area = (cathetus_a * cathetus_b) / 2

    print(f"\n" + "=" * 40)
    print(f"  RESULTADOS DEL TRIÁNGULO")
    print(f"" + "=" * 40)
    print(f"• Cateto A:     {cathetus_a:.2f}")
    print(f"• Cateto B:     {cathetus_b:.2f}")
    print(f"• Hipotenusa:   {hypotenuse:.2f}")
    print(f"-" * 40)
    print(f"• Perímetro:    {perimeter:.2f}")
    print(f"• Área:         {area:.2f}")
    print(f"=" * 40)

    # Llamar a la función gráfica
    plot_triangle(cathetus_a, cathetus_b)


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
