#standardSQL
SELECT
    question.Id AS Question_ID, question.Title, question.Tags, answer.Id as Answer_ID, answer.Score, answer.Body
FROM
        `sotorrent-org.2020_12_31.Posts` question
    JOIN
        `sotorrent-org.2020_12_31.Posts` answer
    ON
        answer.ParentId = question.Id
        AND answer.PostTypeId = 2
        AND question.PostTypeId = 1
WHERE
        question.Tags LIKE '%<library-name>%';