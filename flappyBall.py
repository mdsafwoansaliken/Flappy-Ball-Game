from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

#screen variables
W_Width, W_Height = 800, 600
FPS = 60
#Ball variables
Ball_Size = 20
ball_x = W_Width // 4
ball_y = (W_Height - Ball_Size) // 2
gravity = 0.5
jump_force = 8
ball_velocity = 0
flappy_ball = None
#obstacle variables
bar_w = 50
bar_distance = 200
bar_speed = 1
bars = []

#Gameplay variables
game_over = False
game_aclr = 0.2
score = 0
high_score = 0
life_bars = []
isPaused = False
reset = False
finish = False

def draw_points(x, y):
    glPointSize(2) 
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def find_zone(x0, y0, x1, y1):
    zone = 0
    dx = x1 - x0
    dy = y1 - y0

    if dx > dy:
        if dx >= 0 and dy > 0:
            zone = zone
        elif dx <= 0 and dy > 0:
            zone = 3
        elif dx <= 0 and dy < 0:
            zone = 4
        else:
            zone = 7
    else:
        if dx >= 0 and dy > 0:
            zone = 1
        elif dx <= 0 and dy > 0:
            zone = 2
        elif dx <= 0 and dy < 0:
            zone = 5
        else:
            zone = 6
    return zone

def convert(x, y, currentZone, convertingZone):
    nx = 0
    ny = 0
    if currentZone == 0:
        if convertingZone == 0:
            nx, ny = x, y
        elif convertingZone == 1:
            nx, ny = y, x
        elif convertingZone == 2:
            nx, ny = -y, x
        elif convertingZone == 3:
            nx, ny = -x, y
        elif convertingZone == 4:
            nx, ny = -x, -y
        elif convertingZone == 5:
            nx, ny = -y, -x
        elif convertingZone == 6:
            nx, ny = y, -x
        elif convertingZone == 7:
            nx, ny = x, -y
    else:
        if currentZone == 1:
            nx, ny = y, x
        elif currentZone == 2:
            nx, ny = y, -x
        elif currentZone == 3:
            nx, ny = -x, y
        elif currentZone == 4:
            nx, ny = -x, -y
        elif currentZone == 5:
            nx, ny = -y, -x
        elif currentZone == 6:
            nx, ny = -y, x
        elif currentZone == 7:
            nx, ny = x, -y
    return nx, ny

def draw_line(x0, y0, x1, y1, color=(0.0, 1.0, 0.0)):
    glColor3f(*color)
    zone = find_zone(x0, y0, x1, y1)
    a = convert(x0, y0, zone, 0)
    b = convert(x1, y1, zone, 0)
    nx0, ny0 = a[0], a[1]
    nx1, ny1 = b[0], b[1]
    dx = nx1 - nx0
    dy = ny1 - ny0
    d = (2 * dy) - dx
    de = 2 * dy
    dne = 2 * (dy - dx)

    x = nx0
    y = ny0
    while x < nx1:
        if d <= 0:
            x += 1
            d += de
        else:
            x += 1
            y += 1
            d += dne
        c = convert(x, y, 0, zone)
        x3, y3 = c[0], c[1]
        draw_points(x3, y3)

class Bar:
    def __init__(self, barX, barHeight, distance, barWidth=bar_w, wHeight=W_Height, counted = False, clash = True):
        self.barX = barX
        self.barHeight = barHeight
        self.distance = distance
        self.barWidth = barWidth
        self.wHeight = wHeight
        self.c = counted
        self.cla = clash

    def draw(self):
        draw_line(self.barX, 0, self.barX + self.barWidth, 0)
        draw_line(self.barX, 0, self.barX, self.barHeight)
        draw_line(self.barX + self.barWidth, 0, self.barX + self.barWidth, self.barHeight)
        draw_line(self.barX, self.barHeight, self.barX + self.barWidth, self.barHeight)

        draw_line(self.barX, self.barHeight + self.distance, self.barX + self.barWidth, self.barHeight + self.distance)
        draw_line(self.barX, self.barHeight + self.distance, self.barX, self.wHeight)
        draw_line(self.barX + self.barWidth, self.barHeight + self.distance, self.barX + self.barWidth, self.wHeight)
        draw_line(self.barX, self.wHeight, self.barX + self.barWidth, self.wHeight)

