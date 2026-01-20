
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QPushButton, QColorDialog, QSpinBox, QDoubleSpinBox,
    QLineEdit, QCheckBox, QLabel
)
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsSettings


class ColorButton(QPushButton):
    def __init__(self, initial="#ff0000", parent=None):
        super().__init__(parent)
        self._color = QColor(initial)
        self.clicked.connect(self.pick)
        self._update_label()

    def pick(self):
        c = QColorDialog.getColor(self._color, self.parentWidget(), "Elegir color")
        if c.isValid():
            self._color = c
            self._update_label()

    def _update_label(self):
        self.setText(self._color.name())

    def color_hex(self):
        return self._color.name()


class BBoxCoordsSettingsDialog(QDialog):
    SETTINGS_GROUP = "bbox_coords"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BBox Coords - Ajustes")
        self.settings = QgsSettings()

        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        form.addRow(QLabel("<b>Estilo del bounding box</b>"))

        self.bbox_line_color = ColorButton(self._get("bbox_line_color", "#ff0000"))
        form.addRow("Color línea", self.bbox_line_color)

        self.bbox_line_width = QSpinBox()
        self.bbox_line_width.setRange(1, 20)
        self.bbox_line_width.setValue(int(self._get("bbox_line_width", 2)))
        form.addRow("Grosor línea", self.bbox_line_width)

        self.bbox_fill_color = ColorButton(self._get("bbox_fill_color", "#ff0000"))
        form.addRow("Color relleno", self.bbox_fill_color)

        self.bbox_fill_alpha = QSpinBox()
        self.bbox_fill_alpha.setRange(0, 255)
        self.bbox_fill_alpha.setValue(int(self._get("bbox_fill_alpha", 40)))
        form.addRow("Alpha relleno (0-255)", self.bbox_fill_alpha)

        form.addRow(QLabel("<b>Estilo del texto</b>"))

        self.text_color = ColorButton(self._get("text_color", "#000000"))
        form.addRow("Color texto", self.text_color)

        self.text_font_family = QLineEdit(self._get("text_font_family", "Arial"))
        form.addRow("Fuente", self.text_font_family)

        self.text_font_size_pt = QDoubleSpinBox()
        self.text_font_size_pt.setRange(6.0, 72.0)
        self.text_font_size_pt.setDecimals(1)
        self.text_font_size_pt.setValue(float(self._get("text_font_size_pt", "12")))
        form.addRow("Tamaño (pt)", self.text_font_size_pt)

        self.decimals = QSpinBox()
        self.decimals.setRange(0, 12)
        self.decimals.setValue(int(self._get("decimals", 6)))
        form.addRow("Decimales", self.decimals)

        form.addRow(QLabel("<b>Caja del texto</b>"))

        self.text_bg_enabled = QCheckBox()
        self.text_bg_enabled.setChecked(self._get_bool("text_bg_enabled", True))
        form.addRow("Fondo activo", self.text_bg_enabled)

        self.text_bg_color = ColorButton(self._get("text_bg_color", "#ffffff"))
        form.addRow("Color fondo", self.text_bg_color)

        self.text_bg_alpha = QSpinBox()
        self.text_bg_alpha.setRange(0, 255)
        self.text_bg_alpha.setValue(int(self._get("text_bg_alpha", 180)))
        form.addRow("Alpha fondo (0-255)", self.text_bg_alpha)

        self.text_frame_enabled = QCheckBox()
        self.text_frame_enabled.setChecked(self._get_bool("text_frame_enabled", True))
        form.addRow("Marco activo", self.text_frame_enabled)

        self.text_frame_color = ColorButton(self._get("text_frame_color", "#000000"))
        form.addRow("Color marco", self.text_frame_color)

        self.text_frame_width = QSpinBox()
        self.text_frame_width.setRange(0, 10)
        self.text_frame_width.setValue(int(self._get("text_frame_width", 1)))
        form.addRow("Grosor marco", self.text_frame_width)

        form.addRow(QLabel("<b>Opciones</b>"))

        self.copy_to_clipboard = QCheckBox()
        self.copy_to_clipboard.setChecked(self._get_bool("copy_to_clipboard", True))
        form.addRow("Copiar coordenadas al portapapeles", self.copy_to_clipboard)

        self.show_messagebar = QCheckBox()
        self.show_messagebar.setChecked(self._get_bool("show_messagebar", True))
        form.addRow("Mostrar resumen en barra de mensajes", self.show_messagebar)

        btns = QHBoxLayout()
        layout.addLayout(btns)

        btn_ok = QPushButton("Guardar")
        btn_cancel = QPushButton("Cancelar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)

        btns.addStretch(1)
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)

    def accept(self):
        self._set("bbox_line_color", self.bbox_line_color.color_hex())
        self._set("bbox_line_width", self.bbox_line_width.value())
        self._set("bbox_fill_color", self.bbox_fill_color.color_hex())
        self._set("bbox_fill_alpha", self.bbox_fill_alpha.value())

        self._set("text_color", self.text_color.color_hex())
        self._set("text_font_family", self.text_font_family.text().strip() or "Arial")
        self._set("text_font_size_pt", str(self.text_font_size_pt.value()))
        self._set("decimals", self.decimals.value())

        self._set("text_bg_enabled", self.text_bg_enabled.isChecked())
        self._set("text_bg_color", self.text_bg_color.color_hex())
        self._set("text_bg_alpha", self.text_bg_alpha.value())

        self._set("text_frame_enabled", self.text_frame_enabled.isChecked())
        self._set("text_frame_color", self.text_frame_color.color_hex())
        self._set("text_frame_width", self.text_frame_width.value())

        self._set("copy_to_clipboard", self.copy_to_clipboard.isChecked())
        self._set("show_messagebar", self.show_messagebar.isChecked())

        super().accept()

    def _key(self, name):
        return f"{self.SETTINGS_GROUP}/{name}"

    def _get(self, name, default):
        return self.settings.value(self._key(name), default)

    def _get_bool(self, name, default):
        v = self.settings.value(self._key(name), default)
        if isinstance(v, bool):
            return v
        return str(v).lower() in ("1", "true", "yes", "y", "t")

    def _set(self, name, value):
        self.settings.setValue(self._key(name), value)
