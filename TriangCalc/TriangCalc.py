import math

def showvalues():
    print("\n")
    print(f"The Cathetus A sizes: {cathetus_a:.2f}")
    print(f"The Cathetus B sizes: {cathetus_b:.2f}")
    print(f"The length of the Hypotenuse is: {hypotenuse:.2f}")

def showinputnumbermsj():
    print('Input a valid number')

def showvalidoptionmsj():
    print('Input a valid option')

def calccathetusvalue(hypotenusevalue, cathetusvalue):
    return math.sqrt((hypotenusevalue ** 2) - (cathetusvalue ** 2))

cathetus_a_inputmsj = 'Input the size of Cathetus A:'
cathetus_b_inputmsj = 'Input the size of Cathetus B:'
hypotenuse_input_msj = 'Input the size of the Hypotenuse:'

print('\nCalculate the Hypotenuse (H), Cathetus A (A) or Cathetus B (B)\n')

while True:
    option = input('\nPress either H, A, B or E to Exit + Enter key: ')
    match option:
        case "H" | "h":
            while True:
                try:
                    cathetus_a = float(input(cathetus_a_inputmsj))
                    if cathetus_a>0:
                        break
                    else:
                        showinputnumbermsj()
                except ValueError:
                    showinputnumbermsj()

            while True:
                try:
                    cathetus_b = float(input(cathetus_b_inputmsj))
                    if cathetus_b>0:
                        break
                    else:
                        showinputnumbermsj()
                except ValueError:
                    showinputnumbermsj()

            hypotenuse = math.hypot(cathetus_a, cathetus_b)
            showvalues()

        case "A" | "a":
            while True:
                try:
                    cathetus_b = float(input(cathetus_b_inputmsj))
                    if cathetus_b > 0:
                        break
                    else:
                        showinputnumbermsj()
                except ValueError:
                    showinputnumbermsj()

            while True:
                try:
                    hypotenuse = float(input(hypotenuse_input_msj))
                    if hypotenuse > 0:
                        break
                    else:
                        showinputnumbermsj()
                except ValueError:
                    showinputnumbermsj()

            #cathetus_a = math.sqrt((hypotenuse ** 2) - (cathetus_b ** 2))
            cathetus_a=calccathetusvalue(hypotenuse, cathetus_b)
            showvalues()

        case "B" | "b":
            while True:
                try:
                    cathetus_a = float(input(cathetus_a_inputmsj))
                    if cathetus_a > 0:
                        break
                    else:
                        showinputnumbermsj()
                except ValueError:
                    showinputnumbermsj()

            while True:
                try:
                    hypotenuse = float(input(hypotenuse_input_msj))
                    if hypotenuse>0:
                        break
                    else:
                        showinputnumbermsj()
                except ValueError:
                    showinputnumbermsj()

            #cathetus_b = math.sqrt((hypotenuse ** 2) - (cathetus_a ** 2))
            cathetus_b = calccathetusvalue(hypotenuse, cathetus_a)
            showvalues()

        case "E" | "e":
            break
        case _:
            showvalidoptionmsj()