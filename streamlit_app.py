# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# App title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit data with SEARCH_ON column
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowflake dataframe to Pandas dataframe
pd_df = my_dataframe.to_pandas()

# Create multiselect dropdown with only fruit names
ingredients_list = st.multiselect('Choose up to 5 ingredients:', pd_df['FRUIT_NAME'].tolist())

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)  # Create a space-separated string
    
    for fruit_chosen in ingredients_list:
        search_on_row = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']
        
        if not search_on_row.empty:  
            search_on = search_on_row.iloc[0]
            
            st.subheader(f"{fruit_chosen} Nutrition Information")
            try:
                response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
                if response.status_code == 200:
                    sf_df = pd.DataFrame(response.json())
                    st.dataframe(sf_df, use_container_width=True)
                else:
                    st.error(f"Error fetching data for {fruit_chosen}: {response.status_code}")
            except Exception as e:
                st.error(f"Failed to retrieve nutrition data: {str(e)}")

# Submit Order Button
time_to_insert = st.button('Submit Order')

if time_to_insert and ingredients_list:  
    my_insert_stmt = f""" 
        INSERT INTO smoothies.public.orders(ingredients) 
        VALUES ('{ingredients_string}') 
    """

    session.sql(my_insert_stmt).collect()
    st.success(f'Your Smoothie is ordered!', icon="✅")
