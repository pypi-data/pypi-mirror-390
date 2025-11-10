import yaml
from collections import OrderedDict
from pathlib import Path
import pandas as pd
from datetime import datetime, timezone



def is_observation_type(variable):
    if isinstance(variable, dict):
        required_keys = {"value_system", "value", "code", "units_system", "units"}

        if required_keys.issubset(variable.keys()):
            if isinstance(variable["value"], (int, float, str)) and \
                    isinstance(variable["value_system"], str) and \
                    isinstance(variable["code"], str) and \
                    isinstance(variable["units_system"], str) and \
                    isinstance(variable["units"], str):
                return True
    return False


def ordered_load(stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def check_first_file_extension(folder_path):
    folder = Path(folder_path)
    first_file = next((f for f in folder.iterdir() if f.is_file()), None)

    if not first_file:
        return None

    ext = first_file.suffix.lower()

    if ext == '.dcm':
        return 'dcm'
    elif ext == '.nrrd':
        return 'nrrd'
    elif ''.join(first_file.suffixes) == '.nii.gz':
        return 'nii.gz'
    elif ext == '.txt':
        return 'txt'
    else:
        return 'unknown'


def read_dataset_samples(dataset_path: Path):
    dataset_path = Path(dataset_path)
    sample_df = pd.read_excel(dataset_path / "samples.xlsx")
    unique_samples = sample_df.drop_duplicates(subset=["sample id"])

    return dict(zip(unique_samples["sample id"], unique_samples["sample type"]))

def get_current_formated_time():

    now = datetime.now(timezone.utc)
    formatted = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return formatted