# -*- coding: utf-8 -*-
"""
Created on Thu May  1 15:49:15 2025
@author: hah
Improved: Dynamic element list with quantities, board packing, side‑by‑side board layout.
"""

import streamlit as st
import ezdxf
from ezdxf import units
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FormatStrFormatter
import tempfile
import os
import logging

############### User Activity Log #################
logging.basicConfig(
    filename='./user_activity.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def log_action(action, details=None):
    user = "User"
    log_message = f"{user} - {action}"
    if details:
        log_message += f" - {str(details)}"
    logging.info(log_message)
###################################################

# Page config
st.set_page_config(page_icon="LogoTab.png", page_title="FirikaWebapp")

# Hardcoded login (unchanged)
USERNAME = "FischerRista"
PASSWORD = "FischerRista"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.image('IMAGE.JPG')
    st.title("Anmeldung")
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")
    if st.button("Anmeldung"):
        log_action("Login pressed")
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Ungültiger Benutzername oder Kennwort")
    st.stop()

###############################################################################
# Helper functions (mostly unchanged, with minor corrections)

def adjust_h_for_fire_resistance(Cb, Ct, fire_resistance):
    if fire_resistance == 'REI60':
        return Cb - 1, Ct - 1
    elif fire_resistance == 'REI90':
        return Cb - 1.5, Ct - 1.5
    else:
        return Cb, Ct

def get_element_length(element_length_type, num_ribs, Length):
    if element_length_type == '1m':
        return 1000.0
    elif element_length_type == '0.5m':
        return 500
    elif element_length_type == 'compact':
        return num_ribs * 100
    elif element_length_type == 'Lenght':
        return Length
    else:
        return 0

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
        1: [64.5],
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
    # Length in mm
    first_center = 64.5
    last_center_max = Length - 35.5
    cm = Length // 10
    spacings = []
    max_ribs = 0

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
            spacings = [100, 100, 200, 100, 100, 100]
        elif num_ribs == 6:
            spacings = [100, 200, 100, 200, 100]
        elif num_ribs == 5:
            spacings = [200, 200, 200, 100]
        elif num_ribs == 4:
            spacings = [200, 300, 200]
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
            spacings = [200, 300]
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
        return []  # too short

    if num_ribs < 2 or num_ribs > max_ribs:
        return []

    centers = [first_center]
    current = first_center
    for s in spacings:
        current += s
        centers.append(round(current, 1))
    if centers[-1] > last_center_max + 1e-9:
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

def parse_code(code):
    """Parse a product code and return a template dictionary with geometry."""
    parts = code.split('/')
    if len(parts) < 6:
        return None, "Ungültiges Format. Erwartet: C/02-11/65.35.08/100/EPS/R0"

    rib_part = parts[1]
    rib_info = rib_part.split('-')
    if len(rib_info) != 2:
        return None, f"Ungültige Rippeninformation: {rib_part}"

    try:
        num_ribs = int(rib_info[0])
        if num_ribs < 1 or num_ribs > 10:
            return None, "Anzahl Rippen muss zwischen 1 und 10 liegen."
    except ValueError:
        return None, f"Ungültige Anzahl Rippen: {rib_info[0]}"

    try:
        h_rib = int(rib_info[1])
        if h_rib not in [11, 13, 15, 17, 19]:
            return None, "Rippenhöhe muss 11,13,15,17,19 cm sein."
    except ValueError:
        return None, f"Ungültige Rippenhöhe: {rib_info[1]}"

    covers_part = parts[2]
    covers_info = covers_part.split('.')
    if len(covers_info) < 3:
        return None, f"Ungültige Cover-Information: {covers_part}"

    try:
        Ct_mm = int(covers_info[0])
        Cb_mm = int(covers_info[1])
    except ValueError:
        return None, f"Ungültige Betondeckung: {covers_info[0]} oder {covers_info[1]}"

    try:
        element_length_code = int(parts[3])
    except ValueError:
        return None, f"Ungültiger Längencode: {parts[3]}"

    insulation_type = parts[4]
    if insulation_type not in ['EPS', 'XPS', 'SW']:
        return None, f"Ungültiger Dämmtyp: {insulation_type}"

    fire_resistance = parts[5]
    insulation = 'EPS/XPS' if insulation_type in ['EPS', 'XPS'] else 'SW'
    if insulation == 'SW' and fire_resistance != 'REI120':
        return None, "SW-Dämmung muss REI120 haben."
    elif insulation == 'EPS/XPS' and fire_resistance not in ['R0', 'REI60', 'REI90']:
        return None, f"Ungültiger Feuerwiderstand für EPS/XPS: {fire_resistance}"

    Ct = Ct_mm / 10.0
    Cb = Cb_mm / 10.0
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

    if element_length_type == 'Lenght':
        Length_custom = element_length_code * 10
    else:
        Length_custom = 0
    element_length_mm = get_element_length(element_length_type, num_ribs, Length_custom)

    big_box_length = element_length_mm + 10.0
    big_box_height = (Cb + Ct + h_rib) * 10 + 20
    if num_ribs < 5:
        small_box_width = 18 if insulation == 'SW' else 17
    else:
        small_box_width = 18.5 if insulation == 'SW' else 17.5
    small_box_height = h_rib * 10 + 1.5

    rib_centers = calculate_rib_centers(element_length_type, num_ribs, element_length_mm)
    if not rib_centers:
        return None, "Keine gültigen Rippenpositionen (Abstandsregeln nicht erfüllt)."

    template = {
        'width': big_box_length,
        'height': big_box_height,
        'rib_centers': rib_centers,
        'small_box_width': small_box_width,
        'small_box_height': small_box_height,
        'Cb': Cb,
        'code': code
    }
    return template, None

# Packing algorithm: returns list of placements
def pack_elements(templates, board_width, board_height):
    """
    templates: list of element template dicts (in order, with repetitions for quantity)
    board_width, board_height in mm.
    Returns list of dicts: {'element': template, 'board': board_index, 'x': x, 'y': y}
    """
    placements = []
    board_index = 0
    row_y = 0
    row_x = 0
    row_height = None  # height of current row (all elements in a row must have same height)

    for elem in templates:
        w = elem['width']
        h = elem['height']

        # Check if element fits in board at all
        if w > board_width or h > board_height:
            raise ValueError(f"Element {elem['code']} ist breiter oder höher als die Platte!")

        placed = False
        while not placed:
            # If we have a row height set, check if current element has different height
            if row_height is not None and row_height != h:
                # Start a new row
                new_y = row_y + row_height
                if new_y + h > board_height:
                    # Need a new board
                    board_index += 1
                    row_y = 0
                    row_x = 0
                    row_height = None
                    continue
                else:
                    row_y = new_y
                    row_x = 0
                    row_height = h

            # Check horizontal fit
            if row_x + w > board_width:
                # Start a new row (same board)
                new_y = row_y + row_height if row_height is not None else row_y + h
                if new_y + h > board_height:
                    # Need a new board
                    board_index += 1
                    row_y = 0
                    row_x = 0
                    row_height = None
                    continue
                else:
                    row_y = new_y
                    row_x = 0
                    row_height = h

            # Place element
            placements.append({
                'element': elem,
                'board': board_index,
                'x': row_x,
                'y': row_y
            })
            row_x += w
            if row_height is None:
                row_height = h
            placed = True

    return placements

# Visualization function: draws all boards side by side
def visualize_boards(placements, board_width, board_height):
    """
    placements: list from pack_elements
    board_width, board_height in mm
    Returns matplotlib figure.
    """
    if not placements:
        return None

    num_boards = max(p['board'] for p in placements) + 1
    gap = 250  # mm between boards

    # Compute total width and height needed
    total_width = num_boards * (board_width + gap) - gap
    total_height = board_height

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, total_width)
    ax.set_ylim(0, total_height)

    for board_idx in range(num_boards):
        # Offset for this board
        x_offset = board_idx * (board_width + gap)

        # Draw board outline (dashed)
        rect = Rectangle((x_offset, 0), board_width, board_height,
                         fill=None, edgecolor='black', linestyle=':', linewidth=1.5)
        ax.add_patch(rect)

        # Get placements for this board
        board_placements = [p for p in placements if p['board'] == board_idx]
        for p in board_placements:
            elem = p['element']
            dx = x_offset + p['x']
            dy = p['y']

            # Draw main box (element bounding box)
            ax.add_patch(Rectangle((dx, dy), elem['width'], elem['height'],
                                   fill=None, edgecolor='blue', linewidth=2))

            # Draw ribs
            y_initial = dy + (elem['Cb'] * 10 + 10 + 0.75)  # same as before
            y_center = y_initial + (elem['small_box_height'] / 2)
            rib_edges = []
            for center_x in elem['rib_centers']:
                x1 = dx + center_x - elem['small_box_width'] / 2
                x2 = dx + center_x + elem['small_box_width'] / 2
                ax.add_patch(Rectangle((x1, y_initial), elem['small_box_width'], elem['small_box_height'],
                                       fill=None, edgecolor='red', linewidth=2))
                rib_edges.append((x1, x2))

            # Draw connections (green lines)
            rib_edges_sorted = sorted(rib_edges, key=lambda x: x[0])
            current_pos = dx
            connection_segments = []
            for rib_left, rib_right in rib_edges_sorted:
                if current_pos < rib_left:
                    connection_segments.append((current_pos, rib_left))
                current_pos = rib_right
            if current_pos < dx + elem['width']:
                connection_segments.append((current_pos, dx + elem['width']))

            for start, end in connection_segments:
                ax.plot([start, end], [y_center, y_center], color='green', linestyle='-', linewidth=1.5)

    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlabel("Breite (mm)")
    ax.set_ylabel("Höhe (mm)")

    # Add corner markers (optional)
    # not necessary

    plt.tight_layout()
    return fig

