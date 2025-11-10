import pydicom


DEFAULT_TAGS = [
    "PatientID", "StudyDate", "Modality", "Manufacturer",
    "Rows", "Columns", "PixelSpacing", "SliceThickness"
]

def extract_meta(path, keys=None, anonymize=False):
    ds = pydicom.dcmread(path, stop_before_pixels=True)
    data = {}

    tags = keys if keys else DEFAULT_TAGS

    for tag in tags:
        if hasattr(ds, tag):
            value = getattr(ds, tag)
            # convert pydicom objects to python primitives
            try:
                value = value.value
            except:
                pass
            data[tag] = value

    if anonymize:
        for sensitive in ["PatientName", "PatientBirthDate", "InstitutionName"]:
            if sensitive in data:
                data[sensitive] = None

    return data


def extract_folder(folder):
    """Return metadata for all .dcm files inside a folder."""
    import os
    results = []
    for name in os.listdir(folder):
        if name.lower().endswith(".dcm"):
            path = os.path.join(folder, name)
            results.append({ "file": name, **extract_meta(path) })
    return results
