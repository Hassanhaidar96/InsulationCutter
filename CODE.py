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
from matplotlib.ticker import FormatStrFormatter

def adjust_h_for_fire_resistance(Cb, Ct, fire_resistance):
    if fire_resistance == 'REI60':
        return Cb - 1, Ct - 1
    elif fire_resistance == 'REI90':
        return Cb - 1.5, Ct - 1.5
    else:
        return Cb, Ct

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

def get_centers_05m(num_ribs):
    if num_ribs == 2:
        return [114.5, 414.5]
    elif num_ribs == 3:
        return [114.5, 214.5, 414.5]
    elif num_ribs == 4:
        return [114.5, 214.5, 314.5, 414.5]
    elif num_ribs == 5:
        return [64.5, 164.5, 264.5, 364.5, 464.5]
    else:
        return []
    
def get_centers_compact(num_ribs):
    
    if num_ribs == 1:
        return [55]
    if num_ribs == 2:
        return [64.5, 164.5]
    elif num_ribs == 3:
        return [64.5, 164.5, 264.5]
    elif num_ribs == 4:
        return [64.5, 164.5, 264.5, 364.5]
    elif num_ribs == 5:
        return [64.5, 164.5, 264.5, 364.5, 464.5]
    elif num_ribs == 6:
        return [64.5, 164.5, 264.5, 364.5, 464.5 , 564.5]
    elif num_ribs == 7:
        return [64.5 , 164.5 , 264.5 , 364.5 , 464.5 , 564.5 , 664.5]
    elif num_ribs == 8:
        return [64.5 , 164.5 , 264.5 , 364.5 , 464.5 , 564.5 , 664.5, 764.5]
    elif num_ribs == 9:
        return [64.5 , 164.5 , 264.5 , 364.5 , 464.5 , 564.5 , 664.5, 764.5, 864.5]
    elif num_ribs == 10:
        return [64.5 , 164.5 , 264.5 , 364.5 , 464.5 , 564.5 , 664.5, 764.5, 864.5, 964.5]
    else:
        return []


def calculate_rib_centers(element_length_type, num_ribs, element_length_mm):
    if element_length_type == '1m':
        return get_centers_1m(num_ribs)
    if element_length_type == '0.5m':
        return get_centers_05m(num_ribs)
    if element_length_type == 'compact':
        return get_centers_compact(num_ribs)
    else:
        return []

def create_dxf(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height,Cb):
    doc = ezdxf.new(dxfversion='R2010', setup=True)
    doc.units = units.MM
    msp = doc.modelspace()

    # Add big box
    msp.add_lwpolyline([(0, 0), (big_box_length, 0), (big_box_length, big_box_height), (0, big_box_height), (0, 0)], close=True)

    # Add ribs
    # y_center = (big_box_height - small_box_height) / 2
    y_center = (small_box_height/ 2 ) + Cb*10
    for center_x in rib_centers:
        x1 = center_x - small_box_width / 2
        x2 = center_x + small_box_width / 2
        y1 = y_center
        y2 = y_center + small_box_height
        msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)], close=True)

    return doc


# def visualize(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height):
#     fig, ax = plt.subplots()
#     ax.add_patch(Rectangle((0, 0), big_box_length, big_box_height, fill=None, edgecolor='blue'))
#     y_center = (big_box_height - small_box_height) / 2
#     for center_x in rib_centers:
#         x1 = center_x - small_box_width / 2
#         y1 = y_center
#         ax.add_patch(Rectangle((x1, y1), small_box_width, small_box_height, fill=None, edgecolor='red'))
#     plt.xlim(0, big_box_length)
#     plt.ylim(0, big_box_height)
#     plt.gca().set_aspect('equal', adjustable='box')
#     return fig

# More Refined Labelings 

