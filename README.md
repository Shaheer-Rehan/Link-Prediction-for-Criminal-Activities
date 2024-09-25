# Link Prediction for Criminal Activities in the US: Leveraging Demographics, Spatial, and Temporal Data

## Overview
This project leverages social network analysis techniques to predict links between cities based on demographic and crime features. Specifically, it uses Weighted Jaccard Similarity to measure the similarity of crime-related attributes across major cities in the US and visualizes the connections through a network map. The aim is to identify patterns in criminal activities (like homicides) and explore how different cities are related to each other based on demographic factors, crime rates, and geographic proximity.

## Approach
### 1. Data Preprocessing:
Extracting relevant crime-related features such as:
- Quarterly crime counts
- Victim race, sex, and age group
- Nearest cities  

Then, this data is organized for multiple cities to facilitate comparison.

### 2. Weighted Jaccard Similarity:
Jaccard Similarity measures the overlap between two sets (e.g., crime features in two cities). Weighted Jaccard Similarity assigns different weights to crime features to calculate a more comprehensive similarity score. Cities with higher similarity scores are more likely to share common criminal activity patterns.

### 3. Link Prediction:
Based on the similarity scores, cities are connected to each other if their weighted Jaccard similarity exceeds a defined threshold. Cities with strong similarities are connected in a graph representation.

### 4. Visualization:
An interactive map is created using Plotly to display connections between cities. Furthermore, dominant demographics for each city are presented in a table, highlighting the most common victim race, sex, and age group in crimes.

## Code Explanation
### 1. preprocessing.py
This script handles the preprocessing of the dataset and prepares it for similarity calculations. The key functions include:
- Features from raw crime data are extracted and the data is organized into a format suitable for analysis.
- The cities are organized in a dictionary, where each key is a city, and the value is the corresponding crime data for that city.

### 2. model.py
This script performs the core analysis and visualization. Key components include:  

**Jaccard Similarity Functions:**  
- jaccard_similarity(set1, set2) computes the Jaccard similarity between two sets.
- weighted_jaccard_similarity(city1_dict, city2_dict, weight) computes the weighted similarity between two cities based on crime features.

**Network Construction:**  
- create_edges(city_dict, jaccard_threshold) defines the edges between cities whose weighted similarity exceeds the given threshold. The resulting graph shows how cities are connected.

**Visualization:**  
- create_network_map_visualization(graph) creates an interactive USA map with connections between cities based on the crime similarity.
- create_table_for_dominant_demographics() generates a table showing the most frequent crime-related demographic attributes for each city.

## Installation Guide
1. Clone the repository:  
git clone https://github.com/Shaheer-Rehan/Link-Prediction-for-Criminal-Activities.git
cd Link-Prediction-for-Criminal-Activities
2. Install the required packages:
The packages required to be installed are pandas, numpy, networkx, plotly.
3. Download the resources folder (containing the dataset) and the python script files.
