import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np

# Load JSON data from file
with open("metamask_swaps.json", "r") as file:
    data = json.load(file)

# Load data into DataFrame
df = pd.DataFrame(data)

# Convert the DATE column to datetime
df['DATE'] = pd.to_datetime(df['DATE'])

# Filter data for the last quarter of 2023
start_date = '2023-10-01'
end_date = '2023-12-31'
df_filtered = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]


# Pivot the DataFrame to have API_PROVIDER as columns
pivot_df = df_filtered.pivot_table(index='DATE', columns='API_PROVIDER', values='BRIDGE_COUNT')
print(pivot_df.describe())

# Plot the time series
pivot_df.plot(figsize=(10, 6))
plt.title('Bridge Count by API Provider (Last Quarter of 2023)')
plt.xlabel('Date')
plt.ylabel('Bridge Count')
plt.grid(True)
plt.legend(title='API Provider')
plt.savefig('charts/Bridge_Count_timeseries.png')


# Group by API_PROVIDER and sum the BRIDGE_COUNT
bridge_counts = df_filtered.groupby('API_PROVIDER')['BRIDGE_COUNT'].sum()

# Get unique colors for each group
colors = plt.cm.tab10(range(len(bridge_counts)))

# Plot the Bridge Count
fig, ax = plt.subplots(figsize=(10, 6))
for i, (provider, count) in enumerate(bridge_counts.items()):
    ax.bar(provider, count, color=colors[i], label=provider)

plt.title('Bridge Count by API Provider (Last Quarter of 2023)')
plt.xlabel('API Provider')
plt.ylabel('Bridge Count')
plt.grid(axis='y')
plt.legend()
plt.savefig('charts/Bridge_count_Q4.png')


# Drop rows with missing values
pivot_df.dropna(inplace=True)

# Calculate the line of best fit for each column (API_PROVIDER)
plt.figure(figsize=(10, 6))

for col in pivot_df.columns:
    x_values = (pivot_df.index - pivot_df.index[0]).days  # Convert dates to days since the first date
    y_values = pivot_df[col]

    # Calculate the line of best fit
    coefficients = np.polyfit(x_values, y_values, 1)
    line = np.poly1d(coefficients)

    # Print the daily change (slope)
    slope_daily = coefficients[0]
    print(f"Slope for {col}: gaining {slope_daily} new bridge uses per day")

    # Plot the data and the line of best fit
    plt.scatter(x_values, y_values, label=col)
    plt.plot(x_values, line(x_values), label=f'Line of Best Fit - {col}')

plt.xlabel('Days since {}'.format(pivot_df.index[0].strftime('%Y-%m-%d')))
plt.ylabel('Bridge Count')
plt.title('Line of Best Fit for each API Provider')
plt.legend()
plt.savefig('charts/line_of_best_fit.png')