# DXF generation: draws all boards side by side with dashed outlines
def create_dxf_boards(placements, board_width, board_height):
    doc = ezdxf.new(dxfversion='R2010', setup=True)
    doc.units = units.MM
    msp = doc.modelspace()

    # Define dashed line type (if not already)
    # Using existing 'DASHED' or create one
    # For simplicity, we'll use line with linetype 'DASHED' (which is standard)
    # But we need to ensure it exists; ezdxf has DASHED in the default linetypes for R2010

    num_boards = max(p['board'] for p in placements) + 1
    gap = 250  # mm

    for board_idx in range(num_boards):
        x_offset = board_idx * (board_width + gap)

        # Draw board outline as dashed polyline
        points = [(x_offset, 0),
                  (x_offset + board_width, 0),
                  (x_offset + board_width, board_height),
                  (x_offset, board_height),
                  (x_offset, 0)]
        msp.add_lwpolyline(points, close=True, dxfattribs={'linetype': 'DASHED'})

        # Get placements for this board
        board_placements = [p for p in placements if p['board'] == board_idx]
        for p in board_placements:
            elem = p['element']
            dx = x_offset + p['x']
            dy = p['y']

            # Draw main box
            msp.add_lwpolyline(
                [(dx, dy), (dx + elem['width'], dy),
                 (dx + elem['width'], dy + elem['height']),
                 (dx, dy + elem['height']), (dx, dy)],
                close=True
            )

            # Add product code text (at bottom-left, like before)
            text_x = dx + 50
            text_y = dy - 20
            msp.add_text(elem['code'], dxfattribs={
                'height': 10,
                'insert': (text_x, text_y),
            })

            # Draw ribs
            y_initial = dy + (elem['Cb'] * 10 + 10 - 0.75)  # using -0.75 as in original DXF
            y_center = y_initial + (elem['small_box_height'] / 2)
            rib_edges = []
            for center_x in elem['rib_centers']:
                x1 = dx + center_x - elem['small_box_width'] / 2
                x2 = dx + center_x + elem['small_box_width'] / 2
                msp.add_lwpolyline(
                    [(x1, y_initial), (x2, y_initial),
                     (x2, y_initial + elem['small_box_height']),
                     (x1, y_initial + elem['small_box_height']),
                     (x1, y_initial)],
                    close=True
                )
                rib_edges.append((x1, x2))

            # Draw connections
            rib_edges_sorted = sorted(rib_edges, key=lambda x: x[0])
            current_pos = dx
            connection_segments = []
            for rib_left, rib_right in rib_edges_sorted:
                if current_pos < rib_left:
                    connection_segments.append((current_pos, rib_left))
                current_pos = rib_right
            if current_pos < dx + elem['width']:
                connection_segments.append((current_pos, dx + elem['width']))
            for start, end in connection_segments:
                msp.add_line((start, y_center), (end, y_center))

    return doc

