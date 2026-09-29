import pygame
import sys
import math
import os

# =========================================================
# INITIALIZE
# =========================================================

pygame.init()

try:
    pygame.mixer.init()
    mixer_available = True
except:
    mixer_available = False


# =========================================================
# FULLSCREEN
# =========================================================

info = pygame.display.Info()

WIDTH = info.current_w
HEIGHT = info.current_h

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.FULLSCREEN
)

pygame.display.set_caption("Calculator")

clock = pygame.time.Clock()


# =========================================================
# BASE SCREEN / SCALING
# =========================================================

BASE_W = 360
BASE_H = 640

SCALE_X = WIDTH / BASE_W
SCALE_Y = HEIGHT / BASE_H
SCALE = min(SCALE_X, SCALE_Y)


def sx(x):
    return int(x * SCALE_X)


def sy(y):
    return int(y * SCALE_Y)


def sw(w):
    return int(w * SCALE_X)


def sh(h):
    return int(h * SCALE_Y)


# =========================================================
# FONTS
# =========================================================

button_font = pygame.font.Font(
    None,
    max(20, int(34 * SCALE))
)

display_font = pygame.font.Font(
    None,
    max(30, int(48 * SCALE))
)

lyrics_font = pygame.font.Font(
    None,
    max(20, int(25 * SCALE))
)

small_font = pygame.font.Font(
    None,
    max(16, int(20 * SCALE))
)


# =========================================================
# COLORS
# =========================================================

BG = (18, 18, 20)

BUTTON = (42, 42, 46)
BUTTON_HOVER = (60, 60, 65)

OPERATOR = (255, 145, 45)
EQUALS = (60, 170, 100)
CLEAR = (190, 65, 65)

WHITE = (245, 245, 245)
GRAY = (150, 150, 155)


# =========================================================
# MUSIC
# =========================================================

MUSIC_FILE = "equals.mp3"

music_loaded = False

if mixer_available and os.path.exists(MUSIC_FILE):

    try:
        pygame.mixer.music.load(MUSIC_FILE)
        music_loaded = True
    except:
        music_loaded = False


# =========================================================
# LYRICS
# =========================================================

lyrics = []

if os.path.exists("lyrics.txt"):

    try:

        with open(
            "lyrics.txt",
            "r",
            encoding="utf-8"
        ) as file:

            lyrics = [
                line.strip()
                for line in file.readlines()
                if line.strip()
            ]

    except:

        lyrics = []


# =========================================================
# LYRIC TIMES
# =========================================================

LYRIC_TIMES = [
    4.0,
    6.0,
    8.0,
    12.0,
    14.0,
    16.0,
    18.0,
    21.0,
    24.0,
    26.0,
    28.0,
    32.0,
    37.0,
    40.0,
    56.0,
    60.0,
    64.0,
    68.0,
    72.0,
    76.0,
    80.0,
    84.0,
    88.0,
    92.0,
    96.0,
    100.0,
    104.0,
    108.0,
    112.0,
    116.0,
    120.0,
    124.0,
    128.0,
    132.0,
    136.0,
    140.0,
    144.0,
    148.0,
    152.0,
    156.0,
    160.0,
    164.0,
    168.0,
    172.0,
    176.0,
    180.0,
    184.0,
    188.0,
    192.0,
    196.0,
    200.0,
    204.0,
    208.0,
    212.0,
    216.0,
    220.0,
    224.0,
    228.0,
    232.0,
    236.0,
    240.0
]


# =========================================================
# MUSIC STATE
# =========================================================

music_playing = False
current_lyric = ""
lyrics_finished = False

calculator_locked = False


# =========================================================
# CALCULATOR STATE
# =========================================================

current = "0"
previous = None
operator = None
waiting_for_number = False


# =========================================================
# CALCULATOR FUNCTIONS
# =========================================================

def calculate(a, b, op):

    try:

        if op == "+":
            return a + b

        elif op == "−":
            return a - b

        elif op == "×":
            return a * b

        elif op == "÷":

            if b == 0:
                return "Error"

            return a / b

    except:

        return "Error"

    return "Error"


