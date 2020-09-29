from PySide2 import QtWidgets
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

def maya_main_window():
    """Returns the open maya window as a """
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)

class SimpleUI(QtWidgets.QDialog):
    """Docstring goes here FIX LATER"""

    def __init__(self):
        """Constructor docstring do something about"""
        super(SimpleUI, self).__init__(parent=maya_main_window())
        self.setWindowTitle("Window Title Test")


