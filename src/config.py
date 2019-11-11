class GameConfig(object):
    cube_size = 60
    rows = 10
    # columns should always be an odd
    columns = 13
    interval = 20

    _blank_wight = 0.6
    _brink_weight = 0.2
    _steel_weight = 0.1
    _grass_weight = 0.05
    _water_weight = 0.05
    _blank_area = [(0, 0), (0, 6), (0, 12), (9, 4), (9, 8), (9, 6)]
    _steel_area = [(5, 6)]
    _brink_area = [(9, 5), (9, 7), (8, 5), (8, 6), (8, 7)]

    enemies = 20
    player_lives = 3
    enemy_born_columns = [(columns - 1) / 2 * i for i in range(3)]

    _enemy_1_weight = 0.6
    _enemy_2_weight = 0.3
    _enemy_3_weight = 0.1

    @classmethod
    def width(cls):
        return cls.columns * cls.cube_size

    @classmethod
    def height(cls):
        return cls.rows * cls.cube_size

    @classmethod
    def terrain_weights(cls):
        return [cls._blank_wight, cls._brink_weight, cls._steel_weight, cls._grass_weight, cls._water_weight]

    @classmethod
    def blank_area(cls):
        return cls._blank_area

    @classmethod
    def brink_area(cls):
        return cls._brink_area

    @classmethod
    def steel_area(cls):
        return cls._steel_area

    @classmethod
    def enemy_weights(cls):
        return [cls._enemy_1_weight, cls._enemy_2_weight, cls._enemy_3_weight]
