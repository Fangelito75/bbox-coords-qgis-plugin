
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QColor, QIcon, QTextDocument
from qgis.PyQt.QtWidgets import QAction

from qgis.core import (
    QgsSettings,
    QgsWkbTypes,
    QgsTextAnnotation,
    QgsPointXY,
    QgsProject,
    QgsCoordinateTransform,
)
from qgis.gui import QgsRubberBand, QgsMapCanvasAnnotationItem

from .settings_dialog import BBoxCoordsSettingsDialog


class BBoxCoordsPlugin:
    SETTINGS_GROUP = "bbox_coords"

    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()

        self.action_toggle = None
        self.action_settings = None

        self.enabled = False
        self._current_layer = None

        self._rubber = None
        self._annotation_item = None

    def initGui(self):
        icon = QIcon(self._plugin_icon_path())

        self.action_toggle = QAction(icon, "BBox Coords: Activar/Desactivar", self.iface.mainWindow())
        self.action_toggle.setCheckable(True)
        self.action_toggle.triggered.connect(self.toggle)

        self.action_settings = QAction(icon, "BBox Coords: Ajustes", self.iface.mainWindow())
        self.action_settings.triggered.connect(self.open_settings)

        self.iface.addToolBarIcon(self.action_toggle)
        self.iface.addToolBarIcon(self.action_settings)
        self.iface.addPluginToMenu("&BBox Coords", self.action_toggle)
        self.iface.addPluginToMenu("&BBox Coords", self.action_settings)

    def unload(self):
        self._disconnect_all()
        self._clear_overlays()

        if self.action_toggle:
            self.iface.removeToolBarIcon(self.action_toggle)
            self.iface.removePluginMenu("&BBox Coords", self.action_toggle)

        if self.action_settings:
            self.iface.removeToolBarIcon(self.action_settings)
            self.iface.removePluginMenu("&BBox Coords", self.action_settings)

    # -------------------- Actions --------------------
    def toggle(self, checked):
        self.enabled = bool(checked)
        if self.enabled:
            self._connect_all()
            self._maybe_update_from_selection()
            self.iface.messageBar().pushInfo("BBox Coords", "Activado. Selecciona una geometría.")
        else:
            self._disconnect_all()
            self._clear_overlays()
            self.iface.messageBar().pushInfo("BBox Coords", "Desactivado.")

    def open_settings(self):
        dlg = BBoxCoordsSettingsDialog(self.iface.mainWindow())
        if dlg.exec_() and self.enabled:
            self._maybe_update_from_selection()

    # -------------------- Signals --------------------
    def _connect_all(self):
        self.iface.currentLayerChanged.connect(self._on_current_layer_changed)
        self._on_current_layer_changed(self.iface.activeLayer())

    def _disconnect_all(self):
        try:
            self.iface.currentLayerChanged.disconnect(self._on_current_layer_changed)
        except Exception:
            pass
        self._disconnect_layer_selection()

    def _on_current_layer_changed(self, layer):
        self._disconnect_layer_selection()
        self._current_layer = layer

        if not self.enabled:
            return

        if layer is None or not hasattr(layer, "selectionChanged"):
            self._clear_overlays()
            return

        layer.selectionChanged.connect(self._on_selection_changed)
        self._maybe_update_from_selection()

    def _disconnect_layer_selection(self):
        if self._current_layer is None:
            return
        try:
            self._current_layer.selectionChanged.disconnect(self._on_selection_changed)
        except Exception:
            pass

    def _on_selection_changed(self, selected, deselected, clearAndSelect):
        if self.enabled:
            self._maybe_update_from_selection()

    # -------------------- Core --------------------
    def _maybe_update_from_selection(self):
        layer = self.iface.activeLayer()
        if layer is None or not hasattr(layer, "selectedFeatures"):
            self._clear_overlays()
            return

        feats = layer.selectedFeatures()
        if not feats:
            self._clear_overlays()
            return

        geom = feats[0].geometry()
        if geom is None or geom.isEmpty():
            self._clear_overlays()
            return

        extent = geom.boundingBox()
        xmin, ymin, xmax, ymax = extent.xMinimum(), extent.yMinimum(), extent.xMaximum(), extent.yMaximum()
        crs_auth = layer.crs().authid() if layer.crs().isValid() else "CRS desconocido"

        decimals = int(self._get_int("decimals", 6))
        fmt = f"{{:.{decimals}f}}"

        text = (
            f"Layer CRS: {crs_auth}\n"
            f"xmin: {fmt.format(xmin)}\n"
            f"ymin: {fmt.format(ymin)}\n"
            f"xmax: {fmt.format(xmax)}\n"
            f"ymax: {fmt.format(ymax)}"
        )

        self._draw_bbox(extent)
        self._draw_text(layer, extent, text)

        if self._get_bool("copy_to_clipboard", True):
            try:
                self.iface.mainWindow().clipboard().setText(text)
            except Exception:
                pass

        if self._get_bool("show_messagebar", True):
            self.iface.messageBar().pushInfo(
                "BBox Coords",
                f"xmin={fmt.format(xmin)}, ymin={fmt.format(ymin)}, xmax={fmt.format(xmax)}, ymax={fmt.format(ymax)}"
            )

    def _ensure_rubber(self):
        if self._rubber is None:
            self._rubber = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
            self._rubber.setLineStyle(Qt.SolidLine)

    def _draw_bbox(self, extent):
        self._ensure_rubber()

        line_color = QColor(self._get_str("bbox_line_color", "#ff0000"))
        fill_color = QColor(self._get_str("bbox_fill_color", "#ff0000"))
        fill_alpha = self._get_int("bbox_fill_alpha", 40)
        width = self._get_int("bbox_line_width", 2)

        fill_color.setAlpha(max(0, min(255, int(fill_alpha))))

        self._rubber.setStrokeColor(line_color)
        self._rubber.setFillColor(fill_color)
        self._rubber.setWidth(int(width))

        self._rubber.reset(QgsWkbTypes.PolygonGeometry)

        p1 = QgsPointXY(extent.xMinimum(), extent.yMinimum())
        p2 = QgsPointXY(extent.xMaximum(), extent.yMinimum())
        p3 = QgsPointXY(extent.xMaximum(), extent.yMaximum())
        p4 = QgsPointXY(extent.xMinimum(), extent.yMaximum())

        self._rubber.addPoint(p1, False)
        self._rubber.addPoint(p2, False)
        self._rubber.addPoint(p3, False)
        self._rubber.addPoint(p4, True)
        self._rubber.show()

    def _clear_annotation(self):
        if self._annotation_item is not None:
            try:
                self.canvas.scene().removeItem(self._annotation_item)
            except Exception:
                pass
        self._annotation_item = None

    def _draw_text(self, layer, extent, text_plain):
        self._clear_annotation()

        # Build QTextDocument (QGIS 3.26 compatible)
        font_family = self._get_str("text_font_family", "Arial")
        font_size_pt = float(self._get_str("text_font_size_pt", "12"))
        text_color = self._get_str("text_color", "#000000")

        import html
        escaped = html.escape(text_plain).replace("\n", "<br/>")

        html_text = (
            f"<div style='font-family:{font_family};"
            f"font-size:{font_size_pt}pt;"
            f"color:{text_color};'>"
            f"{escaped}</div>"
        )

        doc = QTextDocument()
        doc.setHtml(html_text)

        ann = QgsTextAnnotation()
        ann.setDocument(doc)

        # Fixed map position in MAP CRS. Transform from layer CRS to canvas destination CRS if needed.
        ann.setHasFixedMapPosition(True)

        pt_layer = QgsPointXY(extent.xMinimum(), extent.yMaximum())
        try:
            dest_crs = self.canvas.mapSettings().destinationCrs()
            if layer.crs().isValid() and dest_crs.isValid() and layer.crs() != dest_crs:
                xform = QgsCoordinateTransform(layer.crs(), dest_crs, QgsProject.instance())
                pt_map = xform.transform(pt_layer)
            else:
                pt_map = pt_layer
        except Exception:
            pt_map = pt_layer

        # IMPORTANT: In QGIS 3.26 setMapPosition is on the annotation, not on the canvas item
        ann.setMapPosition(pt_map)

        item = QgsMapCanvasAnnotationItem(ann, self.canvas)

        # Frame/background (best-effort; API differs slightly across versions)
        try:
            bg_enabled = self._get_bool("text_bg_enabled", True)
            bg = QColor(self._get_str("text_bg_color", "#ffffff"))
            bg.setAlpha(max(0, min(255, int(self._get_int("text_bg_alpha", 180)))))
            item.setFrameBackgroundColor(bg if bg_enabled else QColor(255, 255, 255, 0))
        except Exception:
            pass

        try:
            frame_enabled = self._get_bool("text_frame_enabled", True)
            fc = QColor(self._get_str("text_frame_color", "#000000"))
            if frame_enabled:
                item.setFrameColor(fc)
                item.setFrameSize(int(self._get_int("text_frame_width", 1)))
            else:
                item.setFrameSize(0)
        except Exception:
            pass

        self._annotation_item = item
        item.update()

    def _clear_overlays(self):
        if self._rubber is not None:
            try:
                self._rubber.reset(QgsWkbTypes.PolygonGeometry)
            except Exception:
                pass
        self._clear_annotation()

    def _plugin_icon_path(self):
        import os
        return os.path.join(os.path.dirname(__file__), "icon.png")

    # -------------------- Settings wrappers --------------------
    def _settings(self):
        return QgsSettings()

    def _key(self, name):
        return f"{self.SETTINGS_GROUP}/{name}"

    def _get_str(self, name, default):
        return self._settings().value(self._key(name), default, type=str)

    def _get_int(self, name, default):
        return int(self._settings().value(self._key(name), default))

    def _get_bool(self, name, default):
        v = self._settings().value(self._key(name), default)
        if isinstance(v, bool):
            return v
        return str(v).lower() in ("1", "true", "yes", "y", "t")
