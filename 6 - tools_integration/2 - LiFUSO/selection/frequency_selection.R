
frequency.selection <- function(results.calls, results.frequent) {
  methods.dataframe <- results.frequent$methods
  
  # Get the most frequent methods
  frequency.methods <- methods.dataframe$freq.methods
  unique.methods <- methods.dataframe$unique.methods
  precedents.methods <- methods.dataframe$precedents
  
  if (length(frequency.methods) == 1) {
    return(list(c(str_c(precedents.methods[1], ".", unique.methods[1]))))
  }
  
  outliers <- get_outliers(frequency.methods)
  
  if (length(outliers) == 0) {
    outliers <- get_outliers(frequency.methods, 1)
  }
  
  if (length(outliers) == 0) {
    return(list(c()))
  }
  
  last.outlier <- outliers[length(outliers)]
  data.iterate <- which(frequency.methods == last.outlier)
  selected.calls <- c()
  
  # Generate the calls from the methods' precedence
  for (index.methods in c(1:data.iterate)) {
    selected.precedents.divided <- strsplit(precedents.methods[index.methods], ",")[[1]]
    calls.generated <- unname(unlist(Map(function(precedent) str_c(precedent, ".", unique.methods[index.methods]), 
                                         selected.precedents.divided)))
    
    selected.calls <- c(selected.calls, calls.generated)
  }
  
  # Iterate over the snippets and select only the generated calls
  filtered.snippets <- c()
  
  for (snippet in results.calls) {
    snippet.divided <- strsplit(snippet, "<br>")[[1]]
    snippet.filtered <- Filter(function(call) call %in% selected.calls, snippet.divided)
    
    if (length(snippet.filtered) > 0) {
      joined.snippet <- paste(snippet.filtered, collapse = "<br>")
      filtered.snippets <- c(filtered.snippets, joined.snippet)
    }
  }
  
  return(list(filtered.snippets))
}


cluster.name <- function(all.names) {
  unique.names <- unique(all.names)
  frequency.elements <- unlist(lapply(unique.names, function(element) length(which(all.names == element))))
  sorted.frequencies <- sort(frequency.elements, decreasing = T)
  outliers.names <- get_outliers(sorted.frequencies)
  
  if (length(outliers.names) == 0) {
    outliers.names <- get_outliers(sorted.frequencies, 1)
  }
  
  if (length(outliers.names) == 0) {
    outliers.names <- max(sorted.frequencies)
  }
  
  last.outlier <- outliers.names[length(outliers.names)]
  data.iterate <- which(sorted.frequencies == last.outlier) * 2
  
  process.name <- function(name) {
    name.divided <- strsplit(name, "\\|")[[1]]
    str.composed <- c()
    
    if (length(name.divided) >= 4) {
      if (length(name.divided) == 4) {
        if (name.divided[2] == "VB")
          str.composed <- c(name.divided[1], name.divided[3])
        else
          str.composed <- c(name.divided[3], name.divided[1])
      }
      
      if (length(name.divided) > 4) {
        if (name.divided[2] == "VB") {
          str.composed <- c(name.divided[1])
          
          for (index in seq(from=3, to=length(name.divided), by=2)) {
            str.composed <- c(str.composed, name.divided[index])
          }
        }
        else {
          str.composed <- c(name.divided[length(name.divided) - 1])
          
          for (index in seq(from=length(name.divided) - 3, to=1, by=-2)) {
            str.composed <- c(str.composed, name.divided[index])
          }
        }
      }
    }
  
    return(paste(str.composed, collapse = " "))
  }
  
  obtain.selected.elements <- function(data.index) {
    index.name <- sorted.frequencies[data.index]
    selected.elements <- unique.names[which(frequency.elements >= index.name)]
    selected.elements <- Filter(function(name) !grepl("<", name), selected.elements)
    selected.elements <- Filter(function(name) !grepl(">", name), selected.elements)
    
    return(selected.elements)
  }
  
  selected.elements <- obtain.selected.elements(data.iterate)
  original.length <- length(selected.elements)
  names <- unique(unlist(lapply(selected.elements, process.name)))
  names <- Filter(function(name) nchar(name) > 0, names)
  
  if (original.length > length(names)) {
    diff.index <- original.length - length(names)
    
    selected.elements <- obtain.selected.elements(data.iterate + diff.index)
    
    names <- unique(unlist(lapply(selected.elements, process.name)))
    names <- Filter(function(name) nchar(name) > 0, names)
  }
  
  names.cluster <- data.frame(name=names)
  return(names.cluster)
}
