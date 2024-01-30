import subprocess
from pyspark.sql import SparkSession

def filter_empty_contexts(record):
    contexts_codes = [context for context in record.Contexts if len(context) > 0]

    return len(contexts_codes) > 0

def obtain_contexts(record):
    codes = record.Codes
    contexts_codes = []

    for code in codes:
        result = subprocess.run(['java', '-jar', 'islandParser.jar', '-s', code], stdout=subprocess.PIPE)
        contexts = result.stdout.decode('utf-8').split('\n')
        contexts = list(filter(lambda element: len(element.strip()) > 0, contexts))

        if len(contexts) > 0:
            contexts_codes.append(contexts)

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
        contexts_codes
    )

if __name__ == '__main__':
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

    print("Loading all Stack Overflow data ...")
    dataset = spark.read.parquet("java_answers_code.parquet")
    print("Done!")

    print("Obtaining the contexts for each code in each answer ...")
    rdd_contexts = dataset.rdd.map(lambda record: obtain_contexts(record))
    dataset_contexts = rdd_contexts.toDF(['AnswerID', 'AnswerBody', 'AnswerScore', 'PostID', 'PostTitle', 'Question', 'Tags', 'PostScore', 'AcceptedAnswerID', 'Codes', 'Contexts'])
    print("Done!")

    print("Filter out those with no code ...")
    dataset_contexts_filtered = dataset_contexts.rdd.filter(lambda record: len(record.Contexts) > 0).toDF()
    dataset_contexts_filtered_empty = dataset_contexts_filtered.rdd.filter(lambda record: filter_empty_contexts(record)).toDF()
    print("Done!")

    print("Writing the filtered dataset to a local parquet file ...")
    dataset_contexts_filtered_empty.write.parquet("2-java_answers_contexts.parquet")
    print("Done!")
