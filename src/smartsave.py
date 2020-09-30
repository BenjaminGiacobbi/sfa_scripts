import logging
import re

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pmc
from pymel.core.system import Path

log = logging.getLogger(__name__)


def maya_main_window():
    """Returns the open maya window as a """
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window), QtWidgets.QWidget)


class SmartSaveUI(QtWidgets.QDialog):
    """Docstring goes here"""
    def __init__(self):
        super(SmartSaveUI, self).__init__(parent=maya_main_window())
        self.setWindowTitle("Smart Save")
        self.setMinimumWidth(500)
        self.setWindowFlags(self.windowFlags() ^
                            QtCore.Qt.WindowContextHelpButtonHint)
        self.create_ui()

    def create_ui(self):
        self.title_label = QtWidgets.QLabel("Smart Save")
        self.title_label.setStyleSheet("font: 20px")
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.title_label)
        self.setLayout(self.main_layout)


class SceneFile(object):
    """Abstract representation of a scene file"""
    def __init__(self, path=None):
        self.folder_path = Path()
        self.descriptor = "main"
        self.task = "none"
        self.ver = 1
        self.ext = ".ma"
        scene = pmc.system.sceneName()
        if not path and scene:
            path = scene
        if not path and not scene:
            log.warning("Unable to initialize SceneFile object"
                        "from a new scene. Please specify a path.")
            return
        self._init_from_path(path)

    @property
    def filename(self):
        pattern = "{descriptor}_{task}_v{ver:03d}{ext}"
        return pattern.format(descriptor=self.descriptor,
                              task=self.task,
                              ver=self.ver,
                              ext=self.ext)

    @property
    def path(self):
        return self.folder_path / self.filename

    def _init_from_path(self, path):
        path = Path(path)
        self.folder_path = path.parent
        property_list = re.findall(r"([^\W_v]+|\.[A-Za-z0-9]+)", path.name)
        self.descriptor, self.task, ver, self.ext = property_list
        self.ver = int(ver.lstrip("0"))

    def save(self):
        """Saves the scene file.

        Returns:
            Path: the path to the scene file if successful
        """
        try:
            return pmc.system.saveAs(self.path)
        except RuntimeError as error:
            log.warning("Missing directories in path. Creating directories...")
            self.folder_path.makedirs_p()
            return pmc.system.saveAs(self.path)

    def next_avail_ver(self):
        """Returns the next available version number in the same folder"""
        pattern = "{descriptor}_{task}_v*{ext}".format(
            descriptor=self.descriptor,
            task=self.task,
            ext=self.ext)
        matching_scene_files = []
        for file_ in self.folder_path.files():
            if file_.name.fnmatch(pattern):
                matching_scene_files.append(file_)
        if not matching_scene_files:
            return 1
        matching_scene_files.sort()
        version_match = re.search(r'[0-9]{3}', matching_scene_files[-1])
        latest_version = int(version_match.group())
        return latest_version + 1

    def increment_save(self):
        """Increments the version and saves the scene file

        If the existing version of the file already exists, saves as the
        next largest available version

        Return:
            Path: the path to the scene file if successful
        """
        self.ver = self.next_avail_ver()
        self.save()