###############################################################################
# Streamlit UI

st.title('DXF-Generator für FIRIKA Dämmung (mit Plattenanordnung)')

# Board dimensions
board_width = st.number_input('Plattenbreite (mm)', min_value=1000, value=1200, step=50)
board_height = st.number_input('Plattenhöhe (mm)', min_value=1000, value=2400, step=50)

# Initialize session state for element list if not present
if 'element_entries' not in st.session_state:
    st.session_state.element_entries = [{'code': '', 'quantity': 1}]

# Function to add a new row
def add_row():
    st.session_state.element_entries.append({'code': '', 'quantity': 1})

# Function to remove a row
def remove_row(index):
    if len(st.session_state.element_entries) > 1:
        st.session_state.element_entries.pop(index)

# Display the dynamic list
st.subheader("Elemente und Stückzahlen")
for i, entry in enumerate(st.session_state.element_entries):
    cols = st.columns([4, 1, 1])
    with cols[0]:
        new_code = st.text_input(f"Code {i+1}", value=entry['code'], key=f"code_{i}")
    with cols[1]:
        new_qty = st.number_input(f"Menge {i+1}", min_value=1, value=entry['quantity'], step=1, key=f"qty_{i}")
    with cols[2]:
        if st.button("Entfernen", key=f"remove_{i}"):
            remove_row(i)
            st.rerun()
    # Update session state
    st.session_state.element_entries[i]['code'] = new_code
    st.session_state.element_entries[i]['quantity'] = new_qty

