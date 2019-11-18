from PySide2.QtCore import Qt


class GameConfig(object):
    # Window parameter
    cube_size = 60
    rows = 10
    columns = 13  # columns should always be an odd

    # Refresh interval
    interval = 20

    # Terrain
    _blank_wight = 0.6
    _brick_weight = 0.2
    _steel_weight = 0.1
    _grass_weight = 0.05
    _water_weight = 0.05
    _blank_area = [(0, 0), (0, 6), (0, 12), (9, 4), (9, 8), (9, 6)]
    _steel_area = [(5, 6)]
    _home_area = (9, 6)
    _brick_area = [(9, 5), (9, 7), (8, 5), (8, 6), (8, 7)]

    # Game parameters
    # Enemy
    enemies = 10
    max_enemies_in_field = 5
    enemy_born_columns = [(13 - 1) / 2 * i for i in range(3)]

    _enemy_1_weight = 0.6
    _enemy_2_weight = 0.3
    _enemy_3_weight = 0.1

    enemy_shoot_weight = 0.02
    enemy_change_weight = 0.01

    # Player
    player_lives = 1

    player_1_control_up = Qt.Key_W
    player_1_control_down = Qt.Key_S
    player_1_control_left = Qt.Key_A
    player_1_control_right = Qt.Key_D
    player_1_control_shoot = Qt.Key_J

    player_2_control_up = Qt.Key_Up
    player_2_control_down = Qt.Key_Down
    player_2_control_left = Qt.Key_Left
    player_2_control_right = Qt.Key_Right
    player_2_control_shoot = Qt.Key_Slash

    @classmethod
    def width(cls):
        return cls.columns * cls.cube_size

    @classmethod
    def height(cls):
        return cls.rows * cls.cube_size

    @classmethod
    def terrain_weights(cls):
        return [cls._blank_wight, cls._brick_weight, cls._steel_weight, cls._grass_weight, cls._water_weight]

    @classmethod
    def blank_area(cls):
        return cls._blank_area

    @classmethod
    def brink_area(cls):
        return cls._brick_area

    @classmethod
    def steel_area(cls):
        return cls._steel_area

    @classmethod
    def home_area(cls):
        return cls._home_area

    @classmethod
    def enemy_weights(cls):
        return [cls._enemy_1_weight, cls._enemy_2_weight, cls._enemy_3_weight]
