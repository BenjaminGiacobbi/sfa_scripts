import logging
import pymel.core as pmc
from pymel.core.system import Path
import re

log = logging.getLogger(__name__)


class SceneFile(object):
    """Abstract representation of a scene file"""
    def __init__(self, path=None):
        self.folder_path = Path()
        self.descriptor = "main"
        self.task = "none"
        self.version = 1
        self.version = ".ma"
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
        """saves the scene file.

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
        latest_scene_file = matching_scene_files[-1]
        latest_scene_file = latest_scene_file.name.stripext()
        latest_ver_num = int(latest_scene_file.split('_v')[-1])
        return latest_ver_num + 1

    def increment_save(self):
        """Increments the version and saves the scene file

        If the existing version of the file already exists, it should
        increment to the largest version number available in the folder

        Return:
            Path: the path to the scene file if successful"""
        self.ver = self.next_avail_ver()
        self.save()
