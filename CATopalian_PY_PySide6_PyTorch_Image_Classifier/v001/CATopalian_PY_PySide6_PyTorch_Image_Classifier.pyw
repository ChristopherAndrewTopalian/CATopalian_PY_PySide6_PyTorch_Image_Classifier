# CATopalian_PY_PySide6_PyTorch_Image_Classifier.pyw

import sys
import os
import json

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtMultimedia import *

from PIL import Image
import torch
import torchvision.models as models
import torchvision.transforms as transforms

from src.py.theme.create_dark_palette import create_dark_palette

from src.py.scroll.create_scrollable_div import create_scrollable_div

####

app = QApplication(sys.argv)
QApplication.setStyle(QStyleFactory.create('Fusion'))
app.setPalette(create_dark_palette(app))

# qss location
qssFile = os.path.join('src', 'qss', 'style001.qss')

# open, read, apply qss style sheet
with open(qssFile, "r") as style_file:
    app.setStyleSheet(style_file.read())

####

# icon location
iconFile = os.path.join('src', 'media', 'textures', 'icons', 'catopalian_true_ai.png')

####

# set app icon
app.setWindowIcon(QIcon(iconFile))

####

# sound file location
clickSoundFile = os.path.join('src', 'media', 'sounds', 'click.wav')

# setup click sound
clickSound = QSoundEffect()
clickSound.setSource(QUrl.fromLocalFile(clickSoundFile))
clickSound.setVolume(0.2)

####

### WORLDWIDE STATE & MODEL SETUP ###

dog_keywords = [
    "terrier", "retriever", "spaniel", "hound", "poodle",
    "shepherd", "bulldog", "collie", "dog", "puppy"
]

# Load pre-trained MobileNetV3 with standard ImageNet weights
weights = models.MobileNet_V3_Small_Weights.DEFAULT
model = models.mobilenet_v3_small(weights=weights)
model.eval()
preprocess = weights.transforms()
categories = weights.meta["categories"]

####

def get_images_from_directory(dir_path):
    """Reads a folder and returns all valid image filenames."""
    allowed_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
    files = []
    if os.path.exists(dir_path):
        try:
            for item in os.listdir(dir_path):
                ext = os.path.splitext(item)[1].lower()
                if ext in allowed_exts:
                    files.append(item)
        except Exception as err:
            print(f"Error reading directory {dir_path}: {err}")
    return files

# CLASSIFICATION LOGIC

def run_classification(image_path, status_title, output_box):
    """Runs PyTorch MobileNet inference on the selected image."""
    status_title.setText("Analyzing image...")
    status_title.setStyleSheet("color: yellow; font-size: 24px; font-weight: bold;")
    QApplication.processEvents()

    try:
        img = Image.open(image_path).convert("RGB")
        batch = preprocess(img).unsqueeze(0)

        with torch.no_grad():
            prediction = model(batch).squeeze(0).softmax(0)

        # Get top 3 class predictions
        top3_prob, top3_cat_id = torch.topk(prediction, 3)

        predictions_list = []
        dog_detected = False

        for i in range(top3_prob.size(0)):
            score = float(top3_prob[i].item())
            class_name = categories[top3_cat_id[i].item()]
            predictions_list.append({
                "className": class_name,
                "probability": round(score, 4)
            })

            # Check if class name matches dog keywords
            if any(k in class_name.lower() for k in dog_keywords):
                dog_detected = True

        # Update visual title
        if dog_detected:
            status_title.setText("DOG DETECTED")
            status_title.setStyleSheet("color: lightgreen; font-size: 24px; font-weight: bold;")
        else:
            status_title.setText("NO DOG DETECTED")
            status_title.setStyleSheet("color: salmon; font-size: 24px; font-weight: bold;")

        # Update JSON output box
        output_box.setText(json.dumps(predictions_list, indent=2))

    except Exception as err:
        status_title.setText("ERROR")
        status_title.setStyleSheet("color: red; font-size: 24px; font-weight: bold;")
        output_box.setText(f"Inference error: {err}")

# UI ACTIONS & THUMBNAIL POPULATION

