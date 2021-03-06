import logging
import re

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import pymel.core as pmc
from pymel.core.system import Path

log = logging.getLogger(__name__)


def maya_main_window():
    """Returns the open maya window

    Return:
        wrapInstance: the maya window as a WrapInstance object
    """
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)


def gold_button_stylesheet():
    """Styles a QPushButton object as gold with black text.

    Return:
        stylesheet: A stylesheet with QPushButton selectors
    """
    stylesheet = """
        QPushButton {
            font-weight: bold;
            color: #191300;
            border: 1px solid #FFCA1C;
            background-color: #EABF3C;
        }
        QPushButton:hover { 
            background-color: #FFD147; 
        }
        QPushButton:pressed { 
            background-color: #916D00; 
            border: none;
        }
        """
    return stylesheet


def _check_object_length(test_object, zero_return, nonzero_return):
    try:
        if test_object.__len__() is 0:
            return zero_return
        else:
            return nonzero_return
    except AttributeError as error:
        log.warning("Object does not contain a __len__ attribute.")


class SmartSaveUI(QtWidgets.QDialog):
    """This class draws a SmartSaveUI with active user feedback according
    to a filename convention of [descriptor]_[task]_v[version].[ext]"""
    def __init__(self):
        super(SmartSaveUI, self).__init__(parent=maya_main_window())
        self.setWindowTitle("Smart Save")
        self.setMinimumWidth(500)
        self.setMaximumWidth(1000)
        self.setMaximumHeight(200)
        self.setWindowFlags(self.windowFlags())
        self.scene_file = SceneFile()
        self.current_ui_desc = self.scene_file.descriptor
        self.current_ui_task = self.scene_file.task
        self.current_ui_ver = self.scene_file.ver
        self._create_ui()
        self._create_connections()

    def _create_ui(self):
        """Creates the main GUI window and assembles user controls"""
        self.title_lbl = QtWidgets.QLabel("Smart Save")
        self.title_lbl.setStyleSheet("font: 20px")
        self.folder_lay = self._create_folder_ui()
        self.filename_lay = self._create_filename_ui()
        self.button_lay = self._create_buttons_ui()
        self.main_lay = QtWidgets.QVBoxLayout()

        self.main_lay.addWidget(self.title_lbl)
        self.main_lay.addLayout(self.folder_lay)
        self.main_lay.addLayout(self.filename_lay)
        self.main_lay.addLayout(self.button_lay)
        self.setLayout(self.main_lay)

    def _create_folder_ui(self):
        self.folder_le = QtWidgets.QLineEdit(self.scene_file.folder_path)
        self.folder_le.setMinimumHeight(30)
        self.folder_browse_btn = QtWidgets.QPushButton("Browse")
        self.folder_browse_btn.setMinimumHeight(30)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.folder_le)
        layout.addWidget(self.folder_browse_btn)
        return layout

    def _create_filename_ui(self):
        self.desc_le = QtWidgets.QLineEdit(self.current_ui_desc)
        self.desc_le.setMaxLength(50)
        self.desc_le.setMinimumWidth(100)
        self.desc_le.setMinimumHeight(30)

        self.task_le = QtWidgets.QLineEdit(self.current_ui_task)
        self.task_le.setMaxLength(20)
        self.task_le.setFixedWidth(100)
        self.task_le.setMinimumHeight(30)

        self._set_ui_placeholder_text()

        self.ver_sbx = QtWidgets.QSpinBox()
        self.ver_sbx.setValue(self.current_ui_ver)
        self.ver_sbx.setButtonSymbols(QtWidgets.QAbstractSpinBox.PlusMinus)
        self.ver_sbx.setRange(1, 99)
        self.ver_sbx.setFixedWidth(50)
        self.ver_sbx.setMinimumHeight(30)

        layout = self._create_filename_headers()
        layout.addWidget(self.desc_le, 1, 0)
        layout.addWidget(QtWidgets.QLabel("_"), 1, 1)
        layout.addWidget(self.task_le, 1, 2)
        layout.addWidget(QtWidgets.QLabel("_v"), 1, 3)
        layout.addWidget(self.ver_sbx, 1, 4)
        layout.addWidget(QtWidgets.QLabel(self.scene_file.ext), 1, 6)
        return layout

    def _create_filename_headers(self):
        self.descriptor_lbl = QtWidgets.QLabel("Descriptor")
        self.descriptor_lbl.setStyleSheet("font-weight: bold")
        self.task_lbl = QtWidgets.QLabel("Task")
        self.task_lbl.setStyleSheet("font-weight: bold")
        self.ver_lbl = QtWidgets.QLabel("Version")
        self.ver_lbl.setStyleSheet("font-weight: bold")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.descriptor_lbl, 0, 0)
        layout.addWidget(self.task_lbl, 0, 2)
        layout.addWidget(self.ver_lbl, 0, 4)
        return layout

    def _create_buttons_ui(self):
        self.save_btn = QtWidgets.QPushButton()
        self.save_btn.setMinimumHeight(40)
        self.save_increment_btn = QtWidgets.QPushButton()
        self.save_increment_btn.setStyleSheet(gold_button_stylesheet())
        self.save_increment_btn.setMinimumHeight(40)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.save_btn)
        layout.addWidget(self.save_increment_btn)
        return layout

    def _create_connections(self):
        self.folder_browse_btn.clicked.connect(self._open_browse_dialog)
        self.desc_le.textEdited.connect(self._update_descriptor_display)
        self.task_le.textEdited.connect(self._update_task_display)
        self.ver_sbx.valueChanged.connect(self._update_ver_display)
        self.save_btn.clicked.connect(self._save)
        self.save_increment_btn.clicked.connect(self._save_increment)
        self._update_filename_display()

    def _set_scene_properties_from_ui(self):
        self.scene_file.folder_path = self.folder_le.text()
        self.scene_file.descriptor = self.current_ui_desc
        self.scene_file.task = self.current_ui_task
        self.scene_file.ver = self.current_ui_ver
        self.scene_file.ext = ".ma"

        self.desc_le.setText(self.current_ui_desc)
        self.task_le.setText(self.current_ui_task)
        self._set_ui_placeholder_text()

    def _set_ui_placeholder_text(self):
        self.desc_le.setPlaceholderText(self.current_ui_desc)
        self.task_le.setPlaceholderText(self.current_ui_task)

    @QtCore.Slot()
    def _open_browse_dialog(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self, caption="Browse", dir=self.folder_le.text(),
            options=QtWidgets.QFileDialog.ShowDirsOnly |
            QtWidgets.QFileDialog.DontResolveSymlinks)
        if folder:
            self.folder_le.setText(folder)
            self._update_filename_display()

    @QtCore.Slot()
    def _save(self):
        self._set_scene_properties_from_ui()
        self.scene_file.save()
        self._update_filename_display()

    @QtCore.Slot()
    def _save_increment(self):
        self._set_scene_properties_from_ui()
        self.scene_file.save_increment()
        self.current_ui_ver = self.scene_file.ver
        self._update_filename_display()

    @QtCore.Slot()
    def _update_descriptor_display(self):
        self.current_ui_desc = _check_object_length(
            self.desc_le.text(), self.scene_file.descriptor,
            self.desc_le.text())
        self._update_filename_display()

    @QtCore.Slot()
    def _update_task_display(self):
        self.current_ui_task = _check_object_length(
            self.task_le.text(), self.scene_file.task, self.task_le.text())
        self._update_filename_display()

    @QtCore.Slot()
    def _update_ver_display(self):
        self.current_ui_ver = self.ver_sbx.value()
        self._update_filename_display()

    def _update_filename_display(self):
        if self.ver_sbx.value() is not self.current_ui_ver:
            self.ver_sbx.setValue(self.current_ui_ver)
        next_ver = self.scene_file.next_avail_ver(
            search_desc=self.current_ui_desc,
            search_task=self.current_ui_task,
            search_ext=self.scene_file.ext,
            search_path=Path(self.folder_le.text()))
        name_str = "{desc}_{task}".format(desc=self.current_ui_desc,
                                          task=self.current_ui_task)
        save_str = "_v{ver:03d}.ma".format(ver=self.current_ui_ver)
        inc_str = "_v{ver:03d}.ma".format(ver=next_ver)

        self.save_btn.setText("Save as: \n" + name_str + save_str)
        self.save_increment_btn.setText("Increment save as: \n"
                                        + name_str + inc_str)


