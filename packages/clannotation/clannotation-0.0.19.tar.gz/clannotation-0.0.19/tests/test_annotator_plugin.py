import hashlib
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

import botocore
from moto import mock_s3


@mock_s3
class TestAnnotatorPlugin(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.append("../../")
        sys.path.append("../src")
        sys.path.append("../src/plugins")

        # setup a moto-mocked S3 client
        from claws import aws_utils

        import settings

        self._aws_connector = aws_utils.AWSConnector(bucket=settings.BUCKET)
        self.client = self._aws_connector.s3_client
        self.client._request_signer.sign = lambda *args, **kwargs: None

        try:
            self._s3 = self._aws_connector.s3_resource
            self._s3.meta.client.head_bucket(Bucket=settings.BUCKET)
        except botocore.exceptions.ClientError:
            pass
        else:
            err = "{bucket} should not exist.".format(bucket=settings.BUCKET)
            raise EnvironmentError(err)

        self._s3.create_bucket(Bucket=settings.BUCKET)

        self.client.put_bucket_policy(
            Bucket=settings.BUCKET,
            Policy='{"Version":"2012-10-17", "Statement":[{"Sid":"AddPerm", '
            '"Effect":"Allow", "Principal": "*", "Action":['
            '"s3:GetObject"], "Resource":["arn:aws:s3:::'
            + settings.BUCKET
            + '/*"]}]}',
        )

        current_dir = os.path.dirname(__file__)
        fixtures_dir = os.path.join(current_dir, "unit_test_fixtures")

        self._upload_fixtures(
            bucket=settings.BUCKET,
            fixtures_dir=fixtures_dir,
            aws_dir=f"{settings.VALID_ANNOTATIONS}/members/",
        )

        # upload dummy data to moto mock
        self.s3_key = "/members/78"
        annotations = {
            "anno1.json": {"key1": "value1"},
            "anno2.json": {"key2": "value2"},
            "test-item-1.json": {"test-key-1": "value1"},
            "test-item-2.json": {"test-key-2": "value2"},
        }

        for file_name, content in annotations.items():
            self.client.put_object(
                Bucket=settings.BUCKET,
                Key=f"{settings.ANNOTATION_PATH}{self.s3_key}/{file_name}",
                Body=json.dumps(content),
            )

        from longsight.instrumentation import Instrumentation

        self._instrumentation = Instrumentation(self._aws_connector)

    def _upload_fixtures(
        self, bucket: str, fixtures_dir: str, aws_dir: str
    ) -> None:
        fixtures_paths = [
            os.path.join(path, filename)
            for path, _, files in os.walk(fixtures_dir)
            for filename in files
        ]
        for path in fixtures_paths:
            key = f"{aws_dir}/{os.path.relpath(path, fixtures_dir)}"
            self.client.upload_file(
                Filename=path,
                Bucket=bucket,
                Key=key,
                ExtraArgs={"ACL": "public-read"},
            )

    def test_get_valid_annotations(self):
        """
        Test that we get the valid annotations list from S3
        :return:
        """
        annotator_plugin_instance = self.get_annotation_instance()

        valid_annotations = annotator_plugin_instance.get_valid_annotations(
            "members"
        )

        expected_valid_annotations = {"test-item-1.json", "test-item-2.json"}

        self.assertEqual(valid_annotations, expected_valid_annotations)

    def test_generate_annotation_list(self):
        """
        Test that we generate a list of annotations correctly
        :return: None
        """
        annotator_plugin_instance = self.get_annotation_instance()

        # Set up the valid_annotations list and rebuild_route method for test
        annotator_plugin_instance._valid_annotations = [
            "anno1.json",
            "anno2.json",
        ]

        items = [
            {"id": "item1"},
            {"id": "item2"},
        ]
        route = "/example/23"
        identifier_key = "id"

        annotation_list = annotator_plugin_instance.generate_annotation_list(
            items, route, identifier_key
        )

        expected_annotation_list = [
            "annotations/example/item1/anno1.json",
            "annotations/example/item1/anno2.json",
            "annotations/example/item2/anno1.json",
            "annotations/example/item2/anno2.json",
        ]

        self.assertEqual(annotation_list, expected_annotation_list)

    def get_annotation_instance(self):
        from clannotation import annotator
        import settings

        return annotator.Annotator(
            settings,
            aws_connector=self._aws_connector,
            instrumentation=self._instrumentation,
        )

    def test_get_annotations(self):
        """
        Test that we can fetch annotations from s3
        :return: None
        """
        annotator_plugin_instance = self.get_annotation_instance()

        from claws import aws_utils

        aws_utils.s3_client = self.client

        # Set up the valid_annotations list for the test
        annotator_plugin_instance._valid_annotations = [
            "anno1.json",
            "anno2.json",
        ]

        result = annotator_plugin_instance.get_annotations(self.s3_key)

        expected_result = {
            annotator_plugin_instance._settings.LABS_PREFIX
            + "anno1": {"key1": "value1"},
            annotator_plugin_instance._settings.LABS_PREFIX
            + "anno2": {"key2": "value2"},
        }

        self.assertEqual(result, expected_result)

    def test_parse_key_list_input(self):
        """
        Test that the list parser returns the first result in the list
        :return: None
        """
        from clannotation import annotator

        item_key = ["key1", "key2", "key3"]

        result = annotator.Annotator.parse_key(item_key)

        self.assertEqual(result, "key1")

    def test_parse_key_string_input(self):
        """
        Test that the list parser echoes a string
        :return: None
        """
        from clannotation import annotator

        item_key = "key1"

        result = annotator.Annotator.parse_key(item_key)

        self.assertEqual(result, "key1")

    def test_extract_key_key_exists(self):
        """
        Test we can extract a key when it exists
        :return: None
        """
        from clannotation import annotator

        item = {
            "key1": "value1",
            "key2": ["value2a", "value2b"],
        }
        key = "key2"

        result = annotator.Annotator.extract_key(item, key)

        self.assertEqual(result, "/value2a")

    def test_extract_key_key_does_not_exist(self):
        """
        Test that we get a None return value for a non-existent key
        :return: None
        """
        from clannotation import annotator

        item = {
            "key1": "value1",
            "key2": ["value2a", "value2b"],
        }
        key = "key3"

        result = annotator.Annotator.extract_key(item, key)

        self.assertIsNone(result)

    def test_build_s3_key_key_exists(self):
        """
        Test that we build an s3 key in a standardised way
        :return: None
        """
        from clannotation import annotator

        item = {
            "key1": "value1",
            "key2": ["value2a", "value2b"],
        }
        route = "your-route/"
        key = "key2"

        result = annotator.Annotator.build_s3_key(item, route, key)

        self.assertEqual(result, "your-route/value2a")

    def test_build_s3_key_key_does_not_exist(self):
        """
        Test that we handle a key that does not exist
        :return: None
        """
        from clannotation import annotator

        item = {
            "key1": "value1",
            "key2": ["value2a", "value2b"],
        }
        route = "members/"
        key = "key3"

        result = annotator.Annotator.build_s3_key(item, route, key)

        self.assertEqual(result, "members")

    def test_doi_to_md5(self):
        """
        Check that the DOI to MD5 conversion works
        :return: None
        """
        from clannotation import annotator

        doi = "10.1000/xyz123"
        expected_md5 = hashlib.md5(doi.lower().encode()).hexdigest()

        result = annotator.Annotator.doi_to_md5(doi)

        self.assertEqual(result, expected_md5)

    def test_patch_item(self):
        """
        Check that we can patch a single item
        :return: None
        """
        annotation_plugin_instance = self.get_annotation_instance()

        doi = "10.1000/xyz123"

        item = {
            "DOI": doi,
            "title": "Sample Title",
        }
        route = "your-route/"
        identifier_key = "DOI"

        hashlib.md5(doi.lower().encode()).hexdigest()

        mocked_rebuild_route_result = f"your-route/{doi}/"
        mocked_get_annotations_result = {
            "annotation_key": "annotation_value",
        }

        annotation_plugin_instance.rebuild_route = MagicMock(
            return_value=mocked_rebuild_route_result
        )
        annotation_plugin_instance.get_annotations = MagicMock(
            return_value=mocked_get_annotations_result
        )

        result = annotation_plugin_instance.patch_item(
            item, route, identifier_key
        )

        expected_result = {
            "DOI": doi,
            "title": "Sample Title",
            "annotation_key": "annotation_value",
        }

        self.assertEqual(result, expected_result)

    def test_rebuild_route_two_parts(self):
        """
        Test that we can rebuild a route URL
        :return: None
        """
        from clannotation import annotator

        route = "/members"
        new_identifier = "1234"

        result = annotator.Annotator.rebuild_route(route, new_identifier)

        self.assertEqual(result, "/members/1234")

    def test_rebuild_route_more_than_two_parts(self):
        """
        Test that we can rebuild a route URL with an identifier
        :return: None
        """
        from clannotation import annotator

        route = "/members/1234/"
        new_identifier = "5678"

        result = annotator.Annotator.rebuild_route(route, new_identifier)

        self.assertEqual(result, "/members/5678")

    def test_annotate_item(self):
        """
        Test that we can annotate an item
        :return:
        """
        annotation_plugin_instance = self.get_annotation_instance()

        doi = "10.1000/xyz123"

        response = {
            "message": {
                "DOI": doi,
                "title": "Sample Title",
            }
        }
        route = "your-route/"
        identifier_key = "DOI"

        mocked_patch_item_result = {
            "DOI": doi,
            "title": "Sample Title",
            "annotation_key": "annotation_value",
        }

        annotation_plugin_instance.patch_item = MagicMock(
            return_value=mocked_patch_item_result
        )

        result = annotation_plugin_instance.annotate_item(
            response, route, identifier_key
        )

        expected_result = {
            "message": {
                "DOI": doi,
                "title": "Sample Title",
                "annotation_key": "annotation_value",
            }
        }

        self.assertEqual(result, expected_result)

    def test_annotate_item_list(self):
        """
        Test that we correctly annotate a list of items
        :return:
        """
        annotation_plugin_instance = self.get_annotation_instance()

        doi = "10.1000/xyz123"
        doi_2 = "10.1001/xyz456"

        response = {
            "message": {
                "items": [
                    {
                        "DOI": doi,
                        "title": "Sample Title 1",
                    },
                    {
                        "DOI": doi_2,
                        "title": "Sample Title 2",
                    },
                ],
            }
        }
        route = "your-route/"
        key = "DOI"

        mocked_generate_annotation_list_result = [
            "members/32/annotation_1_1.json",
            "members/32/annotation_1_2.json",
            "members/33/annotation_1_1.json",
            "members/33/annotation_1_2.json",
        ]

        mocked_valid_annotations = [
            "annotation_1_1.json",
            "annotation_1_2.json",
        ]

        annotation_plugin_instance._valid_annotations = mocked_valid_annotations

        annotation_plugin_instance.generate_annotation_list = MagicMock(
            return_value=mocked_generate_annotation_list_result
        )

        mocked_get_multiple_s3_objs_result = [
            {
                "members/32/annotation_1_1.json": '{"annotation_1_1_key": "annotation_1_1_value"}'
            },
            {
                "members/32/annotation_1_2.json": '{"annotation_1_2_key": "annotation_1_2_value"}'
            },
            {
                "members/33/annotation_1_1.json": '{"annotation_2_1_key": "annotation_2_1_value"}'
            },
            {
                "members/33/annotation_1_2.json": '{"annotation_2_2_key": "annotation_2_2_value"}'
            },
        ]

        with patch(
            "claws.aws_utils.AWSConnector.get_multiple_s3_objs"
        ) as mock_get_multiple_s3_objs:
            mock_get_multiple_s3_objs.return_value = (
                mocked_get_multiple_s3_objs_result
            )

            result = annotation_plugin_instance.annotate_item_list(
                response, route, key
            )

            mock_get_multiple_s3_objs.assert_called()

            expected_result = {
                "message": {
                    "items": [
                        {
                            "DOI": doi,
                            "title": "Sample Title 1",
                            "cr-labs-annotation_1_1": {
                                "annotation_1_1_key": "annotation_1_1_value"
                            },
                            "cr-labs-annotation_1_2": {
                                "annotation_1_2_key": "annotation_1_2_value"
                            },
                        },
                        {
                            "DOI": doi_2,
                            "title": "Sample Title 2",
                            "cr-labs-annotation_1_1": {
                                "annotation_2_1_key": "annotation_2_1_value"
                            },
                            "cr-labs-annotation_1_2": {
                                "annotation_2_2_key": "annotation_2_2_value"
                            },
                        },
                    ],
                }
            }

            self.assertEqual(result, expected_result)

    def test_annotate(self):
        """
        Test we correctly annotate items
        :return: None
        """
        annotation_plugin_instance = self.get_annotation_instance()

        self.maxDiff = None

        response_list = {
            "message-type": "list",
            "message": {"items": [{"id": "78"}, {"id": "79"}]},
        }
        response_item = {"message-type": "single", "message": {"id": "78"}}
        route_list = "/members"
        route = "/members/78"
        identifier_key = "id"

        mocked_valid_annotations = [
            "annotation_1_1.json",
            "annotation_1_2.json",
        ]

        with patch(
            "claws.aws_utils.AWSConnector.get_multiple_s3_objs"
        ) as mock_get_multiple_s3_objs:
            mocked_get_multiple_s3_objs_result = [
                {
                    "annotations/members/78/annotation_1_1.json": '{"annotation_1_1_key": "annotation_1_1_value"}'
                },
                {
                    "annotations/members/78/annotation_1_2.json": '{"annotation_1_2_key": "annotation_1_2_value"}'
                },
                {
                    "annotations/members/79/annotation_1_1.json": '{"annotation_2_1_key": "annotation_2_1_value"}'
                },
                {
                    "annotations/members/79/annotation_1_2.json": '{"annotation_2_2_key": "annotation_2_2_value"}'
                },
            ]

            mock_get_multiple_s3_objs.return_value = (
                mocked_get_multiple_s3_objs_result
            )

            result_list = annotation_plugin_instance.annotate(
                response=response_list,
                route=route_list,
                identifier_key=identifier_key,
                valid_annotations=mocked_valid_annotations,
            )

            self.assertDictEqual(
                result_list["message"]["items"][0],
                {
                    "cr-labs-annotation_1_1": {
                        "annotation_1_1_key": "annotation_1_1_value"
                    },
                    "cr-labs-annotation_1_2": {
                        "annotation_1_2_key": "annotation_1_2_value"
                    },
                    "id": "78",
                },
            )

            self.assertDictEqual(
                result_list["message"]["items"][1],
                {
                    "cr-labs-annotation_1_1": {
                        "annotation_2_1_key": "annotation_2_1_value"
                    },
                    "cr-labs-annotation_1_2": {
                        "annotation_2_2_key": "annotation_2_2_value"
                    },
                    "id": "79",
                },
            )

        with patch(
            "claws.aws_utils.AWSConnector.s3_obj_to_str"
        ) as s3_obj_to_str:
            s3_obj_to_str.return_value = '{"blah": "message"}'

            result_item = annotation_plugin_instance.annotate(
                response=response_item,
                route=route,
                identifier_key=identifier_key,
                valid_annotations=mocked_valid_annotations,
            )

            self.assertEqual(
                result_item,
                {
                    "message": {
                        "cr-labs-annotation_1_1": {"blah": "message"},
                        "cr-labs-annotation_1_2": {"blah": "message"},
                        "id": "78",
                    },
                    "message-type": "single",
                },
            )

    def test_rebuild_route_journals_pathway(self):
        from clannotation import annotator

        result = annotator.Annotator.rebuild_route(
            "/journals/1234-567x", ["8765-4321", "1235-4678"]
        )
        self.assertEqual(result, "/journals/1234567X")
