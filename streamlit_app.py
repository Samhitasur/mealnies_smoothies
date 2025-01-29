# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

from snowflake.snowpark.functions import col

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
)


if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

time_to_insert = st.button('Submit Order')

# Now, the insert is dependent on the button click
if time_to_insert and ingredients_list:  
    my_insert_stmt = """ 
        insert into smoothies.public.orders(ingredients) 
        values ('""" + ingredients_string + """') 
    """

    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")

        
