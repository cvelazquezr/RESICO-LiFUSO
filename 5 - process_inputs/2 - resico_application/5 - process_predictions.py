import json
import pandas as pd
from pyspark.sql import SparkSession

class Answer(object):
    def __init__(self, answer_id, post_id, tags, context_size, context_index, api_reference, code_reference, prediction):
        self.answer_id = answer_id
        self.post_id = post_id
        self.tags = tags
        self.context_size = context_size
        self.context_index = context_index
        self.api_reference = api_reference
        self.code_reference = code_reference
        self.prediction = prediction

    def __str__(self):
        return "{} - {} - {} - {}".format(self.answer_id, self.api_reference, self.code_reference, self.prediction)
    

class Pattern(object):
    # In this case the group_id is the answer_id
    def __init__(self, group_id):
        self.group_id = group_id
        self.patterns = []
        self.counts = []

    def __str__(self):
        return "{} ".format(self.group_id) + " ".join(["{}: {}".format(pattern, count) for pattern, count in zip(self.patterns, self.counts)])
    
    def assign_pattern(self, pattern):
        if pattern in self.patterns:
            index_pattern = self.patterns.index(pattern)
            self.counts[index_pattern] += 1
        else:
            self.patterns.append(pattern)
            self.counts.append(1)

def ends_star(statement):
    return statement.split(".")[-1] == "*"

def analyse_fragment(code_fragment):
    imports = []

    splitted_fragment = code_fragment.split("\n")
    lines_import = list(filter(lambda line: line.startswith("import"), splitted_fragment))

    # Analyse the import lines
    statements = []
    for line in lines_import:
        line_splitted = line.split(" ")

        if len(line_splitted) == 2:
            statements.append(line_splitted[1])

    for statement in statements:
        statement = statement.strip()

        if "." in statement:
            if ";" in statement:
                index_semicolon = statement.index(";")
                statement = statement[:index_semicolon]
            if not ends_star(statement):
                imports.append(statement)
    return imports

def transform_tags(tags_str):
    tags = ""

    for char in tags_str:
        if char == '<' or char == '>':
            tags += ' '
        else:
            tags += char
    tags_formatted = list(filter(lambda char: len(char) > 0, tags.split(" ")))

    return tags_formatted


print("Configuring Spark ...")
spark = SparkSession.builder \
    .master("local[*]") \
    .appName("RESICO") \
    .config("spark.cores.max", "8") \
    .config("spark.executor.memory", "250g") \
    .config("spark.driver.memory", "250g") \
    .config("spark.memory.offHeap.enabled", "true") \
    .config("spark.memory.offHeap.size", "250g") \
    .config("spark.driver.maxResultSize", "250g") \
    .config("spark.sql.parquet.columnarReaderBatchSize", "2048") \
    .getOrCreate()

DATA_FOLDER = "/mansion/cavelazq/PhD/joint_tools/data"
MODELS_FOLDER = DATA_FOLDER + "/models"

library_patterns = [
    "org.jfree",
    "com.google.common",
    "org.apache.pdfbox",
    "org.jsoup",
    "org.apache.http",
    "org.apache.poi",
    "org.quartz"
]

print("Loading the Stack Overflow data ...")
dataset = spark.read.parquet("4-java_answers_fqns.parquet")
print("Done!")

print("Objectifying the data ...")
answer_ids = [int(row.AnswerID) for row in dataset.select("AnswerID").collect()]
post_ids = [int(row.PostID) for row in dataset.select("PostID").collect()]
tags = [row.Tags for row in dataset.select("Tags").collect()]
context_sizes = [list(row.Context_Sizes) for row in dataset.select("Context_Sizes").collect()]
context_indexes = [list(row.Index) for row in dataset.select("Index").collect()]
api_references = [row.API_Reference for row in dataset.select("API_Reference").collect()]
code_references = [row.Code for row in dataset.select("Code").collect()]
predicted_fqns = [row.Predicted_FQN for row in dataset.select("Predicted_FQN").collect()]

# Make a list of answers with the zipped list
answers = []

for answer_id, post_id, tag_list, context_size, index, api_reference, code_reference, predicted_fqn in \
        zip(answer_ids, post_ids, tags, context_sizes, context_indexes, api_references, code_references, predicted_fqns):
    answers.append(Answer(answer_id, post_id, tag_list, sum(context_size), index, api_reference, code_reference, predicted_fqn))

