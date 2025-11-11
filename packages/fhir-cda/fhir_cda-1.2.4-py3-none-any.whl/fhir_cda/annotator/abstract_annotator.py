from pathlib import Path
from abc import ABC
import json


class AbstractAnnotator(ABC):

    def __init__(self, dataset_path, category):
        self._root = Path(dataset_path)
        self._category = category
        self._descriptions = {}

    def save(self, path=None):
        if path:
            save_path = Path(path) / f"{self._category}.json"
        else:
            save_path = self._root / f"{self._category}.json"

        with open(save_path, "w") as json_file:
            json.dump(self._descriptions, json_file, indent=4)