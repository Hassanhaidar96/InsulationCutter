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

def get_board_dimensions(insulation, insulation_thickness):
    if insulation == 'EPS':
        if insulation_thickness == 80:
            return (2500, 1000)
        elif insulation_thickness == 120:
            return (2500, 1200)
    elif insulation == 'SW':
        if insulation_thickness == 80:
            return (2400, 1200)
        elif insulation_thickness == 120:
            return (1200, 600)
    elif insulation == 'XPS':
        if insulation_thickness == 80:
            return (3000, 1000)
        elif insulation_thickness == 120:
            return (1200, 600)
    return (0, 0)  # default

def create_dxf(big_board_length, big_board_height, element_x_offset, element_y_offset, 
               rib_centers, small_box_width, small_box_height, Cb, element_length_mm):
    doc = ezdxf.new(dxfversion='R2010', setup=True)
    doc.units = units.MM
    msp = doc.modelspace()

    # Add big board
    msp.add_lwpolyline(
        [(0, 0), (big_board_length, 0), (big_board_length, big_board_height), 
         (0, big_board_height), (0, 0)],
        close=True
    )

    # Calculate element position (9cm from left, at top in Y)
    element_x = element_x_offset
    element_y = big_board_height - (element_y_offset + ((Cb + small_box_height/10 + Ct) * 10))
    
    # Add element boundary (for visualization)
    element_height = (Cb + small_box_height/10 + Ct) * 10
    msp.add_lwpolyline(
        [(element_x, element_y), 
         (element_x + element_length_mm, element_y),
         (element_x + element_length_mm, element_y + element_height),
         (element_x, element_y + element_height),
         (element_x, element_y)],
        close=True
    )

    # Calculate rib positions relative to element
    y_initial = element_y + (Cb * 10) + 10 - 0.75  # Base Y position
    y_center = y_initial + (small_box_height / 2)  # Vertical center of ribs
    rib_edges = []  # Store (left, right) edges of all ribs
    
    # Add ribs and collect their edges
    for center_x in rib_centers:
        x1 = element_x + center_x - small_box_width / 2
        x2 = element_x + center_x + small_box_width / 2
        
        # Add rib
        msp.add_lwpolyline(
            [(x1, y_initial), (x2, y_initial), (x2, y_initial + small_box_height), 
             (x1, y_initial + small_box_height), (x1, y_initial)],
            close=True
        )
        rib_edges.append((x1, x2))

    # Sort ribs by their left edge
    rib_edges_sorted = sorted(rib_edges, key=lambda x: x[0])
    
    # Create connecting line segments (skipping rib areas)
    current_pos = element_x  # Start from left element edge
    connection_segments = []
    
    for rib_left, rib_right in rib_edges_sorted:
        if current_pos < rib_left:
            # Add segment from current position to left of rib
            connection_segments.append((current_pos, rib_left))
        current_pos = rib_right  # Move past this rib
    
    # Add final segment from last rib to right edge
    if current_pos < element_x + element_length_mm:
        connection_segments.append((current_pos, element_x + element_length_mm))
    
    # Draw only the non-penetrating connecting lines
    for start, end in connection_segments:
        msp.add_line((start, y_center), (end, y_center))
    
    return doc

