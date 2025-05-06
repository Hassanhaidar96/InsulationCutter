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
        2: [114.5, 914.5], 3: [114.5, 514.5, 914.5],
        4: [114.5, 414.5, 614.5, 914.5], 5: [114.5, 314.5, 514.5, 714.5, 914.5],
        6: [114.5, 314.5, 414.5, 614.5, 714.5, 914.5],
        7: [114.5, 214.5, 414.5, 514.5, 614.5, 814.5, 914.5],
        8: [114.5, 214.5, 314.5, 414.5, 614.5, 714.5, 814.5, 914.5],
        9: [114.5, 214.5, 314.5, 414.5, 514.5, 614.5, 714.5, 814.5, 914.5],
        10: [64.5, 164.5, 264.5, 364.5, 464.5, 564.5, 664.5, 764.5, 864.5, 964.5]
    }
    return centers.get(num_ribs, [])

def get_centers_05m(num_ribs):
    centers = {
        2: [114.5, 414.5], 3: [114.5, 214.5, 414.5],
        4: [114.5, 214.5, 314.5, 414.5], 5: [64.5, 164.5, 264.5, 364.5, 464.5]
    }
    return centers.get(num_ribs, [])

def get_centers_compact(num_ribs):
    centers = {
        1: [55], 2: [64.5, 164.5], 3: [64.5, 164.5, 264.5],
        4: [64.5, 164.5, 264.5, 364.5], 5: [64.5, 164.5, 264.5, 364.5, 464.5],
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
    first_center = 64.5
    if num_ribs == 1:
        return [first_center] if Length >= first_center + 35 else []
    last_center_max = Length - 35.5
    best_centers = []
    for spacing in range(100, 10000, 100): 
        last_center = first_center + spacing * (num_ribs - 1)
        if last_center <= last_center_max:
            best_centers = [first_center + i * spacing for i in range(num_ribs)]
        else:
            break
    return best_centers

def calculate_rib_centers(element_length_type, num_ribs, element_length_mm):
    return {
        '1m': get_centers_1m,
        '0.5m': get_centers_05m,
        'compact': get_centers_compact,
        'Lenght': lambda n: get_centers_Length(n, element_length_mm)
    }.get(element_length_type, lambda _: [])(num_ribs)

def parse_product_code(code):
    try:
        parts = code.split('/')
        if len(parts) < 6:
            raise ValueError("Invalid code format")

        rib_part = parts[1].split('-')
        num_ribs = int(rib_part[0])
        h_rib = int(rib_part[1])

        covers = parts[2].split('.')
        Ct_mm, Cb_mm = int(covers[0]), int(covers[1])

        length_code = int(parts[3])
        if length_code == 100:
            el_type = '1m'
        elif length_code == 50:
            el_type = '0.5m'
        elif length_code == num_ribs * 10:
            el_type = 'compact'
        else:
            el_type = 'Lenght'
            custom_length = length_code * 10

        insulation = 'EPS/XPS' if parts[4] in ['EPS', 'XPS'] else 'SW'
        fire = parts[5]

        Ct, Cb = Ct_mm / 10, Cb_mm / 10
        Cb, Ct = adjust_h_for_fire_resistance(Cb, Ct, fire)

        el_length = get_element_length(el_type, num_ribs, custom_length if el_type == 'Lenght' else 0)
        big_length = el_length + 10
        big_height = (Cb + Ct + h_rib) * 10 + 20
        small_width = 18 if insulation == 'SW' else 17
        small_height = h_rib * 10 + 1.5

        rib_centers = calculate_rib_centers(el_type, num_ribs, el_length)

        return {
            'big_length': big_length,
            'big_height': big_height,
            'rib_centers': rib_centers,
            'small_width': small_width,
            'small_height': small_height,
            'Cb': Cb
        }

    except Exception as e:
        st.error(f"Error parsing code '{code}': {str(e)}")
        return None

def create_dxf(elements):
    doc = ezdxf.new(dxfversion='R2010', setup=True)
    doc.units = units.MM
    msp = doc.modelspace()
    y_offset = 0
    vertical_gap = 50

    for element in reversed(elements):  # Reverse to make first at top
        # Main box
        msp.add_lwpolyline([
            (0, y_offset), (element['big_length'], y_offset),
            (element['big_length'], y_offset + element['big_height']),
            (0, y_offset + element['big_height']), (0, y_offset)
        ], close=True)

        # Ribs
        y_rib_base = y_offset + element['Cb'] * 10 + 10 - 0.75
        for center in element['rib_centers']:
            x1 = center - element['small_width'] / 2
            x2 = center + element['small_width'] / 2
            msp.add_lwpolyline([
                (x1, y_rib_base), (x2, y_rib_base),
                (x2, y_rib_base + element['small_height']),
                (x1, y_rib_base + element['small_height']), (x1, y_rib_base)
            ], close=True)

        y_offset += element['big_height'] + vertical_gap

    return doc

def visualize_elements(elements):
    fig, ax = plt.subplots()
    y_offset = 0
    vertical_gap = 20

    for element in reversed(elements):  # reverse for visual matching
        ax.add_patch(Rectangle((0, y_offset), element['big_length'], element['big_height'],
                               edgecolor='black', facecolor='none', linewidth=1.5))

        y_rib_base = y_offset + element['Cb'] * 10 + 10 - 0.75
        for center in element['rib_centers']:
            x1 = center - element['small_width'] / 2
            ax.add_patch(Rectangle((x1, y_rib_base), element['small_width'], element['small_height'],
                                   edgecolor='blue', facecolor='lightblue', linewidth=1.2))

        y_offset += element['big_height'] + vertical_gap

    ax.set_aspect('equal')
    ax.set_title("Visualized Elements")
    st.pyplot(fig)

# Streamlit interface
st.title("Element Visualizer & DXF Exporter")

codes_input = st.text_area("Enter product codes (one per line):")

if st.button("Visualize"):
    codes = codes_input.strip().splitlines()
    parsed_elements = [parse_product_code(code.strip()) for code in codes if code.strip()]
    parsed_elements = [el for el in parsed_elements if el]

    if parsed_elements:
        visualize_elements(parsed_elements)

if st.button("Download DXF"):
    codes = codes_input.strip().splitlines()
    parsed_elements = [parse_product_code(code.strip()) for code in codes if code.strip()]
    parsed_elements = [el for el in parsed_elements if el]

    if parsed_elements:
        doc = create_dxf(parsed_elements)
        dxf_bytes = doc.write_to_bytes()
        st.download_button("Download DXF File", data=dxf_bytes, file_name="elements.dxf")
