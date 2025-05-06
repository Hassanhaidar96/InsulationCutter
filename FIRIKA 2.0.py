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

def get_element_length(element_length_type, num_ribs,Length):
    if element_length_type == '1m':
        return 1000  # in mm
    elif element_length_type == '0.5m':
        return 500  # in mm
    elif element_length_type == 'compact':
        return num_ribs * 100  # 10 cm per rib, converted to mm
    elif element_length_type == 'Lenght':
        return Length  # 10 cm per rib, converted to mm    

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


def get_centers_Length(num_ribs, Length):
    if num_ribs < 1:
        return []

    first_center = 64.5  # Fixed starting position

    # Handle single rib case
    if num_ribs == 1:
        min_length = first_center + 35  # 64.5 + 35 = 99.5mm
        return [first_center] if Length >= min_length else []

    last_center_max = Length - 35.5  # Maximum allowed last rib center position

    # Try spacings that are multiples of 100
    best_centers = []
    for spacing in range(100, 10000, 100):  
        total_span = spacing * (num_ribs - 1)
        last_center = first_center + total_span

        if last_center <= last_center_max:
            # This spacing is valid
            centers = [first_center + i * spacing for i in range(num_ribs)]
            best_centers = centers  # Update the best so far
        else:
            break  # No need to try larger spacings

    return best_centers


def calculate_rib_centers(element_length_type, num_ribs, element_length_mm):
    if element_length_type == '1m':
        return get_centers_1m(num_ribs)
    if element_length_type == '0.5m':
        return get_centers_05m(num_ribs)
    if element_length_type == 'compact':
        return get_centers_compact(num_ribs)
    if element_length_type == 'Lenght':
        return get_centers_Length(num_ribs,element_length_mm) ##
    else:
        return []

 
def create_dxf(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height, Cb):
    doc = ezdxf.new(dxfversion='R2010', setup=True)
    doc.units = units.MM
    msp = doc.modelspace()

    # Add big box (slab)
    msp.add_lwpolyline(
        [(0, 0), (big_box_length, 0), (big_box_length, big_box_height), (0, big_box_height), (0, 0)],
        close=True
    )

    # Calculate rib positions
    y_initial = (Cb * 10) + 10 - 0.75  # Base Y position
    y_center = y_initial + (small_box_height / 2)  # Vertical center of ribs
    rib_edges = []  # Store (left, right) edges of all ribs
    
    # Add ribs and collect their edges
    for center_x in rib_centers:
        x1 = center_x - small_box_width / 2
        x2 = center_x + small_box_width / 2
        y1 = y_initial
        y2 = y_initial + small_box_height
        
        # Add rib
        msp.add_lwpolyline(
            [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)],
            close=True
        )
        rib_edges.append((x1, x2))

    # Sort ribs by their left edge
    rib_edges_sorted = sorted(rib_edges, key=lambda x: x[0])
    
    # Create connecting line segments (skipping rib areas)
    current_pos = 0  # Start from left slab edge
    connection_segments = []
    
    for rib_left, rib_right in rib_edges_sorted:
        if current_pos < rib_left:
            # Add segment from current position to left of rib
            connection_segments.append((current_pos, rib_left))
        current_pos = rib_right  # Move past this rib
    
    # Add final segment from last rib to right edge
    if current_pos < big_box_length:
        connection_segments.append((current_pos, big_box_length))
    
    # Draw only the non-penetrating connecting lines
    for start, end in connection_segments:
        msp.add_line((start, y_center), (end, y_center))
    
    return doc


