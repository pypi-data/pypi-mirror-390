from typing import Optional, List
from .elements import ObservationValue, ImagingStudySeries, ImagingStudySeriesInstance, DocumentAttachment
import pydicom
from pydicom.uid import UID
from fhir_cda.terms import SNOMEDCT
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path


class ObservationMeasurement:
    def __init__(self, value: Optional[ObservationValue] = None, code: Optional[str] = "",
                 code_system="http://loinc.org",
                 unit: Optional[str] = None,
                 display: Optional[str] = None, uuid: Optional[str] = ""):

        if value is not None and not isinstance(value, ObservationValue):
            raise ValueError(f"value={value} is not an ObservationValue type")
        elif not isinstance(code, str):
            raise ValueError(f"code={code} is not an instance of type str")
        elif unit is not None and not isinstance(unit, str):
            raise ValueError(f"unit={unit} is not an instance of type str")
        elif display is not None and not isinstance(display, str):
            raise ValueError(f"display={display} is not an instance of type str")
        elif not isinstance(uuid, str):
            raise ValueError(f"uuid={uuid} is not an instance of type str")

        self.measurement_type = "ObservationMeasurement"
        self.uuid = uuid
        self.value = value
        self.code = code
        self.unit = unit
        self.code_system = code_system
        self.display = display

    def __repr__(self):
        return (
            f"ObservationMeasurement(uuid={self.uuid},value={self.value}, code='{self.code}', value_system='{self.code_system}')")

    def set(self, item):
        self.uuid = item.get("uuid", "")
        self.code = item.get("code", "")
        self.display = item.get("display", "")
        self.code_system = item.get("codeSystem", "")
        self.unit = item.get("unit", "")
        value = item.get("value", None)
        self.value = ObservationValue().set(value) if value is not None else None
        return self

    def set_uuid(self, uuid: str):
        self.uuid = uuid
        return self

    def set_value(self, value: ObservationValue):
        self.value = value
        return self

    def set_unit(self, unit: str):
        self.unit = unit
        return self

    def set_code_system(self, code_system: str):
        self.code_system = code_system
        return self

    def set_display(self, display: str):
        self.display = display
        return self

    def set_code(self, code: str):
        self.code = code
        return self

    def get(self):
        measurement = {
            "resourceType": "Observation",
            "uuid": self.uuid,
            "value": self.value.get(),
            "code": self.code,
            "codeSystem": self.code_system,
            "unit": self.unit,
            "display": self.display if isinstance(self.display, str) else ""
        }
        return {k: v for k, v in measurement.items() if v is not None}



class DocumentReferenceMeasurement:
    def __init__(self, attachments: Optional[List[DocumentAttachment]] = None, title: Optional[str] = "",
                 uuid: Optional[str] = ""):
        if not (isinstance(attachments, list) and all(isinstance(item, DocumentAttachment) for item in attachments)):
            raise ValueError(f"attachments={attachments} is not an instance of type list")
        if not isinstance(title, str):
            raise ValueError(f"title={title} is not an instance of type str")
        elif not isinstance(uuid, str):
            raise ValueError(f"uuid={uuid} is not an instance of type str")

        self.measurement_type = "DocumentReferenceMeasurement"
        self.uuid = uuid
        self.attachments = attachments
        self.title = title

    def __repr__(self):
        return (
            f"DocumentReferenceMeasurement(uuid={self.uuid}, title={self.title})")

    def set(self, item):
        self.uuid = item.get("uuid", "")
        self.title = item.get("title", "")
        self.attachments = item.get("attachments", [])
        return self

    def set_uuid(self, uuid: str):
        self.uuid = uuid
        return self

    def set_attachments(self, attachments: List[DocumentAttachment]):
        if not isinstance(attachments, list):
            raise ValueError(f"attachments={attachments} is not an instance of type list")
        elif not all(isinstance(item, DocumentAttachment) for item in attachments):
            raise ValueError(f"attachments={attachments}: some attachments are not an DocumentAttachment type")
        self.attachments = attachments
        return self

    def set_title(self, title: str):
        self.title = title
        return self

    def get(self):
        measurement = {
            "resourceType": "DocumentReference",
            "uuid": self.uuid,
            "title": self.title,
            "attachments": [a.get() for a in self.attachments if isinstance(a, DocumentAttachment)]
        }
        return measurement


