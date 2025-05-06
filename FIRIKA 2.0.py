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
        2: [114.5, 414.5], 3: [114.5, 214.5, 414.5],
        4: [114.5, 214.5, 314.5, 414.5], 5: [64.5, 164.5, 264.5, 364.5, 464.5]
    }
    return centers.get(num_ribs, [])

def get_centers_compact(num_ribs):
    centers = {
        1: [55], 2: [64.5, 164.5], 
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
    if num_ribs < 1: return []
    first_center = 64.5
    if num_ribs == 1:
        return [first_center] if Length >= first_center + 35 else []
    last_center_max = Length - 35.5
    best_centers = []
    for spacing in range(100, 10000, 100):  
        last_center = first_center + spacing * (num_ribs - 1)
        if last_center <= last_center_max:
            best_centers = [first_center + i*spacing for i in range(num_ribs)]
        else: break
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
        if len(parts) < 6: raise ValueError("Invalid code format")
        
        # Rib info
        rib_part = parts[1].split('-')
        if len(rib_part) != 2: raise ValueError("Invalid rib format")
        num_ribs = int(rib_part[0])
        h_rib = int(rib_part[1])
        
        # Covers
        covers = parts[2].split('.')
        if len(covers) < 3: raise ValueError("Invalid cover format")
        Ct_mm, Cb_mm = int(covers[0]), int(covers[1])
        
        # Element length
        length_code = int(parts[3])
        if length_code == 100: el_type = '1m'
        elif length_code == 50: el_type = '0.5m'
        elif length_code == num_ribs * 10: el_type = 'compact'
        else: 
            el_type = 'Lenght'
            custom_length = length_code * 10
        
        # Insulation and fire
        insulation = 'EPS/XPS' if parts[4] in ['EPS', 'XPS'] else 'SW'
        fire = parts[5]
        
        # Convert covers to cm
        Ct, Cb = Ct_mm/10, Cb_mm/10
        Cb, Ct = adjust_h_for_fire_resistance(Cb, Ct, fire)
        
        # Calculate dimensions
        el_length = get_element_length(el_type, num_ribs, custom_length if el_type == 'Lenght' else 0)
        big_length = el_length + 10
        big_height = (Cb + Ct + h_rib) * 10 + 20
        small_width = 18 if insulation == 'SW' else 17
        small_height = h_rib * 10 + 1.5
        
        # Get rib centers
        rib_centers = calculate_rib_centers(el_type, num_ribs, el_length)
        
        return {
            'big_length': big_length,
            'big_height': big_height,
            'rib_centers': rib_centers,
            'small_width': small_width,
            'small_height': small_height,
            'Cb': Cb,
            'valid': bool(rib_centers)
        }
    except Exception as e:
        st.error(f"Error parsing code '{code}': {str(e)}")
        return {'valid': False}

def create_dxf(elements):
    doc = ezdxf.new(dxfversion='R2010', setup=True)
    doc.units = units.MM
    msp = doc.modelspace()
    
    total_height = sum(e['big_height'] for e in elements) + (len(elements)-1)*50
    y_offset = total_height
    
    for element in reversed(elements):
        y_offset -= element['big_height']
        
        # Corrected slab polyline (4 points + close=True)
        slab_points = [
            (0, y_offset),
            (element['big_length'], y_offset),
            (element['big_length'], y_offset + element['big_height']),
            (0, y_offset + element['big_height'])
        ]
        msp.add_lwpolyline(slab_points, close=True)
        
        # Add ribs with corrected polyline
        y_rib_base = y_offset + element['Cb']*10 + 10 - 0.75
        for center in element['rib_centers']:
            x1 = center - element['small_width']/2
            x2 = center + element['small_width']/2
            rib_points = [
                (x1, y_rib_base),
                (x2, y_rib_base),
                (x2, y_rib_base + element['small_height']),
                (x1, y_rib_base + element['small_height'])
            ]
            msp.add_lwpolyline(rib_points, close=True)
        
        # Connections remain the same
        y_center = y_rib_base + element['small_height']/2
        current_x = 0
        rib_edges = sorted([(c - element['small_width']/2, c + element['small_width']/2) 
                          for c in element['rib_centers']])
        for left, right in rib_edges:
            if current_x < left:
                msp.add_line((current_x, y_center), (left, y_center))
            current_x = right
        if current_x < element['big_length']:
            msp.add_line((current_x, y_center), (element['big_length'], y_center))
        
        y_offset -= 50
    
    return doc

def visualize(elements):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Start from bottom
    y_offset = 0
    vertical_gap = 50
    
    for element in elements:
        # Draw slab
        ax.add_patch(Rectangle(
            (0, y_offset), 
            element['big_length'], 
            element['big_height'],
            edgecolor='navy', 
            fill=None, 
            linewidth=1.5
        ))
        
        # Draw ribs
        y_rib = y_offset + element['Cb']*10 + 10 + 0.75
        for center in element['rib_centers']:
            x1 = center - element['small_width']/2
            ax.add_patch(Rectangle(
                (x1, y_rib), 
                element['small_width'], 
                element['small_height'],
                edgecolor='maroon', 
                fill=None, 
                linewidth=1
            ))
        
        # Draw connections
        y_center = y_rib + element['small_height']/2
        current_x = 0
        rib_edges = sorted([
            (c - element['small_width']/2, c + element['small_width']/2) 
            for c in element['rib_centers']
        ])
        for left, right in rib_edges:
            if current_x < left:
                ax.plot(
                    [current_x, left], [y_center, y_center], 
                    color='forestgreen', 
                    linewidth=1.5
                )
            current_x = right
        if current_x < element['big_length']:
            ax.plot(
                [current_x, element['big_length']], [y_center, y_center],
                color='forestgreen', 
                linewidth=1.5
            )
        
        y_offset += element['big_height'] + vertical_gap
    
    ax.set_xlim(0, max(e['big_length'] for e in elements))
    ax.set_ylim(0, y_offset - vertical_gap)
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    return fig

# Streamlit UI
st.title("FIRIKA Insulation Generator")

# Initialize session state for elements if not present
if 'elements' not in st.session_state:
    st.session_state.elements = []

num_elements = st.number_input("Number of elements", 1, 10, 1)
codes = []

for i in range(num_elements):
    code = st.text_input(f"Element {i+1} code", key=f"code_{i}",
                        placeholder="C/02-11/65.35.08/100/EPS/R0")
    codes.append(code)

if st.button("Process Elements"):
    st.session_state.elements.clear()
    for i, code in enumerate(codes):
        if not code.strip():
            st.warning(f"Element {i+1}: Empty code skipped")
            continue
        element = parse_product_code(code)
        if element and element['valid']:
            st.session_state.elements.append(element)
            st.success(f"Element {i+1}: Successfully parsed")
        elif element and not element['valid']:
            st.warning(f"Element {i+1}: No valid rib centers found")

if st.session_state.elements:
    if st.button("Show Visualization"):
        fig = visualize(st.session_state.elements)
        st.pyplot(fig)
        plt.close(fig)  # Prevents memory leaks

    if st.button("Generate DXF"):
        from io import BytesIO  # Ensure this import exists
        try:
            dxf_file = create_dxf(st.session_state.elements)
            buffer = BytesIO()  # Now BytesIO is defined
            dxf_file.saveas(buffer)
            buffer.seek(0)
            
            if len(buffer.getvalue()) == 0:
                st.error("Empty DXF file - no entities created")
            else:
                st.download_button(
                    "Download DXF",
                    buffer.getvalue(),
                    "combined_elements.dxf",
                    "application/dxf"
                )
        except Exception as e:
            st.error(f"DXF generation failed: {str(e)}")