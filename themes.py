"""Five original skins inspired by the supplied Nami references and macOS."""
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QRadialGradient, QPen
from PySide6.QtWidgets import QFrame, QWidget

THEMES = {
 'aurora': dict(name='Aurora', desc='Пастель, коралл и холодное стекло', bg='#EFF0F5', panel='#F9FAFD', side='#F3EEF1', text='#30313B', muted='#696A79', line='#DFDCE5', accent='#B84249', button='#B84249', button_text='#FFFFFF', tint='#FCE7E7', green='#24754B', radius=18, glow1='#FAD5CE', glow2='#D5E8EF'),
 'graphite': dict(name='Graphite', desc='Тёмная студия с коралловым акцентом', bg='#242830', panel='#2B3039', side='#22262E', text='#F4F5F8', muted='#B3BBCB', line='#454B58', accent='#FF8986', button='#FF8986', button_text='#272B32', tint='#453539', green='#8FDDB0', radius=16, glow1='#303743', glow2='#28313B'),
 'paper': dict(name='Paper', desc='Бумага, тонкая сетка и шалфей', bg='#F3EDDF', panel='#FFFCF4', side='#F1E7D0', text='#343A30', muted='#736650', line='#D7C8AA', accent='#3D664B', button='#3D664B', button_text='#FFFFFF', tint='#E5EDDF', green='#3D664B', radius=4, glow1='#F5EACF', glow2='#EAE9DA'),
 'mac_light': dict(name='macOS Light', desc='Светлый жемчуг и системный синий', bg='#EFF1F7', panel='#FFFFFF', side='#E9EDF5', text='#23283A', muted='#626B7D', line='#D9DFEC', accent='#2465CE', button='#2465CE', button_text='#FFFFFF', tint='#E6EEFF', green='#24754B', radius=16, glow1='#E6E8FC', glow2='#DCEFF4'),
 'mac_midnight': dict(name='macOS Midnight', desc='Ночной индиго и лавандовый акцент', bg='#1C1F2D', panel='#252A3B', side='#191E2D', text='#F4F3FB', muted='#B8BED2', line='#414960', accent='#B5A6FF', button='#B5A6FF', button_text='#201B37', tint='#37334F', green='#92DABA', radius=16, glow1='#302D4D', glow2='#1F3449'),
}


def stylesheet(key):
    t = THEMES[key]
    return f'''
QWidget {{ color: {t['text']}; font-family: "Segoe UI"; font-size: 14px; background: transparent; }}
QDialog#shortcutRecording {{ background: {t['panel']}; }}
QFrame#shell {{ border: 1px solid {t['line']}; border-radius: {t['radius']}px; }}
QFrame#sidebar {{ background: {t['side']}; border-right: 1px solid {t['line']}; border-top-left-radius: {t['radius']}px; border-bottom-left-radius: {t['radius']}px; }}
QFrame#panel, QFrame#themeCard {{ background: {t['panel']}; border: 1px solid {t['line']}; border-radius: {max(4,t['radius']-4)}px; }}
QFrame#themeCard[selected="true"] {{ border: 2px solid {t['accent']}; }}
QLabel#title {{ font-size: 29px; font-weight: 700; }}
QLabel#brand {{ font-size: 23px; font-weight: 700; }}
QLabel#section {{ font-size: 17px; font-weight: 600; }}
QLabel#muted, QLabel#micro {{ color: {t['muted']}; }}
QLabel#micro {{ font-size: 12px; letter-spacing: 1px; }}
QLabel#badge {{ background: {t['tint']}; color: {t['green']}; border-radius: 10px; padding: 8px 12px; font-size: 12px; font-weight: 700; }}
QLabel#hero {{ font-size: 33px; font-weight: 700; }}
QLabel#status {{ background: {t['tint']}; border-radius: 8px; padding: 12px; }}
QPushButton {{ background: {t['panel']}; min-height: 42px; padding: 0 16px; border: 1px solid {t['line']}; border-radius: 9px; font-weight: 600; }}
QPushButton:hover {{ background: {t['tint']}; border-color: {t['accent']}; }}
QPushButton:focus, QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {{ border: 2px solid {t['accent']}; }}
QPushButton#primary {{ background: {t['button']}; color: {t['button_text']}; border-color: {t['button']}; }}
QPushButton#primary:hover {{ border: 2px solid {t['text']}; }}
QPushButton:disabled {{ color: {t['muted']}; background: {t['side']}; border-color: {t['line']}; }}
QPushButton#nav {{ text-align: left; background: transparent; border: 1px solid transparent; min-height: 46px; padding-left: 16px; }}
QPushButton#nav:checked {{ background: {t['panel']}; border: 1px solid {t['accent']}; color: {t['accent']}; }}
QLineEdit, QComboBox {{ background: {t['panel']}; border: 1px solid {t['line']}; border-radius: 9px; min-height: 44px; padding: 0 12px; }}
QComboBox QAbstractItemView {{ background: {t['panel']}; color: {t['text']}; selection-background-color: {t['tint']}; border: 1px solid {t['line']}; }}
QPlainTextEdit {{ background: {t['side']}; border: 1px solid {t['line']}; border-radius: 9px; padding: 10px; font-family: Consolas; }}
QCheckBox {{ spacing: 10px; min-height: 30px; }}
QCheckBox::indicator {{ width: 18px; height: 18px; }}
QScrollArea {{ border: none; }}
QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {t['line']}; border-radius: 4px; min-height: 32px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}
QMenu {{ background: {t['panel']}; border: 1px solid {t['line']}; padding: 6px; }}
QMenu::item {{ padding: 9px 18px; }}
QMenu::item:selected {{ background: {t['tint']}; }}
QToolTip {{ background: {t['panel']}; color: {t['text']}; border: 1px solid {t['line']}; }}
'''

