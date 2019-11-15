from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGraphicsPixmapItem
import random

from .base import Direction, Tank, TerrainType, TankType, Data, FoodType
from .config import GameConfig

cube_size = GameConfig.cube_size
interval = GameConfig.interval
content_width = GameConfig.width()
content_height = GameConfig.height()
data = Data()


class TerrainItem(QGraphicsPixmapItem):
    def __init__(self, png: QPixmap, terrain: TerrainType):
        super().__init__(png)
        self.terrain = terrain


class HomeItem(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()
        png = QPixmap('../images/home.png').scaled(cube_size, cube_size)
        self.setPixmap(png)
        self.setX(cube_size * GameConfig.home_area()[1])
        self.setY(cube_size * GameConfig.home_area()[0])


class TankItem(QGraphicsPixmapItem):
    def __init__(self, tank, direction: Direction):
        png = QPixmap('../images/%s' % tank.pic).scaled(cube_size, cube_size)
        QGraphicsPixmapItem.__init__(self, png)
        self.directions = []
        self.direction = direction
        self.tank = Tank(tank)
        self.setTransformOriginPoint(cube_size / 2, cube_size / 2)
        self.move_timer = QTimer()
        self.move_timer.setInterval(interval)
        self.move_timer.timeout.connect(self.move)
        self.move_timer.start()

    def move(self):
        x, y = self.x(), self.y()
        if len(self.directions) != 0:
            d = self.directions[-1]
            if self.direction != d:
                self.check_turn(self.direction, d)
                x, y = self.x(), self.y()
                self.direction = d
            if d == Direction.UP:
                self.setRotation(0)
                self.moveBy(0, -self.tank.speed)
            elif d == Direction.DOWN:
                self.setRotation(180)
                self.moveBy(0, self.tank.speed)
            elif d == Direction.LEFT:
                self.setRotation(270)
                self.moveBy(-self.tank.speed, 0)
            else:
                self.setRotation(90)
                self.moveBy(self.tank.speed, 0)
            self.check_edge()
        else:
            self.check_pos()
        self.check_collide(x, y)

    def check_edge(self):
        if self.x() < 0:
            self.setX(0)
        if self.x() > content_width - cube_size:
            self.setX(content_width - cube_size)
        if self.y() < 0:
            self.setY(0)
        if self.y() > content_height - cube_size:
            self.setY(content_height - cube_size)

    def check_pos(self):
        if self.direction == Direction.UP or self.direction == Direction.DOWN:
            if self.y() % (cube_size / 2) != 0:
                speed = self.tank.speed if self.direction == Direction.DOWN else -self.tank.speed
                self.moveBy(0, speed)
        if self.direction == Direction.LEFT or self.direction == Direction.RIGHT:
            if self.x() % (cube_size / 2) != 0:
                speed = self.tank.speed if self.direction == Direction.RIGHT else -self.tank.speed
                self.moveBy(speed, 0)

    def check_turn(self, before_turn: Direction, after_turn: Direction):
        before_in_x = before_turn in [Direction.LEFT, Direction.RIGHT]
        after_in_x = after_turn in [Direction.LEFT, Direction.RIGHT]
        if after_in_x != before_in_x:
            if before_in_x:
                pos = self.x() % (cube_size / 2)
                if pos != 0:
                    if pos > cube_size / 4:
                        self.moveBy(cube_size / 2 - pos, 0)
                    else:
                        self.moveBy(-pos, 0)
            else:
                pos = self.y() % (cube_size / 2)
                if pos != 0:
                    if pos > cube_size / 4:
                        self.moveBy(0, cube_size / 2 - pos)
                    else:
                        self.moveBy(0, -pos)

    def check_collide(self, x, y):
        colliding_items = self.collidingItems(mode=Qt.IntersectsItemBoundingRect)
        back = False
        for item in colliding_items:
            if isinstance(item, TankItem):
                back = True
                break
            elif isinstance(item, TerrainItem):
                if not item.terrain.tank_passable:
                    back = True
                    if isinstance(self, EnemyItem):
                        self.directions = [random.choice(
                            list({Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT} - set(self.directions)))]
                    break
            elif isinstance(item, FoodItem) and not isinstance(self, EnemyItem):
                item.scene().foods.remove(item)
                item.scene().removeItem(item)
                self.get_food(item)
        if back:
            self.setX(x)
            self.setY(y)

    def shoot(self):
        if self.tank.ammo_storage > 0:
            self.tank.ammo_storage -= 1
            if self.scene() is not None:
                ammo_png = QPixmap('../images/ammo.png').scaled(5, 8)
                ammo = AmmoItem(ammo_png, self, self.direction)
                self.scene().addItem(ammo)

    def destroy(self):
        self.scene().destroy_tank(self)

    def get_food(self, food_item):
        pass

    def __str__(self):
        return self.tank.name


class EnemyItem(TankItem):
    def __init__(self, png):
        super().__init__(png, Direction.DOWN)
        self.setRotation(180)
        self.auto_timer = QTimer()
        self.auto_timer.setInterval(500)
        self.auto_timer.timeout.connect(self.auto)
        self.auto_timer.start()

    def auto(self):
        change_score = random.randint(0, 99)
        if change_score < 40 or len(self.directions) == 0:
            directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
            if self.x() < cube_size:
                directions.remove(Direction.LEFT)
            if self.x() > content_width - cube_size:
                directions.remove(Direction.RIGHT)
            if self.y() < cube_size:
                directions.remove(Direction.UP)
            if self.y() > content_height - cube_size:
                directions.remove(Direction.DOWN)
            self.directions = [random.choice(directions)]
        shoot_score = random.randint(0, 99)
        if shoot_score < GameConfig.enemy_shoot_weight * 100:
            self.shoot()


class AmmoItem(QGraphicsPixmapItem):
    def __init__(self, png, tank_item: TankItem, direction: Direction):
        QGraphicsPixmapItem.__init__(self, png)

        self.tank_item = tank_item
        self.tank = tank_item.tank
        self.direction = direction
        self.available = True

        if self.direction == Direction.UP:
            self.setX(self.tank_item.x() + cube_size / 2 - 3)
            self.setY(self.tank_item.y())
        elif self.direction == Direction.DOWN:
            self.setX(self.tank_item.x() + cube_size / 2 + 3)
            self.setY(self.tank_item.y() + cube_size)
            self.setRotation(180)
        elif self.direction == Direction.LEFT:
            self.setX(self.tank_item.x())
            self.setY(self.tank_item.y() + cube_size / 2 + 3)
            self.setRotation(270)
        elif self.direction == Direction.RIGHT:
            self.setX(self.tank_item.x() + cube_size)
            self.setY(self.tank_item.y() + cube_size / 2 - 3)
            self.setRotation(90)

        self.timer = QTimer()
        self.timer.setInterval(interval)
        self.timer.timeout.connect(self.move)
        self.timer.start()

    def move(self):
        if self.available:
            if self.direction == Direction.UP:
                self.moveBy(0, -self.tank.ammo_speed)
            elif self.direction == Direction.DOWN:
                self.moveBy(0, self.tank.ammo_speed)
            elif self.direction == Direction.LEFT:
                self.moveBy(-self.tank.ammo_speed, 0)
            elif self.direction == Direction.RIGHT:
                self.moveBy(self.tank.ammo_speed, 0)
            self.check_edge()
            self.check_collide()

    def check_edge(self):
        if self.x() < 0 or self.x() > content_width or self.y() < 0 or self.y() > content_height:
            self.destroy()

    def check_collide(self):
        colliding_items = self.collidingItems(mode=Qt.IntersectsItemBoundingRect)
        if len(colliding_items) > 0:
            self.hit(colliding_items)
            pass

    def hit(self, items):
        destroy = False
        for item in items:
            if isinstance(item, TerrainItem):
                if item.terrain.destroyable and self.tank.power >= item.terrain.strength:
                    item.scene().removeItem(item)
                if not item.terrain.ammo_passable:
                    destroy = True
            if isinstance(item, TankItem):
                if self.tank == item.tank:
                    continue
                if self.tank.is_player != item.tank.is_player:
                    if self.tank.is_player:
                        self.score(item.tank)
                    item.destroy()
                destroy = True
            if isinstance(item, AmmoItem):
                destroy = True
                item.destroy()
        if destroy:
            self.destroy()

    def score(self, enemy: Tank):
        if self.tank.type == TankType.PLAYER_ONE:
            if enemy.type in data.player_1_kills:
                data.player_1_kills[enemy.type] += 1
            else:
                data.player_1_kills[enemy.type] = 1
        elif self.tank.type == TankType.PLAYER_TWO:
            if enemy.type in data.player_2_kills:
                data.player_2_kills[enemy.type] += 1
            else:
                data.player_2_kills[enemy.type] = 1

    def destroy(self):
        self.available = False
        self.tank.ammo_storage += 1
        if self.scene() is not None:
            self.scene().removeItem(self)


class FoodItem(QGraphicsPixmapItem):
    def __init__(self, food_type: FoodType = None):
        QGraphicsPixmapItem.__init__(self)
        self.food_type = FoodItem.random_food_type() if food_type is None else food_type
        self.draw(self.food_type)
        x = random.randint(0, content_width - cube_size)
        y = random.randint(0, content_height - cube_size)
        self.setX(x)
        self.setY(y)
        self.setZValue(20)

    def draw(self, food_type):
        png_path = '../images/%s'
        if food_type == FoodType.Boom:
            png_path = png_path % 'food_boom.png'
        elif food_type == FoodType.CLOCK:
            png_path = png_path % 'food_clock.png'
        elif food_type == FoodType.IRON:
            png_path = png_path % 'food_iron.png'
        elif food_type == FoodType.GUN:
            png_path = png_path % 'food_gun.png'
        elif food_type == FoodType.PROTECT:
            png_path = png_path % 'food_protect.png'
        elif food_type == FoodType.STAR:
            png_path = png_path % 'food_star.png'
        elif food_type == FoodType.TANK:
            png_path = png_path % 'food_tank.png'
        png = QPixmap(png_path).scaled(cube_size, cube_size)
        self.setPixmap(png)

    @staticmethod
    def random_food_type():
        return random.choice(list(FoodType.__members__.values()))
