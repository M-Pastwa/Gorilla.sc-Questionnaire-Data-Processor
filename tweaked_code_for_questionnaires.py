# -*- coding: utf-8 -*-
"""
Created on Sat May  7 16:41:00 2025

@author: Maciej Pastwa
"""


import os
import pandas as pd
import string
import re
from itertools import product

# Set prefix and folder path
prefix = 'your_file_prefix'
folder_path = r"your_folder_path"

# Set Page IDs for specific logic
prefix_part_page_id = 'Page_ID'  # For repeated question prefixes, ['ID1', 'ID2'] for multiple Page IDs
key_as_question_page_id = 'Page_ID'  # For using 'Key' as Question name

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

# Convert Local Date and Time to datetime
merged_df['Local Date and Time'] = pd.to_datetime(merged_df['Local Date and Time'], errors='coerce')

# Assign to dynamic variable
globals()[f"{prefix}_merged_df"] = merged_df

print(merged_df['Participant Private ID'].unique())
print(f"Total number of unique Participant Private IDs: {merged_df['Participant Private ID'].nunique()}")

# Save merged dataframe
output_path = os.path.join(folder_path, f"{prefix}_merged_df.csv")
merged_df.to_csv(output_path, index=False)
print(f"All CSVs merged and saved to: {output_path}")

# === Begin Post-Merge Processing ===

# Remove Page ID rows used for prefix handling to avoid duplication
filtered_df = merged_df[~merged_df['Page ID'].str.contains(prefix_part_page_id, na=False)].copy()

# Create base normal_df
normal_df = filtered_df[['Participant Private ID']].drop_duplicates().copy()

# Participant metadata
participant_info = filtered_df.groupby('Participant Private ID').agg({
    'Local Date and Time': ['min', 'max'],
    'Participant Device': 'first',
    'Participant OS': 'first',
    'Participant Browser': 'first',
    'Participant Monitor Size': 'first'
}).reset_index()
participant_info.columns = ['Participant Private ID', 'Start_Time', 'End_Time', 'Participant Device', 'Participant OS', 'Participant Browser', 'Participant Monitor Size']
normal_df = normal_df.merge(participant_info, on='Participant Private ID', how='left')

# Responses for Key == 'value'
value_responses = filtered_df[filtered_df['Key'] == 'value'][['Participant Private ID', 'Question', 'Response']].dropna()
value_responses = value_responses.groupby(['Participant Private ID', 'Question'])['Response'].first().unstack().reset_index()
normal_df = normal_df.merge(value_responses, on='Participant Private ID', how='left')

# === TWEAK 1: Treat 'Key' column as question name in a specific Page ID ===
key_df = merged_df[merged_df['Page ID'].str.contains(key_as_question_page_id, na=False)].copy()
key_df = key_df[['Participant Private ID', 'Key', 'Response']].dropna()
key_df = key_df.groupby(['Participant Private ID', 'Key'])['Response'].first().unstack().reset_index()
normal_df = normal_df.merge(key_df, on='Participant Private ID', how='left')

# === TWEAK 2: Apply fixed position-based prefixes like AA_, AB_, AC_ (no merging) ===
part_df = merged_df[merged_df['Page ID'].str.contains(prefix_part_page_id, na=False)].copy()
letter_codes = ["".join(p) for p in product(string.ascii_uppercase, repeat=2)]

# Get number of questions from the first participant block
first_pid = part_df['Participant Private ID'].iloc[0]
first_questions = part_df[part_df['Participant Private ID'] == first_pid]['Question'].tolist()
question_labels = letter_codes[:len(first_questions)]

# Assign fixed index to each row per participant
part_df['q_index'] = part_df.groupby('Participant Private ID').cumcount()
part_df = part_df[part_df['q_index'] < len(question_labels)].copy()
part_df['Question_Mod'] = part_df['q_index'].map(lambda i: f"{question_labels[i]}")

# Add full label: AA_, AB_, ... + question text
part_df['Question_Mod'] = part_df['Question_Mod'] + '_' + part_df['Question']

# Pivot into wide format
repeat_pivot = part_df.pivot_table(
    index='Participant Private ID',
    columns='Question_Mod',
    values='Response',
    aggfunc='first'
).reset_index()
normal_df = normal_df.merge(repeat_pivot, on='Participant Private ID', how='left')

# === TWEAK 3: Truncate column names ===
normal_df.columns = [col[:54] for col in normal_df.columns]

# Final deduplication
normal_df = normal_df.drop_duplicates(subset=['Participant Private ID'])

# Save final dataframe
normal_output_path = os.path.join(folder_path, f"{prefix}_normal_df.csv")
normal_df.to_csv(normal_output_path, index=False)
print(f"{prefix}_normal_df saved to: {normal_output_path}")

# Display preview
print(normal_df.head())

# === PART THREE: Create colnames_normal_df with cleaned column names and replace commas ===
import unicodedata

def normalize_column(name):
    # Normalize unicode accents (e.g., ę -> e)
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
    # Remove all non-letter characters (punctuation, digits, etc.)
    name = re.sub(r'[^a-zA-Z]', '', name)
    return name

colnames_normal_df = normal_df.copy()
colnames_normal_df.columns = [normalize_column(col) for col in colnames_normal_df.columns]

# Replace all commas in the entire DataFrame with '(coma)'
colnames_normal_df = colnames_normal_df.applymap(
    lambda x: str(x).replace(',', '(coma)') if isinstance(x, str) else x
)

# Save colnames_normal_df
colname_output_path = os.path.join(folder_path, f"{prefix}colnames_normal_df.csv")
colnames_normal_df.to_csv(colname_output_path, index=False)
print(f"colnames_normal_df saved to: {colname_output_path}")




