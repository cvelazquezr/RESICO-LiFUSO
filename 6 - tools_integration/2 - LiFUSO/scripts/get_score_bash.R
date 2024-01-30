library(cluster)
library(dynamicTreeCut)

args = commandArgs(trailingOnly=TRUE)

if (length(args) == 0) {
  stop("A file path must be supplied", call.=FALSE)
}

file.path <- args[1]

data.tags <- read.csv(file.path, header = F)

# Getting the similarities from the data
data.matrix <- as.matrix(data.tags)
sim <- data.matrix / sqrt(rowSums(data.matrix * data.matrix))
sim <- sim %*% t(sim)
d_sim <- as.dist(1 - sim)
d_sim[is.na(d_sim)] <- 0.0

# Clustering the data
dendrogram <- hclust(d_sim, method = "average")

# Cutting the dendrogram
cut.results <- cutreeHybrid(dendro = dendrogram, distM = as.matrix(d_sim),
                            minClusterSize = 1, verbose = 0)

# Score
silhouette.scores <- silhouette(cut.results$labels, dist = as.matrix(d_sim))
summary.silhouette <- summary(silhouette.scores)
avg.silhouette <- round(summary.silhouette$avg.width, digits = 2)

# Printing information
text.out <- paste(file.path, avg.silhouette, sep = ",")
message(text.out)
