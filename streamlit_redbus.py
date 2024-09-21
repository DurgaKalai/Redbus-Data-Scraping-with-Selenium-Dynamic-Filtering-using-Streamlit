import streamlit as st
import pymysql
import pandas as pd

# Connect to MySQL database
def get_connection():
    return pymysql.connect(host='127.0.0.1', user='root', passwd='Ria@3009', database='red_bus_details')

# Function to fetch route names starting with a specific letter, arranged alphabetically
def fetch_route_names(connection, starting_letter):
    query = f"SELECT DISTINCT Route_Name FROM bus_routes WHERE Route_Name LIKE '{starting_letter}%' ORDER BY Route_Name"
    route_names = pd.read_sql(query, connection)['Route_Name'].tolist()
    return route_names

# Function to fetch data from MySQL based on selected Route_Name and price sort order
def fetch_data(connection, route_name, price_sort_order):
    price_sort_order_sql = "ASC" if price_sort_order == "Low to High" else "DESC"
    query = f"SELECT * FROM bus_routes WHERE Route_Name = %s ORDER BY Star_Rating DESC, Price {price_sort_order_sql}"
    df = pd.read_sql(query, connection, params=(route_name,))
    return df

# Function to filter data based on Star_Rating and Bus_Type
def filter_data(df, star_ratings, bus_types):
    filtered_df = df[df['Star_Rating'].isin(star_ratings) & df['Bus_Type'].isin(bus_types)]
    return filtered_df

# Main Streamlit app
def main():
    st.set_page_config(page_title="Bus Ticket Booking", page_icon="🚌", layout="wide")
    
    # Apply a custom CSS style for vibrant colors
    st.markdown("""
        <style>
            .reportview-container {
                background: #e0f7fa; /* Light cyan background */
            }
            .sidebar .sidebar-content {
                background: #ffab40; /* Bright orange sidebar */
            }
            h1 {
                color: #d32f2f; /* Dark red for the main heading */
                font-size: 2.5em;
                text-align: center;
                font-family: 'Arial', sans-serif;
            }
            h2 {
                color: #f57c00; /* Orange for subheadings */
                font-family: 'Arial', sans-serif;
            }
            h3 {
                color: #1976d2; /* Bright blue for smaller headings */
            }
            .stButton>button {
                background-color: #388e3c; /* Dark green button */
                color: white;
                font-weight: bold;
            }
            .stDataFrame {
                border: 1px solid #ddd; /* Optional: border for dataframes */
                border-radius: 5px;
            }
            .stSelectbox, .stMultiselect, .stSlider {
                border-radius: 5px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.header('🚌 Easy and Secure Online Bus Tickets Booking')

    connection = get_connection()

    try:
        # Sidebar - Input for starting letter
        starting_letter = st.sidebar.text_input('Enter starting letter of Route Name', 'A')

        # Fetch route names starting with the specified letter
        if starting_letter:
            route_names = fetch_route_names(connection, starting_letter.upper())

            if route_names:
                # Sidebar - Selectbox for Route_Name
                selected_route = st.sidebar.radio('Select Route Name', route_names)

                if selected_route:
                    # Sidebar - Selectbox for sorting preference
                    price_sort_order = st.sidebar.selectbox('Sort by Price', ['Low to High', 'High to Low'])

                    # Fetch data based on selected Route_Name and price sort order
                    data = fetch_data(connection, selected_route, price_sort_order)

                    if not data.empty:
                        # Display data table with a subheader
                        st.write(f"### Data for Route: {selected_route}")
                        st.dataframe(data.style.highlight_max(axis=0), use_container_width=True)

                        # Filter by Star_Rating and Bus_Type
                        star_ratings = data['Star_Rating'].unique().tolist()
                        selected_ratings = st.multiselect('Filter by Star Rating', star_ratings)

                        bus_types = data['Bus_Type'].unique().tolist()
                        selected_bus_types = st.multiselect('Filter by Bus Type', bus_types)

                        # Additional filter for Price range
                        min_price, max_price = st.slider('Filter by Price', float(data['Price'].min()), float(data['Price'].max()), (float(data['Price'].min()), float(data['Price'].max())))

                        if selected_ratings and selected_bus_types:
                            filtered_data = filter_data(data, selected_ratings, selected_bus_types)
                            filtered_data = filtered_data[(filtered_data['Price'] >= min_price) & (filtered_data['Price'] <= max_price)]
                            
                            # Display filtered data table with a subheader
                            st.write(f"### Filtered Data for Star Rating: {selected_ratings} and Bus Type: {selected_bus_types} within Price: {min_price} - {max_price}")
                            st.dataframe(filtered_data.style.highlight_max(axis=0), use_container_width=True)
                        elif selected_ratings or selected_bus_types:
                            filtered_data = filter_data(data, selected_ratings if selected_ratings else star_ratings, selected_bus_types if selected_bus_types else bus_types)
                            filtered_data = filtered_data[(filtered_data['Price'] >= min_price) & (filtered_data['Price'] <= max_price)]
                            
                            st.write(f"### Filtered Data for Price: {min_price} - {max_price}")
                            st.dataframe(filtered_data.style.highlight_max(axis=0), use_container_width=True)
                    else:
                        st.write(f"No data found for Route: {selected_route} with the specified price sort order.")
            else:
                st.write("No routes found starting with the specified letter.")
    finally:
        connection.close()

if __name__ == '__main__':
    main()
