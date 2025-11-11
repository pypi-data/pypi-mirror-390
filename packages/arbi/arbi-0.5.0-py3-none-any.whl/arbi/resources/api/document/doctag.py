# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ...._utils import maybe_transform, strip_not_given, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.api.document import doctag_create_params, doctag_update_params
from ....types.api.document.doc_tag_response import DocTagResponse
from ....types.api.document.doctag_delete_response import DoctagDeleteResponse

__all__ = ["DoctagResource", "AsyncDoctagResource"]


class DoctagResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DoctagResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#accessing-raw-response-data-eg-headers
        """
        return DoctagResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DoctagResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#with_streaming_response
        """
        return DoctagResourceWithStreamingResponse(self)

    def create(
        self,
        document_ext_id: str,
        *,
        tag_ext_id: str,
        note: Optional[str] | Omit = omit,
        workspace_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocTagResponse:
        """
        Create a doctag by applying a tag to this document.

        Unique constraint ensures each tag can only be applied to a document once
        (idempotent). Note field semantics by tag type:

        - date: note contains the date value (yyyy-mm-dd)
        - annotation: note contains the comment text
        - checkbox/list: note is optional contextual metadata

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        extra_headers = {**strip_not_given({"workspace-key": workspace_key}), **(extra_headers or {})}
        return self._post(
            f"/api/document/{document_ext_id}/doctag",
            body=maybe_transform(
                {
                    "tag_ext_id": tag_ext_id,
                    "note": note,
                },
                doctag_create_params.DoctagCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocTagResponse,
        )

    def update(
        self,
        doctag_ext_id: str,
        *,
        document_ext_id: str,
        note: Optional[str] | Omit = omit,
        workspace_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocTagResponse:
        """Update a doctag's note.

        Can be used to update note for any tag type.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        if not doctag_ext_id:
            raise ValueError(f"Expected a non-empty value for `doctag_ext_id` but received {doctag_ext_id!r}")
        extra_headers = {**strip_not_given({"workspace-key": workspace_key}), **(extra_headers or {})}
        return self._patch(
            f"/api/document/{document_ext_id}/doctag/{doctag_ext_id}",
            body=maybe_transform({"note": note}, doctag_update_params.DoctagUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocTagResponse,
        )

    def delete(
        self,
        doctag_ext_id: str,
        *,
        document_ext_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DoctagDeleteResponse:
        """
        Delete a doctag by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        if not doctag_ext_id:
            raise ValueError(f"Expected a non-empty value for `doctag_ext_id` but received {doctag_ext_id!r}")
        return self._delete(
            f"/api/document/{document_ext_id}/doctag/{doctag_ext_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DoctagDeleteResponse,
        )


class AsyncDoctagResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDoctagResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDoctagResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDoctagResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/arbitrationcity/arbi-python#with_streaming_response
        """
        return AsyncDoctagResourceWithStreamingResponse(self)

    async def create(
        self,
        document_ext_id: str,
        *,
        tag_ext_id: str,
        note: Optional[str] | Omit = omit,
        workspace_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocTagResponse:
        """
        Create a doctag by applying a tag to this document.

        Unique constraint ensures each tag can only be applied to a document once
        (idempotent). Note field semantics by tag type:

        - date: note contains the date value (yyyy-mm-dd)
        - annotation: note contains the comment text
        - checkbox/list: note is optional contextual metadata

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        extra_headers = {**strip_not_given({"workspace-key": workspace_key}), **(extra_headers or {})}
        return await self._post(
            f"/api/document/{document_ext_id}/doctag",
            body=await async_maybe_transform(
                {
                    "tag_ext_id": tag_ext_id,
                    "note": note,
                },
                doctag_create_params.DoctagCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocTagResponse,
        )

    async def update(
        self,
        doctag_ext_id: str,
        *,
        document_ext_id: str,
        note: Optional[str] | Omit = omit,
        workspace_key: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocTagResponse:
        """Update a doctag's note.

        Can be used to update note for any tag type.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        if not doctag_ext_id:
            raise ValueError(f"Expected a non-empty value for `doctag_ext_id` but received {doctag_ext_id!r}")
        extra_headers = {**strip_not_given({"workspace-key": workspace_key}), **(extra_headers or {})}
        return await self._patch(
            f"/api/document/{document_ext_id}/doctag/{doctag_ext_id}",
            body=await async_maybe_transform({"note": note}, doctag_update_params.DoctagUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocTagResponse,
        )

    async def delete(
        self,
        doctag_ext_id: str,
        *,
        document_ext_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DoctagDeleteResponse:
        """
        Delete a doctag by its ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not document_ext_id:
            raise ValueError(f"Expected a non-empty value for `document_ext_id` but received {document_ext_id!r}")
        if not doctag_ext_id:
            raise ValueError(f"Expected a non-empty value for `doctag_ext_id` but received {doctag_ext_id!r}")
        return await self._delete(
            f"/api/document/{document_ext_id}/doctag/{doctag_ext_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DoctagDeleteResponse,
        )


class DoctagResourceWithRawResponse:
    def __init__(self, doctag: DoctagResource) -> None:
        self._doctag = doctag

        self.create = to_raw_response_wrapper(
            doctag.create,
        )
        self.update = to_raw_response_wrapper(
            doctag.update,
        )
        self.delete = to_raw_response_wrapper(
            doctag.delete,
        )


class AsyncDoctagResourceWithRawResponse:
    def __init__(self, doctag: AsyncDoctagResource) -> None:
        self._doctag = doctag

        self.create = async_to_raw_response_wrapper(
            doctag.create,
        )
        self.update = async_to_raw_response_wrapper(
            doctag.update,
        )
        self.delete = async_to_raw_response_wrapper(
            doctag.delete,
        )


class DoctagResourceWithStreamingResponse:
    def __init__(self, doctag: DoctagResource) -> None:
        self._doctag = doctag

        self.create = to_streamed_response_wrapper(
            doctag.create,
        )
        self.update = to_streamed_response_wrapper(
            doctag.update,
        )
        self.delete = to_streamed_response_wrapper(
            doctag.delete,
        )


class AsyncDoctagResourceWithStreamingResponse:
    def __init__(self, doctag: AsyncDoctagResource) -> None:
        self._doctag = doctag

        self.create = async_to_streamed_response_wrapper(
            doctag.create,
        )
        self.update = async_to_streamed_response_wrapper(
            doctag.update,
        )
        self.delete = async_to_streamed_response_wrapper(
            doctag.delete,
        )