class SceneFile(object):
    """Abstract representation of a scene file"""
    def __init__(self, path=None):
        self._folder_path = Path(cmds.workspace(query=True,
                                                rootDirectory=True)) / "scenes"
        self.descriptor = "main"
        self.task = "model"
        self.ver = 1
        self.ext = ".ma"
        scene = pmc.system.sceneName()
        if not path and scene:
            path = scene
        if not path and not scene:
            log.info("Initialize with default properties.")
            return
        self._init_from_path(path)

    @property
    def folder_path(self):
        return self._folder_path

    @folder_path.setter
    def folder_path(self, val):
        self._folder_path = Path(val)

    @property
    def filename(self):
        pattern = "{descriptor}_{task}_v{ver:03d}{ext}"
        return pattern.format(descriptor=self.descriptor,
                              task=self.task,
                              ver=self.ver,
                              ext=self.ext)

    @property
    def path(self):
        return self._folder_path / self.filename

    def _init_from_path(self, path):
        path = Path(path)
        self._folder_path = path.parent
        try:
            property_list = re.findall(r"([^\W_v]+|\.[A-Za-z0-9]+)", path.name)
            self.descriptor, self.task, ver, self.ext = property_list
            self.ver = int(ver.lstrip("0"))
        except ValueError as error:
            log.warning("File does not match naming convention. "
                        "Using default values...")

    def save(self):
        """Saves the scene file.

        Return:
            Path: the path to the scene file if successful
        """
        try:
            return pmc.system.saveAs(self.path)
        except RuntimeError as error:
            log.warning("Missing directories in path. Creating directories...")
            self.folder_path.makedirs_p()
            return pmc.system.saveAs(self.path)

    def next_avail_ver(self, search_desc=None,
                       search_task=None, search_ext=None, search_path=None):
        """Returns the next available version number using provided
        descriptor, task, ext, and folder path to search for
        """
        if not search_desc:
            search_desc = self.descriptor
        if not search_task:
            search_task = self.task
        if not search_ext:
            search_ext = self.ext
        if not search_path:
            search_path = self.folder_path
        pattern = "{descriptor}_{task}_v*{ext}".format(descriptor=search_desc,
                                                       task=search_task,
                                                       ext=search_ext)
        matching_scene_files = []
        for file_ in search_path.files():
            if file_.name.fnmatch(pattern):
                matching_scene_files.append(file_)
        if not matching_scene_files:
            return 1
        matching_scene_files.sort()
        version_match = re.search(r'[0-9]{3}', matching_scene_files[-1])
        latest_version = int(version_match.group())
        return latest_version + 1

    def save_increment(self):
        """Increments the version and saves the scene file

        If the existing version of the file already exists, saves as the
        next largest available version

        Return:
            Path: the path to the scene file if successful
        """
        self.ver = self.next_avail_ver()
        self.save()
