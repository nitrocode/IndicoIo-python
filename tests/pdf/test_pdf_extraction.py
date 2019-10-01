import os.path

import PIL
from PIL import Image
from PIL.PpmImagePlugin import PpmImageFile
import six

from indicoio import pdf_extraction
from .indico_pdf_base import PDFTestCase

import unittest

DIR = os.path.dirname(os.path.realpath(__file__))
PDF = os.path.join(DIR, "data", "test.pdf")


class PDFExtractionTestCase(PDFTestCase):
    def test_pdf_extraction(self):
        results = pdf_extraction(PDF, raw_text=True)
        assert "raw_text" in results.keys()
        assert "metadata" in results.keys()
        assert isinstance(results.get("raw_text"), six.string_types)
        assert isinstance(results.get("metadata"), dict)

    def test_pdf_extraction_batch(self):
        results = pdf_extraction([PDF])
        assert isinstance(results, list)

    @unittest.skip(
        "Remove this skip line when PDF extraction V2 allows image extraction"
    )
    def test_image_support(self):
        results = pdf_extraction(PDF, raw_text=True, images=True)
        assert "raw_text" in results.keys()
        assert "metadata" in results.keys()
        assert "images" in results.keys()
        assert isinstance(results.get("images"), list)
        assert isinstance(results.get("images")[0], PIL.JpegImagePlugin.JpegImageFile)

    @unittest.skip(
        "Remove this skip line when PDF extraction V2 allows table extraction"
    )
    def test_table_support(self):
        results = pdf_extraction(PDF, raw_text=True, tables=True)
        assert "raw_text" in results.keys()
        assert "metadata" in results.keys()
        assert "tables" in results.keys()
        assert isinstance(results.get("tables"), list)

    def test_url_support(self):
        url = "https://papers.nips.cc/paper/4824-imagenet-classification-with-deep-convolutional-neural-networks.pdf"
        results = pdf_extraction(url, raw_text=True)
        assert "raw_text" in results.keys()
        assert "metadata" in results.keys()
        assert isinstance(results.get("raw_text"), six.string_types)
        assert isinstance(results.get("metadata"), dict)
