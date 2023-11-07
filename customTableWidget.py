from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QGridLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QTableWidget, QStyledItemDelegate,QStyle
from PyQt5.QtGui import QColor, QPalette, QBrush
from PyQt5 import QtCore as qtc

class CustomItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Сохраняем оригинальный цвет текста
        original_color = index.data(qtc.Qt.ForegroundRole)
        if original_color is not None:
            if option.state & QStyle.State_Selected:
                # Устанавливаем цвет текста в зависимости от оригинального
                painter.setPen(QColor(original_color.color()))
                option.palette.setBrush(QPalette.Highlight, QBrush(QColor(0, 0, 255)))  # Синий фон
                option.palette.setBrush(QPalette.HighlightedText, QBrush(original_color.color()))
        super(CustomItemDelegate, self).paint(painter, option, index)


class CustomTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(CustomTableWidget, self).__init__(*args, **kwargs)
        self.setItemDelegate(CustomItemDelegate())
    def keyPressEvent(self, event):
        # Forward the event to the parent widget
        self.parent().customKeyPressEvent(self, event)
        super().keyPressEvent(event);
    def focusOutEvent(self, event):
        self.clearSelection()
        super(CustomTableWidget, self).focusOutEvent(event)

