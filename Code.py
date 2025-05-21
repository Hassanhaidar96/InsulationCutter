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
from io import BytesIO  
import tempfile
import os

def adjust_h_for_fire_resistance(Cb, Ct, fire_resistance):
    if fire_resistance == 'REI60':
        return Cb - 1, Ct - 1
    elif fire_resistance == 'REI90':
        return Cb - 1.5, Ct - 1.5
    else:
        return Cb, Ct

def get_element_length(element_length_type, num_ribs, Length):
    if element_length_type == '1m':
        return 1000  # in mm
    elif element_length_type == '0.5m':
        return 500  # in mm
    elif element_length_type == 'compact':
        return num_ribs * 100  # 10 cm per rib, converted to mm
    elif element_length_type == 'Lenght':
        return Length  # in mm

def get_centers_1m(num_ribs):
    centers = {
        2: [114.5, 914.5],
        3: [114.5, 514.5, 914.5],
        4: [114.5, 414.5, 614.5, 914.5],
        5: [114.5, 314.5, 514.5, 714.5, 914.5],
        6: [114.5, 314.5, 414.5, 614.5, 714.5, 914.5],
        7: [114.5, 214.5, 414.5, 514.5, 614.5, 814.5, 914.5],
        8: [114.5, 214.5, 314.5, 414.5, 614.5, 714.5, 814.5, 914.5],
        9: [114.5, 214.5, 314.5, 414.5, 514.5, 614.5, 714.5, 814.5, 914.5],
        10: [64.5, 164.5, 264.5, 364.5, 464.5, 564.5, 664.5, 764.5, 864.5, 964.5]
    }
    return centers.get(num_ribs, [])

def get_centers_05m(num_ribs):
    centers = {
        2: [114.5, 414.5],
        3: [114.5, 214.5, 414.5],
        4: [114.5, 214.5, 314.5, 414.5],
        5: [64.5, 164.5, 264.5, 364.5, 464.5]
    }
    return centers.get(num_ribs, [])

def get_centers_compact(num_ribs):
    centers = {
        1: [55],
        2: [64.5, 164.5],
        3: [64.5, 164.5, 264.5],
        4: [64.5, 164.5, 264.5, 364.5],
        5: [64.5, 164.5, 264.5, 364.5, 464.5],
        6: [64.5, 164.5, 264.5, 364.5, 464.5, 564.5],
        7: [64.5, 164.5, 264.5, 364.5, 464.5, 564.5, 664.5],
        8: [64.5, 164.5, 264.5, 364.5, 464.5, 564.5, 664.5, 764.5],
        9: [64.5, 164.5, 264.5, 364.5, 464.5, 564.5, 664.5, 764.5, 864.5],
        10: [64.5, 164.5, 264.5, 364.5, 464.5, 564.5, 664.5, 764.5, 864.5, 964.5]
    }
    return centers.get(num_ribs, [])


# def get_centers_Length(num_ribs, Length):
#     if num_ribs < 1:
#         return []

#     first_center = 64.5  # Fixed starting position
#     if num_ribs == 1:
#         min_length = first_center + 35  # 64.5 + 35 = 99.5mm
#         return [first_center] if Length >= min_length else []

#     last_center_max = Length - 35.5  # Maximum allowed last rib center position
#     best_centers = []
#     for spacing in range(100, 10000, 100):  
#         total_span = spacing * (num_ribs - 1)
#         last_center = first_center + total_span
#         if last_center <= last_center_max:
#             centers = [first_center + i * spacing for i in range(num_ribs)]
#             best_centers = centers
#         else:
#             break
#     return best_centers

