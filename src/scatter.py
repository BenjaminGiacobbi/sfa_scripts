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
        self.setWindowTitle("Scatter Tool")
        self.setWindowFlags(self.windowFlags())
        self.setMaximumWidth(750)
        self.scatter_tool = ScatterTool()
        self._create_ui()
        self._create_connections()

    def _create_ui(self):
        self.obj_lbl = QtWidgets.QLabel("Scatter Objects")
        self.obj_lbl.setStyleSheet("font: 20px")
        self.obj_layout = QtWidgets.QVBoxLayout()
        self.obj_layout.addWidget(self.obj_lbl)
        self.obj_layout.addLayout(self._create_object_ui())
        self.mod_lbl = QtWidgets.QLabel("Modifiers")
        self.mod_lbl.setStyleSheet("font: 20px")
        self.mod_layout = QtWidgets.QVBoxLayout()
        self.mod_layout.addWidget(self.mod_lbl)
        self.mod_layout.addLayout(self._create_modifier_ui())
        self.scatter_btn_layout = self._create_button_ui()
        self.main_lay = QtWidgets.QVBoxLayout()
        self.main_lay.addLayout(self.obj_layout)
        self.main_lay.addStretch()
        self.main_lay.addLayout(self.mod_layout)
        self.main_lay.addLayout(self.scatter_btn_layout)
        self.setLayout(self.main_lay)

    def _create_object_ui(self):
        self.obj_le = QtWidgets.QLineEdit()
        self.obj_le.setMinimumWidth(200)
        self.obj_le.setMinimumHeight(30)
        self.obj_le.setPlaceholderText("Object to scatter")
        self.obj_le.setEnabled(False)
        self.target_le = QtWidgets.QLineEdit()
        self.target_le.setMinimumWidth(200)
        self.target_le.setMinimumHeight(30)
        self.target_le.setEnabled(False)
        self.target_le.setPlaceholderText("Object to target")
        self.obj_btn = QtWidgets.QPushButton("Get From Selection")
        self.target_btn = QtWidgets.QPushButton("Get From Selection")
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.obj_le, 0, 0)
        layout.addWidget(self.target_le, 0, 2)
        layout.addWidget(self.obj_btn, 1, 0)
        layout.addWidget(self.target_btn, 1, 2)
        return layout

    def _create_modifier_ui(self):
        # TODO break this up, it's too big, maybe do each row
        self.rotation_sbx = QtWidgets.QSpinBox()
        self.rotation_sbx.setValue(int(self.scatter_tool.rot_offset * 100))
        self.rotation_sbx.setSuffix("%")
        self.rotation_sbx.setMaximumWidth(50)
        self.scale_sbx = QtWidgets.QSpinBox()
        self.scale_sbx.setValue(int(self.scatter_tool.rot_offset * 100))
        self.scale_sbx.setSuffix("%")
        self.scale_sbx.setMaximumWidth(50)
        self.sample_sbx = QtWidgets.QSpinBox()
        self.sample_sbx.setValue(int(self.scatter_tool.scatter_percent * 100))
        self.sample_sbx.setSuffix("%")
        self.sample_sbx.setMaximumWidth(50)
        self.orient_cbx = QtWidgets.QCheckBox()
        self.orient_cbx.setChecked(True)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel("Rotation Offset Range"), 0, 0)
        layout.addWidget(self.rotation_sbx, 0, 2)
        layout.addWidget(QtWidgets.QLabel("Scale Offset Range"), 0, 4)
        layout.addWidget(self.scale_sbx, 0, 6)
        layout.addWidget(QtWidgets.QLabel("Vertex Percent to Scatter"), 1, 0)
        layout.addWidget(self.sample_sbx, 1, 2)
        layout.addWidget(QtWidgets.QLabel("Orient to Normals"), 1, 4)
        layout.addWidget(self.orient_cbx, 1, 6)
        return layout

    def _create_button_ui(self):
        self.scatter_btn = QtWidgets.QPushButton("Scatter")
        self.scatter_btn.setStyleSheet("font-size: 20px")
        self.scatter_btn.setEnabled(False)
        self.scatter_btn.setMaximumWidth(300)
        self.scatter_btn.setMaximumHeight(100)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.scatter_btn)
        return layout

    def _create_connections(self):
        self.obj_btn.clicked.connect(self._select_obj)
        self.target_btn.clicked.connect(self._select_target)
        self.scatter_btn.clicked.connect(self._scatter)

    @QtCore.Slot()
    def _select_obj(self):
        self.scatter_tool.set_scatter_obj()
        if self.scatter_tool.scatter_obj:
            self.obj_le.setText(self.scatter_tool.scatter_obj)
        else:
            om.MGlobal.displayWarning("Couldn't find object to scatter. "
                                      "Select one object and press "
                                      "\"Get From Selection\"")
        self._update_scatter_btn_state()

    @QtCore.Slot()
    def _select_target(self):
        self.scatter_tool.set_scatter_target()
        if self.scatter_tool.scatter_target:
            self.target_le.setText(self.scatter_tool.scatter_target)
        else:
            om.MGlobal.displayWarning("Couldn't find target object. Select "
                                      "one object and press \"Get From "
                                      "Selection\"")
        self._update_scatter_btn_state()

    @QtCore.Slot()
    def _scatter(self):
        self.scatter_tool.scatter_percent = float(self.sample_sbx.value()) / 100
        self.scatter_tool.scale_offset = float(self.scale_sbx.value()) / 100
        self.scatter_tool.rot_offset = float(self.rotation_sbx.value()) / 100
        self.scatter_tool.align = self.orient_cbx.isChecked()
        self.scatter_tool.scatter()

    def _update_scatter_btn_state(self):
        if self.scatter_tool.scatter_obj and self.scatter_tool.scatter_target:
            self.scatter_btn.setEnabled(True)
        else:
            self.scatter_btn.setEnabled(False)


