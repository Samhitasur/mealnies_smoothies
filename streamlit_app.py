import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# App Title
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch Fruit Options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Multi-select for Ingredients
ingredients_list = st.multiselect("Choose up to 5 ingredients:", pd_df["FRUIT_NAME"].tolist())

# Name Input Field
name_on_order = st.text_input("Enter your name for the order:")

# Fetch and Display Nutrition Info
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")
        
        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        st.dataframe(data=response.json(), use_container_width=True)

# Submit Order Button
time_to_insert = st.button("Submit Order")

if time_to_insert and ingredients_list and name_on_order:  
    my_insert_stmt = f""" 
        INSERT INTO smoothies.public.orders(ingredients, name_on_order) 
        VALUES ('{ingredients_string}', '{name_on_order}') 
    """
    session.sql(my_insert_stmt).collect()
    st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
