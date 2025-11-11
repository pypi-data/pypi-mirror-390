from typing import Optional, Literal, List

InputResourceType = ["Observation", "ImagingStudy", "DocumentReference", ""]
OutputResourceType = ["DiagnosticReport", *InputResourceType]


class WorkflowGoal:

    def __init__(self, description):
        self.description = description if isinstance(description, str) else str(description)

    def get(self):
        goal = {
            "description": self.description
        }
        return {k: v for k, v in goal.items() if v not in ("", None)}


class WorkflowActionInput:

    def __init__(self, display: str, resource_type: Literal["Observation", "ImagingStudy", "DocumentReference", ""] = ""
                 ):
        if not isinstance(display, str):
            raise ValueError(f"display should be a string")
        self.resource_type = resource_type
        self.display = display

    def set_resource_type(self, resource_type: Literal["Observation", "ImagingStudy", "DocumentReference"]):
        if resource_type not in InputResourceType:
            raise ValueError(f"resource_type should be one of {InputResourceType}")
        self.resource_type = resource_type
        return self

    def get(self):
        action_input = {
            "resource_type": self.resource_type,
            "display": self.display,
        }
        return {k: v for k, v in action_input.items() if v not in ("", None)}


class WorkflowActionOutput:
    def __init__(self, display: str,
                 resource_type: Literal["Observation", "ImagingStudy", "DocumentReference", ""] = "",
                 code: Optional = None,
                 system: Optional = None,
                 unit: Optional = None):
        if not isinstance(display, str):
            raise ValueError(f"display should be a string")
        self.resource_type = resource_type
        self.code = code
        self.system = system
        self.display = display
        self.unit = unit

    def set_resource_type(self, resource_type: Literal[
        "Observation", "ImagingStudy", "DocumentReference", "DiagnosticReport"]):
        print(OutputResourceType)
        if resource_type not in OutputResourceType:
            raise ValueError(f"resource_type should be one of {OutputResourceType}")
        self.resource_type = resource_type
        return self

    def set_code(self, code: str):
        if not isinstance(code, str):
            raise ValueError(f"code should be a string")
        self.code = code
        return self

    def set_system(self, system: str):
        if not isinstance(system, str):
            raise ValueError(f"system should be a string")
        self.system = system
        return self

    def set_unit(self, unit: str):
        if not isinstance(unit, str):
            raise ValueError(f"unit should be a string")
        self.unit = unit
        return self

    def get(self):
        action_output = {
            "resource_type": self.resource_type,
            "display": self.display,
            "code": self.code,
            "system": self.system,
            "unit": self.unit
        }
        if self.resource_type == "Observation":
            action_output["code"] = self.code
            action_output["system"] = self.system
            action_output["unit"] = self.unit
        return {k: v for k, v in action_output.items() if v not in ("", None)}


class WorkflowAction:
    def __init__(self, title: str, description: str, action_input: List[WorkflowActionInput],
                 action_output: List[WorkflowActionOutput], related_tool_uuid: str = ""):
        if not isinstance(title, str):
            raise ValueError(f"title should be a string")
        elif not isinstance(action_input, list):
            raise ValueError(f"action_input should be a WorkflowActionInput list")
        elif not isinstance(action_output, list):
            raise ValueError(f"action_output should be a WorkflowActionOutput list")

        self.title = title
        self.description = description if isinstance(description, str) else "No description available."
        self.related_tool_uuid = related_tool_uuid
        self.action_input = action_input
        self.action_output = action_output

    def set_related_tool_uuid(self, related_tool_uuid: str):
        if not isinstance(related_tool_uuid, str):
            raise ValueError(f"related_tool_uuid should be a string")
        self.related_tool_uuid = related_tool_uuid
        return self

    def annotate_input(self) -> list[WorkflowActionInput]:
        return self.action_input

    def annotate_output(self) -> list[WorkflowActionOutput]:
        return self.action_output

    def get(self):
        action = {
            "title": self.title,
            "description": self.description,
            "related_tool_uuid": self.related_tool_uuid,
            "input": [action_input.get() for action_input in self.action_input if
                      isinstance(action_input, WorkflowActionInput)],
            "output": [action_output.get() for action_output in self.action_output if
                       isinstance(action_output, WorkflowActionOutput)]
        }
        return {k: v for k, v in action.items() if v not in ("", None)}
