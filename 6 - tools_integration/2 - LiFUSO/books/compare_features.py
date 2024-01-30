import numpy as np
from bs4 import BeautifulSoup


class Feature(object):
    def __init__(self, name="", description=[], snippets=[]):
        self.name = name
        self.description = description
        self.snippets = snippets

    def set_name(self, new_name):
        self.name = new_name[11:-13]

    def set_description(self, new_description: str):
        self.description = new_description[3:-4].split(",")

    def add_snippet(self, code_snippet: str):
        self.snippets.append(code_snippet[24:-13].split(","))

    def api_calls(self):
        all_calls = []
        for snippet in self.snippets:
            all_calls += snippet

        return len(set(all_calls))

    def method_calls(self):
        all_method_calls = []

        for snippet in self.snippets:
            for call in snippet:
                all_calls_snippet = call.split(".")
                all_method_calls += all_calls_snippet[1:]

        return len(set(all_method_calls))

    def __str__(self):
        return "{} - {} - {}".format(self.name, self.description, len(self.snippets))


def extract_features(contents: list[str]):
    features = []
    feature = Feature()
    open_name = False
    open_code = False

    for line in contents:
        line = str(line)
        if line.startswith("<p><strong>"):
            features.append(feature)
            open_name = False
            open_code = False
            feature = Feature()
            feature.set_name(line)
            feature.snippets = []
        elif line.startswith("<p>Name description:</p>"):
            open_name = True
            open_code = False
            continue
        elif line.startswith("<p>Code description:</p>"):
            open_name = False
            open_code = True
            continue

        if line.startswith("<p>") and open_name:
            feature.set_description(line)
            open_name = False
        elif line.startswith("<pre class") and open_code:
            feature.add_snippet(line)

    features.append(feature)
    features = features[1:]
    return features


def stats_api_calls(features: list[Feature]):
    numbers = [feature.api_calls() for feature in features]
    # print(numbers)

    return np.mean(numbers), np.std(numbers)


def stats_method_calls(features: list[Feature]):
    numbers = [feature.method_calls() for feature in features]

    return np.mean(numbers), np.std(numbers)


DATA_FOLDER = "/home/kmilo/Dev/R/features/clusters-exploration/books"

OLD_FEATURES = "{}/old_generated".format(DATA_FOLDER)
NEW_FEATURES = "{}/new_generated".format(DATA_FOLDER)

LIBRARIES = [
    "guava",
    "httpclient",
    "jfreechart",
    "jsoup",
    "pdfbox",
    "poi-ooxml",
    "quartz",
]

for library in LIBRARIES:
    print("LIBRARY {} ...".format(library))

    file_old = "{}/{}.html".format(OLD_FEATURES, library)
    file_new = "{}/{}.html".format(NEW_FEATURES, library)

    with open(file_old) as fo:
        soup_old = BeautifulSoup(fo, "html.parser")

    with open(file_new) as fn:
        soup_new = BeautifulSoup(fn, "html.parser")

    content_old = soup_old.contents[2].contents[3].contents[1].contents
    content_new = soup_new.contents[2].contents[3].contents[1].contents

    features_old = extract_features(content_old)
    features_new = extract_features(content_new)

    print("Number of old features: {}".format(len(features_old)))
    print("Number of new features: {}".format(len(features_new)))
    print()

    mean_apis_old, std_apis_old = stats_api_calls(features_old)
    mean_apis_new, std_apis_new = stats_api_calls(features_new)
    print("Mean old API calls: {} STD: {}".format(mean_apis_old, std_apis_old))
    print("Mean new API calls: {} STD: {}".format(mean_apis_new, std_apis_new))
    print()

    mean_calls_old, std_calls_old = stats_method_calls(features_old)
    mean_calls_new, std_calls_new = stats_method_calls(features_new)
    print("Mean old method calls: {} STD: {}".format(mean_calls_old, std_calls_old))
    print("Mean new method calls: {} STD: {}".format(mean_calls_new, std_calls_new))
    print()