def format_number(value):

    if isinstance(value, str):
        return value

    try:

        if math.isinf(value) or math.isnan(value):
            return "Error"

        if value == int(value):
            return str(int(value))

        return str(round(value, 10))

    except:

        return "Error"


# =========================================================
# START MUSIC
# =========================================================

def start_music():

    global music_playing
    global current_lyric
    global lyrics_finished
    global calculator_locked

    if not music_loaded:
        return

    try:

        pygame.mixer.music.stop()
        pygame.mixer.music.play()

        music_playing = True
        current_lyric = ""
        lyrics_finished = False

        # Lock calculator
        calculator_locked = True

    except:

        music_playing = False
        calculator_locked = False


# =========================================================
# STOP MUSIC
# =========================================================

def stop_music():

    global music_playing
    global current_lyric
    global calculator_locked

    if mixer_available:

        try:
            pygame.mixer.music.stop()
        except:
            pass

    music_playing = False
    current_lyric = ""

    calculator_locked = False


# =========================================================
# UPDATE LYRICS
# =========================================================

def update_lyrics():

    global current_lyric
    global music_playing
    global lyrics_finished
    global calculator_locked

    if not music_playing:
        return

    try:

        position = pygame.mixer.music.get_pos()

    except:

        return

    # Music stopped
    if position < 0:

        music_playing = False
        current_lyric = ""
        lyrics_finished = True
        calculator_locked = False

        return

    seconds = position / 1000.0

    current_lyric = ""

    # Find current lyric
    for i in range(len(LYRIC_TIMES)):

        if i >= len(lyrics):
            break

        start_time = LYRIC_TIMES[i]

        if i + 1 < len(LYRIC_TIMES):

            end_time = LYRIC_TIMES[i + 1]

        else:

            end_time = 999999

        if start_time <= seconds < end_time:

            current_lyric = lyrics[i]

            break

    # Unlock after music ends
    if not pygame.mixer.music.get_busy():

        music_playing = False
        current_lyric = ""
        lyrics_finished = True

        calculator_locked = False


# =========================================================
# BUTTON PRESS
# =========================================================

def press_button(value):

    global current
    global previous
    global operator
    global waiting_for_number

    # Do nothing while music is playing
    if calculator_locked:
        return

    # =====================================================
    # NUMBERS
    # =====================================================

    if value.isdigit():

        if current == "Error":

            current = value
            previous = None
            operator = None
            waiting_for_number = False

            return

        if waiting_for_number:

            current = value
            waiting_for_number = False

            return

        if current == "0":

            current = value

        else:

            current += value

        return

    # =====================================================
    # DECIMAL
    # =====================================================

    if value == ".":

        if current == "Error":

            current = "0."
            previous = None
            operator = None
            waiting_for_number = False

            return

        if waiting_for_number:

            current = "0."
            waiting_for_number = False

        elif "." not in current:

            current += "."

        return

    # =====================================================
    # CLEAR
    # =====================================================

    if value == "AC":

        current = "0"
        previous = None
        operator = None
        waiting_for_number = False

        return

    # =====================================================
    # BACKSPACE
    # =====================================================

    if value == "⌫":

        if current == "Error":

            current = "0"

            return

        if waiting_for_number:
            return

        if len(current) > 1:

            current = current[:-1]

        else:

            current = "0"

        return

    # =====================================================
    # PERCENT
    # =====================================================

    if value == "%":

        if current == "Error":
            return

        try:

            number = float(current)

            if previous is not None and operator in ["+", "−"]:

                number = previous * number / 100

            else:

                number = number / 100

            current = format_number(number)

        except:

            current = "Error"

        return

    # =====================================================
    # OPERATORS
    # =====================================================

    if value in ["+", "−", "×", "÷"]:

        if current == "Error":
            return

        try:

            current_number = float(current)

        except:

            current = "Error"
            return

        if previous is not None and operator is not None:

            if not waiting_for_number:

                result = calculate(
                    previous,
                    current_number,
                    operator
                )

                if result == "Error":

                    current = "Error"
                    previous = None
                    operator = None
                    waiting_for_number = False

                    return

                current = format_number(result)

                current_number = float(result)

            previous = current_number

        else:

            previous = current_number

        operator = value
        waiting_for_number = True

        return

    # =====================================================
    # EQUALS
    # =====================================================

    if value == "=":

        # If there is no calculation,
        # "=" starts the music
        if previous is None or operator is None:

            start_music()

            return

        try:

            if waiting_for_number:

                second_number = previous

            else:

                second_number = float(current)

            result = calculate(
                previous,
                second_number,
                operator
            )

            current = format_number(result)

        except:

            current = "Error"

        previous = None
        operator = None
        waiting_for_number = True

        return


