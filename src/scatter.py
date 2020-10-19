import logging
import random

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel

log = logging.getLogger(__name__)


def maya_main_window():
    """Returns the open maya window

    Return:
        wrapInstance: the maya window as a WrapInstance object
    """
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)


def cross(a, b):
    c = [a[1] * b[2] - a[2] * b[1],
         a[2] * b[0] - a[0] * b[2],
         a[0] * b[1] - a[1] * b[0]]
    return c


class ScatterUI(QtWidgets.QDialog):
    """This class draws a scatter tool UI etc etc... write more here"""
    def __init__(self):
        super(ScatterUI, self).__init__(parent=maya_main_window())
        self.setWindowTitle("Scatter Object")
        self.setWindowFlags(self.windowFlags())


class ScatterTool(object):
    def __init__(self, percent=1.0, rotation=0.0, scale=0.0):
        self.scatter_target = None
        self.scatter_vertices = None
        self.scatter_obj = None
        # TODO these variables need better names
        self.scatter_percent = percent
        self.rotation_offset = rotation
        self.scale_offset = scale
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

    def scatter(self):
        """Scatters the target object across vertices list

        Return:
            String: The group name of the scattered objects
        """
        scattered = []
        sampled_vertices = self.sample_scatter_points()
        for vert in sampled_vertices:
            instance = cmds.instance(self.scatter_obj)
            pos = cmds.pointPosition(vert, world=True)

            # calculating the vertex normals
            cmds.select(vert, r=True)
            vtx_normals = cmds.polyNormalPerVertex(query=True, xyz=True)
            avg_normal = self.average_normals(vtx_normals)
            transform_matrix = self.get_matrix_from_normal(avg_normal, pos)

            # applying transformations
            cmds.select(instance[0], r=True)
            cmds.move(pos[0], pos[1], pos[2], a=True)
            cmds.xform(ws=True, matrix=transform_matrix)

            # applying extra rotation
            extra_rot = self.random_rotation_offset()
            cmds.rotate(extra_rot[0], extra_rot[1], extra_rot[2], r=True)

            # applying random scale
            random_scale = self.random_scale(instance[0])
            cmds.setAttr("{}.scale".format(instance[0]), random_scale[0],
                         random_scale[1], random_scale[2])

            # list to group
            scattered.append(instance[0])
        scattered_group = cmds.group(scattered, name="scattered_grp")
        return scattered_group

    def sample_scatter_points(self):
        if self.scatter_percent < 1:
            sample_size = int(len(self.scatter_vertices) * self.scatter_percent)
            sampled = random.sample(self.scatter_vertices, sample_size)
            return sampled
        else:
            return self.scatter_vertices

    def random_rotation_offset(self):
        rotation_xyz = [0.0, 0.0, 0.0]
        if self.rotation_offset > 0:
            rotation_range = self.rotation_offset * 180
            for counter in range(len(rotation_xyz)):
                offset = random.uniform(-rotation_range, rotation_range)
                rotation_xyz[counter] = offset
        return rotation_xyz

    def random_scale(self, obj):
        new_scale = [1.0, 1.0, 1.0]
        if self.scale_offset > 0:
            ran_scale = random.uniform(-self.scale_offset, self.scale_offset)
            obj_scale = cmds.getAttr("{}.scale".format(obj))[0]
            for counter in range(len(obj_scale)):
                new_scale[counter] = new_scale[counter] * (1.0 + ran_scale)
        return new_scale

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

    def get_matrix_from_normal(self, normal_xyz, position):
        """Converts averaged normal vectors to rotation eulers

        Return:
            List: A list representing a 16 item matrix
        """
        # TODO need to convert the normal to world space,
        # will fix numerous problems
        tangent_1 = cross(normal_xyz, [0, 1, 0])
        tangent_2 = cross(normal_xyz, tangent_1)
        matrix = [tangent_2[0], tangent_2[1], tangent_2[2], 0.0,
                  normal_xyz[0], normal_xyz[1], normal_xyz[2], 0.0,
                  tangent_1[0], tangent_1[1], tangent_1[2], 0.0,
                  position[0], position[1], position[2], 1.0]
        return matrix

    def world_normal_from_local(self, normal, vertex):
        """Converts a normal vector to world space

        Return:
            List: a list representing a normal vector
        """
        parent_shape = cmds.listRelatives(vertex, parent=True)
        parent_transform = cmds.listRelatives(parent_shape[0], parent=True)
        matrix = cmds.xform(parent_transform[0], q=True, m=True, ws=True)


