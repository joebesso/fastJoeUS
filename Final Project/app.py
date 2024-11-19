"""
Name: Joseph Besso
CS230: Section 5
Data: U.S. Fast Food Locations dataset

Description:
This Streamlit app visualizes fast food restaurant data with filters by province and city. It has maps,
bar charts, and pie charts for detailed analysis.
"""

# Import necessary libraries
import streamlit as st  # For building interactive web apps
import pandas as pd  # For data manipulation and analysis
import plotly.express as px  # For creating interactive plots
import plotly.graph_objs as go  # For creating graphs (used by plotly)

# Function to load and clean the data
import pandas as pd


def load_and_clean_data(filepath):
    try:
        # Define parameters in a dictionary for reusability and clarity
        settings = {
            "duplicate_subset": "id",  # Column to check for duplicates
            "duplicate_keep": "last",  # Which duplicate to keep
            "columns_to_clean": ["categories"]  # Columns to clean
        }

        # Load data from CSV file into a DataFrame
        df = pd.read_csv(filepath)

        # Drop duplicate rows based on the settings in the dictionary
        df = df.drop_duplicates(subset=[settings["duplicate_subset"]], keep=settings["duplicate_keep"])

        # Clean specified columns: remove leading/trailing spaces and convert to lowercase
        for column in settings["columns_to_clean"]:
            if column in df.columns:
                df[column] = df[column].apply(lambda x: x.strip().lower() if isinstance(x, str) else x)

        return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


    # Handle different exceptions (errors)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")  # File not found error
    except pd.errors.EmptyDataError:
        print("Error: No data found in the file.")  # Empty file error
    except KeyError:
        print("Error: The 'categories' column is missing in the data.")  # Missing column error
    except Exception as e:
        print(f"An unexpected error occurred: {e}")  # Catch other unforeseen errors


# Set up the page for the Streamlit app
st.set_page_config(page_title="Fast Food Location Dashboard", layout="wide")  # Set the title and layout of the page
df = load_and_clean_data('data.csv')  # Load and clean data from a CSV file
st.sidebar.title("Filters")  # Set title for the sidebar

# Set the main title of the web app
st.title("Fast Food Locations Data Visualization")

# Add an image to the sidebar
st.sidebar.image('ff.jpg', caption='Fast Food Locations', use_column_width=True)

# Dropdown menu for selecting a province from the 'province' column in the data
selected_province = st.sidebar.selectbox("Select Province", options=["All"] + df['province'].unique().tolist())


# Function to filter data by the selected province
def filter_data_by_province(province="All"):
    """Filter data by province, default is LA province"""
    if province == "LA":
        return df  # Return all data if 'LA' is selected
    return df[df['province'] == province]  # Filter by the selected province


# Apply the province filter
filtered_df = filter_data_by_province(selected_province)

# Filter available cities based on the selected province
if selected_province == "All":
    available_cities = [city for city in
                        df['city'].unique()]  # Get all cities if 'All' is selected using list comprehension

else:
    available_cities = df[df['province'] == selected_province][
        'city'].unique().tolist()  # Get cities from the selected province

# Dropdown menu for selecting a city based on the selected province
selected_city = st.sidebar.selectbox("Select City", options=["All"] + available_cities)


# Function to filter data by city and province
def filter_data_by_city_province(df, city, province):
    """Filter the DataFrame by selected city and province."""
    if city == "All":
        return df[df['province'] == province]  # Return all cities in the province
    return df[(df['city'].str.lower() == city.lower()) & (
                df['province'].str.lower() == province.lower())]  # Filter by both city and province


# Apply the city and province filter
filtered_city_province_df = filter_data_by_city_province(filtered_df, selected_city, selected_province)

# Display filtered data (based on province and city) in a table
st.title("Fast Food Restaurant Data")

if not filtered_city_province_df.empty:  # Check if the filtered DataFrame is not empty
    st.subheader(
        f"Details for Fast Food Restaurants in {selected_city}, {selected_province}")  # Show subheader for details
    st.write(filtered_city_province_df[
                 ['name', 'address', 'categories', 'city', 'postalCode', 'province']])  # Display relevant columns
else:
    st.write(f"No fast food restaurants found in {selected_city}, {selected_province}.")  # Message when no data found

# Count the number of fast-food locations per province
province_counts = filtered_city_province_df['province'].value_counts().reset_index()
province_counts.columns = ['province', 'count']  # Rename columns for better clarity

# Join the counts back to the filtered DataFrame to use with Plotly map
map_data = pd.merge(filtered_city_province_df, province_counts, on='province', how='left')

# Plotting the map for selected province and city
if 'latitude' in map_data.columns and 'longitude' in map_data.columns:  # Check if latitude and longitude exist
    # Plot a map with locations and counts
    fig_map = px.scatter_mapbox(
        map_data,
        lat="latitude",
        lon="longitude",
        color="count",  # Density indicated by count color
        size="count",  # Size of markers based on count
        hover_name="name",  # Information displayed on hover
        hover_data={"address": True, "city": True, "province": True, "count": True},  # More hover data
        zoom=10,  # Zoom level for the map
        height=600,  # Height of the map
        title=f"Density Map of Fast-Food Locations in {selected_city}, {selected_province}"  # Map title
    )
    fig_map.update_layout(mapbox_style="open-street-map")  # Set map style
    st.plotly_chart(fig_map)  # Display map using Plotly
