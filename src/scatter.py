import logging
import random

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
from maya.OpenMayaUI import MQtUtil
from maya.OpenMaya import MVector, MGlobal
import maya.cmds as cmds
import maya.mel as mel

log = logging.getLogger(__name__)


def maya_main_window():
    """Returns the open maya window.

    Return:
        wrapInstance: The maya window as a WrapInstance object.
    """
    main_window = MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)


def cross(a, b):
    c = [a[1] * b[2] - a[2] * b[1],
         a[2] * b[0] - a[0] * b[2],
         a[0] * b[1] - a[1] * b[0]]
    return c


class ScatterUI(QtWidgets.QDialog):
    """Draws a scatter tool UI to interface with ScatterTool class."""
    def __init__(self):
        super(ScatterUI, self).__init__(parent=maya_main_window())
        self.setWindowTitle("Scatter Tool")
        self.setWindowFlags(
            self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMaximumWidth(750)
        self.scatter = ScatterTool()
        self._create_ui()
        self._create_connections()

    def _create_ui(self):
        self._create_sub_layouts()
        self.main_lay = QtWidgets.QVBoxLayout()
        self.main_lay.addLayout(self.obj_layout)
        self.main_lay.addSpacerItem(
            QtWidgets.QSpacerItem(150, 30, QtWidgets.QSizePolicy.Expanding))
        self.main_lay.addLayout(self.mod_layout)
        self.main_lay.addSpacerItem(
            QtWidgets.QSpacerItem(150, 30, QtWidgets.QSizePolicy.Expanding))
        self.main_lay.addStretch()
        self.main_lay.addLayout(self.scatter_btn_layout)
        self.setLayout(self.main_lay)

    def _create_sub_layouts(self):
        self.obj_lbl = QtWidgets.QLabel("Main Objects")
        self.obj_lbl.setStyleSheet("font: 24px")
        self.obj_layout = QtWidgets.QVBoxLayout()
        self.obj_layout.addWidget(self.obj_lbl)
        self.obj_layout.addLayout(self._create_object_ui())
        self.mod_lbl = QtWidgets.QLabel("Modifiers")
        self.mod_lbl.setStyleSheet("font: 24px")
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
        self.obj_btn = QtWidgets.QPushButton(
            "Get From Selection\n(Single-object only)")
        self.target_btn = QtWidgets.QPushButton(
            "Get From Selection\n(Supports multiple objects)")
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
            le.setReadOnly(True)

    def _create_modifier_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel("Random Rotation Range"))
        layout.addLayout(self._create_rotation_controls())
        layout.addSpacerItem(
            QtWidgets.QSpacerItem(150, 30, QtWidgets.QSizePolicy.Expanding))
        layout.addWidget(QtWidgets.QLabel("Random Scale Range"))
        layout.addLayout(self._create_scale_layout())
        layout.addSpacerItem(
            QtWidgets.QSpacerItem(150, 30, QtWidgets.QSizePolicy.Expanding))
        layout.addWidget(QtWidgets.QLabel("Miscellaneous"))
        layout.addLayout(self._create_misc_modifiers())
        return layout

    def _create_rotation_controls(self):
        self.x_neg_lbl = QtWidgets.QLabel("Negative X")
        self.x_pos_lbl = QtWidgets.QLabel("Positive X")
        self.y_neg_lbl = QtWidgets.QLabel("Negative Y")
        self.y_pos_lbl = QtWidgets.QLabel("Positive Y")
        self.z_neg_lbl = QtWidgets.QLabel("Negative Z")
        self.z_pos_lbl = QtWidgets.QLabel("Positive Z")
        self._align_widgets([self.x_neg_lbl, self.x_pos_lbl, self.y_neg_lbl,
                             self.y_pos_lbl, self.z_neg_lbl, self.z_pos_lbl])
        self.x_neg_sbx = self._create_double_sbx(" Deg", [0.0, 180.0], 0.1)
        self.x_pos_sbx = self._create_double_sbx(" Deg", [0.0, 180.0], 0.1)
        self.y_neg_sbx = self._create_double_sbx(" Deg", [0.0, 180.0], 0.1)
        self.y_pos_sbx = self._create_double_sbx(" Deg", [0.0, 180.0], 0.1)
        self.z_neg_sbx = self._create_double_sbx(" Deg", [0.0, 180.0], 0.1)
        self.z_pos_sbx = self._create_double_sbx(" Deg", [0.0, 180.0], 0.1)
        return self._assemble_rotation_layout()

    def _assemble_rotation_layout(self):
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.x_neg_lbl, 0, 1)
        layout.addWidget(self.x_neg_sbx, 0, 2)
        layout.addWidget(self.x_pos_lbl, 0, 4)
        layout.addWidget(self.x_pos_sbx, 0, 5)
        layout.addWidget(self.y_neg_lbl, 1, 1)
        layout.addWidget(self.y_neg_sbx, 1, 2)
        layout.addWidget(self.y_pos_lbl, 1, 4)
        layout.addWidget(self.y_pos_sbx, 1, 5)
        layout.addWidget(self.z_neg_lbl, 2, 1)
        layout.addWidget(self.z_neg_sbx, 2, 2)
        layout.addWidget(self.z_pos_lbl, 2, 4)
        layout.addWidget(self.z_pos_sbx, 2, 5)
        return layout

    def _create_scale_layout(self):
        self.scale_min_lbl = QtWidgets.QLabel("Minimum Scale")
        self.scale_max_lbl = QtWidgets.QLabel("Maximum Scale")
        self._align_widgets([self.scale_min_lbl, self.scale_max_lbl])
        self.scale_min_sbx = self._create_double_sbx("x", [0.0, 1.0], 0.01)
        self.scale_min_sbx.setValue(1.0)
        self.scale_max_sbx = self._create_double_sbx("x", [1.0, 5.0], 0.01)
        self.scale_max_sbx.setValue(1.0)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.scale_min_lbl, 0, 1)
        layout.addWidget(self.scale_min_sbx, 0, 2)
        layout.addWidget(self.scale_max_lbl, 0, 4)
        layout.addWidget(self.scale_max_sbx, 0, 5)
        return layout

    @staticmethod
    def _create_double_sbx(suffix, sbx_range, step):
        sbx = QtWidgets.QDoubleSpinBox()
        sbx.setSuffix(suffix)
        sbx.setRange(sbx_range[0], sbx_range[1])
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
        self.density_sbx = self._create_double_sbx("%", [0.0, 100.0], 0.1)
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
        self.scatter.set_scatter_obj()
        if len(self.scatter.scatter_obj) is 1:
            self.obj_le.setText(self.scatter.scatter_obj[0])
        else:
            self.obj_le.clear()
            MGlobal.displayError(
                "Failed to get scatter object. Select one shape object in "
                "Object Mode and press \"Get From Selection\"")
        self._update_scatter_btn_state()

    @QtCore.Slot()
    def _select_target(self):
        self.scatter.set_scatter_targets()
        full_targets = self.scatter.target_objs + self.scatter.target_verts
        if len(full_targets) > 0:
            target_str = ""
            for idx in range(len(full_targets)):
                target_str += full_targets[idx]
                if idx is not len(full_targets) - 1:
                    target_str += ", "
            self.target_le.setText(target_str)
        else:
            self.target_le.clear()
            MGlobal.displayError(
                "Failed to get scatter targets. Select one or more shapes in "
                "Object Mode and press \"Get From Selection\"")
        self._update_scatter_btn_state()

    @QtCore.Slot()
    def _scatter(self):
        """Retrieves scatter modifiers from UI and then runs scatter."""
        if not cmds.objExists(self.scatter.scatter_obj[0]):
            MGlobal.displayError("Specified scatter object does not exist.")
            self.obj_le.clear()
            self._update_scatter_btn_state()
            return
        for target in self.scatter.target_objs + self.scatter.target_verts:
            if not cmds.objExists(target):
                MGlobal.displayError("One or more of the scatter targets does "
                                     "not exist. Please reselect.")
                self.target_le.clear()
                self._update_scatter_btn_state()
                return
        self._set_scatter_properties_from_ui()
        self.scatter.scatter()

    def _set_scatter_properties_from_ui(self):
        scatter_density = float(self.density_sbx.value()) / 100
        scale_range = [self.scale_min_sbx.value(), self.scale_max_sbx.value()]
        rot_range_x = [-self.x_neg_sbx.value(), self.x_pos_sbx.value()]
        rot_range_y = [-self.y_neg_sbx.value(), self.y_pos_sbx.value()]
        rot_range_z = [-self.z_neg_sbx.value(), self.z_pos_sbx.value()]
        self.scatter.scatter_density = scatter_density
        self.scatter.scale_range = scale_range
        self.scatter.rot_range_x = rot_range_x
        self.scatter.rot_range_y = rot_range_y
        self.scatter.rot_range_z = rot_range_z
        self.scatter.align = self.orient_cbx.isChecked()

    def _update_scatter_btn_state(self):
        if self.obj_le.text() and self.target_le.text():
            self.scatter_btn.setEnabled(True)
        else:
            self.scatter_btn.setEnabled(False)


