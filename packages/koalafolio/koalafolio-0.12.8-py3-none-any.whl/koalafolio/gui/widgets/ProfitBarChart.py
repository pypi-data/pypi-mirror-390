from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLabel, QCheckBox, QApplication, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal, Qt, QRect, QSize, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
import sys

BAR_KEYS = ["profit", "tax_profit", "fees", "fiat_profit"]
BAR_COLORS = {
    "profit": QColor(60, 180, 75),      # green
    "tax_profit": QColor(255, 225, 25), # yellow
    "fees": QColor(230, 25, 75),        # red
    "fiat_profit": QColor(0, 130, 200), # blue
}
BAR_LABELS = {
    "profit": "Profit",
    "tax_profit": "Tax Profit",
    "fees": "Fees",
    "fiat_profit": "Fiat Profit"
}

class ProfitBarChartModel:
    def __init__(self, year_data):
        """
        year_data: list of dicts, each dict has keys from BAR_KEYS and a 'year' key
        Example: [{'year': 2021, 'profit': 100, 'tax_profit': 80, 'fees': -10, 'fiat_profit': 50}, ...]
        """
        self.year_data = year_data

    def years(self):
        return [d['year'] for d in self.year_data]

    def data(self, year, key):
        for d in self.year_data:
            if d['year'] == year:
                return d.get(key, 0)
        return 0

    def rowCount(self):
        return len(self.year_data)

    def columnCount(self):
        return len(BAR_KEYS)

