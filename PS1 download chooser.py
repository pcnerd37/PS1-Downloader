from PyQt5.QtWidgets import QApplication, QCheckBox, QVBoxLayout, QWidget, QPushButton, QScrollArea, QFileDialog, QHBoxLayout, QLabel, QProgressBar, QMessageBox, QGridLayout, QLineEdit
import requests
from bs4 import BeautifulSoup

def get_file_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    entries = []
    for row in soup.find_all('tr'):
        link = row.find('a')
        size = row.find('td', class_='size')
        if link and '(USA)' in link.text and size:
            size_text = size.text.strip()
            size_value = float(size_text.split()[0])  # Assuming size is like '266.9 MiB'
            entries.append((link.text, size_text, size_value))
    return entries

def download_files(links, download_folder, progress_callback):
    total_files = len(links)
    for index, (link_text, _, _) in enumerate(links):
        file_url = base_url + link_text
        r = requests.get(file_url, stream=True)
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        downloaded_size = 0
        with open(f"{download_folder}/{link_text}", 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded_size += len(chunk)
                progress = int((downloaded_size / total_size) * 100)
                progress_callback(progress, index, total_files)
        print(f"Downloaded {link_text}")

def update_progress_bar(progress, file_index, total_files):
    progress_bar.setValue(progress)
    progress_bar.setFormat(f"Downloading file {file_index+1} of {total_files}: {progress}%")

def update_total_size_label():
    total_size = sum(file_links_with_sizes[i][2] for i, cb in enumerate(checkboxes) if cb.isChecked())
    total_size_label.setText(f"Total size: {total_size:.2f} MiB")

def search_items(query):
    for widget, (link_text, _, _) in zip(container_widgets, file_links_with_sizes):
        if query.lower() in link_text.lower():
            widget.show()
        else:
            widget.hide()

def select_all(checkboxes, is_checked):
    for checkbox in checkboxes:
        checkbox.stateChanged.disconnect()
        checkbox.setChecked(is_checked)
    for checkbox in checkboxes:
        checkbox.stateChanged.connect(lambda _, cb=checkbox: update_total_size_label())
    update_total_size_label()

# URL and File Links
base_url = "https://myrient.erista.me/files/Redump/Sony%20-%20PlayStation/"
file_links_with_sizes = get_file_links(base_url)

app = QApplication([])
window = QWidget()
layout = QVBoxLayout(window)

search_line_edit = QLineEdit()
search_line_edit.setPlaceholderText("Search items...")
search_line_edit.textChanged.connect(search_items)
layout.addWidget(search_line_edit)

# Create a scroll area widget and vertical box layout
scroll_area = QScrollArea()
scroll_widget = QWidget()
scroll_layout = QVBoxLayout(scroll_widget)

checkboxes = []
container_widgets = []
for link_text, size_text, _ in file_links_with_sizes:
    file_layout = QHBoxLayout()
    checkbox = QCheckBox(link_text)
    checkbox.stateChanged.connect(update_total_size_label)
    label = QLabel(size_text)
    file_layout.addWidget(checkbox)
    file_layout.addWidget(label)
    container_widget = QWidget()
    container_widget.setLayout(file_layout)
    scroll_layout.addWidget(container_widget)
    container_widgets.append(container_widget)
    checkboxes.append(checkbox)

scroll_widget.setLayout(scroll_layout)
scroll_area.setWidgetResizable(True)
scroll_area.setWidget(scroll_widget)
layout.addWidget(scroll_area)

# Progress bar and total size label
progress_bar = QProgressBar()
progress_bar.setMaximum(100)
layout.addWidget(progress_bar)

total_size_label = QLabel("Total size: 0.00 MiB")
layout.addWidget(total_size_label)

# Download and Select All buttons
button_layout = QGridLayout()
download_btn = QPushButton('Download Selected')
download_btn.clicked.connect(lambda: on_download(checkboxes, file_links_with_sizes))
button_layout.addWidget(download_btn, 0, 0)

select_all_btn = QPushButton('Select/Deselect All')
select_all_btn.setCheckable(True)
select_all_btn.toggled.connect(lambda checked: select_all(checkboxes, checked))
button_layout.addWidget(select_all_btn, 0, 1)

layout.addLayout(button_layout)

window.setLayout(layout)
window.show()
app.exec_()