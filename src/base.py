from enum import Enum
import random
from src.config import GameConfig


def generate_random_map(columns: int, rows: int):
    terrain_map = []
    terrains = list(TerrainType.__members__.values())
    weights = GameConfig.terrain_weights()
    for i in range(rows):
        terrain_type_line = random.choices(terrains, weights=weights, k=columns)
        terrain_line = [Terrain(t) for t in terrain_type_line]
        terrain_map.append(terrain_line)
    for (i, j) in GameConfig.blank_area():
        terrain_map[i][j] = Terrain(TerrainType.BLANK, [1, 1, 1, 1])
    for (i, j) in GameConfig.steel_area():
        terrain_map[i][j] = Terrain(TerrainType.STEEL, [1, 1, 1, 1])
    for (i, j) in GameConfig.brink_area():
        terrain_map[i][j] = Terrain(TerrainType.BRICK, [1, 1, 1, 1])
    return terrain_map


class Direction(Enum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3


class GameType(Enum):
    ONE_PLAYER = 1
    TWO_PLAYERS = 2


class TerrainType(Enum):
    BLANK = 1, True, True, False, 0
    BRICK = 2, False, False, True, 0
    STEEL = 3, False, False, True, 20
    GRASS = 4, True, True, False, 0
    WATER = 5, False, True, False, 0

    def __init__(self, index: int, tank_passable: bool, ammo_passable: bool, destroyable: bool, strength: int):
        self._index = index
        self._tank_passable = tank_passable
        self._ammo_passable = ammo_passable
        self._destroyable = destroyable
        self._strength = strength

    @property
    def index(self):
        return self._index

    @property
    def tank_passable(self):
        return self._tank_passable

    @property
    def ammo_passable(self):
        return self._ammo_passable

    @property
    def destroyable(self):
        return self._destroyable

    @property
    def strength(self):
        return self._strength


class TankType(Enum):
    PLAYER_ONE = 'Player 1', 3, 20, 10, 3, 3, 10, 0, True, 'player_tank_1.png'
    PLAYER_TWO = 'Player 2', 3, 20, 10, 3, 3, 10, 0, True, 'player_tank_2.png'
    ENEMY_1 = 'Enemy 1', 1, 10, 10, 3, 3, 10, 100, False, 'tank_1.png'
    ENEMY_2 = 'Enemy 2', 1, 10, 10, 3, 4, 15, 150, False, 'tank_2.png'
    ENEMY_3 = 'Enemy 3', 1, 30, 20, 3, 2, 7, 200, False, 'tank_3.png'

    def __init__(self, tank_name: str, lives: int, hit_point: int, power: int,
                 max_storage: int, speed: int, ammo_speed: int, score: int,
                 is_player: bool, pic: str):
        self._tank_name = tank_name
        self._lives = lives
        self._hit_point = hit_point
        self._power = power
        self._max_storage = max_storage
        self._speed = speed
        self._ammo_speed = ammo_speed
        self._score = score
        self._is_player = is_player
        self._pic = pic

    @property
    def tank_name(self):
        return self._tank_name

    @property
    def lives(self):
        return self._lives

    @property
    def hit_point(self):
        return self._hit_point

    @property
    def power(self):
        return self._power

    @property
    def max_storage(self):
        return self._max_storage

    @property
    def speed(self):
        return self._speed

    @property
    def ammo_speed(self):
        return self._ammo_speed

    @property
    def score(self):
        return self._score

    @property
    def is_player(self):
        return self._is_player

    @property
    def pic(self):
        return self._pic


class Tank(object):
    def __init__(self, tank):
        if isinstance(tank, Tank):
            self.type = tank.type
        elif isinstance(tank, TankType):
            self.type = tank
        self.name = tank.name
        self.lives = tank.lives
        self.hit_point = tank.hit_point
        self.power = tank.power
        self.max_storage = tank.max_storage
        self.speed = tank.speed
        self.ammo_speed = tank.ammo_speed
        self.score = tank.score
        self.is_player = tank.is_player
        self.pic = tank.pic
        self.ammo_storage = self.max_storage


class Terrain(object):
    def __init__(self, terrain: TerrainType, state=None):
        self.terrain = terrain
        if state is None and terrain != TerrainType.BLANK:
            self.state = []
            while sum(self.state) == 0:
                self.state = random.choices([0, 1], k=4)
        else:
            self.state = state


class FoodType(Enum):
    BOOM = 0,
    CLOCK = 1,
    GUN = 2,
    IRON = 3,
    PROTECT = 4,
    STAR = 5,
    TANK = 6,


class Data(object):
    _instance = None
    game_type = GameType.ONE_PLAYER
    stage = 1
    player_1_lives = GameConfig.player_lives
    player_2_lives = GameConfig.player_lives
    player_1_score = 0
    player_2_score = 0
    player_1_kills = {}
    player_2_kills = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @classmethod
    def reset(cls):
        cls.game_type = GameType.ONE_PLAYER
        cls.stage = 1
        cls.player_1_lives = GameConfig.player_lives
        cls.player_2_lives = GameConfig.player_lives
        cls.player_1_score = 0
        cls.player_2_score = 0
        cls.player_1_kills = {}
        cls.player_2_kills = {}