class QProfitBarChartView(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.selected_start = 0
        self.selected_end = 0
        self.enabled_keys = {k: True for k in BAR_KEYS}
        self.setMinimumHeight(200)
        self.setContentsMargins(0,0,0,0)
        self.margin = 20
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setSelection(self, start, end):
        self.selected_start = start
        self.selected_end = end
        self.update()

    def setEnabledKey(self, key, enabled):
        self.enabled_keys[key] = enabled
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        years = self.model.years()
        n_years = self.selected_end - self.selected_start + 1
        if n_years < 1:
            return

        # Find max/min for scaling
        max_val = 0
        min_val = 0
        for i in range(self.selected_start, self.selected_end + 1):
            year = years[i]
            for key in BAR_KEYS:
                if self.enabled_keys[key]:
                    max_val = max(max_val, self.model.data(year, key))
                    min_val = min(min_val, self.model.data(year, key))
        min_val = abs(min_val)
        if max_val <= 1:
            max_val = 1
        if min_val <= 1:
            min_val = 1
                 
        # Layout
        margin = self.margin
        bar_area = QRect(margin, margin, rect.width() - 2*margin, rect.height() - 3*margin)
        center_offset_factor = max_val/ (max_val + min_val)
        if center_offset_factor > 0.9:
            center_offset_factor = 0.9
        elif center_offset_factor < 0.1:
            center_offset_factor = 0.1
        # calculate zero line based on center offset factor
        zero_y = bar_area.top() + int(bar_area.height() * center_offset_factor + margin)
    
        # Bar width logic
        if n_years == 1:
            # 1 year: 4 bars, separated, span the whole width
            bar_width = bar_area.width() // (len(BAR_KEYS)*2)
            gap = bar_width
            x0 = bar_area.left() + (bar_area.width() - (len(BAR_KEYS)*bar_width + (len(BAR_KEYS)-1)*gap)) // 2
            year = years[self.selected_start]
            for idx, key in enumerate(BAR_KEYS):
                if not self.enabled_keys[key]:
                    continue
                val = self.model.data(year, key)
                color = BAR_COLORS[key]
                x = x0 + idx * (bar_width + gap)
                self._drawBar(painter, x, zero_y, bar_width, bar_area.height(), val, max_val, min_val, center_offset_factor, color)
            # Draw full year centered above the bars
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            painter.drawText(
                bar_area.left(), bar_area.top() - 20, bar_area.width(), 20,
                Qt.AlignHCenter | Qt.AlignVCenter, str(year)
            )
        else:
            # Multiple years: group of 4 bars per year, small gap between bars, big gap between years
            group_width = bar_area.width() // n_years
            bar_width = group_width // (len(BAR_KEYS) + 1)
            bar_gap = 0
            group_gap = group_width - (bar_width*len(BAR_KEYS))
            for i in range(self.selected_start, self.selected_end + 1):
                year = years[i]
                group_x = bar_area.left() + (i-self.selected_start)*group_width + group_gap//2
                bar_xs = []
                for j, key in enumerate(BAR_KEYS):
                    if not self.enabled_keys[key]:
                        continue
                    val = self.model.data(year, key)
                    color = BAR_COLORS[key]
                    x = group_x + j*bar_width
                    bar_xs.append(x)
                    self._drawBar(painter, x, zero_y, bar_width, bar_area.height(), val, max_val, min_val, center_offset_factor, color)
                # Draw year label above the group, centered
                if bar_xs:
                    first_bar = bar_xs[0]
                    last_bar = bar_xs[-1] + bar_width
                    center_x = (first_bar + last_bar) // 2
                    painter.setPen(Qt.black)
                    painter.setFont(QFont("Arial", 10, QFont.Bold))
                    painter.drawText(center_x - 12, bar_area.top() - 8 - (margin//2), 30, 16, Qt.AlignCenter, str(year))

        # Draw horizontal zero line
        pen = QPen(Qt.gray)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(bar_area.left(), zero_y, bar_area.right(), zero_y)

    def _drawBar(self, painter, x, zero_y, bar_width, bar_area_height, val, max_val, min_val, center_offset_factor, color):
        # Draw a single bar, positive up, negative down
        positive_height = bar_area_height * center_offset_factor
        negative_height = bar_area_height * (1 - center_offset_factor)
        if val >= 0:
            h = int((abs(val)/max_val)*positive_height)
            y = zero_y - h
        else:
            y = zero_y
            h = int((abs(val)/min_val)*negative_height)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(x, y, bar_width, h)
        
        # Draw value label
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        value_str = str(val)
        text_rect = QRect(x, y - 18 if val >= 0 else y + h + 2, bar_width, 16)
        painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignVCenter, value_str)

class QProfitBarChartLegend(QWidget):
    toggled = pyqtSignal(str, bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkboxes = {}
        self._alignment_mode = 'grouped'
        self._spacer_items = []
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0,0,0,0)
        for key in BAR_KEYS:
            cb = QCheckBox(BAR_LABELS[key])
            cb.setChecked(True)
            cb.setStyleSheet(f"QCheckBox::indicator {{ background: {BAR_COLORS[key].name()}; }}")
            cb.toggled.connect(lambda checked, k=key: self.toggled.emit(k, checked))
            self._layout.addWidget(cb)
            self.checkboxes[key] = cb
        self._layout.addStretch()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # <-- Add this line

    def setChecked(self, key, checked):
        self.checkboxes[key].setChecked(checked)

    def setAlignmentMode(self, mode, bar_area_rect=None, bar_positions=None):
        # mode: 'single' or 'grouped'
        # bar_area_rect: QRect of the bar area (from QProfitBarChartView)
        # bar_positions: list of x positions for each bar (for 'single' mode)
        self._alignment_mode = mode
        # Remove all spacers
        for item in self._spacer_items:
            self._layout.removeItem(item)
        self._spacer_items.clear()
        # Remove all widgets
        for cb in self.checkboxes.values():
            self._layout.removeWidget(cb)
        # Remove stretch
        while self._layout.count() > 0:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        # Re-add widgets with spacers
        if mode == 'single' and bar_area_rect and bar_positions:
            # Add spacers to align checkboxes with bars
            total_width = bar_area_rect.width()
            last_x = bar_area_rect.left()
            for i, key in enumerate(BAR_KEYS):
                x = bar_positions[i]
                spacer = QWidget()
                spacer.setFixedWidth(max(0, x - last_x))
                self._layout.addWidget(spacer)
                self._spacer_items.append(self._layout.itemAt(self._layout.count()-1))
                self._layout.addWidget(self.checkboxes[key])
                last_x = x + self.checkboxes[key].sizeHint().width()
            # Add stretch at end
            self._layout.addStretch()
        else:
            # Centered legend
            self._layout.addStretch()
            for key in BAR_KEYS:
                self._layout.addWidget(self.checkboxes[key])
            self._layout.addStretch()
        self.update()

class RangeSlider(QWidget):
    startValueChanged = pyqtSignal(int)
    endValueChanged = pyqtSignal(int)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self._min = 0
        self._max = 10
        self._start = 0
        self._end = 0
        self._handle_radius = 8
        self._dragging = None  # 'start', 'end', 'range', or None
        self._drag_offset = 0
        self._drag_range_start = 0
        self._drag_range_end = 0
        self.setMinimumHeight(30)
        self.setMouseTracking(True)

    def setMinimum(self, value):
        self._min = value
        self.update()

    def setMaximum(self, value):
        self._max = value
        self.update()

    def setValue(self, value_tuple):
        self._start, self._end = value_tuple
        self.update()

    def setStart(self, value):
        self._start = max(self._min, min(value, self._end))
        self.startValueChanged.emit(self._start)
        self.update()

    def setEnd(self, value):
        self._end = min(self._max, max(value, self._start))
        self.endValueChanged.emit(self._end)
        self.update()

    def start(self):
        return self._start

    def end(self):
        return self._end

    def _posToValue(self, pos):
        slider_left = self._handle_radius
        slider_right = self.width() - self._handle_radius
        rel = (pos - slider_left) / (slider_right - slider_left)
        rel = min(max(rel, 0), 1)
        return int(round(self._min + rel * (self._max - self._min)))

    def _valueToPos(self, value):
        slider_left = self._handle_radius
        slider_right = self.width() - self._handle_radius
        rel = (value - self._min) / (self._max - self._min) if self._max > self._min else 0
        return int(slider_left + rel * (slider_right - slider_left))

    def mousePressEvent(self, event):
        x = event.x()
        start_pos = self._valueToPos(self._start)
        end_pos = self._valueToPos(self._end)
        singleYearMode = (self._start == self._end)
        # If both handles are at the same position, treat any click on the handle/bar as a range drag
        if singleYearMode:
            if abs(x - start_pos) < self._handle_radius + 6:
                self._dragging = 'range'
                self._drag_offset = x
                self._drag_range_start = self._start
                self._drag_range_end = self._end
                return
        # If not in single year mode, check for handle clicks
        # Check if user clicked on left or right handle
        if abs(x - start_pos) < self._handle_radius + 2:
            self._dragging = 'start'
            return
        if abs(x - end_pos) < self._handle_radius + 2:
            self._dragging = 'end'
            return
        # Check if user clicked on the range bar (between handles)
        if start_pos + self._handle_radius < x < end_pos - self._handle_radius:
            self._dragging = 'range'
            self._drag_offset = x
            self._drag_range_start = self._start
            self._drag_range_end = self._end
            return
        # Clicked left of left handle: move left handle
        if x < start_pos - self._handle_radius:
            new_start = self._posToValue(x)
            # Clamp so start does not go past end
            new_start = min(new_start, self._end)
            self.setStart(new_start)
            self._dragging = None
            return
        # Clicked right of right handle: move right handle
        if x > end_pos + self._handle_radius:
            new_end = self._posToValue(x)
            # Clamp so end does not go before start
            new_end = max(new_end, self._start)
            self.setEnd(new_end)
            self._dragging = None
            return
        # If we reach here, no handle was clicked, so reset dragging
        self._dragging = None

    def mouseMoveEvent(self, event):
        if self._dragging == 'start':
            value = self._posToValue(event.x())
            self.setStart(value)
            if self._start > self._end:
                self.setEnd(self._start)
        elif self._dragging == 'end':
            value = self._posToValue(event.x())
            self.setEnd(value)
            if self._end < self._start:
                self.setStart(self._end)
        elif self._dragging == 'range':
            # Calculate how much the mouse moved in value units
            delta_px = event.x() - self._drag_offset
            slider_left = self._handle_radius
            slider_right = self.width() - self._handle_radius
            px_per_val = (slider_right - slider_left) / (self._max - self._min) if self._max > self._min else 1
            delta_val = int(round(delta_px / px_per_val))
            range_width = self._drag_range_end - self._drag_range_start
            # Special case: if handles are at the same position, move both together as a single handle
            if range_width == 0:
                new_pos = self._drag_range_start + delta_val
                # Clamp to min/max
                new_pos = max(self._min, min(self._max, new_pos))
                self.setStart(new_pos)
                self.setEnd(new_pos)
            else:
                new_start = self._drag_range_start + delta_val
                new_end = self._drag_range_end + delta_val
                # Clamp to min/max
                if new_start < self._min:
                    new_start = self._min
                    new_end = new_start + range_width
                if new_end > self._max:
                    new_end = self._max
                    new_start = new_end - range_width
                self.setStart(new_start)
                self.setEnd(new_end)
        self.update()

    def mouseReleaseEvent(self, event):
        self._dragging = None

    def paintEvent(self, event):
        painter = QPainter(self)
        slider_left = self._handle_radius
        slider_right = self.width() - self._handle_radius
        y = self.height() // 2

        # Draw track
        painter.setPen(QPen(Qt.gray, 3))
        painter.drawLine(slider_left, y, slider_right, y)

        # Draw selected range (bar)
        start_pos = self._valueToPos(self._start)
        end_pos = self._valueToPos(self._end)
        painter.setPen(QPen(Qt.blue, 5))
        painter.drawLine(start_pos, y, end_pos, y)

        # Draw handles
        painter.setBrush(Qt.white)
        painter.setPen(QPen(Qt.black, 1))
        painter.drawEllipse(QPoint(start_pos, y), self._handle_radius, self._handle_radius)
        painter.drawEllipse(QPoint(end_pos, y), self._handle_radius, self._handle_radius)

    def sizeHint(self):
        return QSize(200, 30)

class QProfitBarChartSlider(QWidget):
    selectionChanged = pyqtSignal(int, int)
    def __init__(self, years, parent=None):
        super().__init__(parent)
        self.years = years
        self.start = 0
        self.end = 0
        self.setMinimumHeight(60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # New buttons for both handles
        self.range_left_btn = QPushButton("≪")
        self.left_left_btn = QPushButton("<")
        self.left_right_btn = QPushButton(">")
        self.right_left_btn = QPushButton("<")
        self.right_right_btn = QPushButton(">")
        self.range_right_btn = QPushButton("≫")
        for btn in [self.range_left_btn,
                    self.left_left_btn, 
                    self.left_right_btn, 
                    self.right_left_btn, 
                    self.right_right_btn,
                    self.range_right_btn]:
            btn.setFixedWidth(30)

        self.left_left_btn.clicked.connect(self.move_left_handle_left)
        self.left_right_btn.clicked.connect(self.move_left_handle_right)
        self.right_left_btn.clicked.connect(self.move_right_handle_left)
        self.right_right_btn.clicked.connect(self.move_right_handle_right)
        self.range_left_btn.clicked.connect(self.move_both_handles_left)
        self.range_right_btn.clicked.connect(self.move_both_handles_right)

        self.range_slider = RangeSlider(Qt.Horizontal)
        self.range_slider.setMinimum(0)
        self.range_slider.setMaximum(len(years)-1)
        self.range_slider.setValue((0, 0))
        self.range_slider.startValueChanged.connect(self.rangeChanged)
        self.range_slider.endValueChanged.connect(self.rangeChanged)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.range_left_btn)
        layout.addWidget(self.left_left_btn)
        layout.addWidget(self.left_right_btn)
        layout.addWidget(self.range_slider)
        layout.addWidget(self.right_left_btn)
        layout.addWidget(self.right_right_btn)
        layout.addWidget(self.range_right_btn)
        self.setLayout(layout)

    def rangeChanged(self, value):
        self.start = self.range_slider.start()
        self.end = self.range_slider.end()
        self.selectionChanged.emit(self.start, self.end)
        self.update()

    # Move left handle left
    def move_left_handle_left(self) -> bool:
        if self.range_slider.start() > self.range_slider._min:
            self.range_slider.setStart(self.range_slider.start() - 1)
            return True
        return False

    # Move left handle right
    def move_left_handle_right(self) -> bool:
        if self.range_slider.start() < self.range_slider.end():
            self.range_slider.setStart(self.range_slider.start() + 1)
            return True
        return False

    # Move right handle left
    def move_right_handle_left(self) -> bool:
        if self.range_slider.end() > self.range_slider.start():
            self.range_slider.setEnd(self.range_slider.end() - 1)
            return True
        return False

    # Move right handle right
    def move_right_handle_right(self) -> bool:
        if self.range_slider.end() < self.range_slider._max:
            self.range_slider.setEnd(self.range_slider.end() + 1)
            return True
        return False
            
    def move_both_handles_left(self) -> bool:
        if self.move_left_handle_left():
            self.move_right_handle_left()
            return True
        return False
        
    def move_both_handles_right(self) -> bool:
        if self.move_right_handle_right():
            self.move_left_handle_right()
            return True
        return False

    def paintEvent(self, event):
        # Draw year labels under the slider
        painter = QPainter(self)
        rect = self.rect()
        n = len(self.years)
        if n == 0:
            return
        slider_rect = self.range_slider.geometry()
        x0 = slider_rect.left()
        x1 = slider_rect.right()
        for i, year in enumerate(self.years):
            x = x0 + (x1-x0)*i/(n-1) if n > 1 else (x0+x1)//2
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", 8))
            painter.drawText(int(x)-8, slider_rect.bottom()+15, str(year)[-2:])

class QProfitBarChartWidget(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.slider = QProfitBarChartSlider(self.model.years())
        # Set range to maximum (last year)
        last_idx = len(self.model.years()) - 1
        self.slider.range_slider.setStart(0)
        self.slider.range_slider.setEnd(last_idx)
        self.slider.start = 0
        self.slider.end = last_idx
        self.bar_chart = QProfitBarChartView(self.model)
        self.bar_chart.setSelection(0, last_idx)  # <-- Ensure bar chart uses initial range
        self.slider.selectionChanged.connect(self.onSelectionChanged)
        self.legend = QProfitBarChartLegend()
        self.legend.toggled.connect(self.bar_chart.setEnabledKey)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(4)  # <-- Add or adjust this line (try 0, 2, or 4)
        layout.addWidget(self.slider)
        layout.addWidget(self.bar_chart, 1)
        layout.addWidget(self.legend)
        self.setLayout(layout)
        # Call with last year as default
        self.onSelectionChanged(0, last_idx)

    def onSelectionChanged(self, start, end):
        self.bar_chart.setSelection(start, end)
        # Align legend if only 1 year is selected
        if end - start == 0:
            # Calculate bar positions for alignment
            bar_area = self.bar_chart.rect()
            margin = 20
            bar_area_rect = QRect(margin, margin, bar_area.width() - 2*margin, bar_area.height() - 3*margin)
            n_bars = len(BAR_KEYS)
            bar_width = bar_area_rect.width() // (n_bars*2)
            gap = bar_width
            x0 = bar_area_rect.left() + (bar_area_rect.width() - (n_bars*bar_width + (n_bars-1)*gap)) // 2
            bar_positions = [x0 + i*(bar_width+gap) for i in range(n_bars)]
            self.legend.setAlignmentMode('single', bar_area_rect, bar_positions)
        else:
            self.legend.setAlignmentMode('grouped')

# Add this function before the test GUI block
def apply_debug_stylesheet(widget):
    widget.slider.setStyleSheet("""
        QFrame, QWidget {
            background: #e0f7fa;
            border: 2px solid #00838f;
        }
    """)
    widget.bar_chart.setStyleSheet("""
        QFrame, QWidget {
            background: #fffde7;
            border: 2px solid #fbc02d;
        }
    """)
    widget.setStyleSheet("""
        QFrame, QWidget {
            background: #5d559c;
            border: 2px solid #6a1b9a;
        }
    """)
    widget.legend.setStyleSheet("""
        QCheckBox {
            font-size: 12px;
            color: #ffffff;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        QCheckBox::indicator:checked {
            background: #ffeb3b;
        }
        QCheckBox::indicator:unchecked {
            background: #bdbdbd;
        }
    """)

# Test GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Example data
    data = [
        {'year': 2021, 'profit': 100, 'tax_profit': 80, 'fees': -10, 'fiat_profit': 50},
        {'year': 2022, 'profit': 150, 'tax_profit': 120, 'fees': -20, 'fiat_profit': 70},
        {'year': 2023, 'profit': -50, 'tax_profit': -30, 'fees': -150, 'fiat_profit': -20},
        {'year': 2024, 'profit': 200, 'tax_profit': 180, 'fees': -15, 'fiat_profit': 100},
    ]
    model = ProfitBarChartModel(data)
    w = QProfitBarChartWidget(model)
    w.resize(700, 400)
    apply_debug_stylesheet(w)
    w.show()
    sys.exit(app.exec_())