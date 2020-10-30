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
        self._create_sub_layouts()
        self.main_lay = QtWidgets.QVBoxLayout()
        self.main_lay.addLayout(self.obj_layout)
        self.main_lay.addSpacerItem(QtWidgets.QSpacerItem(
            150, 30, QtWidgets.QSizePolicy.Expanding))
        self.main_lay.addLayout(self.mod_layout)
        self.main_lay.addSpacerItem(QtWidgets.QSpacerItem(
            150, 30, QtWidgets.QSizePolicy.Expanding))
        self.main_lay.addStretch()
        self.main_lay.addLayout(self.scatter_btn_layout)
        self.setLayout(self.main_lay)

    def _create_sub_layouts(self):
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

    def _create_object_ui(self):
        self.obj_le = QtWidgets.QLineEdit()
        self.obj_le.setPlaceholderText("Object to scatter")
        self.target_le = QtWidgets.QLineEdit()
        self.target_le.setPlaceholderText("Object to target")
        self._set_read_only_fields([self.obj_le, self.target_le])
        self.obj_btn = QtWidgets.QPushButton("Get From Selection")
        self.target_btn = QtWidgets.QPushButton("Get From Selection")
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.obj_le, 0, 0)
        layout.addWidget(self.target_le, 0, 2)
        layout.addWidget(self.obj_btn, 1, 0)
        layout.addWidget(self.target_btn, 1, 2)
        return layout

    @staticmethod
    def _set_read_only_fields(le_list):
        for le in le_list:
            le.setMinimumWidth(200)
            le.setMinimumHeight(30)
            le.setEnabled(False)

    def _create_modifier_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Random Rotation Range"))
        layout.addLayout(self._create_rotation_controls())
        layout.addSpacerItem(QtWidgets.QSpacerItem(
            150, 30, QtWidgets.QSizePolicy.Expanding))
        layout.addWidget(QtWidgets.QLabel("Random Scale Range"))
        layout.addLayout(self._create_scale_layout())
        layout.addSpacerItem(QtWidgets.QSpacerItem(
            150, 30, QtWidgets.QSizePolicy.Expanding))
        layout.addWidget(QtWidgets.QLabel("Miscellaneous"))
        layout.addLayout(self._create_misc_modifiers())
        return layout

    def _create_rotation_controls(self):
        self.x_min_lbl = QtWidgets.QLabel("X Min")
        self.x_max_lbl = QtWidgets.QLabel("X Max")
        self.y_min_lbl = QtWidgets.QLabel("Y Min")
        self.y_max_lbl = QtWidgets.QLabel("Y Max")
        self.z_min_lbl = QtWidgets.QLabel("Z Min")
        self.z_max_lbl = QtWidgets.QLabel("Z Max")
        self._align_widgets([self.x_min_lbl, self.x_max_lbl, self.y_min_lbl,
                             self.y_max_lbl, self.z_min_lbl, self.z_max_lbl])
        self.x_min_sbx = self._create_sbx(" Deg", [0.0, 180.0], 1, True)
        self.x_max_sbx = self._create_sbx(" Deg", [0.0, 180.0], 1, False)
        self.y_min_sbx = self._create_sbx(" Deg", [0.0, 180.0], 1, True)
        self.y_max_sbx = self._create_sbx(" Deg", [0.0, 180.0], 1, False)
        self.z_min_sbx = self._create_sbx(" Deg", [0.0, 180.0], 1, True)
        self.z_max_sbx = self._create_sbx(" Deg", [0.0, 180.0], 1, False)
        return self._assemble_rotation_layout()

    def _assemble_rotation_layout(self):
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.x_min_lbl, 0, 1)
        layout.addWidget(self.x_min_sbx, 0, 2)
        layout.addWidget(self.x_max_lbl, 0, 4)
        layout.addWidget(self.x_max_sbx, 0, 5)
        layout.addWidget(self.y_min_lbl, 1, 1)
        layout.addWidget(self.y_min_sbx, 1, 2)
        layout.addWidget(self.y_max_lbl, 1, 4)
        layout.addWidget(self.y_max_sbx, 1, 5)
        layout.addWidget(self.z_min_lbl, 2, 1)
        layout.addWidget(self.z_min_sbx, 2, 2)
        layout.addWidget(self.z_max_lbl, 2, 4)
        layout.addWidget(self.z_max_sbx, 2, 5)
        return layout

    def _create_scale_layout(self):
        self.scale_min_lbl = QtWidgets.QLabel("Scale Min")
        self.scale_max_lbl = QtWidgets.QLabel("Scale Max")
        self._align_widgets([self.scale_min_lbl, self.scale_max_lbl])
        self.scale_min_sbx = self._create_sbx("x", [0.0, 1.0], 0.01, False)
        self.scale_min_sbx.setValue(1.0)
        self.scale_max_sbx = self._create_sbx("x", [1.0, 5.0], 0.01, False)
        self.scale_max_sbx.setValue(1.0)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.scale_min_lbl, 0, 1)
        layout.addWidget(self.scale_min_sbx, 0, 2)
        layout.addWidget(self.scale_max_lbl, 0, 4)
        layout.addWidget(self.scale_max_sbx, 0, 5)
        return layout

    @staticmethod
    def _create_sbx(suffix, sbx_range, step, is_negative,):
        if isinstance(step, int):
            sbx = QtWidgets.QSpinBox()
        else:
            sbx = QtWidgets.QDoubleSpinBox()
        sbx.setSuffix(suffix)
        sbx.setRange(sbx_range[0], sbx_range[1])
        if is_negative is True:
            sbx.setPrefix("-")
        sbx.setWrapping(True)
        sbx.setSingleStep(step)
        sbx.setMaximumWidth(80)
        sbx.setMinimumHeight(30)
        return sbx

    @staticmethod
    def _align_widgets(widget_list):
        for widget in widget_list:
            widget.setMinimumWidth(120)
            widget.setMinimumHeight(30)
            widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    def _create_misc_modifiers(self):
        self.density_lbl = QtWidgets.QLabel("Scatter Density")
        self.orient_lbl = QtWidgets.QLabel("Orient to Normals")
        self._align_widgets([self.density_lbl, self.orient_lbl])
        self.density_sbx = self._create_sbx("%", [1, 100], 1, False)
        self.density_sbx.setValue(100)
        self.orient_cbx = QtWidgets.QCheckBox()
        self.orient_cbx.setChecked(True)
        self.orient_cbx.setMaximumWidth(80)
        self.orient_cbx.setMinimumHeight(30)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.density_lbl, 0, 1)
        layout.addWidget(self.density_sbx, 0, 2)
        layout.addWidget(self.orient_lbl, 0, 4)
        layout.addWidget(self.orient_cbx, 0, 5)
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
        """Retrieves UI values to populate instance variables, then scatters"""
        self.scatter_tool.scatter_density = float(
            self.density_sbx.value()) / 100
        self.scatter_tool.scale_range = [self.scale_min_sbx.value(),
                                         self.scale_max_sbx.value()]
        self.scatter_tool.rot_range_x = [self.x_min_sbx.value(),
                                         self.x_max_sbx.value()]
        self.scatter_tool.rot_range_y = [self.y_min_sbx.value(),
                                         self.y_max_sbx.value()]
        self.scatter_tool.rot_range_z = [self.z_min_sbx.value(),
                                         self.z_max_sbx.value()]
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
        self.scatter_density = 1.0
        self.rot_range_x = [0.0, 0.0]
        self.rot_range_y = [0.0, 0.0]
        self.rot_range_z = [0.0, 0.0]
        self.scale_range = [1.0, 1.0]
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
        if self.scatter_density < 1.0:
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
        sample_size = int(len(self.scatter_vertices) * self.scatter_density)
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
        if self.scale_range[0] < 1.0 or self.scale_range[1] > 1.0:
            scale = self.random_scale(scale)
        cmds.setAttr("{}.scale".format(instance), scale[0], scale[1], scale[2])
        extra_rot = self.random_marginal_rotation()
        cmds.rotate(extra_rot[0], extra_rot[1], extra_rot[2],
                    instance, os=True, r=True)

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
        offset_x = random.uniform(-self.rot_range_x[0], self.rot_range_x[1])
        print(offset_x)
        offset_y = random.uniform(-self.rot_range_y[0], self.rot_range_y[1])
        print(offset_y)
        offset_z = random.uniform(-self.rot_range_z[0], self.rot_range_z[1])
        print(offset_z)
        extra_rot = [offset_x, offset_y, offset_z]
        return extra_rot

    def random_scale(self, current_scale):
        new_scale = [1.0, 1.0, 1.0]
        ran_scale = random.uniform(self.scale_range[0], self.scale_range[1])
        for counter in range(len(current_scale)):
            new_scale[counter] = current_scale[counter] * ran_scale
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
        tangent_1 = om.MVector(
            tangent_1[0], tangent_1[1], tangent_1[2]).normal()
        tangent_2 = cross(normal_xyz, tangent_1)
        tangent_2 = om.MVector(
            tangent_2[0], tangent_2[1], tangent_2[2]).normal()
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
        


