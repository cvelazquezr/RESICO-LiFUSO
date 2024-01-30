import numpy as np
from pyspark.sql import SparkSession
from gensim.models import Word2Vec

def transform_contexts(record, apis_model, keys_apis, contexts_model, keys_context):
    contexts_codes = record.Contexts

    transformed_inputs = []
    transformed_contexts = []

    for index_contexts, contexts in enumerate(contexts_codes):
        if len(contexts) > 0:
            for index_context, context in enumerate(contexts):
                divided_context = context.split(",")

                if len(divided_context) == 2:
                    api = divided_context[0].replace("|", ".")
                    internal_context = divided_context[1].split("|")

                    # Vectorise
                    if api in keys_apis:
                        transformed_api = apis_model.wv[api]
                        transformed_tokens = []

                        for token in internal_context:
                            if token in keys_context:
                                transformed_token = contexts_model.wv[token]
                                transformed_tokens.append(transformed_token)

                        if len(transformed_tokens) > 0:
                            transformed_context = np.mean(transformed_tokens)
                            transformed_input = (transformed_api + transformed_context) / 2
                            transformed_input_text = [str(number) for number in transformed_input]

                            transformed_inputs.append(",".join(transformed_input_text))
                            transformed_contexts.append((index_contexts, index_context))

    return (
        record.AnswerID,
        record.AnswerBody,
        record.AnswerScore,
        record.PostID,
        record.PostTitle,
        record.Question,
        record.Tags,
        record.PostScore,
        record.AcceptedAnswerID,
        record.Codes,
        record.Contexts,
        transformed_contexts,
        transformed_inputs
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
MODELS_FOLDER = DATA_FOLDER + "/models/w2v"

print("Loading the trained w2v models ...")
apis_w2v = Word2Vec.load("{}/data_apis.model".format(MODELS_FOLDER))
contexts_w2v = Word2Vec.load("{}/data_contexts.model".format(MODELS_FOLDER))

keys_apis = list(apis_w2v.wv.key_to_index.keys())
keys_context = list(contexts_w2v.wv.key_to_index.keys())
print("Done!")

print("Loading all Stack Overflow data ...")
dataset = spark.read.parquet("2-java_answers_contexts.parquet")
print("Done!")

print("Transforming the obtained contexts into vectors ...")
rdd_transformed = dataset.rdd.map(lambda record: transform_contexts(record, apis_w2v, keys_apis, contexts_w2v, keys_context))
dataset_transformed = rdd_transformed.toDF(
    ['AnswerID', 'AnswerBody', 'AnswerScore', 'PostID', 'PostTitle', 'Question', 'Tags', 'PostScore', 'AcceptedAnswerID', 'Codes', 'Contexts', 'Indexes', 'Vectors']
)
print("Done!")

print("Filter out those with no code ...")
dataset_transformed_filtered = dataset_transformed.rdd.filter(lambda record: len(record.Vectors) > 0).toDF()
print("Done!")

print("Writing the filtered dataset to a local parquet file ...")
dataset_transformed_filtered.write.parquet("3-java_answers_vectors.parquet")
print("Done!")
