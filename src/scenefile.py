from pathlib import Path

class SceneFile(object):
    """Abstract representation of a scene file"""
    def __init__(self, folder_path, descriptor, task, ver, ext):
        self.folder_path = Path(folder_path)
        self.descriptor = descriptor
        self.task = task
        self.ver = ver
        self.ext = ext

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


scene_file = SceneFile("D:/", "tank", "model", 1, ".ma")
print(scene_file.path)
