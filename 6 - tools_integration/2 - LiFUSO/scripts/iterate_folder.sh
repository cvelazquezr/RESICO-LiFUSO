#!/usr/bin/bash

LIST_FILES=$(find $1 -type f)

for FILE_PATH in $LIST_FILES
do
  echo $FILE_PATH
  Rscript --vanilla /Users/kmilo/Dev/R/features/clusters-exploration/scripts/get_score_bash.R $FILE_PATH
done
