# ArucoSheet

A powerful command-line tool to generate highly customizable, print-ready PDF sheets of ArUco markers for computer vision applications.

## Features

-   **Custom Marker Size**: Specify the exact side length of the markers in millimeters.
-   **Flexible Layouts**: Define a precise grid (e.g., 4 rows, 3 columns) for your markers.
-   **Auto-Fit Mode**: Automatically calculate the maximum number of markers that can fit on a standard A4 page.
-   **Sequential ID Generation**: Simply provide a starting ID, and the tool will generate all subsequent markers needed to fill the grid.
-   **Optional ID Labels**: Choose whether to display a clear "ID: X" label beneath each marker for easy identification.
-   **High-Quality PDF Output**: Generates a 300 DPI PDF, perfect for crisp, accurate printing.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/ArucoSheet.git
    cd ArucoSheet
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    



## Usage

`ArucoSheet` is a command-line tool. All functionality is controlled via arguments passed to the script in your terminal.

You must choose one of two layout modes:
*   `--auto-fit`: Let the tool calculate the maximum number of markers that can fit.
*   `--grid`: Manually specify the exact number of rows and columns.

---

### Example 1: The Easiest Way to Get Markers

**Goal:** Generate a PDF with as many 80mm markers as can fit on an A4 page.

This is the simplest and most common use case. The tool will calculate the optimal grid, start from ID 0, and include ID labels.

```bash
python ArucoSheet.py --size 80 --auto-fit
```
*This will generate a file like `ArucoSheet_3x2_80mm_ID.pdf`.*

### Example 2: Auto-Fit with a Specific Starting ID

**Goal:** Generate a sheet of 80mm markers for a project that requires specific IDs (e.g., for motion capture), starting from ID 10.

```bash
python ArucoSheet.py --size 80 --auto-fit --start-id 10
```
*The markers on the generated PDF will be numbered 10, 11, 12, and so on.*

### Example 3: Creating a Precise Grid

**Goal:** Generate a PDF with a specific 3x2 grid of smaller, 50mm markers.

Use the `--grid` flag when you need an exact number of markers, regardless of whether more could fit.

```bash
python ArucoSheet.py --size 50 --grid 3 2
```
*This will create a sheet with exactly 6 markers (3 rows, 2 columns), generating a file named `ArucoSheet_3x2_50mm_ID.pdf`.*

### Example 4: A Denser Layout Without ID Labels

**Goal:** Maximize the number of 60mm markers on a page by removing the space-consuming ID labels.

The `--hide-id` flag is useful when you can identify markers by their pattern alone and want to fit more on a single sheet.

```bash
python ArucoSheet.py --size 60 --auto-fit --hide-id
```
*This will likely fit more markers vertically compared to the version with labels and generate a file like `ArucoSheet_4x3_60mm_noID.pdf`.*

### Example 5: Getting Help

**Goal:** See all available commands and options directly from the terminal.

The `--help` flag is your built-in guide to all the tool's capabilities.

```bash
python ArucoSheet.py --help
```

This will display the following helpful message:
```
usage: ArucoSheet.py [-h] -s SIZE (-g ROWS COLS | -a) [--start-id START_ID] [--hide-id]

Generates a print-ready PDF sheet of ArUco markers.

optional arguments:
  -h, --help            show this help message and exit
  -s SIZE, --size SIZE  The side length of each marker in millimeters (mm).
  -g ROWS COLS, --grid ROWS COLS
                        Specify the exact grid layout (e.g., 3 2 for 3 rows and 2 columns).
  -a, --auto-fit        Automatically calculate the maximum number of markers that can fit on the page.
  --start-id START_ID   The ID of the first marker in the sequence. Default: 0.
  --hide-id             If set, the ID label below each marker will not be shown.
```
