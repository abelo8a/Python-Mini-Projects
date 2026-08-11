import math


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


def show_values(cathetus_a, cathetus_b, hypotenuse):
    """Muestra los resultados formateados en pantalla."""
    print(f"\nThe Cathetus A size: {cathetus_a:.2f}")
    print(f"The Cathetus B size: {cathetus_b:.2f}")
    print(f"The length of the Hypotenuse is: {hypotenuse:.2f}")


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
            # Si eligen A pedimos B, si eligen B pedimos A
            is_option_a = (option == "a")
            known_cathetus = get_positive_float(msg_b if is_option_a else msg_a)

            while True:
                hypotenuse = get_positive_float(msg_h)
                if hypotenuse > known_cathetus:
                    break
                print("Error: The Hypotenuse must be larger than the Cathetus.")

            calculated_cathetus = math.sqrt((hypotenuse ** 2) - (known_cathetus ** 2))

            # Asignar correctamente las variables para la función de impresión
            cathetus_a = calculated_cathetus if is_option_a else known_cathetus
            cathetus_b = known_cathetus if is_option_a else calculated_cathetus
            show_values(cathetus_a, cathetus_b, hypotenuse)

        case "e":
            print("Exiting program...")
            break

        case _:
            print('Input a valid option')