def get_centers_Length(num_ribs, Length):
    first_center = 64.5  # Starting position fixed
    last_center_max = Length - 35.5  # Last center must be <= this value
    
    # Determine the maximum number of ribs based on Length (converted to cm)
    cm = Length // 10  # Convert mm to cm via integer division
    
    # Initialize variables to hold spacings
    spacings = []
    
    # Determine spacings based on cm range and num_ribs
    if 90 <= cm <= 99:
        max_ribs = 9
        if num_ribs == 9:
            spacings = [100] * 8
        elif num_ribs == 8:
            spacings = [100, 100, 100, 200, 100, 100, 100]
        elif num_ribs == 7:
            spacings = [100, 100, 200, 200, 100, 100]
        elif num_ribs == 6:
            spacings = [100, 200, 200, 200, 100]
        elif num_ribs == 5:
            spacings = [200, 200, 200, 200]
        elif num_ribs == 4:
            spacings = [300, 200, 300]  
        elif num_ribs == 3:
            spacings = [400, 400] 
        elif num_ribs == 2:
            spacings = [800]  
            
    elif 80 <= cm <= 89:
        max_ribs = 8
        if num_ribs == 8:
            spacings = [100] * 7
        elif num_ribs == 7:
            spacings = [100, 100, 200, 100, 100,100]
        elif num_ribs == 6:
            spacings = [100, 200, 100, 200,100]
        elif num_ribs == 5:
            spacings = [200, 200, 200,100]
        elif num_ribs == 4:
            spacings = [200,300,200]  
        elif num_ribs == 3:
            spacings = [300, 400]  
        elif num_ribs == 2:
            spacings = [700]  
    elif 70 <= cm <= 79:
        max_ribs = 7
        if num_ribs == 7:
            spacings = [100] * 6
        elif num_ribs == 6:
            spacings = [100, 100, 200, 100, 100]
        elif num_ribs == 5:
            spacings = [100, 200, 200, 100]
        elif num_ribs == 4:
            spacings = [200, 200, 200]
        elif num_ribs == 3:
            spacings = [300, 300] 
        elif num_ribs == 2:
            spacings = [600]  
    elif 60 <= cm <= 69:
        max_ribs = 6
        if num_ribs == 6:
            spacings = [100] * 5
        elif num_ribs == 5:
            spacings = [100, 100, 200, 100]
        elif num_ribs == 4:
            spacings = [200, 100, 200]
        elif num_ribs == 3:
            spacings = [200, 300]  # Not possible (num_200 = 3), will fail check
        elif num_ribs == 2:
            spacings = [500]  
    elif 50 <= cm <= 59:
        max_ribs = 5
        if num_ribs == 5:
            spacings = [100] * 4
        elif num_ribs == 4:
            spacings = [100, 200, 100]
        elif num_ribs == 3:
            spacings = [200, 200]
        elif num_ribs == 2:
            spacings = [400]  
    elif 40 <= cm <= 49:
        max_ribs = 4
        if num_ribs == 4:
            spacings = [100] * 3
        elif num_ribs == 3:
            spacings = [200, 100]
        elif num_ribs == 2:
            spacings = [300] 
    elif 30 <= cm <= 39:
        max_ribs = 3
        if num_ribs == 3:
            spacings = [100] * 2
        elif num_ribs == 2:
            spacings = [200]
    elif 20 <= cm <= 29:
        max_ribs = 2
        if num_ribs == 2:
            spacings = [100]
    else:
        return []  # Length is below 20 cm
    
    # Check if num_ribs is invalid for the cm range
    if num_ribs < 2 or num_ribs > max_ribs:
        return []
    
    # Calculate the centers
    centers = [first_center]
    current = first_center
    for s in spacings:
        current += s
        centers.append(round(current, 1))  # Round to avoid floating issues
    
    # Check if the last center exceeds the allowed position
    if centers[-1] > last_center_max + 1e-9:  # Floating point tolerance
        return []
    
    return centers



