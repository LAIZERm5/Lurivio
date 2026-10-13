"""Click-to-record keyboard or modifier+mouse shortcut. No text typing."""
from PySide6.QtCore import Qt, QEvent, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QApplication
from hotkeys import parse_hotkey, parse_binding, modifier_bits, mouse_binding
from i18n import tr, manager

class RecordingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = None
        self.setObjectName('shortcutRecording')
        self.setWindowTitle(tr('Запись сочетания'))
        self.setMinimumWidth(480)
        self.setModal(True)
        layout = QVBoxLayout(self);layout.setContentsMargins(24,24,24,24);layout.setSpacing(16)
        title=QLabel(tr('Нажмите нужное сочетание'));title.setStyleSheet('font-size:20px;font-weight:600;');layout.addWidget(title)
        help_text=QLabel(tr('Клавиатура: например Ctrl+Alt+K.\nМышь: удерживайте Ctrl, Alt, Shift или Win и нажмите\nколёсико либо боковую кнопку внутри этого окна.\nEsc — отмена. ЛКМ, ПКМ и прокрутка не назначаются.'))
        help_text.setWordWrap(True);layout.addWidget(help_text)
        self.status=QLabel(tr('Ожидаю нажатия…'));self.status.setWordWrap(True);layout.addWidget(self.status)
        cancel=QPushButton(tr('Отмена'));cancel.setMinimumHeight(44)
        # Avoid Enter accepting an empty dialog through a default button.
        cancel.setAutoDefault(False);cancel.setDefault(False);cancel.clicked.connect(self.reject);layout.addWidget(cancel)
        QApplication.instance().installEventFilter(self)
        self.finished.connect(lambda _:QApplication.instance().removeEventFilter(self))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def take(self, text):
        try:
            canonical, _, _ = parse_binding(text)
        except ValueError as error:
            self.status.setText(tr(str(error)));return False
        self.value=canonical;self.accept();return True

    def eventFilter(self, watched, event):
        if not self.isVisible() or not hasattr(watched,'window') or watched.window() is not self:
            return False
        if event.type()==QEvent.Type.KeyPress:
            if event.isAutoRepeat():return True
            key=event.key()
            if key==Qt.Key.Key_Escape:
                self.reject();return True
            if key in (Qt.Key.Key_Control,Qt.Key.Key_Alt,Qt.Key.Key_Shift,Qt.Key.Key_Meta,Qt.Key.Key_AltGr):
                self.status.setText(tr('Модификатор нажат. Добавьте клавишу или кнопку мыши.'));return True
            sequence=QKeySequence(event.keyCombination()).toString(QKeySequence.SequenceFormat.PortableText)
            self.take(sequence);return True
        if event.type()==QEvent.Type.MouseButtonPress:
            button={Qt.MouseButton.MiddleButton:'MouseMiddle',Qt.MouseButton.BackButton:'MouseX1',Qt.MouseButton.ForwardButton:'MouseX2'}.get(event.button())
            if button:
                try:self.take(mouse_binding(event.modifiers(),button))
                except ValueError as error:self.status.setText(tr(str(error)))
                return True
        return False

class ShortcutRecorder(QLineEdit):
    recordingStarted=Signal()
    recordingFinished=Signal()
    recorded=Signal(str)
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self._binding=text;self.setReadOnly(True);self.setMinimumHeight(56)
        self.setAccessibleName(tr('Нажмите для записи сочетания'))
        self.setToolTip(tr('Нажмите поле, затем нажмите сочетание клавиш или модификатор с кнопкой мыши.'))
        self.set_binding(text);self._recording=False
        manager.changed.connect(self.retranslate)
    def retranslate(self):
        self.setAccessibleName(tr('Нажмите для записи сочетания'))
        self.setToolTip(tr('Нажмите поле, затем нажмите сочетание клавиш или модификатор с кнопкой мыши.'))
    def binding(self):return self._binding
    def set_binding(self,text):
        self._binding=text;self.setText(text)
    # Compatibility with keyboard-only programmatic tests/integration.
    def setKeySequence(self,sequence):self.set_binding(sequence.toString(QKeySequence.SequenceFormat.PortableText))
    def keySequence(self):return QKeySequence(self._binding)
    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:
            event.accept();self.setFocus();self.start_recording()
        else:super().mousePressEvent(event)
    def keyPressEvent(self,event):
        if event.key() in (Qt.Key.Key_Return,Qt.Key.Key_Enter,Qt.Key.Key_Space):
            self.start_recording();event.accept()
        else:super().keyPressEvent(event)
    def start_recording(self):
        if self._recording:return
        self._recording=True;self.recordingStarted.emit()
        dialog=RecordingDialog(self)
        try:
            if dialog.exec()==QDialog.DialogCode.Accepted and dialog.value:
                self.set_binding(dialog.value);self.recorded.emit(dialog.value)
        finally:
            self.recordingFinished.emit();self._recording=False;dialog.deleteLater()
