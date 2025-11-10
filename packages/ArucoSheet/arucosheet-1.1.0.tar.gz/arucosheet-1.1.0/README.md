# ArucoSheet

<img src="https://raw.githubusercontent.com/follen99/ArUcoSheet/refs/heads/main/.github/logo.png" style="zoom:50%;" />

A powerful command-line tool to generate highly customizable, print-ready PDF sheets of ArUco markers for computer vision applications.

## Features

-   **Custom Marker Size**: Specify the exact side length of the markers in millimeters.
-   **Flexible Layouts**: Define a precise grid (e.g., 4 rows, 3 columns) for your markers.
-   **Auto-Fit Mode**: Automatically calculate the maximum number of markers that can fit on a standard A4 page.
-   **Sequential ID Generation**: Simply provide a starting ID, and the tool will generate all subsequent markers needed to fill the grid.
-   **Optional ID Labels**: Choose whether to display a clear "ID: X" label beneath each marker for easy identification.
-   **High-Quality PDF Output**: Generates a 300 DPI PDF, perfect for crisp, accurate printing.


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

## Installation

There are two ways to install `ArucoSheet`: via PyPI (recommended for most users) or from source (for developers).

### 1. Recommended: Install via PyPI

This is the simplest and recommended method. It will automatically download the tool and install all required dependencies.

**Prerequisites:**
*   Python 3.7+
*   `pip` (Python's package installer)

Open your terminal and run the following command:

```bash
pip install ArucoSheet
```

This will make the `arucosheet` command available system-wide in your terminal.

**To verify the installation**, run the help command. This should display the tool's help menu with all available options:

```bash
arucosheet --help
```

### 2. Alternative: Install from Source (for Developers)

If you want to contribute to the project, modify the code, or install the very latest (unreleased) version, you can install it directly from the source code.

**Prerequisites:**
*   Python 3.7+
*   `pip`
*   `git`

Follow these steps in your terminal:

```bash
# 1. Clone the repository from GitHub
git clone https://github.com/your-username/ArucoSheet.git

# 2. Navigate into the project directory
cd ArucoSheet

# 3. (Optional but recommended) Create and activate a virtual environment
python -m venv venv
# On Windows:
# .\venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# 4. Install the package in editable mode
pip install -e .
```

The `-e` flag stands for "editable". This is ideal for development, as any changes you make to the source code will be immediately reflected when you run the `arucosheet` command.

## Usage

Once installed, the `arucosheet` command becomes available in your terminal. All functionality is controlled via command-line arguments.

The tool operates in one of two layout modes, and you must choose one:
*   `--auto-fit`: Let the tool calculate the maximum number of markers that can fit on the page.
*   `--grid`: Manually specify the exact number of rows and columns for the layout.

The generated PDF file will be saved in your current working directory.

---

### Example 1: The Easiest Way to Get Markers

**Goal:** Generate a PDF with as many 80mm markers as can fit on an A4 page.

This is the simplest and most common use case. The tool will calculate the optimal grid, start from ID 0, and include ID labels by default.

```bash
arucosheet --size 80 --auto-fit
```
*This will generate a file like `ArucoSheet_3x2_80mm_ID.pdf`.*

### Example 2: Auto-Fit with a Specific Starting ID

**Goal:** Generate a sheet of 80mm markers for a project that requires specific IDs (e.g., for motion capture), starting from ID 10.

```bash
arucosheet --size 80 --auto-fit --start-id 10
```
*The markers on the generated PDF will be numbered 10, 11, 12, and so on.*

### Example 3: Creating a Precise Grid

**Goal:** Generate a PDF with a specific 3x2 grid of smaller, 50mm markers.

Use the `--grid` flag when you need an exact number of markers, regardless of whether more could fit.

```bash
arucosheet --size 50 --grid 3 2
```
*This will create a sheet with exactly 6 markers (3 rows, 2 columns), generating a file named `ArucoSheet_3x2_50mm_ID.pdf`.*

### Example 4: A Denser Layout Without ID Labels

**Goal:** Maximize the number of 60mm markers on a page by removing the space-consuming ID labels.

The `--hide-id` flag is useful when you can identify markers by their pattern alone and want to fit more on a single sheet.

```bash
arucosheet --size 60 --auto-fit --hide-id
```
*This will likely fit more markers vertically compared to the version with labels and generate a file like `ArucoSheet_4x3_60mm_noID.pdf`.*

### Example 5: Getting Help

**Goal:** See all available commands and options directly from the terminal.

The `--help` flag is your built-in guide to all the tool's capabilities.

```bash
arucosheet --help
```

This will display the following helpful message:
```
usage: arucosheet [-h] -s SIZE (-g ROWS COLS | -a) [--start-id START_ID] [--hide-id]

Generates a print-ready PDF sheet of ArUco markers.

optional arguments:
  -h, --help            show this help message and exit
  -s SIZE, --size SIZE  The side length of each marker in millimeters (mm).
  -g ROWS COLS, --grid ROWS COLS
                        Specify the exact grid layout (e.g., 3 2 for 3 rows and 2 columns).
  -a, --auto-fit        Automatically calculate the maximum number of markers that can fit on the page.
  --start-id START_ID   The ID of the first marker in the sequence. Default: 0.
  --hide-id             If set, the ID label below each marker will not be shown.```
