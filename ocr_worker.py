"""Persistent, prewarmed OCR worker. All model access stays on this thread."""
import hashlib
import logging
import queue
import time
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from links import extract_urls


def image_array(image):
    if isinstance(image, np.ndarray):
        return image.copy()
    rgb = image.convertToFormat(QImage.Format.Format_RGB888)
    # Respect row padding and retain ownership by copying before rgb is freed.
    data = np.frombuffer(rgb.constBits(), dtype=np.uint8, count=rgb.sizeInBytes())
    return data.reshape(rgb.height(), rgb.bytesPerLine())[:, :rgb.width()*3].reshape(rgb.height(), rgb.width(), 3)[:, :, ::-1].copy()


def recognise(engine, bgr, fast):
    height, width = bgr.shape[:2]
    if fast and height <= 120 and width >= height * 4:
        # The recognizer resizes to its own input height. No 2x screen upscale,
        # no orientation classifier, and no detection pass for a tight single line.
        # Tighten only empty margins on a mostly uniform background. Wide blank
        # padding otherwise shrinks glyphs inside the recognition model input.
        import cv2
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        if int(gray.max()) - int(gray.min()) < 2:
            return [], '', 0.0, 'пустая область'
        border = np.concatenate((gray[:3].ravel(), gray[-3:].ravel(),
                                 gray[:, :3].ravel(), gray[:, -3:].ravel()))
        background = float(np.median(border))
        ys, xs = np.nonzero(np.abs(gray.astype(np.int16)-int(background)) > 35)
        tight = bgr
        if len(xs):
            left, right = max(0, int(xs.min())-3), min(width, int(xs.max())+4)
            top, bottom = max(0, int(ys.min())-3), min(height, int(ys.max())+4)
            if bottom-top >= 8 and right-left >= 24:
                tight = bgr[top:bottom, left:right]
        result, _ = engine(tight, use_det=False, use_cls=False)
        if result:
            text = '\n'.join(str(row[0]) for row in result)
            confidence = min(float(row[1]) for row in result)
            urls = extract_urls(text)
            if len(urls) == 1 and confidence >= .93:
                return urls, text, confidence, 'строка'
    # General selection (or uncertain fast result): normal text detection.
    import cv2
    if max(height, width) > 1920:
        scale = 1920 / max(height, width)
        bgr = cv2.resize(bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    if bgr.shape[0] < 32:
        scale = 32 / bgr.shape[0]
        bgr = cv2.resize(bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    bgr = np.pad(bgr, ((12,12), (12,12), (0,0)), constant_values=255)
    result, _ = engine(bgr, use_cls=False)
    text = '\n'.join(str(row[1]) for row in (result or []))
    confidence = min((float(row[2]) for row in (result or [])), default=0)
    return extract_urls(text), text, confidence, 'область'

class OcrWorker(QThread):
    ready = Signal()
    result = Signal(list, str, float, float, str)
    failed = Signal(str)

    def __init__(self):
        super().__init__()
        self.jobs = queue.Queue(maxsize=2)

    def submit(self, image, fast=True, capture_mode='auto'):
        self.jobs.put_nowait((image, fast, capture_mode))

    def clear_cache(self):
        try:
            self.jobs.put_nowait(('clear',))
        except queue.Full:
            pass

    def stop(self):
        self.requestInterruption()
        try:
            self.jobs.put_nowait(None)
        except queue.Full:
            pass

    def run(self):
        try:
            from qr_decoder import QrDecoder, recognise_capture
            decoder = QrDecoder()
            from rapidocr_onnxruntime import RapidOCR
            engine = RapidOCR(det_limit_side_len=960,
                              intra_op_num_threads=2, inter_op_num_threads=1)
            # Prewarm both normal and single-line paths; no network or user image.
            dummy = np.full((48, 320, 3), 255, np.uint8)
            engine(dummy, use_cls=False)
            engine(dummy, use_det=False, use_cls=False)
            self.ready.emit()
            previous_key = previous_result = None
            while not self.isInterruptionRequested():
                job = self.jobs.get()
                if job is None or self.isInterruptionRequested():
                    break
                if len(job) == 1 and job[0] == 'clear':
                    previous_key = previous_result = None
                    continue
                image, fast, capture_mode = job
                try:
                    tick = time.perf_counter()
                    bgr = image_array(image)
                    key = (bgr.shape, hashlib.blake2b(bgr, digest_size=16).digest(), bool(fast), capture_mode)
                    if key == previous_key and previous_result is not None:
                        urls, text, confidence, original_mode = previous_result
                        mode = original_mode + ' / кэш'
                    else:
                        urls, text, confidence, mode = recognise_capture(engine, bgr, fast, capture_mode, decoder)
                        # One in-memory fingerprint/result only; no screenshots,
                        # result history or cache files. Clear clears this too.
                        previous_key = key if urls else None
                        previous_result = (urls,text,confidence,mode) if urls else None
                    bgr = None
                    self.result.emit(urls, text, confidence, time.perf_counter()-tick, mode)
                except Exception:
                    logging.exception('Local OCR failed')
                    self.failed.emit('Ошибка OCR. Попробуйте другую область. Технический журнал: errors.log в папке настроек.')
                finally:
                    image = None
                    job = None
        except ModuleNotFoundError as error:
            logging.exception('Recognition dependency missing')
            if error.name == 'zxingcpp':
                self.failed.emit('Для QR нужна новая библиотека ZXing. Полностью закройте приложение и запустите Start.bat для обновления.')
            else:
                self.failed.emit('Не удалось загрузить OCR. Повторите установку через Start.bat или проверьте errors.log.')
        except Exception:
            logging.exception('OCR initialization failed')
            self.failed.emit('Не удалось загрузить OCR. Повторите установку через Start.bat или проверьте errors.log.')
