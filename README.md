# BBox Coords – QGIS Plugin

**BBox Coords** is a QGIS plugin that draws the bounding box (extent) of a selected feature and displays its coordinates directly on the map canvas, using the layer coordinate reference system (CRS).  
Both the bounding box and the coordinate text are fully configurable (colors, line width, font size, background, etc.).

This plugin is intended for cartographic inspection, spatial analysis, and scientific workflows where explicit visualization of feature extents is required.

---

## Features

- Computes the bounding box of the selected feature
- Displays bounding box as a rectangle on the map canvas
- Shows bounding box coordinates (xmin, ymin, xmax, ymax)
- Uses the **layer CRS** (no reprojection of coordinates)
- Fully configurable styling:
  - Bounding box line color, width, and fill
  - Text color, font family, font size
  - Text background and frame
  - Number of decimal places
- Copies coordinates to clipboard (optional)
- Compatible with **QGIS 3.26 LTR**

---

## Installation

### From ZIP (manual installation)

1. Download the plugin ZIP file
2. Open QGIS
3. Go to **Plugins → Manage and Install Plugins**
4. Select **Install from ZIP**
5. Choose the downloaded ZIP file
6. Enable the plugin

### From QGIS Plugin Repository
*(Available once the plugin is published)*

1. Open **Plugins → Manage and Install Plugins**
2. Search for **BBox Coords**
3. Install and enable

---

## Usage

1. Activate the plugin using the toolbar button **“BBox Coords: Activate/Deactivate”**
2. Select a feature from a vector layer
3. The bounding box and its coordinates will be displayed on the map
4. Open **“BBox Coords: Settings”** to customize appearance and options

> If multiple features are selected, the plugin uses the first selected feature.

---

## Coordinate Reference System (CRS)

- Coordinates are reported **in the CRS of the layer**
- No transformation is applied to the coordinate values
- The annotation position is correctly transformed to the map CRS if on-the-fly reprojection is enabled

---

## Authors and Affiliation

**Authors**
- Félix González  
- José Antonio González  
- José María De la Rosa  

**Affiliation**  
Institute of Natural Resources and Agrobiology of Seville (IRNAS-CSIC)  
Spanish National Research Council (CSIC)

---

## License

This plugin is released under the **GNU General Public License v3 (GPL-3.0)**.

---

## Citation

If you use this plugin in academic work, please cite it as software:

> González, F., González, J. A., & De la Rosa, J. M. (2026).  
> *BBox Coords: QGIS plugin for bounding box visualization*.  
> IRNAS-CSIC.

(A DOI will be provided via Zenodo after release.)

---

## Acknowledgements

This plugin was developed using the QGIS Python API (PyQGIS) and is intended to support open and reproducible geospatial research.

---

#
