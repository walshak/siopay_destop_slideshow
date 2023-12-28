import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QListWidget,
    QDialog,
    QDialogButtonBox,
    QAction,
    QToolBar,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sqlite3
from PIL import Image

class ImageDatabase:
    def __init__(self):
        self.conn = sqlite3.connect("images.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def insert_image(self, path):
        self.cursor.execute("INSERT INTO images (path) VALUES (?)", (path,))
        self.conn.commit()

    def get_all_images(self):
        self.cursor.execute("SELECT * FROM images")
        return self.cursor.fetchall()

class ImageApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SioPay Image Slideshow")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Upload Images
        self.upload_button = QPushButton("Upload Images")
        self.upload_button.clicked.connect(self.upload_images)
        self.layout.addWidget(self.upload_button)

        self.upload_button.setStyleSheet("""
            background-color: #0a3d8f; 
            color: #eceff1; 
            border: none; 
            padding: 10px; 
            margin-top: 10px;
        """)

        # CRUD List
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.SingleSelection)
        self.image_list.itemClicked.connect(self.show_image)
        self.layout.addWidget(self.image_list)

        # CRUD Buttons
        self.crud_button_layout = QVBoxLayout()
        self.add_button = QPushButton("Add Image")
        self.add_button.clicked.connect(self.add_image)
        self.crud_button_layout.addWidget(self.add_button)

        self.add_button.setStyleSheet("""
            background-color: #0a3d8f; 
            color: #eceff1; 
            border: none; 
            padding: 10px; 
            margin-top: 10px;
        """)

        self.remove_button = QPushButton("Remove Image")
        self.remove_button.clicked.connect(self.remove_image)
        self.crud_button_layout.addWidget(self.remove_button)

        self.remove_button.setStyleSheet("""
            background-color: #0a3d8f; 
            color: #eceff1; 
            border: none; 
            padding: 10px; 
            margin-top: 10px;
        """)

        self.layout.addLayout(self.crud_button_layout)

        # Image Slideshow Button
        self.slideshow_button = QPushButton("Start Slideshow")
        self.slideshow_button.clicked.connect(self.start_slideshow)
        self.layout.addWidget(self.slideshow_button)

        self.slideshow_button.setStyleSheet("""
            background-color: #0a3d8f; 
            color: #eceff1; 
            border: none; 
            padding: 10px; 
            margin-top: 10px;
        """)

        self.image_db = ImageDatabase()
        self.load_images()

    def upload_images(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                self.image_db.insert_image(file_path)
            self.load_images()

    def load_images(self):
        self.image_list.clear()
        images = self.image_db.get_all_images()
        for image in images:
            path = image[1]
            filename = os.path.basename(path)
            self.image_list.addItem(filename)

    def show_image(self, item):
        image_path = self.image_db.get_all_images()[self.image_list.currentRow()][1]
        pixmap = QPixmap(image_path)
        dialog = QDialog(self)
        dialog.setWindowTitle("Image Preview")
        dialog.setGeometry(200, 200, 400, 400)
        label = QLabel(dialog)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        dialog.exec_()

    def add_image(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                self.image_db.insert_image(file_path)
            self.load_images()

    def remove_image(self):
        selected_row = self.image_list.currentRow()
        if selected_row != -1:
            image_id = self.image_db.get_all_images()[selected_row][0]
            self.image_db.cursor.execute("DELETE FROM images WHERE id=?", (image_id,))
            self.image_db.conn.commit()
            self.load_images()

    def start_slideshow(self):
        images = self.image_db.get_all_images()
        if images:
            slideshow = SlideshowDialog(images)
            slideshow.exec_()

class SlideshowDialog(QDialog):
    def __init__(self, images):
        super().__init__()

        self.setWindowTitle("Image Slideshow")
        self.setGeometry(0, 0, QApplication.desktop().screenGeometry().width(),
                         QApplication.desktop().screenGeometry().height())

        # Add Maximize Button
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        self.setWindowFlags(self.windowFlags() | Qt.WindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint))

        self.images = images
        self.current_index = 0

        self.layout = QVBoxLayout(self)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.timer = self.startTimer(10000)  # Change the timer interval as needed
        self.show_image()

    def show_image(self):
        image_path = self.images[self.current_index][1]
        pixmap = QPixmap(image_path)

        # Calculate the maximum size while maintaining the aspect ratio
        max_width = self.image_label.width()
        max_height = self.image_label.height()

        scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        # Update the displayed image when the dialog is resized
        self.show_image()
        super().resizeEvent(event)

    def timerEvent(self, event):
        self.current_index = (self.current_index + 1) % len(self.images)
        self.show_image()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Use a light theme with gray and deep blue as secondary colors
    app.setStyle("GTK+")
    palette = app.palette()
    palette.setColor(app.palette().Window, Qt.white)
    palette.setColor(app.palette().WindowText, Qt.black)
    palette.setColor(app.palette().Base, Qt.lightGray)
    palette.setColor(app.palette().AlternateBase, Qt.gray)
    palette.setColor(app.palette().Button, Qt.blue)
    palette.setColor(app.palette().ButtonText, Qt.white)
    app.setPalette(palette)

    window = ImageApp()
    window.show()

    sys.exit(app.exec_())
