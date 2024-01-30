generate.books <- function(library.name, selected.feature.code, selected.feature.name) {
  print("Generating Feature Books ...")
  old.wd <- getwd()
  book.folder <- "books"
  
  # Generating the data for the book
  # Title
  data.str <- sprintf("#' ---\n#' title: \"Feature Book for the **%s** library\"\n#' ---\n\n", library.name)
  data.str <- str_c(data.str, "#'\n")
  data.str <- str_c(data.str, "#' ```{r setup, include=FALSE}\n")
  data.str <- str_c(data.str, "#' knitr::opts_chunk$set(echo = TRUE)\n")
  data.str <- str_c(data.str, "#' ```\n")
  data.str <- str_c(data.str, "#'\n")
  
  for (index.code in c(1:length(selected.feature.code))) {
    # Get feature name
    names <- selected.feature.name[index.code][[1]]$name
    
    # Get feature code
    code.description <- unlist(selected.feature.code[index.code][[1]])
    code.description <- unique(code.description)
    
    if (!is.null(code.description)) {
      data.str <- str_c(data.str, sprintf("#' **Feature %s**\n", index.code))
      data.str <- str_c(data.str, "#'\n")
      
      data.str <- str_c(data.str, "#' Name description:\n")
      data.str <- str_c(data.str, "#'\n")
      data.str <- str_c(data.str, sprintf("#' %s\n", paste(names, collapse = ",")))
      data.str <- str_c(data.str, "#'\n")
      
      data.str <- str_c(data.str, "#' Code description:\n")
      for (call in code.description) {
        call <- str_replace_all(call, "<br>", ",")
        data.str <- str_c(data.str, "#'\n")
        data.str <- str_c(data.str, "#' ```{java}\n")
        data.str <- str_c(data.str, sprintf("#' %s\n", call))
        data.str <- str_c(data.str, "#' ```\n")
      }
      
      data.str <- str_c(data.str, "#' \n")
      data.str <- str_c(data.str, "#' \n")
    }
  }
  
  # Writing the data to a file
  setwd(book.folder)
  script.name <- str_c(library.name, ".R")
  
  file.connection <- file(script.name)
  writeLines(data.str, file.connection)
  close(file.connection)
  
  knitr::spin(script.name, format = "Rmd", knit = F)
  rmarkdown::render(str_c(library.name, ".Rmd"), "html_document")
  
  # Delete files .R and .Rmd
  unlink(sprintf("%s.R", library.name))
  unlink(sprintf("%s.Rmd", library.name))
  
  setwd(old.wd)
  print("Generation done!")
}
