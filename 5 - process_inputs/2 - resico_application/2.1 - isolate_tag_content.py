from pyspark.sql import SparkSession

def transform_tags(tags_str):
    tags = ""

    for char in tags_str:
        if char == '<' or char == '>':
            tags += ' '
        else:
            tags += char
    tags_formatted = list(filter(lambda char: len(char) > 0, tags.split(" ")))

    return tags_formatted

def filter_record(record, tags):
    tags_record = transform_tags(record.Tags)

    if len(set(tags_record).intersection(set(tags))) > 0:
        return True
    return False


def filter_record_per_tag(record, tag):
    tags_record = transform_tags(record.Tags)
    return tag in tags_record

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

tags = ["jfreechart", "guava", "pdfbox", "jsoup", "httpclient", "apache-poi", "quartz-scheduler"]

print("Loading all Stack Overflow data ...")
dataset = spark.read.parquet("2-java_answers_contexts.parquet")
print("Done!")

# Extract the data with the name of the libraries in their tags
print("Extracting the data with the tags ...")
dataset_filtered = dataset.rdd.filter(lambda record: filter_record(record, tags)).toDF()
print("Done!")

# Saving the ids of the answer where the post tags is 
for tag in tags:
    print("Processing tag {} ...".format(tag))
    records_tag = dataset_filtered.rdd.filter(lambda record: filter_record_per_tag(record, tag)).toDF()
    records_ids = [int(row.AnswerID) for row in records_tag.select("AnswerID").collect()]

    with open("{}/library_tag_ids/{}.txt".format(DATA_FOLDER, tag), "w") as f:
        for record_id in records_ids:
            f.write("{}\n".format(record_id))
