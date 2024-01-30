def read_ids(file_path: str):
    ids = []
    with_tags = []
    with open(file_path) as f:
        while True:
            line = f.readline()
            if not line: break
            else:
                line = line.strip()
                line_divided = line.split(" ")
                ids.append(line_divided[0])
                with_tags.append(line_divided[1])
    return ids, with_tags

dataset = spark.read.parquet("java_answers.parquet")
selected_dataset = dataset.select(['AnswerID', 'PostTitle', 'AnswerBody'])

poi_ids, poi_tags = read_ids("libraries/answer_ids/apache-poi.txt")
guava_ids, guava_tags = read_ids("libraries/answer_ids/guava.txt")
http_ids, http_tags = read_ids("libraries/answer_ids/httpclient.txt")
jfree_ids, jfree_tags = read_ids("libraries/answer_ids/jfreechart.txt")
jsoup_ids, jsoup_tags = read_ids("libraries/answer_ids/jsoup.txt")
pdfbox_ids, pdfbox_tags = read_ids("libraries/answer_ids/pdfbox.txt")
quartz_ids, quartz_tags = read_ids("libraries/answer_ids/quartz-scheduler.txt")

poi_ids = [int(id) for id in poi_ids]
guava_ids = [int(id) for id in guava_ids]
http_ids = [int(id) for id in http_ids]
jfree_ids = [int(id) for id in jfree_ids]
jsoup_ids = [int(id) for id in jsoup_ids]
pdfbox_ids = [int(id) for id in pdfbox_ids]
quartz_ids = [int(id) for id in quartz_ids]

filtered_poi = selected_dataset.rdd.filter(lambda record: record.AnswerID in poi_ids).toDF()
filtered_guava = selected_dataset.rdd.filter(lambda record: record.AnswerID in guava_ids).toDF()
filtered_http = selected_dataset.rdd.filter(lambda record: record.AnswerID in http_ids).toDF()
filtered_jfree = selected_dataset.rdd.filter(lambda record: record.AnswerID in jfree_ids).toDF()
filtered_jsoup = selected_dataset.rdd.filter(lambda record: record.AnswerID in jsoup_ids).toDF()
filtered_pdfbox = selected_dataset.rdd.filter(lambda record: record.AnswerID in pdfbox_ids).toDF()
filtered_quartz = selected_dataset.rdd.filter(lambda record: record.AnswerID in quartz_ids).toDF()

filtered_poi = filtered_poi.toPandas()
filtered_guava = filtered_guava.toPandas()
filtered_http = filtered_http.toPandas()
filtered_jfree = filtered_jfree.toPandas()
filtered_jsoup = filtered_jsoup.toPandas()
filtered_pdfbox = filtered_pdfbox.toPandas()
filtered_quartz = filtered_quartz.toPandas()

def sort_tags(data_ids: list, lib_ids: list, lib_tags: list):
    new_ord_tags = []
    for data_id in data_ids:
        index_lib = lib_ids.index(data_id)
        new_ord_tags.append(lib_tags[index_lib])
    return new_ord_tags

poi_tags_sorted = sort_tags(filtered_poi.AnswerID.tolist(), poi_ids, poi_tags)
guava_tags_sorted = sort_tags(filtered_guava.AnswerID.tolist(), guava_ids, guava_tags)
http_tags_sorted = sort_tags(filtered_http.AnswerID.tolist(), http_ids, http_tags)
jfree_tags_sorted = sort_tags(filtered_jfree.AnswerID.tolist(), jfree_ids, jfree_tags)
jsoup_tags_sorted = sort_tags(filtered_jsoup.AnswerID.tolist(), jsoup_ids, jsoup_tags)
pdfbox_tags_sorted = sort_tags(filtered_pdfbox.AnswerID.tolist(), pdfbox_ids, pdfbox_tags)
quartz_tags_sorted = sort_tags(filtered_quartz.AnswerID.tolist(), quartz_ids, quartz_tags)

filtered_poi['WithTags'] = poi_tags_sorted
filtered_guava['WithTags'] = guava_tags_sorted
filtered_http['WithTags'] = http_tags_sorted
filtered_jfree['WithTags'] = jfree_tags_sorted
filtered_jsoup['WithTags'] = jsoup_tags_sorted
filtered_pdfbox['WithTags'] = pdfbox_tags_sorted
filtered_quartz['WithTags'] = quartz_tags_sorted

filtered_poi.to_csv("libraries/poi-ooxml.csv", index=False)
filtered_guava.to_csv("libraries/guava.csv", index=False)
filtered_http.to_csv("libraries/httpclient.csv", index=False)
filtered_jfree.to_csv("libraries/jfreechart.csv", index=False)
filtered_jsoup.to_csv("libraries/jsoup.csv", index=False)
filtered_pdfbox.to_csv("libraries/pdfbox.csv", index=False)
filtered_quartz.to_csv("libraries/quartz.csv", index=False)
