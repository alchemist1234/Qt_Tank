from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QPixmap, QKeyEvent, QBrush, QFont, QPen
from PySide2.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsRectItem, QGraphicsPixmapItem

from src.config import GameConfig
from src.base import Direction, TankType, TerrainType, generate_random_map
from src.item import TankItem, EnemyItem, TerrainItem

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
        self.selected = None
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

    def next_stage(self):
        self.stage += 1
        self.stage_text_item.setPlainText(self._stage_text % self.stage)

    def reset_stage(self):
        self.stage = 0
        self.stage_text_item.setPlainText(self._stage_text % self.stage)

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
            self.main_window.start_game(self.selected)

    def animation_hold(self):
        self.removeItem(self.stage_text_item)
        self.animation_timer_3.start()
        self.main_window.enter_game_scene()

    def start_animation(self, selected: int):
        self.animation_timer_1.start()
        self.selected = selected


class StartScene(QGraphicsScene):
    def __init__(self, mask_scene, stage=1):
        super().__init__()
        self.mask_scene = mask_scene
        self.y_list = [300, 400]
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

        png = QPixmap()
        png.load('../images/%s' % TankType.PLAYER_ONE.pic)
        png = png.scaled(25, 25)
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
                self.mask_scene.start_animation(self.selected)


class GameScene(QGraphicsScene):
    def __init__(self, stage=1):
        super().__init__()
        self.stage = stage
        self.started = False
        self.tank1 = TankItem(TankType.PLAYER_ONE, Direction.UP)
        self.tank2 = TankItem(TankType.PLAYER_TWO, Direction.UP)
        self.enemies = []
        self.terrain_map = generate_random_map(columns, rows)
        self.draw_terrain(self.terrain_map)
        brush = QBrush()
        brush.setColor(Qt.black)
        brush.setStyle(Qt.SolidPattern)
        self.setBackgroundBrush(brush)

    def start(self, players):
        self.started = True
        self.add_tank1(self.tank1)
        if players > 1:
            self.add_tank2(self.tank2)
        self.add_enemy(EnemyItem(TankType.ENEMY_1), 0)
        self.add_enemy(EnemyItem(TankType.ENEMY_2), 6)
        self.add_enemy(EnemyItem(TankType.ENEMY_3), 12)

    def add_tank1(self, tank: TankItem):
        self.tank1 = tank
        self.tank1.setX(4 * cube_size)
        self.tank1.setY(content_height - cube_size)
        self.addItem(tank)

    def add_tank2(self, tank: TankItem):
        self.tank2 = tank
        self.tank2.setX(8 * cube_size)
        self.tank2.setY(content_height - cube_size)
        self.addItem(tank)

    def add_enemy(self, enemy: EnemyItem, x_cell=0):
        enemy.setX(x_cell * cube_size)
        enemy.setY(0)
        self.enemies.append(enemy)
        self.addItem(enemy)

    def draw_terrain(self, terrain_list: list):
        size = int(cube_size / 2)
        for r, line in enumerate(terrain_list):
            for c, cell in enumerate(line):
                png = QPixmap()
                if cell.terrain == TerrainType.BRINK:
                    png.load('../images/brink.png')
                elif cell.terrain == TerrainType.STEEL:
                    png.load('../images/steel.png')
                elif cell.terrain == TerrainType.GRASS:
                    png.load('../images/grass.png')
                elif cell.terrain == TerrainType.WATER:
                    png.load('../images/water.png')
                else:
                    continue
                png = png.scaled(size, size)
                for index, state in enumerate(cell.state):
                    x = c * cube_size + index % 2 * size
                    y = r * cube_size + index // 2 * size
                    if state:
                        item = TerrainItem(png, cell.terrain)
                        if cell.terrain == TerrainType.GRASS:
                            item.setZValue(10)
                        item.setX(x)
                        item.setY(y)
                        self.addItem(item)

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
                if event.key() == Qt.Key_W:
                    self.tank1.directions.remove(Direction.UP)
                elif event.key() == Qt.Key_S:
                    self.tank1.directions.remove(Direction.DOWN)
                elif event.key() == Qt.Key_A:
                    self.tank1.directions.remove(Direction.LEFT)
                elif event.key() == Qt.Key_D:
                    self.tank1.directions.remove(Direction.RIGHT)
            if self.tank2 is not None:
                if event.key() == Qt.Key_Up:
                    self.tank2.directions.remove(Direction.UP)
                elif event.key() == Qt.Key_Down:
                    self.tank2.directions.remove(Direction.DOWN)
                elif event.key() == Qt.Key_Left:
                    self.tank2.directions.remove(Direction.LEFT)
                elif event.key() == Qt.Key_Right:
                    self.tank2.directions.remove(Direction.RIGHT)
