import unittest
import indicoio
import indicoio.custom

import os
import json


class FinetuneCollectionTest(unittest.TestCase):

    def tearDown(self):
        indicoio.config.host = self.previous_host
        indicoio.config.api_key = self.previous_api_key

    def setUp(self):
        self.previous_host = indicoio.config.host
        self.previous_api_key = indicoio.config.api_key
        indicoio.config.host = os.getenv("INDICO_API_HOST")
        indicoio.config.api_key = os.getenv("INDICO_API_KEY")
        self.collection_name = os.getenv("FINETUNE_COLLECTION_NAME")
        assert self.collection_name

        data_path = os.path.join(os.path.dirname(__file__), "data")
        fn_base = "reuters_annotated"
        texts_path = os.path.join(data_path, "{}.texts.txt".format(fn_base))
        annot_path = os.path.join(data_path, "{}.annotations.nljson".format(fn_base))
        with open(texts_path) as f:
            self.texts = f.read().split("\n")
        with open(annot_path) as f:
            self.annotations = [
                json.loads(line)
                for line in f.read().split("\n")
            ]

    @unittest.skipIf(not os.getenv("FINETUNE_COLLECTION_NAME"),
                     "This test requires that FINETUNE_COLLECTION_NAME"
                     " is set in the testing environment")
    def test_load_predict(self):
        """
        Loads a collection in the FINETUNE_COLLECTION_NAME from host
         INDICO_API_HOST using api_key INDICO_API_KEY.  Then it predicts
         against this collection.  This assumes that the collection is
         an annotation collection.

        The assertion is based on the idea that the model will likely not
         be very good with the low sample size.
        :return:
        """
        collection = indicoio.custom.FinetuneCollection(self.collection_name)
        collection.load()
        predictions = collection.predict(self.texts)

        success_levels = []
        for prediction, annotation in zip(predictions, self.annotations):
            p = set([
                named_entity["text"]
                for named_entity in prediction
            ])
            a = set([
                named_entity["text"]
                for named_entity in annotation
            ])
            success_levels.append(len(p & a) / len(a))
        average_success_level = sum(success_levels) / len(success_levels)

        self.assertGreater(average_success_level, .8)