class Ball:
    def __init__(self, cX, cY, radius, life = 3):
        self.cX = cX
        self.cY = cY
        self.r = radius
        self.tempR = radius
        self.life = life

    def draw(self):
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_POINTS)

        num_iterations = int(self.r / 1)

        for _ in range(num_iterations):
            for point in self.midpoint_circle():
                glVertex2f(point[0], point[1])
            self.tempR -= 1

        glEnd()
        self.tempR = self.r

    def midpoint_circle(self):
        x = 0
        y = int(self.tempR)
        d = 1 - self.tempR
        points = []

        while y > x:
            if d < 0:
                x += 1
                d += 2 * x + 1
            else:
                y -= 1
                x += 1
                d += 2 * (x - y) + 1

            points.append((self.cX + x, self.cY + y))
            points.append((self.cX + y, self.cY + x))
            points.append((self.cX - x, self.cY + y))
            points.append((self.cX - y, self.cY + x))
            points.append((self.cX + x, self.cY - y))
            points.append((self.cX + y, self.cY - x))
            points.append((self.cX - x, self.cY - y))
            points.append((self.cX - y, self.cY - x))

        return points

    def update(self):
        global ball_velocity, game_over, bars, bar_speed, score, game_aclr, high_score

        if not game_over:
            ball_velocity -= gravity
            self.cY += ball_velocity

            # score and speed system
            for bar in bars:
                if (
                    bar.barX + bar.barWidth - 1 <= self.cX - self.r
                    and bar.c is False and bar.cla is True
                ):
                    score += 1
                    bar_speed += game_aclr
                    bar.c = True 
                    print(f"Score: {score}")

            # collision detection
            for bar in bars:
                if (
                    self.cX + self.r >= bar.barX
                    and self.cX  - self.r <= bar.barX + bar.barWidth
                    and (self.cY - self.r <= bar.barHeight or self.cY + self.r >= bar.barHeight+ bar.distance)
                    and bar.cla is True

                ):
                    if self.life > 1:
                        self.life -= 1
                        bar.cla = False
                    else:
                        self.life -= 1
                        game_over = True
                        if score > high_score:
                            high_score = score
                        print("Game Over")
                        print(f"Score: {score}, High Score: {high_score}")

            if not self.is_within_bounds(W_Width, W_Height):
                game_over = True
                if score > high_score:
                    high_score = score
                print("Game Over")
                print(f"Score: {score}, High Score: {high_score}")

    def jump(self):
        global ball_velocity
        ball_velocity = jump_force

    def is_within_bounds(self, w_width, w_height):
        return (
            0 < self.cX - self.r < w_width
            and 0 < self.cY - self.r < w_height
            and 0 < self.cX + self.r < w_width
            and 0 < self.cY + self.r < w_height
        )

        
def move_bars():
    global bars, game_over
    if not game_over:
        for bar in bars:
            bar.barX -= bar_speed
            if bar.barX + bar.barWidth < 0:
                bar.barX = W_Width
                bar.barHeight = random.uniform(100, W_Height - 100)
                bar.distance = random.uniform(200, 250)
                bar.c = False
                bar.cla = True

def reset_game():
    global bars, flappy_ball, game_over, score, bar_speed, reset, isPaused

    game_over = False
    score = 0
    bar_speed = 0.5
    isPaused = False
    flappy_ball.cY = (W_Height - Ball_Size) // 2
    flappy_ball.tempR = Ball_Size
    flappy_ball.life = 3

    bars = []
    for i in range(3):
        barX = 250 + i * 300
        barHeight = random.uniform(100, W_Height - 100)
        new_bar = Bar(barX, barHeight, bar_distance)
        bars.append(new_bar)

def leftBtn():
    col = (0, 1, 1)
    draw_line(20, 560, 50, 580, col)
    draw_line(20, 560, 80, 560, col)
    draw_line(20, 560, 50, 540, col)

def middleBtn1():
    col = (1, 1, 0)
    draw_line(390, 540, 390, 590, col)
    draw_line(410, 540, 410, 590, col)

def middleBtn2():
    col = (1, 1, 0)
    draw_line(390, 540, 390, 590, col)
    draw_line(390, 540, 410, 570, col)
    draw_line(390, 590, 410, 570, col)

def rightBtn():
    col = (1, 0, 0)
    draw_line(720, 550, 770, 580, col)
    draw_line(720, 580, 770, 550, col)

def midBtn():
    global isPaused
    if isPaused is False:
        return middleBtn1()
    else:
        return middleBtn2()



def mouse_over(x, y):
    if 390 <= x <= 410 and 540 <= y <= 590:
        return "middle"
    elif 20 <= x <= 80 and 560 <= y <= 580:
        return "left"
    elif 720 <= x <= 770 and 550 <= y <= 580:
        return "right"

def mouseListener(button, state, x, y):
    global isPaused, midBtn, game_over, reset, finish
    y = glutGet(GLUT_WINDOW_HEIGHT) - y
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and mouse_over(x, y) == "middle" and game_over is False:
        if isPaused:
            midBtn = middleBtn1
            isPaused = False
        else:
            midBtn = middleBtn2
            isPaused = True
        print(isPaused)
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and mouse_over(x, y) == "left":
        reset = True
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and mouse_over(x, y) == "right":
        finish = True
    
    glutPostRedisplay()

def keyboardListener(key, x, y):
    global isPaused, game_over, reset, finish
    if key == b' ':
        flappy_ball.jump()
    if key == b"v":
        reset = True
    if key == b"b" and game_over is False:
        if isPaused:
            isPaused = False
        else:
            isPaused = True
    if key == b"n":
        finish = True

