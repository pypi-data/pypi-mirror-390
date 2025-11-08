from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response

from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_404_NOT_FOUND

from django_to_galaxy.models import History
from django_to_galaxy.api.serializers.create_dataset_collection import (
    CollectionListSerializer,
    CollectionListPairedSerializer,
    CollectionPairedSerializer,
)

from bioblend import ConnectionError

example_payload_list = {
    "200": openapi.Response(
        description="Dataset collection created successfully.",
        examples={
            "application/json": {
                "summary": "Example payload",
                "description": "An example of a payload to create a dataset collection.",
                "value": {
                    "history_id": 1,
                    "collection_name": "My Dataset Collection",
                    "elements_names": ["dataset1", "dataset2"],
                    "elements_ids": ["f4b5e6d8a9c0b1e2", "a1b2c3d4e5f60708"],
                },
            }
        },
    )
}

example_payload_list_paired = {
    "200": openapi.Response(
        description="Dataset collection created successfully.",
        examples={
            "application/json": {
                "summary": "Example payload",
                "description": "An example of a payload to create a paired dataset collection.",
                "value": {
                    "history_id": 1,
                    "collection_name": "My Paired Collection",
                    "pairs_names": ["pair1", "pair2"],
                    "first_elements_ids": ["id1", "id2"],
                    "second_elements_ids": ["id3", "id4"],
                },
            }
        },
    )
}

example_payload_paired = {
    "200": openapi.Response(
        description="Dataset collection created successfully.",
        examples={
            "application/json": {
                "summary": "Example payload",
                "description": "An example of a payload to create a paired dataset collection.",
                "value": {
                    "history_id": 1,
                    "collection_name": "My Paired Collection",
                    "first_element_id": "id1",
                    "second_element_id": "id2",
                },
            }
        },
    )
}


