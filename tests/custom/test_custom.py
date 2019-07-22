import unittest
import uuid

from indicoio.utils.errors import IndicoError
from indicoio.custom import Collection, collections, vectorize

TEST_DATA = [
    ["input 1", "label 1"],
    ["input 11", "label 1"],
    ["input 2", "label 2"],
    ["input 22", "label 2"],
    ["input 3", "label 3"],
    ["input 33", "label 3"],
    ["input 4", "label 4"],
    ["input 44", "label 4"],
]

IMAGE_TEST_DATA = [
    ["https://i.imgur.com/xUX1rvY.png", "dog"],
    ["https://i.imgur.com/xUX1rvY.png", "dog"],
    ["https://i.imgur.com/2Q0EWRz.jpg", "cat"],
    ["https://i.imgur.com/XhUDCMP.jpg", "cat"],
]


class CustomAPITestBase(unittest.TestCase):
    test_data = None
    test_user_email = "contact@indico.io"

    def setUp(self):
        self.uuid = uuid.uuid1()
        self.collection_name = "__test_python___{}__".format(self.uuid)
        self.alternate_name = "__alternate{}".format(self.collection_name)

        self.collection = Collection(self.collection_name)
        assert self.test_data is not None

        self.collection.add_data(self.test_data)
        self.collection.train()
        self.collection.wait()

    def tearDown(self):
        for cn in [self.collection_name, self.alternate_name]:
            self._clean_collection(cn)

        collection_names = list(collections().keys())
        assert self.collection_name not in collection_names
        assert self.alternate_name not in collection_names

    @staticmethod
    def _clean_collection(collection_name):
        col = Collection(collection_name)
        try:
            info = col.info()
            if info["status"] == "training":
                col.wait()

            emails = set(
                [
                    email
                    for perm in info["permissions"]
                    for email in info["permissions"][perm]
                ]
            )
            for email in emails:
                col.deauthorize(email)

            if info["registered"]:
                col.deregister()

            col.clear()
        except IndicoError as e:
            if "does not exist" not in str(e):
                raise e


class CustomAPIsTextTestCase(CustomAPITestBase):
    test_data = TEST_DATA

    def test_add_predict(self):
        result = self.collection.predict(self.test_data[0][0])
        assert self.test_data[0][1] in result.keys()

    def test_add_predict_tfidf(self):
        collection = Collection(self.collection_name)
        collection.add_data(self.test_data, save_for_explanations=True)
        collection.train(model_type="tfidf")

    def test_vectorize(self):
        joinedtoken = "awkwardjoin"
        assert sum(vectorize(joinedtoken, subtokens=False)) == 0.0
        assert sum(vectorize(joinedtoken, subtokens=True)) != 0.0
        assert sum(vectorize(joinedtoken, subtokens=False, domain="finance")) == 0.0
        assert sum(vectorize(joinedtoken, subtokens=True, domain="finance")) != 0.0

    def test_list_collection(self):
        collection = Collection(collection_name)
        collection.add_data(test_data)
        collection.train()
        collection.wait()
        result = collection.predict(self.test_data[0][0])
        assert self.test_data[0][1] in result.keys()
        collection.explain(self.test_data[0][0], sequence_features=True)

    def test_vectorize(self):
        joinedtoken = "awkwardjoin"
        assert sum(vectorize(joinedtoken, subtokens=False)) == 0.0
        assert sum(vectorize(joinedtoken, subtokens=True)) != 0.0
        assert sum(vectorize(joinedtoken, subtokens=False, domain="finance")) == 0.0
        assert sum(vectorize(joinedtoken, subtokens=True, domain="finance")) != 0.0

    def test_list_collection(self):
        assert collections()[self.collection_name]

    def test_clear_example(self):
        result = self.collection.predict(self.test_data[0][0])
        assert self.test_data[0][1] in result.keys()
        self.collection.remove_example(self.test_data[0][0])
        self.collection.train()
        self.collection.wait()
        result = self.collection.predict(self.test_data[0][0])
        assert self.test_data[0][1] not in result.keys()

    def test_clear_collection(self):
        assert collections()[self.collection_name]
        self.collection.clear()
        assert not collections().get(self.collection_name)

    def test_register(self):
        self.collection.register()
        assert self.collection.info().get("registered")
        assert not self.collection.info().get("public")
        self.collection.deregister()
        assert not self.collection.info().get("registered")
        assert not self.collection.info().get("public")

    def test_make_public(self):
        self.collection.register(make_public=True)
        info = self.collection.info()
        assert info["registered"]
        assert info["public"]
        self.collection.deregister()
        info = self.collection.info()
        assert not info["registered"]
        assert not info["public"]

    def test_authorize_read_permissions(self):
        self.collection.register()
        self.collection.authorize(email=self.test_user_email, permission_type="read")

        permissions = self.collection.info()["permissions"]
        read = permissions["read"]
        write = permissions["write"]
        assert self.test_user_email in read
        assert self.test_user_email not in write

        self.collection.deauthorize(email=self.test_user_email)

        permissions = self.collection.info()["permissions"]
        read = permissions["read"]
        write = permissions["write"]
        assert self.test_user_email not in read
        assert self.test_user_email not in write

    def test_authorize_write_permissions(self):
        self.collection.register()
        self.collection.authorize(email=self.test_user_email, permission_type="write")
        assert self.test_user_email in self.collection.info().get("permissions").get(
            "write"
        )
        assert not self.test_user_email in self.collection.info().get(
            "permissions"
        ).get("read")
        self.collection.deauthorize(email=self.test_user_email)
        assert not self.test_user_email in self.collection.info().get(
            "permissions"
        ).get("read")
        assert not self.test_user_email in self.collection.info().get(
            "permissions"
        ).get("write")

    def test_rename(self):
        self.collection.rename(self.alternate_name)
        new_collection = Collection(self.alternate_name)

        # name no longer exists
        with self.assertRaises(IndicoError):
            collection = Collection(self.collection_name)
            collection.train()

        # collection is now accessible via the alternate name
        new_collection.info()

    def test_add_large_batch(self):
        self.collection.add_data(self.test_data * 100)
        self.collection.train()
        self.collection.wait()
        result = self.collection.predict(self.test_data[0][0])
        assert self.test_data[0][1] in result.keys()


