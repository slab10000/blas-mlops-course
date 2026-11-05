"""The data contract for deliveries: what a valid file looks like."""
COLUMNS = ["distance_km", "items", "hour", "raining", "courier_months", "restaurant", "late"]
RESTAURANTS = ["pizza", "sushi", "burger", "salad", "thai"]


def problems(df):
    """Return a list of what is wrong with df. An empty list means the data passes."""
    found = []
    if list(df.columns) != COLUMNS:
        found.append(f"columns are {list(df.columns)}, expected {COLUMNS}")
        return found
    if df.isna().any().any():
        found.append("there are missing values")
    if not df["distance_km"].between(0.1, 50).all():
        found.append(f"distance_km outside 0.1 to 50 (max is {df['distance_km'].max():g}): wrong units?")
    if not df["items"].between(1, 30).all():
        found.append("items outside 1 to 30")
    if not df["hour"].between(0, 23).all():
        found.append("hour outside 0 to 23")
    if not df["restaurant"].isin(RESTAURANTS).all():
        found.append("unknown restaurant name")
    if not 0.05 < df["late"].mean() < 0.40:
        found.append(f"late rate {df['late'].mean():.2f} outside 0.05 to 0.40")
    return found
