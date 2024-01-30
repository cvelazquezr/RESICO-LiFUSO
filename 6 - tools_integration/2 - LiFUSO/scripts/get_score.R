library(cluster)
library(dynamicTreeCut)

args = commandArgs(trailingOnly=TRUE)

if (length(args) == 0) {
  stop("A folder path must be supplied", call.=FALSE)
}

folder.path <- args[1]
folder.combinations <- list.files(path = folder.path)

for (folder in folder.combinations) {
  folder.files <- paste(folder.path, folder, sep="/")
  csv.files <- list.files(path = folder.files, pattern = "*.csv")
  
  for (file.name in csv.files) {
    path <- paste(folder.files, file.name, sep ="/")
    data.tags <- read.csv(path, header = F)
    
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
    text.out <- paste(path, avg.silhouette, sep = ",")
    message(text.out)
  }
}
