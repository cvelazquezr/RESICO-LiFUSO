shinyServer(function(input, output, session) {
    
    output$clustersTreeMapUI <- renderHighchart({
      # Selecting the input for an specific library and combination
      # Data reading
      data.path <- str_c(getwd(), "/datasets/input/", input$library)
      data.tags <- read.csv(str_c(data.path, "/similarity_matrix.csv"), header = F)
      
      data.usages <- readLines(str_c(data.path, "/code_usages.txt"))
      name.candidates <- readLines(str_c(data.path, "/name_candidates.txt"))
      titles.information <- readLines(str_c(data.path, "/extra_information.txt"))
      
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
      
      # Inspecting the clusters
      cluster.labels <- unname(cut.results$labels)
      unique.labels <- unique(cluster.labels)
      number.clusters <<- length(unique.labels)
      
      silhouette.scores <- silhouette(cut.results$labels, dist = as.matrix(d_sim))
      summary.silhouette <- summary(silhouette.scores)
      
      output$silhouetteScore <- renderText({
        str_c("Silhouette Score: ", round(summary.silhouette$avg.width, digits = 2))
      })
      
      output$numberClusters <- renderText({
        str_c("Number of Clusters: ", number.clusters)
      })
      
      # Get the usages for each cluster
      get.labels <- function(index.label) {
        indexes.cluster <- which(cluster.labels == index.label)
        labels.cluster <- unname(data.usages[indexes.cluster])
        
        # Join all usages
        all.labels <- str_c(labels.cluster, collapse = " ")
        
        return(all.labels)
      }
      
      # Get the names for each cluster
      get.names <- function(index.label) {
        indexes.cluster <- which(cluster.labels == index.label)
        names.cluster <- unname(name.candidates[indexes.cluster])
        
        # Join all names
        all.names <- str_c(names.cluster, collapse = " ")
        
        return(all.names)
      }
      
      # Get the links of titles
      get.links <- function(index.label) {
        indexes.cluster <- which(cluster.labels == index.label)
        information.cluster <- unname(titles.information[indexes.cluster])
        
        # Making link elements
        links <- c()
        for (information.title in information.cluster) {
          information.divided <- strsplit(information.title, "-->")[[1]]
          title.post <- information.divided[1]
          link.post <- information.divided[2]
          
          link <- str_c('<a href="',link.post,'">',title.post,'</a>')
          links <- c(links, link)
        }
        
        return(links)
      }
      
      # Make document composed by other documents for the usages
      document.corpus <- get.labels(unique.labels[1])
      for (iter in c(2 : length(unique.labels))) {
        document.corpus <- c(document.corpus, get.labels(unique.labels[iter]))
      }
      
      # Make document composed by other documents for the names
      document.names <- get.names(unique.labels[1])
      for (iter in c(2 : length(unique.labels))) {
        document.names <- c(document.names, get.names(unique.labels[iter]))
      }
      
      # API Usage information
      cluster.group <- c()
      cluster.subgroup <- c()
      value.length <- c()
      value.calls <- c()
      value.name <- c()
      
      k <- 1
      for (document in document.corpus) {
        cluster.sentence <- strsplit(document, " ")[[1]]
        cluster.group <- c(cluster.group, rep(str_c("cluster-", k), length(cluster.sentence)))
        cluster.subgroup <- c(cluster.subgroup, str_c("Snippet-", c(1:length(cluster.sentence))))
        
        usages.subgroup <- c()
        for (usage in cluster.sentence) {
          usages.subgroup <- c(usages.subgroup, str_replace_all(usage, ",", "<br>"))
          usage.divided <- strsplit(usage, ",")[[1]]
          value.length <- c(value.length, length(usage.divided))
        }
        value.calls <- c(value.calls, usages.subgroup)
        k <- k + 1
      }
      
      for (document in document.names) {
        cluster.sentence <- strsplit(document, " ")[[1]]
        
        for (name in cluster.sentence) {
          value.name <- c(value.name, name)
        }
      }
      
      title.links <- c()
      for (iter in c(1 : length(unique.labels))) {
        title.links <- c(title.links, get.links(unique.labels[iter]))
      }
      
      # Data frame to show information
      data.information <<- data.frame(cluster.group,
                                      cluster.subgroup,
                                      value.calls,
                                      value.length,
                                      value.name,
                                      title.links)
      
      data.information <<- data.information %>%
        rename(
          group = cluster.group,
          subgroup = cluster.subgroup,
          calls = value.calls,
          value = value.length,
          name = value.name,
          links = title.links
        )
      
      # Extract information to show on the Summary tab
      frequency.attributes <- most.frequent.attributes(data.information, number.clusters)
      
      output$popularClass <- renderText({
        str_c("Most frequent class: <font color=\"#FF0000\"><b>",
              frequency.attributes$frequent.class$unique.classes,
              "</b></font> used ",
              frequency.attributes$frequent.class$frequency.classes, " times.")
      })
      
      output$popularAPI <- renderText({
        str_c("Most frequent API: <font color=\"#FF0000\"><b>", 
              frequency.attributes$frequent.api$unique.apis,
              "</b></font> used ", 
              frequency.attributes$frequent.api$frequency.apis, " times.")
      })
      
      output$populationChart <- renderPlot({
        population.data <- frequency.attributes$population
        
        ggplot(population.data, aes(Type, Quantity)) + 
          geom_lv(aes(fill = Type), color='black', size=0.75) + 
          geom_boxplot(outlier.alpha = 0, coef=0, fill="#00000000") +
          scale_y_continuous(breaks = scales::pretty_breaks(n = 20)) +
          theme(legend.position = "none", text = element_text(size=20))
      })
      
      # Construct hierarchical data
      hierarchical.data <- data_to_hierarchical(data.information,
                                                group_vars = c("group", "subgroup"),
                                                size_var = "value")
      
      # Adding more information to the hierarchical data 
      k <- 1
      for (item in hierarchical.data) {
        if (!is.null(item$parent)) {
          calls.item <- filter(data.information, group == item$parent & subgroup == item$name)$calls
          item$calls <- calls.item
        }
        hierarchical.data[[k]] <- item
        k <- k + 1
      }
      
      clickJS <- JS("function(event) {Shiny.onInputChange('treemapclick', event.point.name);}")
      hchart(hierarchical.data,
             type = "treemap",
             layoutAlgorithm = "squarified",
             levelIsConstant = T,
             allowDrillToNode = T,
             levels = list(
               list(level = 1,
                    dataLabels = list(enabled = T),
                    borderWidth = 3,
                    borderColor = "black"),
               
               list(level = 2,
                    dataLabels = list(enabled = F))
             )) %>%
        hc_tooltip(pointFormat = "<b>API calls: {point.value:,.0f}</b><br>
                                  {point.calls}") %>%
        hc_title(text = str_c(input$library, " library")) %>%
        hc_plotOptions(treemap = list(events = list(click = clickJS)))
    })
    
    # Extracts the frequency of classes and methods from all clusters
    most.frequent.attributes <- function(all.data, number.clusters) {
      all.classes <- c()
      all.apis <- c()
      
      metrics.per.cluster <- c()
      types.metrics.per.cluster <- c()
      
      frequency.classes <- c()
      frequency.apis <- c()
      
      for (index in 1:number.clusters) {
        cluster.name <- str_c("cluster-", index)
        filtered.data <- filter(data.information, group == cluster.name)
        
        classes.methods.calls.list <- classes.methods.calls(filtered.data$calls)
        
        all.classes <- c(all.classes, classes.methods.calls.list$classes)
        all.apis <- c(all.apis, classes.methods.calls.list$methods)
        
        metrics.per.cluster <- c(metrics.per.cluster, length(classes.methods.calls.list$classes))
        metrics.per.cluster <- c(metrics.per.cluster, length(classes.methods.calls.list$methods))
        
        types.metrics.per.cluster <- c(types.metrics.per.cluster, "Classes")
        types.metrics.per.cluster <- c(types.metrics.per.cluster, "APIs")
      }
      
      unique.classes <- unique(all.classes)
      unique.apis <- unique(all.apis)
      
      for (class.name in unique.classes) {
        frequency.classes <- c(frequency.classes, length(which(all.classes == class.name)))
      }
      
      for (api.name in unique.apis) {
        frequency.apis <- c(frequency.apis, length(which(all.apis == api.name)))
      }
      
      df.classes <- data.frame(unique.classes, frequency.classes)
      most.frequent.class <- head(df.classes[order(frequency.classes, decreasing = T),], n = 1)
      
      df.apis <- data.frame(unique.apis, frequency.apis)
      most.frequent.api <- head(df.apis[order(frequency.apis, decreasing = T),], n = 1)
      
      df.population <- data.frame(Quantity=metrics.per.cluster, Type=types.metrics.per.cluster)
      
      list(frequent.class=most.frequent.class, frequent.api=most.frequent.api, population=df.population)
    }
    
    # Extracts classes and methods from the usages of a specific cluster
    classes.methods.calls <- function(cluster, unique = F) {
      all.classes <- c()
      all.methods <- c()
      all.calls <- c()
      
      for (usage in cluster) {
        cleaned.calls <- strsplit(usage, "<br>")[[1]]
        all.calls <- c(all.calls, cleaned.calls)
        
        classes.usages <- c()
        methods.usages <- c()
      
        for (call in cleaned.calls) {
          call.divided <- strsplit(call, "\\.")[[1]]
          
          classes.usages <- c(classes.usages, call.divided[1])
          methods.usages <- c(methods.usages, call.divided[2:length(call.divided)])
        }
        
        unique.classes.usages <- unique(classes.usages)
        unique.methods.usages <- unique(methods.usages)
        
        if (unique) {
          all.classes <- c(all.classes, unique.classes.usages)
          all.methods <- c(all.methods, unique.methods.usages)
        } else {
          all.classes <- c(all.classes, classes.usages)
          all.methods <- c(all.methods, methods.usages)
        }
      }
      
      list(classes=all.classes, methods=all.methods, calls=all.calls)
    }

    obtain.frequency <- function(data.calls) {
      # Extracting frequencies from the calls
      classes.methods.calls.list <- classes.methods.calls(data.calls)
      
      all.classes <- classes.methods.calls.list$classes
      all.methods <- classes.methods.calls.list$methods
      all.calls <- classes.methods.calls.list$calls
      
      unique.classes <- unique(all.classes)
      unique.methods <- unique(all.methods)
      
      freq.classes <- unlist(lapply(unique.classes, function(class.name) length(which(all.classes == class.name))))
      freq.methods <- unlist(lapply(unique.methods, function(method.name) length(which(all.methods == method.name))))
      
      percent.classes <- round(freq.classes / length(data.calls), digits = 2) * 100
      percent.classes <- unlist(lapply(percent.classes, function(freq) if (freq > 100) 100 else freq))
      percent.methods <- round(freq.methods / length(data.calls), digits = 2) * 100
      percent.methods <- unlist(lapply(percent.methods, function(freq) if (freq > 100) 100 else freq))
      
      # Getting the precedents of the method calls
      precedents <- c()
      for (method.call in unique.methods) {
        precedents.method_call <- c()
        
        for (call in all.calls) {
          call.divided <- strsplit(call, "\\.")[[1]]
        
          if (method.call %in% call.divided) {
            indexes.method_call <- which(call.divided == method.call)
            
            for (index in indexes.method_call) {
              precedents.method_call <- c(precedents.method_call, paste(call.divided[1:index - 1], collapse = "."))
            }
          }
        }
        precedents <- c(precedents, paste(unique(precedents.method_call), collapse = ","))
      }
      
      df.classes <- data.frame(unique.classes, freq.classes, percent.classes)
      df.methods <- data.frame(unique.methods, freq.methods, percent.methods, precedents)
      
      # Order data frames
      ordered.classes <- df.classes[order(freq.classes, decreasing = T),]
      ordered.methods <- df.methods[order(freq.methods, decreasing = T),]
      
      return(list("classes" = ordered.classes, "methods" = ordered.methods))
    }
    
    # Reacts to the event of clicking into a cluster and shows information about it
    observeEvent(input$treemapclick, {
      if (!is.null(input$treemapclick)) {
        element.clicked <- input$treemapclick
        if (startsWith(element.clicked, "cluster-")) {
          cluster.name <- element.clicked
          filtered.data <- filter(data.information, group == cluster.name)
          filtered.data_names <- filtered.data$name
          filtered.data_calls <- filtered.data$calls
          
          # Getting frequent calls and methods
          results.list <- obtain.frequency(filtered.data_calls)
          
          # Finding the frequency of the names
          joined.names <- paste(filtered.data_names, collapse = ",")
          
          all.names <<- strsplit(joined.names, ",")[[1]]
          
          unique.names <- unique(all.names)
          frequency.names <- c()
          for (name in unique.names) {
            frequency.names <- c(frequency.names, length(which(all.names == name)))
          }
          
          df.names <- data.frame(unique.names, frequency.names)
          first_n.names <- head(df.names[order(frequency.names, decreasing = T),], n = 20)
          
          print(cluster.name)
          print(length(filtered.data_names))
          print("==============================")
          
          output$frequentClasses <- renderTable(head(results.list$classes, n = 10), caption = "Frequent Classes")
          output$frequentMethods <- renderTable(head(results.list$methods, n = 10), caption = "Frequent Methods")
          
          frequency.methods <- results.list$methods$freq.methods
          outliers <- get_outliers(frequency.methods)
          
          if (length(outliers) > 0 || length(frequency.methods) <= 5) {
            output$distinctionCluster <- renderText({
              "Cluster well defined"
            })
            
            output$namesOutput <- renderUI({
              apply(cluster.name(all.names), 1, function(x) tags$li(HTML(x['name'])))
            })
          } else {
            output$distinctionCluster <- renderText({
              "Cluster with an unclear prevalence of methods"
            })
            
            output$namesOutput <- renderUI({
              "No name since there is not a clear prevalence of methods"
            })
          }
          
          output$titlesOutput <- renderUI({
            apply(filtered.data, 1, function(x) tags$li(HTML(x['links'])))
          })
        }
      }
    })

    # Generate the books for those clusters well defined
    observeEvent(input$books, {
      # Get the features that are considered as well-defined
      get.distinctions <- function(number.cluster) {
        name.cluster <- str_c("cluster-", number.cluster)
        filtered.data <- filter(data.information, group == name.cluster)
        filtered.data_names <- filtered.data$name
        
        results.calls <- filtered.data$calls
        results.frequent <- obtain.frequency(results.calls)
        
        selected.snippets <- frequency.selection(results.calls, results.frequent)
        
        if (is.null(selected.snippets[[1]])) {
          return(list(c(), c()))
        }
        
        joined.names <- paste(filtered.data_names, collapse = ",")
        all.names <<- strsplit(joined.names, ",")[[1]]
        
        selected.names <- cluster.name(all.names)
        
        return(list(selected.snippets, selected.names))
      }
      
      # Parallel processing
      results.distinctions <- mclapply(1:number.clusters, get.distinctions)
      results.distinctions <- Filter(function(element) !is.null(element[[1]]), results.distinctions)

      # Extract the data from the lists
      distinction.code <- lapply(results.distinctions, function(result) result[[1]])
      names.code <- lapply(results.distinctions, function(result) result[[2]])

      generate.books(input$library, distinction.code, names.code)
    })
    
    # Event that reacts when the Evaluate button is clicked
    observeEvent(input$evaluate, {
      print("Performing Evaluation ...")
      
      print("Getting usages on the clusters ...")
      number.clusters <- as.integer(strsplit(last(data.information$group), "-")[[1]][2])
      
      get.usages <- function(number.cluster) {
        name.cluster <- str_c("cluster-", number.cluster)
        filtered.data <- filter(data.information, group == name.cluster)
        
        results.calls <- filtered.data$calls
        results.frequent <- obtain.frequency(results.calls)
        
        return(frequency.selection(results.calls, results.frequent))
      }
      
      # Parallel processing
      results.usages <- mclapply(1:number.clusters, get.usages)
      results.filtered <- Filter(function(element) !is.null(element[[1]]), results.usages)

      # Extract the data
      clusters <- lapply(results.filtered, function(result) result[[1]])
      
      print("Done!")

      ################### RQ2 ###################
      print("RQ2 ...")
      print("Performing processing of features ...")
      evaluation.rq2 <- evaluation_rq2(clusters, input$library)
      evaluated.rq2 <- evaluation.rq2[[1]]
      number.tutorials <- evaluation.rq2[[2]]
      
      print("Done with the processing!")

      print("Summary of the evaluation ...")

      features.matched <- unique(evaluated.rq2$feature.number)
      filtered.dataframe_cookbook <- data.frame()

      for (feature.number_matched in features.matched) {
        filtered.cluster <- evaluated.rq2 %>%
          filter(feature.number == feature.number_matched) %>%
          filter(relevance == max(relevance))

        filtered.dataframe_cookbook <- rbind(filtered.dataframe_cookbook, head(filtered.cluster, n = 1))
      }

      mean.relevance_cookbooks <- mean(filtered.dataframe_cookbook$relevance)
      mean.overflow_cookbooks <- mean(filtered.dataframe_cookbook$overflow)
      mean.overflow.classes_cookbooks <- mean(filtered.dataframe_cookbook$overflow.classes)
      mean.overflow.methods_cookbooks <- mean(filtered.dataframe_cookbook$overflow.methods)

      print(str_c("Number of selected clusters: ", length(clusters)))
      print(str_c("Number of matched features: ", length(features.matched)))
      print("Matched features: ")
      print(features.matched)
      print(str_c("Mean of features' relevances: ", round(mean.relevance_cookbooks, digits=2)))
      print(str_c("Mean of features' overflows: ", round(mean.overflow_cookbooks, digits=2)))
      print(str_c("Mean of features' overflow classes: ", round(mean.overflow.classes_cookbooks, digits=2)))
      print(str_c("Mean of features' overflow methods: ", round(mean.overflow.methods_cookbooks, digits=2)))

      print("Done!")
      
      ################### RQ3 ###################
      print("RQ3 ...")

      # Removing clusters matched in the previous step
      filtered.dataframe <- data.frame()

      for (feature.number_matched in features.matched) {
        filtered.cluster <- evaluated.rq2 %>%
          filter(feature.number == feature.number_matched) %>%
          filter(relevance == max(relevance))

        filtered.dataframe <- rbind(filtered.dataframe, head(filtered.cluster, n = 1))
      }

      clusters.matched <- unique(filtered.dataframe$cluster.number)
      clusters[clusters.matched] <- list(c())
      clusters <- Filter(function(cluster) !is.null(cluster), clusters)

      # Sending the remaining for evaluation
      evaluation.rq3 <- evaluation_github(clusters, input$library)
      evaluated.clusters_github <- evaluation.rq3[[1]]
      number.github <- evaluation.rq3[[2]]

      features.matched_github <- unique(evaluated.clusters_github$feature.number)
      filtered.dataframe_github <- data.frame()

      for (feature.number_matched in features.matched_github) {
        filtered.cluster <- evaluated.clusters_github %>%
          filter(feature.number == feature.number_matched) %>%
          filter(relevance == max(relevance))

        filtered.dataframe_github <- rbind(filtered.dataframe_github, head(filtered.cluster, n = 1))
      }
      
      clusters.extended <- unique(filtered.dataframe_github$cluster.number)
      mean.relevance <- mean(filtered.dataframe_github$relevance)
      mean.overflow <- mean(filtered.dataframe_github$overflow)
      mean.overflow_classes <- mean(filtered.dataframe_github$overflow.classes)
      mean.overflow_methods <- mean(filtered.dataframe_github$overflow.methods)

      print(str_c("Number of previously matched clusters: ", length(clusters.matched)))
      print(str_c("Number of new matched clusters: ", length(clusters.extended)))
      print(str_c("Mean of their relevances: ", round(mean.relevance, digits = 2)))
      print(str_c("Mean of features' overflows: ", round(mean.overflow, digits=2)))
      print(str_c("Mean of features' overflow classes: ", round(mean.overflow_classes, digits=2)))
      print(str_c("Mean of features' overflow methods: ", round(mean.overflow_methods, digits=2)))

      print("Done!")

      print("Done with the evaluation!")
    })
  }
)