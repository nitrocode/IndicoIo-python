#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np

from indicoio import sentiment_hq
from .indico_text_base import TextTest
import unittest


class SentimentHQTest(TextTest):

    @unittest.skip("Remove this skip line when prod has async available")
    def test_batch_sentiment_hq(self):
        test_data = ["Worst song ever", "Best song ever"] * 5000
        response = sentiment_hq(test_data, job_options={"job": True})
        self.assertTrue(isinstance(response, list))
        self.assertTrue(response[0] < 0.5)

    @unittest.skip("Remove this skip line when prod has async available")
    def test_sentiment_hq(self):
        test_string = "Worst song ever."
        response = sentiment_hq(test_string, job_options={"job": True})

        self.assertTrue(isinstance(response, (float, np.float32)))
        self.assertTrue(response < 0.5)

        test_string = "Best song ever."
        response = sentiment_hq(test_string, job_options={"job": True})
        self.assertTrue(isinstance(response, (float, np.float32)))
        self.assertTrue(response > 0.5)