class CustomAPIsImageTestCase(CustomAPITestBase):

    test_data = IMAGE_TEST_DATA

    def test_add_image_batch(self):
        result = self.collection.predict(self.test_data[0][0])
        assert self.test_data[0][1] in result.keys()

    def test_comparison_model(self):
        collection = Collection(collection_name)
        collection.add_data(
            [
                {
                    "jd_title": "Field Engineer",
                    "resume_text": "Worked as part of field eng. team building software with a direct line into clients.",
                    "description": "Must have prior experience working as field eng.",
                    "fit": "yes",
                },
                {
                    "jd_title": "Field Engineer",
                    "resume_text": "Migrated infrastructure to AWS",
                    "description": "Must have prior experience working as field eng.",
                    "fit": "yes",
                },
                {
                    "jd_title": "Field Engineer",
                    "resume_text": "Discord mod",
                    "description": "Must have prior experience working as field eng.",
                    "fit": "no",
                },
                {
                    "jd_title": "Field Engineer",
                    "resume_text": "cat walker",
                    "description": "Must have prior experience working as field eng.",
                    "fit": "no",
                },
            ],
            comparison=["resume_text", "description"],
            target="fit",
        )
        collection.train()
        collection.wait()

        result = collection.predict(
            {
                "jd_title": "Field Engineer",
                "resume_text": "cat walker",
                "description": "Must have prior experience working as field eng.",
                "fit": "no",
            },
            top_n=1,
        )
        assert "no" in result.keys()

    def test_multilabel_sequence_model(self):
        import indicoio

        indicoio.config.host = "localhost:8001"
        collection = Collection(sequence_collection_name)
        collection.add_data(
            [
                ["Color: red", [{"start": 7, "end": 10, "label": "color"}]],
                ["Color: blue", [{"start": 7, "end": 11, "label": "color"}]],
                ["Color: green", [{"start": 7, "end": 12, "label": "color"}]],
                ["Color: yellow", [{"start": 7, "end": 13, "label": "color"}]],
            ]
            * 5
        )
        collection.train(model_version="multilabel_v1", timeout=30)
        collection.wait()
        result = collection.predict("Color: purple")
        assert len(result) == 1.0
        assert result[0]["text"] == "purple"