def visualize(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height, Cb):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Draw the big box (slab)
    ax.add_patch(Rectangle((0, 0), big_box_length, big_box_height, 
                fill=None, edgecolor='blue', linewidth=2))
    
    # Calculate rib positions
    y_initial = (Cb * 10) + 10 + 0.75  # Base Y position
    y_center = y_initial + (small_box_height / 2)  # Vertical center of ribs
    rib_edges = []  # To store (left, right) edges of ribs
    
    # Draw ribs and collect their edges
    for center_x in rib_centers:
        x1 = center_x - small_box_width / 2
        x2 = center_x + small_box_width / 2
        ax.add_patch(Rectangle((x1, y_initial), small_box_width, small_box_height,
                    fill=None, edgecolor='red', linewidth=2))
        rib_edges.append((x1, x2))
    
    # Create connection segments (skipping areas inside ribs)
    connection_segments = []
    
    # Start from left edge of slab
    current_pos = 0
    
    # Sort ribs by their left edge
    rib_edges_sorted = sorted(rib_edges, key=lambda x: x[0])
    
    for rib_left, rib_right in rib_edges_sorted:
        if current_pos < rib_left:
            # Add segment from current position to left of rib
            connection_segments.append((current_pos, rib_left))
        current_pos = rib_right  # Skip the rib area
    
    # Add final segment from last rib to right edge
    if current_pos < big_box_length:
        connection_segments.append((current_pos, big_box_length))
    
    # Draw connecting lines for each segment
    for start, end in connection_segments:
        ax.plot([start, end], [y_center, y_center], 
               color='green', linestyle='-', linewidth=1.5)
    
    # Set axis limits and aspect ratio
    ax.set_xlim(0, big_box_length)
    ax.set_ylim(0, big_box_height)
    ax.set_aspect('equal', adjustable='box')
    
    # # Customize ticks
    # xticks = [0] + [x for rib in rib_edges for x in rib] + [big_box_length]
    # yticks = [0, y_initial, y_initial + small_box_height, big_box_height]
    
    # Customize x and y ticks (show start, end, and major divisions)
    xticks = [0] + rib_centers + [big_box_length]
    yticks = [0, big_box_height / 2, big_box_height]
    
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    
    # Formatting
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.set_xlabel("Length (mm)", fontsize=12)
    ax.set_ylabel("Height (mm)", fontsize=12)
    
    # Highlight slab corners only
    ax.scatter([big_box_length], [0], color='black', marker='o', s=50, zorder=5)
    ax.scatter([0], [big_box_height], color='black', marker='o', s=50, zorder=5)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    return fig

# Streamlit UI
st.title('DXF Generator for FIRIKA Insulation')

Length = ""
element_length_type = st.selectbox('Length of element', ['1m', '0.5m', 'compact','Lenght'])
if element_length_type == 'Lenght':
    Length = st.number_input('Lenght [mm]' ,min_value=300, max_value=900, value=300, step=100)


if element_length_type == '0.5m':
    num_ribs = st.selectbox('Number of ribs', [2, 3, 4, 5])
elif element_length_type == 'compact':
    num_ribs = st.number_input('Number of ribs', min_value=1, max_value=10, value=1, step=1)
else:  # 1m case
    num_ribs = st.number_input('Number of ribs', min_value=2, max_value=10, value=2, step=1)

h_rib = st.selectbox('Height of Ribs (cm)', [11, 13, 15, 17, 19])
Cb = st.number_input('Concrete Cover buttom (cm)' , value=2.5, step=0.5)
Ct = st.number_input('Concrete Cover top (cm)', value=2.5, step=0.5)


# Select insulation material
insulation = st.radio('Insulation material', ['EPS/XPS', 'SW'])

#Fire resistance options
if insulation == 'SW':
    fire_resistance = st.selectbox('Fire resistance', ['REI120'])  # Only REI120 for SW
else:
    fire_resistance = st.selectbox('Fire resistance', ['R0', 'REI60', 'REI90'])  


# Process inputs
Cb, Ct = adjust_h_for_fire_resistance(Cb, Ct, fire_resistance)

element_length_mm = get_element_length(element_length_type, num_ribs,Length)

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


def generate_dxf():
    if not rib_centers:
        st.error('Cannot generate DXF: undefined spacing for the current inputs.')
        return None
    with st.spinner('Generating DXF...'):
        doc = create_dxf(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height, Cb)
        doc.saveas('Insulation.dxf')
    with open('Insulation.dxf', 'rb') as f:
        return f.read()

# Single interactive download button
dxf_data = generate_dxf()
if dxf_data:
    st.download_button(
        label='Generate and Download DXF',
        data=dxf_data,
        file_name='Insulation.dxf',
        mime='application/dxf'
    )