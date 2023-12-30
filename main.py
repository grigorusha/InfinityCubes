# Импортируем библиотеку pygame
import pygame
from pygame import *
import random

import webbrowser
from tkinter import Tk
from tkinter import filedialog as fd
import os

# Объявляем базовые переменные
SIZE_X_START = 3
SIZE_Y_START = 3
CUBE_SIZE = 100
BORDER = 5
TILE = 10
SHIFT = 3
PANEL_SIZE = 30*4+4

BACKGROUND_COLOR = "#000000"
GRAY_COLOR = "#808080"
GRAY_COLOR2 = "#A0A0A0"

CUBE_COLOR = [("W","#FFFFFF"),("R","#FF0000"),("B","#0000FF"),
              ("Y","#FFFF00"),("P","#800080"),("G","#008000")]
level = []
level_digit = []

def init_level(y,x):
    # инициализация уровня
    level = []
    for ny in range(y):
        str = []
        for nx in range(x):
            # передняя и верхняя стороны кубика. достаточно для ориентации (нач коорд - лев верх угол)
            str.append(["W", "B"])
        level.append(str)
    return level

def init_level_digit(y,x,level):
    level_digit = []
    nn = 1
    for ny in range(y):
        stroka = []
        for nx in range(x):
            cube = level[ny][nx]
            stroka.append(str(nn))
            nn += 1
        level_digit.append(stroka)

    return level_digit

def next_cubes(top, face):
    for face_ind, COLOR_ONE in enumerate(CUBE_COLOR):
        if COLOR_ONE[0] == face:
            break
    for top_ind, COLOR_ONE in enumerate(CUBE_COLOR):
        if COLOR_ONE[0] == top:
            break

    back_ind = (top_ind + 3)%6
    vek = 1-(top_ind % 2)*2

    face_set = CUBE_COLOR.copy()
    face1 = min(top_ind, back_ind)
    face_set.pop(face1)
    face_set.pop(face1+2)

    if vek < 0:
        face_set.reverse()

    while face_set[0][0]!=face:
        elem = face_set.pop(0)
        face_set.append(elem)

    return face_set

def turn_cube(cube, vek):
    face_set = next_cubes(cube[0], cube[1])
    face_set2 = next_cubes(face_set[4 - vek][0], cube[0])
    if vek == 1:  # UP
        cube = [face_set2[3][0], face_set2[2][0]]
    elif vek == 3:  # DOWN
        cube = [face_set2[3][0], face_set2[0][0]]
    elif vek == 2:  # LEFT
        cube = [face_set2[3][0], cube[1]]
    elif vek == 4:  # RIGHT
        cube = [face_set2[3][0], cube[1]]
    return cube

def check_button(place, y, x):
    if (x >= place.left) and (x <= place.right) and (y >= place.top) and (y <= place.bottom):
        return True
    return False

def read_file():
    dir = os.path.abspath(os.curdir)
    filetypes = (("Text file", "*.txt"),("Any file", "*"))
    filename = fd.askopenfilename(title="Open Level", initialdir=dir,filetypes=filetypes)
    if filename=="":
        return ""

    x = y = 0
    level = []
    digit_mode = False
    level_digit = []
    with open(filename,'r') as f:
        lines = f.readlines()
        for str in lines:
            str = str.replace('\n','').strip()
            if str=="!":
                digit_mode = True
                continue
            if not digit_mode:
                str_mas = []
                while len(str)>=2:
                    sim1 = str[0]
                    sim2 = str[1]
                    str = str[3:]
                    str_mas.append([sim1,sim2])
                level.append(str_mas)
                y += 1
                x = max(x,len(str_mas))
            else:
                str_mas = str.split(" ")
                level_digit.append(str_mas)

    return level, y, x, digit_mode, level_digit

def save_file(level, digit_mode, level_digit):
    dir = os.path.abspath(os.curdir)
    filetypes = (("Text file", "*.txt"),("Any file", "*"))
    filename = fd.asksaveasfile("w", title="Save Level as...", initialdir=dir,filetypes=filetypes)
    if filename==None:
        return ""

    with open(filename.name, 'w') as f:
        for stroka in level:
            line = ""
            for cube in stroka:
                line += cube[0]+cube[1]+" "
            f.write(line+"\n")

        if digit_mode:
            f.write("!\n")
            for stroka in level_digit:
                line = ""
                for digit in stroka:
                    line += digit+" "
                f.write(line+"\n")

