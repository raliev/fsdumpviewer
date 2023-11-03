import re
import sys
from collections import OrderedDict

from PyQt5.QtCore import QEvent
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtWidgets import QTableWidgetItem
from parser import parser
from docompare import compare
from setupUI import setupUI, CSV, BASH_ZIP_SELECTED, BASH_COPY_SELECTED_TO_CURRENT, BASH_COPY_SELECTED_TO_ANOTHER
from structure_manipulations import add_marks_to_all_folders, get_last_element, remove_last_folder;
import shlex


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

    def exportCSV(self, lines, exportFileName):
        with open(exportFileName, "w", encoding="utf-8") as file:
            for line in lines:
                file.write(line + "\n")

    def produceFilesForExport(self, directories, path, any=0):
        selected_files = []
        if directories.get(path) is None or directories[path].get('files') is None:
            print ("unexpected: "+path+" doesn't exist in the memory structures (or path -> files)")
            return selected_files;
        for filename, file_info in directories[path]['files'].items():
            if file_info['selected'] == 1 or any:
                if not file_info['permissions'].startswith('d'):
                    file_to_export = path + filename
                    selected_files.append(file_to_export)
                else:
                    selected_files.extend(self.produceFilesForExport(directories, path + filename + "/", any=1))
            else:
                if file_info['permissions'].startswith('d'):
                    selected_files.extend(self.produceFilesForExport(directories, path + filename + "/", any=0))
        return selected_files;

    def export_zip_commands(self, selected_files, export_file_name, group_size):
        with open(export_file_name, "w", encoding="utf-8") as file:
            for i in range(0, len(selected_files), group_size):
                group_files = [shlex.quote(file) for file in selected_files[i:i+group_size]]
                zip_command = f"zip myzip.zip {' '.join(group_files)}\n"
                file.write(zip_command)
                print(zip_command.strip())

    def exportZIPSelected(self, lines, exportFileName):
        self.export_zip_commands(lines, exportFileName, 10)

    def exportCopySelectedToCurrent(self, lines, exportFileName):
        with open(exportFileName, "w", encoding="utf-8") as file:
            for line in lines:
                file.write("cp " + shlex.quote(line) + " .\n")

    def exportCopySelectedToAnotherPanel(self, lines, exportFileName, anotherPanelNo):
        with open(exportFileName, "w", encoding="utf-8") as file:
            for line in lines:
                ourPanelSelectedPath = self.shortest_path1;
                anotherPanelSelectedPath = self.shortest_path2;
                if (anotherPanelNo == 1) :
                    ourPanelSelectedPath = self.shortest_path2;
                    anotherPanelSelectedPath = self.shortest_path1;
                targetLocation = anotherPanelSelectedPath + line.removeprefix(ourPanelSelectedPath)
                file.write("cp " + shlex.quote(line) + " " + shlex.quote(targetLocation) + "\n")
    def export(self, directories, exportFileName, mode, shortest_path, panelNo):
        selected_files = self.produceFilesForExport(directories, shortest_path, any=0)
        if mode == CSV:
            self.exportCSV(selected_files, exportFileName)
        if mode == BASH_ZIP_SELECTED:
            self.exportZIPSelected(selected_files, exportFileName)
        if mode == BASH_COPY_SELECTED_TO_CURRENT:
            self.exportCopySelectedToCurrent(selected_files, exportFileName)
        if mode == BASH_COPY_SELECTED_TO_ANOTHER:
            anotherPanel = 2;
            if panelNo == 2:
                anotherPanel = 1;
            self.exportCopySelectedToAnotherPanel(selected_files, exportFileName, anotherPanel)

    def askForFileName(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,
                                                  "QFileDialog.getSaveFileName()",
                                                  "", # Стартовый путь
                                                  "All Files (*);;Text Files (*.txt)", # Фильтры для форматов файлов
                                                  options=options)
        if fileName:
            print(f"Save file name: {fileName}")
            return fileName;
        return None;
    def export_selected2(self):
        fileName = self.askForFileName()
        if fileName is not None:
            self.export(self.text2Struct, fileName, self.exportSelectedAsSelectBox2.currentText(), self.shortest_path2, panelNo=2);

    def export_selected1(self):
        fileName = self.askForFileName()
        if fileName is not None:
            self.export(self.text1Struct, fileName, self.exportSelectedAsSelectBox1.currentText(), self.shortest_path1, panelNo=1);

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
            self.update_currentpath1(sel_path);
            self.update_currentpath1_inputbox(sel_path);
        if (source == self.result_table2):
            self.update_currentpath2(sel_path);
            self.update_currentpath2_inputbox(sel_path);

    def tableSpecificData(self, source):
        sel_path = None;
        result_table = None;
        textStruct = None;
        if (source == self.result_table1):
            textStruct = self.text1Struct;
            sel_path = self.selected_path1;
            self.update_currentpath1_inputbox(self.selected_path1)
            result_table = self.result_table1;
        if (source == self.result_table2):
            textStruct = self.text2Struct;
            sel_path = self.selected_path2;
            self.update_currentpath2_inputbox(self.selected_path2)
            result_table = self.result_table2;
        return sel_path, textStruct, result_table;

    def synchronize_panels(self, source_table):
        if self.syncPanels.isChecked():
            print("Synchronizing...")
            target_table = self.result_table2 if source_table == self.result_table1 else self.result_table1
            another_panel_data = self.fetch_table_specific_data(target_table)

            self.print_selected_path(another_panel_data['selected_path'])
            constructed_path = self.construct_path(source_table, another_panel_data['shortest_path'])
            self.print_constructed_path(constructed_path)

            if self.is_path_valid(another_panel_data['text_struct'], constructed_path):
                self.update_selected_path(source_table, constructed_path)
                self.populate_table(target_table, another_panel_data['text_struct'], constructed_path)

    def fetch_table_specific_data(self, result_table):
        return self.tableSpecificData(result_table)

    def print_selected_path(self, path):
        print(f"Selected path={path}")

    def print_constructed_path(self, path):
        print(f"Constructed path={path}")

    def construct_path(self, source_table, shortest_path):
        source_selected_path = self.selected_path1 if source_table == self.result_table1 else self.selected_path2
        source_shortest_path = self.shortest_path1 if source_table == self.result_table1 else self.shortest_path2
        if source_selected_path.startswith(source_shortest_path):
            return shortest_path + source_selected_path.removeprefix(source_shortest_path)
        return source_selected_path

    def is_path_valid(self, text_struct, path):
        return text_struct.get(path) and text_struct[path].get('files')

    def update_selected_path(self, source_table, constructed_path):
        if source_table == self.result_table1:
            self.selected_path2 = constructed_path
            self.update_currentpath2_inputbox(self.selected_path2)
        else:
            self.selected_path1 = constructed_path
            self.update_currentpath1_inputbox(self.selected_path1)

    def populate_table(self, result_table, text_struct, path):
        self.add_dir_contents(result_table, text_struct, path)

    def synchronize_panel(self, numPanel):
        if numPanel == 1:
            ourpath, theirpath, ourshortestpath, theirshortestpath, theirtable = (self.selected_path1, self.selected_path2,
                                                                                  self.shortest_path1, self.shortest_path2,
                                                                                  self.result_table2
                                                                                  )
        if numPanel == 2:
            ourpath, theirpath, ourshortestpath, theirshortestpath, theirtable = (self.selected_path2, self.selected_path1,
                                                                                  self.shortest_path2, self.shortest_path1,
                                                                                  self.result_table1
                                                                                  )
        anotherPanel_selected_path, anotherPanel_textStruct, anotherPanel_result_table = self.tableSpecificData(theirtable)
        constructedPath = ourpath;
        if constructedPath.startswith(ourshortestpath):
            constructedPath = theirshortestpath + constructedPath.removeprefix(ourshortestpath);
        if anotherPanel_textStruct.get(constructedPath) is not None:
            if anotherPanel_textStruct[constructedPath]['files'] is not None:
                if numPanel == 1:
                    self.selected_path2 = constructedPath;
                    self.update_currentpath2_inputbox(self.selected_path2)
                    self.add_dir_contents(anotherPanel_result_table, anotherPanel_textStruct, self.selected_path2);

            if numPanel == 2:
                    self.selected_path1 = constructedPath;
                    self.update_currentpath1_inputbox(self.selected_path1)
                    self.add_dir_contents(anotherPanel_result_table, anotherPanel_textStruct, self.selected_path1);

    def customKeyPressEvent(self, source_table, event):

        selected_path, textStruct, result_table = self.tableSpecificData(source_table)
        current_item = result_table.currentItem()
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Получите текущую выбранную ячейку
            current_item = result_table.currentItem()
            if current_item:
                row = current_item.row()
                self.refresh_table(result_table, current_item);

                if self.syncPanels.checkState() == Qt.Checked:
                    print("synchronizing...")

                    if source_table == self.result_table1:
                        self.synchronize_panel(1)
                    if source_table == self.result_table2:
                        self.synchronize_panel(2)



                # event.accept()
                return;
        elif event.key() == Qt.Key_Space:
            if current_item:
                self.handle_select(result_table, textStruct, selected_path, current_item);
                # event.accept()
                return;

        super().keyPressEvent(event)

    def docompare(self):

        config = {
            'compare_names': True,
            'compare_sizes': self.compare_sizes.checkState() == Qt.Checked,
            'compare_dates': self.compare_modiftime.checkState() == Qt.Checked,
            'compare_checksums': self.compare_checksums.checkState() == Qt.Checked,
            'compare_specialmark': self.compare_specialmark.checkState() == Qt.Checked
        }

        compare(self.selected_path1, self.selected_path2, self.text1Struct, self.text2Struct, config)
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

            if folder == ".":
                #this is not a valid directory
                return;

            if folder != ".." and not textStruct[selected_path]['files'][folder]['permissions'].startswith("d") :
                #this is not a directory
                return;

            was_it_selected = -1;

            if folder != ".." and textStruct[selected_path]['files'][folder]['autoselected'] != 1:
              was_it_selected = textStruct[selected_path]['files'][folder]['selected']

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
                   print ("textStruct["+selected_path+"]['files']["+file_info['filename']+"]['autoselected']=" +  str(was_it_selected) )
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
            if current_item.text() != "..":
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
            # Разделяем элементы на поддиректории и файлы
            dirs = []
            files = []

            print(path,content);

            if content.get('files') is None:
                continue;
            for filename, file_info in content['files'].items():
                if file_info['permissions'].startswith('d'):
                    dirs.append((filename, file_info))
                else:
                    files.append((filename, file_info))

            # Сортируем поддиректории и файлы отдельно
            sorted_dirs = OrderedDict(sorted(dirs))
            sorted_files = OrderedDict(sorted(files))

            # Объединяем отсортированные поддиректории и файлы в один список
            sorted_all = OrderedDict(list(sorted_dirs.items()) + list(sorted_files.items()))

            sorted_directories[path] = {
                'files': sorted_all,
                'size': content['size']
            }

        return sorted_directories

    def removeIgnored(self, textStruct, regexp):
        # Компилируем регулярное выражение заранее для повышения производительности
        if (regexp == ""):
             return;
        patternSome = re.compile(regexp)


        # Функция для рекурсивного удаления элементов, подходящих под регулярное выражение

        def remove_items(directories, path, pattern):
            patternAll = re.compile(".*")
            paths_to_remove = []  # Список путей для удаления
            path1 = path;
            if (pattern == patternSome):
                while (path1 != "/" and path1 != "./"):
                    lastComponent = get_last_element(path1);
                    if directories.get(path1) is not None:
                        if pattern.match(lastComponent):
                            paths_to_remove.append((path1, ""));
                            remove_items(directories, path1, patternAll)
                    path1 = remove_last_folder(path1);


            for filename, file_info in directories.get(path, {}).get('files', {}).items():
                if pattern.match(filename):
                    # Если имя файла или директории подходит под регулярное выражение, помечаем для удаления
                    paths_to_remove.append((path, filename))
                    if file_info['permissions'].startswith('d'):
                        subpath = path + filename + "/"
                        print("removing subfolders..." + subpath)
                        paths_to_remove.append((subpath, ""));

                        remove_items(directories, subpath, patternAll)

            # Удаляем файлы и папки, помеченные для удаления
            for path, filename in paths_to_remove:
                if filename == "":
                    print ("deleting dir "+path)
                    if directories.get(path) is  None:
                        continue;
                    del directories[path];
                    continue;
                if path:
                    # Удаление файла или папки в поддиректории
                    print("deleting "+path + filename)
                    if directories.get(path) is  None or directories[path].get('files') is None or directories[path]['files'].get(filename) is None:
                            continue;
                    del directories[path]['files'][filename]
                else:
                    # Удаление файла или папки в корневом каталоге

                    print("deleting "+path + filename)

                    del directories['files'][filename]

        # Запускаем процесс удаления на корневом уровне структуры
        for path in list(textStruct.keys()):
            remove_items(textStruct, path, patternSome)


    def process_raw_data(self):

        #text1 = self.text_area1.toPlainText().splitlines()
        #text2 = self.text_area2.toPlainText().splitlines()

        if (self.file_path1.text() is not None):
            text1 = self.read_file_content(self.file_path1)
            self.selected_path1, self.text1Struct = parser(text1);
            self.shortest_path1 = self.selected_path1;
            self.update_currentpath1_inputbox(self.selected_path1)
            self.removeIgnored(self.text1Struct, self.ignoreRegexp.text());
            self.text1Struct = self.sort_by_name(self.text1Struct)
            self.add_dir_contents(self.result_table1, self.text1Struct, self.selected_path1);

        if (self.file_path2.text() != ""):
            text2 = self.read_file_content(self.file_path2)
            self.selected_path2,self.text2Struct = parser(text2);
            self.shortest_path2 = self.selected_path2;
            self.update_currentpath2_inputbox(self.selected_path2)
            self.removeIgnored(self.text2Struct, self.ignoreRegexp.text());
            self.text2Struct = self.sort_by_name(self.text2Struct)
        self.add_dir_contents(self.result_table2, self.text2Struct, self.selected_path2);


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

                if file_info['selectedSpecialMark'] > 0:
                    item.setForeground(QBrush(QColor(0, 255, 255)))

                if file_info.get('autoselected') is not None and file_info['autoselected'] > 0:
                    item.setForeground(QBrush(QColor(128, 0, 0)))

                rowCnt += 1
                result_table.setRowCount(rowCnt)
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

    def update_shortestpath1(self, var):
        self.shortest_path1 = var;
    def update_shortestpath2(self, var):
        self.shortest_path2 = var;
    def update_currentpath1(self, var):
        self.selected_path1 = var;
    def update_currentpath2(self, var):
        self.selected_path2 = var;

    def update_currentpath1_inputbox(self, new_value):
        self.currentpath1.textChanged.disconnect()
        self.currentpath1.setText(new_value)
        self.currentpath1.textChanged.connect(self.update_currentpath1)
    def update_currentpath2_inputbox(self, new_value):
        self.currentpath2.textChanged.disconnect()
        self.currentpath2.setText(new_value)
        self.currentpath2.textChanged.connect(self.update_currentpath2)
    def update_shortestpath1_inputbox(self, new_value):
        self.currentpath1.textChanged.disconnect()
        self.currentpath1.setText(new_value)
        self.currentpath1.textChanged.connect(self.update_shortestpath1)
    def update_shortestpath2_inputbox(self, new_value):
        self.currentpath2.textChanged.disconnect()
        self.currentpath2.setText(new_value)
        self.currentpath2.textChanged.connect(self.update_shortestpath2)

app = QApplication(sys.argv)
window = DiffApp(sys.argv)
window.show()
sys.exit(app.exec_())
