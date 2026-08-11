import math
from datetime import datetime
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


def save_to_history(cathetus_a, cathetus_b, hypotenuse, perimeter, area, angle_a, angle_b):
    """Guarda de forma permanente los resultados en un archivo de texto."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = (
        f"====================================================\n"
        f"REGISTRO DE CÁLCULO: {timestamp}\n"
        f"====================================================\n"
        f"• Cateto A:              {cathetus_a:.2f}\n"
        f"• Cateto B:              {cathetus_b:.2f}\n"
        f"• Hipotenusa:            {hypotenuse:.2f}\n"
        f"----------------------------------------------------\n"
        f"• Perímetro:             {perimeter:.2f}\n"
        f"• Área:                  {area:.2f}\n"
        f"----------------------------------------------------\n"
        f"• Ángulo Recto (C):      90.00°\n"
        f"• Ángulo opuesto a B (α): {angle_a:.2f}°\n"
        f"• Ángulo opuesto a A (β): {angle_b:.2f}°\n"
        f"====================================================\n\n"
    )

    try:
        with open("historial_triangulos.txt", "a", encoding="utf-8") as file:
            file.write(log_entry)
        print("[HISTORIAL] Resultados guardados con éxito en 'historial_triangulos.txt'")
    except IOError:
        print("[ERROR] No se pudo escribir en el archivo de historial.")


def show_history_in_console():
    """Lee el archivo de texto y muestra todo el historial en la consola."""
    print(f"\n" + "=" * 40)
    print(f"      MOSTRANDO HISTORIAL COMPLETO")
    print(f"==========================================")
    try:
        with open("historial_triangulos.txt", "r", encoding="utf-8") as file:
            content = file.read().strip()
            if content:
                print(content)
            else:
                print("El archivo de historial existe pero está vacío.")
    except FileNotFoundError:
        print("Aún no hay ningún registro en el historial. ¡Realiza tu primer cálculo!")
    print("=" * 40)


def plot_triangle(cathetus_a, cathetus_b, angle_a, angle_b):
    """Genera una gráfica del triángulo rectángulo con información de los ángulos."""
    x = [0, cathetus_a, 0, 0]
    y = [0, 0, cathetus_b, 0]

    plt.figure(figsize=(6, 5))
    plt.plot(x, y, marker='o', color='b', linestyle='-', linewidth=2)
    plt.fill(x, y, color='skyblue', alpha=0.4)

    plt.text(cathetus_a / 2, -0.06 * cathetus_b, f'A = {cathetus_a:.2f}', ha='center', va='top', fontsize=10,
             weight='bold')
    plt.text(-0.06 * cathetus_a, cathetus_b / 2, f'B = {cathetus_b:.2f}', ha='right', va='center', fontsize=10,
             weight='bold')
    plt.text(cathetus_a / 2, cathetus_b / 2, f'H', ha='left', va='bottom', fontsize=10, weight='bold', color='darkblue')

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
    plt.gca().set_aspect('equal', adjustable='box')

    print("\n[INFO] Cerrar la ventana del gráfico para continuar en la consola...")
    plt.show()


def show_values(cathetus_a, cathetus_b, hypotenuse):
    """Muestra los resultados en consola, los guarda y genera la gráfica."""
    perimeter = cathetus_a + cathetus_b + hypotenuse
    area = (cathetus_a * cathetus_b) / 2

    angle_right = 90.0
    angle_a = math.degrees(math.atan2(cathetus_b, cathetus_a))
    angle_b = 180.0 - angle_right - angle_a

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

    save_to_history(cathetus_a, cathetus_b, hypotenuse, perimeter, area, angle_a, angle_b)
    plot_triangle(cathetus_a, cathetus_b, angle_a, angle_b)


# Mensajes de los prompts
msg_a = 'Input the size of Cathetus A: '
msg_b = 'Input the size of Cathetus B: '
msg_h = 'Input the size of the Hypotenuse: '

print('\n==================================================================')
print('Calculate the Hypotenuse (H), Cathetus A (A) or Cathetus B (B)')
print('==================================================================')

while True:
    option = input('\nPress H, A, B, V (View History) or E (Exit) + Enter: ').strip().lower()

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

        case "v":
            show_history_in_console()

        case "e":
            print("Exiting program...")
            break

        case _:
            print('Input a valid option')
