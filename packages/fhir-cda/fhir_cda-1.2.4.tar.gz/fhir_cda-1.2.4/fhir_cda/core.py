from pathlib import Path
from .annotator import MeasurementAnnotator, WorkflowAnnotator, WorkflowToolAnnotator, ProcessAnnotator
from typing import Dict, Any


class Annotator:
    measurement_annotator = MeasurementAnnotator
    workflow_annotator = WorkflowAnnotator
    workflow_tool_annotator = WorkflowToolAnnotator
    process_annotator = ProcessAnnotator

    def __init__(self, dataset_path):
        self.root = Path(dataset_path)

    def measurements(self, mode="default"):
        """
        :param mode: string, "default" for default mode, "update" for update mode
        :return:
        """
        return self.measurement_annotator(self.root, mode)

    def workflow(self):
        return self.workflow_annotator(self.root)

    def workflow_tool(self):
        return self.workflow_tool_annotator(self.root)

    def process(self, mapping: Dict[str, Any]):
        """
           Expected `assay_map` structure:

               {
                   "measurements": [
                       {
                           "sub-1": {
                               "uuid": "subject uuid (str)",

                               "sams": [
                                   {"uuid": "sample uuid (str)", "sample_type": "str"}
                               ]
                           }
                       }
                   ],

                   "results": [
                       {
                           "sub-1": {
                               "uuid": "subject uuid (str)",

                               "sams": [
                                   {"dataset": "dataset uuid (str)", "dataset_name": "dataset_name (str)", "uuid": "sample uuid (str)", "name": "sample name (str)", "url": "sample folder url (str)"}
                               ]
                           }
                       }
                   ],

                   "workflow": {
                       "uuid": "workflow uuid (str)",

                       "tools": [
                           {
                               "uuid": "tool uuid (str)",

                               "inputs": [
                                   {"name": "str", "resource": "str"}
                               ],

                               "outputs": [
                                   {"name": "str", "resource": "str", "code": "str", "system": "str", "unit": "str"}
                               ]
                           }
                       ]
                   }
               }

           Args:
               mapping (dict): Mapping dictionary describing measurements and workflow.
        """
        return self.process_annotator(self.root, mapping)
