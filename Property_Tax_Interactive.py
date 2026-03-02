## Hello! Going to try to use the seattel property tax data that I so love to use to create a web map.
## I will use Folium and Streamlit. Going to start out trying to do something like this -> https://www.youtube.com/watch?v=uXj76K9Lnqc
## GOod luck to me!
## data here --> https://gis-kingcounty.opendata.arcgis.com/datasets/kingcounty::parcels-for-king-county-with-address-with-property-information-parcel-address-area/about
## to run, from the correct folder --> py -m streamlit run Property_Tax_Interactive.py

import streamlit as st
import pandas as pd
import pydeck

my_blog_post_url = "https://amschechter.github.io/jekyll/update/2026/02/16/Land_Value_Tax.html"

APP_TITLE = 'Property Tax in Seattle'
APP_SUB_TITLE = 'Data Source: King County Assessor'
APP_INTRO_TEXT = "Use the panel on the left to change the map display. The Select All/One button at the top 'enables' the parcel type dropdown.  \n The color and height of each Hexagon seen in the map denotes the same variable which is the summed improved/land/combined (whichever you selected) value in that hexagon."

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    st.write("This webpage is made as an addendum to my [blog post here](%s)" % my_blog_post_url, ", and to show differences between the two aspects of property tax calculation: Improved value and Land Value.")
    st.write(APP_INTRO_TEXT)
    
    ## LOAD DATA
    #data_frame = pd.read_csv("C:/Users/aaron/Fun Mapping Work/Steamlit_plus_Folium/Data/Parcels_for_King_County_with_Address_with_Property_Information___parcel_address_area_Seattle_Only.csv")
    #data_frame = pd.read_csv("C:/Users/aaron/Fun Mapping Work/Steamlit_plus_Folium/Data/Parcels_for_King_County_with_Address_with_Property_Information_Trimmed_Columns_SEA_ONLY.csv")
    data_frame = pd.read_csv("Data/Parcels_for_King_County_with_Address_with_Property_Information_Trimmed_Columns_SEA_ONLY.csv")

    data_frame['PREUSE_DESC'] = data_frame['PREUSE_DESC'].str.rstrip() ##takes the whitespace off the end of the column
    data_frame['COMBINED_APPR_VAL'] = data_frame['APPRLNDVAL'] + data_frame['APPR_IMPR'] ## add combined tax column

    ## Make the sidebar and filters!
    value_type_list = ['Land Value', 'Improved Value', 'Combined Imprvd & Land Value']
    parcel_type_list = list(data_frame['PREUSE_DESC'].unique())

    with st.sidebar.form(key='variable_form'):
        st.header('Visualization Settings')

        selection_mode = st.radio("Select All Parcel Types?", ["Select All", "Select Just One"])

        parcel_type = st.selectbox('Parcel Type', parcel_type_list)   
        value_type = st.selectbox('Assessed Value Type', value_type_list)
        hexagon_size = st.slider(label='Size of Hexagon (Radius in Meters)', min_value=150, max_value=700, value=300)   

        submit_button = st.form_submit_button(label='recalculate map')
    
    filtered_df = load_data(data_frame, parcel_type, selection_mode)

    display_map(filtered_df, value_type, hexagon_size)

    parcel_type_label = 'All properties'
    if(selection_mode == 'Select Just One'):
        parcel_type_label = parcel_type

    st.subheader(f"{value_type} Information about {parcel_type_label} parcels")

    filtered_count = len(filtered_df)
    total_land_val = filtered_df['APPRLNDVAL'].sum()
    total_improved_val = filtered_df['APPR_IMPR'].sum()
    imp_to_land_ratio = total_improved_val / total_land_val

    

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label = f'{parcel_type_label} Count', value = f"{filtered_count:,}")
    with col2:
        st.metric(label = f'{parcel_type_label} Improved Val to Land Val Ratio', value = round(imp_to_land_ratio, 3))
    
    col3, col4 = st.columns(2)
    with col3:
        st.metric(label = f'{parcel_type_label} total land value', value = f"{total_land_val:,}")
    with col4:
        st.metric(label = f'{parcel_type_label} total improved value', value = f"{total_improved_val:,}")

    
    ##write some closing thoughts 


    ## DISPLAY FILTERS AND MAP

def display_map(df, Value_Type, hex_size):
    if(Value_Type == 'Land Value'):
        color_and_height_col = 'APPRLNDVAL'
    elif(Value_Type == 'Improved Value'):
        color_and_height_col = 'APPR_IMPR'
    elif(Value_Type == 'Combined Imprvd & Land Value'):
        color_and_height_col = 'COMBINED_APPR_VAL'

    pydeck_layer = pydeck.Layer(
        "HexagonLayer",
        data=df,
        get_position="[LON, LAT]",
        get_elevation_weight = color_and_height_col,
        get_color_weight = color_and_height_col,
        radius=hex_size,
        auto_highlight=True,
        elevation_scale=4,
        elevation_range=[0, 1000],
        pickable=True,
        extruded=True,
        opacity=0.6
    )
    #pydeck_map = st.pydeck_chart(
    st.pydeck_chart(
        pydeck.Deck(
            map_style=None,  # Use Streamlit theme to pick map style
            initial_view_state=pydeck.ViewState(
            latitude=47.59,
            longitude=-122.35,
            zoom=10.5,
            pitch=35),
            tooltip={
                "html": "<b>Summed Value:</b> ${colorValue}",
                "style": {"color": "white"}
            },
            layers=[
                pydeck_layer                
            ],
        )
    )

    st.markdown('*This is an interactive map. Click and drag to move about, use your mousewheel to zoom in/out, cntrl+drag to pan.*')
    #pydeck_map
    #st.write(pydeck_chart)



    #map = folium.Map(location=[47.55, -122.2], zoom_start=10, )
    #st_map = st_folium(map, width=700, height=450)
    ## DISPLAY METRICS

def load_data(incoming_df, Land_use_type, radio_button_value):
    
    if(radio_button_value == 'Select Just One'):
        mask = (incoming_df['PREUSE_DESC'] == Land_use_type)
        data_frame_trimmed = incoming_df[mask]
        return data_frame_trimmed
        
    #st.write('radio val -', radio_button_value)
    #data_frame_trimmed = incoming_df[mask]

    return incoming_df



if __name__ == "__main__":
    main()