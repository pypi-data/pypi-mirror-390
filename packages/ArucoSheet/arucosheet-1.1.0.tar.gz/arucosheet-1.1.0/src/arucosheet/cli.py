import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import argparse
import os
import math

# --- SCRIPT CONSTANTS ---
ARUCO_DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
PAPER_FORMAT = 'A4'
DPI = 300
MARGIN_CM = 1.0

def setup_parser():
    """Configures the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Generates a print-ready PDF sheet of ArUco markers.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '-s', '--size',
        type=int,
        required=True,
        help="The side length of each marker in millimeters (mm)."
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help="Specify the output path for the generated PDF. \nCan be a directory (e.g., 'my_pdfs/') or a full file path (e.g., 'my_pdfs/custom.pdf')."
    )
    
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
    """Converts centimeters to pixels based on the given DPI."""
    return int((cm / 2.54) * dpi)

def create_cell_image(marker_id, marker_size_px, show_id=True):
    """
    Generates a composite image: the marker and, optionally, its ID label.
    """
    marker_img_np = cv2.aruco.generateImageMarker(
        ARUCO_DICTIONARY, marker_id, marker_size_px, borderBits=1
    )
    marker_img = Image.fromarray(marker_img_np).convert('RGB')

    if not show_id:
        return marker_img

    text_area_height_cm = 1.0
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

def main():
    """Main function to orchestrate the PDF generation."""
    parser = setup_parser()
    args = parser.parse_args()
    
    print("Starting ArUco sheet generation...")

    marker_size_cm = args.size / 10.0
    show_id = not args.hide_id
    
    paper_sizes_cm = {'A4': (21.0, 29.7)}
    page_w_cm, page_h_cm = paper_sizes_cm[PAPER_FORMAT]
    
    printable_width_cm = page_w_cm - (MARGIN_CM * 2)
    printable_height_cm = page_h_cm - (MARGIN_CM * 2)
    
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
    else:
        rows, cols = args.grid
        total_content_width_cm = cols * cell_width_cm
        total_content_height_cm = rows * cell_height_cm
        
        if total_content_width_cm > printable_width_cm or total_content_height_cm > printable_height_cm:
            print("\n--- ERROR ---")
            print("The specified grid and marker size exceeds the printable area of an A4 page.")
            print("Please try a smaller grid, a smaller marker size, or use --auto-fit mode.")
            return
        
    id_tag = 'ID' if not args.hide_id else 'noID'
    default_filename = f"ArUcoSheet_{rows}x{cols}_{args.size}mm_{id_tag}.pdf"

    if args.output:
        # L'utente ha fornito un percorso di output
        if args.output.lower().endswith('.pdf'):
            # L'utente ha specificato un percorso completo di file
            output_path = args.output
            # Assicurati che la directory genitore esista
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
        else:
            # L'utente ha specificato solo una directory
            output_dir = args.output
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, default_filename)
    else:
        # Nessun percorso specificato, salva nella directory corrente
        output_path = default_filename

    num_markers = rows * cols
    ids_to_print = list(range(args.start_id, args.start_id + num_markers))
    
    page_w_px = cm_to_pixels(page_w_cm, DPI)
    page_h_px = cm_to_pixels(page_h_cm, DPI)
    marker_size_px = cm_to_pixels(marker_size_cm, DPI)
    
    sheet = Image.new('RGB', (page_w_px, page_h_px), 'white')

    total_grid_width_px = cols * marker_size_px
    total_grid_height_px = rows * cm_to_pixels(cell_height_cm, DPI)
    gap_x = (page_w_px - total_grid_width_px) / (cols + 1)
    gap_y = (page_h_px - total_grid_height_px) / (rows + 1)

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
    # output_filename = f"ArUcoSheet_{rows}x{cols}_{args.size}mm_{id_tag}.pdf"
    try:
        sheet.save(output_path, "PDF", resolution=DPI)
        print("\nGeneration successful!")
        print(f"PDF file saved as: '{os.path.abspath(output_path)}'")
    except Exception as e:
        print(f"\nAn error occurred while saving the PDF: {e}")

if __name__ == '__main__':
    main()