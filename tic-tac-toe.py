def check_num(num):
    return False if not 1 <= num <= 9 else True

def check_xo(string):
    return False if string not in 'XO' else True

def check_end(matrix):
    return True if (matrix[0][0] == matrix[0][1] == matrix[0][2] \
            or matrix[1][0] == matrix[1][1] == matrix[1][2] \
            or matrix[2][0] == matrix[2][1] == matrix[2][2] \
            or matrix[0][0] == matrix[1][0] == matrix[2][0] \
            or matrix[0][1] == matrix[1][1] == matrix[2][1] \
            or matrix[0][2] == matrix[1][2] == matrix[2][2] \
            or matrix[0][0] == matrix[1][1] == matrix[2][2] \
            or matrix[0][2] == matrix[1][1] == matrix[2][0]) else False

def print_matrix(matrix):
    for row in range(3):
        print(*matrix[row])

matrix = [
     [1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]
]
print_matrix(matrix)
n_motion = 1
prev_run=''
while n_motion <= 9:
    print('введите цифру')
    answer_num = int(input())
    if not check_num(answer_num):
        print('Ошибка: введите число от 1 до 9!')
        continue

    row = (answer_num - 1) // 3
    col = answer_num - row * 3 - 1
    if not type(matrix[row][col]) == int:
        print('эту клетку уже выбирал игрок', matrix[row][col])
        continue

    print('введите Х or O')
    answer_xo = input()
    if not check_xo(answer_xo):
        print('Ошибка: введите X или О!')
        continue
    if answer_xo == prev_run:
        print('Не ваша очередь ходить!')
        continue
    prev_run = answer_xo

    matrix[row][col] = answer_xo
    n_motion += 1
    print_matrix(matrix)
    if check_end(matrix):
        print('выйграл',answer_xo)
        break
else:
    print('ничья')
