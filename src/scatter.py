import logging

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import maya.cmds as cmds

log = logging.getLogger(__name__)


def maya_main_window():
    """Returns the open maya window

    Return:
        wrapInstance: the maya window as a WrapInstance object
    """
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)


class ScatterUI(QtWidgets.QDialog):
    """This class draws a scatter tool UI etc etc... write more here"""
    def __init__(self):
        super(ScatterUI, self).__init__(parent=maya_main_window())
        self.setWindowTitle("Scatter Object")
        self.setWindowFlags(self.windowFlags())


class ScatterTool(object):
    def __init__(self):
        self.scatter_target = None
        self.scatter_vertices = None
        self.scatter_obj = None
        selection = self.get_object_from_selection()
        if selection:
            self.current_sel = selection
            self.scatter_obj = self.current_sel

    def get_object_from_selection(self):
        """Retrieves object from selection to fill scatter_obj"""
        selection = cmds.ls(sl=True, transforms=True)
        if not selection or len(selection) > 1:
            om.MGlobal.displayError("Please select a polygon in Object Mode.")
            return
        return selection[0]

    def set_scatter_obj(self):
        self.scatter_obj = self.get_object_from_selection()

    def set_scatter_target(self):
        """Retrieves vertices from selection and fills scatter_target"""
        self.scatter_target = self.get_object_from_selection()
        if self.scatter_target:
            vertices = cmds.ls(
                "{}.vtx[:]".format(self.scatter_target), fl=True)
            self.scatter_vertices = vertices

    def scatter(self, percent=1.0, rotation_offset=0.0):
        """Scatters the currently filled object across selected target
        vertices list

        Return:
            String: The group name of the scattered objects
        """
        if not self.scatter_target or not self.scatter_vertices:
            om.MGlobal.displayError("Missing target or scatter object")
            return
        scattered = []
        for vert in self.scatter_vertices:
            instance = cmds.instance(self.scatter_obj)
            pos = cmds.pointPosition(vert, world=True)
            cmds.move(float(pos[0]), float(pos[1]), float(pos[2]), instance, a=True)
            scattered.append(instance[0])
        scattered_group = cmds.group(scattered, name="scattered_grp")
        return scattered_group
