import pandas as pd
import numpy as np
from gensim.models import Word2Vec

DATA_FOLDER = "/mansion/cavelazq/PhD/joint_tools/data"
data_file = DATA_FOLDER + "/csv/data.tsv"

print("Reading the input file ...")
# It has to be a TSV file
dataframe = pd.read_csv(data_file, sep="\t").dropna()

print("Separating the fields of the data ...")
# Separate the fields
apis = list(map(lambda element: element.replace("|", "."), dataframe.api.to_list()))
contexts = list(map(lambda element: element.split("|"), dataframe.context.to_list()))
fqns = dataframe.fqn.to_list()

print("Vectorising APIs ...")
apis_w2v = Word2Vec([apis], vector_size=20, min_count=1, batch_words=1000, workers=20)

print("Saving the Word2Vec model for APIs ...")
apis_w2v.save("{}/models/w2v/data_apis.model".format(DATA_FOLDER))

print("Vectorising Contexts ...")
contexts_w2v = Word2Vec(contexts, vector_size=20, min_count=1, batch_words=1000, workers=20)

print("Saving the Word2Vec model for Contexts ...")
contexts_w2v.save("{}/models/w2v/data_contexts.model".format(DATA_FOLDER))

print("Labelling the FQNs ...")
unique_fqns = list(set(fqns))
mapping_fqns = dict()

for index, fqn in enumerate(unique_fqns):
    mapping_fqns[fqn] = index

print("Saving the mapping ...")
labelled_fqns = [mapping_fqns[fqn] for fqn in fqns]

with open("{}/models/w2v/data_mapping.txt".format(DATA_FOLDER), "w") as f:
    for item, value in mapping_fqns.items():
        f.write("{}:{}\n".format(value, item))

with open("{}/models/w2v/data_labels.txt".format(DATA_FOLDER), "w") as f:
    for label in labelled_fqns:
        f.write("{}\n".format(label))

print("Loading the Word2Vec model for APIs ...")
apis_w2v = Word2Vec.load("{}/models/w2v/data_apis.model".format(DATA_FOLDER))

print("Loading the Word2Vec model for Contexts ...")
contexts_w2v = Word2Vec.load("{}/models/w2v/data_contexts.model".format(DATA_FOLDER))

print("Loading the transformed FQNs ...")
labelled_fqns = []

with open("{}/models/w2v/data_labels.txt".format(DATA_FOLDER)) as f:
    while True:
        line = f.readline()
        if not line:
            break
        else:
            line = line.strip()
            labelled_fqns.append(line)

print("Transforming the data given the trained models ...")
transformed_data = []

for index, (api, context, fqn) in enumerate(zip(apis, contexts, labelled_fqns)):
    print("{} / {} ...".format(index + 1, len(labelled_fqns)))

    transformed_api = apis_w2v.wv[api]
    transformed_tokens = []

    for token in context:
        transformed_token = contexts_w2v.wv[token]
        transformed_tokens.append(transformed_token)

    transformed_context = np.mean(transformed_tokens)

    transformed_input = (transformed_api + transformed_context) / 2

    transformed_input_str = [str(number) for number in transformed_input]

    transformed_data.append(",".join(transformed_input_str) + "," + fqn)

print("Saving the transformed data ...")

with open("{}/transformed_input/data.csv".format(DATA_FOLDER), "w") as f:
    for line in transformed_data:
        f.write(line + "\n")

print("Done!")