# =========================================================
# BUTTON LAYOUT
# =========================================================

button_data = [

    ("AC", 10, 300, 78, 58),
    ("⌫", 94, 300, 78, 58),
    ("%", 178, 300, 78, 58),
    ("÷", 262, 300, 88, 58),

    ("7", 10, 366, 78, 58),
    ("8", 94, 366, 78, 58),
    ("9", 178, 366, 78, 58),
    ("×", 262, 366, 88, 58),

    ("4", 10, 432, 78, 58),
    ("5", 94, 432, 78, 58),
    ("6", 178, 432, 78, 58),
    ("−", 262, 432, 88, 58),

    ("1", 10, 498, 78, 58),
    ("2", 94, 498, 78, 58),
    ("3", 178, 498, 78, 58),
    ("+", 262, 498, 88, 58),

    ("0", 10, 564, 162, 58),
    (".", 178, 564, 78, 58),
    ("=", 262, 564, 88, 58)
]


# =========================================================
# DRAW BUTTON
# =========================================================

def draw_button(rect, text, color):

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=sw(14)
    )

    pygame.draw.rect(
        screen,
        (70, 70, 75),
        rect,
        width=max(1, sw(1)),
        border_radius=sw(14)
    )

    text_surface = button_font.render(
        text,
        True,
        WHITE
    )

    text_rect = text_surface.get_rect(
        center=rect.center
    )

    screen.blit(
        text_surface,
        text_rect
    )


# =========================================================
# DRAW CALCULATOR NUMBER
# =========================================================

def draw_display():

    # IMPORTANT:
    # Completely hide the calculator number
    # while lyrics/music are playing.

    if calculator_locked:
        return

    display_text = current

    font = display_font

    if len(display_text) > 10:

        font = pygame.font.Font(
            None,
            max(24, int(38 * SCALE))
        )

    if len(display_text) > 16:

        font = pygame.font.Font(
            None,
            max(20, int(30 * SCALE))
        )

    text_surface = font.render(
        display_text,
        True,
        WHITE
    )

    text_rect = text_surface.get_rect(
        right=sx(345),
        centery=sy(245)
    )

    screen.blit(
        text_surface,
        text_rect
    )


# =========================================================
# DRAW LYRICS
# =========================================================

def draw_lyrics():

    if not current_lyric:
        return

    if len(current_lyric) > 32:

        lyric_font = small_font

    else:

        lyric_font = lyrics_font

    words = current_lyric.split()

    lines = []
    line = ""

    max_width = sw(320)

    # Wrap lyrics if too long
    for word in words:

        test = line + " " + word

        if lyric_font.size(test)[0] <= max_width:

            line = test.strip()

        else:

            if line:
                lines.append(line)

            line = word

    if line:
        lines.append(line)

    # =====================================================
    # LYRICS ARE NOW IN THE DISPLAY AREA
    # =====================================================

    start_y = sy(220)

    for i, line in enumerate(lines):

        text_surface = lyric_font.render(
            line,
            True,
            WHITE
        )

        text_rect = text_surface.get_rect(
            center=(
                WIDTH // 2,
                start_y + sy(i * 32)
            )
        )

        screen.blit(
            text_surface,
            text_rect
        )


