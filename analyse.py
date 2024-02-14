import pandas as pd
import matplotlib.pyplot as plt
import os

# Read the CSV file without specifying dtypes for columns that might have NA values
df = pd.read_csv('Bungee_TX_data.csv')

# Convert timestamp to datetime
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

# Group by token name and datetime (date and hour)
df['date'] = df['datetime'].dt.date
df['hour'] = df['datetime'].dt.hour
df['minute'] = df['datetime'].dt.minute

# Convert columns to numeric
numeric_columns = ['value', 'decimals', 'tokenPrice']
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# Calculate the token amount by dividing the value by 10**decimals
df['token_amount'] = df['value'] / (10 ** df['decimals'])

# Calculate the dollar volume of each TX
df['dollar_volume'] = df['token_amount'] * df['tokenPrice']  # Fix the calculation here

# Drop unnecessary columns
columns_to_drop = ['transactionHash', 'timestamp', 'address', 'decimals', 'Unnamed: 9']
df = df.drop(columns=columns_to_drop)

df = df[['blockNumber', 'datetime', 'date', 'hour', 'minute', 'tokenName', 'from', 'to', 'token_amount', 'tokenPrice', 'dollar_volume']]


# Basic statistics
print("Basic Volume Statistics:")
print(df['dollar_volume'].describe())

# Group by 'tokenName' and calculate the summed dollar volume for each group
token_volume_sum = df.groupby('tokenName')['dollar_volume'].sum()

# Create a pie chart
plt.figure(figsize=(10, 8))
patches, texts, autotexts = plt.pie(token_volume_sum, labels=token_volume_sum.index, startangle=140,
                                    autopct='%1.1f%%')
plt.title('Distribution of Dollar Volume grouped by Token Name')
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.tight_layout()

# Hide labels for slices below 0.5%
for i, (percentage, token_name) in enumerate(zip(token_volume_sum / token_volume_sum.sum() * 100, token_volume_sum.index)):
    if percentage < 0.5:
        texts[i].set_text('')  # Set label to an empty string if percentage is below 0.5%

# Show the plot
plt.savefig('charts/volume_pi')



# Create a directory to save the plots if it doesn't exist
if not os.path.exists('charts'):
    os.makedirs('charts')

# Filter the DataFrame for dollar_volume in the range [0, 1000]
df_range1 = df[(df['dollar_volume'] >= 50) & (df['dollar_volume'] <= 5000)]

# Plot histogram for range [0, 1000]
plt.hist(df_range1['dollar_volume'], bins=100, color='blue', alpha=0.7)
plt.xlabel('Dollar Volume')
plt.ylabel('Frequency')
plt.title('Histogram of Dollar Volume (Range: 50 - 5,000 USD)')
plt.grid(True)

# Save the plot to a file
plt.savefig('charts/Volume_hist_50_5000.png')

# Clear the current plot
plt.clf()

# Filter the DataFrame for dollar_volume in the range [1000, 800000]
df_range2 = df[(df['dollar_volume'] > 50000) & (df['dollar_volume'] <= 800000)]

# Plot histogram for range [1000, 800000]
plt.hist(df_range2['dollar_volume'], bins=100, color='green', alpha=0.7)
plt.xlabel('Dollar Volume')
plt.ylabel('Frequency')
plt.title('Histogram of Dollar Volume (Range: 50,000 - 800,000 USD)')
plt.grid(True)

# Save the plot to a file
plt.savefig('charts/Volume_hist_50000_800000.png')

# Show the plots
plt.show()

# Create the directory if it doesn't exist
directory = 'tables'
if not os.path.exists(directory):
    os.makedirs(directory)

# Get the specific statistics for token_amount
token_amount_statistics = df['token_amount'].value_counts().head(20)

# Write to a text file with a custom format for floating-point numbers and including the header
token_amount_statistics.to_csv(os.path.join(directory, 'token_amount_count.txt'), float_format='%.2f', header=['Count'], index_label='Token Amount')

# Create the directory if it doesn't exist
directory = 'tables'
if not os.path.exists(directory):
    os.makedirs(directory)

# Get the specific statistics for token_amount
token_amount_statistics = df['token_amount'].value_counts().head(20)

# Filter and store DataFrames for each token_amount value
for token_amount_value in token_amount_statistics.index:
    filtered_df = df[df['token_amount'] == token_amount_value]
    # Define a filename based on the token_amount value
    filename = f"filtered_df_{token_amount_value}.csv"
    # Write the filtered DataFrame to a CSV file in the 'tables' directory
    filtered_df.to_csv(os.path.join(directory, filename), index=False)

    print(f"Filtered DataFrame for token_amount {token_amount_value} saved to tables/{filename}")


# Plot time series for dollar volume
plt.figure(figsize=(10, 6))
plt.plot(df['datetime'], df['dollar_volume'], color='blue')
plt.title('Time Series for Dollar Volume')
plt.xlabel('Date')
plt.ylabel('Dollar Volume')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# Define the bins for the histogram (60-minute intervals)
bins = pd.date_range(start=df['datetime'].min(), end=df['datetime'].max(), freq='60T')

# Plot the histogram
plt.figure(figsize=(10, 6))
plt.hist(df['datetime'], bins=bins, weights=df['dollar_volume'] / 1000000, color='blue', edgecolor='black')
plt.title('Bucket Histogram of Dollar Volume (60-Minute Intervals)')
plt.xlabel('Date')
plt.ylabel('Dollar Volume ($ millions)')
plt.grid(True)
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('charts/volume_hist.png')

# Filter the DataFrame for February 5th
filtered_df = df[df['date'] == pd.to_datetime('2024-02-05').date()]

# Get the last 4 hours of February 5th
last_4_hours_df = filtered_df[filtered_df['hour'] >= 20]  # Assuming you want the last 4 hours starting from 8 PM (20:00)

# Apply filter for dollar_volume >= 10000
filtered_df = last_4_hours_df[last_4_hours_df['dollar_volume'] >= 1000]

# Group by 'minute' and calculate the sum of dollar volume for each minute
minute_dollar_volume_sum = filtered_df.groupby('minute')['dollar_volume'].count()

# Plot the line graph
plt.figure(figsize=(10, 6))
plt.plot(minute_dollar_volume_sum.index, minute_dollar_volume_sum.values, color='blue')
plt.title('Count of TX by Minute (2024-02-05)')
plt.xlabel('Minute')
plt.ylabel('TX count')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Show the plot
plt.savefig('charts/count_tx_by_min.png')


# Define the bins for the histogram (1-minute intervals)
bins = pd.date_range(start=filtered_df['datetime'].min(), end=filtered_df['datetime'].max(), freq='1T')

# Plot the histogram
plt.figure(figsize=(10, 6))
plt.hist(filtered_df['datetime'], bins=bins, weights=filtered_df['dollar_volume'], color='blue', edgecolor='black')
plt.title('Histogram of Dollar Volume (1-Minute Intervals)')
plt.xlabel('February 05 20:00 - 23:59')
plt.ylabel('Dollar Volume ($)')
plt.grid(True)
plt.xticks(rotation=45)

plt.tight_layout()
# plt.show()
plt.savefig('charts/volume_hist_feb5_last_4hr.png')


# # Filter for token_amount == 500,000 or 700,000
filtered_df = last_4_hours_df[last_4_hours_df['token_amount']>=495000]
print(filtered_df['from'])
