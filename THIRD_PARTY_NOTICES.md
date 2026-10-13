# Third-party notices

Lurivio's MIT license covers its own source code only. It does not replace
licenses for dependencies, bundled native libraries, Qt or OCR model weights.

Runtime components include:

| Component | License / review requirement |
| :-- | :-- |
| PySide6 Essentials / Qt / Shiboken | PySide6 metadata offers LGPL-3.0-only, GPL or commercial terms. Review the LGPL option and individual Qt/native components before binary distribution. |
| RapidOCR (`rapidocr_onnxruntime`) | Apache-2.0 package metadata. Model provenance and model-weight terms must also be reviewed. |
| ONNX Runtime | MIT; wheel includes a license text. |
| ZXing-C++ Python bindings (`zxing-cpp` 2.3.0) | Apache-2.0 per installed wheel metadata. Review upstream and bundled components; canonical Apache-2.0 text supplied in third_party. |
| OpenCV Python | Apache-2.0 package metadata; native/third-party notices are also shipped in the wheel. |
| NumPy | BSD-style project license plus bundled native-library notices. |
| Pillow | Its own project license/metadata; see collected license texts and project documentation. |
| Other runtime dependencies | PyYAML, Shapely, pyclipper, protobuf, flatbuffers, tqdm, six, packaging, colorama and their transitive/native components retain their own terms. |

`tools/collect_licenses.py` copies available LICENSE/NOTICE files and distribution
metadata into binary builds. Standard GNU GPLv3/LGPLv3 texts are supplied under
`third_party`. If a wheel does not ship full texts, package metadata alone is
**not** a substitute for satisfying its distribution obligations.

Before publishing a binary, the distributor must review component/model licenses,
include required attribution and texts, and preserve user rights required by
applicable terms (including LGPL relinking/replacement requirements where relevant).
The onedir layout keeps dynamic Qt/native libraries separate but is not, by itself,
a declaration of full license compliance. Sources for unmodified upstream packages
are available through their published projects; redistribution requirements still
need review for the exact versions and bundle.

- [Qt for Python](https://doc.qt.io/qtforpython-6/licenses.html)
- [RapidOCR](https://github.com/RapidAI/RapidOCR)
- [ONNX Runtime](https://github.com/microsoft/onnxruntime)
- [OpenCV Python](https://github.com/opencv/opencv-python)
- [NumPy](https://numpy.org/)
- [Pillow](https://python-pillow.org/)

No Nami screenshots, logos or assets are redistributed in this repository.
The example application images are generated from Lurivio itself using dummy URLs.
No affiliation with Nami, Apple or Microsoft is claimed.

## QR decoding (0.6.0)

QR recognition uses the existing OpenCV dependency (QRCodeDetector). No external QR service or new decoder library is used. OpenCV license obligations remain applicable.

## QR decoding (0.6.1)

ZXing-C++ is the primary offline decoder; OpenCV is retained as fallback. The pinned zxing-cpp wheel is collected into the portable build with its available metadata/notices. Upstream: https://github.com/zxing-cpp/zxing-cpp . No QR service, upload or account is used.