class Background(QFrame):
    def __init__(self):
        super().__init__()
        self.theme = 'aurora'
        self.setObjectName('shell')

    def paintEvent(self, event):
        t = THEMES[self.theme]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path_rect = QRectF(self.rect()).adjusted(.5, .5, -.5, -.5)
        from PySide6.QtGui import QPainterPath
        path = QPainterPath()
        path.addRoundedRect(path_rect, t['radius'], t['radius'])
        p.setClipPath(path)
        p.fillRect(self.rect(), QColor(t['bg']))
        for x, y, color in [(0, 0, t['glow1']), (self.width(), self.height(), t['glow2'])]:
            gradient = QRadialGradient(x, y, self.width() * .9)
            gradient.setColorAt(0, QColor(color))
            fade = QColor(color); fade.setAlpha(0)
            gradient.setColorAt(1, fade)
            p.fillRect(self.rect(), gradient)
        if self.theme == 'paper':
            p.setPen(QPen(QColor('#EAE2CE'), .5))
            for x in range(0, self.width(), 24):
                p.drawLine(x, 0, x, self.height())
            for y in range(0, self.height(), 24):
                p.drawLine(0, y, self.width(), y)
        p.setClipping(False)
        p.setPen(QPen(QColor(t['line']), 1))
        p.drawPath(path)

class Swatch(QWidget):
    def __init__(self, theme):
        super().__init__()
        self.theme = theme
        self.setFixedHeight(72)

    def paintEvent(self, event):
        t = THEMES[self.theme]
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(t['glow1']))
        gradient.setColorAt(1, QColor(t['bg']))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(gradient)
        p.drawRoundedRect(self.rect(), 8, 8)
        p.setBrush(QColor(t['side']))
        p.drawRoundedRect(QRectF(10, 12, 44, 49), 5, 5)
        p.setBrush(QColor(t['panel']))
        p.drawRoundedRect(QRectF(64, 12, self.width()-74, 49), 5, 5)
        # Miniature Windows-style controls, matching the real native titlebar.
        p.setPen(QPen(QColor(t['muted']), 1))
        right = self.width() - 15
        p.drawLine(right-34, 21, right-28, 21)
        p.drawRect(right-22, 17, 6, 6)
        p.drawLine(right-10, 17, right-4, 23)
        p.drawLine(right-4, 17, right-10, 23)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(t['accent']))
        p.drawRoundedRect(QRectF(74, 34, min(95, self.width()-90), 14), 4, 4)

# Draw unambiguous checked AND unchecked states in every light/dark skin.
from PySide6.QtWidgets import QCheckBox, QStyleOptionButton, QStyle, QApplication
class ThemedCheckBox(QCheckBox):
    def paintEvent(self, event):
        super().paintEvent(event)
        key = QApplication.instance().property('lurivioTheme') or 'aurora'
        t = THEMES.get(key, THEMES['aurora'])
        option = QStyleOptionButton(); self.initStyleOption(option)
        indicator = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, option, self)
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        checked = self.isChecked()
        color = QColor(t['accent'] if checked else t['muted'])
        if not self.isEnabled():
            color.setAlpha(120)
        p.setPen(QPen(color, 1.3)); p.setBrush(QColor(t['button'] if checked else t['panel']))
        box = QRectF(indicator).adjusted(.8,.8,-.8,-.8)
        p.drawRoundedRect(box,4,4)
        if checked:
            p.setPen(QPen(QColor(t['button_text']),2.0,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin))
            from PySide6.QtCore import QPointF
            p.drawLine(QPointF(box.left()+3,box.center().y()),QPointF(box.left()+6,box.bottom()-4))
            p.drawLine(QPointF(box.left()+6,box.bottom()-4),QPointF(box.right()-3,box.top()+4))
