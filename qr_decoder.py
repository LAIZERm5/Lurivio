"""Offline QR decoding: ZXing-C++ first, OpenCV fallback. Never open payloads."""
import cv2
import numpy as np
import zxingcpp

MAX_PAYLOAD = 65536

def clean_payloads(values):
    found = []
    for value in values:
        if isinstance(value,str) and value and '\x00' not in value and len(value)<=MAX_PAYLOAD and value not in found:
            found.append(value)
    return found

class QrDecoder:
    """Decode the original pixels before enhancement, without URL guessing."""
    def __init__(self):
        self.detector=cv2.QRCodeDetector()

    def _zxing(self,image,binarizer=zxingcpp.Binarizer.LocalAverage):
        found=[]
        try:
            results=zxingcpp.read_barcodes(np.ascontiguousarray(image),formats=zxingcpp.BarcodeFormat.QRCode,
                try_rotate=True,try_downscale=True,binarizer=binarizer,return_errors=False)
            for result in results:
                if not result.valid:continue
                try:
                    # Raw UTF-8 avoids HRI/escaped display conversions of content.
                    value=result.bytes.decode('utf-8')
                except UnicodeError:continue
                found.append(value)
        except (ValueError,RuntimeError):
            pass
        return clean_payloads(found)

    def decode(self,bgr,thorough=False):
        if bgr is None or bgr.size==0 or min(bgr.shape[:2])<12:return []
        gray=cv2.cvtColor(bgr,cv2.COLOR_BGR2GRAY)
        if int(gray.max())==int(gray.min()):return []
        # Do not shrink the original frame first: that can erase small/dense QR
        # modules. ZXing's own multiscale search retains the original scan.
        border=max(12,min(64,round(min(gray.shape)*.08)))
        padded=cv2.copyMakeBorder(gray,border,border,border,border,cv2.BORDER_CONSTANT,value=255)
        attempts=[gray,padded,cv2.copyMakeBorder(255-gray,border,border,border,border,cv2.BORDER_CONSTANT,value=255)]
        for image in attempts:
            values=self._zxing(image)
            if values:return values
        # Dotted/rounded modules may break the continuity of finder rings.
        # Conservative black-module closing is a fallback only. Every returned
        # result must still pass the QR decoder's validity/error-correction checks.
        longest=max(gray.shape)
        styled=cv2.resize(gray,None,fx=1600/longest,fy=1600/longest,interpolation=cv2.INTER_AREA) if longest>1600 else gray
        for candidate in (styled,255-styled):
            _,binary=cv2.threshold(candidate,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            binary=cv2.copyMakeBorder(binary,24,24,24,24,cv2.BORDER_CONSTANT,value=255)
            for size in (3,5):
                closed=255-cv2.morphologyEx(255-binary,cv2.MORPH_CLOSE,np.ones((size,size),np.uint8))
                values=self._zxing(closed)
                if values:return values
        # Contrast normalization helps coloured low-contrast codes. Do not synthesize
        # payloads or treat an erroneous checksum as valid.
        if thorough:
            normalized=cv2.normalize(padded,None,0,255,cv2.NORM_MINMAX)
            values=self._zxing(normalized,zxingcpp.Binarizer.GlobalHistogram)
            if values:return values
            if min(gray.shape)<500:
                enlarged=cv2.resize(padded,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
                values=self._zxing(enlarged)
                if values:return values
        # Retain the independently implemented decoder as a bounded fallback.
        longest=max(gray.shape)
        small=cv2.resize(gray,None,fx=1600/longest,fy=1600/longest,interpolation=cv2.INTER_AREA) if longest>1600 else gray
        for image in (small,cv2.copyMakeBorder(small,border,border,border,border,cv2.BORDER_CONSTANT,value=255)):
            try:
                ok,decoded,_,_=self.detector.detectAndDecodeMulti(image)
                values=clean_payloads(decoded) if ok else []
                if not values:
                    decoded,_,_=self.detector.detectAndDecode(image)
                    values=clean_payloads([decoded])
            except (cv2.error,UnicodeError):continue
            if values:return values
        return []

def recognise_capture(engine,bgr,fast=True,capture_mode='auto',decoder=None):
    from ocr_worker import recognise
    if capture_mode not in ('auto','ocr','qr'):capture_mode='auto'
    h,w=bgr.shape[:2]
    scan_qr=capture_mode=='qr' or (capture_mode=='auto' and min(h,w)>=48 and max(h,w)/min(h,w)<=8)
    if scan_qr:
        values=(decoder or QrDecoder()).decode(bgr,thorough=capture_mode=='qr')
        if values:return values,'\n\n'.join(values),1.0,'QR'
    if capture_mode=='qr':return [],'',0.0,'QR'
    return recognise(engine,bgr,fast)