def calculate_rib_centers(element_length_type, num_ribs, element_length_mm):
    if element_length_type == '1m':
        return get_centers_1m(num_ribs)
    elif element_length_type == '0.5m':
        return get_centers_05m(num_ribs)
    elif element_length_type == 'compact':
        return get_centers_compact(num_ribs)
    elif element_length_type == 'Lenght':
        return get_centers_Length(num_ribs, element_length_mm)
    else:
        return []


def create_dxf(elements_data):
    doc = ezdxf.new(dxfversion='R2010', setup=True)
    doc.units = units.MM
    msp = doc.modelspace()
    y_offset = 0

    for element in elements_data:
        big_box_length = element['big_box_length']
        big_box_height = element['big_box_height']
        rib_centers = element['rib_centers']
        small_box_width = element['small_box_width']
        small_box_height = element['small_box_height']
        Cb = element['Cb']

        # Draw main box
        msp.add_lwpolyline(
            [(0, y_offset), (big_box_length, y_offset),
             (big_box_length, y_offset + big_box_height),
             (0, y_offset + big_box_height), (0, y_offset)],
            close=True
        )

        # Draw ribs
        y_initial = y_offset + (Cb * 10 + 10 - 0.75)
        y_center = y_initial + (small_box_height / 2)
        rib_edges = []

        for center_x in rib_centers:
            x1 = center_x - small_box_width / 2
            x2 = center_x + small_box_width / 2
            msp.add_lwpolyline(
                [(x1, y_initial), (x2, y_initial),
                 (x2, y_initial + small_box_height),
                 (x1, y_initial + small_box_height),
                 (x1, y_initial)],
                close=True
            )
            rib_edges.append((x1, x2))

        # Draw connections
        rib_edges_sorted = sorted(rib_edges, key=lambda x: x[0])
        current_pos = 0
        connection_segments = []
        
        for rib_left, rib_right in rib_edges_sorted:
            if current_pos < rib_left:
                connection_segments.append((current_pos, rib_left))
            current_pos = rib_right
        
        if current_pos < big_box_length:
            connection_segments.append((current_pos, big_box_length))
        
        for start, end in connection_segments:
            msp.add_line((start, y_center), (end, y_center))

        y_offset += big_box_height + 50  # 5cm spacing

    return doc

def visualize(elements_data):
    fig, ax = plt.subplots(figsize=(10, 6))
    y_offset = 0

    for element in elements_data:
        big_box_length = element['big_box_length']
        big_box_height = element['big_box_height']
        rib_centers = element['rib_centers']
        small_box_width = element['small_box_width']
        small_box_height = element['small_box_height']
        Cb = element['Cb']

        # Draw main box
        ax.add_patch(Rectangle((0, y_offset), big_box_length, big_box_height,
                             fill=None, edgecolor='blue', linewidth=2))

        # Draw ribs
        y_initial = y_offset + (Cb * 10 + 10 + 0.75)
        y_center = y_initial + (small_box_height / 2)
        rib_edges = []
        
        for center_x in rib_centers:
            x1 = center_x - small_box_width / 2
            x2 = center_x + small_box_width / 2
            ax.add_patch(Rectangle((x1, y_initial), small_box_width, small_box_height,
                        fill=None, edgecolor='red', linewidth=2))
            rib_edges.append((x1, x2))

        # Draw connections
        connection_segments = []
        current_pos = 0
        
        rib_edges_sorted = sorted(rib_edges, key=lambda x: x[0])
        for rib_left, rib_right in rib_edges_sorted:
            if current_pos < rib_left:
                connection_segments.append((current_pos, rib_left))
            current_pos = rib_right
        
        if current_pos < big_box_length:
            connection_segments.append((current_pos, big_box_length))
        
        for start, end in connection_segments:
            ax.plot([start, end], [y_center, y_center], color='green',
                   linestyle='-', linewidth=1.5)

        y_offset += big_box_height + 50  # 5cm spacing

    # Configure plot
    max_length = max(e['big_box_length'] for e in elements_data)
    total_height = sum(e['big_box_height'] for e in elements_data) + 50 * (len(elements_data)-1)
    ax.set_xlim(0, max_length)
    ax.set_ylim(0, total_height)
    ax.set_aspect('equal', adjustable='box')
    
    # Formatting
    all_centers = []
    for e in elements_data:
        all_centers.extend(e['rib_centers'])
    xticks = [0] + sorted(all_centers) + [max_length]
    yticks = []
    current_y = 0
    for e in elements_data:
        yticks.append(current_y)
        current_y += e['big_box_height']
        yticks.append(current_y)
        current_y += 50
    ax.set_xticks(xticks)
    ax.set_yticks(list(set(yticks)))
    
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_xlabel("Length (mm)", fontsize=12)
    ax.set_ylabel("Height (mm)", fontsize=12)
    
    # Add corner markers
    ax.scatter([max_length], [0], color='black', marker='o', s=50, zorder=5)
    ax.scatter([0], [total_height], color='black', marker='o', s=50, zorder=5)
    
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    return fig