def main():
    # основные константы
    SIZE_X = SIZE_X_START
    SIZE_Y = SIZE_Y_START
    file_ext = False
    digit_mode = False

    # основная инициализация
    random.seed()
    pygame.init()  # Инициация PyGame
    font = pygame.font.SysFont('Verdana', 18)
    fontd = pygame.font.SysFont('Verdana', 24)
    timer = pygame.time.Clock()
    Tk().withdraw()

    icon = os.path.abspath(os.curdir) + "\\InfinityCubes.ico"
    if os.path.isfile(icon):
        pygame.display.set_icon(pygame.image.load(icon))

    ################################################################################
    ################################################################################
    # перезапуск программы при смене параметров
    while True:
        # дополнительные константы
        WIN_WIDTH = SIZE_X * CUBE_SIZE  # Ширина создаваемого окна
        WIN_HEIGHT = SIZE_Y * CUBE_SIZE + PANEL_SIZE  # Высота
        DISPLAY = (WIN_WIDTH, WIN_HEIGHT)  # Группируем ширину и высоту в одну переменную

        if file_ext:
            file_ext = False
        else:
            level = init_level(SIZE_Y, SIZE_X)
            level_digit = init_level_digit(SIZE_Y, SIZE_X, level)
        moves_stack = []
        moves = 0
        solved = True
        scramble_move = 0

        # инициализация окна
        screen = pygame.display.set_mode(DISPLAY)  # Создаем окошко
        pygame.display.set_caption("Infinity Cubes")  # Пишем в шапку
        screen.fill(BACKGROUND_COLOR) # Заливаем поверхность сплошным цветом

        # инициализация всех кнопок
        button_y1 = CUBE_SIZE * SIZE_Y + BORDER + 10
        button_reset = font.render('Reset', True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        button_reset_place = button_reset.get_rect(topleft=(10, button_y1))
        button_scramble = font.render('Scramble', True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        button_scramble_place = button_scramble.get_rect(topleft=(button_reset_place.right+10, button_y1))
        button_undo = font.render('Undo', True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        button_undo_place = button_undo.get_rect(topleft=(button_scramble_place.right+10, button_y1))

        button_y2 = button_reset_place.bottom + 5
        button_minusx = font.render('-', True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        button_minusx_place = button_minusx.get_rect(topleft=(10, button_y2))
        textx = font.render(str(SIZE_X), True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        textx_place = textx.get_rect(topleft=(button_minusx_place.right+3, button_y2))
        button_plusx = font.render('+', True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        button_plusx_place = button_plusx.get_rect(topleft=(textx_place.right+3, button_y2))
        button_minusy = font.render('-', True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        button_minusy_place = button_minusy.get_rect(topleft=(button_plusx_place.right+10, button_y2))
        texty = font.render(str(SIZE_Y), True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        texty_place = texty.get_rect(topleft=(button_minusy_place.right+3, button_y2))
        button_plusy = font.render('+', True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        button_plusy_place = button_plusy.get_rect(topleft=(texty_place.right+3, button_y2))
        button_open = font.render('Open', True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        button_open_place = button_open.get_rect(topleft=(button_plusy_place.right+10, button_y2))
        button_save = font.render('Save', True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
        button_save_place = button_save.get_rect(topleft=(button_open_place.right+10, button_y2))

        button_y3 = button_minusx_place.bottom + 5

        ################################################################################
        ################################################################################
        # Основной цикл программы
        while True:
            vek = mouse_x = mouse_y = cube_pos_x = cube_pos_y = 0
            undo = False

            ################################################################################
            ################################################################################
            # отрисовка элементов меню и кнопок

            if scramble_move == 0:

                # menu
                pf_black = Surface((CUBE_SIZE*SIZE_X, PANEL_SIZE))
                pf_black.fill(Color("#000000"))
                screen.blit(pf_black, (0, CUBE_SIZE*SIZE_Y))
                pf = Surface((CUBE_SIZE*SIZE_X, 5))
                pf.fill(Color("#B88800"))
                screen.blit(pf, (0, CUBE_SIZE*SIZE_Y+BORDER))

                button_info = font.render('Puzzle Photo ->', True, CUBE_COLOR[0][1], CUBE_COLOR[2][1])
                button_info_place = button_info.get_rect(topleft=(10, button_y3))
                button_about = font.render('About ->', True, CUBE_COLOR[0][1], CUBE_COLOR[2][1])
                button_about_place = button_about.get_rect(topleft=(button_info_place.right + 10, button_y3))

                button_y4 = button_info_place.bottom + 5
                if digit_mode:
                    button_digit = font.render('Digits', True, CUBE_COLOR[2][1], CUBE_COLOR[3][1])
                else:
                    button_digit = font.render('Digits', True, CUBE_COLOR[2][1], CUBE_COLOR[5][1])
                button_digit_place = button_digit.get_rect(topleft=(10, button_y4))

                # text
                text_moves = font.render('Moves: ' + str(moves), True, CUBE_COLOR[1][1])
                text_moves_place = text_moves.get_rect(topleft=(button_digit_place.right+10, button_y4))
                screen.blit(text_moves, text_moves_place)
                if solved:
                    text_solved = font.render('Solved', True, CUBE_COLOR[0][1])
                else:
                    text_solved = font.render('not solved', True, CUBE_COLOR[5][1])
                text_solved_place = text_solved.get_rect(topleft=(text_moves_place.right + 10, button_y4))
                screen.blit(text_solved, text_solved_place)

                # button
                screen.blit(button_reset, button_reset_place)
                screen.blit(button_scramble, button_scramble_place)
                screen.blit(button_undo, button_undo_place)
                screen.blit(button_minusx, button_minusx_place)
                screen.blit(textx, textx_place)
                screen.blit(button_plusx, button_plusx_place)
                screen.blit(button_minusy, button_minusy_place)
                screen.blit(texty, texty_place)
                screen.blit(button_plusy, button_plusy_place)
                screen.blit(button_open, button_open_place)
                screen.blit(button_save, button_save_place)
                screen.blit(button_digit, button_digit_place)
                screen.blit(button_info, button_info_place)
                screen.blit(button_about, button_about_place)

            ################################################################################
            ################################################################################
            # обработка событий

            if scramble_move == 0:
                timer.tick(10)

                for ev in pygame.event.get():  # Обрабатываем события
                    if (ev.type == QUIT) or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                        return SystemExit, "QUIT"
                    if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                        mouse_x = ev.pos[0]
                        mouse_y = ev.pos[1]
                    if ev.type == MOUSEBUTTONDOWN and ev.button == 5:
                        mouse_x = button_undo_place.right
                        mouse_y = button_undo_place.top
            else:
                cube_pos_x = random.randint(0,SIZE_X-1)
                cube_pos_y = random.randint(0,SIZE_Y-1)
                vek = random.randint(1,4)
                mouse_x = mouse_y = 1

            ################################################################################
            ################################################################################
            # обработка нажатия на кнопки

            if mouse_x+mouse_y > 0 and scramble_move == 0:
                if mouse_y>CUBE_SIZE*SIZE_Y+BORDER:
                    if check_button(button_reset_place, mouse_y, mouse_x): # reset
                        break
                    elif check_button(button_scramble_place, mouse_y, mouse_x):  # scramble
                        scramble_move = SIZE_X * SIZE_Y * 1000
                    elif check_button(button_undo_place, mouse_y, mouse_x):  # undo
                        if len(moves_stack) > 0:
                            vek,cube_pos_y,cube_pos_x = moves_stack.pop()
                            vek = (vek + 1) % 4 + 1
                            moves -= 1
                            undo = True
                    elif check_button(button_open_place, mouse_y, mouse_x):  # open
                        fil = read_file()
                        if fil!="":
                            level, SIZE_Y, SIZE_X, digit_mode, level_digit = fil
                            file_ext = True
                            break
                    elif check_button(button_save_place, mouse_y, mouse_x):  # save
                        save_file(level, digit_mode, level_digit)
                    elif check_button(button_digit_place, mouse_y, mouse_x):  # digit
                        digit_mode = not digit_mode
                    elif check_button(button_about_place, mouse_y, mouse_x):  # about
                        webbrowser.open("https://github.com/grigorusha/InfinityCubes", new=2, autoraise=True)
                        webbrowser.open("https://twistypuzzles.com/forum/viewtopic.php?t=38581", new=2, autoraise=True)
                    elif check_button(button_info_place, mouse_y, mouse_x):  # photo
                        webbrowser.open("https://twistypuzzles.com/forum/viewtopic.php?t=39088", new=2, autoraise=True)

                    elif check_button(button_minusx_place, mouse_y, mouse_x):
                        if SIZE_X > 2:
                            SIZE_X -= 1
                        break
                    elif check_button(button_plusx_place, mouse_y, mouse_x):
                        if SIZE_X < 10:
                            SIZE_X += 1
                        break
                    elif check_button(button_minusy_place, mouse_y, mouse_x):
                        if SIZE_Y > 2:
                            SIZE_Y -= 1
                            pos = pygame.mouse.get_pos()
                            pygame.mouse.set_pos(pos[0], pos[1] - CUBE_SIZE)
                        break
                    elif check_button(button_plusy_place, mouse_y, mouse_x):
                        if SIZE_Y < 10:
                            SIZE_Y += 1
                            pos = pygame.mouse.get_pos()
                            pygame.mouse.set_pos(pos[0], pos[1]+CUBE_SIZE)
                        break

                ################################################################################
                ################################################################################
                # обработка нажатия на кубики в игровом поле

                else:
                    # определим координаты кубика
                    xx = mouse_x // CUBE_SIZE
                    xx2 = mouse_x % CUBE_SIZE
                    if xx2>0:
                        xx += 1
                    yy = mouse_y // CUBE_SIZE
                    yy2 = mouse_y % CUBE_SIZE
                    if yy2>0:
                        yy += 1
                    xx -= 1
                    yy -= 1

                    cube_pos_x = xx
                    cube_pos_y = yy

                    # определим сторону на которую нажали
                    nn1 = xx2>yy2
                    nn2 = (CUBE_SIZE-xx2)>yy2
                    vek = 0
                    if nn1 and nn2:
                        vek = 1
                    elif (not nn1) and nn2:
                        vek = 2
                    elif (not nn1) and (not nn2):
                        vek = 3
                    elif nn1 and (not nn2):
                        vek = 4

            ################################################################################
            ################################################################################
            # логика игры - выполнение перемещений кубиков

            if vek!=0:
                # играем мышкой, координаты уже знаем
                nx = cube_pos_x
                ny = cube_pos_y

                # cube = level[yy][xx]
                # [yy-1][xx] : vek = 1
                # [yy][xx-1] : vek = 2
                # [yy+1][xx] : vek = 3
                # [yy][xx+1] : vek = 4

                # вращение кубиков
                if vek == 1:
                    cube_first = level[0][nx]
                    for yy in range(1,SIZE_Y):
                        cube = level[yy][nx]
                        cube = turn_cube(cube, vek)
                        level[yy-1][nx] = cube
                    cube = turn_cube(cube_first, vek)
                    level[SIZE_Y-1][nx] = cube
                if vek == 2:
                    cube_first = level[ny][0]
                    for xx in range(1,SIZE_X):
                        cube = level[ny][xx]
                        cube = turn_cube(cube, vek)
                        level[ny][xx-1] = cube
                    cube = turn_cube(cube_first, vek)
                    level[ny][SIZE_X-1] = cube
                if vek == 3:
                    cube_first = level[SIZE_Y-1][nx]
                    for yy in range(SIZE_Y-2,-1,-1):
                        cube = level[yy][nx]
                        cube = turn_cube(cube, vek)
                        level[yy+1][nx] = cube
                    cube = turn_cube(cube_first, vek)
                    level[0][nx] = cube
                if vek == 4:
                    cube_first = level[ny][SIZE_X-1]
                    for xx in range(SIZE_X-2,-1,-1):
                        cube = level[ny][xx]
                        cube = turn_cube(cube, vek)
                        level[ny][xx+1] = cube
                    cube = turn_cube(cube_first, vek)
                    level[ny][0] = cube

                if digit_mode:
                    if vek == 1:
                        digit_first = level_digit[0][nx]
                        for yy in range(1, SIZE_Y):
                            level_digit[yy - 1][nx] = level_digit[yy][nx]
                        level_digit[SIZE_Y - 1][nx] = digit_first
                    if vek == 2:
                        digit_first = level_digit[ny][0]
                        for xx in range(1,SIZE_X):
                            level_digit[ny][xx-1] = level_digit[ny][xx]
                        level_digit[ny][SIZE_X-1] = digit_first
                    if vek == 3:
                        digit_first = level_digit[SIZE_Y-1][nx]
                        for yy in range(SIZE_Y-2,-1,-1):
                            level_digit[yy+1][nx] = level_digit[yy][nx]
                        level_digit[0][nx] = digit_first
                    if vek == 4:
                        digit_first = level_digit[ny][SIZE_X-1]
                        for xx in range(SIZE_X-2,-1,-1):
                            level_digit[ny][xx+1] = level_digit[ny][xx]
                        level_digit[ny][0] = digit_first

                if not undo:
                    moves += 1
                    moves_stack.append([vek,ny,nx])

            if scramble_move != 0:
                scramble_move -= 1
                moves_stack = []
                moves = 0
                continue

            ################################################################################
            ################################################################################
            # отрисовка кубиков на игровом поле

            x = y = 0  # координаты
            for ny,row in enumerate(level):  # вся строка
                for nx,cube in enumerate(row):  # каждый куб
                    # верхняя плитка
                    pf = Surface((CUBE_SIZE-BORDER*2-TILE*2, CUBE_SIZE-BORDER*2-TILE*2))
                    for up,COLOR_ONE in enumerate(CUBE_COLOR):
                        if COLOR_ONE[0]==cube[0]:
                            pf.fill(Color(COLOR_ONE[1]))
                            break
                    screen.blit(pf, (x+BORDER+TILE, y+BORDER+TILE))

                    face_set = next_cubes(cube[0],cube[1])

                    # передняя плитка
                    for nn,COLOR_ONE in enumerate(CUBE_COLOR):
                        if COLOR_ONE[0]==face_set[0][0]:
                            draw.polygon(screen,COLOR_ONE[1], [[x+BORDER+TILE, y+CUBE_SIZE-BORDER-TILE],
                                                               [x+BORDER+TILE+CUBE_SIZE-BORDER*2-TILE*2, y+CUBE_SIZE-BORDER-TILE],
                                                               [x+BORDER+TILE+CUBE_SIZE-BORDER*2-TILE*2-SHIFT, y+CUBE_SIZE-BORDER-TILE+TILE],
                                                               [x+BORDER+TILE+SHIFT, y+CUBE_SIZE-BORDER-TILE+TILE]] )
                            break

                    # левая плитка
                    for nn,COLOR_ONE in enumerate(CUBE_COLOR):
                        if COLOR_ONE[0]==face_set[1][0]:
                            draw.polygon(screen,COLOR_ONE[1], [[x+BORDER, y+BORDER+TILE+SHIFT],
                                                               [x+BORDER+TILE, y+BORDER+TILE],
                                                               [x+BORDER+TILE, y+BORDER+TILE+CUBE_SIZE-BORDER*2-TILE*2],
                                                               [x+BORDER, y+BORDER+TILE+CUBE_SIZE-BORDER*2-TILE*2-SHIFT]] )
                            break

                    # задняя плитка
                    for nn,COLOR_ONE in enumerate(CUBE_COLOR):
                        if COLOR_ONE[0]==face_set[2][0]:
                            draw.polygon(screen,COLOR_ONE[1], [[x+BORDER+TILE+SHIFT, y+BORDER],
                                                               [x+BORDER+TILE+CUBE_SIZE-BORDER*2-TILE*2-SHIFT, y+BORDER],
                                                               [x+BORDER+TILE+CUBE_SIZE-BORDER*2-TILE*2, y+BORDER+TILE],
                                                               [x+BORDER+TILE, y+BORDER+TILE]] )
                            break

                    # правая плитка
                    for nn,COLOR_ONE in enumerate(CUBE_COLOR):
                        if COLOR_ONE[0]==face_set[3][0]:
                            draw.polygon(screen,COLOR_ONE[1], [[x+CUBE_SIZE-BORDER-TILE, y+BORDER+TILE],
                                                               [x+CUBE_SIZE-BORDER-TILE+TILE, y+BORDER+TILE+SHIFT],
                                                               [x+CUBE_SIZE-BORDER-TILE+TILE, y+BORDER+TILE+CUBE_SIZE-BORDER*2-TILE*2-SHIFT],
                                                               [x+CUBE_SIZE-BORDER-TILE, y+BORDER+TILE+CUBE_SIZE-BORDER*2-TILE*2]] )
                            break

                    # цифры
                    if digit_mode:
                        if level_digit[ny][nx]!="0":
                            digit = fontd.render(level_digit[ny][nx], True, BACKGROUND_COLOR)
                            digit_place = digit.get_rect(center=(x+CUBE_SIZE/2, y+CUBE_SIZE/2))
                            screen.blit(digit, digit_place)

                    x += CUBE_SIZE
                y += CUBE_SIZE
                x = 0

            # проверка решения
            solved = True
            for ny,row in enumerate(level):  # вся строка
                if not solved: break
                for nx,cube in enumerate(row):  # каждый куб
                    if cube[0]==" " or cube[0]=="X": continue
                    if (cube[0]!="W")or(cube[1]!="B"):
                        solved = False
                        break
            if digit_mode and solved:
                num = 1
                for row in level_digit:  # вся строка
                    if not solved: break
                    for dig in row:  # каждый куб
                        if dig == "0": continue
                        if dig != str(num):
                            solved = False
                            break
                        num += 1

            pygame.display.update()  # обновление и вывод всех изменений на экран

main()