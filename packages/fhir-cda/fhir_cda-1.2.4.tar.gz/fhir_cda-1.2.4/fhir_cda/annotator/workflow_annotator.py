from abc import ABC
from .abstract_annotator import AbstractAnnotator
from pprint import pprint
from fhir_cda.utils import ordered_load
from fhir_cda.ehr.workflow import (WorkflowGoal, WorkflowActionInput, WorkflowActionOutput, WorkflowAction)
from typing import List, Optional, Union
import copy


class WorkflowAnnotator(AbstractAnnotator, ABC):
    def __init__(self, dataset_path):
        super().__init__(dataset_path, "workflow")
        self.cwl_content = {}
        self.elements = {}
        self._analysis_workflow()

    def _analysis_workflow(self):
        primary_folder = self._root / "primary"

        workflow_paths = list(primary_folder.glob("*.cwl"))
        if not workflow_paths:
            self._descriptions = {}
            raise Exception("No workflow cwl found")

        workflow_path = workflow_paths[0]
        with open(workflow_path, 'r') as file:
            self.cwl_content = ordered_load(file)

        self.elements["workflow"] = {
            "uuid": "",
            "name": self._root.name,
            "title": self.cwl_content.get("class"),
            "version": self.cwl_content.get("cwlVersion"),
            "description": "",
            "purpose": "",
            "usage": "",
            "author": "",
            "goal": [],
            "action": []
        }

        self._generate_action_goal(self.cwl_content["steps"])

    def _generate_action_goal(self, steps):
        workflow_goals = []
        for idx, step in enumerate(steps.keys()):
            inputs = steps[step]["run"]["inputs"]
            outputs = steps[step]["run"]["outputs"]
            workflow_action_inputs = []
            workflow_action_outputs = []

            for i, name in enumerate(inputs.keys()):
                workflow_action_inputs.append(WorkflowActionInput(
                    display=name
                ))
            for j, name in enumerate(outputs.keys()):
                workflow_action_outputs.append(WorkflowActionOutput(
                    display=name
                ))
                workflow_goals.append(WorkflowGoal(description=name))

            self.elements["workflow"]["action"].append(WorkflowAction(
                title=step,
                description=f'step {idx + 1}',
                action_input=workflow_action_inputs,
                action_output=workflow_action_outputs
            ))
        self.update_goals(workflow_goals)

    def _convert_elements_to_descriptions(self):
        self._descriptions["workflow"] = copy.deepcopy(self.elements["workflow"])
        self._descriptions["workflow"]["goal"] = []
        self._descriptions["workflow"]["action"] = []
        for g in self.elements["workflow"].get("goal", []):
            self._descriptions["workflow"]["goal"].append(g.get())
        for a in self.elements["workflow"].get("action", []):
            self._descriptions["workflow"]["action"].append(a.get())

    def update_workflow_field(self, field, value):
        if field not in self.elements.get("workflow"):
            raise ValueError(f"field {field} is not in descriptions['workflow_tool']")
        else:
            self.elements["workflow"][field] = value
        return self

    def update_name(self, name: str):
        self.elements["workflow"]["name"] = name
        return self

    def update_goals(self, goals: List[WorkflowGoal]):
        if not isinstance(goals, List):
            return self
        else:
            self.elements["workflow"]["goal"] = [g for g in goals if isinstance(g, WorkflowGoal)]
            return self

    def add_goal(self, goal: WorkflowGoal):
        if isinstance(goal, WorkflowGoal):
            self.elements["workflow"]["goal"].append(goal)
        else:
            raise ValueError(f"Goal {goal} is not a WorkflowGoal")
        return self

    def update_uuid(self, uuid: str):
        if isinstance(uuid, str):
            self.elements["workflow"]["uuid"] = uuid
        else:
            raise ValueError(f"UUID {uuid} is not a string")
        return self

    def update_title(self, title: str):
        if isinstance(title, str):
            self.elements["workflow"]["title"] = title
        else:
            raise ValueError(f"Title {title} is not a string")
        return self

    def update_version(self, version: str):
        if isinstance(version, str):
            self.elements["workflow"]["version"] = version
        else:
            raise ValueError(f"Version {version} is not a string")
        return self

    def update_description(self, description):
        if isinstance(description, str):
            self.elements["workflow"]["description"] = description
        else:
            raise ValueError(f"Description {description} is not a string")
        return self

    def update_purpose(self, purpose: str):
        if isinstance(purpose, str):
            self.elements["workflow"]["purpose"] = purpose
        else:
            raise ValueError(f"Purpose {purpose} is not a string")
        return self

    def update_usage(self, usage: str):
        if isinstance(usage, str):
            self.elements["workflow"]["usage"] = usage
        else:
            raise ValueError(f"Usage {usage} is not a string")
        return self

    def update_author(self, author: str):
        if isinstance(author, str):
            self.elements["workflow"]["author"] = author
        else:
            raise ValueError(f"Author {author} is not a string")
        return self

    def annotate_action(self, step: Optional[int] = None) -> Union[WorkflowAction, list[WorkflowAction]]:
        actions = self.elements["workflow"]["action"]
        if isinstance(step, int) and 0 <= step < len(actions):
            print(f"Get step {step} action {actions[step].get()}")
            return actions[step]
        else:
            print(f"Get total {len(actions)} action, you can use .get() method to get action details")
            return actions

    def get_descriptions(self):
        self._convert_elements_to_descriptions()
        return self._descriptions

    def save(self, path=None):
        self._convert_elements_to_descriptions()
        super().save(path)
