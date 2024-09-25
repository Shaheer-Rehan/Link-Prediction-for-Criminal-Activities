import networkx as nx
import plotly.graph_objects as go
from preprocessing import *



"""Function for calculating Jaccard Similarity"""
def jaccard_similarity(set1, set2):     # this function takes two sets as input and returns the Jaccard similarity between them
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0



"""Function for weighted Jaccard Similarity"""
features = ["quarterly_counts", "victim_race", "victim_sex", "victim_age_group", "nearest_cities"]   # list of features being considered
weight_values = [1/(len(features)) for _ in range(len(features))]      # list of weights for each feature
def weighted_jaccard_similarity(city1_dict, city2_dict, weight):   # this function takes two dictionaries as input and returns the 
                                                                   # weighted Jaccard similarity between them
    total_similarity = 0
    for feature, weight in zip(features, weight):
        set1 = set(city1_dict[feature].items())
        set2 = set(city2_dict[feature].items())
        similarity = jaccard_similarity(set1, set2)
        total_similarity += weight * similarity 
    return total_similarity
    


"""Defining edges between cities based on weighted Jaccard Similarity"""
def create_edges(city_dict, jaccard_threshold):     # this function takes a dictionary of cities as input and 
                                                    # returns a dictionary of similarity scores and a dictionary of edges between cities
    edges = {}
    similarity_scores = {}
    for city1, city1_data in city_dict.items():
        edges[city1] = []
        similarity_scores[city1] = {}
        for city2, city2_data in city_dict.items():
            if city1 != city2:
                similarity = weighted_jaccard_similarity(city1_data, city2_data, weight = weight_values)
                similarity_scores[city1][city2] = similarity
                if similarity >= jaccard_threshold:
                    edges[city1].append(city2)
    return similarity_scores, edges

similarity_dict, graph = create_edges(city_dict, jaccard_threshold = 0.1)
# print(graph)



def getCitiesCordinates():
    return {
        'Albuquerque': (35.0844, -106.6504),
        'Atlanta': (33.7490, -84.3880),
        'Baltimore': (39.2904, -76.6122),
        'Baton Rouge': (30.4515, -91.1871),
        'Birmingham': (33.5207, -86.8025),
        'Boston': (42.3601, -71.0589),
        'Buffalo': (42.8802, -78.8787),
        'Charlotte': (35.2271, -80.8431),
        'Chicago': (41.8781, -87.6298),
        'Cincinnati': (39.1031, -84.5120),
        'Columbus': (39.9612, -82.9988),
        'Dallas': (32.7767, -96.7970),
        'Denver': (39.7392, -104.9903),
        'Detroit': (42.3314, -83.0458),
        'Durham': (35.9940, -78.8986),
        'Fort Worth': (32.2555, -97.3308),
        'Fresno': (36.7372, -119.7871),
        'Houston': (29.7604, -95.3698),
        'Indianapolis': (39.7684, -86.1581),
        'Jacksonville': (30.3322, -81.6557),
        'Kansas City': (39.0997, -94.5786),
        'Las Vegas': (36.1699, -115.1398),
        'Long Beach': (33.7701, -118.1937),
        'Los Angeles': (34.3522, -118.2437),
        'Louisville': (38.2527, -85.7585),
        'Memphis': (35.1495, -90.0490),
        'Miami': (25.7617, -80.1918),
        'Milwaukee': (43.0389, -87.9065),
        'Minneapolis': (44.9778, -93.2650),
        'Nashville': (36.1627, -86.7816),
        'New Orleans': (29.9511, -90.0715),
        'New York': (40.7128, -74.0060),
        'Oakland': (39.8044, -122.2711),
        'Oklahoma City': (35.4676, -97.5164),
        'Omaha': (41.2565, -95.9345),
        'Philadelphia': (39.9526, -75.1652),
        'Phoenix': (33.4484, -112.0740),
        'Pittsburgh': (40.4406, -79.9959),
        'Richmond': (37.5407, -77.4360),
        'San Antonio': (29.4241, -98.4936),
        'Sacramento': (38.5816, -121.4944),
        'Savannah': (32.0809, -81.0912),
        'San Bernardino': (34.9183, -117.1098),
        'San Diego': (32.7157, -117.1611),
        'San Francisco': (37.7749, -122.4194),
        'St. Louis': (38.6270, -90.1994),
        'Stockton': (38.9577, -121.2908),
        'Tampa': (27.9506, -82.4572),
        'Tulsa': (36.1540, -95.9928),
        'Washington': (38.9072, -77.0369)
    }

