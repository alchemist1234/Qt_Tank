from PySide2.QtCore import QTimer, Qt, QRect
from PySide2.QtGui import QPixmap, QKeyEvent, QBrush, QFont, QPen, QMovie, QTransform
from PySide2.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsRectItem, QGraphicsPixmapItem

from src.config import GameConfig
from src.base import Direction, GameType, TankType, TerrainType, generate_random_map, Terrain
from src.item import TankItem, EnemyItem, TerrainItem, HomeItem, FoodItem

import random

columns = GameConfig.columns
rows = GameConfig.rows
cube_size = GameConfig.cube_size
content_width = GameConfig.width()
content_height = GameConfig.height()
interval = GameConfig.interval


class MaskScene(QGraphicsScene):
    _stage_text = 'STAGE %s'

    def __init__(self, main_window, stage=1):
        super().__init__()
        self.main_window = main_window
        self.stage = stage
        self.upper_mask = QGraphicsRectItem(0, 0, content_width, 0)
        self.lower_mask = QGraphicsRectItem(0, content_height, content_width, 0)
        self.stage_text_item = QGraphicsTextItem()
        self.mask_height = 0
        self.animation_timer_1 = QTimer()
        self.animation_timer_2 = QTimer()
        self.animation_timer_3 = QTimer()
        self.init()

    def init(self):
        mask_brush = QBrush()
        mask_brush.setColor(Qt.gray)
        mask_brush.setStyle(Qt.SolidPattern)
        mask_pen = QPen()
        mask_pen.setColor(Qt.gray)
        self.upper_mask.setBrush(mask_brush)
        self.lower_mask.setBrush(mask_brush)
        self.upper_mask.setPen(mask_pen)
        self.lower_mask.setPen(mask_pen)
        self.addItem(self.upper_mask)
        self.addItem(self.lower_mask)

        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.stage_text_item.setPlainText(self._stage_text % self.stage)
        self.stage_text_item.setFont(font)
        self.stage_text_item.setDefaultTextColor(Qt.black)
        self.stage_text_item.setX(content_width / 2 - int(self.stage_text_item.boundingRect().width() / 2))
        self.stage_text_item.setY(content_height / 2 - int(self.stage_text_item.boundingRect().height() / 2))

        self.animation_timer_1.setInterval(interval)
        self.animation_timer_1.timeout.connect(self.animation_in)

        self.animation_timer_2.setSingleShot(True)
        self.animation_timer_2.timeout.connect(self.animation_hold)
        self.animation_timer_2.setInterval(800)

        self.animation_timer_3.setInterval(interval)
        self.animation_timer_3.timeout.connect(self.animation_out)

    def animation_in(self):
        self.mask_height += 10
        finished = False
        if self.mask_height > content_height / 2:
            self.mask_height = content_height / 2
            finished = True
        self.upper_mask.setRect(0, 0, content_width, self.mask_height)
        self.lower_mask.setRect(0, content_height - self.mask_height, content_width, self.mask_height)
        if finished:
            self.addItem(self.stage_text_item)
            self.animation_timer_1.stop()
            self.animation_timer_2.start()

    def animation_out(self):
        self.mask_height -= 10
        finished = False
        if self.mask_height < 0:
            self.mask_height = 0
            finished = True
        self.upper_mask.setRect(0, 0, content_width, self.mask_height)
        self.lower_mask.setRect(0, content_height - self.mask_height, content_width, self.mask_height)
        if finished:
            self.animation_timer_3.stop()
            self.main_window.start_stage()

    def animation_hold(self):
        self.removeItem(self.stage_text_item)
        self.animation_timer_3.start()
        self.main_window.switch_game_scene()

    def start_animation(self):
        self.stage = self.main_window.data.stage
        self.stage_text_item.setPlainText(self._stage_text % self.stage)
        self.animation_timer_1.start()


