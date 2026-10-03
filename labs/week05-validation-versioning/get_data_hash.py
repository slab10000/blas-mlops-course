import os
import yaml

def get_data_hash(dvc_file_path=None):
    """Read the DVC pointer file and return the content hash of the tracked data.

    Resolves relative to this script's own location by default, so it works
    the same way regardless of which directory you run train.py from --
    same pattern as DATA_PATH at the top of train.py.
    """
    if dvc_file_path is None:
        here = os.path.dirname(os.path.abspath(__file__))
        dvc_file_path = os.path.join(here, "loan_applications.csv.dvc")
    with open(dvc_file_path) as f:
        dvc_meta = yaml.safe_load(f)
    return dvc_meta["outs"][0]["md5"]

if __name__ == "__main__":
    print(get_data_hash())
