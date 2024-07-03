from PySide6 import QtCore, QtWidgets

class ClickableLabel(QtWidgets.QLabel):

    clicked = QtCore.Signal(); # Generate a custom signal for the click event

    def __init__(self, text="", parent=None):
        super().__init__(text, parent);
        self.setMouseTracking(True);
        self.installEventFilter(self);

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            self.clicked.emit();
            return True
        return False