# =========================================================
# MUSIC MESSAGE
# =========================================================

def draw_lock_message():

    if not calculator_locked:
        return

    text_surface = small_font.render(
        "♫  MUSIC PLAYING  ♫",
        True,
        GRAY
    )

    text_rect = text_surface.get_rect(
        center=(
            WIDTH // 2,
            sy(275)
        )
    )

    screen.blit(
        text_surface,
        text_rect
    )


# =========================================================
# MAIN LOOP
# =========================================================

running = True

while running:

    mouse_pos = pygame.mouse.get_pos()

    # Update lyrics/music
    update_lyrics()

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        # =================================================
        # QUIT
        # =================================================

        if event.type == pygame.QUIT:

            running = False

        # =================================================
        # TOUCH / MOUSE
        # =================================================

        elif event.type == pygame.MOUSEBUTTONDOWN:

            # Ignore calculator touches during music
            if calculator_locked:
                continue

            x, y = event.pos

            for button in button_data:

                text, bx, by, bw, bh = button

                rect = pygame.Rect(
                    sx(bx),
                    sy(by),
                    sw(bw),
                    sh(bh)
                )

                if rect.collidepoint(x, y):

                    press_button(text)

                    break

        # =================================================
        # KEYBOARD
        # =================================================

        elif event.type == pygame.KEYDOWN:

            # ESC exits
            if event.key == pygame.K_ESCAPE:

                running = False

            # Calculator keyboard
            elif not calculator_locked:

                if event.key == pygame.K_0:
                    press_button("0")

                elif event.key == pygame.K_1:
                    press_button("1")

                elif event.key == pygame.K_2:
                    press_button("2")

                elif event.key == pygame.K_3:
                    press_button("3")

                elif event.key == pygame.K_4:
                    press_button("4")

                elif event.key == pygame.K_5:
                    press_button("5")

                elif event.key == pygame.K_6:
                    press_button("6")

                elif event.key == pygame.K_7:
                    press_button("7")

                elif event.key == pygame.K_8:
                    press_button("8")

                elif event.key == pygame.K_9:
                    press_button("9")

                elif event.key == pygame.K_PERIOD:
                    press_button(".")

                elif event.key == pygame.K_PLUS:
                    press_button("+")

                elif event.key == pygame.K_MINUS:
                    press_button("−")

                elif event.key == pygame.K_RETURN:
                    press_button("=")

                elif event.key == pygame.K_BACKSPACE:
                    press_button("⌫")

    # =====================================================
    # DRAW EVERYTHING
    # =====================================================

    screen.fill(BG)

    # Lyrics first
    draw_lyrics()

    # Calculator number
    # Automatically disappears during music
    draw_display()

    # Music status
    draw_lock_message()

    # =====================================================
    # DRAW BUTTONS
    # =====================================================

    for button in button_data:

        text, bx, by, bw, bh = button

        rect = pygame.Rect(
            sx(bx),
            sy(by),
            sw(bw),
            sh(bh)
        )

        color = BUTTON

        # Operators
        if text in ["÷", "×", "−", "+"]:

            color = OPERATOR

        # Equals
        elif text == "=":

            color = EQUALS

        # AC
        elif text == "AC":

            color = CLEAR

        # Hover
        elif (
            not calculator_locked
            and rect.collidepoint(mouse_pos)
        ):

            color = BUTTON_HOVER

        # Darken while locked
        if calculator_locked:

            color = (
                max(15, color[0] - 15),
                max(15, color[1] - 15),
                max(15, color[2] - 15)
            )

        draw_button(
            rect,
            text,
            color
        )

    # =====================================================
    # UPDATE SCREEN
    # =====================================================

    pygame.display.flip()

    clock.tick(60)


# =========================================================
# CLEAN EXIT
# =========================================================

try:

    if mixer_available:
        pygame.mixer.music.stop()

except:

    pass


pygame.quit()
sys.exit()