lifeBar1 = Ball(235, 560, 7)
life_bars.append(lifeBar1)
lifeBar2 = Ball(215, 560, 7)
life_bars.append(lifeBar2)
lifeBar3 = Ball(255, 560, 7)
life_bars.append(lifeBar3)


def text():
    col = (1, 0, 0)
    #G
    draw_line(40, 200, 40, 400, col)
    draw_line(40, 400, 100, 400, col)
    draw_line(40, 200, 70, 200, col)
    draw_line(70, 200, 70, 300, col)
    draw_line(70, 300, 100, 300, col)
    draw_line(100, 200, 100, 300, col)
    draw_line(100, 350, 100, 400, col)

    #A
    draw_line(120, 200, 120, 400, col)
    draw_line(180, 200, 180, 400, col)
    draw_line(120, 300, 180, 300, col)
    draw_line(120, 400, 180, 400, col)

    #M
    draw_line(200, 200, 200, 400, col)
    draw_line(200, 400, 220, 400, col)
    draw_line(230, 300, 220, 400, col)
    draw_line(230, 300, 240, 400, col)
    draw_line(240, 400, 260, 400, col)
    draw_line(260, 200, 260, 400, col)

    #E
    draw_line(280, 200, 280, 400, col)
    draw_line(280, 200, 340, 200, col)
    draw_line(280, 300, 340, 300, col)
    draw_line(280, 400, 340, 400, col)

    #O
    draw_line(440, 200, 440, 400, col)
    draw_line(440, 200, 500, 200, col)
    draw_line(440, 400, 500, 400, col)
    draw_line(500, 200, 500, 400, col)

    #v
    draw_line(540, 200, 520, 400, col)
    draw_line(540, 200, 560, 200, col)
    draw_line(560, 200, 580, 400, col)

    #E
    draw_line(600, 200, 600, 400, col)
    draw_line(600, 200, 660, 200, col)
    draw_line(600, 300, 660, 300, col)
    draw_line(600, 400, 660, 400, col)

    #R
    draw_line(680, 200, 680, 400, col)
    draw_line(680, 400, 740, 400, col)
    draw_line(680, 300, 740, 300, col)
    draw_line(740, 300, 740, 400, col)
    draw_line(740, 200, 680, 300, col)

def draw_char(x, y, char):
    glColor3f(1.0, 0.0, 0.0)
    glPointSize(2)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def draw_text(x, y, text):
    glColor3f(1.0, 0.0, 0.0)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))


def display_final_score(final_score):
    x = W_Width // 2 - 60
    y = W_Height // 2 - 150
    score_str = "Final Score: {}".format(final_score)
    draw_text(x, y, score_str)

def display_score(score):
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(W_Width - 200, W_Height - 40)
    score_str = "Score: {}".format(score)
    for char in score_str:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def display_high_score(high_score):
    x = W_Width // 2 - 60
    y = W_Height // 2 - 180
    score_str = "High Score: {}".format(high_score)
    draw_text(x, y, score_str)

def update(_):
    global ball_x, ball_y, Ball_Size, flappy_ball, isPaused, reset 
    if reset:
        reset_game()
        reset = False
    else:
        if isPaused is False:
            flappy_ball.update()
            move_bars()
    glutPostRedisplay()
    glutTimerFunc(int(1000 / FPS), update, 0)


def display():
    global game_over, score, life_bars, high_score
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    if not game_over:
        flappy_ball.draw()
        for bar in bars:
            bar.draw()
        midBtn()
        for n in range(flappy_ball.life):
            life_bars[n].draw()
        display_score(score)
    
    if game_over:
        text()
        display_high_score(high_score)
        display_final_score(score)

    leftBtn()
    rightBtn()


    glutSwapBuffers()
    if game_over:
        glutIdleFunc(None)
    if finish is True:
        print(f"Goodbye! Last Score: {score}, High Score: {high_score}")
        glutLeaveMainLoop()

def init():
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W_Width, 0, W_Height)


def main():
    global bars, flappy_ball
    glutInit()
    glutInitWindowSize(W_Width, W_Height)
    glutInitWindowPosition(0, 0)
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)

    wind = glutCreateWindow(b"Flappy Ball Game")
    init()

    flappy_ball = Ball(ball_x, ball_y, Ball_Size)
    for i in range(3):
        barX = 250 + i * 300
        barHeight = random.uniform(100, W_Height - 100)
        new_bar = Bar(barX, barHeight, bar_distance)
        bars.append(new_bar)
    
    
    glutDisplayFunc(display)
    glutIdleFunc(lambda: glutPostRedisplay())
    glutKeyboardFunc(keyboardListener)
    glutMouseFunc(mouseListener)
    glutTimerFunc(16, update, 0)
    glutMainLoop()


if __name__ == "__main__":
    main()
