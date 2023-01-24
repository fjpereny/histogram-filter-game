
import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QPushButton, QGridLayout, QLabel
from PyQt5.QtWidgets import QMessageBox, QDoubleSpinBox, QVBoxLayout
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import QSize
from localization import Ui_MainWindow
import random
import numpy as np

GAME_MODE = False

GRID_WIDTH = 5
GRID_HEIGHT = 1
N = GRID_WIDTH * GRID_HEIGHT

P = np.zeros((GRID_HEIGHT, GRID_WIDTH))
P += 1.0 / N

SENSOR_WRONG = 0.0
SENSOR_RIGHT = 1.0 - SENSOR_WRONG

MOVE_FAIL = 0.0
MOVE_SUCCESS = 1.0 - MOVE_FAIL

ROBOT_X = None
ROBOT_Y = None

ROBOT_ICON = None

N_COLORS = 2
COLORS ={   
            0: '#FF0000',
            1: '#0000FF',
            2: '#00FF00',
            3: '#FFFF00',
            4: '#00FFFF',
        }


def rand_start():
    x = random.randint(0, GRID_WIDTH - 1)
    y = random.randint(0, GRID_HEIGHT - 1)
    return (x, y)


def make_grid(parent, layout):
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            new_button = QPushButton()
            layout.addWidget(new_button, i, j)
            new_button.setParent(parent)
            new_button.setObjectName(f"Grid_{j}_{i}")
            new_button.setFixedSize(75, 75)
            new_button.clicked.connect(tile_click)
            rand_color = COLORS[random.randint(0, N_COLORS - 1)]
            set_button_colors(new_button, rand_color, "#00FF00")
            new_button.show()
    update_grid()


def set_button_colors(button, background, border):
        if background in ['#ffff00', '#00ff00', '#00ffff']:
            text_color = 'black'
        else:
            text_color = 'white'
        button.setStyleSheet(   f"background-color: {background};" +
                                f"color: {text_color};" +
                                f"border: 3px solid {border}"
                            )


def update_grid():
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            prob = P[i][j]
            prob_str = str(np.round(prob * 100, 2)) + '%'
            button = ui.centralwidget.findChild(QPushButton, f"Grid_{j}_{i}")
            button.setText(prob_str)

            max_p = np.max(P)
            perc_75 = np.percentile(P, 75)

            cur_color = button.palette().button().color().name().lower()
            border = "black"
            if prob >= perc_75 and prob >= 0.01:
                border = "orange"
            if prob == max_p:
                border = "#00FF00"
            set_button_colors(button, cur_color, border)

            if not GAME_MODE and i == ROBOT_Y and j == ROBOT_X:
                button.setIcon(ROBOT_ICON)
                button.setIconSize(QSize(35, 35))
            else:
                button.setIcon(QtGui.QIcon())
            


def set_robot():
    global ROBOT_X
    global ROBOT_Y
    # Randomly Setting Robot Location
    ROBOT_X, ROBOT_Y = rand_start()


def restart(widget, layout):
    while layout.count() > 0:
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

    make_grid(widget, layout)
    set_robot()
    global P
    P = np.zeros((GRID_HEIGHT, GRID_WIDTH))
    P += 1.0 / N
    update_grid()
    clear_sensor_color()

    global SENSOR_WRONG, SENSOR_RIGHT, MOVE_FAIL, MOVE_SUCCESS
    SENSOR_WRONG = 0.0
    SENSOR_RIGHT = 1.0 - SENSOR_WRONG
    sense_error_spin = ui.centralwidget.findChild(QDoubleSpinBox, "sense_error_spin")
    if sense_error_spin:
        sense_error_spin.setValue(0.0)
    MOVE_FAIL = 0.0
    MOVE_SUCCESS = 1.0 - MOVE_FAIL
    move_error_spin = ui.centralwidget.findChild(QDoubleSpinBox, "move_error_spin")
    if move_error_spin:
        move_error_spin.setValue(0.0)


