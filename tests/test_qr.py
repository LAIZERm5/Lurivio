import unittest
from unittest.mock import Mock, patch
import cv2
import numpy as np
from qr_decoder import QrDecoder, recognise_capture, clean_payloads

def make_qr(value, scale=8):
    qr=cv2.QRCodeEncoder_create().encode(value)
    qr=cv2.copyMakeBorder(qr,4,4,4,4,cv2.BORDER_CONSTANT,value=255)
    qr=cv2.resize(qr,None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
    return cv2.cvtColor(qr,cv2.COLOR_GRAY2BGR)

class QrTests(unittest.TestCase):
    def setUp(self):self.decoder=QrDecoder()
    def test_exact_url(self):
        value='https://example.com/Guide?x=1&y=2#test'
        self.assertEqual(self.decoder.decode(make_qr(value)),[value])
    def test_unicode_and_multiline(self):
        value='Привет\nLurivio\nhttps://пример.рф/путь?x=1'
        self.assertEqual(self.decoder.decode(make_qr(value)),[value])
    def test_wifi(self):
        value='WIFI:T:WPA;S:Test network;P:example-password;;'
        self.assertEqual(self.decoder.decode(make_qr(value)),[value])
    def test_rotated_and_inverted(self):
        value='https://example.org/qr'
        image=make_qr(value)
        for img in (np.rot90(image).copy(),255-image):
            self.assertEqual(self.decoder.decode(img),[value])
    def test_multiple(self):
        a=make_qr('https://example.com/a');b=make_qr('https://example.org/b')
        canvas=np.full((max(a.shape[0],b.shape[0])+80,a.shape[1]+b.shape[1]+120,3),255,np.uint8)
        canvas[40:40+a.shape[0],40:40+a.shape[1]]=a
        canvas[40:40+b.shape[0],80+a.shape[1]:80+a.shape[1]+b.shape[1]]=b
        self.assertEqual(set(self.decoder.decode(canvas)),{'https://example.com/a','https://example.org/b'})
    def test_blank(self):
        self.assertEqual(self.decoder.decode(np.full((200,200,3),255,np.uint8)),[])
    def test_qr_bypasses_ocr(self):
        engine=Mock(side_effect=AssertionError('OCR must not run'))
        value='https://example.com/a.'
        result=recognise_capture(engine,make_qr(value),True,'auto',self.decoder)
        self.assertEqual(result[0],[value]);self.assertEqual(result[3],'QR');engine.assert_not_called()
    def test_qr_only_no_fallback(self):
        engine=Mock(side_effect=AssertionError('OCR must not run'))
        self.assertEqual(recognise_capture(engine,np.full((200,200,3),255,np.uint8),True,'qr',self.decoder)[0],[])
    def test_ocr_only_skips_qr(self):
        decoder=Mock(side_effect=AssertionError('QR must not run'))
        with patch('ocr_worker.recognise',return_value=(['https://a.com'],'text',.99,'строка')) as ocr:
            self.assertEqual(recognise_capture(None,make_qr('https://a.com'),True,'ocr',decoder)[3],'строка')
            ocr.assert_called_once();decoder.decode.assert_not_called()
    def test_auto_fallback(self):
        with patch('ocr_worker.recognise',return_value=([], '',0,'область')) as ocr:
            recognise_capture(None,np.full((200,200,3),255,np.uint8),True,'auto',self.decoder)
            ocr.assert_called_once()
    def test_payload_limits(self):
        self.assertEqual(clean_payloads(['abc','abc','','a\x00b','x'*65537,None]),['abc'])

if __name__=='__main__':unittest.main()
