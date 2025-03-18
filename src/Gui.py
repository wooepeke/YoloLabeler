import sys
import os
import shutil
import json
from PyQt5.QtCore import Qt, QFile, QTextStream, QFileInfo, QRect, QPoint, QSize, QModelIndex
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QCursor
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTreeView, 
                            QFileSystemModel, QLabel, QTextEdit, QPushButton, QMenu, 
                            QAction, QMessageBox, QInputDialog, QFileDialog)

class FileExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.drawing_rect = None
        self.rectangles = []  # List to hold drawn rectangles
        self.current_image = None  # To store the currently displayed image
        self.image_position = QPoint()  # Image offset within QLabel
        self.image_size = QSize()  # Store the original image size
        self.scaled_image = None  # Store the scaled image
        self.current_file_path = None  # Track the currently selected file

    def initUI(self):
        self.setWindowTitle("Advanced File Explorer with Annotations")
        self.setGeometry(100, 100, 1000, 700)  # Set window size

        # Get parent directory of the current working directory
        current_folder = os.getcwd()
        parent_folder = os.path.dirname(current_folder)

        # Create file system model
        self.model = QFileSystemModel()
        self.model.setRootPath(parent_folder)
        
        # Allow drag and drop
        self.model.setReadOnly(False)

        # Create tree view
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(parent_folder))
        self.tree.selectionModel().selectionChanged.connect(self.on_file_selected)
        
        # Enable drag and drop in tree view
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(QTreeView.InternalMove)
        
        # Enable context menu for file operations
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        # Image display
        self.image_display = QLabel(self)
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setText("Select an image file")
        self.image_display.setStyleSheet("border: 1px solid #cccccc;")

        # Json display
        self.json_display = QLabel(self)
        self.json_display.setAlignment(Qt.AlignLeft)
        self.json_display.setText("Select an json file")
        self.json_display.setStyleSheet("border: 1px solid #cccccc;")

        # Annotation information display
        self.info_display = QLabel(self)
        self.info_display.setText("No annotations")
        self.info_display.setFixedHeight(30)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.undo_button = QPushButton("Undo", self)
        self.undo_button.clicked.connect(self.undo_bbox)
        btn_layout.addWidget(self.undo_button)
        
        self.clear_button = QPushButton("Clear All", self)
        self.clear_button.clicked.connect(self.clear_annotations)
        btn_layout.addWidget(self.clear_button)

        self.export_button = QPushButton("Export Coordinates", self)
        self.export_button.clicked.connect(self.export_coordinates)
        btn_layout.addWidget(self.export_button)
        
        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.quit_program)
        btn_layout.addWidget(self.quit_button)

        # Layout setup
        file_panel = QVBoxLayout()
        file_panel.addWidget(QLabel("File Explorer:"))
        file_panel.addWidget(self.tree)
        
        image_panel = QVBoxLayout()
        image_panel.addWidget(self.image_display)
        image_panel.addWidget(self.json_display)
        image_panel.addWidget(self.info_display)
        image_panel.addLayout(btn_layout)

        h_layout = QHBoxLayout()
        h_layout.addLayout(file_panel, 1)
        h_layout.addLayout(image_panel, 2)

        main_layout = QVBoxLayout()
        main_layout.addLayout(h_layout)

        self.setLayout(main_layout)
        self.drawing = False
        self.start_point = QPoint()
        
        # Status message
        self.status_label = QLabel("Ready")
        self.status_label.setFixedHeight(20)
        main_layout.addWidget(self.status_label)

    def show_context_menu(self, position):
        indexes = self.tree.selectedIndexes()
        if not indexes:
            return
            
        # Get the first selected index (for single selection)
        index = indexes[0]
        file_path = self.model.filePath(index)
        file_info = QFileInfo(file_path)
        
        # Create context menu
        context_menu = QMenu(self)
        
        # Add actions based on selection type
        if file_info.isDir():
            new_folder_action = QAction("New Folder", self)
            new_folder_action.triggered.connect(lambda: self.create_new_folder(file_path))
            context_menu.addAction(new_folder_action)
            
            import_action = QAction("Import Files", self)
            import_action.triggered.connect(lambda: self.import_files(file_path))
            context_menu.addAction(import_action)
        
        if file_info.isFile() or file_info.isDir():
            rename_action = QAction("Rename", self)
            rename_action.triggered.connect(lambda: self.rename_item(file_path))
            context_menu.addAction(rename_action)
            
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.delete_item(file_path))
            context_menu.addAction(delete_action)
            
            cut_action = QAction("Cut", self)
            cut_action.triggered.connect(lambda: self.cut_item(file_path))
            context_menu.addAction(cut_action)
            
            copy_action = QAction("Copy", self)
            copy_action.triggered.connect(lambda: self.copy_item(file_path))
            context_menu.addAction(copy_action)
        
        # Add paste action if we have something in clipboard
        if hasattr(self, 'clipboard_path'):
            paste_action = QAction("Paste", self)
            paste_action.triggered.connect(lambda: self.paste_item(file_path))
            context_menu.addAction(paste_action)
        
        # Show the context menu
        context_menu.exec_(self.tree.viewport().mapToGlobal(position))

    def create_new_folder(self, parent_path):
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and folder_name:
            new_folder_path = os.path.join(parent_path, folder_name)
            try:
                os.makedirs(new_folder_path)
                self.status_label.setText(f"Created folder: {folder_name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not create folder: {str(e)}")

    def rename_item(self, file_path):
        old_name = os.path.basename(file_path)
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=old_name)
        
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            try:
                os.rename(file_path, new_path)
                self.status_label.setText(f"Renamed: {old_name} to {new_name}")
                
                # If renamed file was the current image, update path
                if self.current_file_path == file_path:
                    self.current_file_path = new_path
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not rename: {str(e)}")

    def delete_item(self, file_path):
        name = os.path.basename(file_path)
        msg = f"Are you sure you want to delete '{name}'?"
        if QFileInfo(file_path).isDir():
            msg += "\nAll contents will be permanently deleted."
            
        confirm = QMessageBox.question(self, "Confirm Delete", msg, 
                                      QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            try:
                if QFileInfo(file_path).isDir():
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                    
                # Clear display if deleted file was current image
                if self.current_file_path == file_path:
                    self.current_file_path = None
                    self.current_image = None
                    self.image_display.clear()
                    self.image_display.setText("Image deleted")
                    self.rectangles.clear()
                
                self.status_label.setText(f"Deleted: {name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete: {str(e)}")

    def cut_item(self, file_path):
        self.clipboard_path = file_path
        self.clipboard_operation = "cut"
        name = os.path.basename(file_path)
        self.status_label.setText(f"Cut: {name}")

    def copy_item(self, file_path):
        self.clipboard_path = file_path
        self.clipboard_operation = "copy"
        name = os.path.basename(file_path)
        self.status_label.setText(f"Copied: {name}")

    def paste_item(self, destination_path):
        if not hasattr(self, 'clipboard_path') or not self.clipboard_path:
            return
            
        # If destination is a file, use its parent directory
        if os.path.isfile(destination_path):
            destination_path = os.path.dirname(destination_path)
            
        source_path = self.clipboard_path
        source_name = os.path.basename(source_path)
        destination_file = os.path.join(destination_path, source_name)
        
        # Check if destination already exists
        if os.path.exists(destination_file):
            confirm = QMessageBox.question(self, "File exists", 
                        f"{source_name} already exists at destination.\nOverwrite?",
                        QMessageBox.Yes | QMessageBox.No)
            if confirm != QMessageBox.Yes:
                return
        
        try:
            if self.clipboard_operation == "cut":
                shutil.move(source_path, destination_path)
                self.status_label.setText(f"Moved: {source_name}")
                self.clipboard_path = None
            else:  # copy
                if os.path.isdir(source_path):
                    dest_dir = os.path.join(destination_path, source_name)
                    shutil.copytree(source_path, dest_dir)
                else:
                    shutil.copy2(source_path, destination_path)
                self.status_label.setText(f"Copied: {source_name}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Operation failed: {str(e)}")

    def import_files(self, folder_path):
        files, _ = QFileDialog.getOpenFileNames(self, "Import Files", "", 
                                             "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)")
        if not files:
            return
            
        for file_path in files:
            try:
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(folder_path, file_name)
                
                # Check if file already exists
                if os.path.exists(dest_path):
                    confirm = QMessageBox.question(self, "File exists", 
                              f"{file_name} already exists. Overwrite?",
                              QMessageBox.Yes | QMessageBox.No)
                    if confirm != QMessageBox.Yes:
                        continue
                        
                shutil.copy2(file_path, folder_path)
            except Exception as e:
                QMessageBox.warning(self, "Import Error", f"Failed to import {file_name}: {str(e)}")
        
        self.status_label.setText(f"Imported {len(files)} files")

    def clear_annotations(self):
        if self.rectangles:
            self.rectangles.clear()
            self.update_image_display()
            self.update_annotation_info()

    def on_file_selected(self):
        indexes = self.tree.selectedIndexes()
        if not indexes:
            return

        index = indexes[0]
        file_path = self.model.filePath(index)
        self.current_file_path = file_path

        # Clear any previous content
        self.image_display.clear()
        
        # Check if the selected file is a directory
        if QFileInfo(file_path).isDir():
            self.image_display.setText("Select a file to display")
            self.rectangles.clear()
            self.update_annotation_info()
            return

        # If the file is an image, display it
        if self.is_image_file(file_path):
            self.display_image(file_path)
        elif file_path.lower().endswith('.json'):
            # If it's a JSON file, read and display its content
            self.display_json(file_path)
        else:
            # If it's not an image or JSON file, show a default message
            self.image_display.setText("Selected file is not an image or JSON")
                
    def is_image_file(self, file_path):
            return any(file_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'])
            
    def update_annotation_info(self):
        """Update the annotation information display"""
        if not self.rectangles:
            self.info_display.setText("No annotations")
        else:
            self.info_display.setText(f"Annotations: {len(self.rectangles)} bounding boxes")
            
    def export_coordinates(self):
        """Export the coordinates of all bounding boxes with labels to a JSON file"""
        if not self.rectangles or not self.current_file_path:
            QMessageBox.information(self, "Export", "No annotations to export")
            return

        # Ensure labels folder exists
        labels_folder = os.path.join(self.parent_folder, "labels")
        os.makedirs(labels_folder, exist_ok=True)  # Create if doesn't exist

        # JSON and YOLO format file paths
        base_name = os.path.splitext(os.path.basename(self.current_file_path))[0]
        json_path = os.path.join(labels_folder, f"{base_name}.json")
        txt_path = os.path.join(labels_folder, f"{base_name}.txt")

        try:
            # Ensure JSON file exists before writing
            if not os.path.exists(json_path):
                with open(json_path, 'w') as f:
                    json.dump({}, f)  # Initialize with an empty JSON object

            # Collect labeled bounding boxes
            labeled_boxes = []
            for i, item in enumerate(self.rectangles):
                rect = item['rect']  # Accessing the QRect here
                label = item['label']

                # Save the coordinates and label
                labeled_boxes.append({
                    'label': label,
                    'x': rect.x(),
                    'y': rect.y(),
                    'width': rect.width(),
                    'height': rect.height()
                })

            # Save to JSON file
            with open(json_path, 'w') as f:
                json.dump({
                    'image': self.current_file_path,
                    'size': {
                        'width': self.image_size.width(),
                        'height': self.image_size.height()
                    },
                    'annotations': labeled_boxes
                }, f, indent=2)

            # Also save in YOLO format
            with open(txt_path, 'w') as f:
                img_width = self.image_size.width()
                img_height = self.image_size.height()

                for box in labeled_boxes:
                    x_center = (box['x'] + box['width'] / 2) / img_width
                    y_center = (box['y'] + box['height'] / 2) / img_height
                    width = box['width'] / img_width
                    height = box['height'] / img_height

                    f.write(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

            self.status_label.setText(f"Annotations exported to {os.path.basename(json_path)}")

            annotated_folder = os.path.join(self.parent_folder, "annotated_images")
            if not os.path.exists(annotated_folder):
                os.makedirs(annotated_folder)
            annotated_path = os.path.join(annotated_folder, os.path.basename(self.image_path))
            self.image_display.pixmap().save(annotated_path)
            print(f"Annotated image saved at: {annotated_path}")

        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export annotations: {str(e)}")

    def display_image(self, file_path):
        self.current_image = QPixmap(file_path)
        self.image_path = file_path  # Store file path for saving annotated image
        self.image_folder = os.path.dirname(file_path)  # Store the image folder
        self.parent_folder = os.path.dirname(self.image_folder)  # Get one level above image folder

        if "annotated_images" in file_path:
            self.export_button.setDisabled(True)
        
        if self.current_image.isNull():
            self.image_display.setText("Failed to load image.")
        else:
            # Set image
            self.scaled_image = self.current_image.scaled(self.image_display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_position = QPoint((self.image_display.width() - self.scaled_image.width()) // 2, 
                                         (self.image_display.height() - self.scaled_image.height()) // 2)
            self.image_size = self.current_image.size()
            self.image_display.setPixmap(self.scaled_image)
            self.rectangles.clear()
            
            # # Set json
            label_folder = os.path.join(self.parent_folder, "labels")
            files_and_dirs = os.listdir(label_folder)
            
            filename = os.path.splitext(os.path.basename(file_path))[0] + ".json"
            
            try:
                json_path = os.path.join(label_folder, filename)
                self.display_json(json_path)
            except:
                print("No File found")

    def display_json(self, json_path):
        """Display the content of a JSON file"""
        try:
            print(json_path)
            with open(json_path, 'r') as json_file:
                data = json.load(json_file)
            
            # Convert the data to a formatted string for display
            formatted_json = json.dumps(data, indent=4)
            
            # Display the formatted JSON string in the QLabel
            self.json_display.setText(f"JSON Content:\n{formatted_json}")
            
            # Set styling for the QLabel (left alignment and monospaced font)
            self.json_display.setStyleSheet("""
                font-family: Courier, monospace;
                font-size: 10pt;
                background-color: #f7f7f7;
                border: 1px solid #cccccc;
                padding: 10px;
                text-align: left;
                word-wrap: break-word;
            """)
        except Exception as e:
            # QMessageBox.warning(self, "Error", f"Failed to read JSON file: {str(e)}")   
            self.json_display.setText(f"No Json File Found")
            
    def mousePressEvent(self, event):
        if "annotated_images" in self.current_file_path:
            return

        if self.current_image and event.button() == Qt.LeftButton:
            self.drawing = True
            local_pos = (event.pos() - self.image_display.pos())
            if not self.is_inside_image(local_pos):
                self.drawing = False
                return
            self.start_point = self.convert_to_original_image_coords(local_pos)

    def mouseMoveEvent(self, event):
        if "annotated_images" in self.current_file_path:
            return

        if self.drawing and self.current_image:
            local_pos = event.pos() - self.image_display.pos()
            if not self.is_inside_image(local_pos):
                return
            self.drawing_rect = QRect(self.start_point, self.convert_to_original_image_coords(local_pos)).normalized()
            self.update_image_display()

    def mouseReleaseEvent(self, event):
        if "annotated_images" in self.current_file_path:
            return

        if self.drawing and self.current_image:
            local_pos = event.pos() - self.image_display.pos()
            if not self.is_inside_image(local_pos):
                return
                
            self.drawing_rect = QRect(self.start_point, self.convert_to_original_image_coords(local_pos)).normalized()
            
            # Only add the rectangle if it has a reasonable size
            if self.drawing_rect.width() > 5 and self.drawing_rect.height() > 5:
                # Get a label for this rectangle
                label, ok = QInputDialog.getText(self, "Object Label", "Enter a label for this object:", text="object")
                
                if ok:  # User clicked OK
                    # Store rectangle with its label (use a dictionary instead of just the rect)
                    self.rectangles.append({
                        'rect': self.drawing_rect,
                        'label': label
                    })
                    self.update_image_display()
                    self.update_annotation_info()
            
            self.drawing = False

    def is_inside_image(self, pos):
        return (self.image_position.x() <= pos.x() <= self.image_position.x() + self.scaled_image.width() and
                self.image_position.y() <= pos.y() <= self.image_position.y() + self.scaled_image.height())

    def convert_to_original_image_coords(self, pos):
        relative_x = (pos.x() - self.image_position.x()) / self.scaled_image.width()
        relative_y = (pos.y() - self.image_position.y()) / self.scaled_image.height()
        original_x = int(relative_x * self.image_size.width())
        original_y = int(relative_y * self.image_size.height())
        return QPoint(original_x, original_y)

    def update_image_display(self):
        if self.current_image:
            pixmap = self.scaled_image.copy()
            painter = QPainter(pixmap)
            
            # Draw all rectangles
            for item in self.rectangles:
                rect = item['rect']
                label = item['label']
                
                # Draw rectangle
                painter.setPen(QPen(QColor(0, 255, 0), 3))
                painter.setBrush(Qt.transparent)
                
                scaled_rect = QRect(
                    int(rect.x() * self.scaled_image.width() / self.image_size.width()),
                    int(rect.y() * self.scaled_image.height() / self.image_size.height()),
                    int(rect.width() * self.scaled_image.width() / self.image_size.width()),
                    int(rect.height() * self.scaled_image.height() / self.image_size.height())
                )
                painter.drawRect(scaled_rect)
                
                # Draw label above the rectangle
                painter.setPen(QColor(0, 0, 0))
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)
                
                label_rect = QRect(
                    scaled_rect.x(),
                    scaled_rect.y() - 20,  # Position above the box
                    scaled_rect.width(),
                    20
                )
                
                # Draw background for text
                painter.fillRect(label_rect, QColor(0, 255, 0, 180))
                painter.drawText(label_rect, Qt.AlignCenter, label)
                
            painter.end()
            self.image_display.setPixmap(pixmap)
            self.update_annotation_info()

    def undo_bbox(self):
        if self.rectangles:
            self.rectangles.pop()
            self.update_image_display()

    def quit_program(self):
        QApplication.quit()

app = QApplication(sys.argv)
window = FileExplorer()
window.show()
sys.exit(app.exec_())
