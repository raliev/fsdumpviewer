from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QGridLayout, QLineEdit

from customTableWidget import CustomTableWidget;


def setupUI(diffApp, argv):
    # Установка интерфейса
    layout = QVBoxLayout()
    grid_layout = QGridLayout()

    diffApp.file_path1 = QLineEdit(diffApp)
    if len(argv) > 1:  # Проверяем, есть ли аргумент командной строки для первого файла
        diffApp.file_path1.setText(argv[1])
    diffApp.select_file_button1 = QPushButton("Select File", diffApp)
    diffApp.select_file_button1.clicked.connect(lambda: diffApp.select_file(diffApp.file_path1))

    diffApp.file_path2 = QLineEdit(diffApp)
    if len(argv) > 2:  # Проверяем, есть ли аргумент командной строки для второго файла
        diffApp.file_path2.setText(argv[2])
    diffApp.select_file_button2 = QPushButton("Select File", diffApp)
    diffApp.select_file_button2.clicked.connect(lambda: diffApp.select_file(diffApp.file_path2))

    grid_layout.addWidget(diffApp.file_path1, 0, 0)
    grid_layout.addWidget(diffApp.select_file_button1, 0, 1)
    grid_layout.addWidget(diffApp.file_path2, 1, 0)
    grid_layout.addWidget(diffApp.select_file_button2, 1, 1)

    layout.addLayout(grid_layout)

    #diffApp.text_area1 = QTextEdit(diffApp)
    #diffApp.text_area2 = QTextEdit(diffApp)
    #grid_layout.addWidget(diffApp.text_area1, 0, 0)
    #grid_layout.addWidget(diffApp.text_area2, 0, 1)
    #layout.addLayout(grid_layout)

    diffApp.process_button = QPushButton("Process", diffApp)
    diffApp.process_button.clicked.connect(diffApp.process_raw_data)
    layout.addWidget(diffApp.process_button)
    diffApp.compare_button = QPushButton("Compare", diffApp)
    diffApp.compare_button.clicked.connect(diffApp.docompare)
    layout.addWidget(diffApp.compare_button)

    # Создание таблицы для отображения результатов
    diffApp.result_table1 = CustomTableWidget(0, 3)
    diffApp.result_table1.setHorizontalHeaderLabels(["Filename", "Size", "Permissions"])
    diffApp.result_table1.horizontalHeader().setStretchLastSection(True)
    diffApp.result_table1.setEditTriggers(QTableWidget.NoEditTriggers)
    diffApp.result_table1.installEventFilter(diffApp)
    diffApp.result_table2 = CustomTableWidget(0, 3)
    diffApp.result_table2.setHorizontalHeaderLabels(["Filename", "Size", "Permissions"])
    diffApp.result_table2.horizontalHeader().setStretchLastSection(True)
    diffApp.result_table2.setEditTriggers(QTableWidget.NoEditTriggers)

    monospace_font = QFont("Courier New")
    diffApp.result_table1.setFont(monospace_font)
    diffApp.result_table2.setFont(monospace_font)

    grid_layout2 = QGridLayout()
    grid_layout2.addWidget(diffApp.result_table1, 0, 0)
    grid_layout2.addWidget(diffApp.result_table2, 0, 1)
    layout.addLayout(grid_layout2)
    diffApp.setLayout(layout)

