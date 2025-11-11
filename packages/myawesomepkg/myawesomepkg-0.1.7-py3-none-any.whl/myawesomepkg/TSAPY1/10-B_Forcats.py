✅ Step 1: Load forcats package
r
Copy
Edit
library(forcats)
🔹 1. Creating Factors
r
Copy
Edit
grades <- c("B", "A", "C", "A", "B")
f_grades <- factor(grades)
f_grades
With specified order:

r
Copy
Edit
f_grades <- factor(grades, levels = c("A", "B", "C"), ordered = TRUE)
🔹 2. Modifying Factor Orders
r
Copy
Edit
# Reorder by frequency
fct_infreq(f_grades)

# Reorder manually
fct_relevel(f_grades, "C", "B", "A")
🔹 3. Modifying Factor Levels (Renaming)
r
Copy
Edit
fct_recode(f_grades,
           "Excellent" = "A",
           "Good" = "B",
           "Average" = "C")
🔹 4. Lump Less Frequent Levels
r
Copy
Edit
items <- c("apple", "banana", "apple", "cherry", "banana", "fig", "fig", "fig")
f_items <- factor(items)

# Combine less frequent into "Other"
fct_lump(f_items, n = 2)
🔹 5. Drop Unused Levels
r
Copy
Edit
f <- factor(c("high", "medium", "low"), levels = c("low", "medium", "high", "extreme"))
f_dropped <- fct_drop(f)
🔹 6. Reverse Factor Order
r
Copy
Edit
fct_rev(f_grades)
🔹 7. Count Factors
r
Copy
Edit
fct_count(f_grades)
📌 Summary of Key forcats Functions

Function	Use Case
fct_relevel()	Change order of levels manually
fct_infreq()	Order by frequency
fct_recode()	Rename factor levels
fct_lump()	Combine low-freq levels
fct_drop()	Drop unused levels
fct_rev()	Reverse order
fct_count()	Count frequencies