class StartScene(QGraphicsScene):
    def __init__(self, main_window, stage=1):
        super().__init__()
        self.main_window = main_window
        self.y_list = [300, 400]
        self.game_type_list = [GameType.ONE_PLAYER, GameType.TWO_PLAYERS]
        self.selected = 0
        self.stage = stage
        self.one_play_text_item = QGraphicsTextItem()
        self.two_plays_text_item = QGraphicsTextItem()
        self.indicator_item = None
        self.start = False

        self.init()

    def init(self):
        brush = QBrush()
        brush.setColor(Qt.black)
        brush.setStyle(Qt.SolidPattern)
        self.setBackgroundBrush(brush)

        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.one_play_text_item.setPlainText('One Player')
        self.two_plays_text_item.setPlainText('Two Players')
        self.one_play_text_item.setDefaultTextColor(Qt.white)
        self.two_plays_text_item.setDefaultTextColor(Qt.white)
        self.one_play_text_item.setFont(font)
        self.two_plays_text_item.setFont(font)
        self.one_play_text_item.setX(300)
        self.two_plays_text_item.setX(300)
        self.one_play_text_item.setY(self.y_list[0])
        self.two_plays_text_item.setY(self.y_list[1])
        self.addItem(self.one_play_text_item)
        self.addItem(self.two_plays_text_item)

        png = QPixmap('../images/%s' % TankType.PLAYER_1.pic).scaled(25, 25)
        self.indicator_item = QGraphicsPixmapItem(png)
        self.indicator_item.setRotation(90)
        self.indicator_item.setX(260)
        self.indicator_item.setY(self.y_list[self.selected] + 8)
        self.addItem(self.indicator_item)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Up:
            self.selected -= 1
            if self.selected < 0:
                self.selected = len(self.y_list) - 1
        if event.key() == Qt.Key_Down:
            self.selected += 1
            if self.selected >= len(self.y_list):
                self.selected = 0
        self.indicator_item.setY(self.y_list[self.selected] + 8)

        if event.key() == Qt.Key_Space:
            if not self.start:
                self.start = True
                self.main_window.set_game_type(self.game_type_list[self.selected])
                self.main_window.start_stage_animation()


