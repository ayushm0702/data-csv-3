"""Week 3: Python & Data Wrangling
Clean a messy fitness dataset in Pandas: handle missing values, filter rows,
create new columns, then visualize with Matplotlib & Seaborn.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load
df = pd.read_csv("data.csv")
print("Raw shape:", df.shape)
print(df.isna().sum(), "\n")

# 2. Fix dates: strip quotes, handle mixed formats, drop rows with no date
df["Date"] = df["Date"].astype(str).str.replace("'", "", regex=False)
df["Date"] = pd.to_datetime(df["Date"].replace("nan", pd.NA), format="mixed", errors="coerce")
df = df.dropna(subset=["Date"])

# 3. Remove duplicates
df = df.drop_duplicates()

# 4. Fix wrong values
#    - Duration 450 is a typo for 45
df.loc[df["Duration"] > 300, "Duration"] = df["Duration"] / 10
#    - Maxpulse can't be below Pulse: swap them
bad = df["Maxpulse"] < df["Pulse"]
df.loc[bad, ["Pulse", "Maxpulse"]] = df.loc[bad, ["Maxpulse", "Pulse"]].values

# 5. Missing Calories: fill with the median calories for that duration
df["Calories"] = df["Calories"].fillna(df.groupby("Duration")["Calories"].transform("median"))

# 6. New columns
df["Calories_per_min"] = (df["Calories"] / df["Duration"]).round(2)
df["Intensity"] = pd.cut(df["Maxpulse"], bins=[0, 120, 135, 300],
                         labels=["Low", "Medium", "High"])
df["Weekday"] = df["Date"].dt.day_name()

# 7. Filter rows: high-effort sessions
high = df[(df["Duration"] >= 60) & (df["Calories"] > 300)]
print("High-effort sessions:", len(high))

# 8. Save
df.sort_values("Date").to_csv("cleaned_data.csv", index=False)
print("Clean shape:", df.shape)
print(df.describe().round(2))

# 9. Visualize
sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
sns.scatterplot(data=df, x="Duration", y="Calories", hue="Intensity", ax=ax[0])
ax[0].set_title("Calories vs Duration")
sns.lineplot(data=df.sort_values("Date"), x="Date", y="Calories", marker="o", ax=ax[1])
ax[1].set_title("Daily Calories, Dec 2020")
ax[1].tick_params(axis="x", rotation=45)
plt.tight_layout()
plt.savefig("calories_plot.png", dpi=150)
