from abc import ABC
from .abstract_annotator import AbstractAnnotator
from typing import Literal

from fhir_cda.ehr import ObservationMeasurement, DocumentReferenceMeasurement, ImagingStudyMeasurement
import json

from ..utils import check_first_file_extension
import copy
from pathlib import Path


class MeasurementAnnotator(AbstractAnnotator, ABC):

    def __init__(self, dataset_path, mode="default"):
        """

        :param dataset_path:
        :param mode: string, "default" or "update"
        """
        super().__init__(dataset_path, "measurements")
        self._patient_paths = []
        self.elements = {}
        if mode == "update":
            self._read_measurements()
        else:
            self._analysis_dataset()

    def _read_measurements(self):
        measurements_path = self._root / "measurements.json"
        if not measurements_path.exists():
            raise ValueError("Measurements json file does not exist!")
        else:
            with open(measurements_path, "r") as f:
                self._descriptions = json.load(f)
                self._convert_descriptions_to_elements()

    def _convert_descriptions_to_elements(self):
        self.elements["dataset"] = copy.deepcopy(self._descriptions["dataset"])
        self.elements["patients"] = []
        for idx, p in enumerate(self._descriptions.get("patients", [])):
            patient_element = {
                "uuid": p.get("uuid", ""),
                "name": p.get("name", ""),
                "observations": [ObservationMeasurement().set(o) for o in p.get("observations", [])],
                "imagingStudy": [ImagingStudyMeasurement().set(i) for i in p.get("imagingStudy", [])],
                "documentReference": [DocumentReferenceMeasurement().set(d) for d in p.get("documentReference", [])],
            }
            self.elements["patients"].append(patient_element)
        self.elements["patients"] = sorted(self.elements["patients"], key=lambda x: x["name"])

    def _convert_elements_to_descriptions(self):
        self._descriptions["dataset"] = copy.deepcopy(self.elements["dataset"])
        self._descriptions["patients"] = []
        for idx, p in enumerate(self.elements.get("patients", [])):
            patient_description = {
                "uuid": p.get("uuid", ""),
                "name": p.get("name", ""),
                "observations": [observationMeasurement.get() for observationMeasurement in p.get("observations", [])],
                "imagingStudy": [imagingStudyMeasurement.get() for imagingStudyMeasurement in
                                 p.get("imagingStudy", [])],
                "documentReference": [documentReferenceMeasurement.get() for documentReferenceMeasurement in
                                      p.get("documentReference", [])]

            }
            self._descriptions["patients"].append(patient_description)
        self._descriptions["patients"] = sorted(self._descriptions["patients"], key=lambda x: x["name"])

    def _analysis_dataset(self):
        primary_folder = self._root / "primary"
        if not primary_folder.exists():
            self.elements = {}
            raise ValueError(
                'The dataset structure is not based on a SPARC SDS dataset format, please check it and try again!')
        self.elements["dataset"] = {
            "uuid": "",
            "name": self._root.name,
        }
        self.elements["patients"] = []
        self._patient_paths = [x for x in primary_folder.iterdir() if x.is_dir()]
        for p in self._patient_paths:
            patient = {
                "uuid": "",
                "name": p.name,
                "observations": [],
                "imagingStudy": [],
                "documentReference": [],
            }
            self.elements["patients"].append(patient)

    def automated_generating_imaging_study_measurement_by_scan_dataset(self):
        for path, patient in zip(self._patient_paths, self.elements["patients"]):
            patient["imagingStudy"] = self._analysis_imaging_study_samples(path)
        return self

    @staticmethod
    def _analysis_imaging_study_samples(study):
        imaging_studies = []
        if study.exists():
            sams = [x for x in study.iterdir() if x.is_dir()]
            if len(sams) < 1:
                return imaging_studies
            else:
                dcm_sams = [sam for sam in sams if check_first_file_extension(sam) == "dcm"]
                nrrd_sams = [sam for sam in sams if check_first_file_extension(sam) == "nrrd"]

            if len(dcm_sams) > 0:
                imaging_study = ImagingStudyMeasurement(sample_details=dcm_sams, description="dcm")
                if len(imaging_study.series) > 0:
                    imaging_studies.append(imaging_study)
            if len(nrrd_sams) > 0:
                imaging_study = ImagingStudyMeasurement(sample_details=nrrd_sams, description="nrrd")
                if len(imaging_study.series) > 0:
                    imaging_studies.append(imaging_study)
        return imaging_studies

    def add_measurements(self, subjects, measurements):
        self.add_measurement(subjects, measurements)
        return self

    def add_measurement(self, subjects, measurement):
        if isinstance(subjects, list) and isinstance(measurement, list):
            for s in subjects:
                self.add_measurements_by_subject(s, measurement)
        elif isinstance(subjects, list) and isinstance(measurement, (
                ObservationMeasurement, DocumentReferenceMeasurement, ImagingStudyMeasurement)):
            m = measurement
            for s in subjects:
                self.add_measurement_by_subject(s, m)
        elif isinstance(subjects, str) and isinstance(measurement, list):
            s = subjects
            for m in measurement:
                self.add_measurement_by_subject(s, m)
        elif isinstance(subjects, str) and isinstance(measurement, (
                ObservationMeasurement, DocumentReferenceMeasurement, ImagingStudyMeasurement)):
            s = subjects
            m = measurement
            self.add_measurement_by_subject(s, m)
        return self

    def add_measurements_by_subject(self, subject, measurements):
        s = subject
        for m in measurements:
            self.add_measurement_by_subject(s, m)

        return self

    def add_measurement_by_subject(self, subject, measurement):
        if not isinstance(subject, str):
            raise ValueError(f"subject={subject} is not an instance of type str")
        if not isinstance(measurement, (ObservationMeasurement, DocumentReferenceMeasurement, ImagingStudyMeasurement)):
            raise ValueError(f"measurement={measurement} is not an instance of type Measurement")
        subject_path = self._root / "primary" / subject
        if not subject_path.exists():
            raise ValueError(f"subject_path={subject_path} is not exists")

        matched_patient = self._find_matched_patient(subject)
        assert isinstance(matched_patient, dict)

        if measurement.measurement_type == "ObservationMeasurement":
            matched_patient["observations"].append(measurement)
        elif measurement.measurement_type == "DocumentReferenceMeasurement":
            matched_patient["documentReference"].append(measurement)
        elif measurement.measurement_type == "ImagingStudyMeasurement":
            matched_patient["imagingStudy"].append(measurement)
        return self

    def update_dataset(self, field, value):
        if field not in self.elements.get("dataset"):
            raise ValueError(f"field {field} is not in descriptions['dataset']")
        else:
            self.elements["dataset"][field] = value

    def update_patient(self, subject, field, value):
        matched_patient = self._find_matched_patient(subject)
        if field not in matched_patient:
            raise ValueError(f"field {field} is not in descriptions['patient']")
        elif field in ["observations", "documentReference", "imagingStudy"]:
            print(
                f"detected your want to update {subject}'s {field} measurements, now forward you to update_patient_measurements() method.")
            if field == "observations":
                self.update_patient_measurements(subject, "ObservationMeasurement")
            elif field == "documentReference":
                self.update_patient_measurements(subject, "DocumentReferenceMeasurement")
            elif field == "imagingStudy":
                self.update_patient_measurements(subject, "ImagingStudyMeasurement")

        else:
            matched_patient[field] = value
        return self

    def update_patient_measurements(self,
                                    subject: str,
                                    category: Literal[
                                        "ObservationMeasurement",
                                        "ImagingStudyMeasurement",
                                        "DocumentReferenceMeasurement"]):
        matched_patient = self._find_matched_patient(subject)

        if category == "ObservationMeasurement":
            return matched_patient["observations"]
        elif category == "ImagingStudyMeasurement":
            return matched_patient["imagingStudy"]
        elif category == "DocumentReferenceMeasurement":
            return matched_patient["documentReference"]
        else:
            raise ValueError(
                f"Unrecognized category '{category}', only accepted values are ObservationMeasurement, ImagingStudyMeasurement, and DocumentReferenceMeasurement.")

    def _find_matched_patient(self, subject):
        matched_patients = [p for p in self.elements.get("patients", []) if
                            p.get("name") == subject]
        if len(matched_patients) == 0:
            raise ValueError(f"No patients found for {subject}")
        matched_patient = matched_patients[0]
        return matched_patient

    def get_descriptions(self):
        self._convert_elements_to_descriptions()
        return self._descriptions

    def save(self, path=None):
        self._convert_elements_to_descriptions()
        super().save(path)
