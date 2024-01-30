from bs4 import BeautifulSoup
from pyspark.sql import SparkSession

def obtain_codes(record):
    answer_body = record.AnswerBody

    soup = BeautifulSoup(answer_body, 'html.parser')
    codes = soup.find_all('code')

    codes_text = [code.text for code in codes]

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
        codes_text
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
    dataset = spark.read.parquet("java_answers.parquet")
    print("Done!")

    print("Obtaining the code for the body of each answer ...")
    rdd_codes = dataset.rdd.map(lambda record: obtain_codes(record))
    dataset_codes = rdd_codes.toDF(['AnswerID', 'AnswerBody', 'AnswerScore', 'PostID', 'PostTitle', 'Question', 'Tags', 'PostScore', 'AcceptedAnswerID', 'Codes'])
    print("Done!")

    print("Filter out those with no code ...")
    dataset_codes_filtered = dataset_codes.rdd.filter(lambda record: len(record.Codes) > 0).toDF()
    print("Done!")

    print("Writing the filtered dataset to a local parquet file ...")
    dataset_codes_filtered.write.parquet("1-java_answers_code.parquet")
    print("Done!")
