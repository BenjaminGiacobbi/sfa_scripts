import logging
import random

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.OpenMaya as om
import maya.api.OpenMaya as OpenMaya
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
        self.rotation_sbx.setValue(
            int(self.scatter_tool.rotation_offset * 100))
        self.rotation_sbx.setSuffix("%")
        self.rotation_sbx.setMaximumWidth(50)
        self.scale_sbx = QtWidgets.QSpinBox()
        self.scale_sbx.setValue(int(self.scatter_tool.rotation_offset * 100))
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
            print(self.scatter_tool.scatter_obj)
        self._update_scatter_btn_state()

    @QtCore.Slot()
    def _select_target(self):
        self.scatter_tool.set_scatter_target()
        if self.scatter_tool.scatter_target:
            self.target_le.setText(self.scatter_tool.scatter_target)
            print(self.scatter_tool.scatter_target)
        self._update_scatter_btn_state()

    @QtCore.Slot()
    def _scatter(self):
        self.scatter_tool.scatter_percent = float(
            self.sample_sbx.value()) / 100
        self.scatter_tool.scale_offset = float(self.scale_sbx.value()) / 100
        self.scatter_tool.rotation_offset = float(
            self.rotation_sbx.value()) / 100
        self.scatter_tool.orient = self.orient_cbx.isChecked()
        self.scatter_tool.scatter()

    def _update_scatter_btn_state(self):
        if self.scatter_tool.scatter_obj and self.scatter_tool.scatter_target:
            self.scatter_btn.setEnabled(True)


class ScatterTool(object):
    def __init__(self):
        self.scatter_target = None
        self.scatter_vertices = None
        self.scatter_obj = None
        self.scatter_percent = 1.0
        self.rotation_offset = 0.0
        self.scale_offset = 0.0
        self.orient = True
        selection = self._get_object_from_selection()
        if selection:
            self.current_sel = selection
            self.scatter_obj = self.current_sel

    @staticmethod
    def _get_object_from_selection():
        """Retrieves object from selection to fill scatter_obj"""
        selection = cmds.ls(sl=True, transforms=True)
        if not selection or len(selection) > 1:
            om.MGlobal.displayError("Please select a polygon in Object Mode.")
            return None
        return selection[0]

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
        # TODO break this up, this function is too big
        scattered = []
        sampled_vertices = self.sample_scatter_points()
        for vert in sampled_vertices:
            instance = cmds.instance(self.scatter_obj)
            pos = cmds.pointPosition(vert, world=True)

            # calculating the vertex normals
            cmds.select(vert, r=True)
            vtx_normals = cmds.polyNormalPerVertex(query=True, xyz=True)
            avg_normal = self.average_normals(vtx_normals)
            world_normal = self.world_normal_from_local(avg_normal, vert)
            transform_matrix = self.get_matrix_from_normal(world_normal, pos)

            # applying transformations
            cmds.select(instance[0], r=True)
            cmds.move(pos[0], pos[1], pos[2], a=True)
            cmds.xform(matrix=transform_matrix)

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

    # TODO probably pull the check out of this because it's weird that it returns the property
    def sample_scatter_points(self):
        if self.scatter_percent < 1:
            sample_size = int(
                len(self.scatter_vertices) * self.scatter_percent)
            sampled = random.sample(self.scatter_vertices, sample_size)
            return sampled
        else:
            return self.scatter_vertices

    # TODO maybe pull the check out of this one as well
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
            ran_scale = random.uniform(-self.scale_offset,
                                       self.scale_offset)
            obj_scale = cmds.getAttr("{}.scale".format(obj))[0]
            for counter in range(len(obj_scale)):
                new_scale[counter] = new_scale[counter] * (1.0 + ran_scale)
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

    def get_matrix_from_normal(self, normal_xyz, position):
        """Converts averaged normal vectors to rotation eulers

        Return:
            List: A list representing a 16 item matrix
        """
        # TODO need to convert the normal to world space,
        tangent_1 = cross(normal_xyz, [0, 1, 0])
        tangent_2 = cross(normal_xyz, tangent_1)
        matrix = [tangent_2[0], tangent_2[1], tangent_2[2], 0.0,
                  normal_xyz[0], normal_xyz[1], normal_xyz[2], 0.0,
                  tangent_1[0], tangent_1[1], tangent_1[2], 0.0,
                  position[0], position[1], position[2], 1.0]
        return matrix

    @staticmethod
    def world_normal_from_local(normal, vertex):
        """Converts a normal vector to world space

        Return:
            List: a list representing a normal vector
        """
        parent_shape = cmds.listRelatives(vertex, parent=True)
        parent_transform = cmds.listRelatives(parent_shape[0], parent=True)
        matrix = cmds.xform(parent_transform[0], q=True, m=True, ws=True)
        normal_str = "{0}, {1}, {2}".format(normal[0], normal[1], normal[2])
        mel_code_1 = "{" + normal_str + "}"
        matrix_str = "{0},{1},{2},{3},{4},{5},{6},{7}," \
                     "{8},{9},{10},{11},{12},{13},{14},{15}"
        matrix_str = matrix_str.format(matrix[0], matrix[1], matrix[2],
                                       matrix[3], matrix[4], matrix[5],
                                       matrix[6], matrix[7], matrix[8],
                                       matrix[9], matrix[10], matrix[11],
                                       matrix[12], matrix[13], matrix[14],
                                       matrix[15])
        mel_code_2 = "{" + matrix_str + "}"
        evaluation = mel.eval("pointMatrixMult " + mel_code_1 + mel_code_2)
        print(evaluation)
        return evaluation
        


