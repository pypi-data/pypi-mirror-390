 1. Line Plot
r
Copy
Edit
x <- c(1, 2, 3, 4, 5)
y <- c(2, 4, 6, 8, 10)

plot(x, y, type="l", col="blue", main="Line Plot", xlab="X-axis", ylab="Y-axis")
🔹 2. Scatter Plot
r
Copy
Edit
x <- c(1, 2, 3, 4, 5)
y <- c(5, 3, 6, 2, 7)

plot(x, y, main="Scatter Plot", xlab="X", ylab="Y", col="red", pch=19)
🔹 3. Pie Chart
r
Copy
Edit
slices <- c(10, 20, 30, 40)
labels <- c("A", "B", "C", "D")

pie(slices, labels=labels, main="Pie Chart")
🔹 4. Bar Chart
r
Copy
Edit
values <- c(5, 10, 15, 20)
names <- c("A", "B", "C", "D")

barplot(values, names.arg=names, col="green", main="Bar Chart", ylab="Values")