print("Done!")

print("Group the data by AnswerIDs ...")
groups_answers = {}

for answer in answers:
    if answer.answer_id in groups_answers.keys():
        groups_answers[answer.answer_id].append(answer)
    else:
        groups_answers[answer.answer_id] = [answer]
print("Done!")

print("Check library patterns per group ...")
# There might be different library predictions per answer, hence the counts field in the Pattern class
patterns = []

for group_id, answer_list in groups_answers.items():
    pattern = Pattern(group_id)

    for answer in answer_list:
        prediction_answer = answer.prediction
        # There is a maximum of one library prediction per fragment, this is only for accessing that single element
        answer_pattern = list(filter(lambda lib_pattern: prediction_answer.startswith(lib_pattern), library_patterns))[0]

        pattern.assign_pattern(answer_pattern)
    patterns.append(pattern)
print("Done!")

print("Make data to later predict usability of the library and later relatedness ...")
data_answer_id = []
data_predicted_apis = []
data_total_tokens = []
data_tags = []
data_classes = []
data_methods = []
data_ambiguous = []
data_imports = []
data_predicted_library = []

with open("ambiguous_fqns.json") as f:
    data_json_library = json.load(f)
    ambiguous_simple_names = list(data_json_library.keys())

for pattern in patterns:
    answer_id = pattern.group_id
    group = groups_answers[answer_id]
    tags_group = group[0].tags # All tags in the group should be the same
    predicted_apis = len(group)
    total_tokens = group[0].context_size # The context size is the same for all

    number_api_classes = 0
    number_api_methods = 0
    ambiguous_predictions = 0
    import_statements = []

    for answer in group:
        reference = answer.api_reference
        code = answer.code_reference

        class_reference = reference.split(".")[0]
        number_api_classes += 1
        method_reference = ""

        if "." in reference:
            method_reference = reference.split(".")[1]
            number_api_methods += 1

        # Check on ambiguity
        if class_reference in ambiguous_simple_names:
            ambiguous_predictions += 1

        imports_fragment = analyse_fragment(code)
        
        if len(imports_fragment) > 0:
            import_statements += imports_fragment
            
    data_answer_id.append(answer_id)
    data_predicted_apis.append(predicted_apis)
    data_total_tokens.append(total_tokens)
    data_tags.append(tags_group)
    data_classes.append(number_api_classes)
    data_methods.append(number_api_methods)
    data_ambiguous.append(ambiguous_predictions)
    data_predicted_library.append(",".join(pattern.patterns))

    if len(import_statements) == 0:
        data_imports.append("-")
    else:
        data_imports.append(",".join(import_statements))

print("Done!")

print("Creating the column about library usability or not ...")
library_usability = []

library_tags_patterns = {
    "org.jfree": "jfreechart",
    "com.google.common": "guava",
    "org.apache.pdfbox": "pdfbox",
    "org.jsoup": "jsoup",
    "org.apache.http": "httpclient",
    "org.apache.poi": "apache-poi",
    "org.quartz": "quartz-scheduler"
}

for tag_str, predictions in zip(data_tags, data_predicted_library):
    tag_list = transform_tags(tag_str)
    predictions_to_tag = [library_tags_patterns[prediction] for prediction in predictions.split(",")]

    is_predicted = False

    for predicted_tag in predictions_to_tag:
        if predicted_tag in tag_list:
            is_predicted = True
    
    if is_predicted:
        library_usability.append("Y")
    else:
        library_usability.append("-")
print("Done!")

print("Create the pandas dataframe to be used later ...")
data = {
    'AnswerID': data_answer_id,
    'Predicted_APIs': data_predicted_apis,
    'Total_Tokens': data_total_tokens,
    'Tags': data_tags,
    'Classes': data_classes,
    'Methods': data_methods,
    'Ambiguity': data_ambiguous,
    'Imports': data_imports,
    'Predicted_Library': data_predicted_library,
    'Library_Used': library_usability
}
print("Done!")

print("Saving the created dataframe to disk ...")
df = pd.DataFrame(data=data)
df.to_csv("Incomplete_SO_library_usage.csv", index=False)
print("Done!")
