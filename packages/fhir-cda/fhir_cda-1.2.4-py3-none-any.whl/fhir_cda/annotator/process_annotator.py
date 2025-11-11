from abc import ABC
from .abstract_annotator import AbstractAnnotator
from typing import Literal, Dict, Any

from fhir_cda.ehr import ObservationMeasurement, DocumentReferenceMeasurement, ImagingStudyMeasurement, \
    ObservationValue, Quantity, DocumentAttachment
import json
import mimetypes
from ..utils import check_first_file_extension, read_dataset_samples, get_current_formated_time
import copy
from pathlib import Path
import uuid
import warnings

mimetypes.add_type("model/obj", ".obj")


class ProcessAnnotator(AbstractAnnotator, ABC):

    def __init__(self, dataset_path: Path, mapping: Dict[str, Any]):

        super().__init__(dataset_path, "process")

        self._patient_paths = []
        self._patients = {}
        self._sample_descriptions = {}
        self.elements = {}
        self._mapping = mapping

        # start to analysis workflow process result dataset
        self._analysis_dataset()

    def _convert_elements_to_descriptions(self):
        self._descriptions["process"] = copy.deepcopy(self.elements["process"])
        for c in self._descriptions["process"]["cohort"]:
            for p in c["processes"]:
                outputs = []
                for o in p["outputs"]:
                    outputs.append(o.get())
                p["outputs"] = outputs

    def _analysis_dataset(self):
        primary_folder = self._root / "primary"

        sample_description = read_dataset_samples(self._root)
        all_annotated_outputs = [o for tool in self._mapping["workflow"]["tools"] for o in tool.get("outputs", [])]
        for key in sample_description:
            annotated_output = next((o for o in all_annotated_outputs if o["name"] == sample_description[key]), None)
            if annotated_output is None:
                continue
            self._sample_descriptions[key] = {
                "name": sample_description[key],
                "annotation": annotated_output,
            }

        if not primary_folder.exists():
            self.elements = {}
            raise ValueError(
                'The dataset structure is not based on a SPARC SDS dataset format, please check it and try again!')
        self.elements["process"] = {
            "study": {
                "uuid": "",
                "name": ""
            },
            "researcher": {
                "uuid": ""
            },
            "assay": {
                "uuid": "",
                "name": ""
            },
            "dataset": {
                "uuid": "",
                "name": ""
            },
            "workflow": self._mapping["workflow"].get("uuid", ""),
            "cohort": []
        }

        for patient_dir in primary_folder.iterdir():
            if not patient_dir.is_dir():
                continue

            patient_name = patient_dir.name
            self._patients[patient_name] = {}
            cohort = {
                "uuid": self._mapping["result"][patient_name]["uuid"],
                "processes": []
            }

            for sample_dir in patient_dir.iterdir():
                if not sample_dir.is_dir():
                    continue
                sample_name = sample_dir.name
                resource = self._analysis_samples(sample_dir)
                if resource:
                    self._patients[patient_name][sample_name] = resource

            for tool in self._mapping["workflow"].get("tools", []):
                process_description = {
                    "uuid": str(uuid.uuid4()),
                    "tool_uuid": tool.get("uuid", ""),
                    "date": get_current_formated_time(),
                    "inputs": [],
                    "outputs": []
                }
                for m in self._mapping["measurements"]:
                    for sam in m[patient_name]['sams']:
                        input_data = next((i for i in tool['inputs'] if i['name'] == sam['sample_type']), None)
                        if input_data is None:
                            continue
                        process_description["inputs"].append({
                            "uuid": sam.get("uuid", ""),
                            "resourceType": input_data.get("resource", ""),
                        })
                for sam in self._patients[patient_name].values():
                    output_data = next((o for o in tool['outputs'] if o['name'] == sam['sample_type']), None)
                    if output_data is None:
                        continue
                    process_description["outputs"].append(sam["resource"])

                cohort["processes"].append(process_description)

            self.elements["process"]["cohort"].append(cohort)

    def _analysis_samples(self, sam_dir):
        first_file_suffix = check_first_file_extension(sam_dir)
        if first_file_suffix:
            try:
                if first_file_suffix == 'nii.gz' or first_file_suffix == "dcm" or first_file_suffix == "nrrd":
                    if self._sample_descriptions[sam_dir.name]["annotation"]["resource"] != "ImagingStudy":
                        msg = f"Annotation Error: the tool annotation shows this sample is '{self._sample_descriptions[sam_dir.name]['annotation']['resource']}' resource, but process annotator detect it should be 'ImagingStudy' resource."
                        warnings.warn(msg)

                    imaging_study = self._analysis_imaging_study_samples(sam_dir, first_file_suffix)
                    imaging_study["resource"].get_series()[0].set_name(self._sample_descriptions[sam_dir.name]["name"])
                    return imaging_study
                elif first_file_suffix == 'txt':
                    if self._sample_descriptions[sam_dir.name]["annotation"]["resource"] != "Observation":
                        msg = f"Annotation Error: the tool annotation shows this sample is '{self._sample_descriptions[sam_dir.name]['annotation']['resource']}' resource, but process annotator detect it should be 'Observation' resource."
                        warnings.warn(msg)

                    ob = self._analysis_observation_samples(sam_dir,
                                                            self._sample_descriptions[sam_dir.name]["annotation"])
                    return ob
                else:
                    if self._sample_descriptions[sam_dir.name]["annotation"]["resource"] != "DocumentReference":
                        msg = f"Annotation Error: the tool annotation shows this sample is '{self._sample_descriptions[sam_dir.name]['annotation']['resource']}' resource, but process annotator detect it should be 'DocumentReference' resource."
                        warnings.warn(msg)

                    document = self._analysis_document_samples(sam_dir)
                    return document
            except Exception as e:
                msg = f"The outputs annotation is not match the real dataset samples: {e}"
                warnings.warn(msg)
                return None
        else:
            raise ValueError(f"No valid files found in sample directory: {sam_dir}")

    def _analysis_imaging_study_samples(self, sam_dir: Path, first_file_suffix: str):
        if sam_dir.exists():
            result_sam = next(
                (r for r in self._mapping["result"][sam_dir.parent.name]["sams"] if r["name"] == sam_dir.name), None)
            return {
                "resource": ImagingStudyMeasurement(uuid=result_sam.get("uuid", "") if result_sam else "",
                                                    endpoint_url=result_sam.get("url", "") if result_sam else "",
                                                    sample_details=[sam_dir], description=first_file_suffix),
                "sample_type": self._sample_descriptions[sam_dir.name]["name"],
            }

        return None

    def _analysis_observation_samples(self, sam_dir: Path, annotation):
        files = [f for f in sam_dir.iterdir() if f.is_file()]
        # TODO single value
        if len(files) == 0:
            return None
        # TODO component
        first_file = files[0]

        with open(first_file, "r", encoding="utf-8") as f:
            value = f.read()

        try:
            result_sam = next(
                (r for r in self._mapping["result"][sam_dir.parent.name]["sams"] if r["name"] == sam_dir.name), None)
            return {
                "resource": ObservationMeasurement(
                    uuid=result_sam.get("uuid", "") if result_sam else "",
                    value=ObservationValue(value_quantity=Quantity(value=float(value), unit=annotation.get("unit", ""),
                                                                   code=annotation.get("unit", ""))),
                    code_system=annotation.get("system", ""),
                    code=annotation.get("code", "")
                ),
                "sample_type": self._sample_descriptions[sam_dir.name]["name"]
            }
        except ValueError:
            raise ValueError("Observation measurement value only supports floats")

    def _analysis_document_samples(self, sam_dir: Path):
        attachments = []
        result_sam = next(
            (r for r in self._mapping["result"][sam_dir.parent.name]["sams"] if r["name"] == sam_dir.name), None)
        for f in sam_dir.iterdir():
            if f.is_file():
                mime_type, encoding = mimetypes.guess_type(f)
                attachments.append(
                    DocumentAttachment(url=f"{result_sam.get('url', '') if result_sam else ''}/{f.name}",
                                       content_type=mime_type if mime_type else "None"))

        return {
            "resource": DocumentReferenceMeasurement(attachments=attachments,
                                                     uuid=result_sam.get("uuid", "") if result_sam else "",
                                                     title=self._sample_descriptions[sam_dir.name]["name"]),
            "sample_type": self._sample_descriptions[sam_dir.name]["name"]
        }

    def update_study(self, uid: str = None, name: str = None):
        if not isinstance(uid, str):
            raise ValueError("uid must be a string")
        if not isinstance(name, str):
            raise ValueError("name must be a string")
        if uid is not None:
            self.elements["process"]["study"]["uuid"] = uid
        if name is not None:
            self.elements["process"]["study"]["name"] = name
        return self

    def update_assay(self, uid: str = None, name: str = None):
        if not isinstance(uid, str):
            raise ValueError("uid must be a string")
        if not isinstance(name, str):
            raise ValueError("name must be a string")
        if uid is not None:
            self.elements["process"]["assay"]["uuid"] = uid
        if name is not None:
            self.elements["process"]["assay"]["name"] = name
        return self

    def update_researcher(self, uid: str):
        if not isinstance(uid, str):
            raise ValueError("uid must be a string")
        self.elements["process"]["researcher"]["uuid"] = uid
        return self

    def update_dataset(self, uid: str = None, name: str = None):
        if not isinstance(uid, str):
            raise ValueError("uid must be a string")
        if not isinstance(name, str):
            raise ValueError("name must be a string")
        if uid is not None:
            self.elements["process"]["dataset"]["uuid"] = uid
        if name is not None:
            self.elements["process"]["dataset"]["name"] = name
        return self

    def get_descriptions(self):
        self._convert_elements_to_descriptions()
        return self._descriptions

    def save(self, path=None):
        self._convert_elements_to_descriptions()
        super().save(path)
