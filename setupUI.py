from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidget, QLabel, QCheckBox, QComboBox, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QGridLayout, QLineEdit

from customTableWidget import CustomTableWidget;

LSLR_ONLYSELECTED = "export to `ls -lR` ONLY selected";
LSLR_EXCLUDESELECTED = "export to `ls -lR` EXCLUDE selected";
CSV = "csv";
BASH_ZIP_SELECTED = "bash: zip selected";
BASH_COPY_SELECTED_TO_CURRENT = "bash: copy selected to .";
BASH_COPY_SELECTED_TO_ANOTHER = "bash: copy selected to another panel";
BASH_CREATE_MD5 = "bash: create md5sum(selected)";

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

    ignoreRegexpLabel = QLabel('Ignore files (regexp):')

    diffApp.ignoreRegexp = QLineEdit(diffApp)
    diffApp.ignoreRegexp.setText("^\.|^(Generated)|^gensrc$|^classes$|\.class$")
    grid_layout.addWidget(ignoreRegexpLabel)
    grid_layout.addWidget(diffApp.ignoreRegexp)

    syncPanelsLabel = QLabel('Synchronize panels when navigating')
    diffApp.syncPanels = QCheckBox(diffApp)
    diffApp.syncPanels.setCheckState(Qt.Checked)
    grid_layout.addWidget(syncPanelsLabel)
    grid_layout.addWidget(diffApp.syncPanels)


    layout.addLayout(grid_layout)

    #diffApp.text_area1 = QTextEdit(diffApp)
    #diffApp.text_area2 = QTextEdit(diffApp)
    #grid_layout.addWidget(diffApp.text_area1, 0, 0)
    #grid_layout.addWidget(diffApp.text_area2, 0, 1)
    #layout.addLayout(grid_layout)

    diffApp.process_button = QPushButton("Process", diffApp)
    diffApp.process_button.clicked.connect(diffApp.process_raw_data)
    layout.addWidget(diffApp.process_button)

    diffApp.compare_sizes = QCheckBox(diffApp)
    diffApp.compare_sizesLabel = QLabel("compare sizes")
    diffApp.compare_sizes.setCheckState(Qt.Checked)

    hbox1 = QHBoxLayout()
    hbox1.addWidget(diffApp.compare_sizes)
    hbox1.addWidget(diffApp.compare_sizesLabel, 1)

    hboxCb = QHBoxLayout()

    hboxCb.addLayout(hbox1)

    diffApp.compare_modiftime = QCheckBox(diffApp)
    diffApp.compare_modiftimeLabel = QLabel("compare modif times")
    diffApp.compare_modiftime.setCheckState(Qt.Unchecked)

    hbox2 = QHBoxLayout()
    hbox2.addWidget(diffApp.compare_modiftime)
    hbox2.addWidget(diffApp.compare_modiftimeLabel, 1)

    hboxCb.addLayout(hbox2)

    diffApp.compare_checksums = QCheckBox(diffApp)
    diffApp.compare_checksumsLabel = QLabel("compare checksums")
    diffApp.compare_checksums.setCheckState(Qt.Unchecked)

    hbox = QHBoxLayout()
    hbox.addWidget(diffApp.compare_checksums)
    hbox.addWidget(diffApp.compare_checksumsLabel, 1)

    hboxCb.addLayout(hbox)

    diffApp.compare_specialmark = QCheckBox(diffApp)
    diffApp.compare_specialmarkLabel = QLabel("special mark")
    diffApp.compare_specialmark.setCheckState(Qt.Checked)

    hbox = QHBoxLayout()
    hbox.addWidget(diffApp.compare_specialmark)
    hbox.addWidget(diffApp.compare_specialmarkLabel, 1)

    hboxCb.addLayout(hbox)

    layout.addLayout(hboxCb)


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
    diffApp.result_table2.installEventFilter(diffApp)

    diffApp.result_table2.setSelectionBehavior(QTableWidget.SelectRows)
    diffApp.result_table1.setSelectionBehavior(QTableWidget.SelectRows)


    monospace_font = QFont("Courier New")
    diffApp.result_table1.setFont(monospace_font)
    diffApp.result_table2.setFont(monospace_font)

    grid_layout2 = QGridLayout()

    diffApp.shortestpath1 = QLineEdit(diffApp)
    diffApp.shortestpath2 = QLineEdit(diffApp)

    diffApp.currentpath1 = QLineEdit(diffApp)
    diffApp.currentpath2 = QLineEdit(diffApp)

    l = 0;

    grid_layout2.addWidget(diffApp.shortestpath1, l, 0)
    grid_layout2.addWidget(diffApp.shortestpath2, l, 1)

    diffApp.shortestpath1.textChanged.connect(diffApp.update_shortestpath1);
    diffApp.shortestpath2.textChanged.connect(diffApp.update_shortestpath2);

    l+=1;

    grid_layout2.addWidget(diffApp.currentpath1, l, 0)
    grid_layout2.addWidget(diffApp.currentpath2, l, 1)

    diffApp.currentpath1.textChanged.connect(diffApp.update_currentpath1);
    diffApp.currentpath2.textChanged.connect(diffApp.update_currentpath2);

    l+=1;

    grid_layout2.addWidget(diffApp.result_table1, l, 0)
    grid_layout2.addWidget(diffApp.result_table2, l, 1)

    def setupComboBox(comboBox, items):
        for item in items:
            comboBox.addItem(item)

    items = [CSV, BASH_ZIP_SELECTED, BASH_COPY_SELECTED_TO_CURRENT, BASH_COPY_SELECTED_TO_ANOTHER, BASH_CREATE_MD5, LSLR_ONLYSELECTED, LSLR_EXCLUDESELECTED]

    # Создаем и настраиваем первый QComboBox
    diffApp.exportSelectedAsSelectBox1 = QComboBox(diffApp)
    setupComboBox(diffApp.exportSelectedAsSelectBox1, items)

    # Создаем и настраиваем второй QComboBox
    diffApp.exportSelectedAsSelectBox2 = QComboBox(diffApp)
    setupComboBox(diffApp.exportSelectedAsSelectBox2, items)

    l+=1;

    grid_layout2.addWidget(diffApp.exportSelectedAsSelectBox1, l, 0)
    grid_layout2.addWidget(diffApp.exportSelectedAsSelectBox2, l, 1)

    diffApp.exportSelectedButton1 = QPushButton("Export", diffApp)
    diffApp.exportSelectedButton2 = QPushButton("Export", diffApp)
    diffApp.exportSelectedButton1.clicked.connect(diffApp.export_selected1)
    diffApp.exportSelectedButton2.clicked.connect(diffApp.export_selected2)

    l+=1;

    grid_layout2.addWidget(diffApp.exportSelectedButton1, l, 0)
    grid_layout2.addWidget(diffApp.exportSelectedButton2, l, 1)


    layout.addLayout(grid_layout2)
    diffApp.setLayout(layout)

