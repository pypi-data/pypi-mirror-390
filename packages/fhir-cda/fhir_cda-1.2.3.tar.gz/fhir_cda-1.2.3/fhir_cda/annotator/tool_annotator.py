from abc import ABC
from .abstract_annotator import AbstractAnnotator
from pathlib import Path
import json


class WorkflowToolAnnotator(AbstractAnnotator, ABC):
    def __init__(self, dataset_path):
        super().__init__(dataset_path, "workflow_tool")
        self._metadata_path = self._root / "workflow_tool.json"
        self._get_description()

    def _get_description(self):
        metadata_path = self._metadata_path
        if not metadata_path.exists():
            self._descriptions["workflow_tool"] = {
                "uuid": "",
                "name": "",
                "title": "",
                "version": "",
                "description": "",
                "model": [],
                "software": [],
                "input": [],
                "output": []
            }
        else:
            with open(metadata_path, "r") as f:
                self._descriptions = json.load(f)

    def update_uuid(self, uuid: str):
        if not isinstance(uuid, str):
            raise ValueError(f"UUID {uuid} is not a string")
        self._descriptions["workflow_tool"]["uuid"] = uuid
        return self

    def update_name(self, name: str):
        if not isinstance(name, str):
            raise ValueError(f"Title {name} is not a string")
        self._descriptions["workflow_tool"]["name"] = name
        return self

    def update_title(self, title: str):
        if not isinstance(title, str):
            raise ValueError(f"Title {title} is not a string")
        self._descriptions["workflow_tool"]["title"] = title
        return self

    def update_version(self, version: str):
        if not isinstance(version, str):
            raise ValueError(f"Version {version} is not a string")
        self._descriptions["workflow_tool"]["version"] = version
        return self

    def update_description(self, description: str):
        if not isinstance(description, str):
            raise ValueError(f"Description {description} is not a string")
        self._descriptions["workflow_tool"]["description"] = description
        return self

    def update_field(self, field, value):
        if field not in self._descriptions.get("workflow_tool"):
            raise ValueError(f"field {field} is not in descriptions['workflow_tool']")
        else:
            self._descriptions["workflow_tool"][field] = value
        return self

    def update_model(self, value):
        if type(value) is list:
            self._descriptions["workflow_tool"]["model"].extend(value)
        elif type(value) is str:
            self._descriptions["workflow_tool"]["model"].append(value)
        else:
            raise ValueError(
                f"Value {value} is invalid. Expected a string or a list of strings (UUIDs), but got {type}.")
        return self

    def update_software(self, value):
        if type(value) is list:
            self._descriptions["workflow_tool"]["software"].extend(value)
        elif type(value) is str:
            self._descriptions["workflow_tool"]["software"].append(value)
        else:
            raise ValueError(
                f"Value {value} is invalid. Expected a string or a list of strings (UUIDs), but got {type}.")
        return self

    def get_descriptions(self):
        return self._descriptions

    def save(self, path=None):
        super().save(path)
