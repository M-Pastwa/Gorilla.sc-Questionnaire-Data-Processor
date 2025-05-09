Universal Code:

Simple code for merging and normalizing Gorilla.sc questionnaire data. 
It assumes that the question is in Question column, and answer in Response column.
At the beginning you must set prefix for created files (eg. study title) and path to folder with your data downloaded from Gorilla.sc and unzipped.
It creates 2 .csv files: 
- merged_df - all data merged with no additional operations
- normal_df - each row is for 1 ParticipantID, each question is moved to separate column,
only Responses where "Key" is "value" are taken (Gorilla duplicates Responses into value and quantised; this prevents the data from cloning each column).

Created CSVs:

separator - coma
text qualificator - none
decimal - dot

Tweaked Code:

For more advanced operations.
All features from original code are kept, additionally at the beginning you can set:
- Page ID for questionnaires in which no questions should be merged (e.g. the questions are the same for different stimuli and you want to keep original order);
it marks the order of questions with AA, AB, AC, AD etc.
- Page ID for questionnaires in which the question is in Key column - some types of questions in Gorilla save questions like that.
Additionally, this code has some tweaks for SPSS data preparation:
- shortens the column names to max 54 charachters
- removes all special signs from the column names, changes regional letters into plain ones from english alphabet
- removes all comas from Responses
This code also saves an additional .csv - colnames_normal_df - with all the tweaks described above added to normal_df