class ScatterTool(object):
    def __init__(self):
        self.target_objs = []
        self.target_verts = []
        self.scatter_obj = None
        self.scatter_density = 1.0
        self.rot_range_x = [0.0, 0.0]
        self.rot_range_y = [0.0, 0.0]
        self.rot_range_z = [0.0, 0.0]
        self.scale_range = [1.0, 1.0]
        self.align = True

    @staticmethod
    def get_object_from_selection():
        selection = cmds.ls(sl=True, transforms=True)
        if selection:
            return selection
        else:
            return []

    def set_scatter_obj(self):
        selection = cmds.ls(sl=True, transforms=True)
        if selection:
            self.scatter_obj = selection
        else:
            self.scatter_obj = []

    def set_scatter_targets(self):
        """Retrieves vertices from object after setting scatter target."""
        obj_targets = []
        vert_targets = cmds.ls(orderedSelection=True, flatten=True)
        cmds.filterExpand(vert_targets, selectionMask=31, expand=True)
        for obj in vert_targets:
            if "vtx[" not in obj:
                obj_targets.append(obj)
                vert_targets.remove(obj)
        self.target_objs = obj_targets
        self.target_verts = vert_targets

    def scatter(self):
        """Scatters the target object across vertices list.

        Return:
            String: The group name of the scattered objects.
        """
        combined_verts = self.target_verts
        scattered = []
        if len(self.target_objs) > 0:
            for obj in self.target_objs:
                combined_verts += cmds.ls(obj + ".vtx[*]", flatten=True)
        if self.scatter_density < 1.0:
            combined_verts = self._sample_vertices(combined_verts)
        scale = cmds.getAttr("{}.scale".format(self.scatter_obj[0]))[0]
        for vert in combined_verts:
            instance = cmds.instance(self.scatter_obj[0])
            pos = cmds.pointPosition(vert, world=True)
            self._apply_transforms(instance[0], vert, pos, scale)
            scattered.append(instance[0])
        scattered_group = cmds.group(scattered, name="scattered_grp")
        return scattered_group

    def _sample_vertices(self, vert_list):
        """Samples a percentage of vertices stored by the instance.

        Return:
            List: A list of strings representing Maya vertex nodes.
        """
        sample_size = int(len(vert_list) * self.scatter_density)
        sampled = random.sample(vert_list, sample_size)
        return sampled

    def _apply_transforms(self, instance, vertex, vert_pos, scale):
        """Tests modifier conditions and applies transformations to the
        instanced object"""
        cmds.select(instance, r=True)
        cmds.move(vert_pos[0], vert_pos[1], vert_pos[2], a=True)
        if self.align is True:
            matrix = self._align_to_normals(vertex, vert_pos)
            cmds.select(instance, r=True)
            cmds.xform(ws=True, m=matrix)
        if self.scale_range[0] < 1.0 or self.scale_range[1] > 1.0:
            scale = self._random_scale(scale)
        cmds.setAttr("{}.scale".format(instance), scale[0], scale[1], scale[2])
        extra_rot = self._random_marginal_rotation()
        cmds.rotate(extra_rot[0], extra_rot[1], extra_rot[2],
                    instance, os=True, r=True)

    def _align_to_normals(self, vertex, position):
        """Angles an object based on the position and normals of a vertex.

        Return:
            List: A 16 item list representing a [4][4] transformation matrix.
        """
        cmds.select(vertex, r=True)
        vtx_normals = cmds.polyNormalPerVertex(q=True, xyz=True)
        avg_normal = self.average_normals(vtx_normals)
        avg_normal = MVector(
            avg_normal[0], avg_normal[1], avg_normal[2]).normal()
        parent_shape = cmds.listRelatives(vertex, parent=True)[0]
        parent_transform = cmds.listRelatives(parent_shape, parent=True)[0]
        parent_matrix = cmds.xform(parent_transform, q=True, m=True, ws=True)
        world_normal = self.world_normal_from_local(avg_normal, parent_matrix)
        transform_matrix = self.get_matrix_from_normal(
            world_normal, position, parent_matrix)
        return transform_matrix

    def _random_marginal_rotation(self):
        """Generates random rotation to apply on three axes.

        Return:
            List: A 3 item list representing xyz rotation values in degrees.
        """
        offset_x = random.uniform(self.rot_range_x[0], self.rot_range_x[1])
        offset_y = random.uniform(self.rot_range_y[0], self.rot_range_y[1])
        offset_z = random.uniform(self.rot_range_z[0], self.rot_range_z[1])
        return [offset_x, offset_y, offset_z]

    def _random_scale(self, current_scale):
        """Generates a random sc"""
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
                dir_sum += normal_list[coord_iterator]
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
        tangent_1 = MVector(tangent_1[0], tangent_1[1], tangent_1[2]).normal()
        tangent_2 = cross(normal_xyz, tangent_1)
        tangent_2 = MVector(tangent_2[0], tangent_2[1], tangent_2[2]).normal()
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
        matrix_str = ("{0},{1},{2},{3},{4},{5},{6},{7},"
                      "{8},{9},{10},{11},{12},{13},{14},{15}")
        matrix_str = matrix_str.format(
            parent_mat[0], parent_mat[1], parent_mat[2], parent_mat[3],
            parent_mat[4], parent_mat[5], parent_mat[6], parent_mat[7],
            parent_mat[8], parent_mat[9], parent_mat[10], parent_mat[11],
            parent_mat[12], parent_mat[13], parent_mat[14], parent_mat[15])
        mel_code_2 = "{" + matrix_str + "}"
        evaluation = mel.eval("pointMatrixMult " + mel_code_1 + mel_code_2)
        return evaluation