def make_controls(parent, layout):

    # Separator
    sep = QtWidgets.QFrame(parent)
    sep.setFrameShape(QtWidgets.QFrame.HLine)
    if GRID_WIDTH > 9:
        layout.addWidget(sep, 0, 0, 1, 10)
    else:
        layout.addWidget(sep, 0, 0, 1, 10)
    sep.show()

    # Control Buttons
    up_button = QPushButton()
    layout.addWidget(up_button, 1, 2)
    up_button.setObjectName("up_button")
    up_button.setParent = parent
    up_button.setText("UP")
    up_button.show()
    up_seq = QKeySequence("Up")
    up_button.setShortcut(up_seq)
    up_button.clicked.connect(lambda: move(0, -1))

    down_button = QPushButton()
    layout.addWidget(down_button, 3, 2)
    down_button.setObjectName("down_button")
    down_button.setParent = parent
    down_button.setText("DOWN")
    down_button.show()
    down_seq = QKeySequence("Down")
    down_button.setShortcut(down_seq)
    down_button.clicked.connect(lambda: move(0, 1))

    left_button = QPushButton()
    layout.addWidget(left_button, 2, 1)
    left_button.setObjectName("left_button")
    left_button.setParent = parent
    left_button.setText("LEFT")
    left_button.show()
    left_seq = QKeySequence("Left")
    left_button.setShortcut(left_seq)
    left_button.clicked.connect(lambda: move(-1, 0))

    right_button = QPushButton()
    layout.addWidget(right_button, 2, 3)
    right_button.setObjectName("right_button")
    right_button.setParent = parent
    right_button.setText("RIGHT")
    right_button.show()
    right_seq = QKeySequence("Right")
    right_button.setShortcut(right_seq)
    right_button.clicked.connect(lambda: move(1, 0))

    # Sensor Display
    label = QLabel()
    layout.addWidget(label, 1, 5)
    label.setObjectName("sensor_label")
    label.setText("Sensor")
    label.setParent(parent)
    label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    label.show()

    sensor = QPushButton()
    layout.addWidget(sensor, 2, 5)
    sensor.setObjectName("sensor")
    sensor.setText("")
    sensor.setParent(parent)
    sensor.show()

    sense_button = QPushButton()
    layout.addWidget(sense_button, 3, 5)
    sense_button.setObjectName("sense_button")
    sense_button.setText("Sense")
    sense_button.setParent(parent)
    sense_button.show()
    sense_seq = QKeySequence("Space")
    sense_button.setShortcut(sense_seq)
    sense_button.clicked.connect(sense)

    sense_error_label = QLabel()
    layout.addWidget(sense_error_label, 1, 7)
    sense_error_label.setText("Sense Error")
    sense_error_label.setParent(parent)
    sense_error_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    sense_error_spin = QDoubleSpinBox()
    sense_error_spin.setParent(ui.centralwidget)
    sense_error_spin.setObjectName("sense_error_spin")
    layout.addWidget(sense_error_spin, 2, 7)
    sense_error_spin.setValue(0.0)
    sense_error_spin.setMinimum(0)
    sense_error_spin.setMaximum(1)
    sense_error_spin.setSingleStep(0.01)
    sense_error_spin.setParent(parent)
    sense_error_spin.valueChanged.connect(lambda: update_sensor_error(sense_error_spin.value()))

    move_fail_label = QLabel()
    layout.addWidget(move_fail_label, 1, 8)
    move_fail_label.setText("Move Error")
    move_fail_label.setParent(parent)
    move_fail_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    move_error_spin = QDoubleSpinBox()
    move_error_spin.setParent(ui.centralwidget)
    move_error_spin.setObjectName("move_error_spin")
    layout.addWidget(move_error_spin, 2, 8)
    move_error_spin.setValue(0.0)
    move_error_spin.setMinimum(0)
    move_error_spin.setMaximum(1)
    move_error_spin.setSingleStep(0.01)
    move_error_spin.setParent(parent)
    move_error_spin.valueChanged.connect(lambda: update_move_fail(move_error_spin.value()))

    game_button = QPushButton()
    game_button.setParent(ui.centralwidget)
    game_button.setObjectName("game_button")
    layout.addWidget(game_button, 3, 7)
    game_button.setText("Game")
    game_button.clicked.connect(start_game)

    learn_button = QPushButton()
    learn_button.setParent(ui.centralwidget)
    learn_button.setObjectName("learn_button")
    layout.addWidget(learn_button, 3, 8)
    learn_button.setText("Learn")
    learn_button.clicked.connect(start_learning)