else:
    st.write("The dataset must contain latitude and longitude for each restaurant.")  # Message when data is missing

# Multi-select for categories
categories_selected = st.sidebar.multiselect("Select Categories", options=df['categories'].unique().tolist())


# Function to filter data by selected categories
def get_category_data(categories_selected, selected_province):
    """Filter data by selected categories and province."""
    if not categories_selected:
        category_filtered = df  # Return all data if no specific category is selected
    else:
        category_filtered = df[df['categories'].isin(categories_selected)]  # Filter data by selected categories

    # Further filter data by province
    return category_filtered[category_filtered['province'] == selected_province]


# Apply filters for categories and province
filtered_data = get_category_data(categories_selected, selected_province)
category_counts = filtered_data.groupby(['province', 'categories']).size().reset_index(name='count')

# Plot bar chart for selected province and categories
fig_bar = px.bar(
    category_counts,
    x="province",
    y="count",
    color="categories",
    title=f"Fast-Food Category Frequency by Province: {selected_province}",
    labels={"count": "Number of Locations", "province": "Province"}
)
fig_bar.update_layout(barmode='stack')  # Stack bars in the chart
st.plotly_chart(fig_bar)  # Display the bar chart


# Function to get pie chart data based on selected categories
def get_pie_chart_data(categories_selected):
    """Get data for pie chart based on selected categories."""
    if not categories_selected:
        return df  # Return all data if no categories are selected
    return df[df['categories'].isin(categories_selected)]  # Filter data by categories


# Prepare data for pie chart
pie_data = get_pie_chart_data(categories_selected)
type_counts = pie_data['categories'].value_counts()

# Plot pie chart for fast-food category distribution across the U.S.
fig_pie = px.pie(
    values=type_counts.values,
    names=type_counts.index,
    title="Distribution of Fast-Food Types Across the U.S."
)
st.plotly_chart(fig_pie)  # Display the pie chart


# Function to get top 10 restaurants by city
def get_top_restaurants_by_city(df, city):
    """Get the top 10 restaurant names based on the count of restaurants in the selected city."""
    city_data = df[df['city'].str.lower() == city.lower()]  # Filter data by selected city
    restaurant_counts = city_data['name'].value_counts().head(10)  # Count top 10 restaurants
    return restaurant_counts


# Function to get top 10 most common restaurants
def get_top_10_restaurants(df):
    """Get the top 10 most common restaurant names in the given province."""
    restaurant_counts = df.groupby(['name']).size().reset_index(name='count')  # Count occurrences of each restaurant
    restaurant_counts = restaurant_counts.sort_values(by=['count'], ascending=False)  # Sort by count
    top_10_restaurants = restaurant_counts.head(10)  # Select top 10
    return top_10_restaurants


# Function to get data for the top 10 restaurants
def get_restaurants_by_top_10(df, top_10_restaurants):
    """Get data for the top 10 most common restaurants."""
    top_10_data = df[df['name'].isin(top_10_restaurants['name'])]  # Filter data for top 10 restaurants
    return top_10_data


# Streamlit interface for user input
st.title("Top 10 Most Common Restaurants on Map")

# Filter the dataframe by the selected province
if selected_province == "All":
    filtered_df = df
else:
    filtered_df = df[df['province'] == selected_province]  # Filter data by selected province

# Display the province name
st.sidebar.write(f"Showing data for {selected_province}")

# Get the top 10 most common restaurants in the selected province
top_10_restaurants_data = get_top_10_restaurants(filtered_df)

# Display the table of top 10 most common restaurants
st.subheader(f"Top 10 Most Common Restaurants in {selected_province}")
st.write(top_10_restaurants_data)

# Get data for the top 10 restaurants
top_10_data = get_restaurants_by_top_10(filtered_df, top_10_restaurants_data)

# Plot the top 10 restaurants on a map using Plotly
if 'latitude' in top_10_data.columns and 'longitude' in top_10_data.columns:  # Check if latitude and longitude exist
    fig_map = px.scatter_mapbox(
        top_10_data,
        lat='latitude',
        lon='longitude',
        color='name',  # Color by restaurant name
        hover_name='name',
        hover_data=['city', 'address', 'postalCode'],
        size_max=15,  # Maximum size for markers
        title=f"Top 10 Most Common Restaurants in {selected_province}",
        zoom=10,  # Zoom level for the map
    )
    fig_map.update_layout(mapbox_style="open-street-map")  # Set map style
    st.plotly_chart(fig_map)  # Display the map
else:
    st.write("The dataset must contain latitude and longitude for each restaurant.")  # Error message for missing data

# Set the sidebar title
st.sidebar.title("Fast-Food Accessibility Dashboard")

# Add additional information in the sidebar
st.sidebar.markdown("Explore fast-food locations by state, popular food types, and more!")
