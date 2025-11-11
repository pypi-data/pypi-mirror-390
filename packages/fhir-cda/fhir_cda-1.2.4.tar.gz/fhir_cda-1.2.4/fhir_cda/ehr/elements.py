from typing import Optional, Literal, List, Union


class Quantity:
    def __init__(self, value: Optional[float] = None, comparator: Optional[Literal["<", "<=", ">=", ">"]] = None,
                 unit: Optional[str] = None, system: Optional[str] = "http://unitsofmeasure.org",
                 code: Optional[str] = None):
        """
        :param value: Numerical value (with implicit precision) for Observation
        :param comparator: < | <= | >= | > - how to understand the value
        :param unit: Unit representation
        :param system: System that defines coded unit form
        :param code: Coded form of the unit
        """
        self.value = value
        self.comparator = comparator
        self.unit = unit
        self.system = system
        self.code = code

    def get(self):
        quantity = {
            "value": self.value if isinstance(self.value, float) or isinstance(self.value, int) else None,
            "comparator": self.comparator if self.comparator in ["<", "<=", ">=", ">"] else None,
            "unit": self.unit if isinstance(self.unit, str) else None,
            "system": self.system if isinstance(self.system, str) else None,
            "code": self.code if isinstance(self.code, str) else None
        }
        return {k: v for k, v in quantity.items() if v not in ("", None)}


class Coding:

    def __init__(self, system: str = "", version: str = "", code: str = "", display: Optional[str] = None,
                 user_selected: Optional[bool] = None):
        self.system = system
        self.version = version
        self.code = code
        self.display = display
        self.user_selected = user_selected

    def get(self):
        coding = {
            "system": self.system if isinstance(self.system, str) else None,
            "version": self.version if isinstance(self.version, str) else None,
            "code": self.code if isinstance(self.code, str) else None,
            "display": self.display if isinstance(self.display, str) else None,
            "userSelected": self.user_selected if isinstance(self.user_selected, bool) else None
        }
        return {k: v for k, v in coding.items() if v not in ("", None)}


class CodeableConcept:

    def __init__(self, codings: List[Coding] = None, text: str = ""):
        self.codings = codings
        self.text = text

    def get(self):
        codeableconcept = {
            "coding": [coding.get() for coding in self.codings if isinstance(coding, Coding)] if isinstance(
                self.codings, list) else None,
            "text": self.text if isinstance(self.text, str) else None
        }

        return {k: v for k, v in codeableconcept.items() if v not in ("", None, [])}


class Range:

    def __init__(self, low: Optional[float] = None, high: Optional[float] = None):
        self.low = low
        self.high = high

    def get(self):
        _range = {
            "low": self.low if isinstance(self.low, float) else None,
            "high": self.high if isinstance(self.high, float) else None
        }
        return {k: v for k, v in _range.items() if v not in ("", None)}


class Ratio:

    def __init__(self, numerator: Optional[Quantity] = None, denominator: Optional[Quantity] = None):
        self.numerator = numerator
        self.denominator = denominator

    def get(self):
        ratio = {
            "numerator": self.numerator.get() if isinstance(self.numerator, Quantity) else None,
            "denominator": self.denominator.get() if isinstance(self.denominator, Quantity) else None
        }
        return {k: v for k, v in ratio.items() if v not in ("", None)}


class SampledData:

    def __init__(self, origin: str, period: float, dimensions: int, factor: Optional[float] = None,
                 lower_limit: Optional[float] = None, upper_limit: Optional[float] = None, data: Optional[str] = None):
        self.origin = origin
        self.period = period
        self.dimensions = dimensions
        self.factor = factor
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.data = data

    def get(self):
        sampled_data = {
            "origin": self.origin if isinstance(self.origin, str) else None,
            "period": self.period if isinstance(self.period, float) else None,
            "factor": self.factor if isinstance(self.factor, float) else None,
            "lowerLimit": self.lower_limit if isinstance(self.lower_limit, float) else None,
            "upperLimit": self.upper_limit if isinstance(self.upper_limit, float) else None,
            "dimensions": self.dimensions if isinstance(self.dimensions, int) and self.dimensions > 0 else None,
            "data": self.data if isinstance(self.data, str) else None
        }
        return {k: v for k, v in sampled_data.items() if v not in ("", None)}


class Period:

    def __init__(self, start: str = '', end: str = ''):
        self.start = start
        self.end = end

    def get(self):
        period = {
            "start": self.start if isinstance(self.start, str) else None,
            "end": self.end if isinstance(self.end, str) else None
        }
        return {k: v for k, v in period.items() if v not in ("", None)}