def start_game():
    global GAME_MODE
    GAME_MODE = True
    restart(ui.centralwidget, grid_layout)


def start_learning():
    global GAME_MODE
    GAME_MODE = False
    restart(ui.centralwidget, grid_layout)


def sense():
    cur_loc = ui.centralwidget.findChild(QPushButton, f"Grid_{ROBOT_X}_{ROBOT_Y}")
    cur_color = cur_loc.palette().button().color().name()

    sensor = ui.centralwidget.findChild(QPushButton, "sensor")
    sensor.setStyleSheet(f"background-color: {cur_color}")

    global P
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            loc = ui.centralwidget.findChild(QPushButton, f"Grid_{col}_{row}")
            color = loc.palette().button().color().name()
            if color == cur_color:
                P[row][col] *= SENSOR_RIGHT
            else:
                P[row][col] *= SENSOR_WRONG
    normalize()
    update_grid()


def move(x, y):
    global P
    Q = np.zeros((GRID_HEIGHT, GRID_WIDTH))
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            Q[row][col] += P[(row-y)%GRID_HEIGHT][(col-x)%GRID_WIDTH] * MOVE_SUCCESS
            Q[(row-y)%GRID_HEIGHT][(col-x)%GRID_WIDTH] += P[(row-y)%GRID_HEIGHT][(col-x)%GRID_WIDTH] * MOVE_FAIL
    P = Q
    global ROBOT_X
    global ROBOT_Y
    ROBOT_X += x
    ROBOT_X %= GRID_WIDTH
    ROBOT_Y += y
    ROBOT_Y %= GRID_HEIGHT

    normalize()
    update_grid()
    clear_sensor_color()


def clear_sensor_color():
    sensor = ui.centralwidget.findChild(QPushButton, "sensor")
    if sensor:
        sensor.setStyleSheet("")


def normalized_matrix():
    s = np.sum(P)
    Q = P / s
    return Q


def normalize():
    global P
    P = normalized_matrix()
    update_grid()


def tile_click():

    # Tile color change
    if not GAME_MODE:
        return
    else:
        sender = ui.centralwidget.sender()
        _, x, y = sender.objectName().split('_')
        correct = (int(x) == int(ROBOT_X) and int(y) == int(ROBOT_Y))

        dialog = QMessageBox()
        if correct:
            dialog.setText("Correct! You Win!")
        else:
            dialog.setText("Incorrect! Try Again!")
        dialog.setWindowTitle("Guess")
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.buttonClicked.connect(dialog.close)
        dialog.exec()


def update_sensor_error(val):
    global SENSOR_WRONG
    global SENSOR_RIGHT
    SENSOR_WRONG = val
    SENSOR_RIGHT = 1.0 - SENSOR_WRONG


def update_move_fail(val):
    global MOVE_FAIL
    global MOVE_SUCCESS
    MOVE_FAIL = val
    MOVE_SUCCESS = 1.0 - MOVE_FAIL


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    ROBOT_ICON = QtGui.QIcon(CUR_DIR + '/Frank.jpeg')

    # Initializing World Grid
    v_layout = QVBoxLayout(ui.centralwidget)
    v_layout.setObjectName("v_layout")
    grid_layout = QGridLayout()
    grid_layout.setObjectName("grid_layout")
    control_grid = QGridLayout()
    control_grid.setObjectName("control_layout")
    v_layout.addLayout(grid_layout)
    v_layout.addLayout(control_grid)
    restart(ui.centralwidget, grid_layout)
    make_controls(ui.centralwidget, control_grid)

    # GUI Setup
    action_reset = ui.actionReset.triggered.connect(lambda: restart(ui.centralwidget, grid_layout))

    # Debug


    MainWindow.show()
    sys.exit(app.exec_())