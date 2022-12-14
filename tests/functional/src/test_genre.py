"""
This module tests API that handles genre data.
"""

import http
import json

import pytest
from tests.functional.models import Genre
from tests.functional.settings import test_settings


@pytest.mark.asyncio
class TestGenreApi:
    """Test API that handles genres data."""

    async def test_get_list(
            self,
            storages_clean,
            upload_data_to_es_index,
            make_get_request,
            genres_factory
    ):
        """ Test GET genres list at /api/v1/genres/."""
        # Setup #
        await storages_clean(index_name=test_settings.es_index_genres)

        quantity = 3
        genres = await upload_data_to_es_index(
            quantity=quantity,
            obj_factory=genres_factory,
            index_name=test_settings.es_index_genres,
            es_id_field=test_settings.es_id_field
        ).__anext__()

        # Run #
        response = await make_get_request(url='genres/')

        res = sorted([Genre(**i) for i in response.body], key=lambda x: x.id)
        expected = sorted(genres, key=lambda x: x.id)

        # Assertions #
        assert response.status == http.HTTPStatus.OK
        assert len(response.body) == quantity
        assert res == expected

    async def test_pagination(
            self,
            storages_clean,
            upload_data_to_es_index,
            make_get_request,
            genres_factory,
    ):
        """Test pagination at /api/v1/genres/."""
        # Setup #
        await storages_clean(index_name=test_settings.es_index_genres)

        quantity = 50
        _ = await upload_data_to_es_index(
            quantity=quantity,
            obj_factory=genres_factory,
            index_name=test_settings.es_index_genres,
            es_id_field=test_settings.es_id_field
        ).__anext__()

        # Run #
        response = await make_get_request(
            url='genres/',
            query_data={'page[size]': 20,
                        'page[number]': 3}
        )

        # Assertions #
        assert len(response.body) == 10

    async def test_get_by_id(
            self,
            storages_clean,
            upload_data_to_es_index,
            make_get_request,
            genres_factory,
    ):
        """ Test GET genre by id at /api/v1/genres/{genre_id}."""
        # Setup #
        await storages_clean(index_name=test_settings.es_index_genres)

        quantity = 5
        genres = await upload_data_to_es_index(
            quantity=quantity,
            obj_factory=genres_factory,
            index_name=test_settings.es_index_genres,
            es_id_field=test_settings.es_id_field
        ).__anext__()
        genre = genres[0]

        # Run #
        response = await make_get_request(url=f'genres/{genre.id}')

        # Assertions #
        assert response.status == http.HTTPStatus.OK
        assert Genre(**response.body) == genre.dict()

    async def test_get_by_id_cached(
            self,
            storages_clean,
            upload_data_to_es_index,
            make_get_request,
            genres_factory,
            redis_client,
    ):
        """Test caching for GET genres at /api/v1/genres/{genre_id}."""
        # Setup #
        await storages_clean(index_name=test_settings.es_index_genres)

        quantity = 2
        genres = await upload_data_to_es_index(
            quantity=quantity,
            obj_factory=genres_factory,
            index_name=test_settings.es_index_genres,
            es_id_field=test_settings.es_id_field
        ).__anext__()
        target_genre = genres[0]

        await make_get_request(url=f'genres/{target_genre.id}')

        # Run #
        cached = await redis_client.get(target_genre.id)

        # Assertions #
        assert Genre(**json.loads(cached.decode('utf-8'))) == target_genre

    async def test_not_found(
            self,
            make_get_request,
    ):
        """
        Test the response status when genre is not found by id at
        /api/v1/genres/{genre_id}.
        """
        # Run #
        response = await make_get_request(url='genres/test-uid')

        # Assertions #
        assert response.status == http.HTTPStatus.NOT_FOUND
        assert response.body == {'detail': 'Genre with id test-uid not found'}
