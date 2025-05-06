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

def get_centers_Length(num_ribs, Length):
    if num_ribs < 1:
        return []

    first_center = 64.5  # Fixed starting position
    if num_ribs == 1:
        min_length = first_center + 35  # 64.5 + 35 = 99.5mm
        return [first_center] if Length >= min_length else []

    last_center_max = Length - 35.5  # Maximum allowed last rib center position
    best_centers = []
    for spacing in range(100, 10000, 100):  
        total_span = spacing * (num_ribs - 1)
        last_center = first_center + total_span
        if last_center <= last_center_max:
            centers = [first_center + i * spacing for i in range(num_ribs)]
            best_centers = centers
        else:
            break
    return best_centers

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

def create_dxf(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height, Cb):
    doc = ezdxf.new(dxfversion='R2010', setup=True)
    doc.units = units.MM
    msp = doc.modelspace()

    msp.add_lwpolyline(
        [(0, 0), (big_box_length, 0), (big_box_length, big_box_height), (0, big_box_height), (0, 0)],
        close=True
    )

    y_initial = (Cb * 10) + 10 - 0.75
    y_center = y_initial + (small_box_height / 2)
    rib_edges = []

    for center_x in rib_centers:
        x1 = center_x - small_box_width / 2
        x2 = center_x + small_box_width / 2
        y1 = y_initial
        y2 = y_initial + small_box_height
        
        msp.add_lwpolyline(
            [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)],
            close=True
        )
        rib_edges.append((x1, x2))

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
    
    return doc

def visualize(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height, Cb):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.add_patch(Rectangle((0, 0), big_box_length, big_box_height, fill=None, edgecolor='blue', linewidth=2))
    
    y_initial = (Cb * 10) + 10 + 0.75
    y_center = y_initial + (small_box_height / 2)
    rib_edges = []
    
    for center_x in rib_centers:
        x1 = center_x - small_box_width / 2
        x2 = center_x + small_box_width / 2
        ax.add_patch(Rectangle((x1, y_initial), small_box_width, small_box_height, fill=None, edgecolor='red', linewidth=2))
        rib_edges.append((x1, x2))
    
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
        ax.plot([start, end], [y_center, y_center], color='green', linestyle='-', linewidth=1.5)
    
    ax.set_xlim(0, big_box_length)
    ax.set_ylim(0, big_box_height)
    ax.set_aspect('equal', adjustable='box')
    
    xticks = [0] + rib_centers + [big_box_length]
    yticks = [0, big_box_height / 2, big_box_height]
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    ax.set_xlabel("Length (mm)", fontsize=12)
    ax.set_ylabel("Height (mm)", fontsize=12)
    
    ax.scatter([big_box_length], [0], color='black', marker='o', s=50, zorder=5)
    ax.scatter([0], [big_box_height], color='black', marker='o', s=50, zorder=5)
    
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    return fig

# Streamlit UI
st.title('DXF Generator for FIRIKA Insulation')

code = st.text_input('Enter product code', placeholder='e.g., C/02-11/65.35.08/100/EPS/R0')

valid_input = True
num_ribs = None
h_rib = None
Cb = None
Ct = None
element_length_type = None
element_length_mm = None
insulation = None
fire_resistance = None

