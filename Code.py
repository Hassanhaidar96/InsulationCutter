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
import io

def adjust_h_for_fire_resistance(Cb, Ct, fire_resistance):
    if fire_resistance == 'REI60':
        return Cb - 1, Ct - 1
    elif fire_resistance == 'REI90':
        return Cb - 1.5, Ct - 1.5
    else:
        return Cb, Ct

def get_element_length(element_length_type, num_ribs, Length):
    if element_length_type == '1m':
        return 1000
    elif element_length_type == '0.5m':
        return 500
    elif element_length_type == 'compact':
        return num_ribs * 100
    elif element_length_type == 'Lenght':
        return Length

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
    base = [64.5 + i * 100 for i in range(num_ribs)]
    return base if num_ribs >= 1 else []

def get_centers_Length(num_ribs, Length):
    if num_ribs < 1:
        return []
    first_center = 64.5
    if num_ribs == 1:
        return [first_center] if Length >= first_center + 35 else []
    last_center_max = Length - 35.5
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

        msp.add_lwpolyline(
            [(0, y_offset), (big_box_length, y_offset),
             (big_box_length, y_offset + big_box_height),
             (0, y_offset + big_box_height), (0, y_offset)],
            close=True
        )

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

        y_offset += big_box_height + 50

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

        ax.add_patch(Rectangle((0, y_offset), big_box_length, big_box_height,
                               fill=None, edgecolor='blue', linewidth=2))

        y_initial = y_offset + (Cb * 10 + 10 + 0.75)
        y_center = y_initial + (small_box_height / 2)
        rib_edges = []

        for center_x in rib_centers:
            x1 = center_x - small_box_width / 2
            x2 = center_x + small_box_width / 2
            ax.add_patch(Rectangle((x1, y_initial), small_box_width, small_box_height,
                                   fill=None, edgecolor='red', linewidth=2))
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
            ax.plot([start, end], [y_center, y_center], color='green',
                    linestyle='-', linewidth=1.5)

        y_offset += big_box_height + 50

    ax.set_aspect('equal')
    ax.set_xlim(0, 1200)
    ax.set_ylim(0, y_offset + 100)
    ax.axis('off')
    st.pyplot(fig)

# --- Example Usage in Streamlit ---

st.title("DXF Rib Generator")

# Dummy example data
element = {
    'big_box_length': 1000,
    'big_box_height': 200,
    'rib_centers': get_centers_1m(5),
    'small_box_width': 30,
    'small_box_height': 50,
    'Cb': 1
}
elements_data = [element]

if st.button("Show Visualization"):
    visualize(elements_data)

if st.button("Download DXF"):
    try:
        doc = create_dxf(elements_data)
        buffer = io.BytesIO()
        doc.write(buffer)
        st.download_button("Download DXF File", buffer.getvalue(), file_name="rib_output.dxf")
    except Exception as e:
        st.error(f"Error generating DXF: {e}")



