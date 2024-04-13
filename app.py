from PyQt6.QtWidgets import QMainWindow, QApplication, QProgressBar, QColorDialog
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtGui import QMovie, QIcon, QPixmap
from PIL import Image, ImageColor, ImageQt

from image_utils import generate_gif
import classic_gen, stripe_gen
from gui import Ui_MainWindow

from enum import Enum
import sys


class StaticTypes(Enum):
    CLASSIC = 1,
    STRIPED = 2

class GeneratorWorker(QObject):
    """
        A worker thread class. This class is used to offload the task of
        generating the GIF from the main thread (GUI thread).
    """
    # initializing signals
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, width: int, height: int, square_size: int, colors, blur: int, type: StaticTypes):
        super().__init__()
        self.width = width
        self.height = height
        self.square_size = square_size
        self.colors = colors
        self.type = type
        self.blur = blur

    def run(self):
        if self.type == StaticTypes.CLASSIC:
            generate_gif(self.width,
                         self.height,
                         self.square_size,
                         self.colors,
                         self.blur,
                         self.update_progress,
                         classic_gen.generate_classic_static)

        elif self.type == StaticTypes.STRIPED:
            generate_gif(self.width,
                         self.height,
                         self.square_size,
                         self.colors,
                         self.blur,
                         self.update_progress,
                         stripe_gen.generate_striped_static)

        self.finished.emit()

    def update_progress(self, percent):
        self.progress.emit(percent)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.initUI()


    def initUI(self):
        """Initializes the GUI"""
        self.setupUi(self)

        self.remove_color_btn.setDisabled(True)
        self.mov_static = None
        self.set_max_square_size()

        # set the icons for the default colors in the combo box
        for i in range(self.color_combo_box.count()):
            color = self.color_combo_box.itemText(i)
            img = Image.new("RGBA", (16, 16), ImageColor.getcolor(color, "RGB"))
            icon = QIcon(QPixmap.fromImage(ImageQt.ImageQt(img)))
            self.color_combo_box.setItemIcon(i, icon)

        # create and add the progressbar to the statusbar
        self.progressbar = QProgressBar()
        self.progressbar.setMaximumWidth(600)
        self.progressbar.setRange(0, 100)
        self.statusbar.addPermanentWidget(self.progressbar)

        # connecting signals to slots
        self.actionExit.triggered.connect(lambda: self.close())
        self.width_textbox.valueChanged.connect(self.set_max_square_size)
        self.height_textbox.valueChanged.connect(self.set_max_square_size)
        self.generator_btn.clicked.connect(self.generate_static)
        self.add_color_btn.clicked.connect(self.pick_color)
        self.remove_color_btn.clicked.connect(self.remove_color)


    def generate_static(self) -> None:
        """Generates the static GIF image"""
        self.generator_btn.setDisabled(True)
        self.progressbar.setValue(0)

        # get the type of static we want to generate from the radio buttons
        if self.classic_type_radio_btn.isChecked():
            static_type = StaticTypes.CLASSIC
        elif  self.strip_type_radio_btn.isChecked():
            static_type = StaticTypes.STRIPED

        # get the width, height, the square size and the blur from the QLineEdit widgets
        input_w = int(self.width_textbox.text())
        input_h = int(self.height_textbox.text())
        input_square_size = int(self.square_size_textbox.text())
        input_blur = int(self.blur_textbox.text())

        # get the colors from the combo box
        colors = []
        for i in range(self.color_combo_box.count()):
            colors.append(self.color_combo_box.itemText(i))

        # creating the worker and moving it to the thread
        self.thread = QThread()
        self.worker = GeneratorWorker(input_w, input_h, input_square_size, colors, input_blur, static_type)
        self.worker.moveToThread(self.thread)

        # Connecting signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(lambda: self.set_static("static.gif"))
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_progressbar)

        self.thread.start()


    def set_static(self, file_name) -> None:
        """Sets and displays the generated GIF on the screen"""
        self.mov_static = QMovie(file_name)
        self.static_holder_lbl.setMovie(self.mov_static)

        self.mov_static.start()
        self.generator_btn.setEnabled(True)


    def update_progressbar(self, progress) -> None:
        """Updates the progressbar"""
        self.progressbar.setValue(progress)


    def set_max_square_size(self) -> None:
        """Sets the maximum allowed size of the square based on the input dimensions"""
        width = self.width_textbox.value()
        height = self.height_textbox.value()

        limit = (width if width < height else height) // 2
        self.square_size_textbox.setMaximum(limit)


    def pick_color(self) -> None:
        """Opens a color dialog and adds the chosen color to the combo box"""
        picked_color = QColorDialog.getColor().name().upper()

        # create an icon for the picked color and add it to the combo box with that color
        img = Image.new("RGBA", (16, 16), ImageColor.getcolor(picked_color, "RGB"))
        icon = QIcon(QPixmap.fromImage(ImageQt.ImageQt(img)))
        self.color_combo_box.addItem(icon, picked_color)

        # we are now allowed to remove items from the combo box
        self.remove_color_btn.setEnabled(True)


    def remove_color(self) -> None:
        """Removes the selected color from the combo box"""
        self.color_combo_box.removeItem(self.color_combo_box.currentIndex())

        color_count = self.color_combo_box.count()
        self.remove_color_btn.setDisabled(color_count == 2)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())