import logging
import random

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
        print("Object: " + self.scatter_obj)

    def set_scatter_target(self):
        """Retrieves vertices from selection and fills scatter_target"""
        self.scatter_target = self.get_object_from_selection()
        print("Target: " + self.scatter_target)
        if self.scatter_target:
            vertices = cmds.ls(
                "{}.vtx[:]".format(self.scatter_target), fl=True)
            self.scatter_vertices = vertices

    def scatter(self, vertex_percent=1.0, rotation_offset=0.0):
        """Scatters the currently filled object across selected target
        vertices list

        Return:
            String: The group name of the scattered objects
        """
        if not self.scatter_target or not self.scatter_vertices:
            om.MGlobal.displayError("Missing target or scatter object")
            return
        scattered = []
        if vertex_percent < 1:
            sample = int(len(self.scatter_vertices) * vertex_percent)
            self.scatter_vertices = random.sample(self.scatter_vertices,
                                                  sample)
        rotation_offset = rotation_offset * 180
        for vert in self.scatter_vertices:
            # TODO find out why instance returns as a tuple
            instance = cmds.instance(self.scatter_obj)
            pos = cmds.pointPosition(vert, world=True)
            cmds.move(pos[0], pos[1], pos[2], instance, a=True)
            scattered.append(instance[0])
            cmds.select(vert, r=True)
            vtx_normals = cmds.polyNormalPerVertex(query=True, xyz=True)
            avg_normal = self.average_normals(vtx_normals)
            # calculate rotation xyz from the computed normal

            # transform the instance to that rotation value

            # apply rotation offset
            cmds.select(instance[0], r=True)
            x_offset = random.uniform(-rotation_offset, rotation_offset)
            print(x_offset)
            y_offset = random.uniform(-rotation_offset, rotation_offset)
            print(y_offset)
            z_offset = random.uniform(-rotation_offset, rotation_offset)
            print(z_offset)
            cmds.rotate(x_offset, y_offset, z_offset, r=True)
        scattered_group = cmds.group(scattered, name="scattered_grp")
        return scattered_group

    def average_normals(self, normal_list):
        """Calculates the average normal of a set of normal values given in
        a successive list

        Return:
            List: A list of normal values x, y, and z"""
        normal_xyz = []
        for outer_count in range(3):
            dir_sum = 0
            dir_count = len(normal_list) // 3
            for inner_count in range(dir_count):
                coord_iterator = outer_count + (3 * inner_count)
                dir_sum = dir_sum + normal_list[coord_iterator]
            normal_xyz.append(dir_sum / dir_count)
        return normal_xyz

    def set_rotation_from_normal(self, normal_xyz):
        """Converts averaged normal vectors to rotation eulers

        Return:
            List: A list of rotation values x, y, and z"""
        # rotation_list = []
        # for counter in range(3):
        #   if normal_xyz[counter] < 0:
        #       rotation_modifier = -180
        #    else:
        #        rotation_modifier = 180
        #    normal_xyz[counter] = normal_xyz[counter] * rotation_modifier
        #    rotation_list.append(normal_xyz[counter])

        return [0, 0, 0]
