library(dynamicTreeCut)
library(stringr)
library(cluster)
library(clValid)
library(dplyr)
library(shiny)
library(shinycssloaders)
library(treemap)
library(highcharter)
library(RColorBrewer)
library(ggplot2)
library(parallel)
library(lvplot)
library(knitr)
library(rmarkdown)
library(reticulate)

source("selection/frequency_selection.R")
source("evaluation/perform_evaluation.R")
source("evaluation/rq2.R")
source("evaluation/rq3.R")
source("books/generate_books.R")

# Loading the Python script for the highest indices
source_python("scripts/local_bumps.py")

data.information <- data.frame()
all.names <- ""

defaultW <- getOption("warn")
options(warn = -1)