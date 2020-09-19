from pathlib import Path
import re


class SceneFile(object):
    """Abstract representation of a scene file"""
    def __init__(self, path):
        self.folder_path = Path()
        self.descriptor = 'main'
        self.task = 'none'
        self.version = 1
        self.version = '.ma'
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
        property_list = re.findall(r'([^\W_v]+|\.[A-Za-z0-9]+)', path.name)
        self.descriptor, self.task, ver, self.ext = property_list
        self.ver = int(ver.lstrip("0"))


scene_file = SceneFile("D:/assets/tank_model_v001.ma")
print(scene_file.path)
print(scene_file.folder_path)
print(scene_file.filename)
print(scene_file.descriptor)
print(scene_file.task)
print(scene_file.ver)
print(scene_file.ext)
