import sys
import os
from PyQt5.QtCore import Qt, QFile, QTextStream, QFileInfo
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QFileSystemModel, QLabel, QTextEdit, QMessageBox

class FileExplorer(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Explorer with File Preview")
        self.setGeometry(100, 100, 800, 400)  # Window size (width, height)

        # Get the current working directory and move one level up
        current_folder = os.getcwd()
        parent_folder = os.path.dirname(current_folder)  # This gets the parent directory

        # Create the QFileSystemModel to access the file system
        self.model = QFileSystemModel()
        self.model.setRootPath(parent_folder)  # Set the root to the parent folder

        # Create the QTreeView for displaying the file system
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(parent_folder))  # Show only files inside the parent folder

        # Connect the selectionChanged signal to handle file clicks
        self.tree.selectionModel().selectionChanged.connect(self.on_file_selected)

        # Create a QTextEdit for displaying file content (on the right side)
        self.file_content_display = QTextEdit(self)
        self.file_content_display.setReadOnly(True)  # Make the QTextEdit read-only

        # Create a horizontal layout
        h_layout = QHBoxLayout()

        # Add the file system view (tree) to the left side
        h_layout.addWidget(self.tree, 1)  # 1 means it takes up most of the space
        # Add the file content display to the right side
        h_layout.addWidget(self.file_content_display, 2)  # 2 means it takes up less space

        # Set the layout for the main window
        self.setLayout(h_layout)

    def on_file_selected(self):
        # Get the selected index from the QTreeView
        index = self.tree.selectedIndexes()[0]
        
        # Get the file path of the selected item
        file_path = self.model.filePath(index)

        # Check if the selected item is a directory
        if QFileInfo(file_path).isDir():
            self.file_content_display.clear()  # Clear the content display if it's a directory
            return

        # Check if the selected item is a file (using QFileInfo)
        if QFileInfo(file_path).isFile():
            self.display_file_content(file_path)

    def display_file_content(self, file_path):
        # Open the file and read its contents (only for text files)
        file = QFile(file_path)
        if file.open(QFile.ReadOnly | QFile.Text):
            text_stream = QTextStream(file)
            file_content = text_stream.readAll()  # Read the entire file content
            self.file_content_display.setText(file_content)  # Display it in QTextEdit
        else:
            self.file_content_display.setText("Failed to open file.")

# Run the application
app = QApplication(sys.argv)
window = FileExplorer()
window.show()
sys.exit(app.exec_())
