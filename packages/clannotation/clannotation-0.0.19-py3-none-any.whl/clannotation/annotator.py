import hashlib
import json
from collections import defaultdict
from pathlib import Path
from timeit import default_timer as timer

from aws_lambda_powertools import single_metric
from aws_lambda_powertools.metrics import MetricUnit
from claws import aws_utils

from longsight.instrumentation import Instrumentation


class Annotator:
    def __init__(
        self,
        settings,
        aws_connector: aws_utils.AWSConnector,
        instrumentation: Instrumentation = None,
    ):
        self._session = aws_connector.s3_session
        self._s3 = aws_connector.s3_resource
        self._s3_client = aws_connector.s3_client
        self._bucket = aws_connector.bucket
        self._settings = settings
        self._aws_connector = aws_connector
        self._valid_annotations = []
        self._instrumentation = instrumentation

    @property
    def instrumentation(self):
        """
        The current instrumentation object.
        :return: an Instrumentation object
        """
        return self._instrumentation

    @property
    def routes(self) -> list[str]:
        """
        The list of routes
        :return: the list of routes
        """
        return ["any"]

    def run(
        self,
        response_headers: dict,
        response_json: dict,
        route: str,
        identifier_key: str,
        request_headers: dict = None,
        request_querystring: dict = None,
        key_status=99,
        proxy=None,
    ) -> tuple[dict, dict]:
        """
        Run the annotation plugin
        :param response_headers: the response headers
        :param response_json: the response body
        :param route: the route
        :param identifier_key: the identifier key
        :return: None
        """
        if key_status == 0 or key_status == 1:
            return response_headers, response_json

        proxy.instrumentation.logger.info("Running annotation plugin")

        # annotate
        start = timer()
        result = response_headers, self.annotate(
            response=response_json, route=route, identifier_key=identifier_key
        )
        end = timer()
        annotation_time = end - start

        if proxy.instrumentation:
            with single_metric(
                name="Annotation Time",
                unit=MetricUnit.Seconds,
                value=annotation_time,
                namespace=proxy.instrumentation.namespace,
            ) as metric:
                metric.add_dimension(name="route", value=route)

        return result

    def get_valid_annotations(self, route_prefix: str):
        """
        Returns valid annotations for the specified route prefix
        :param route_prefix: the first part of a route (e.g. "members")
        :return:
        """
        return {
            obj.key.split("/")[-1]
            for obj in self._bucket.objects.filter(
                Prefix=f"{self._settings.VALID_ANNOTATIONS}/{route_prefix}"
            )
            if obj.key.endswith(".json")
        }

    def generate_annotation_list(self, items, route, identifier_key):
        """
        Generate the annotation list
        :param items: the items
        :return: the annotation list
        """
        final_list = []

        for item in items:
            identifier_value = (
                Annotator.doi_to_md5(item[identifier_key])
                if identifier_key == "DOI"
                else item[identifier_key]
            )

            reroute = self.rebuild_route(
                route=route, new_identifier=identifier_value
            )

            for valid_annotation in self._valid_annotations:
                final_list.append(
                    f"{self._settings.ANNOTATION_PATH}{reroute}/"
                    f"{valid_annotation}",
                )

        return final_list

    def get_annotations(self, s3_key: str) -> dict:
        """
        Get a dictionary of annotations from the S3 bucket
        :param s3_key: the S3 key/path to retrieve from
        :return: a dictionary of annotations
        """
        s3_key = f"{s3_key}/" if not s3_key.endswith("/") else s3_key

        res = {
            self._settings.LABS_PREFIX
            + self._aws_connector.s3_to_json_key(
                f"{self._settings.ANNOTATION_PATH}{s3_key}{obj}"
            ): json.loads(
                self._aws_connector.s3_obj_to_str(
                    bucket=self._settings.BUCKET,
                    s3_path=f"{self._settings.ANNOTATION_PATH}{s3_key}{obj}",
                )
            )
            for obj in self._valid_annotations
        }

        return res

    @staticmethod
    def parse_key(item_key) -> str:
        """
        If a key item is a list, use the first item in the list
        :param item_key: the item key
        :return: the key string
        """
        return item_key[0] if type(item_key) is list else item_key

    @staticmethod
    def extract_key(item: dict, key: str) -> str:
        """
        Extract the key and parse it
        :param item: the item
        :param key: the key to extract
        :return: a string or None
        """
        return (
            f"/{Annotator.parse_key(item[key])}"
            if key and key in item
            else None
        )

    @staticmethod
    def build_s3_key(item: dict, route: str, key: str) -> str:
        """
        Build the S3 key from the item
        :param item: the item
        :param route: the route
        :param key: the key
        :return: a string of the route
        """
        route = route[:-1] if route.endswith("/") else route

        key_result = Annotator.extract_key(item, key)

        return f"{route}{key_result}" if key_result else f"{route}"

    @staticmethod
    def doi_to_md5(doi: str) -> str:
        """
        Return the md5 hash of the DOI
        :param doi: the DOI to hash
        :return: the md5 hash
        """
        return hashlib.md5(doi.lower().encode()).hexdigest()

    def patch_item(
        self, item: dict, route: str | list, identifier_key: str
    ) -> dict:
        """
        Path the annotation into the item
        :param item: the item
        :param route: the route
        :param identifier_key: the identifier key
        :return: a set of annotations
        """
        # check to see if it is a DOI, if it is, md5 hash it
        identifier_value = (
            Annotator.doi_to_md5(item[identifier_key])
            if identifier_key == "DOI"
            else item[identifier_key]
        )

        route = self.rebuild_route(route=route, new_identifier=identifier_value)

        return self.get_annotations(f"{route}") | item

    @staticmethod
    def rebuild_route(route: str, new_identifier: str|list[str]):
        """
        Rebuild the route
        :param route: the route
        :param new_identifier: the new identifier
        :return: a string
        """
        path = route.split("/")

        # Need to filter out Nulls as some ISSNs from journals
        # route are null and shouldn't be used.
        if isinstance(new_identifier, list):
            new_identifier = [nid for nid in new_identifier if nid is not None]

        if (
            path[1] == "journals"
            and isinstance(new_identifier, list)
            and len(new_identifier) > 0
        ):
            new_identifier = new_identifier[0]
            new_identifier = new_identifier.replace("-", "")
            new_identifier = new_identifier.upper()
            new_path = ["", "journals", new_identifier]
            path = new_path

        elif path[1] == "works":
            new_path = ["", "works", str(new_identifier)]
            path = new_path

        elif path[1] == "journals" and len(path) > 2:
            normalized_issn = path[2].replace("-", "")
            normalized_issn = normalized_issn.upper()

            new_path = ["", "journals", normalized_issn]
            path = new_path

        elif len(path) == 2:
            # e.g. /members
            path.append(str(new_identifier))
        else:
            # e.g. /members/1234
            path[2] = str(new_identifier)

            if path[-1] == "":
                del path[-1]

        return "/".join(path)

    def annotate_item(
        self, response: dict, route: str, identifier_key: str
    ) -> dict:
        """
        Annotation an individual item
        :param response: the response
        :param route: the route
        :param identifier_key: the identifier key
        :return: a dictionary
        """
        response["message"] = self.patch_item(
            response["message"], route, identifier_key
        )
        return response

    def annotate_item_list(self, response: dict, route: str, key: str) -> dict:
        """
        Annotate a list of items
        :param response: the response
        :param route: the route
        :param key: the key
        :return: a dictionary
        """
        annotation_list = self.generate_annotation_list(
            items=response["message"]["items"],
            route=route,
            identifier_key=key,
        )

        annotation_files = self._aws_connector.get_multiple_s3_objs(
            bucket=self._settings.BUCKET,
            s3_objs=annotation_list,
        )

        item_count = 0
        final_response = response
        annotation_names = []

        # build the annotation names
        for annotation in self._valid_annotations:
            annotation_names.append(
                f"{self._settings.LABS_PREFIX}{Path(annotation).stem}"
            )

        modulus = len(self._valid_annotations)
        items_found = defaultdict(int)

        # item_count refers to the index of the item in the list to be annotated
        # items_found is a temporary counter for the number of annotations
        # processed
        for item in annotation_list:
            if len(final_response["message"]["items"]) <= item_count:
                break

            final_response["message"]["items"][item_count][
                f"{self._settings.LABS_PREFIX}{Path(item).stem}"
            ] = {}

            # locate the right annotation
            for annotation in annotation_files:
                if item in annotation:
                    if self._instrumentation:
                        self._instrumentation.logger.info(
                            f"Patching item {item_count} from ({item})"
                        )

                    final_response["message"]["items"][item_count][
                        f"{self._settings.LABS_PREFIX}{Path(item).stem}"
                    ] = json.loads(annotation[item])
                    break

            items_found[item_count] += 1

            if items_found[item_count] == modulus:
                item_count += 1

        return final_response

    def annotate(
        self,
        response: dict,
        route: str,
        identifier_key: str,
        valid_annotations: list[str] = None,
    ) -> dict:
        """
        Annotate an entry
        :param response: the response
        :param route: the route
        :param identifier_key: the identifier key
        :param valid_annotations: a list of valid annotations if you want to override the lookup
        :return: a dictionary
        """
        if "message-type" not in response:
            return response

        self.populate_valid_annotations(route, valid_annotations)

        return (
            self.annotate_item_list(response, route, identifier_key)
            if "list" in response["message-type"]
            else self.annotate_item(response, route, identifier_key)
        )

    def populate_valid_annotations(self, route, valid_annotations):
        # populate the list of valid annotations

        if len(self._valid_annotations) > 0:
            return

        if not valid_annotations:
            route_prefixes = route.split("/")

            if route_prefixes[0] == "" and len(route_prefixes) > 1:
                route_prefix = route_prefixes[1]
            else:
                route_prefix = route_prefixes[0]

            self._valid_annotations = self.get_valid_annotations(route_prefix)
        else:
            self._valid_annotations = valid_annotations
