# -*- coding: utf-8 -*-
"""
Created on Thu May  1 15:49:15 2025

@author: hah
"""

import streamlit as st
import ezdxf
from ezdxf import units
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def adjust_h_for_fire_resistance(thickness_slab_cm, fire_resistance):
    if fire_resistance == 'REI60':
        return thickness_slab_cm - 1*2
    elif fire_resistance == 'REI90':
        return thickness_slab_cm - 1.5*2
    else:
        return thickness_slab_cm

def get_element_length(element_length_type, num_ribs):
    if element_length_type == '1m':
        return 1000  # in mm
    elif element_length_type == '0.5m':
        return 500  # in mm
    elif element_length_type == 'compact':
        return num_ribs * 100  # 10 cm per rib, converted to mm

def get_centers_1m(num_ribs):
    if num_ribs == 2:
        return [114.5, 914.5]
    elif num_ribs == 3:
        return [114.5, 514.5, 914.5]
    elif num_ribs == 4:
        return [114.5, 414.5, 614.5, 914.5]
    elif num_ribs == 5:
        return [114.5, 314.5, 514.5, 714.5, 914.5]
    elif num_ribs == 6:
        return [114.5, 314.5 , 414.5 , 614.5, 714.5, 914.5] 
    elif num_ribs == 7:
        return [114.5 , 214.5 , 414.5 , 514.5 , 614.5, 814.5, 914.5] 
    elif num_ribs == 8:
        return [114.5 , 214.5 , 314.5 , 414.5 , 614.5, 714.5, 814.5, 914.5]     
    elif num_ribs == 9:
        return [114.5 , 214.5 , 314.5 , 414.5 , 514.5 , 614.5, 714.5, 814.5, 914.5]        
    elif num_ribs == 10:
        return [64.5 , 164.5 , 264.5 , 364.5 , 464.5 , 564.5 , 664.5, 764.5, 864.5, 964.5]
    else:
        return []

def calculate_rib_centers(element_length_type, num_ribs, element_length_mm):
    if element_length_type == '1m':
        return get_centers_1m(num_ribs)
    
    ### For compact and Half to be defined
    else:
        return []

def create_dxf(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height):
    doc = ezdxf.new(dxfversion='R2010', setup=True)
    doc.units = units.MM
    msp = doc.modelspace()

    # Add big box
    msp.add_lwpolyline([(0, 0), (big_box_length, 0), (big_box_length, big_box_height), (0, big_box_height), (0, 0)], close=True)

    # Add small ribs
    y_center = (big_box_height - small_box_height) / 2
    for center_x in rib_centers:
        x1 = center_x - small_box_width / 2
        x2 = center_x + small_box_width / 2
        y1 = y_center
        y2 = y_center + small_box_height
        msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)], close=True)

    return doc

def visualize(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height):
    fig, ax = plt.subplots()
    ax.add_patch(Rectangle((0, 0), big_box_length, big_box_height, fill=None, edgecolor='blue'))
    y_center = (big_box_height - small_box_height) / 2
    for center_x in rib_centers:
        x1 = center_x - small_box_width / 2
        y1 = y_center
        ax.add_patch(Rectangle((x1, y1), small_box_width, small_box_height, fill=None, edgecolor='red'))
    plt.xlim(0, big_box_length)
    plt.ylim(0, big_box_height)
    plt.gca().set_aspect('equal', adjustable='box')
    return fig

# Streamlit UI
st.title('DXF Generator for FIRIKA Insulation')

# thickness_slab_cm = st.number_input('Thickness of slab (cm)', min_value=10, max_value=50, value=20)
num_ribs = st.number_input('Number of ribs', min_value=2, max_value=10, value=2)
h_rib = st.selectbox('Height of Ribs (cm)', [11, 13, 15, 17, 19])
Cb = st.number_input('Concrete Cover buttom (cm)' , value=2.5)
Ct = st.number_input('Concrete Cover top (cm)' , value=2.5)

thickness_slab_cm = Cb+Ct+h_rib


element_length_type = st.selectbox('Length of element', ['1m', '0.5m', 'compact'])

# Select insulation material
insulation = st.radio('Insulation material', ['EPS/XPS', 'SW'])

#Fire resistance options
if insulation == 'SW':
    fire_resistance = st.selectbox('Fire resistance', ['REI120'])  # Only REI120 for SW
else:
    fire_resistance = st.selectbox('Fire resistance', ['R0', 'REI60', 'REI90'])  


# Process inputs
adjusted_h = adjust_h_for_fire_resistance(thickness_slab_cm, fire_resistance)
element_length_mm = get_element_length(element_length_type, num_ribs)
big_box_length = element_length_mm + 10  # +1 cm
big_box_height = thickness_slab_cm * 10 + 20  # +2 cm

small_box_width = 18 if insulation == 'SW' else 17  # width in mm
small_box_height_mm = (adjusted_h * 10) + 1.5  # 0.15 cm to mm

rib_centers = calculate_rib_centers(element_length_type, num_ribs, element_length_mm)

if st.button('Visualize'):
    if not rib_centers:
        st.warning('Spacing rules not defined for this configuration.')
    else:
        fig = visualize(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height_mm)
        st.pyplot(fig)

if st.button('Download DXF'):
    if not rib_centers:
        st.error('Cannot generate DXF: undefined spacing for the current inputs.')
    else:
        doc = create_dxf(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height_mm)
        doc.saveas('slab_element.dxf')
        st.success('DXF file generated. Click below to download.')
        with open('slab_element.dxf', 'rb') as f:
            st.download_button('Download DXF', f, file_name='slab_element.dxf')