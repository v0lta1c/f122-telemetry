from PySide6.QtWidgets import QLabel, QMenu
from PySide6.QtCore import Signal, QTimer, QTime, QPoint, Qt, QEvent

class ClickableLabel(QLabel):

    clicked = Signal(); # Generate a custom signal for the click event
    rightClicked = Signal(QPoint); # Generate a custom signal for right click

    def __init__(self, parent=None):
        super().__init__(parent);
        self.driver_position = -1;
        self.last_clicked_time = 0;
        self.initContextMenu();

    def mouseReleaseEvent(self, event: QEvent):

        #Only emit if not emitted in last 500ms
        if event.type() == QEvent.MouseButtonRelease:
            current_time = QTime.currentTime().msecsSinceStartOfDay();
            if current_time - self.last_clicked_time > 500:
                self.last_clicked_time = current_time;
                if event.button() == Qt.LeftButton:
                    self.clicked.emit();
                elif event.button() == Qt.RightButton:
                    self.rightClicked.emit(event.pos());
        super().mouseReleaseEvent(event);

    def initContextMenu(self):
        self.content_menu = QMenu(self);
    
    def setContextMenuActions(self, actions):
        self.content_menu.clear();
        for action_text, action_handler in actions.items():
            action = self.content_menu.addAction(action_text);
            action.triggered.connect(lambda _, handler=action_handler: handler(self.driver_position));

    def showContextMenu(self, pos, driver_position: int):
        self.driver_position = driver_position;
        self.content_menu.exec_(self.mapToGlobal(pos));