# Streamlit UI
st.title('DXF Generator for FIRIKA Insulation (Multi-Element)')

# Get number of elements
num_elements = st.number_input('Number of elements', min_value=1, max_value=10, value=1, step=1)

# Collect element codes
elements_data = []
valid_input = True
for i in range(num_elements):
    code = st.text_input(f'Enter product code for element {i+1}',
                        placeholder='e.g., C/02-11/65.35.08/100/EPS/R0',
                        key=f'code_{i}')

    parts = code.split('/')
    if len(parts) < 6:
        # st.error(f'Element {i+1}: Invalid code format. Expected format like C/02-11/65.35.08/100/EPS/R0')
        valid_input = False
        continue

    # Parse rib info
    rib_part = parts[1]
    rib_info = rib_part.split('-')
    if len(rib_info) != 2:
        st.error(f'Element {i+1}: Invalid rib info: {rib_part}. Expected format like 02-11.')
        valid_input = False
        continue
    
    try:
        num_ribs = int(rib_info[0])
        if num_ribs < 1 or num_ribs > 10:
            st.error(f'Element {i+1}: Number of ribs must be between 1 and 10.')
            valid_input = False
    except ValueError:
        st.error(f'Element {i+1}: Invalid number of ribs: {rib_info[0]}. Must be an integer.')
        valid_input = False
        continue
    
    try:
        h_rib = int(rib_info[1])
        if h_rib not in [11, 13, 15, 17, 19]:
            st.error(f'Element {i+1}: Rib height must be one of: 11, 13, 15, 17, 19 cm.')
            valid_input = False
    except ValueError:
        st.error(f'Element {i+1}: Invalid rib height: {rib_info[1]}. Must be an integer.')
        valid_input = False
        continue

    # Parse covers
    covers_part = parts[2]
    covers_info = covers_part.split('.')
    if len(covers_info) < 3:
        st.error(f'Element {i+1}: Invalid covers info: {covers_part}. Expected format like 65.35.08.')
        valid_input = False
        continue
    
    try:
        Ct_mm = int(covers_info[0])
        Cb_mm = int(covers_info[1])
    except ValueError:
        st.error(f'Element {i+1}: Invalid concrete cover values: {covers_info[0]} or {covers_info[1]}. Must be integers.')
        valid_input = False
        continue

    # Parse element length code
    try:
        element_length_code = int(parts[3])
    except ValueError:
        st.error(f'Element {i+1}: Invalid element length code: {parts[3]}. Must be a number.')
        valid_input = False
        continue

    # Parse insulation type
    insulation_type = parts[4]
    if insulation_type not in ['EPS', 'XPS', 'SW']:
        st.error(f'Element {i+1}: Invalid insulation type: {insulation_type}. Must be EPS, XPS, or SW.')
        valid_input = False
        continue
    else:
        insulation = 'EPS/XPS' if insulation_type in ['EPS', 'XPS'] else 'SW'

    # Parse fire resistance
    fire_resistance = parts[5]
    if insulation == 'SW' and fire_resistance != 'REI120':
        st.error(f'Element {i+1}: SW insulation must have fire resistance REI120.')
        valid_input = False
        continue
    elif insulation == 'EPS/XPS' and fire_resistance not in ['R0', 'REI60', 'REI90']:
        st.error(f'Element {i+1}: Invalid fire resistance for EPS/XPS: {fire_resistance}. Allowed: R0, REI60, REI90.')
        valid_input = False
        continue

    # Convert covers from mm to cm
    Ct = Ct_mm / 10.0
    Cb = Cb_mm / 10.0

    # Adjust covers for fire resistance
    Cb, Ct = adjust_h_for_fire_resistance(Cb, Ct, fire_resistance)

    # Determine element_length_type
    if element_length_code == 100:
        element_length_type = '1m'
    elif element_length_code == 50:
        element_length_type = '0.5m'
    elif element_length_code == num_ribs * 10:
        element_length_type = 'compact'
    else:
        element_length_type = 'Lenght'

    # Calculate element_length_mm
    if element_length_type == 'Lenght':
        Length_custom = element_length_code * 10
    else:
        Length_custom = 0
    element_length_mm = get_element_length(element_length_type, num_ribs, Length_custom)

    # Calculate dimensions
    big_box_length = element_length_mm + 10
    big_box_height = (Cb + Ct + h_rib) * 10 + 20
    small_box_width = 18 if insulation == 'SW' else 17
    small_box_height = h_rib * 10 + 1.5

    # Calculate rib centers
    rib_centers = calculate_rib_centers(element_length_type, num_ribs, element_length_mm)

    # Store element data
    elements_data.append({
        'index': i+1,
        'big_box_length': big_box_length,
        'big_box_height': big_box_height,
        'rib_centers': rib_centers,
        'small_box_width': small_box_width,
        'small_box_height': small_box_height,
        'Cb': Cb
    })

