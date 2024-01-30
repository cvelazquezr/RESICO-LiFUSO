import joblib
from pyspark.sql import SparkSession


def predict_fqn(record, model, mapping):
    vector = record.vector
    api_reference = record.api_reference

    prediction = int(model.value.predict([vector])[0])
    model_prediction = mapping[prediction]

    prediction_str = ""
    if model_prediction.split('.')[-1] == api_reference.split('.')[0]:
        prediction_str = model_prediction

    return (
        record.answer_id,
        record.post_id,
        record.tags,
        record.context_sizes,
        record.index_context,
        api_reference,
        record.code_reference,
        prediction_str
    )

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
print("Done!")

DATA_FOLDER = "/mansion/cavelazq/PhD/joint_tools/data"
MODELS_FOLDER = DATA_FOLDER + "/models"

print("Loading the mapping of numbered labels and processing them ...")
mapping_lines = []
with open("{}/w2v/data_mapping.txt".format(MODELS_FOLDER)) as f:
    while True:
        line = f.readline()
        if not line:
            break
        else:
            line = line.strip()
            mapping_lines.append(line)
mapping_lines = list(set(mapping_lines))
divided_lines = [element.split(":") for element in mapping_lines]
divided_lines_int = [(int(element_tuple[0]), element_tuple[1]) for element_tuple in divided_lines]
mapping = dict(divided_lines_int)
print("Done!")

print("Loading all Stack Overflow data ...")
dataset = spark.read.parquet("3-java_answers_vectors.parquet")
print("Done!")

print("Loading the trained classifier ...")
knn_model = joblib.load("{}/cls/knn_github.joblib".format(MODELS_FOLDER))
print("Done!")

print("Getting the information related to the vectors ...")
answer_ids = [int(row.AnswerID) for row in dataset.select("AnswerID").collect()]
post_ids = [int(row.PostID) for row in dataset.select("PostID").collect()]
tags = [row.Tags for row in dataset.select("Tags").collect()]
codes = [row.Codes for row in dataset.select("Codes").collect()]
vectors = [list(row.Vectors) for row in dataset.select("Vectors").collect()]
indexes_contexts = [list(row.Indexes) for row in dataset.select("Indexes").collect()]
indexes_converted = []

for row in indexes_contexts:
    tmp_indexes = []
    for row_index in row:
        tmp_indexes.append((row_index._1, row_index._2))
    indexes_converted.append(tmp_indexes)

contexts = [list(list(row.Contexts)) for row in dataset.select("Contexts").collect()]

converted_vectors = []

for index_i, (answer_id, post_id, tag, vectors_str, indexes_list, context_list) in enumerate(zip(answer_ids, post_ids, tags, vectors, indexes_converted, contexts)):
    context_sizes = []

    for context in context_list:
        context_sizes.append(len(context))

    for index, vector_str in zip(indexes_list, vectors_str):
        converted_vector = [float(number_str) for number_str in vector_str.split(",")]
        context_vector = context_list[index[0]][index[1]]
        api_reference = context_vector.split(",")[0].replace("|", ".")

        converted_vectors.append((answer_id, post_id, tag, context_sizes, index, api_reference, codes[index_i][index[0]], converted_vector))
print("Done!")

print("Broadcasting the trained model with the data to predict ...")
broadcasted_knn = spark.sparkContext.broadcast(knn_model)
df_vectors = spark.createDataFrame(converted_vectors, ['answer_id', 'post_id', 'tags', 'context_sizes', 'index_context', 'api_reference', 'code_reference', 'vector'])
neighbors_rdd = df_vectors.rdd.map(lambda record: predict_fqn(record, broadcasted_knn, mapping))
dataset_neighbors = neighbors_rdd.toDF(['AnswerID', 'PostID', 'Tags', 'Context_Sizes', 'Index', 'API_Reference', 'Code', 'Predicted_FQN'])
print("Done!")

print("Filtering out the invalid predictions by the model ...")
dataset_neighbors_filtered = dataset_neighbors.rdd.filter(lambda record: record.Predicted_FQN != "").toDF()
print("Done!")

print("Writing the neighbors dataset to a local parquet file ...")
dataset_neighbors_filtered.write.parquet("4-java_answers_fqns.parquet")
print("Done!")
