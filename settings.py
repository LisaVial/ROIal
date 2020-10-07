import PyQt5.QtCore as QtCore
import json


class Settings:

    instance = None

    def __init__(self):
        self.last_folder = ""
        self.main_window_geometry = bytearray()
        self.main_window_state = bytearray()
        Settings.instance = self

    def load_settings_from_file(self, path):
        try:
            d = json.load(path)
            if "last_folder" in d.keys():
                self.last_folder = d["last_folder"]
            if "main_window_geometry" in d.keys():
                self.main_window_geometry = QtCore.QByteArray(bytearray(d["main_window_geometry"], "ascii"))
            if "main_window_state" in d.keys():
                self.main_window_state = QtCore.QByteArray(bytearray(d["main_window_state"], "ascii"))
        except:
            pass

    def to_dict(self):
        d = dict()
        d["last_folder"] = self.last_folder
        d["main_window_geometry"] = bytearray(self.main_window_geometry).decode("ascii")
        d["main_window_state"] = bytearray(self.main_window_state).decode("ascii")
        return d

    def save(self, path):
        json.dump(self.to_dict(), path)