def visualize(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height,Cb):
    fig, ax = plt.subplots()
    
    # Draw the big box (slab)
    ax.add_patch(Rectangle((0, 0), big_box_length, big_box_height, fill=None, edgecolor='blue', linewidth=2))
    
    # Draw small boxes (ribs)
    # y_center = (big_box_height - small_box_height) / 2
    y_center = (small_box_height/ 2 ) + Cb*10
    for center_x in rib_centers:
        x1 = center_x - small_box_width / 2
        y1 = y_center
        ax.add_patch(Rectangle((x1, y1), small_box_width, small_box_height, fill=None, edgecolor='red', linewidth=2))
    
    # Set axis limits and aspect ratio
    plt.xlim(0, big_box_length)
    plt.ylim(0, big_box_height)
    plt.gca().set_aspect('equal', adjustable='box')
    
    # Customize x and y ticks (show start, end, and major divisions)
    xticks = [0] + rib_centers + [big_box_length]
    yticks = [0, big_box_height / 2, big_box_height]
    
    plt.xticks(xticks, rotation=45)  # Rotate x-labels for better readability
    plt.yticks(yticks)
    
    # Force 1 decimal place on all ticks
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))  # X-axis: 1 decimal
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))  # Y-axis: 1 decimal
    
    # Label axes with units (assuming meters)
    ax.set_xlabel("Length (m)", fontsize=12)
    ax.set_ylabel("Height (m)", fontsize=12)
    
    # Highlight the last point on x and y axes
    ax.scatter([big_box_length], [0], color='black', marker='o', s=50, zorder=5)  # Last x-point
    ax.scatter([0], [big_box_height], color='black', marker='o', s=50, zorder=5)   # Last y-point
    
    # Add grid for better reference
    ax.grid(True, linestyle='--', alpha=0.5)
    
    return fig


# Streamlit UI
st.title('DXF Generator for FIRIKA Insulation')

# thickness_slab_cm = st.number_input('Thickness of slab (cm)', min_value=10, max_value=50, value=20)
num_ribs = st.number_input('Number of ribs', min_value=2, max_value=10, value=2)
h_rib = st.selectbox('Height of Ribs (cm)', [11, 13, 15, 17, 19])
Cb = st.number_input('Concrete Cover buttom (cm)' , value=2.5, step=0.5)
Ct = st.number_input('Concrete Cover top (cm)', value=2.5, step=0.5)



element_length_type = st.selectbox('Length of element', ['1m', '0.5m', 'compact'])

# Select insulation material
insulation = st.radio('Insulation material', ['EPS/XPS', 'SW'])

#Fire resistance options
if insulation == 'SW':
    fire_resistance = st.selectbox('Fire resistance', ['REI120'])  # Only REI120 for SW
else:
    fire_resistance = st.selectbox('Fire resistance', ['R0', 'REI60', 'REI90'])  


# Process inputs
Cb, Ct = adjust_h_for_fire_resistance(Cb, Ct, fire_resistance)

element_length_mm = get_element_length(element_length_type, num_ribs)
big_box_length = element_length_mm + 10  # +1 cm
big_box_height = (Cb+Ct+h_rib) * 10 + 20  # +2 cm

small_box_width = 18 if insulation == 'SW' else 17  # width in mm
small_box_height = (h_rib * 10) + 1.5  # 0.15 cm to mm

rib_centers = calculate_rib_centers(element_length_type, num_ribs, element_length_mm)

if st.button('Visualize'):
    if not rib_centers:
        st.warning('Spacing rules not defined for this configuration.')
    else:
        fig = visualize(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height,Cb)
        st.pyplot(fig)

if st.button('Download DXF'):
    if not rib_centers:
        st.error('Cannot generate DXF: undefined spacing for the current inputs.')
    else:
        doc = create_dxf(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height,Cb)
        doc.saveas('slab_element.dxf')
        st.success('DXF file generated. Click below to download.')
        with open('slab_element.dxf', 'rb') as f:
            st.download_button('Download DXF', f, file_name='slab_element.dxf')