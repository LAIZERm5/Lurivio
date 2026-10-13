import ctypes
import sys
from PySide6.QtCore import Qt, QRect, QTimer, Signal, QAbstractNativeEventFilter
from PySide6.QtGui import QColor, QPen, QPainter
from PySide6.QtWidgets import QWidget
from i18n import tr

# Capture is a frozen image of one monitor. User crops use logical DPI coordinates.
class RegionOverlay(QWidget):
    selected = Signal(object)
    cancelled = Signal()

    def __init__(self, screen, screenshot):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.screen_geometry = screen.geometry()
        self.screenshot = screenshot
        self.origin = None
        self.current = None
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setGeometry(self.screen_geometry)
        self.setMouseTracking(True)

    def selection(self):
        if self.origin is None or self.current is None:
            return QRect()
        return QRect(self.origin, self.current).normalized().intersected(self.rect())

    def paintEvent(self, event):
        p = QPainter(self)
        p.drawPixmap(0, 0, self.screenshot)
        p.fillRect(self.rect(), QColor(0, 0, 0, 95))
        rect = self.selection()
        if not rect.isEmpty():
            p.save()
            p.setClipRect(rect)
            p.drawPixmap(0, 0, self.screenshot)
            p.restore()
            p.setPen(QPen(QColor('#58ADFF'), 2))
            p.drawRect(rect.adjusted(0, 0, -1, -1))
        # Hide instructions while dragging so they cannot obscure the chosen URL.
        if self.origin is None:
            label = QRect(24, 24, min(590, self.width() - 48), 52)
            p.fillRect(label, QColor('#202020'))
            p.setPen(QColor('white'))
            p.drawText(label.adjusted(16, 0, -16, 0), Qt.AlignmentFlag.AlignVCenter,
                       tr('Выделите ссылку или QR мышью   ·   Esc — отмена'))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.position().toPoint()
            self.current = self.origin
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self.cancelled.emit()
            self.close()

    def mouseMoveEvent(self, event):
        if self.origin is not None:
            self.current = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton or self.origin is None:
            return
        self.current = event.position().toPoint()
        rect = self.selection()
        if rect.width() < 12 or rect.height() < 8:
            self.cancelled.emit()
            self.close()
            return
        # Selection is logical pixels; screen pixmap may be device pixels (125–200% DPI).
        ratio = self.screenshot.devicePixelRatio()
        physical = QRect(round(rect.x() * ratio), round(rect.y() * ratio),
                         round(rect.width() * ratio), round(rect.height() * ratio))
        crop = self.screenshot.toImage().copy(physical)
        self.selected.emit(crop)
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            self.close()