# Visualization and DXF Generation
if valid_input and elements_data:
    # Check for elements with invalid rib configurations
    invalid_elements = [e['index'] for e in elements_data if not e['rib_centers']]
    valid_elements = [e for e in elements_data if e['rib_centers']]
    
    if invalid_elements:
        st.warning(f"The following elements have undefined spacing rules and won't be included: {', '.join(map(str, invalid_elements))}")
    
    if not valid_elements:
        st.error("No valid elements to display or export. Please check your inputs.")
    else:
        
        # Visualization
        if st.button('Visualize All Elements'):
            try:
                fig = visualize(valid_elements)
                st.pyplot(fig)  # Removed expander block
            except Exception as e:
                st.error(f"Visualization error: {str(e)}")
                
                
        
        # Modified DXF Generation
        st.subheader("DXF Export")
        if st.button('Generate DXF File'):
            tmp = None  # Initialize tmp variable for cleanup
            try:
                # Create temporary file
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.dxf')
                
                # Generate DXF content
                doc = create_dxf(valid_elements)
                doc.saveas(tmp.name)
                st.write(f"Temporary file size: {os.path.getsize(tmp.name)} bytes")
                tmp.close()  # Important: Close before reading
                
                # Read generated content
                with open(tmp.name, 'rb') as f:
                    dxf_data = f.read()
                
                # Create download button
                st.download_button(
                    label='Download DXF File',
                    data=dxf_data,
                    file_name='Insulation.dxf',
                    mime='application/dxf'
                )
                st.success("DXF generated successfully!")
                
            except Exception as e:
                st.error(f"DXF generation failed: {str(e)}")
            finally:
                # Clean up temporary file
                if tmp and os.path.exists(tmp.name):
                    os.unlink(tmp.name)
                    
                    
                    
                    


                    
                    
                    
                    
            
                    
                    