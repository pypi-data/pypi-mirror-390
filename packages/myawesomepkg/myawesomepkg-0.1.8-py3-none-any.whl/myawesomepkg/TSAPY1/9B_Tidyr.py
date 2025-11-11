✅ Step 1: Load tidyr and dplyr
r
Copy
Edit
library(tidyr)
library(dplyr)
🔹 Sample Data
r
Copy
Edit
data <- data.frame(
  name = c("Alice", "Bob"),
  math = c(90, 85),
  science = c(95, 80)
)
🔹 1. Gathering → pivot_longer()
r
Copy
Edit
data_long <- data %>%
  pivot_longer(cols = c(math, science), names_to = "subject", values_to = "score")

print(data_long)
🔹 2. Spreading → pivot_wider()
r
Copy
Edit
data_wide <- data_long %>%
  pivot_wider(names_from = subject, values_from = score)

print(data_wide)
🔹 3. Separate Columns
r
Copy
Edit
full_name <- data.frame(name = c("Alice_Smith", "Bob_Jones"))

# Separate name into first and last
full_name_sep <- full_name %>%
  separate(name, into = c("first_name", "last_name"), sep = "_")

print(full_name_sep)
🔹 4. Unite Columns
r
Copy
Edit
# Combine first_name and last_name
full_name_united <- full_name_sep %>%
  unite("full_name", first_name, last_name, sep = " ")

print(full_name_united)
🔹 5. Handling Missing Values
r
Copy
Edit
missing_data <- data.frame(
  name = c("A", "B", "C"),
  score = c(85, NA, 90)
)

# Remove rows with NA
missing_data_clean <- missing_data %>%
  drop_na()

# Replace NA with value
missing_data_filled <- missing_data %>%
  replace_na(list(score = 0))

print(missing_data_clean)
print(missing_data_filled)
Let m