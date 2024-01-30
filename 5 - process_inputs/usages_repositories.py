import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from sys import argv

# Function that reads a JSON file from the arguments
def read_json(json_path):
    with open(json_path) as json_file:
        data_json = json.load(json_file)
    return data_json

# Given a dictionary, returns the keys appended to the values
def get_apis(json_dict):
    elements = []
    for fqn, methods in json_dict.items():
        names_upper = list(filter(lambda method: method[0].isupper(), methods))
        names_lower = list(filter(lambda method: method[0].islower(), methods))

        class_name = fqn.split('.')[-1]
        appendix_names = list(map(lambda method: class_name + '.' + method, names_lower))
        elements += names_upper + appendix_names

    return elements

# Given the APIs in a project, calculates the covered percentage
def get_delta_increase(api_usages_project, all_apis_library, apis_covered):
    apis_present = list(filter(lambda api: api in all_apis_library, api_usages_project))
    index_apis_present = list(map(lambda api: all_apis_library.index(api), apis_present))

    for index_api in index_apis_present:
        apis_covered[index_api] = True
    

    apis_covered_true = list(filter(lambda is_covered: is_covered, apis_covered))
    percentage = len(apis_covered_true) / len(apis_covered) * 100.0
    
    return percentage, apis_covered

# Add main definition
if __name__ == '__main__':
    # Reading from the command line arguments
    if len(argv) != 2:
        print("Usage: python3 usage_repositories.py <data_folder>/<name_of_library>")
        exit(1)
    else:
        DATA_FOLDER = "/mansion/cavelazq/PhD/joint_tools/data"
        API_FOLDER = DATA_FOLDER + "/api_usages"
        JSONS_FOLDER = DATA_FOLDER + "/jsons"
        PERCENTAGE_USAGE_FOLDER = DATA_FOLDER + "/percentage_usages"

        # Path to the data folder
        library_path = API_FOLDER + "/" + argv[1] + ".tsv"
        
        # Reading the data
        print("Reading data ...")
        data_library = pd.read_csv(library_path, sep="\t")
        print("Done!")

        # Reading the JSONs
        print("Reading JSONs ...")
        library_json = read_json(JSONS_FOLDER + "/" + argv[1] + ".json")
        print("Done!")

        # Getting the APIs from the JSONs
        library_apis = get_apis(library_json)

        # Get the names of the projects
        print("Processing projects ...")
        project_names = data_library["project_name"].unique()

        # Stats on the projects
        percentage_covered = 0
        apis_covered = [False] * len(library_apis)

        processed_projects = []
        deltas_increased = []

        with open(PERCENTAGE_USAGE_FOLDER + "/" + argv[1] + ".csv", "w") as percentage_usage_file:
            percentage_usage_file.write("project,percentage,delta_increased\n")

            # Get data for each project
            for index, project_name in enumerate(project_names):
                print("Processing project " + str(index + 1) + "/" + str(len(project_names)) + " ...")

                # Get the data for the project
                data_project = data_library[data_library["project_name"] == project_name]

                # Get the api usage per project
                api_usage_project = list(set(data_project["api_usage"].values.tolist()))

                # Get the covered percentage
                percentage_project, apis_covered = get_delta_increase(api_usage_project, library_apis, apis_covered)

                # Calculate the delta increase
                delta = percentage_project - percentage_covered

                # Update the stats
                percentage_covered = percentage_project
                processed_projects.append(project_name)
                deltas_increased.append(delta)

                percentage_usage_file.write(project_name + "," + str(percentage_covered) + "," + str(delta) + "\n")

        print("Done!")
            