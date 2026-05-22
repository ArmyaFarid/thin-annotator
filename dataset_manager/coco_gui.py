import fiftyone as fo

if fo.dataset_exists("minerals"):
    dataset = fo.load_dataset("minerals")
else:
    dataset = fo.Dataset.from_dir(
        dataset_type=fo.types.COCODetectionDataset,
        data_path="/Users/armyabakouan/Documents/ThinAnnotatorData/dataset/images/",
        labels_path="/Users/armyabakouan/Documents/ThinAnnotatorData/dataset/annotations.json",
        name="minerals",
    )

session = fo.launch_app(dataset)
session.wait()