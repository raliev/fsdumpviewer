import sys
from collections import OrderedDict

from PyQt5.QtCore import QEvent
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtWidgets import QTableWidgetItem

from docompare import compare
from ls_lR_macOSParser import preprocessStructure as ls_lR_macOSParser_preprocessStructure;
from ls_lR_macOSParser2 import preprocessStructure as ls_lR_macOSParser2_preprocessStructure;
from setupUI import setupUI
from structure_manipulations import add_marks_to_all_folders;

text1 = None
text2 = None


class DiffApp(QWidget):
    text1Struct = {}
    text2Struct = {}

    selected_path1 = "./"
    selected_path2 = "./"

    #    selected_path1 = "c:/Windows/"

    def __init__(self, argv):
        super().__init__()
        setupUI(self, argv)

    def setFocusTo(self, widget):
        widget.setFocus()

    def eventFilter(self, source, event):
        if (source == self.result_table1 or source == self.result_table2) and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                if source == self.result_table1:
                    self.setFocusTo(self.result_table2)
                    return True
                if source == self.result_table2:
                    self.setFocusTo(self.result_table1)
                    return True
            if event.key() == Qt.Key_Space:
                result_table = source
                current_item = result_table.currentItem()
                # print("spacebar pressed")
                # print(current_item);
                if current_item:
                    selected_path, textStruct, result_table = self.tableSpecificData(source)
                    event.source = source;
                    self.handle_select(source, textStruct, selected_path, current_item);
                return True
        return super().eventFilter(source, event)

    def setTableSpecificData(self, source, sel_path):
        if (source == self.result_table1):
            self.selected_path1 = sel_path;
        if (source == self.result_table2):
            self.selected_path2 = sel_path;

    def tableSpecificData(self, source):
        sel_path = None;
        result_table = None;
        textStruct = None;
        if (source == self.result_table1):
            textStruct = self.text1Struct;
            sel_path = self.selected_path1;
            result_table = self.result_table1;
        if (source == self.result_table2):
            textStruct = self.text2Struct;
            sel_path = self.selected_path2;
            result_table = self.result_table2;
        return sel_path, textStruct, result_table;

    def customKeyPressEvent(self, source_table, event):

        selected_path, textStruct, result_table = self.tableSpecificData(source_table)
        current_item = result_table.currentItem()
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Получите текущую выбранную ячейку
            current_item = result_table.currentItem()
            if current_item:
                self.refresh_table(result_table, current_item);
                # event.accept()
                return;
        elif event.key() == Qt.Key_Space:
            if current_item:
                self.handle_select(result_table, textStruct, selected_path, current_item);
                # event.accept()
                return;

        super().keyPressEvent(event)

    def docompare(self):
        compare(self.text1Struct, self.text2Struct)
        self.add_dir_contents(self.result_table1, self.text1Struct, self.selected_path1);
        self.add_dir_contents(self.result_table2, self.text2Struct, self.selected_path2);

    def remove_last_folder(self, path: str) -> str:
        parts = path.split('/')
        parts = parts[:-2] if parts[-1] == '' else parts[:-1]
        return '/'.join(parts) + '/'

    def get_last_element(self, path: str) -> str:
        parts = path.split('/')
        if parts[-1] == '':
            return parts[-2]
        else:
            return parts[-1]

    def refresh_table(self, result_table, current_item):
        selected_path, textStruct, result_table = self.tableSpecificData(result_table)

        if current_item:
            row = current_item.row()
            folder = result_table.item(row, 0).text();
            was_it_selected = -1;
            if folder != "..":
              was_it_selected = textStruct[selected_path]['files'][folder]['selected'];
            #print("was it selected:"+str(was_it_selected));
            # print(folder);
            at_least_one_selected = 0;
            if folder == "..":
                for file_info in textStruct[selected_path]['files'].values():
                    if textStruct[selected_path]['files'][file_info['filename']]['autoselected'] == 1:
                        at_least_one_selected = 1;
                    if textStruct[selected_path]['files'][file_info['filename']]['selected'] == 1:
                        at_least_one_selected = 1;
                    if textStruct[selected_path]['files'][file_info['filename']]['childselected'] == 1:
                        at_least_one_selected = 1;
                folder_to_select = self.get_last_element(selected_path);
                selected_path = self.remove_last_folder(selected_path)

            else:
                folder_to_select = "..";
                selected_path = selected_path + folder + "/";

            self.setTableSpecificData(result_table, selected_path)

            if was_it_selected != -1 and textStruct.get(selected_path) is not None:
                for file_info in textStruct[selected_path]['files'].values():
                   textStruct[selected_path]['files'][file_info['filename']]['autoselected'] = was_it_selected;
            if at_least_one_selected == 1 and folder_to_select != "..":
                textStruct[selected_path]['files'][folder_to_select]['autoselected'] = 1;

            # print("selected_path="+selected_path)

            self.add_dir_contents(result_table, textStruct, selected_path);
            self.set_cursor_to(result_table, folder_to_select);

    def set_cursor_to(self, result_table, foldername):
        rows = result_table.rowCount()
        for i in range(rows):
            item = result_table.item(i, 0)
            if item and foldername == item.text():
                result_table.setCurrentCell(i, 0)
                break

    def set_cursor_to_row(self, result_table, row):
        if (row < result_table.rowCount()):
            result_table.setCurrentCell(row, 0)

    def handle_select(self, result_table, textStruct, selected_path, current_item):

        if current_item:
            row = current_item.row()
            filename = result_table.item(row, 0).text();
            item = result_table.item(row, 0)
            # print(selected_path + filename);
            current_status = textStruct[selected_path]['files'][filename]['selected'];
            # print("current_status is "+str(current_status));
            if current_status == 0:
                textStruct[selected_path]['files'][filename]['selected'] = 1;
                add_marks_to_all_folders(textStruct, selected_path, 1);
                item.setForeground(QBrush(QColor(255, 0, 0)))
            else:
                textStruct[selected_path]['files'][filename]['selected'] = 0;
                add_marks_to_all_folders(textStruct, selected_path, -1);
                item.setForeground(QBrush(QColor(255, 255, 255)))
        self.set_cursor_to_row(result_table, row + 1);

    def read_file_content(self, file_path_widget):
        file_path = file_path_widget.text()  # Получение пути к файлу из QLineEdit
        try:
            with open(file_path, 'r') as file:
                return file.read();
        except Exception as e:  # Обработка ошибок, таких как неверный путь или проблемы с правами доступа
            print(f"Error reading file {file_path}: {e}")
            return []

    def sort_by_name(self,directories):
        sorted_directories = {}

        for path, content in directories.items():
            sorted_files = OrderedDict(sorted(content['files'].items()))

            sorted_directories[path] = {
                'files': sorted_files,
                'size': content['size']
            }

        return sorted_directories


    def process_raw_data(self):

        #text1 = self.text_area1.toPlainText().splitlines()
        #text2 = self.text_area2.toPlainText().splitlines()

        selected_path1 = "./";
        selected_path2 = "./";

        if (self.file_path1.text() is not None):
            text1 = self.read_file_content(self.file_path1)
            self.text1Struct = ls_lR_macOSParser_preprocessStructure(text1);
            self.text1Struct = self.sort_by_name(self.text1Struct)
            self.add_dir_contents(self.result_table1, self.text1Struct, selected_path1);

        if (self.file_path2.text() != ""):
            text2 = self.read_file_content(self.file_path2)
            self.text2Struct = ls_lR_macOSParser2_preprocessStructure(text2);
            self.text2Struct = self.sort_by_name(self.text2Struct)
        self.add_dir_contents(self.result_table2, self.text2Struct, selected_path2);


    def add_dir_contents(self, result_table, directories, dir_path):
        result_table.clearContents()
        result_table.setRowCount(1000)
        rowCnt = 0
        if dir_path != "./" and not dir_path.endswith(":/"):
            dirsize = 0;

            if directories.get(dir_path) is not None and directories[dir_path].get('size') is not None:
                dirsize = directories[dir_path]['size'];

            result_table.setItem(rowCnt, 0, QTableWidgetItem(f".."))
            result_table.setItem(rowCnt, 1, QTableWidgetItem(f"{dirsize}"))
            result_table.setItem(rowCnt, 2, QTableWidgetItem(f""))
            item = result_table.item(rowCnt, 0)
            rowCnt += 1;

        if (directories.get(dir_path) is not None):
            for file_info in directories[dir_path]['files'].values():
                # print("file info =")
                # print(file_info)
                result_table.insertRow(rowCnt)
                if (file_info['permissions'].startswith("d")):
                    dirsize = "NA";
                    dirinf = directories.get(dir_path + file_info['filename'] + "/");
                    if dirinf is not None:
                        dirsize = dirinf.get('size');
                    result_table.setItem(rowCnt, 0, QTableWidgetItem(f"{file_info['filename']}"))
                    result_table.setItem(rowCnt, 1, QTableWidgetItem(f"{dirsize}"))
                    result_table.setItem(rowCnt, 2, QTableWidgetItem(f"{file_info['permissions']}"))
                    item = result_table.item(rowCnt, 0)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                else:
                    # print("adding a line with "+file_info['filename'])
                    result_table.setItem(rowCnt, 0, QTableWidgetItem(f"{file_info['filename']}"))
                    result_table.setItem(rowCnt, 1, QTableWidgetItem(f"{file_info['size']}"))
                    result_table.setItem(rowCnt, 2, QTableWidgetItem(f"{file_info['permissions']}"))

                item = result_table.item(rowCnt, 0)
                item.setForeground(QBrush(QColor(255, 255, 255)))

                if file_info.get('childselected') is not None and file_info.get('childselected') > 0:
                    item.setForeground(QBrush(QColor(0, 255, 0)))

                if file_info['selected'] > 0:
                    item.setForeground(QBrush(QColor(255, 0, 0)))

                if file_info.get('autoselected') is not None and file_info['autoselected'] > 0:
                    item.setForeground(QBrush(QColor(128, 0, 0)))

                rowCnt += 1
                #result_table.setRowCount(rowCnt)
    def select_file(self, line_edit):
        file_name, _ = QFileDialog.getOpenFileName(self)
        if file_name:
            line_edit.setText(file_name)
    def resizeEvent(self, event):

        super().resizeEvent(event)

        width1 = int(self.result_table1.width() * 0.7);
        width2 = int(self.result_table1.width() * 0.15);
        self.result_table1.setColumnWidth(0, width1)
        self.result_table1.setColumnWidth(1, width2)

        width1 = int(self.result_table2.width() * 0.7);
        width2 = int(self.result_table2.width() * 0.15);
        self.result_table2.setColumnWidth(0, width1)
        self.result_table2.setColumnWidth(1, width2)


app = QApplication(sys.argv)
window = DiffApp(sys.argv)
window.show()
sys.exit(app.exec_())
