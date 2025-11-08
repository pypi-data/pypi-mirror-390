#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the async GraphQL client."""

import asyncio
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import anyio
import pytest
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError

from regscale.core.utils.async_graphql_client import (
    AsyncRegScaleGraphQLClient,
    run_async_paginated_query,
)


class TestAsyncRegScaleGraphQLClient(TestCase):
    """Test cases for AsyncRegScaleGraphQLClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.endpoint = "https://test.regscale.com/graphql"
        self.headers = {"Authorization": "Bearer test_token"}
        self.client = AsyncRegScaleGraphQLClient(endpoint=self.endpoint, headers=self.headers, max_concurrent=3)

    def test_init(self):
        """Test client initialization."""
        client = AsyncRegScaleGraphQLClient(
            endpoint=self.endpoint,
            headers=self.headers,
            timeout=45.0,
            max_concurrent=10,
        )

        self.assertEqual(client.endpoint, self.endpoint)
        self.assertEqual(client.headers, self.headers)
        self.assertEqual(client.timeout, 45.0)
        self.assertEqual(client.max_concurrent, 10)

        # Verify _create_client method creates a new client with correct params
        with patch("regscale.core.utils.async_graphql_client.AIOHTTPTransport") as mock_transport_class:
            with patch("regscale.core.utils.async_graphql_client.Client") as mock_client_class:
                client._create_client()

                # Verify transport was created with correct params
                mock_transport_class.assert_called_once()
                call_args = mock_transport_class.call_args
                self.assertEqual(call_args[1]["url"], self.endpoint)
                self.assertEqual(call_args[1]["headers"], self.headers)
                self.assertEqual(call_args[1]["timeout"], 45)  # Converted to int

                # Verify client was created
                mock_client_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_success(self):
        """Test successful query execution."""
        with patch.object(self.client.client, "__aenter__") as mock_aenter:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(
                return_value={
                    "issues": {
                        "items": [{"id": 1, "title": "Test Issue"}],
                        "totalCount": 1,
                    }
                }
            )
            mock_aenter.return_value = mock_session

            query = """
                query {
                    issues(skip: 0, take: 10) {
                        items { id title }
                        totalCount
                    }
                }
            """

            result = await self.client.execute_query(query)

            self.assertIn("issues", result)
            self.assertEqual(result["issues"]["totalCount"], 1)
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_with_variables(self):
        """Test query execution with variables."""
        with patch.object(self.client.client, "__aenter__") as mock_aenter:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(return_value={"data": {"result": "success"}})
            mock_aenter.return_value = mock_session

            query = "query($id: Int!) { issue(id: $id) { title } }"
            variables = {"id": 123}

            await self.client.execute_query(query, variables=variables)

            mock_session.execute.assert_called_once()
            call_args = mock_session.execute.call_args
            self.assertEqual(call_args[1]["variable_values"], variables)

    @pytest.mark.asyncio
    async def test_execute_query_with_auth_error_and_retry(self):
        """Test query execution with auth error and successful retry."""
        token_refresh_callback = Mock(return_value="new_token")
        client = AsyncRegScaleGraphQLClient(
            endpoint=self.endpoint,
            headers=self.headers,
            token_refresh_callback=token_refresh_callback,
        )

        with patch.object(client.client, "__aenter__") as mock_aenter:
            mock_session = AsyncMock()
            # First call fails with auth error, second succeeds
            mock_session.execute = AsyncMock(
                side_effect=[
                    TransportQueryError("AUTH_NOT_AUTHENTICATED"),
                    {"data": {"result": "success"}},
                ]
            )
            mock_aenter.return_value = mock_session

            # Need to patch transport recreation
            with patch("regscale.core.utils.async_graphql_client.AIOHTTPTransport"):
                with patch("regscale.core.utils.async_graphql_client.Client") as mock_client:
                    # Set up the new client
                    new_client = MagicMock()
                    new_session = AsyncMock()
                    new_session.execute = AsyncMock(return_value={"data": {"result": "success"}})
                    new_client.__aenter__ = AsyncMock(return_value=new_session)
                    mock_client.return_value = new_client

                    query = "query { test }"
                    result = await client.execute_query(query)

                    self.assertEqual(result, {"data": {"result": "success"}})
                    token_refresh_callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_query_with_non_auth_error(self):
        """Test query execution with non-auth error."""
        with patch.object(self.client.client, "__aenter__") as mock_aenter:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(side_effect=Exception("Network error"))
            mock_aenter.return_value = mock_session

            query = "query { test }"

            with self.assertRaises(Exception) as context:
                await self.client.execute_query(query)

            self.assertIn("Network error", str(context.exception))

    @pytest.mark.asyncio
    async def test_execute_query_with_progress_callback(self):
        """Test query execution with progress callback."""
        progress_callback = Mock()

        with patch.object(self.client.client, "__aenter__") as mock_aenter:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(return_value={"data": {"test": "data"}})
            mock_aenter.return_value = mock_session

            query = "query { test }"
            await self.client.execute_query(query, progress_callback=progress_callback, task_name="Test Query")

            # Verify progress callbacks were made
            progress_callback.assert_any_call("Test Query", "starting")
            progress_callback.assert_any_call("Test Query", "requesting")
            progress_callback.assert_any_call("Test Query", "completed")

    @pytest.mark.asyncio
    async def test_execute_paginated_query_concurrent(self):
        """Test concurrent paginated query execution."""
        query_builder = Mock(side_effect=lambda skip, take: f"query({skip},{take})")

        with patch.object(self.client, "execute_query", new_callable=AsyncMock) as mock_execute:
            # Simulate 3 pages of results
            mock_execute.side_effect = [
                {"issues": {"items": [{"id": 1}, {"id": 2}]}},
                {"issues": {"items": [{"id": 3}, {"id": 4}]}},
                {"issues": {"items": [{"id": 5}]}},
            ]

            result = await self.client.execute_paginated_query_concurrent(
                query_builder=query_builder,
                topic_key="issues",
                total_count=5,
                page_size=2,
                starting_skip=0,
            )

            self.assertEqual(len(result), 5)
            self.assertEqual(query_builder.call_count, 3)
            self.assertEqual(mock_execute.call_count, 3)

    @pytest.mark.asyncio
    async def test_fetch_single_page_success(self):
        """Test successful single page fetch."""
        with patch.object(self.client, "execute_query", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {"issues": {"items": [{"id": 1}, {"id": 2}], "totalCount": 2}}

            result = await self.client._fetch_single_page(
                query="test query",
                variables={},
                topic_key="issues",
                page_num=1,
            )

            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["id"], 1)

    @pytest.mark.asyncio
    async def test_fetch_single_page_with_none_items(self):
        """Test single page fetch when items is None."""
        with patch.object(self.client, "execute_query", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {"issues": {"items": None, "totalCount": 0}}

            result = await self.client._fetch_single_page(
                query="test query",
                variables={},
                topic_key="issues",
                page_num=1,
            )

            self.assertEqual(result, [])

    @pytest.mark.asyncio
    async def test_fetch_single_page_with_error(self):
        """Test single page fetch with error."""
        with patch.object(self.client, "execute_query", new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = Exception("Query failed")

            with self.assertRaises(Exception) as context:
                await self.client._fetch_single_page(
                    query="test query",
                    variables={},
                    topic_key="issues",
                    page_num=1,
                )

            self.assertIn("Query failed", str(context.exception))

    @pytest.mark.asyncio
    async def test_concurrent_pagination_with_mixed_results(self):
        """Test concurrent pagination with some failures."""
        query_builder = Mock(side_effect=lambda skip, take: f"query({skip},{take})")

        with patch.object(self.client, "execute_query", new_callable=AsyncMock) as mock_execute:
            # Mix of success and failure
            mock_execute.side_effect = [
                {"issues": {"items": [{"id": 1}, {"id": 2}]}},
                Exception("Page 2 failed"),
                {"issues": {"items": [{"id": 3}]}},
            ]

            result = await self.client.execute_paginated_query_concurrent(
                query_builder=query_builder,
                topic_key="issues",
                total_count=5,
                page_size=2,
                starting_skip=0,
            )

            # Should still get results from successful pages
            self.assertEqual(len(result), 3)  # Only pages 1 and 3 succeeded

    def test_run_async_paginated_query(self):
        """Test the synchronous wrapper function."""
        query_builder = Mock(side_effect=lambda skip, take: f"query({skip},{take})")

        with patch("regscale.core.utils.async_graphql_client.AsyncRegScaleGraphQLClient") as mock_client_class:
            mock_client = Mock()
            mock_client.execute_paginated_query_concurrent = AsyncMock(return_value=[{"id": 1}, {"id": 2}])
            mock_client_class.return_value = mock_client

            result = run_async_paginated_query(
                endpoint=self.endpoint,
                headers=self.headers,
                query_builder=query_builder,
                topic_key="issues",
                total_count=2,
                page_size=50,
            )

            self.assertEqual(len(result), 2)
            mock_client_class.assert_called_once()
            mock_client.execute_paginated_query_concurrent.assert_called_once()

    def test_run_async_paginated_query_with_token_refresh(self):
        """Test synchronous wrapper with token refresh callback."""
        query_builder = Mock(side_effect=lambda skip, take: f"query({skip},{take})")
        token_refresh = Mock(return_value="new_token")

        with patch("regscale.core.utils.async_graphql_client.AsyncRegScaleGraphQLClient") as mock_client_class:
            mock_client = Mock()
            mock_client.execute_paginated_query_concurrent = AsyncMock(return_value=[{"id": 1}])
            mock_client_class.return_value = mock_client

            run_async_paginated_query(
                endpoint=self.endpoint,
                headers=self.headers,
                query_builder=query_builder,
                topic_key="issues",
                total_count=1,
                token_refresh_callback=token_refresh,
            )

            # Verify token refresh callback was passed to client
            call_kwargs = mock_client_class.call_args[1]
            self.assertEqual(call_kwargs["token_refresh_callback"], token_refresh)

    @pytest.mark.asyncio
    async def test_semaphore_limiting(self):
        """Test that concurrent requests are limited by semaphore."""
        client = AsyncRegScaleGraphQLClient(endpoint=self.endpoint, headers=self.headers, max_concurrent=2)

        # Track concurrent executions
        concurrent_count = 0
        max_concurrent_seen = 0

        async def slow_execute(*args, **kwargs):
            nonlocal concurrent_count, max_concurrent_seen
            concurrent_count += 1
            max_concurrent_seen = max(max_concurrent_seen, concurrent_count)
            await asyncio.sleep(0.1)
            concurrent_count -= 1
            return {"data": {"items": []}}

        with patch.object(client, "execute_query", side_effect=slow_execute):
            query_builder = Mock(side_effect=lambda skip, take: f"query({skip},{take})")

            # Request 5 pages with max_concurrent=2
            await client.execute_paginated_query_concurrent(
                query_builder=query_builder,
                topic_key="data",
                total_count=10,
                page_size=2,
            )

            # Should never exceed max_concurrent
            self.assertLessEqual(max_concurrent_seen, 2)

    @pytest.mark.asyncio
    async def test_execute_query_with_timeout(self):
        """Test query execution respects timeout."""
        client = AsyncRegScaleGraphQLClient(endpoint=self.endpoint, headers=self.headers, timeout=0.001)

        with patch.object(client.client, "__aenter__") as mock_aenter:
            mock_session = AsyncMock()

            async def slow_execute(*args, **kwargs):
                await asyncio.sleep(1)  # Longer than timeout
                return {"data": {}}

            mock_session.execute = slow_execute
            mock_aenter.return_value = mock_session

            # Should timeout
            with self.assertRaises(Exception):
                await client.execute_query("query { test }")

    @pytest.mark.asyncio
    async def test_ssl_verify_setting(self):
        """Test SSL verification setting from ScannerVariables."""
        with patch("regscale.core.utils.async_graphql_client.ScannerVariables") as mock_vars:
            mock_vars.sslVerify = False

            with patch("regscale.core.utils.async_graphql_client.AIOHTTPTransport") as mock_transport:
                AsyncRegScaleGraphQLClient(endpoint=self.endpoint, headers=self.headers)

                # Verify transport was created with ssl parameter
                mock_transport.assert_called()
                call_args = mock_transport.call_args
                # Check that ssl parameter was set (should be ssl context when verify=False)
                self.assertIsNotNone(call_args[1].get("ssl"))

    @pytest.mark.asyncio
    async def test_auth_error_without_callback(self):
        """Test auth error handling without token refresh callback."""
        client = AsyncRegScaleGraphQLClient(
            endpoint=self.endpoint,
            headers=self.headers,
            token_refresh_callback=None,  # No callback
        )

        with patch.object(client.client, "__aenter__") as mock_aenter:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(side_effect=TransportQueryError("AUTH_NOT_AUTHENTICATED"))
            mock_aenter.return_value = mock_session

            with self.assertRaises(Exception) as context:
                await client.execute_query("query { test }")

            self.assertIn("AUTH_NOT_AUTHENTICATED", str(context.exception))

    @pytest.mark.asyncio
    async def test_multiple_auth_retries_exhausted(self):
        """Test that auth retries are exhausted after max attempts."""
        token_refresh = Mock(return_value="new_token")
        client = AsyncRegScaleGraphQLClient(
            endpoint=self.endpoint,
            headers=self.headers,
            token_refresh_callback=token_refresh,
        )

        with patch.object(client.client, "__aenter__") as mock_aenter:
            mock_session = AsyncMock()
            # Always fail with auth error
            mock_session.execute = AsyncMock(side_effect=TransportQueryError("AUTH_NOT_AUTHENTICATED"))
            mock_aenter.return_value = mock_session

            with patch("regscale.core.utils.async_graphql_client.AIOHTTPTransport"):
                with patch("regscale.core.utils.async_graphql_client.Client"):
                    with self.assertRaises(Exception) as context:
                        await client.execute_query("query { test }")

                    # Should have tried to refresh token once
                    token_refresh.assert_called_once()
                    self.assertIn("Failed to execute query", str(context.exception))

    @pytest.mark.asyncio
    async def test_progress_callback_on_error(self):
        """Test progress callback is called on error."""
        progress_callback = Mock()

        with patch.object(self.client.client, "__aenter__") as mock_aenter:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock(side_effect=Exception("Query error"))
            mock_aenter.return_value = mock_session

            with self.assertRaises(Exception):
                await self.client.execute_query(
                    "query { test }",
                    progress_callback=progress_callback,
                    task_name="Error Query",
                )

            # Should have called failed status
            progress_callback.assert_any_call("Error Query", "starting")
            progress_callback.assert_any_call("Error Query", "requesting")
            progress_callback.assert_any_call("Error Query", "failed")

    @pytest.mark.asyncio
    async def test_concurrent_queries_with_progress(self):
        """Test concurrent queries with progress tracking."""
        progress_callback = Mock()
        query_builder = Mock(side_effect=lambda skip, take: f"query({skip},{take})")

        with patch.object(self.client, "execute_query", new_callable=AsyncMock) as mock_execute:
            mock_execute.side_effect = [
                {"data": {"items": [{"id": 1}]}},
                {"data": {"items": [{"id": 2}]}},
            ]

            result = await self.client.execute_paginated_query_concurrent(
                query_builder=query_builder,
                topic_key="data",
                total_count=2,
                page_size=1,
                progress_callback=progress_callback,
                task_name="Test",
            )

            self.assertEqual(len(result), 2)
            # Verify progress was tracked for each page
            progress_callback.assert_any_call("Test (Page 1/2)", "fetched_1_items")
            progress_callback.assert_any_call("Test (Page 2/2)", "fetched_1_items")
