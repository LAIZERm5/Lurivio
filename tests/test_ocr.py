"""Optional real-model smoke test, enabled in Windows CI."""
import os
import unittest
from pathlib import Path

@unittest.skipUnless(os.environ.get('LURIVIO_TEST_OCR') == '1','Set LURIVIO_TEST_OCR=1 for the real-model smoke test')
class OcrSmokeTest(unittest.TestCase):
    def test_visible_url(self):
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        from rapidocr_onnxruntime import RapidOCR
        from ocr_worker import recognise
        paths=[Path('C:/Windows/Fonts/arial.ttf'),Path('/usr/share/fonts/msttcore/arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
        font_path=next((p for p in paths if p.exists()),None)
        if font_path is None:
            self.skipTest('No suitable test font installed')
        font=ImageFont.truetype(str(font_path),32)
        image=Image.new('RGB',(760,64),'white')
        ImageDraw.Draw(image).text((8,8),'https://example.com/Guide?x=1',font=font,fill='black')
        bgr=np.asarray(image)[:,:,::-1].copy()
        engine=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=1)
        for pixels in (bgr,255-bgr):
            result=recognise(engine,pixels,True)
            self.assertEqual(result[0],['https://example.com/Guide?x=1'])

if __name__=='__main__':unittest.main()
