#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from indicoio import content_filtering
from ..image.indico_image_base import ImageTest, DIR


class AsyncJobTest(ImageTest):
    def test_async_job(self):
        test_face = os.path.normpath(os.path.join(DIR, "data/happy.png"))
        response = content_filtering(test_face, job_options={"job": True})
        self.assertTrue(isinstance(response, float))
        self.assertTrue(response < 0.5)

    def test_batch_async_job(self):
        test_data = [
            "https://image-similarity-demo.s3.amazonaws.com/demo_imgs/aas_{}.jpg".format(
                idx
            )
            for idx in range(5)
        ] * 5
        response = content_filtering(test_data, job_options={"job": True})
        self.assertTrue(isinstance(response, list))
        self.assertTrue(isinstance(response[0], float))