class ObservationValue:

    def __init__(self, value_quantity: Optional[Quantity] = None,
                 value_codeable_concept: Optional[CodeableConcept] = None, value_string: Optional[str] = None,
                 value_boolean: Optional[bool] = None, value_integer: Optional[int] = None,
                 value_range: Optional[Range] = None, value_ratio: Optional[Ratio] = None,
                 value_sampled_data: Optional[SampledData] = None, value_time: Optional[str] = None,
                 value_date_time: Optional[str] = None, value_period: Optional[Period] = None):
        self.value_quantity = value_quantity
        self.value_codeable_concept = value_codeable_concept
        self.value_string = value_string
        self.value_boolean = value_boolean
        self.value_integer = value_integer
        self.value_range = value_range
        self.value_ratio = value_ratio
        self.value_sampled_data = value_sampled_data
        self.value_time = value_time
        self.value_date_time = value_date_time
        self.value_period = value_period

    def set(self, item):
        keys = list(item.keys())
        if "valueQuantity" in keys:
            quantity = item["valueQuantity"]
            self.value_quantity = Quantity(value=quantity.get("value", None),
                                           unit=quantity.get("unit", None),
                                           code=quantity.get("code", None),
                                           comparator=quantity.get("comparator", None),
                                           system=quantity.get("system", None))
        elif "valueCodeableConcept" in keys:
            codeableconcept = item["valueCodeableConcept"]
            self.value_codeable_concept = CodeableConcept(text=codeableconcept.get("text", None),
                                                          codings=[Coding(system=c.get("system", None),
                                                                          version=c.get("version", None),
                                                                          display=c.get("display", None),
                                                                          code=c.get("code", None),
                                                                          user_selected=c.get("userSelected", None)) for
                                                                   c in codeableconcept.get("codings", [])])
        elif "valueString" in keys:
            self.value_string = item["valueString"]

        elif "valueBoolean" in keys:
            self.value_boolean = item["valueBoolean"]
        elif "valueInteger" in keys:
            self.value_integer = item["valueInteger"]
        elif "valueTime" in keys:
            self.value_time = item["valueTime"]
        elif "valueDateTime" in keys:
            self.value_date_time = item["valueDateTime"]
        elif "valueRange" in keys:
            value_range = item["valueRange"]
            self.value_range = Range(low=value_range.get("low", None),
                                     high=value_range.get("high", None))
        elif "valueRatio" in keys:
            value_ratio = item["valueRatio"]
            numerator = value_ratio.get("numerator", None)
            denominator = value_ratio.get("denominator", None)
            self.value_ratio = Ratio(numerator=Quantity(value=numerator.get("value", None),
                                                        unit=numerator.get("unit", None),
                                                        code=numerator.get("code", None),
                                                        comparator=numerator.get("comparator", None),
                                                        system=numerator.get("system", None)) if numerator else None,
                                     denominator=Quantity(value=denominator.get("value", None),
                                                          unit=denominator.get("unit", None),
                                                          code=denominator.get("code", None),
                                                          comparator=denominator.get("comparator", None),
                                                          system=denominator.get("system",
                                                                                 None)) if denominator else None)
        elif "valueSampledData" in keys:
            value_sampled_data = item["valueSampledData"]
            self.value_sampled_data = SampledData(origin=value_sampled_data.get("origin", None),
                                                  period=value_sampled_data.get("period", None),
                                                  dimensions=value_sampled_data.get("dimensions", None),
                                                  factor=value_sampled_data.get("factor", None),
                                                  lower_limit=value_sampled_data.get("lower_limit", None),
                                                  upper_limit=value_sampled_data.get("upper_limit", None),
                                                  data=value_sampled_data.get("data", None))
        elif "valuePeriod" in keys:
            value_period = item["valuePeriod"]
            self.value_period = Period(start=value_period.get("start", None),
                                       end=value_period.get("end", None))
        else:
            raise ValueError(f"{item} is not a valid ObservationValue type.")

        return self

    def get(self):
        value = {
            "valueQuantity": self.value_quantity.get() if isinstance(self.value_quantity, Quantity) else None,
            "valueCodeableConcept": self.value_codeable_concept.get() if isinstance(self.value_codeable_concept,
                                                                                    CodeableConcept) else None,
            "valueString": self.value_string if isinstance(self.value_string, str) else None,
            "valueBoolean": self.value_boolean if isinstance(self.value_boolean, bool) else None,
            "valueInteger": self.value_integer if isinstance(self.value_integer, int) else None,
            "valueRange": self.value_range.get() if isinstance(self.value_range, Range) else None,
            "valueRatio": self.value_ratio.get() if isinstance(self.value_ratio, Ratio) else None,
            "valueSampledData": self.value_sampled_data.get() if isinstance(self.value_sampled_data,
                                                                            SampledData) else None,
            "valueTime": self.value_time if isinstance(self.value_time, str) else None,
            "valueDateTime": self.value_date_time if isinstance(self.value_date_time, str) else None,
            "valuePeriod": self.value_period.get() if isinstance(self.value_period, Period) else None
        }
        return {k: v for k, v in value.items() if v not in ("", None)}


