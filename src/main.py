import sys

from PySide2.QtCore import QRect
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsView, QWidget

from src.config import GameConfig
from src.base import GameType, Data
from src.scene import GameScene, StartScene, MaskScene, GameOverScene, ScoreScene

content_height = GameConfig.height()
content_width = GameConfig.width()


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.game_scene = None
        self.mask_scene = MaskScene(self)
        self.start_scene = StartScene(self)
        self.game_over_scene = GameOverScene(self)
        self.main_widget = QWidget()
        self.graph_view = QGraphicsView(self.main_widget)
        self.mask_view = QGraphicsView(self.main_widget)
        self.data = Data()
        self.init()

    def init(self):
        self.setWindowTitle('QTank')
        self.resize(content_width + 20, content_height + 20)

        self.graph_view.setGeometry(QRect(5, 5, content_width + 5, content_height + 5))
        self.graph_view.setScene(self.start_scene)

        self.mask_view.setSceneRect(0, 0, content_width, content_height)
        self.mask_view.setGeometry(QRect(5, 5, content_width + 5, content_height + 5))
        self.mask_view.setStyleSheet('background: transparent')
        self.mask_view.setScene(self.mask_scene)
        self.setCentralWidget(self.main_widget)

    def ready(self):
        self.data.stage = 1
        self.graph_view.setScene(self.start_scene)

    def set_game_type(self, game_type: GameType):
        self.data.game_type = game_type

    def start_stage_animation(self):
        self.mask_scene.start_animation()

    def switch_game_scene(self):
        if self.game_scene is not None:
            self.game_scene.destroy()
        self.game_scene = GameScene(self, self.data.game_type)
        self.game_scene.setSceneRect(0, 0, content_width, content_height)
        self.graph_view.setScene(self.game_scene)

    def start_stage(self):
        self.game_scene.start()

    def show_score(self):
        pass

    def game_over(self):
        if self.game_scene is not None:
            self.game_scene.destroy()
        self.graph_view.setScene(self.game_over_scene)
        self.game_over_scene.game_over()


if __name__ == '__main__':
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