def create_network_map_visualization(graph):
    city_coordinates = getCitiesCordinates()
    df = pd.DataFrame.from_dict(city_coordinates, orient='index', columns=['lat', 'lon'])
    df.reset_index(inplace=True)
    df.columns = ['name', 'lat', 'lon']
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lon=df['lon'],
        lat=df['lat'],
        text=df['name'],
        mode='markers',
        marker=dict(
            size=10,  # Adjust size with age
            color='orange', symbol='circle',
            opacity=1
        )
    ))
    fig.add_trace(go.Scattergeo(
        lon=df['lon'],
        lat=df['lat'],
        text=df['name'],
        mode='text',
        textposition="top center",
        textfont=dict(color="black"),
    ))

    for city, connections in graph.items():
        city_coords = df[df['name'] == city][['lon', 'lat']].values.tolist()
        if connections:
            for connected_city in connections:
                connected_coords = df[df['name'] == connected_city][['lon', 'lat']].values.tolist()
                fig.add_trace(go.Scattergeo(
                    lon=[city_coords[0][0], connected_coords[0][0]],
                    lat=[city_coords[0][1], connected_coords[0][1]],
                    mode='lines',
                    line=dict(
                        width=3,
                        color='red'
                    ),
                    opacity=1
                ))


    fig.update_layout(
        geo=dict(
            scope='usa',
            showland=True,
            landcolor='rgb(245, 245, 245)',
            showcountries=True,
            showocean=True,
            oceancolor="rgb(204, 229, 255)",
        ),
        title="Crime Link Prediction for USA Cities"

    )
    fig.show()

def create_table_for_dominant_demographics():
    table_data = []
    # Iterate over each city in city_dict
    for city, data in city_dict.items():

        # Find the attribute with maximum value for quarterly counts
        max_quarterly_count = max(data['quarterly_counts'], key=data['quarterly_counts'].get)
        table_data.append({'City':city,'Attribute': max_quarterly_count, 'Count': data['quarterly_counts'][max_quarterly_count]})

        # Find the attribute with maximum value for victim race
        max_victim_race = max(data['victim_race'], key=data['victim_race'].get)
        table_data.append(
            {'City':city,'Attribute': f'Victim Race ({max_victim_race})', 'Count': data['victim_race'][max_victim_race]})

        # Find the attribute with maximum value for victim sex
        max_victim_sex = max(data['victim_sex'], key=data['victim_sex'].get)
        table_data.append({'City':city,'Attribute': f'Victim Sex ({max_victim_sex})', 'Count': data['victim_sex'][max_victim_sex]})

        # Find the attribute with maximum value for victim age group
        max_victim_age_group = max(data['victim_age_group'], key=data['victim_age_group'].get)
        table_data.append({'City':city,'Attribute': f'Victim Age Group ({max_victim_age_group})',
                           'Count': data['victim_age_group'][max_victim_age_group]})

    # Create the table figure
    fig = go.Figure(data=[go.Table(
        header=dict(values=['City','Attribute', 'Count']),
        cells=dict(values=[[row['City'] for row in table_data],[row['Attribute'] for row in table_data],
                           [row['Count'] for row in table_data]])
    )])

    # Update layout
    fig.update_layout(
        title=f"Dominant Demographics in Each USA City",
    )

    # Show the table
    fig.show()

create_table_for_dominant_demographics()
create_network_map_visualization(graph)