class ImagingStudySeriesInstance:
    def __init__(self, uid: Optional[str] = None, sop_class_uid: Optional[str] = None,
                 sop_class_name: Optional[str] = None, number: Optional[Union[int, str]] = None):
        self.uid = uid
        self.sop_class_uid = sop_class_uid
        self.sop_class_name = sop_class_name
        self.number = number

    def set(self, item: dict):
        self.uid = item.get("uid", None)
        self.sop_class_uid = item.get("sopClassUid", None)
        self.sop_class_name = item.get("sopClassName", None)
        self.number = item.get("number", None)

        return self

    def get(self):
        instance = {
            "uid": self.uid if isinstance(self.uid, str) else None,
            "sopClassUid": self.sop_class_uid if isinstance(self.sop_class_uid, str) else None,
            "sopClassName": self.sop_class_name if isinstance(self.sop_class_name, str) else None,
            "number": self.number if isinstance(self.number, int) or isinstance(self.number, str) else None
        }
        return instance


class ImagingStudySeries:
    """
    endpoint_uuid: is sample's (series) uuid in digitaltwins platform or by user
    """

    def __init__(self, uid: Optional[str] = None, endpoint_uuid: Optional[str] = None,
                 endpoint_url: Optional[str] = None, name: Optional[str] = None,
                 number_of_instances: Optional[int] = None, body_site: Optional[dict] = None,
                 instances: Optional[List[ImagingStudySeriesInstance]] = None):
        self.uid = uid
        self.endpoint_uuid = endpoint_uuid
        self.endpoint_url = endpoint_url
        self.name = name
        self.number_of_instances = number_of_instances
        self.body_site = body_site
        self.instances = instances

    def set(self, item: dict):
        self.uid = item.get("uid", None)
        self.endpoint_uuid = item.get("endpointUuid", None)
        self.endpoint_url = item.get("endpointUrl", None)
        self.name = item.get("name", None)
        self.number_of_instances = item.get("numberOfInstances", None)
        self.body_site = item.get("bodySite", None)
        if item.get("instances", None) is not None:
            self.instances = [ImagingStudySeriesInstance().set(i) for i in item.get("instances")] if isinstance(
                item.get("instances"), list) else []
        else:
            self.instances = []

        return self

    def set_uid(self, uid: str):
        self.uid = uid
        return self

    def set_endpoint_uuid(self, endpoint_uuid: str):
        self.endpoint_uuid = endpoint_uuid
        return self

    def set_endpoint_url(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        return self

    def set_name(self, name: str):
        self.name = name
        return self

    def set_number_of_instances(self, number_of_instances: int):
        self.number_of_instances = number_of_instances
        return self

    def set_body_site(self, body_site: dict):
        self.body_site = body_site
        return self

    def get(self):
        series = {
            "uid": self.uid if isinstance(self.uid, str) else "",
            "endpointUuid": self.endpoint_uuid if isinstance(self.endpoint_uuid, str) else "",
            "endpointUrl": self.endpoint_url if isinstance(self.endpoint_url, str) else "",
            "name": self.name if isinstance(self.name, str) else "",
            "numberOfInstances": self.number_of_instances if isinstance(self.number_of_instances, int) else None,
            "bodySite": self.body_site if isinstance(self.body_site, dict) else None,
            "instances": [i.get() for i in self.instances if isinstance(i, ImagingStudySeriesInstance)] if isinstance(
                self.instances, list) else []
        }
        return series


class WorkflowGoal:

    def __init__(self, description: str):
        self.description = description

    def get(self):
        goal = {
            "description": self.description.get() if isinstance(self.description, str) else None,
        }
        return {k: v for k, v in goal.items() if v not in ("", None, [])}


class DocumentAttachment:
    def __init__(self, url: Optional[str] = "", content_type: Optional[str] = ""):
        if not isinstance(url, str):
            raise ValueError(f"url={url} is not an instance of type str")
        elif not isinstance(content_type, str):
            raise ValueError(f"content_type={content_type} is not an instance of type str")

        self.url = url
        self.content_type = content_type

    def __repr__(self):
        return (f"DocumentAttachment(url={self.url}, content_type={self.content_type})")

    def set_url(self, url: str):
        self.url = url
        return self

    def set_content_type(self, content_type: str):
        self.content_type = content_type
        return self

    def get(self):
        attachment = {
            "url": self.url,
            "contentType": self.content_type
        }
        return attachment