def visualize(big_board_length, big_board_height, element_x_offset, element_y_offset, 
              rib_centers, small_box_width, small_box_height, Cb, element_length_mm):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Draw the big board
    ax.add_patch(Rectangle((0, 0), big_board_length, big_board_height, 
                fill=None, edgecolor='blue', linewidth=2))
    
    # Calculate element position (9cm from left, at top in Y)
    element_height = (Cb + small_box_height/10 + Ct) * 10
    element_x = element_x_offset
    element_y = big_board_height - (element_y_offset + element_height)
    
    # Draw element boundary
    ax.add_patch(Rectangle((element_x, element_y), element_length_mm, element_height,
                fill=None, edgecolor='purple', linewidth=2, linestyle='--'))
    
    # Calculate rib positions relative to element
    y_initial = element_y + (Cb * 10) + 10 + 0.75  # Base Y position
    y_center = y_initial + (small_box_height / 2)  # Vertical center of ribs
    rib_edges = []  # To store (left, right) edges of ribs
    
    # Draw ribs and collect their edges
    for center_x in rib_centers:
        x1 = element_x + center_x - small_box_width / 2
        x2 = element_x + center_x + small_box_width / 2
        ax.add_patch(Rectangle((x1, y_initial), small_box_width, small_box_height,
                    fill=None, edgecolor='red', linewidth=2))
        rib_edges.append((x1, x2))
    
    # Create connection segments (skipping areas inside ribs)
    connection_segments = []
    
    # Start from left edge of element
    current_pos = element_x
    
    # Sort ribs by their left edge
    rib_edges_sorted = sorted(rib_edges, key=lambda x: x[0])
    
    for rib_left, rib_right in rib_edges_sorted:
        if current_pos < rib_left:
            # Add segment from current position to left of rib
            connection_segments.append((current_pos, rib_left))
        current_pos = rib_right  # Skip the rib area
    
    # Add final segment from last rib to right edge
    if current_pos < element_x + element_length_mm:
        connection_segments.append((current_pos, element_x + element_length_mm))
    
    # Draw connecting lines for each segment
    for start, end in connection_segments:
        ax.plot([start, end], [y_center, y_center], 
               color='green', linestyle='-', linewidth=1.5)
    
    # Set axis limits and aspect ratio
    ax.set_xlim(0, big_board_length)
    ax.set_ylim(0, big_board_height)
    ax.set_aspect('equal', adjustable='box')
    
    # Customize x and y ticks
    xticks = [0, element_x, element_x + element_length_mm, big_board_length]
    yticks = [0, big_board_height / 2, big_board_height]
    
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    # Formatting
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.set_xlabel("Length (mm)", fontsize=12)
    ax.set_ylabel("Height (mm)", fontsize=12)
    
    # Highlight board corners
    ax.scatter([big_board_length], [0], color='black', marker='o', s=50, zorder=5)
    ax.scatter([0], [big_board_height], color='black', marker='o', s=50, zorder=5)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    return fig

# Streamlit UI
st.title('DXF Generator for FIRIKA Insulation')

# Board configuration
insulation = st.selectbox('Insulation material', ['EPS/XPS', 'SW', 'XPS'])
insulation_thickness = st.selectbox('Insulation thickness (mm)', [80, 120])

# Get board dimensions based on insulation type and thickness
big_board_length, big_board_height = get_board_dimensions(insulation, insulation_thickness)
st.write(f"Board dimensions: {big_board_length}mm x {big_board_height}mm")

# Element configuration
element_length_type = st.selectbox('Length of element', ['1m', '0.5m', 'compact'])

if element_length_type == '0.5m':
    num_ribs = st.selectbox('Number of ribs', [2, 3, 4, 5])
elif element_length_type == 'compact':
    num_ribs = st.number_input('Number of ribs', min_value=1, max_value=10, value=1, step=1)
else:  # 1m case
    num_ribs = st.number_input('Number of ribs', min_value=2, max_value=10, value=2, step=1)

h_rib = st.selectbox('Height of Ribs (cm)', [11, 13, 15, 17, 19])
Cb = st.number_input('Concrete Cover bottom (cm)', value=2.5, step=0.5)
Ct = st.number_input('Concrete Cover top (cm)', value=2.5, step=0.5)

# Fire resistance options
if insulation == 'SW':
    fire_resistance = st.selectbox('Fire resistance', ['REI120'])  # Only REI120 for SW
else:
    fire_resistance = st.selectbox('Fire resistance', ['R0', 'REI60', 'REI90'])  

# Process inputs
Cb, Ct = adjust_h_for_fire_resistance(Cb, Ct, fire_resistance)

element_length_mm = get_element_length(element_length_type, num_ribs)
small_box_width = 18 if insulation == 'SW' else 17  # width in mm
small_box_height = (h_rib * 10) + 1.5  # 0.15 cm to mm

rib_centers = calculate_rib_centers(element_length_type, num_ribs, element_length_mm)

# Position of first element (9cm from left, at top in Y)
element_x_offset = 90  # 9cm in mm
element_y_offset = 0   # at top

if st.button('Visualize'):
    if not rib_centers:
        st.warning('Spacing rules not defined for this configuration.')
    else:
        fig = visualize(big_board_length, big_board_height, element_x_offset, element_y_offset,
                       rib_centers, small_box_width, small_box_height, Cb, element_length_mm)
        st.pyplot(fig)

def generate_dxf():
    if not rib_centers:
        st.error('Cannot generate DXF: undefined spacing for the current inputs.')
        return None
    with st.spinner('Generating DXF...'):
        doc = create_dxf(big_board_length, big_board_height, element_x_offset, element_y_offset,
                        rib_centers, small_box_width, small_box_height, Cb, element_length_mm)
        doc.saveas('Insulation_with_board.dxf')
    with open('Insulation_with_board.dxf', 'rb') as f:
        return f.read()

# Single interactive download button
dxf_data = generate_dxf()
if dxf_data:
    st.download_button(
        label='Generate and Download DXF',
        data=dxf_data,
        file_name='Insulation_with_board.dxf',
        mime='application/dxf'
    )