class CreateDatasetListCollectionView(GenericAPIView):
    """
    API endpoint to create a dataset collection (list) in a Galaxy history.

    - POST: Creates a dataset collection in a specified Galaxy history.
    - Serializer: CollectionListSerializer
    - Returns: JSON response with collection details or connection errors.
    """

    serializer_class = CollectionListSerializer

    @swagger_auto_schema(
        operation_description="Create a dataset collection with dataset of an Galaxy history.",
        operation_summary="Create a dataset collection with dataset of an Galaxy history.",
        tags=["collections"],
        responses=example_payload_list,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "history_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                "collection_name": openapi.Schema(
                    type=openapi.TYPE_STRING, example="My Dataset Collection"
                ),
                "elements_names": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    example=["dataset1", "dataset2"],
                ),
                "elements_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    example=["f4b5e6d8a9c0b1e2", "a1b2c3d4e5f60708"],
                ),
            },
            required=[
                "history_id",
                "collection_name",
                "elements_names",
                "elements_ids",
            ],
        ),
    )
    def post(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        # Retrieve history
        try:
            history = History.objects.get(id=data["history_id"])
        except ObjectDoesNotExist:
            return Response(
                {
                    "message": (
                        "Galaxy history with id ",
                        f"<{data['history_id']}> not found!",
                    )
                },
                status=HTTP_404_NOT_FOUND,
            )
        # Collect ConnectionError exceptions
        connection_errors = []
        datasets = []
        # Check each dataset id
        for i in range(len(data.get("elements_names", []))):
            try:
                dataset = history.galaxy_owner.obj_gi.gi.datasets.show_dataset(
                    data["elements_ids"][i]
                )
                datasets.append(dataset)
            except ConnectionError as e:
                connection_errors.append(
                    {
                        "index": i,
                        "type": "elements_ids",
                        "id": data["elements_ids"][i],
                        "error": str(e),
                    }
                )
                datasets.append(None)

        # If any errors, return them as final response
        if connection_errors:
            return Response({"connection_errors": connection_errors}, status=400)

        # Retrieve file & file path
        collection_datamap = {
            "name": data["collection_name"],
            "collection_type": "list",
            "element_identifiers": [],
        }

        for i in range(len(data.get("elements_names", []))):
            if datasets[i] is not None:
                collection_datamap["element_identifiers"].append(
                    {
                        "name": data["elements_names"][i],
                        "src": "hda",
                        "id": data["elements_ids"][i],
                    }
                )
        try:
            history_association = history.galaxy_history.create_dataset_collection(
                collection_description=collection_datamap
            )
        except ConnectionError as e:
            connection_errors.append(
                {"type": "create_dataset_collection", "error": str(e)}
            )
            return Response({"connection_errors": connection_errors}, status=400)

        message = (
            "Collection of list of dataset has "
            f"been created to Galaxy History <{str(history)}>"
        )
        return Response(
            {
                "message": message,
                "history_association_id": history_association.id,
                "history_id": history.id,
            }
        )


class CreateDatasetListPairedCollectionView(GenericAPIView):
    """
    API endpoint to create a paired dataset collection (list:paired) in a Galaxy history.

    - POST: Creates a paired dataset collection in a specified Galaxy history.
    - Serializer: CollectionListPairedSerializer
    - Returns: JSON response with collection details or connection errors.
    """

    serializer_class = CollectionListPairedSerializer

    @swagger_auto_schema(
        operation_description=(
            "Create a paired dataset collection " "(list:paired) in a Galaxy history."
        ),
        operation_summary="Create a paired dataset collection (list:paired) in a Galaxy history.",
        tags=["collections"],
        responses=example_payload_list_paired,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "history_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                "collection_name": openapi.Schema(
                    type=openapi.TYPE_STRING, example="My Paired Collection"
                ),
                "pairs_names": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    example=["pair1", "pair2"],
                ),
                "first_elements_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    example=["id1", "id2"],
                ),
                "second_elements_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    example=["id3", "id4"],
                ),
            },
            required=[
                "history_id",
                "collection_name",
                "pairs_names",
                "first_elements_ids",
                "second_elements_ids",
            ],
        ),
    )
    def post(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        # Retrieve history
        try:
            history = History.objects.get(id=data["history_id"])
        except ObjectDoesNotExist:
            return Response(
                {
                    "message": (
                        "Galaxy history with id ",
                        f"<{data['history_id']}> not found!",
                    )
                },
                status=HTTP_404_NOT_FOUND,
            )
        # Collect ConnectionError exceptions
        connection_errors = []
        first_datasets = []
        second_datasets = []
        # Check each dataset id
        for i in range(len(data.get("pairs_names", []))):
            try:
                first_dataset = history.galaxy_owner.obj_gi.gi.datasets.show_dataset(
                    data["first_elements_ids"][i]
                )
                first_datasets.append(first_dataset)
            except ConnectionError as e:
                connection_errors.append(
                    {
                        "index": i,
                        "type": "first_elements_ids",
                        "id": data["first_elements_ids"][i],
                        "error": str(e),
                    }
                )
                first_datasets.append(None)
            try:
                second_dataset = history.galaxy_owner.obj_gi.gi.datasets.show_dataset(
                    data["second_elements_ids"][i]
                )
                second_datasets.append(second_dataset)
            except ConnectionError as e:
                connection_errors.append(
                    {
                        "index": i,
                        "type": "second_elements_ids",
                        "id": data["second_elements_ids"][i],
                        "error": str(e),
                    }
                )
                second_datasets.append(None)

        # If any errors, return them as final response
        if connection_errors:
            return Response({"connection_errors": connection_errors}, status=400)

        # Retrieve file & file path
        collection_datamap = {
            "name": data["collection_name"],
            "collection_type": "list:paired",
            "element_identifiers": [],
        }

        for i in range(len(data.get("pairs_names", []))):
            if first_datasets[i] is not None and second_datasets[i] is not None:
                collection_datamap["element_identifiers"].append(
                    {
                        "name": data["pairs_names"][i],
                        "src": "new_collection",
                        "collection_type": "paired",
                        "element_identifiers": [
                            {
                                "name": "forward",
                                "src": "hda",
                                "id": data["first_elements_ids"][i],
                            },
                            {
                                "name": "reverse",
                                "src": "hda",
                                "id": data["second_elements_ids"][i],
                            },
                        ],
                    }
                )

        try:
            history_association = history.galaxy_history.create_dataset_collection(
                collection_description=collection_datamap
            )
        except ConnectionError as e:
            connection_errors.append(
                {"type": "create_dataset_collection", "error": str(e)}
            )
            return Response({"connection_errors": connection_errors}, status=400)

        message = (
            "Collection of paired dataset has been "
            f"created to Galaxy History <{str(history)}>"
        )
        return Response(
            {
                "message": message,
                "history_association_id": history_association.id,
                "history_id": history.id,
            }
        )


class CreateDatasetPairedCollectionView(GenericAPIView):
    """
    API endpoint to create a paired dataset collection in a Galaxy history.

    - POST: Creates a paired dataset collection in a specified Galaxy history.
    - Serializer: CollectionPairedSerializer
    - Returns: JSON response with collection details or connection errors.
    """

    serializer_class = CollectionPairedSerializer

    @swagger_auto_schema(
        operation_description="Create a paired dataset collection in a Galaxy history.",
        operation_summary="Create a paired dataset collection in a Galaxy history.",
        tags=["collections"],
        responses=example_payload_paired,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "history_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                "collection_name": openapi.Schema(
                    type=openapi.TYPE_STRING, example="My Paired Collection"
                ),
                "first_element_id": openapi.Schema(
                    type=openapi.TYPE_STRING, example="id1"
                ),
                "second_element_id": openapi.Schema(
                    type=openapi.TYPE_STRING, example="id2"
                ),
            },
            required=[
                "history_id",
                "collection_name",
                "first_element_id",
                "second_element_id",
            ],
        ),
    )
    def post(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        # Retrieve history
        try:
            history = History.objects.get(id=data["history_id"])
        except ObjectDoesNotExist:
            return Response(
                {
                    "message": (
                        "Galaxy history with id ",
                        f"<{data['history_id']}> not found!",
                    )
                },
                status=HTTP_404_NOT_FOUND,
            )

        # Check each dataset id
        try:
            history.galaxy_owner.obj_gi.gi.datasets.show_dataset(
                data["first_element_id"]
            )
        except ConnectionError:
            return Response({"message": "first_element_id is not valid"}, status=400)

        try:
            history.galaxy_owner.obj_gi.gi.datasets.show_dataset(
                data["second_element_id"]
            )
        except ConnectionError:
            return Response({"message": "second_element_id is not valid"}, status=400)

        # Retrieve file & file path
        collection_datamap = {
            "name": data["collection_name"],
            "collection_type": "paired",
            "element_identifiers": [
                {"name": "forward", "src": "hda", "id": data["first_element_id"]},
                {"name": "reverse", "src": "hda", "id": data["second_element_id"]},
            ],
        }

        try:
            history_association = history.galaxy_history.create_dataset_collection(
                collection_description=collection_datamap
            )
        except ConnectionError as e:
            return Response(
                {"message": str(e)},
                status=400,
            )
        message = (
            "Collection of paired dataset has been "
            f"created to Galaxy History <{str(history)}>"
        )

        return Response(
            {
                "message": message,
                "history_association_id": history_association.id,
                "history_id": history.id,
            }
        )