def load_selected_image(image_path, main_image_label, status_title, output_box):
    """Loads image into the main viewer and triggers classification."""
    pixmap = QPixmap(image_path)
    if not pixmap.isNull():
        # Grab your monitor's exact zoom scale (e.g., 1.5)
        ratio = main_image_label.devicePixelRatio()

        # Multiply our target size by the monitor's scale
        scaled_pixmap = pixmap.scaled(
            int(650 * ratio), int(350 * ratio), 
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # Tell the pixmap it is a High-Resolution image so it doesn't render huge
        scaled_pixmap.setDevicePixelRatio(ratio)
        
        main_image_label.setPixmap(scaled_pixmap)
        run_classification(image_path, status_title, output_box)


def populate_thumbnails(folder_path, thumb_layout, main_image_label, status_title, output_box):
    """Clears and rebuilds the left thumbnail gallery."""
    # Clear existing widgets from layout
    while thumb_layout.count():
        item = thumb_layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    files = get_images_from_directory(folder_path)

    if files:
        for filename in files:
            img_path = os.path.join(folder_path, filename)
            pixmap = QPixmap(img_path)

            if not pixmap.isNull():
                thumb = QLabel()

                # Grab your monitor's exact zoom scale
                ratio = thumb.devicePixelRatio()

                # Multiply our target size by the monitor's scale
                scaled_thumb = pixmap.scaled(
                    int(240 * ratio), int(170 * ratio), 
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )

                # Tell the pixmap it is a High-Resolution image
                scaled_thumb.setDevicePixelRatio(ratio)
                
                thumb.setPixmap(scaled_thumb)
                thumb.setAlignment(Qt.AlignCenter)
                thumb.setToolTip(filename)
                thumb.setCursor(QCursor(Qt.PointingHandCursor))
                thumb.setStyleSheet("border: 2px solid transparent; border-radius: 4px;")

                # Mouse click event
                def make_click_handler(path_to_load):
                    return lambda event: load_selected_image(
                        path_to_load, main_image_label, status_title, output_box
                    )

                thumb.mousePressEvent = make_click_handler(img_path)
                thumb_layout.addWidget(thumb)

        # Load first image automatically
        first_img_path = os.path.join(folder_path, files[0])
        load_selected_image(first_img_path, main_image_label, status_title, output_box)
    else:
        no_files_msg = QLabel("No images found in this folder.")
        no_files_msg.setStyleSheet("color: #aaa; font-size: 13px;")
        thumb_layout.addWidget(no_files_msg)

####

def choose_folder_dialog(window, thumb_layout, main_image_label, status_title, output_box):
    """Opens a native directory chooser dialog."""
    chosen_dir = QFileDialog.getExistingDirectory(window, "Select Texture Folder")
    if chosen_dir:
        populate_thumbnails(chosen_dir, thumb_layout, main_image_label, status_title, output_box)

####

# MAIN INTERFACE BUILDER (Purely Functional)

window = QWidget()
window.setWindowTitle("CATopalian PY PySide6 PyTorch Image Classifier")
window.resize(1100, 700)

# Main Horizontal Split Layout
main_layout = QHBoxLayout(window)
main_layout.setContentsMargins(0, 0, 0, 0)
main_layout.setSpacing(0)

# LEFT COLUMN (Sidebar)
left_menu = QWidget()
left_menu.setFixedWidth(250)
left_menu.setStyleSheet("background-color: rgb(20, 20, 20); border-right: 2px solid #555;")
left_layout = QVBoxLayout(left_menu)
left_layout.setContentsMargins(10, 10, 10, 10)
left_layout.setSpacing(10)

# Repository Title Link
title_link = QLabel("CATopalian PY PySide6 PyTorch Image Classifier")
title_link.setWordWrap(True)
title_link.setCursor(QCursor(Qt.PointingHandCursor))
title_link.setStyleSheet("font-size: 17px; font-weight: bold; color: rgb(170, 170, 170);")
title_link.mousePressEvent = lambda e: QDesktopServices.openUrl(
    QUrl("https://github.com/ChristopherAndrewTopalian/CATopalian_PY_PySide6_PyTorch_Image_Classifier")
)
left_layout.addWidget(title_link)

# Choose Folder Button
choose_btn = QPushButton("Choose Folder")
choose_btn.setCursor(QCursor(Qt.PointingHandCursor))
choose_btn.setStyleSheet("""
    QPushButton {
        background-color: rgb(50, 50, 50);
        color: white;
        border: 1px solid #777;
        border-radius: 4px;
        padding: 8px 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: rgb(70, 70, 70);
    }
""")
left_layout.addWidget(choose_btn)

# Scrollable Div for Thumbnails
scroll_area, thumb_container, thumb_layout = create_scrollable_div()
left_layout.addWidget(scroll_area)
main_layout.addWidget(left_menu)

# Connect Choose Folder action
choose_btn.clicked.connect(
    lambda: choose_folder_dialog(window, thumb_layout, main_image, status_title, output_box)
)

# RIGHT COLUMN (Content)
right_content = QWidget()
right_layout = QVBoxLayout(right_content)
right_layout.setContentsMargins(20, 15, 20, 15)
right_layout.setSpacing(10)

# Main Display Image
main_image = QLabel()
main_image.setAlignment(Qt.AlignCenter)
main_image.setFixedHeight(400)
main_image.setStyleSheet("background-color: black; border: 1px solid #777;")
right_layout.addWidget(main_image)

# Status Heading
status_title = QLabel("Select an image...")
status_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 5px;")
right_layout.addWidget(status_title)

# Output Box (JSON Predictions)
output_box = QTextEdit()
output_box.setReadOnly(True) # Prevents typing, makes it act like a selectable label!
output_box.setStyleSheet("""
    QTextEdit {
        background-color: rgb(20, 20, 20);
        border: 1px solid #555;
        border-radius: 5px;
        padding: 12px;
        font-family: Arial;
        font-size: 24px;
        font-weight: bold;
        color: rgb(0, 255,255);
    }
""")
right_layout.addWidget(output_box)

'''
# Output Box (JSON Predictions)
output_box = QLabel()
output_box.setTextInteractionFlags(Qt.TextSelectableByMouse)
output_box.setStyleSheet("""
    background-color: rgb(20, 20, 20);
    border: 1px solid #555;
    border-radius: 5px;
    padding: 12px;
    font-family: Arial;
    font-size: 24px;
    font-weight: bold;
""")
output_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
output_box.setAlignment(Qt.AlignTop | Qt.AlignLeft)
right_layout.addWidget(output_box)
'''

main_layout.addWidget(right_content)

####

# Load Default Folder on Startup (Cross-Platform)
default_folder = os.path.join("src", "media", "textures", "textures_001")
populate_thumbnails(default_folder, thumb_layout, main_image, status_title, output_box)

####

window.show()

sys.exit(app.exec())

####

# Dedicated to God the Father
# All Rights Reserved Christopher Andrew Topalian Copyright 2000-2026
# https://github.com/ChristopherTopalian
# https://github.com/ChristopherAndrewTopalian
# https://sites.google.com/view/CollegeOfScripting