st.button("Element hinzufügen", on_click=add_row)

# Buttons for visualization and DXF
if st.button('Platten visualisieren'):
    log_action("Visualize boards pressed")

    # Parse all entries, build a flat list of templates (with repetitions)
    templates = []
    errors = []
    for entry in st.session_state.element_entries:
        code = entry['code'].strip()
        qty = entry['quantity']
        if not code:
            errors.append("Ein Code fehlt.")
            continue
        template, err = parse_code(code)
        if err:
            errors.append(f"Fehler bei Code '{code}': {err}")
            continue
        # Repeat according to quantity
        for _ in range(qty):
            templates.append(template)

    if errors:
        for e in errors:
            st.error(e)
    elif not templates:
        st.warning("Keine gültigen Elemente eingegeben.")
    else:
        try:
            placements = pack_elements(templates, board_width, board_height)
            fig = visualize_boards(placements, board_width, board_height)
            if fig:
                st.pyplot(fig)
            else:
                st.warning("Keine Platzierungen generiert.")
        except Exception as e:
            st.error(f"Fehler beim Packen: {str(e)}")

# DXF Export
st.subheader("DXF-Export")
if st.button('DXF-Datei generieren'):
    log_action("Generate DXF pressed")

    # Same parsing and packing as above
    templates = []
    errors = []
    for entry in st.session_state.element_entries:
        code = entry['code'].strip()
        qty = entry['quantity']
        if not code:
            errors.append("Ein Code fehlt.")
            continue
        template, err = parse_code(code)
        if err:
            errors.append(f"Fehler bei Code '{code}': {err}")
            continue
        for _ in range(qty):
            templates.append(template)

    if errors:
        for e in errors:
            st.error(e)
    elif not templates:
        st.warning("Keine gültigen Elemente eingegeben.")
    else:
        try:
            placements = pack_elements(templates, board_width, board_height)
            doc = create_dxf_boards(placements, board_width, board_height)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.dxf')
            doc.saveas(tmp.name)
            tmp.close()
            with open(tmp.name, 'rb') as f:
                dxf_data = f.read()
            st.download_button(
                label='Download DXF-Datei',
                data=dxf_data,
                file_name='Dämmung_mit_Platten.dxf',
                mime='application/dxf'
            )
            st.success("DXF erfolgreich generiert!")
            os.unlink(tmp.name)
        except Exception as e:
            st.error(f"DXF-Generierung fehlgeschlagen: {str(e)}")