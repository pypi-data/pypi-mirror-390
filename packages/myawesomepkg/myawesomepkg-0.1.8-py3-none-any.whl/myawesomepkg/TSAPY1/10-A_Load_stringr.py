✅ Step 1: Load stringr
r
Copy
Edit
library(stringr)
🔹 1. String Basics
r
Copy
Edit
str <- "Hello Boss"
str_length(str)         # Length of string
str_to_upper(str)       # Uppercase
str_to_lower(str)       # Lowercase
str_trim("  Hello  ")   # Trim spaces
🔹 2. Combining Strings
r
Copy
Edit
str1 <- "Hello"
str2 <- "Boss"
str_c(str1, str2, sep = " ")  # Combine with space
🔹 3. Subsetting Strings
r
Copy
Edit
str_sub("DataScience", 1, 4)   # "Data"
str_sub("DataScience", -7, -1) # "Science"
🔹 4. Locales
r
Copy
Edit
str_to_upper("straße", locale = "de")  # German-specific case
🔹 5. Basic Matches
r
Copy
Edit
str_detect("apple", "pp")   # TRUE
str_detect("apple", "z")    # FALSE
🔹 6. Anchors (^, $)
r
Copy
Edit
str_detect("Boss is here", "^Boss")   # TRUE
str_detect("Boss is here", "here$")   # TRUE
🔹 7. Repetition
r
Copy
Edit
str_view("banana", "na{2}")    # Match "n" followed by two "a"s
str_view("aaa", "a{2,3}")      # Match 2 to 3 a's
🔹 8. Detect Matches
r
Copy
Edit
texts <- c("cat", "dog", "cow")
str_detect(texts, "c")   # TRUE FALSE TRUE
🔹 9. Extract Matches
r
Copy
Edit
str_extract("Price: Rs 999", "\\d+")   # "999"
🔹 10. Grouped Matches
r
Copy
Edit
str_match("ID: 12345", "ID: (\\d+)")   # Group match returns matrix
🔹 11. Replacing Matches
r
Copy
Edit
str_replace("I love cats", "cats", "dogs")  # "I love dogs"
🔹 12. Splitting
r
Copy
Edit
str_split("one,two,three", ",")[[1]]   # "one" "two" "three"
Let me know if you want all these examples as a downloadable .R script or a reference