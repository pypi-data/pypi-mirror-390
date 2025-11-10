import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse
import os
import math

# --- SCRIPT CONSTANTS ---
# ... (Questa parte rimane invariata) ...
ARUCO_DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
PAPER_FORMAT = 'A4'
DPI = 300
MARGIN_CM = 1.0

def setup_parser():
    # ... (Questa funzione rimane invariata) ...
    parser = argparse.ArgumentParser(
        description="Generates a print-ready PDF sheet of ArUco markers.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # ... (tutti gli argomenti rimangono invariati) ...
    layout_group = parser.add_mutually_exclusive_group(required=True)
    layout_group.add_argument(
        '-g', '--grid',
        type=int,
        nargs=2,
        metavar=('ROWS', 'COLS'),
        help="Specify the exact grid layout (e.g., 3 2 for 3 rows and 2 columns)."
    )
    layout_group.add_argument(
        '-a', '--auto-fit',
        action='store_true',
        help="Automatically calculate the maximum number of markers that can fit on the page."
    )
    parser.add_argument(
        '--start-id',
        type=int,
        default=0,
        help="The ID of the first marker in the sequence. Default: 0."
    )
    parser.add_argument(
        '--hide-id',
        action='store_true',
        help="If set, the ID label below each marker will not be shown."
    )
    return parser


def cm_to_pixels(cm, dpi):
    # ... (Questa funzione rimane invariata) ...
    return int((cm / 2.54) * dpi)

def create_cell_image(marker_id, marker_size_px, show_id=True):
    # ... (Questa funzione rimane invariata) ...
    # 1. Generate the base ArUco marker image
    marker_img_np = cv2.aruco.generateImageMarker(
        ARUCO_DICTIONARY, marker_id, marker_size_px, borderBits=1
    )
    marker_img = Image.fromarray(marker_img_np).convert('RGB')
    if not show_id:
        return marker_img
    # ... (il resto della funzione rimane invariato) ...
    text_area_height_cm = 1.0  # Fixed 1cm height for the label area
    text_area_height_px = cm_to_pixels(text_area_height_cm, DPI)
    total_height = marker_size_px + text_area_height_px
    composite_img = Image.new('RGB', (marker_size_px, total_height), 'white')
    composite_img.paste(marker_img, (0, 0))
    draw = ImageDraw.Draw(composite_img)
    text = f"ID: {marker_id}"
    try:
        font_size = int(text_area_height_px * 0.6)
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    text_x = (marker_size_px - text_width) / 2
    text_y = marker_size_px + (text_area_height_px - text_height) / 2
    draw.text((text_x, text_y), text, font=font, fill='black')
    return composite_img


# --- MODIFICA CHIAVE QUI ---
def main():
    """Main function to orchestrate the PDF generation."""
    
    # 1. La logica di parsing viene spostata DENTRO la funzione main
    parser = setup_parser()
    args = parser.parse_args()
    
    # Da qui in poi, il codice è lo stesso di prima, perché ora ha accesso all'oggetto 'args'
    print("Starting ArUco sheet generation...")

    # ... (tutta la logica esistente della vecchia funzione main rimane qui) ...
    marker_size_cm = args.size / 10.0
    show_id = not args.hide_id
    
    paper_sizes_cm = {'A4': (21.0, 29.7)}
    page_width_cm, page_height_cm = paper_sizes_cm[PAPER_FORMAT]
    
    printable_width_cm = page_width_cm - (MARGIN_CM * 2)
    printable_height_cm = page_height_cm - (MARGIN_CM * 2)
    
    text_area_height_cm = 1.0 if show_id else 0
    cell_width_cm = marker_size_cm
    cell_height_cm = marker_size_cm + text_area_height_cm

    if args.auto_fit:
        cols = math.floor(printable_width_cm / cell_width_cm)
        rows = math.floor(printable_height_cm / cell_height_cm)
        if cols == 0 or rows == 0:
            print("\n--- ERROR ---")
            print(f"The specified marker size ({args.size}mm) is too large to fit even one marker on an A4 page.")
            return
        print(f"Auto-fit mode: Calculated a maximum grid of {rows} rows and {cols} columns.")
    else: # User-defined grid
        rows, cols = args.grid
        total_content_width_cm = cols * cell_width_cm
        total_content_height_cm = rows * cell_height_cm
        
        if total_content_width_cm > printable_width_cm or total_content_height_cm > printable_height_cm:
            print("\n--- ERROR ---")
            print("The specified grid and marker size exceeds the printable area of an A4 page.")
            print("Please try a smaller grid, a smaller marker size, or use --auto-fit mode.")
            return

    num_markers = rows * cols
    ids_to_print = list(range(args.start_id, args.start_id + num_markers))
    page_width_px = cm_to_pixels(page_width_cm, DPI)
    page_height_px = cm_to_pixels(page_height_cm, DPI)
    marker_size_px = cm_to_pixels(marker_size_cm, DPI)
    sheet = Image.new('RGB', (page_width_px, page_height_px), 'white')
    total_grid_width_px = cols * marker_size_px
    total_grid_height_px = rows * cm_to_pixels(cell_height_cm, DPI)
    gap_x = (page_width_px - total_grid_width_px) / (cols + 1)
    gap_y = (page_height_px - total_grid_height_px) / (rows + 1)
    marker_index = 0
    for r in range(rows):
        for c in range(cols):
            marker_id = ids_to_print[marker_index]
            cell_img = create_cell_image(marker_id, marker_size_px, show_id)
            cell_width_px, cell_height_px = cell_img.size
            pos_x = int(gap_x * (c + 1) + c * marker_size_px)
            pos_y = int(gap_y * (r + 1) + r * cell_height_px)
            print(f"  - Generating marker ID {marker_id}...")
            sheet.paste(cell_img, (pos_x, pos_y))
            marker_index += 1
    id_tag = 'ID' if show_id else 'noID'
    output_filename = f"ArUcoSheet_{rows}x{cols}_{args.size}mm_{id_tag}.pdf"
    try:
        sheet.save(output_filename, "PDF", resolution=DPI)
        print("\nGeneration successful!")
        print(f"PDF file saved as: '{os.path.abspath(output_filename)}'")
    except Exception as e:
        print(f"\nAn error occurred while saving the PDF: {e}")

# --- MODIFICA SEMPLIFICATA QUI ---
if __name__ == '__main__':
    main()