import json

def extract_all_indices(simple_name, simple_name_list):
    indices = []
    index = simple_name_list.index(simple_name)
    indices.append(index)

    while index != -1:
        new_index = simple_name_list.index(simple_name, index + 1)

        if new_index != -1:
            indices.append(new_index)
        index = new_index

    return indices

DATA_FOLDER = "/Users/kmilo/Dev/PhD/features-lab/data"
SO_DATA = "{}/so_data".format(DATA_FOLDER)
JSON_DATA = "{}/jsons".format(DATA_FOLDER)

libraries = {"jfreechart", "guava", "pdfbox", "jsoup", "httpclient", "poi-ooxml", "quartz"}

print("Reading the APIs from the libraries in analysis ...")
all_apis = []

for library in libraries:
    print("Reading APIs from library {} ...".format(library))

    with open("{}/{}.json".format(JSON_DATA, library)) as f:
        data_json_library = json.load(f)
        library_fqns = list(data_json_library.keys())
        all_apis += library_fqns

print("Done!")

print("Reading all import statements from SO posts ...")
imports_SO = []

with open("{}/SO_imports.txt".format(SO_DATA)) as f:
    while True:
        line = f.readline()
        if not line:
            break
        else:
            line = line.strip()
            imports_SO.append(line)

print("Done!")

print("Extracting the simple names of APIs and SO imports ...")
simple_names_apis = [api.split(".")[-1] for api in all_apis]
simple_names_SO = [fqn.split(".")[-1] for fqn in imports_SO]
print("Done!")

print("Measuring internal conflict (not that relevant since the model should be strong enough to discern) ...")
print("There are {} ambiguous simple names for the APIs".format(len(simple_names_apis) - len(set(simple_names_apis))))
print("There are {} ambiguous simple names for the SO imports".format(len(simple_names_SO) - len(set(simple_names_SO))))
print("Done!")

print("Comparing the simple names in SO posts to the simple names for each library and saving the conflicts.")

simple_names_apis_set = set(simple_names_apis)
simple_names_SO_set = set(simple_names_SO)

conflict_simple_names = list(simple_names_apis_set.intersection(simple_names_SO_set))

print("There are {} ambiguous simple names between the libraries and the SO import statements.".format(len(conflict_simple_names)))
print("Done!")

print("Iterating over all ambiguous cases to extract conflicting FQNs ...")
ambiguous_cases = {}

for simple_name in conflict_simple_names:
    indices_apis = [i for i, x in enumerate(simple_names_apis) if x == simple_name]
    indices_so = [i for i, x in enumerate(simple_names_SO) if x == simple_name]

    fqns_apis = [all_apis[index] for index in indices_apis]
    fqns_so = [imports_SO[index] for index in indices_so]

    if len(fqns_apis) == 1 and len(fqns_so) == 1 and fqns_apis[0] == fqns_so[0]:
        continue
    else:
        simple_name_fqns = list(set(fqns_apis + fqns_so))
        ambiguous_cases[simple_name] = simple_name_fqns

print("Inspecting conflict between FQNs of the same library ...")
# Since what is matters is to determine that a code snippet is about a library these conflictive cases could be discarded

cleaned_ambiguous_cases = {}

for simple_name, fqns in ambiguous_cases.items():
    libraries_fqns = set([".".join(fqn.split(".")[:2]) for fqn in fqns])

    if len(libraries_fqns) > 1:
        cleaned_ambiguous_cases[simple_name] = fqns

print("Done!")

print("Writing the import statements to a local file ...")
with open("{}/ambiguous_fqns.json".format(SO_DATA), "w") as f:
    json.dump(cleaned_ambiguous_cases, f)
print("Done!")