class ScatterTool(object):
    def __init__(self):
        self.scatter_target = None
        self.scatter_vertices = None
        self.scatter_obj = None
        self.scatter_percent = 1.0
        self.rot_offset = 0.0
        self.scale_offset = 0.0
        self.align = True

    @staticmethod
    def _get_object_from_selection():
        """Retrieves object from selection to fill scatter_obj"""
        selection = cmds.ls(sl=True, transforms=True)
        if selection:
            return selection[0]
        else:
            return None

    def set_scatter_obj(self):
        self.scatter_obj = self._get_object_from_selection()

    def set_scatter_target(self):
        """Retrieves vertices from selection and fills scatter_target"""
        self.scatter_target = self._get_object_from_selection()
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
        if self.scatter_percent < 1.0:
            self.scatter_vertices = self.sample_vertices()
        for vert in self.scatter_vertices:
            instance = cmds.instance(self.scatter_obj)
            pos = cmds.pointPosition(vert, world=True)
            self.apply_transforms(instance[0], vert, pos)
            scattered.append(instance[0])
        scattered_group = cmds.group(scattered, name="scattered_grp")
        return scattered_group

    def sample_vertices(self):
        """Samples the vertices stored by the instance

        Return:
            List: a list of strings representing Maya vertex nodes
        """
        sample_size = int(len(self.scatter_vertices) * self.scatter_percent)
        sampled = random.sample(self.scatter_vertices, sample_size)
        return sampled

    def apply_transforms(self, instance, vertex, vert_pos):
        """Tests modifier conditions and applies transformations to the
        instanced object"""
        cmds.select(instance, r=True)
        cmds.move(vert_pos[0], vert_pos[1], vert_pos[2], a=True)
        if self.align is True:
            matrix = self.align_to_normals(vertex, vert_pos)
            cmds.select(instance, r=True)
            cmds.xform(ws=True, m=matrix)
        scale = cmds.getAttr("{}.scale".format(self.scatter_obj))[0]
        if self.scale_offset > 0.0:
            scale = self.random_scale(scale)
        cmds.setAttr("{}.scale".format(instance), scale[0], scale[1], scale[2])
        if self.rot_offset > 0.0:
            extra_rot = self.random_marginal_rotation()
            cmds.rotate(extra_rot[0], extra_rot[1], extra_rot[2], r=True)

    def align_to_normals(self, vertex, position):
        """Angles an object based on the position and normals of a vertex"""
        cmds.select(vertex, r=True)
        vtx_normals = cmds.polyNormalPerVertex(q=True, xyz=True)
        avg_normal = self.average_normals(vtx_normals)
        avg_normal = om.MVector(
            avg_normal[0], avg_normal[1], avg_normal[2]).normal()
        parent_shape = cmds.listRelatives(vertex, parent=True)[0]
        parent_transform = cmds.listRelatives(parent_shape, parent=True)[0]
        parent_matrix = cmds.xform(parent_transform, q=True, m=True, ws=True)
        world_normal = self.world_normal_from_local(avg_normal, parent_matrix)
        transform_matrix = self.get_matrix_from_normal(
            world_normal, position, parent_matrix)
        return transform_matrix

    def random_marginal_rotation(self):
        extra_rot = [0.0, 0.0, 0.0]
        rotation_range = self.rot_offset * 180
        for counter in range(len(extra_rot)):
            offset = random.uniform(-rotation_range, rotation_range)
            extra_rot[counter] = offset
        return extra_rot

    def random_scale(self, current_scale):
        new_scale = [1.0, 1.0, 1.0]
        ran_scale = random.uniform(-self.scale_offset, self.scale_offset)
        for counter in range(len(current_scale)):
            new_scale[counter] = current_scale[counter] * (1.0 + ran_scale)
        return new_scale

    @staticmethod
    def average_normals(normal_list):
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

    @staticmethod
    def get_matrix_from_normal(normal_xyz, position, parent_mat):
        """Converts averaged normal vectors to rotation eulers

        Return:
            List: A list representing a [4][4] matrix
        """
        local_y = parent_mat[4:7]
        tangent_1 = cross(normal_xyz, local_y)
        tangent_1 = om.MVector(tangent_1[0], tangent_1[1], tangent_1[2]).normal()
        tangent_2 = cross(normal_xyz, tangent_1)
        tangent_2 = om.MVector(tangent_2[0], tangent_2[1], tangent_2[2]).normal()
        matrix = [tangent_2[0], tangent_2[1], tangent_2[2], 0.0,
                  normal_xyz[0], normal_xyz[1], normal_xyz[2], 0.0,
                  tangent_1[0], tangent_1[1], tangent_1[2], 0.0,
                  position[0], position[1], position[2], 1.0]
        return matrix

    @staticmethod
    def world_normal_from_local(normal, parent_mat):
        """Converts a normal vector to world space

        Return:
            List: a list representing a normal vector
        """
        normal_str = "{0}, {1}, {2}".format(normal[0], normal[1], normal[2])
        mel_code_1 = "{" + normal_str + "}"
        matrix_str = "{0},{1},{2},{3},{4},{5},{6},{7}," \
                     "{8},{9},{10},{11},{12},{13},{14},{15}"
        matrix_str = matrix_str.format(
            parent_mat[0], parent_mat[1], parent_mat[2], parent_mat[3],
            parent_mat[4], parent_mat[5], parent_mat[6], parent_mat[7],
            parent_mat[8], parent_mat[9], parent_mat[10], parent_mat[11],
            parent_mat[12], parent_mat[13], parent_mat[14], parent_mat[15])
        mel_code_2 = "{" + matrix_str + "}"
        evaluation = mel.eval("pointMatrixMult " + mel_code_1 + mel_code_2)
        return evaluation
        


