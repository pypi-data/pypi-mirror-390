✅ Step 1: Load dplyr
r
Copy
Edit
library(dplyr)
🔹 Sample Data
r
Copy
Edit
employees <- data.frame(
  emp_id = c(1, 2, 3, 4, 5),
  name = c("John", "Emma", "Raj", "Sara", "Mike"),
  dept_id = c(10, 20, 10, 30, 20)
)

departments <- data.frame(
  dept_id = c(10, 20, 30),
  dept_name = c("HR", "Finance", "IT")
)
🔹 1. Filtering Rows
r
Copy
Edit
# Filter employees from dept 10
employees %>% 
  filter(dept_id == 10)
🔹 2. Mutating Joins (left_join)
r
Copy
Edit
# Add department name to employees
employees %>%
  left_join(departments, by = "dept_id")
🔹 3. Inner Join
r
Copy
Edit
# Only matching employees with department info
employees %>%
  inner_join(departments, by = "dept_id")
🔹 4. Handling Duplicate Keys
r
Copy
Edit
# Add a duplicate dept row
departments2 <- rbind(departments, data.frame(dept_id = 10, dept_name = "HR-Duplicate"))

# Join - will create multiple rows for duplicate keys
employees %>%
  left_join(departments2, by = "dept_id")
🔹 5. Defining Key Column (custom join keys)
r
Copy
Edit
emp <- data.frame(id = c(1, 2), val = c("A", "B"))
ref <- data.frame(key = c(1, 2), desc = c("X", "Y"))

emp %>% 
  left_join(ref, by = c("id" = "key"))
🔹 6. Filtering Joins
r
Copy
Edit
# Semi Join: Keep rows in employees that match departments
employees %>% 
  semi_join(departments, by = "dept_id")

# Anti Join: Keep rows in employees that don't match departments
employees %>% 
  anti_join(departments, by = "dept_id")
🔹 7. Set Operations
r
Copy
Edit
a <- data.frame(x = c(1, 2, 3))
b <- data.frame(x = c(2, 3, 4))

# Union (unique values)
union(a, b)

# Intersect (common values)
intersect(a, b)

# Set difference (in a but not in b)
setdiff(a, b)