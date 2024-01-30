import pandas as pd

def transform_tags(tags_str):
    tags = ""

    for char in tags_str:
        if char == '<' or char == '>':
            tags += ' '
        else:
            tags += char
    tags_formatted = list(filter(lambda char: len(char) > 0, tags.split(" ")))

    return tags_formatted

DATA_FOLDER = "/home/kmilo/Dev/PhD/features-lab/data/so_data"
data = pd.read_csv("{}/Processed_SO_data.csv".format(DATA_FOLDER))

library_tags_patterns = {
    "org.jfree": "jfreechart",
    "com.google.common": "guava",
    "org.apache.pdfbox": "pdfbox",
    "org.jsoup": "jsoup",
    "org.apache.http": "httpclient",
    "org.apache.poi": "apache-poi",
    "org.quartz": "quartz-scheduler"
}

data_per_library = {}

for prediction, name in library_tags_patterns.items():
    data_per_library[name] = data[data["Predicted_Library"] == prediction]

for library_name, data_library in data_per_library.items():
    with open("{}/libraries/answer_ids/{}.txt".format(DATA_FOLDER, library_name), "w") as f:
        answer_ids = data_library["AnswerID"].to_list()
        tags = data_library["Tags"].to_list()
        with_tags = []

        for tag_list in tags:
            if library_name in transform_tags(tag_list):
                with_tags.append("Y")
            else:
                with_tags.append("N")

        for answer_id, with_tag in zip(answer_ids, with_tags):
            f.write("{} {}\n".format(answer_id, with_tag))

# Data having multiple predictions
data_multiple = data[data["Predicted_Library"].str.contains(",")]

answer_ids_multiple = data_multiple["AnswerID"].to_list()
tags_multiple = data_multiple["Tags"].to_list()
prediction_multiple = data_multiple["Predicted_Library"].to_list()

unpredicted_elements = []

for answer_id, tag_list, predictions in zip(answer_ids_multiple, tags_multiple, prediction_multiple):
    tags_changed = transform_tags(tag_list)
    prediction_list = predictions.split(",")
    tags_predictions = [library_tags_patterns[prediction] for prediction in prediction_list]

    intersection_tags = set(tags_changed).intersection(set(tags_predictions))

    if len(intersection_tags) == 1:
        intersected_lib = list(intersection_tags)[0]

        with open("{}/libraries/answer_ids/{}.txt".format(DATA_FOLDER, intersected_lib), "a") as f:
            print("Writing to {} ...".format(intersected_lib))
            f.write("{} Y\n".format(answer_id))

    elif len(intersection_tags) > 1:
        unpredicted_elements.append("{} {} Y".format(answer_id, predictions))
    else:
        unpredicted_elements.append("{} {} N".format(answer_id, predictions))

with open("{}/libraries/answer_ids/unassigned.txt".format(DATA_FOLDER), "w") as f:
    for element in unpredicted_elements:
        f.write(element + "\n")