if code:
    parts = code.split('/')
    if len(parts) < 6:
        st.error('Invalid code format. Expected format like C/02-11/65.35.08/100/EPS/R0')
        valid_input = False
    else:
        # Parse rib info
        rib_part = parts[1]
        rib_info = rib_part.split('-')
        if len(rib_info) != 2:
            st.error(f'Invalid rib info: {rib_part}. Expected format like 02-11.')
            valid_input = False
        else:
            try:
                num_ribs = int(rib_info[0])
                if num_ribs < 1 or num_ribs > 10:
                    st.error('Number of ribs must be between 1 and 10.')
                    valid_input = False
            except ValueError:
                st.error(f'Invalid number of ribs: {rib_info[0]}. Must be an integer.')
                valid_input = False
            try:
                h_rib = int(rib_info[1])
                if h_rib not in [11, 13, 15, 17, 19]:
                    st.error('Rib height must be one of: 11, 13, 15, 17, 19 cm.')
                    valid_input = False
            except ValueError:
                st.error(f'Invalid rib height: {rib_info[1]}. Must be an integer.')
                valid_input = False

        # Parse covers
        covers_part = parts[2]
        covers_info = covers_part.split('.')
        if len(covers_info) < 3:
            st.error(f'Invalid covers info: {covers_part}. Expected format like 65.35.08.')
            valid_input = False
        else:
            try:
                Ct_mm = int(covers_info[0])
                Cb_mm = int(covers_info[1])
                # Insulation thickness is covers_info[2], stored but not used
            except ValueError:
                st.error(f'Invalid concrete cover values: {covers_info[0]} or {covers_info[1]}. Must be integers.')
                valid_input = False

        # Parse element length code
        try:
            element_length_code = int(parts[3])
        except ValueError:
            st.error(f'Invalid element length code: {parts[3]}. Must be a number.')
            valid_input = False

        # Parse insulation type
        insulation_type = parts[4]
        if insulation_type not in ['EPS', 'XPS', 'SW']:
            st.error(f'Invalid insulation type: {insulation_type}. Must be EPS, XPS, or SW.')
            valid_input = False
        else:
            insulation = 'EPS/XPS' if insulation_type in ['EPS', 'XPS'] else 'SW'

        # Parse fire resistance
        fire_resistance = parts[5]
        if insulation == 'SW' and fire_resistance != 'REI120':
            st.error('SW insulation must have fire resistance REI120.')
            valid_input = False
        elif insulation == 'EPS/XPS' and fire_resistance not in ['R0', 'REI60', 'REI90']:
            st.error(f'Invalid fire resistance for EPS/XPS: {fire_resistance}. Allowed: R0, REI60, REI90.')
            valid_input = False

if valid_input and num_ribs is not None and h_rib is not None:
    # Convert covers from mm to cm
    Ct = Ct_mm / 10.0
    Cb = Cb_mm / 10.0

    # Determine element_length_type
    element_length_code = int(parts[3])
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
        Length_custom = element_length_code * 10  # Convert code (e.g., 030 → 300mm)
    else:
        Length_custom = 0  # Not used for other types
    element_length_mm = get_element_length(element_length_type, num_ribs, Length_custom)

    # Adjust covers for fire resistance
    Cb, Ct = adjust_h_for_fire_resistance(Cb, Ct, fire_resistance)

    # Calculate dimensions
    big_box_length = element_length_mm + 10
    big_box_height = (Cb + Ct + h_rib) * 10 + 20
    small_box_width = 18 if insulation == 'SW' else 17
    small_box_height = h_rib * 10 + 1.5

    # Calculate rib centers
    rib_centers = calculate_rib_centers(element_length_type, num_ribs, element_length_mm)

    # Visualization
    if st.button('Visualize'):
        if not rib_centers:
            st.warning('Spacing rules not defined for this configuration.')
        else:
            fig = visualize(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height, Cb)
            st.pyplot(fig)

    # DXF Generation
    def generate_dxf():
        if not rib_centers:
            st.error('Cannot generate DXF: undefined spacing for the current inputs.')
            return None
        with st.spinner('Generating DXF...'):
            doc = create_dxf(big_box_length, big_box_height, rib_centers, small_box_width, small_box_height, Cb)
            doc.saveas('Insulation.dxf')
        with open('Insulation.dxf', 'rb') as f:
            return f.read()

    dxf_data = generate_dxf()
    if dxf_data:
        st.download_button(
            label='Download DXF File',
            data=dxf_data,
            file_name='Insulation.dxf',
            mime='application/dxf'
        )