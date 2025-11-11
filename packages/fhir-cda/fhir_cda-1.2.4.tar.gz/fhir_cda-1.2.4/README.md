# Clinical Description Annotator

![Python3.9+](https://img.shields.io/badge/python_3.9+-34d399)
![PyPI - Version](https://img.shields.io/pypi/v/fhir-cda)

Annotator for annotating measurement results, workflows, workflow tools, models, and workflow tool process datasets in
SPARC SDS datasets to the data format required for [digitaltwins-on-fhir](https://pypi.org/project/digitaltwins-on-fhir/).

## Usage

## Annotate the measurements data for SPARC SDS dataset

- Add measurement for one patient

```py
from fhir_cda import Annotator
from fhir_cda.ehr import ObservationMeasurement, ObservationValue, Quantity

annotator = Annotator("./dataset/dataset-sparc").measurements()

m = ObservationMeasurement(
    value=ObservationValue(
        value_quantity=Quantity(
            value=30,
            unit="year",
            code="a")),
    code="30525-0")

annotator.add_measurements("sub-001", m).save()
```

- Add measurements for one patient

```py
m1 = ObservationMeasurement(
    value=ObservationValue(
        value_quantity=Quantity(
            value=0.15,
            unit="cm",
            code="cm")),
    code="21889-1")
m2 = ObservationMeasurement(
    value=ObservationValue(
        value_quantity=Quantity(
            value=0.15,
            unit="cm",
            code="cm",
            system="http://unitsofmeasure.org")),
    code="21889-1",
    code_system="http://loinc.org",
    display="Size Tumor")
annotator.add_measurements("sub-001", [m1, m2]).save()
```

- Add measurement for multiple patients

```py
m = ObservationMeasurement(
    value=ObservationValue(value_string="Female"),
    code="99502-7",
    display="Recorded sex or gender",
    code_system="http://loinc.org")
annotator.add_measurements(["sub-001", "sub-002"], m).save()
```

- A measurements for multiple patients

```py
m1 = ObservationMeasurement(
    value=ObservationValue(value_string="Female"),
    code="99502-7",
    display="Recorded sex or gender",
    code_system="http://loinc.org")
m2 = ObservationMeasurement(
    value=ObservationValue(
        value_quantity=Quantity(
            value=0.15,
            unit="cm",
            code="cm",
            system="http://unitsofmeasure.org")),
    code="21889-1",
    code_system="http://loinc.org",
    display="Size Tumor")
annotator.add_measurements(["sub-001", "sub-002"], [m1, m2])
annotator.save()
```
- Add DocumentReference measurements
```python
from fhir_cda.ehr import DocumentReferenceMeasurement
m2 = DocumentReferenceMeasurement(
    url="https://example.org/files/df0c4efd-69a6-428a-ba70-786caecfadfb.obj",
    content_type="model/obj",
    title="Breast Surface Mesh")
annotator.add_measurements(["sub-001"], [m2]).save()
```

- Automated generating ImagingStudy Measurement for all patients by scan dataset 
```python
annotator.automated_generating_imaging_study_measurement_by_scan_dataset()
```

- Add ImagingStudy measurements manually
    - Note: If we add it manually, we'll need to add the ImagingStudy measurement for each patient one by one. Alternatively, we can use a loop to automate the process.
```python
from fhir_cda.ehr import ImagingStudyMeasurement
from fhir_cda.utils import check_first_file_extension
from pathlib import Path

p1 = Path("./dataset/dataset-sparc/primary/sub-001")
p1_sams = [x for x in p1.iterdir() if x.is_dir()]
p1_dcm_sams = [sam for sam in p1_sams if check_first_file_extension(sam) == "dcm"]
m4 = ImagingStudyMeasurement(uuid="",
                             sample_paths=p1_dcm_sams,
                             endpoint_url="",
                             description="dcm")
annotator.add_measurements(["sub-001"], [m4])
```


- Notice: The default value for `unit system` and `code system` are:

```python
unit_system = "http://unitsofmeasure.org"
code_system = "http://loinc.org"
```

## Design Decisions
- `ImagingStudy Instances` are not include at this stage, because but can be added it if required. 

## Contributors

Linkun Gao

Chinchien Lin

Ayah Elsayed

Jiali Xu

Gregory Sands

David Nickerson

Thiranja Prasad Babarenda Gamage

## Publications

1. **[Paper Title One](https://doi.org/...)**, Author1, Author2. *Journal Name*, Year.
2. **[Paper Title Two](https://arxiv.org/abs/...)**, Author1, Author2. *Conference Name*, Year.

Please cite the corresponding paper if you use this project in your research.

