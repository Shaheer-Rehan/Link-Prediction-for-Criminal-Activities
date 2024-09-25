import pandas as pd
import os
from sklearn.preprocessing import OneHotEncoder
from geopy.geocoders import OpenCage
from math import radians, cos, sin, asin, sqrt


def see_missing_values(column_name, df):
    missing_data_num = df[column_name].isna().sum()
    print('Missing data count for column {}: {}'.format(column_name, missing_data_num))


def data_preprocessing():
    file_path = 'resources/homicide-data.csv'
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        df = pd.read_csv(file_path, skiprows=0)
        print(df.isna().sum())
        df['reported_date'] = pd.to_datetime(df['reported_date'], format='%Y%m%d', errors='coerce')
        see_missing_values('reported_date', df)
        df.dropna(subset=['reported_date'], inplace=True)
        see_missing_values('reported_date', df)
        df['victim_age'] = df['victim_age'].replace('Unknown', 0)
        df['victim_age'] = pd.to_numeric(df['victim_age'])
        mean_age = df[df['victim_age'] != 0]['victim_age'].mean()
        df['victim_age'] = df['victim_age'].replace(0, int(mean_age))
        df['victim_age'] = df['victim_age'].astype('Int64')
        see_missing_values('victim_age', df)
        see_missing_values('lat', df)
        see_missing_values('lon', df)
        df.dropna(subset=['lat'], inplace=True)
        df.dropna(subset=['lon'], inplace=True)
        see_missing_values('lat', df)
        see_missing_values('lon', df)
        see_missing_values('victim_sex', df)
        duplicates = df['uid'].duplicated().any()
        df.drop(columns = ["victim_last", "victim_first"], axis = 1, inplace = True)
        if duplicates:
            print("There are duplicate values in the 'uid' column.")
            df.drop_duplicates(subset=['uid'], keep='first', inplace=True)
            df.reset_index(drop=True, inplace=True)
            print("Duplicate rows based on 'uid' column have been dropped.")
            return df
        else:
            print("All values in the 'uid' column are unique.")
            df.reset_index(drop=True, inplace=True)
            return df

    else:
        print('File does not exist!')


df_clean = data_preprocessing()
print(df_clean.head())



"""Creating bins for victim_age"""
def age_binning(victim_age):
    if victim_age <= 20:
        return "0-20"
    elif victim_age <= 40:
        return "21-40"
    elif victim_age <= 60:
        return "41-60"
    else:
        return "61+"
    
df_clean["victim_age_group"] = df_clean["victim_age"].apply(age_binning)



"""One Hot Encoding for Victim Demographics"""
def demographic_encoder(df, column_name):
    encoder = OneHotEncoder(sparse_output = False)
    encoded_array = encoder.fit_transform(df[[column_name]])
    column_names = encoder.get_feature_names_out([column_name])
    df_encoded = pd.DataFrame(encoded_array, columns = column_names)
    df = pd.concat([df, df_encoded], axis = 1)
    return df

df_clean = demographic_encoder(df_clean, "victim_race")
df_clean = demographic_encoder(df_clean, "victim_sex")
df_clean = demographic_encoder(df_clean, "victim_age_group")
print(df_clean.head())



"""Converting time data into quarter format"""
def quarter_converter(date):
    quarter = (date.month - 1) // 3 + 1
    return quarter

df_clean["reported_quarter"] = df_clean["reported_date"].apply(quarter_converter)
df_clean["year"] = df_clean['reported_date'].dt.year
df_clean.sort_values(by = ["reported_date"], inplace = True)
df_clean.reset_index(drop = True, inplace = True)



"""Creating dictionary of nearest cities for each city"""
def city_coordinates(city_dict, city):     # Function to fetch coordinates for a city. The data is for US cities only
    country = "USA"
    geolocator = OpenCage(api_key = "3f813a0cfd6845a18271d94ce3f1edc8")
    location = geolocator.geocode(city + ", " + country)
    city_dict[city] = {"lat": location.latitude, "lon": location.longitude}

if os.path.exists('city_coordinates.csv'):      # Checking if the CSV file with coordinates already exists. If it exists, loading the coordinates into city_dict
    city_coordinates_df = pd.read_csv('city_coordinates.csv')
    city_dict = city_coordinates_df.set_index('city').T.to_dict('dict')
else:
    city_dict = {}
    for _, row in df_clean.iterrows():      # Creating dictionary of cities
        city = row["city"]
        if city not in city_dict:
            city_dict[city] = {}
            city_coordinates(city_dict, city)
    city_coordinates_df = pd.DataFrame(city_dict).T.reset_index()
    city_coordinates_df.rename(columns = {"index": "city"}, inplace = True)
    city_coordinates_df.to_csv('city_coordinates.csv', index = False)

def haversine(lat1, lon1, lat2, lon2):      # Function to calculate distance between two cities using Haversine formula
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = float(2 * asin(sqrt(a)))
    R = 6371.0   # Radius of Earth in km
    distance = c * R
    return distance

def nearest_cities(city_dict, city, k):     # Function to find k nearest cities for a given city
    distances = []
    for city2 in city_dict.keys():
        if city != city2:
            lat1, lon1 = city_dict[city]["lat"], city_dict[city]["lon"]
            lat2, lon2 = city_dict[city2]["lat"], city_dict[city2]["lon"]
            distance = haversine(lat1, lon1, lat2, lon2)
            distances.append((city2, distance))
    distances.sort(key = lambda x: x[1])    # Sorting the cities based on distance
    nearest_cities = {i+1: city2 for i, (city2, distance) in enumerate(distances[:k])}
    return nearest_cities

for city in city_dict.keys():
    city_dict[city]["nearest_cities"] = nearest_cities(city_dict, city, 5)
    city_dict[city]["quarterly_counts"] = {}

races = ["Asian", "Black", "Hispanic", "White", "Other", "Unknown"]
sex_categories = ["Male", "Female", "Unknown"]
age_groups = ["0-20", "21-40", "41-60", "61+"] 
for _, row in df_clean.iterrows():
    city = row["city"]
    
    if "victim_race" not in city_dict[city]:
        city_dict[city]["victim_race"] = {race: 0 for race in races}
    for race in races:
        city_dict[city]["victim_race"][race] += row[f"victim_race_{race}"]
    
    if "victim_sex" not in city_dict[city]:
        city_dict[city]["victim_sex"] = {sex: 0 for sex in sex_categories}
    for sex in sex_categories:
        city_dict[city]["victim_sex"][sex] += row[f"victim_sex_{sex}"]
    
    if "victim_age_group" not in city_dict[city]:
        city_dict[city]["victim_age_group"] = {age_group: 0 for age_group in age_groups}
    for age_group in age_groups:
        city_dict[city]["victim_age_group"][age_group] += row[f"victim_age_group_{age_group}"]
    
years = range(df_clean["year"].min(), df_clean["year"].max() + 1)    # List of years in the dataset
quarters = range(1, 5)    # List of quarters in a year
for city in city_dict.keys():
    for year in years:
        for quarter in quarters:
            key = f"{year}_Q{quarter}" 
            quarterly_counts = df_clean[(df_clean["city"] == city) & (df_clean["year"] == year) & (df_clean["reported_quarter"] == quarter)]
            count = len(quarterly_counts)
            city_dict[city]["quarterly_counts"][key] = count
