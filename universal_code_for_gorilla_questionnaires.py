# -*- coding: utf-8 -*-
"""
Created on Sat May  3 16:41:00 2025

@author: Maciej Pastwa
"""

import os
import pandas as pd

# Set prefix and folder path
prefix = 'type_your_prefix'
folder_path = r"C:/Users/your_folder_path"

# Initialize an empty list to store DataFrames
all_data = []

# Iterate through all CSV files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(folder_path, file_name)
        temp_df = pd.read_csv(file_path)

        # Rename duplicate columns
        cols = temp_df.columns
        unique_cols = {}
        new_cols = []
        for col in cols:
            if col in unique_cols:
                unique_cols[col] += 1
                new_cols.append(f"{col}_{unique_cols[col]}")
            else:
                unique_cols[col] = 0
                new_cols.append(col)
        temp_df.columns = new_cols

        all_data.append(temp_df)

# Merge all DataFrames
merged_df = pd.concat(all_data, ignore_index=True)

# Convert Local Date and Time to datetime (fix for aggregation error)
merged_df['Local Date and Time'] = pd.to_datetime(merged_df['Local Date and Time'], errors='coerce')

# Assign to dynamic variable
globals()[f"{prefix}_merged_df"] = merged_df

print(merged_df['Participant Private ID'].unique())
print(f"Total number of unique Participant Private IDs: {merged_df['Participant Private ID'].nunique()}")

# Save merged dataframe
output_path = os.path.join(folder_path, f"{prefix}_merged_df.csv")
merged_df.to_csv(output_path, index=False)
print(f"All CSVs merged and saved to: {output_path}")

# Create normal_df
normal_df = merged_df[['Participant Private ID']].copy()

# Extract participant metadata
participant_info = merged_df.groupby('Participant Private ID').agg({
    'Local Date and Time': ['min', 'max'],
    'Participant Device': 'first',
    'Participant OS': 'first',
    'Participant Browser': 'first',
    'Participant Monitor Size': 'first'
}).reset_index()
participant_info.columns = ['Participant Private ID', 'Start_Time', 'End_Time', 'Participant Device', 'Participant OS', 'Participant Browser', 'Participant Monitor Size']
normal_df = normal_df.merge(participant_info, on='Participant Private ID', how='left')

# Add responses for all questions
selected_responses = merged_df[['Participant Private ID', 'Question', 'Response']].dropna()
selected_responses = selected_responses.groupby(['Participant Private ID', 'Question'])['Response'].first().unstack().reset_index()
normal_df = normal_df.merge(selected_responses, on='Participant Private ID', how='left')

# Add filtered responses (Key == 'value')
filtered_responses = merged_df[merged_df['Key'] == 'value'][['Participant Private ID', 'Question', 'Response']].dropna()
filtered_responses = filtered_responses.groupby(['Participant Private ID', 'Question'])['Response'].first().unstack().reset_index()
normal_df = normal_df.merge(filtered_responses, on='Participant Private ID', how='left')

# Drop duplicate participants
normal_df = normal_df.drop_duplicates(subset=['Participant Private ID'])

# Save final dataframe
normal_output_path = os.path.join(folder_path, f"{prefix}_normal_df.csv")
normal_df.to_csv(normal_output_path, index=False)
print(f"{prefix}_normal_df saved to: {normal_output_path}")

# Display
print(normal_df.head())