class GameScene(QGraphicsScene):
    def __init__(self, main_window, game_type: GameType):
        super().__init__()
        self.main_window = main_window
        self.game_type = game_type
        self.started = False
        self.tank1 = TankItem(TankType.PLAYER_1, Direction.UP)
        self.tank2 = TankItem(TankType.PLAYER_2, Direction.UP) if game_type == GameType.TWO_PLAYERS else None
        self.home = HomeItem()
        self.addItem(self.home)
        self.enemies = []
        self.booms = []
        self.appears = []
        self.appear_tanks = {}
        self.foods = []
        self.remain_enemies = GameConfig.enemies
        self.enemy_born_rects = [QRect(cube_size * i, 0, cube_size, cube_size) for i in GameConfig.enemy_born_columns]
        self.enemy_frozen = False
        self.terrain_map = generate_random_map(columns, rows)
        self.draw_terrain(self.terrain_map)
        brush = QBrush()
        brush.setColor(Qt.black)
        brush.setStyle(Qt.SolidPattern)
        self.setBackgroundBrush(brush)
        self.enemy_born_timer = QTimer()
        self.enemy_born_timer.setInterval(3000)
        self.enemy_born_timer.timeout.connect(self.add_enemy)
        self.boom_timer = QTimer()
        self.boom_timer.setInterval(100)
        self.boom_timer.timeout.connect(self.boom_animation)
        self.appear_timer = QTimer()
        self.appear_timer.setInterval(200)
        self.appear_timer.timeout.connect(self.appear_animation)
        self.terrain_animation_timer = QTimer()
        self.terrain_animation_timer.setInterval(250)
        self.terrain_animation_timer.timeout.connect(self.terrain_animation)
        self.food_timer = QTimer()
        self.food_timer.setInterval(GameConfig.food_appear_interval)
        self.food_timer.timeout.connect(self.generate_food)
        self.enemy_freeze_timer = QTimer()
        self.enemy_freeze_timer.setInterval(GameConfig.enemy_freeze_time)
        self.enemy_freeze_timer.timeout.connect(self.enemy_unfreeze)
        self.protect_home_timer = QTimer()
        self.protect_home_timer.setInterval(GameConfig.protect_home_time)
        self.protect_home_timer.timeout.connect(self.protect_home_timeout)
        self.game_over_timer = QTimer()
        self.game_over_timer.setInterval(20)
        self.game_over_timer.timeout.connect(self.game_over_animation)
        self.game_over_text_item = None

    def start(self):
        self.started = True
        self.remain_enemies = GameConfig.enemies
        self.add_tank1(self.tank1)
        if self.tank2 is not None:
            self.add_tank2(self.tank2)
        self.enemy_born_timer.start()
        self.boom_timer.start()
        self.appear_timer.start()
        self.terrain_animation_timer.start()
        self.food_timer.start()

    def add_tank1(self, tank: TankItem):
        self.tank1 = tank
        self.tank1.setX(4 * cube_size)
        self.tank1.setY(content_height - cube_size)
        appear_id = self.add_appear(4 * cube_size, content_height - cube_size)
        self.appear_tanks[appear_id] = self.tank1

    def add_tank2(self, tank: TankItem):
        self.tank2 = tank
        self.tank2.setX(8 * cube_size)
        self.tank2.setY(content_height - cube_size)
        appear_id = self.add_appear(8 * cube_size, content_height - cube_size)
        self.appear_tanks[appear_id] = self.tank2

    def add_enemy(self):
        if self.remain_enemies > 0 and len(self.enemies) < GameConfig.max_enemies_in_field:
            enemy_type = random.choices([TankType.ENEMY_1, TankType.ENEMY_2, TankType.ENEMY_3],
                                        weights=GameConfig.enemy_weights(), k=1)[0]
            enemy = EnemyItem(enemy_type)
            available_rect = []
            for rect in self.enemy_born_rects:
                has_tank = False
                for e in self.enemies:
                    if rect.contains(int(e.x()), int(e.y())):
                        has_tank = True
                        break
                if self.tank1 is not None:
                    if rect.contains(int(self.tank1.x()), int(self.tank1.y())):
                        has_tank = True
                if self.tank2 is not None:
                    if rect.contains(int(self.tank2.x()), int(self.tank2.y())):
                        has_tank = True
                if not has_tank:
                    available_rect.append(rect)
            if len(available_rect) > 0:
                born_rect = random.choice(available_rect)
                x = born_rect.x()
                self.remain_enemies -= 1
                enemy.setX(x)
                enemy.setY(0)
                enemy.frozen = self.enemy_frozen
                appear_id = self.add_appear(x, 0)
                self.appear_tanks[appear_id] = enemy

    def destroy_tank(self, tank_item: TankItem):
        self.add_boom(tank_item)
        self.removeItem(tank_item)
        if isinstance(tank_item, EnemyItem):
            self.enemies.remove(tank_item)
            if self.remain_enemies == 0 and len(self.enemies) == 0:
                self.next_stage()
        elif tank_item == self.tank1:
            self.tank1 = None
            if self.main_window.data.player_1_lives > 0:
                self.main_window.data.player_1_lives -= 1
                self.add_tank1(TankItem(TankType.PLAYER_1, Direction.UP))
        elif tank_item == self.tank2:
            self.tank2 = None
            if self.main_window.data.player_2_lives > 0:
                self.main_window.data.player_2_lives -= 1
                self.add_tank2(TankItem(TankType.PLAYER_2, Direction.UP))

        if (self.tank1 is None and self.main_window.data.player_1_lives == 0
                and ((self.main_window.data.game_type == GameType.TWO_PLAYERS
                      and self.tank2 is None
                      and self.main_window.data.player_2_lives == 0)
                     or self.main_window.data.game_type == GameType.ONE_PLAYER)):
            self.game_over()

    def boom_animation(self):
        for boom in self.booms[::-1]:
            pic_no = boom.data(0)
            if pic_no >= 5:
                self.removeItem(boom)
                self.booms.remove(boom)
            else:
                pic_no += 1
                boom.setData(0, pic_no)
                png = QPixmap('../images/boom_dynamic.png').copy(96 * pic_no, 0, 96, 96).scaled(cube_size, cube_size)
                boom.setPixmap(png)

    def add_appear(self, x, y):
        png = QPixmap('../images/appear.png').copy(0, 0, 48, 48).scaled(cube_size, cube_size)
        appear = QGraphicsPixmapItem(png)
        appear.setData(0, 0)
        appear.setData(1, 0)
        appear.setX(x)
        appear.setY(y)
        self.appears.append(appear)
        self.addItem(appear)
        return id(appear)

    def appear_animation(self):
        for appear in self.appears:
            pic_no = appear.data(0)
            cycle = appear.data(1)
            if pic_no >= 2 and cycle >= 3:
                self.removeItem(appear)
                self.appears.remove(appear)
                tank = self.appear_tanks.pop(id(appear))
                self.addItem(tank)
                tank.start_move()
                if isinstance(tank, EnemyItem):
                    self.enemies.append(tank)
                elif isinstance(tank, TankItem):
                    tank.protect(GameConfig.born_protect_time)
            else:
                if pic_no >= 2:
                    pic_no = 0
                    cycle += 1
                else:
                    pic_no += 1
                appear.setData(0, pic_no)
                appear.setData(1, cycle)
                png = QPixmap('../images/appear.png').copy(48 * pic_no, 0, 48, 48).scaled(cube_size, cube_size)
                appear.setPixmap(png)

    def add_boom(self, item):
        boom_png = QPixmap('../images/boom_dynamic.png').copy(0, 0, 96, 96).scaled(cube_size, cube_size)
        boom_item = QGraphicsPixmapItem(boom_png)
        boom_item.setX(item.x())
        boom_item.setY(item.y())
        boom_item.setData(0, 0)
        self.addItem(boom_item)
        self.booms.append(boom_item)

    def enemy_freeze(self):
        self.enemy_frozen = True
        for e in self.enemies:
            e.frozen = True
        self.enemy_freeze_timer.start()

    def enemy_unfreeze(self):
        self.enemy_frozen = False
        for e in self.enemies:
            e.frozen = False
        self.enemy_freeze_timer.stop()

    def next_stage(self):
        self.main_window.data.stage += 1
        self.main_window.start_stage_animation()

    def game_over(self):
        if self.tank1 is not None:
            self.tank1.move_timer.stop()
        if self.tank2 is not None:
            self.tank2.move_timer.stop()
        self.game_over_text_item = QGraphicsTextItem('GAME OVER')
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.game_over_text_item.setFont(font)
        self.game_over_text_item.setDefaultTextColor(Qt.white)
        self.game_over_text_item.setX((content_width - self.game_over_text_item.boundingRect().width()) // 2)
        self.game_over_text_item.setY(content_height)
        self.addItem(self.game_over_text_item)
        self.game_over_timer.start()

    def game_over_animation(self):
        speed = -2
        end_y = (content_height - self.game_over_text_item.boundingRect().height()) // 2
        if self.game_over_text_item.y() + speed > end_y:
            self.game_over_text_item.moveBy(0, speed)
        else:
            self.game_over_text_item.setY(end_y)
            self.game_over_timer.stop()
            self.main_window.game_over()

    def destroy(self):
        if self.tank1 is not None:
            self.tank1.move_timer.stop()
            self.tank1.protect_timer.stop()
            self.tank1.protect_animation_timer.stop()
            self.removeItem(self.tank1)
        if self.tank2 is not None:
            self.tank2.move_timer.stop()
            self.tank2.protect_timer.stop()
            self.tank2.protect_animation_timer.stop()
            self.removeItem(self.tank2)
        for e in self.enemies:
            self.removeItem(e)
        self.enemy_born_timer.stop()
        self.boom_timer.stop()
        self.terrain_animation_timer.stop()
        self.food_timer.stop()

    def draw_terrain(self, terrain_list: list):
        size = int(cube_size / 2)
        for r, line in enumerate(terrain_list):
            for c, cell in enumerate(line):
                if cell.terrain == TerrainType.BLANK:
                    continue
                for index, state in enumerate(cell.state):
                    x = c * cube_size + index % 2 * size
                    y = r * cube_size + index // 2 * size
                    if state:
                        item = TerrainItem(cell.terrain)
                        item.setX(x)
                        item.setY(y)
                        self.addItem(item)

    def terrain_animation(self):
        size = int(cube_size / 2)
        for item in self.items():
            if isinstance(item, TerrainItem) and item.terrain == TerrainType.WATER:
                if item.data(0) == 0:
                    png = QPixmap('../images/water1.png').scaled(size, size)
                    item.setData(0, 1)
                else:
                    png = QPixmap('../images/water.png').scaled(size, size)
                    item.setData(0, 0)
                item.setPixmap(png)

    def generate_food(self):
        food = FoodItem()
        self.foods.append(food)
        self.addItem(food)

    def protect_home(self):
        self.protect_home_timer.start()
        self._remove_home_guard()
        self._fill_home_guard(TerrainType.STEEL)

    def protect_home_timeout(self):
        self.protect_home_timer.stop()
        self._remove_home_guard()
        self._fill_home_guard(TerrainType.BRICK)

    def _remove_home_guard(self):
        for (row, col) in GameConfig.home_guard_area():
            item = self.itemAt(col * cube_size, row * cube_size, QTransform())
            if item is not None:
                self.removeItem(item)

    def _fill_home_guard(self, terrain_type: TerrainType):
        for (row, col) in GameConfig.home_guard_area():
            item_left_top = TerrainItem(terrain_type)
            item_left_bottom = TerrainItem(terrain_type)
            item_right_top = TerrainItem(terrain_type)
            item_right_bottom = TerrainItem(terrain_type)
            item_left_top.setX(col * cube_size)
            item_left_top.setY(row * cube_size)
            item_left_bottom.setX(col * cube_size)
            item_left_bottom.setY(row * cube_size + cube_size // 2)
            item_right_top.setX(col * cube_size + cube_size // 2)
            item_right_top.setY(row * cube_size)
            item_right_bottom.setX(col * cube_size + cube_size // 2)
            item_right_bottom.setY(row * cube_size + cube_size // 2)
            self.addItem(item_left_top)
            self.addItem(item_left_bottom)
            self.addItem(item_right_top)
            self.addItem(item_right_bottom)

    def keyPressEvent(self, event: QKeyEvent):
        if self.started:
            if self.tank1 is not None:
                if event.key() == Qt.Key_W:
                    self.tank1.directions.append(Direction.UP)
                elif event.key() == Qt.Key_S:
                    self.tank1.directions.append(Direction.DOWN)
                elif event.key() == Qt.Key_A:
                    self.tank1.directions.append(Direction.LEFT)
                elif event.key() == Qt.Key_D:
                    self.tank1.directions.append(Direction.RIGHT)
                elif event.key() == Qt.Key_J:
                    self.tank1.shoot()

            if self.tank2 is not None:
                if event.key() == Qt.Key_Up:
                    self.tank2.directions.append(Direction.UP)
                elif event.key() == Qt.Key_Down:
                    self.tank2.directions.append(Direction.DOWN)
                elif event.key() == Qt.Key_Left:
                    self.tank2.directions.append(Direction.LEFT)
                elif event.key() == Qt.Key_Right:
                    self.tank2.directions.append(Direction.RIGHT)
                elif event.key() == Qt.Key_Slash:
                    self.tank2.shoot()

    def keyReleaseEvent(self, event: QKeyEvent):
        if self.started:
            if self.tank1 is not None:
                if event.key() == Qt.Key_W and Direction.UP in self.tank1.directions:
                    self.tank1.directions.remove(Direction.UP)
                elif event.key() == Qt.Key_S and Direction.DOWN in self.tank1.directions:
                    self.tank1.directions.remove(Direction.DOWN)
                elif event.key() == Qt.Key_A and Direction.LEFT in self.tank1.directions:
                    self.tank1.directions.remove(Direction.LEFT)
                elif event.key() == Qt.Key_D and Direction.RIGHT in self.tank1.directions:
                    self.tank1.directions.remove(Direction.RIGHT)
            if self.tank2 is not None:
                if event.key() == Qt.Key_Up and Direction.UP in self.tank2.directions:
                    self.tank2.directions.remove(Direction.UP)
                elif event.key() == Qt.Key_Down and Direction.DOWN in self.tank2.directions:
                    self.tank2.directions.remove(Direction.DOWN)
                elif event.key() == Qt.Key_Left and Direction.LEFT in self.tank2.directions:
                    self.tank2.directions.remove(Direction.LEFT)
                elif event.key() == Qt.Key_Right and Direction.RIGHT in self.tank2.directions:
                    self.tank2.directions.remove(Direction.RIGHT)


class ScoreScene(QGraphicsScene):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window


class GameOverScene(QGraphicsScene):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.text = QGraphicsTextItem('GAME  OVER')
        self.timer = QTimer()
        self.init()

    def init(self):
        brush = QBrush()
        brush.setColor(Qt.black)
        brush.setStyle(Qt.SolidPattern)
        self.setBackgroundBrush(brush)
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.text.setFont(font)
        self.text.setDefaultTextColor(Qt.white)
        self.text.setX(content_width - self.text.boundingRect().width() / 2)
        self.text.setY(content_height - self.text.boundingRect().height() / 2)
        self.addItem(self.text)
        self.timer.setSingleShot(True)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.time_over)

    def game_over(self):
        self.timer.start()

    def time_over(self):
        self.main_window.ready()
