"""Synthetic video-like QR fixtures; not a guarantee for a specific Telegram QR."""
import unittest
import cv2
import numpy as np
from qr_decoder import QrDecoder

VALUE='https://t.me/example_public_channel?start=Demo_QR_1234567890'

def modules(value=VALUE):
    params=cv2.QRCodeEncoder_Params();params.correction_level=cv2.QRCodeEncoder_CORRECT_LEVEL_H
    image=cv2.QRCodeEncoder_create(params).encode(value)
    return cv2.copyMakeBorder(image,4,4,4,4,cv2.BORDER_CONSTANT,value=255)

def square(value=VALUE,scale=8):
    gray=cv2.resize(modules(value),None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
    return cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)

def rounded(value=VALUE):
    raw=modules(value);scale=10
    gray=np.full((raw.shape[0]*scale,raw.shape[1]*scale),255,np.uint8)
    for y,x in zip(*np.nonzero(raw==0)):
        cv2.circle(gray,(x*scale+scale//2,y*scale+scale//2),5,0,-1)
    return cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)

class VideoQrTests(unittest.TestCase):
    def setUp(self):self.decoder=QrDecoder()
    def assertReads(self,image,value=VALUE):self.assertIn(value,self.decoder.decode(image,thorough=True))
    def test_rounded_modules(self):self.assertReads(rounded())
    def test_logo_in_center(self):
        image=square();h,w=image.shape[:2];radius=int(min(h,w)*.075)
        cv2.rectangle(image,(w//2-radius,h//2-radius),(w//2+radius,h//2+radius),(255,255,255),-1)
        cv2.circle(image,(w//2,h//2),radius-3,(210,120,20),-1)
        self.assertReads(image)
    def test_jpeg_video_compression(self):
        image=square(scale=4);ok,data=cv2.imencode('.jpg',image,[cv2.IMWRITE_JPEG_QUALITY,35]);self.assertTrue(ok)
        self.assertReads(cv2.imdecode(data,cv2.IMREAD_COLOR))
    def test_colour_low_contrast(self):
        image=square();dark=image[:,:,0]<128
        image[:]=(235,230,220);image[dark]=(180,170,130)
        self.assertReads(image)
    def test_very_low_contrast(self):
        image=square();dark=image[:,:,0]<128
        image[:]=253;image[dark]=250
        self.assertReads(image)
    def test_tight_crop(self):
        gray=modules();ys,xs=np.nonzero(gray==0);gray=gray[ys.min():ys.max()+1,xs.min():xs.max()+1]
        gray=cv2.resize(gray,None,fx=8,fy=8,interpolation=cv2.INTER_NEAREST)
        self.assertReads(cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR))
    def test_dense_qr_in_large_frame(self):
        value='https://example.org/'+('long-segment-'*35)+'?test=1'
        qr=square(value,scale=4);h,w=qr.shape[:2]
        frame=np.full((2160,3840,3),225,np.uint8);frame[140:140+h,600:600+w]=qr
        self.assertReads(frame,value)
    def test_partial_unreadable_never_guesses(self):
        image=square();image[:image.shape[0]//2]=255
        self.assertEqual(self.decoder.decode(image,thorough=True),[])
    def test_inverted_rounded(self):self.assertReads(255-rounded())

if __name__=='__main__':unittest.main()