class ImagingStudyMeasurement:
    """
    uuid: Imaging Study Identifier, should be generated by digitaltwins-on-fhir, fhir-cda, digitaltwins platform or user.
    endpoint_uuid (ImagingStudy): Imaging Study endpoint Identifier, should be generated by digitaltwins-on-fhir and fhir-cda.
    endpoint_uuid (ImagingStudySeries): Imaging Study series endpoint Identifier, can be dataset's sample uuid which generated by digitaltwins platform or user.

    sample_details: str[] or Path[]
    """

    def __init__(self, uuid: str = "", sample_details: list = None, endpoint_url: str = "", description: str = ""):
        if sample_details is not None and not isinstance(sample_details, list):
            raise ValueError(f"samples={sample_details} is not an instance of type list")
        if not isinstance(uuid, str):
            raise ValueError(f"uuid={uuid} is not an instance of type str")
        if description is not None and not isinstance(description, str):
            raise ValueError(f"description={description} is not an instance of type str")
        if endpoint_url is not None and not isinstance(endpoint_url, str):
            raise ValueError(f"endpoint_url={endpoint_url} is not an instance of type str")

        self.measurement_type = "ImagingStudyMeasurement"
        self.uuid = uuid
        self.endpoint_url = endpoint_url
        self.description = description
        self.series = []
        self._samples = []

        if sample_details is not None:
            if len(sample_details) == 0:
                raise ValueError(f"sample_paths={sample_details} should have at least one instance.")
            for sample in sample_details:
                if isinstance(sample, str):
                    self._samples.append({
                        "uuid": "",
                        "path": Path(sample)
                    })
                elif isinstance(sample, Path):
                    self._samples.append({
                        "uuid": "",
                        "path": sample
                    })
                elif self._is_valid_sample_dict(sample):
                    if isinstance(sample["path"], str):
                        sample["path"] = Path(sample["path"])
                    self._samples.append(sample)
                else:
                    raise ValueError(f"sample type {type(sample)} is not a valid type.")
            self._generate_imaging_study()

    def __repr__(self):
        return (
            f"ImagingStudyMeasurement(uuid={self.uuid},endpointUrl={self.endpoint_url}, description={self.description}, series={len(self.series)})")

    @staticmethod
    def _is_valid_sample_dict(d):
        return (
                isinstance(d, dict)
                and "uuid" in d and isinstance(d["uuid"], str)
                and "path" in d and (isinstance(d["path"], Path) or isinstance(d["path"], str))
        )

    def set(self, item):
        self.uuid = item.get("uuid", "")
        self.endpoint_url = item.get("endpoint_url", "")
        self.description = item.get("description", "")
        if item.get("series", None) is not None:
            self.series = [ImagingStudySeries().set(s) for s in item.get("series")] if isinstance(item.get("series"),
                                                                                                  list) else []
        else:
            self.series = []

        return self

    def set_uuid(self, uuid):
        self.uuid = uuid
        return self

    def set_endpoint_url(self, endpoint_url):
        self.endpoint_url = endpoint_url
        return self

    def set_description(self, description):
        self.description = description
        return self

    def get(self):
        imaging_study_measurement = {
            "resourceType": "ImagingStudy",
            "uuid": self.uuid if isinstance(self.uuid, str) else "",
            "endpointUrl": self.endpoint_url if isinstance(self.endpoint_url, str) else "",
            "description": self.description if isinstance(self.description, str) else "",
            "series": [s.get() for s in self.series if isinstance(s, ImagingStudySeries)] if isinstance(self.series,
                                                                                                        list) else [],
        }
        return imaging_study_measurement

    def get_series(self):
        return self.series

    def _generate_imaging_study(self):

        primary_folder = self._samples[0]["path"].parent.parent
        patients_dirs = [x for x in primary_folder.iterdir() if x.is_dir()]

        if len(patients_dirs) < 5:
            for sam in self._samples:
                s = self._read_sam(sam)
                if s is not None:
                    self.series.append(s)
        else:
            self.series.extend(self._analysis_dicom_samples_worker(self._samples))

    def _read_sam(self, sam):
        try:
            dcm_files = list(sam["path"].glob("*.dcm"))
            nrrd_files = list(sam["path"].glob("*.nrrd"))
            nii_files = list(sam["path"].glob("*.nii.gz"))
            if len(dcm_files) < 1 and len(nrrd_files) < 1 and len(nii_files) < 1:
                return
            if (len(dcm_files) > 0 and len(nrrd_files) > 0) or (len(dcm_files) > 0 and len(nii_files) > 0) or (
                    len(nrrd_files) > 0 and len(nii_files) > 0):
                raise ValueError(
                    "dataset format error: Detected dcm, nii.gz and nrrd files under the same sample folder.")

            if len(dcm_files) >= 1:
                s_dicom_file = pydicom.dcmread(dcm_files[0])
                body_part_examined = s_dicom_file.get((0x0018, 0x0015), None)
                body_site = SNOMEDCT.get(body_part_examined.value.upper(),
                                         None) if body_part_examined is not None else None

                suid = s_dicom_file.get((0x0020, 0x000e), None)
                s = ImagingStudySeries(uid=suid.value if suid is not None else "",
                                       endpoint_url="",
                                       endpoint_uuid=sam["uuid"],
                                       name=sam["path"].name,
                                       number_of_instances=len(dcm_files),
                                       body_site=body_site,
                                       instances=self._analysis_dicom_sample_instances(dcm_files)
                                       )
                return s
            if len(nrrd_files) >= 1:
                s = ImagingStudySeries(uid=None,
                                       endpoint_url="",
                                       endpoint_uuid=sam["uuid"],
                                       name=sam["path"].name,
                                       number_of_instances=len(nrrd_files),
                                       instances=[]
                                       )
                return s
            if len(nii_files) >= 1:
                s = ImagingStudySeries(uid=None,
                                       endpoint_url="",
                                       endpoint_uuid=sam["uuid"],
                                       name=sam["path"].name,
                                       number_of_instances=len(nii_files),
                                       instances=[]
                                       )
                return s
        except Exception as e:
            print(f"Error reading {sam}: {e}")
            return None

    def _analysis_dicom_samples_worker(self, sams):
        samples = []
        max_workers = os.cpu_count()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(self._read_sam, sams)

        for result in results:
            if result is not None:
                samples.append(result)

        return samples

    @staticmethod
    def _analysis_dicom_sample_instances(dcms):
        instances = []
        # TODO: 14/05/2025 decision: not consider the instance level at this stage
        # for d in dcms:
        #     dcm = pydicom.dcmread(d)
        #
        #     # Get the SOP Class UID
        #     sop_class_uid = dcm.SOPClassUID
        #     # Get the SOP Class Name using the UID dictionary
        #     sop_class_name = UID(sop_class_uid).name
        #
        #     instance = ImagingStudySeriesInstance(uid=dcm[(0x0008, 0x0018)].value, sop_class_uid=sop_class_uid,
        #                                           sop_class_name=sop_class_name, number=dcm[(0x0020, 0x0013)].value)
        #
        #     # instance = {
        #     #     "uid": dcm[(0x0008, 0x0018)].value,
        #     #     "sopClassUid": sop_class_uid,
        #     #     "sopClassName": sop_class_name,
        #     #     "number": dcm[(0x0020, 0x0013)].value
        #     # }
        #    instances.append(instance)
        return instances
