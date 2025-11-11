✅ Step 1: Install & Load ggplot2
r
Copy
Edit
install.packages("ggplot2")  # Run once
library(ggplot2)
✅ Step 2: Sample Data
r
Copy
Edit
data <- data.frame(
  category = rep(c("A", "B", "C"), each=4),
  subcat = rep(c("X", "Y"), times=6),
  value = c(4, 7, 6, 9, 5, 3, 8, 4, 7, 5, 6, 2)
)
✅ Step 3: Basic ggplot
r
Copy
Edit
ggplot(data, aes(x=subcat, y=value)) +
  geom_bar(stat="identity", fill="steelblue") +
  ggtitle("Basic Bar Chart")
✅ Step 4: Facets
r
Copy
Edit
ggplot(data, aes(x=subcat, y=value)) +
  geom_bar(stat="identity", fill="tomato") +
  facet_wrap(~ category) +
  ggtitle("Faceted by Category")
✅ Step 5: Geometric Objects
r
Copy
Edit
ggplot(data, aes(x=subcat, y=value, fill=category)) +
  geom_bar(stat="identity", position="dodge") +   # Bar chart
  geom_point(aes(color=category), size=3, shape=21) +  # Add points
  ggtitle("Geometric Objects: Bars + Points")
✅ Step 6: Position Adjustment
r
Copy
Edit
ggplot(data, aes(x=subcat, y=value, fill=category)) +
  geom_bar(stat="identity", position=position_dodge(width=0.7)) +
  ggtitle("Position: Dodge for Side-by-Side Bars")
✅ Step 7: Coordinate System (Flip Axis)
r
Copy
Edit
ggplot(data, aes(x=subcat, y=value, fill=category)) +
  geom_bar(stat="identity") +
  coord_flip() +
  ggtitle("Flipped Coordinates")
