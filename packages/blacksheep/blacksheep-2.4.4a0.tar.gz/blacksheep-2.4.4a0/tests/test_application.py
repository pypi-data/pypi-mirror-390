import asyncio
import json
import os
import re
import sys
from base64 import urlsafe_b64decode, urlsafe_b64encode
from collections.abc import AsyncIterable
from dataclasses import dataclass
from datetime import date, datetime
from functools import wraps
from typing import Annotated, Any, Dict, Generic, List, Optional, TypeVar
from uuid import UUID, uuid4

import pytest
from guardpost import AuthenticationHandler, Identity, User
from openapidocs.v3 import Info
from pydantic import VERSION as PYDANTIC_LIB_VERSION
from pydantic import BaseModel, Field, ValidationError
from rodi import Container, inject

from blacksheep import (
    HTTPException,
    JSONContent,
    Request,
    Response,
    TextContent,
)
from blacksheep.contents import FormPart
from blacksheep.exceptions import (
    Conflict,
    InternalServerError,
    InvalidExceptionHandler,
    NotFound,
)
from blacksheep.server.application import Application, ApplicationSyncEvent
from blacksheep.server.bindings import (
    ClientInfo,
    FromBytes,
    FromCookie,
    FromFiles,
    FromForm,
    FromHeader,
    FromJSON,
    FromQuery,
    FromRoute,
    FromServices,
    FromText,
    RequestUser,
    ServerInfo,
)
from blacksheep.server.di import di_scope_middleware
from blacksheep.server.normalization import ensure_response
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.resources import get_resource_file_path
from blacksheep.server.responses import status_code, text
from blacksheep.server.routing import Router, SharedRouterError
from blacksheep.server.security.hsts import HSTSMiddleware
from blacksheep.server.sse import ServerSentEvent, TextServerSentEvent
from blacksheep.testing.helpers import get_example_scope
from blacksheep.testing.messages import MockReceive, MockSend
from tests.utils.application import FakeApplication
from tests.utils.folder import ensure_folder

try:
    # v2
    from pydantic import validate_call
except ImportError:
    # v1
    # v1 validate_arguments is not supported
    # https://github.com/Neoteroi/BlackSheep/issues/559
    validate_call = None


class Item:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c


@dataclass
class Item2:
    a: str
    b: str
    c: str


class Foo:
    def __init__(self, item) -> None:
        self.item = Item(**item)


def read_multipart_mix_dat():
    with open(
        get_resource_file_path("tests", os.path.join("res", "multipart-mix.dat")),
        mode="rb",
    ) as dat_file:
        return dat_file.read()


async def test_application_supports_dynamic_attributes(app):
    foo = object()

    assert (
        hasattr(app, "foo") is False
    ), "This test makes sense if such attribute is not defined"
    app.foo = foo  # type: ignore
    assert app.foo is foo  # type: ignore


async def test_application_get_handler(app):
    @app.router.get("/")
    async def home(request):
        pass

    @app.router.get("/foo")
    async def foo(request):
        pass

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())

    assert app.request is not None
    request: Request = app.request

    assert request is not None

    connection = request.headers[b"connection"]
    assert connection == (b"keep-alive",)


async def test_application_post_multipart_formdata(app):
    @app.router.post("/files/upload")
    async def upload_files(request):
        data = await request.multipart()
        assert data is not None

        assert data[0].name == b"text1"
        assert data[0].file_name is None
        assert data[0].content_type is None
        assert data[0].data == b"text default"

        assert data[1].name == b"text2"
        assert data[1].file_name is None
        assert data[1].content_type is None
        assert data[1].data == "aωb".encode("utf8")

        assert data[2].name == b"file1"
        assert data[2].file_name == b"a.txt"
        assert data[2].content_type == b"text/plain"
        assert data[2].data == b"Content of a.txt.\r\n"

        assert data[3].name == b"file2"
        assert data[3].file_name == b"a.html"
        assert data[3].content_type == b"text/html"
        assert data[3].data == b"<!DOCTYPE html><title>Content of a.html.</title>\r\n"

        assert data[4].name == b"file3"
        assert data[4].file_name == b"binary"
        assert data[4].content_type == b"application/octet-stream"
        assert data[4].data == "aωb".encode("utf8")

        files = await request.files()

        assert files[0].name == b"file1"
        assert files[0].file_name == b"a.txt"
        assert files[0].content_type == b"text/plain"
        assert files[0].data == b"Content of a.txt.\r\n"

        assert files[1].name == b"file2"
        assert files[1].file_name == b"a.html"
        assert files[1].content_type == b"text/html"
        assert files[1].data == b"<!DOCTYPE html><title>Content of a.html.</title>\r\n"

        assert files[2].name == b"file3"
        assert files[2].file_name == b"binary"
        assert files[2].content_type == b"application/octet-stream"
        assert files[2].data == "aωb".encode("utf8")

        file_one = await request.files("file1")
        assert file_one[0].name == b"file1"

        return Response(200)

    boundary = b"---------------------0000000000000000000000001"

    content = b"\r\n".join(
        [
            boundary,
            b'Content-Disposition: form-data; name="text1"',
            b"",
            b"text default",
            boundary,
            b'Content-Disposition: form-data; name="text2"',
            b"",
            "aωb".encode("utf8"),
            boundary,
            b'Content-Disposition: form-data; name="file1"; filename="a.txt"',
            b"Content-Type: text/plain",
            b"",
            b"Content of a.txt.",
            b"",
            boundary,
            b'Content-Disposition: form-data; name="file2"; filename="a.html"',
            b"Content-Type: text/html",
            b"",
            b"<!DOCTYPE html><title>Content of a.html.</title>",
            b"",
            boundary,
            b'Content-Disposition: form-data; name="file3"; filename="binary"',
            b"Content-Type: application/octet-stream",
            b"",
            "aωb".encode("utf8"),
            boundary + b"--",
        ]
    )
    await app(
        get_example_scope(
            "POST",
            "/files/upload",
            [
                (b"content-length", str(len(content)).encode()),
                (b"content-type", b"multipart/form-data; boundary=" + boundary),
            ],
        ),
        MockReceive([content]),
        MockSend(),
    )

    assert app.response is not None
    response: Response = app.response

    data = await response.text()

    assert response is not None
    assert response.status == 200, data


async def test_application_post_handler(app):
    called_times = 0

    @app.router.post("/api/cat")
    async def create_cat(request):
        nonlocal called_times
        called_times += 1
        assert request is not None

        content = await request.read()
        assert b'{"name":"Celine","kind":"Persian"}' == content

        data = await request.json()
        assert {"name": "Celine", "kind": "Persian"} == data

        return Response(201, [(b"Server", b"Python/3.7")], JSONContent({"id": "123"}))

    content = b'{"name":"Celine","kind":"Persian"}'

    await app(
        get_example_scope(
            "POST",
            "/api/cat",
            [
                (b"content-length", str(len(content)).encode()),
                (b"content-type", b"application/json"),
            ],
        ),
        MockReceive([content]),
        MockSend(),
    )

    response = app.response
    assert called_times == 1
    response_data = await response.json()
    assert {"id": "123"} == response_data


async def test_application_post_handler_invalid_content_type(app):
    called_times = 0

    @app.router.post("/api/cat")
    async def create_cat(request):
        nonlocal called_times
        called_times += 1
        assert request is not None

        content = await request.read()
        assert b'{"name":"Celine","kind":"Persian"}' == content

        data = await request.json()
        assert data is None

        return Response(400)

    content = b'{"name":"Celine","kind":"Persian"}'

    await app(
        get_example_scope(
            "POST",
            "/api/cat",
            [
                (b"content-length", str(len(content)).encode()),
                (b"content-type", b"text/plain"),
            ],
        ),
        MockReceive([content]),
        MockSend(),
    )

    response: Response = app.response
    assert called_times == 1
    assert response.status == 400


async def test_application_post_json_handles_missing_body(app):
    @app.router.post("/api/cat")
    async def create_cat(request):
        assert request is not None

        content = await request.read()
        assert b"" == content

        text = await request.text()
        assert "" == text

        data = await request.json()
        assert data is None

        return Response(201)

    await app(
        get_example_scope("POST", "/api/cat", []),
        MockReceive([]),
        MockSend(),
    )

    response = app.response
    assert response.status == 201


async def test_application_returns_400_for_invalid_json(app):
    @app.router.post("/api/cat")
    async def create_cat(request):
        await request.json()
        ...

    # invalid JSON:
    content = b'"name":"Celine";"kind":"Persian"'

    await app(
        get_example_scope(
            "POST",
            "/api/cat",
            [
                (b"content-length", str(len(content)).encode()),
                (b"content-type", b"application/json"),
            ],
        ),
        MockReceive([content]),
        MockSend(),
    )

    response = app.response
    assert response.status == 400
    assert response.content.body == (
        b"Bad Request: Declared Content-Type is application/json but "
        b"the content cannot be parsed as JSON."
    )


async def test_application_middlewares_one(app):
    calls = []

    async def middleware_one(request, handler):
        nonlocal calls
        calls.append(1)
        response = await handler(request)
        calls.append(2)
        return response

    async def middleware_two(request, handler):
        nonlocal calls
        calls.append(3)
        response = await handler(request)
        calls.append(4)
        return response

    @app.router.get("/")
    async def example(request):
        nonlocal calls
        calls.append(5)
        return Response(200, [(b"Server", b"Python/3.7")], JSONContent({"id": "123"}))

    app.middlewares.append(middleware_one)
    app.middlewares.append(middleware_two)

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())

    assert app.response is not None
    response: Response = app.response

    assert response is not None
    assert response.status == 200
    assert calls == [1, 3, 5, 4, 2]


async def test_application_middlewares_as_classes(app):
    calls = []

    class MiddlewareExample:
        def __init__(self, calls: List[int], seed: int) -> None:
            self.seed = seed
            self.calls = calls

        def get_seed(self) -> int:
            self.seed += 1
            return self.seed

        async def __call__(self, request, handler):
            self.calls.append(self.get_seed())
            response = await handler(request)
            self.calls.append(self.get_seed())
            return response

    @app.router.route("/")
    async def example(request):
        nonlocal calls
        calls.append(5)
        return Response(200, [(b"Server", b"Python/3.7")], JSONContent({"id": "123"}))

    app.middlewares.append(MiddlewareExample(calls, 0))
    app.middlewares.append(MiddlewareExample(calls, 2))

    await app(get_example_scope("GET", "/"), MockReceive([]), MockSend())

    assert app.response is not None
    response: Response = app.response

    assert response is not None
    assert response.status == 200
    assert calls == [1, 3, 5, 4, 2]


async def test_application_middlewares_are_applied_only_once(app):
    """
    This test checks that the same request handled bound to several routes
    is normalized only once with middlewares, and that more calls to
    configure_middlewares don't apply several times the chain of middlewares.
    """
    calls = []

    async def example(request: Request):
        nonlocal calls
        calls.append(2)
        return None

    app.router.add_get("/", example)
    app.router.add_head("/", example)

    async def middleware(request, handler):
        nonlocal calls
        calls.append(1)
        response = await handler(request)
        return response

    app.middlewares.append(middleware)

    for method, _ in {("GET", 1), ("GET", 2), ("HEAD", 1), ("HEAD", 2)}:
        await app(get_example_scope(method, "/"), MockReceive([]), MockSend())

        assert app.response is not None
        response: Response = app.response

        assert response is not None
        assert response.status == 204
        assert calls == [1, 2]

        calls.clear()


async def test_application_middlewares_two(app):
    calls = []

    async def middleware_one(request, handler):
        nonlocal calls
        calls.append(1)
        response = await handler(request)
        calls.append(2)
        return response

    async def middleware_two(request, handler):
        nonlocal calls
        calls.append(3)
        response = await handler(request)
        calls.append(4)
        return response

    async def middleware_three(request, handler):
        nonlocal calls
        calls.append(6)
        response = await handler(request)
        calls.append(7)
        return response

    @app.router.get("/")
    async def example(request):
        nonlocal calls
        calls.append(5)
        return Response(200, [(b"Server", b"Python/3.7")], JSONContent({"id": "123"}))

    app.middlewares.append(middleware_one)
    app.middlewares.append(middleware_two)
    app.middlewares.append(middleware_three)

    await app(get_example_scope("GET", "/"), MockReceive([]), MockSend())

    assert app.response is not None
    response: Response = app.response

    assert response is not None
    assert response.status == 200
    assert calls == [1, 3, 6, 5, 7, 4, 2]


async def test_application_middlewares_skip_handler(app):
    calls = []

    async def middleware_one(request, handler):
        nonlocal calls
        calls.append(1)
        response = await handler(request)
        calls.append(2)
        return response

    async def middleware_two(request, handler):
        nonlocal calls
        calls.append(3)
        response = await handler(request)
        calls.append(4)
        return response

    async def middleware_three(request, handler):
        nonlocal calls
        calls.append(6)
        return Response(403)

    @app.router.get("/")
    async def example(request):
        nonlocal calls
        calls.append(5)
        return Response(200, [(b"Server", b"Python/3.7")], JSONContent({"id": "123"}))

    app.middlewares.append(middleware_one)
    app.middlewares.append(middleware_two)
    app.middlewares.append(middleware_three)

    await app(get_example_scope("GET", "/"), MockReceive([]), MockSend())

    assert app.response is not None
    response: Response = app.response

    assert response is not None
    assert response.status == 403
    assert calls == [1, 3, 6, 4, 2]


async def test_application_post_multipart_formdata_files_handler(app):
    ensure_folder("out")
    ensure_folder("tests/out")

    @app.router.post("/files/upload")
    async def upload_files(request):
        files = await request.files("files[]")

        # NB: in this example; we save files to output folder and verify
        # that their binaries are identical
        for part in files:
            full_path = get_resource_file_path(
                "tests", f"out/{part.file_name.decode()}"
            )
            with open(full_path, mode="wb") as saved_file:
                saved_file.write(part.data)

        return Response(200)

    boundary = b"---------------------0000000000000000000000001"
    lines = []

    file_names = {
        "pexels-photo-126407.jpeg",
        "pexels-photo-302280.jpeg",
        "pexels-photo-730896.jpeg",
    }

    rel_path = "files/"

    for file_name in file_names:
        full_path = get_resource_file_path("tests", f"{rel_path}{file_name}")
        with open(full_path, mode="rb") as source_file:
            binary = source_file.read()
            lines += [
                boundary,
                b'Content-Disposition: form-data; name="files[]"; filename="'
                + file_name.encode()
                + b'"',
                b"",
                binary,
            ]

    lines += [boundary + b"--"]
    content = b"\r\n".join(lines)

    await app(
        get_example_scope(
            "POST",
            "/files/upload",
            [
                [b"content-length", str(len(content)).encode()],
                [b"content-type", b"multipart/form-data; boundary=" + boundary],
            ],
        ),
        MockReceive([content]),
        MockSend(),
    )

    assert app.response is not None
    response: Response = app.response

    body = await response.text()
    assert response.status == 200, body

    # now files are in both folders: compare to ensure they are identical
    for file_name in file_names:
        full_path = get_resource_file_path("tests", f"{rel_path}{file_name}")
        copy_full_path = get_resource_file_path("tests", f"out/{file_name}")

        with open(full_path, mode="rb") as source_file:
            binary = source_file.read()
            with open(copy_full_path, mode="rb") as file_clone:
                clone_binary = file_clone.read()

                assert binary == clone_binary


async def test_application_http_exception_handlers(app):
    called = False

    async def exception_handler(self, request, http_exception):
        nonlocal called
        assert request is not None
        called = True
        return Response(200, content=TextContent("Called"))

    app.exceptions_handlers[519] = exception_handler

    @app.router.get("/")
    async def home(request):
        raise HTTPException(519)

    await app(get_example_scope("GET", "/"), MockReceive, MockSend())

    assert app.response is not None
    response: Response = app.response

    assert response is not None
    assert called is True, "Http exception handler was called"

    text = await response.text()
    assert text == "Called", (
        "The response is the one returned by " "defined http exception handler"
    )


async def test_application_invalid_exception_handler(app):
    # https://github.com/Neoteroi/BlackSheep/issues/592
    async def exception_handler(request, http_exception):
        pass

    with pytest.raises(InvalidExceptionHandler):
        app.exceptions_handlers[500] = exception_handler


async def test_application_failing_exception_handler(app):
    # https://github.com/Neoteroi/BlackSheep/issues/592
    async def exception_handler(app, request, http_exception):
        raise Exception("Invalid handler!")

    app.exceptions_handlers[519] = exception_handler

    @app.router.get("/")
    async def home(request):
        raise HTTPException(519)

    await app(get_example_scope("GET", "/"), MockReceive, MockSend())

    assert app.response is not None
    response: Response = app.response

    assert response is not None

    text = await response.text()
    assert text == "Internal Server Error"


async def test_application_http_exception_handlers_called_in_application_context(app):
    async def exception_handler(self, request, http_exception):
        nonlocal app
        assert self is app
        return Response(200, content=TextContent("Called"))

    app.exceptions_handlers[519] = exception_handler

    @app.router.get("/")
    async def home(request):
        raise HTTPException(519)

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())
    assert app.response is not None
    response: Response = app.response

    assert response is not None
    text = await response.text()
    assert text == "Called", (
        "The response is the one returned by " "defined http exception handler"
    )


async def test_application_user_defined_exception_handlers(app):
    called = False

    class CustomException(Exception):
        pass

    async def exception_handler(self, request, exception: CustomException):
        nonlocal called
        assert request is not None
        called = True
        return Response(200, content=TextContent("Called"))

    app.exceptions_handlers[CustomException] = exception_handler

    @app.router.get("/")
    async def home(request):
        raise CustomException()

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())

    assert app.response is not None
    response: Response = app.response

    assert response is not None
    assert called is True, "Http exception handler was called"

    text = await response.text()
    assert text == "Called", (
        "The response is the one returned by " "defined http exception handler"
    )


async def test_user_defined_exception_handlers_called_in_application_context(app):
    class CustomException(Exception):
        pass

    async def exception_handler(
        self: FakeApplication, request: Request, exc: CustomException
    ) -> Response:
        nonlocal app
        assert self is app
        assert isinstance(exc, CustomException)
        return Response(200, content=TextContent("Called"))

    app.exceptions_handlers[CustomException] = exception_handler

    @app.router.get("/")
    async def home(request):
        raise CustomException()

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())

    assert app.response is not None
    response: Response = app.response

    assert response is not None
    text = await response.text()
    assert text == "Called", (
        "The response is the one returned by " "defined http exception handler"
    )


async def test_application_exception_handler_decorator_by_custom_exception(app):
    expected_handler_response_text = "Called"

    class CustomException(Exception):
        pass

    @app.exception_handler(CustomException)
    async def exception_handler(
        self: FakeApplication, request: Request, exc: CustomException
    ) -> Response:
        nonlocal app
        assert self is app
        assert isinstance(exc, CustomException)
        return Response(200, content=TextContent("Called"))

    @app.router.get("/")
    async def home(request):
        raise CustomException()

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())

    assert app.response is not None
    response: Response = app.response

    assert response
    actual_response_text = await response.text()
    assert actual_response_text == expected_handler_response_text


async def test_application_exception_handler_decorator_by_http_status_code(app):
    expected_exception_status_code = 519
    expected_handler_response_text = "Called"

    @app.exception_handler(519)
    async def exception_handler(self, request: Request, exc: HTTPException) -> Response:
        assert isinstance(exc, HTTPException)
        assert exc.status == expected_exception_status_code
        return Response(200, content=TextContent("Called"))

    @app.router.get("/")
    async def home(request):
        raise HTTPException(519)

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())

    assert app.response
    response: Response = app.response

    assert response

    actual_response_text = await response.text()

    assert actual_response_text == expected_handler_response_text


@pytest.mark.parametrize(
    "parameter,expected_value",
    [("a", "a"), ("foo", "foo"), ("Hello%20World!!%3B%3B", "Hello World!!;;")],
)
async def test_handler_route_value_binding_single(parameter, expected_value, app):
    called = False

    @app.router.get("/:value")
    async def home(request, value):
        nonlocal called
        called = True
        assert value == expected_value

    await app(get_example_scope("GET", "/" + parameter), MockReceive(), MockSend())

    assert app.response.status == 204


@pytest.mark.parametrize(
    "parameter,expected_a,expected_b",
    [
        ("a/b", "a", "b"),
        ("foo/something", "foo", "something"),
        ("Hello%20World!!%3B%3B/another", "Hello World!!;;", "another"),
    ],
)
async def test_handler_route_value_binding_two(parameter, expected_a, expected_b, app):
    @app.router.get("/:a/:b")
    async def home(request, a, b):
        assert a == expected_a
        assert b == expected_b

    await app(get_example_scope("GET", "/" + parameter), MockReceive(), MockSend())
    assert app.response.status == 204


@pytest.mark.parametrize(
    "parameter,expected_value", [("12", 12), ("0", 0), ("16549", 16549)]
)
async def test_handler_route_value_binding_single_int(parameter, expected_value, app):
    called = False

    @app.router.get("/:value")
    async def home(request, value: int):
        nonlocal called
        called = True
        assert value == expected_value

    await app(get_example_scope("GET", "/" + parameter), MockReceive(), MockSend())

    assert app.response.status == 204


@pytest.mark.parametrize("parameter", ["xx", "x"])
async def test_handler_route_value_binding_single_int_invalid(parameter, app):
    called = False

    @app.router.get("/:value")
    async def home(request, value: int):
        nonlocal called
        called = True

    await app(get_example_scope("GET", "/" + parameter), MockReceive(), MockSend())

    assert called is False
    assert app.response.status == 400


@pytest.mark.parametrize("parameter", ["xx", "x"])
async def test_handler_route_value_binding_single_float_invalid(parameter, app):
    called = False

    @app.router.get("/:value")
    async def home(request, value: float):
        nonlocal called
        called = True

    await app(get_example_scope("GET", "/" + parameter), MockReceive(), MockSend())

    assert called is False
    assert app.response.status == 400


@pytest.mark.parametrize(
    "parameter,expected_value", [("12", 12.0), ("0", 0.0), ("16549.55", 16549.55)]
)
async def test_handler_route_value_binding_single_float(parameter, expected_value, app):
    called = False

    @app.router.get("/:value")
    async def home(request, value: float):
        nonlocal called
        called = True
        assert value == expected_value

    await app(get_example_scope("GET", "/" + parameter), MockReceive(), MockSend())

    assert app.response.status == 204


@pytest.mark.parametrize(
    "parameter,expected_a,expected_b,expected_c",
    [
        ("a/1/12.50", "a", 1, 12.50),
        ("foo/446/500", "foo", 446, 500.0),
        ("Hello%20World!!%3B%3B/60/88.05", "Hello World!!;;", 60, 88.05),
    ],
)
async def test_handler_route_value_binding_mixed_types(
    parameter, expected_a, expected_b, expected_c, app
):
    @app.router.get("/:a/:b/:c")
    async def home(request, a: str, b: int, c: float):
        assert a == expected_a
        assert b == expected_b
        assert c == expected_c

    await app(get_example_scope("GET", "/" + parameter), MockReceive(), MockSend())
    assert app.response.status == 204


@pytest.mark.parametrize(
    "query,expected_value",
    [
        (b"a=a", ["a"]),
        (b"a=foo", ["foo"]),
        (b"a=Hello%20World!!%3B%3B", ["Hello World!!;;"]),
    ],
)
async def test_handler_query_value_binding_single(query, expected_value, app):
    @app.router.get("/")
    async def home(request, a):
        assert a == expected_value

    await app(get_example_scope("GET", "/", query=query), MockReceive(), MockSend())

    assert app.response.status == 204


@pytest.mark.parametrize(
    "query,expected_value", [(b"a=10", 10), (b"b=20", None), (b"", None)]
)
async def test_handler_query_value_binding_optional_int(query, expected_value, app):
    @app.router.get("/")
    async def home(request, a: Optional[int]):
        assert a == expected_value

    await app(get_example_scope("GET", "/", query=query), MockReceive(), MockSend())
    assert app.response.status == 204


@pytest.mark.parametrize(
    "query,expected_value",
    [
        (b"a=10", 10.0),
        (b"a=12.6", 12.6),
        (b"a=12.6&c=4", 12.6),
        (b"b=20", None),
        (b"", None),
    ],
)
async def test_handler_query_value_binding_optional_float(query, expected_value, app):
    @app.router.get("/")
    async def home(request, a: Optional[float]):
        assert a == expected_value

    await app(get_example_scope("GET", "/", query=query), MockReceive(), MockSend())
    assert app.response.status == 204


@pytest.mark.parametrize(
    "query,expected_value",
    [
        (b"a=10", [10.0]),
        (b"a=12.6", [12.6]),
        (b"a=12.6&c=4", [12.6]),
        (b"a=12.6&a=4&a=6.6", [12.6, 4.0, 6.6]),
        (b"b=20", None),
        (b"", None),
    ],
)
async def test_handler_query_value_binding_optional_list(query, expected_value, app):
    @app.router.get("/")
    async def home(request, a: Optional[List[float]]):
        assert a == expected_value

    await app(get_example_scope("GET", "/", query=query), MockReceive(), MockSend())
    assert app.response.status == 204


@pytest.mark.parametrize(
    "query,expected_a,expected_b,expected_c",
    [
        (b"a=a&b=1&c=12.50", "a", 1, 12.50),
        (b"a=foo&b=446&c=500", "foo", 446, 500.0),
        (b"a=Hello%20World!!%3B%3B&b=60&c=88.05", "Hello World!!;;", 60, 88.05),
    ],
)
async def test_handler_query_value_binding_mixed_types(
    query, expected_a, expected_b, expected_c, app
):
    @app.router.get("/")
    async def home(request, a: str, b: int, c: float):
        assert a == expected_a
        assert b == expected_b
        assert c == expected_c

    await app(get_example_scope("GET", "/", query=query), MockReceive(), MockSend())
    assert app.response.status == 204


@pytest.mark.parametrize(
    "query,expected_value",
    [
        (
            b"a=Hello%20World!!%3B%3B&a=Hello&a=World",
            ["Hello World!!;;", "Hello", "World"],
        ),
    ],
)
async def test_handler_query_value_binding_list(query, expected_value, app):
    @app.router.get("/")
    async def home(request, a):
        assert a == expected_value

    await app(get_example_scope("GET", "/", query=query), MockReceive(), MockSend())
    assert app.response.status == 204


@pytest.mark.parametrize(
    "query,expected_value",
    [(b"a=2", [2]), (b"a=2&a=44", [2, 44]), (b"a=1&a=5&a=18", [1, 5, 18])],
)
async def test_handler_query_value_binding_list_of_ints(query, expected_value, app):
    @app.router.get("/")
    async def home(request, a: List[int]):
        assert a == expected_value

    await app(get_example_scope("GET", "/", query=query), MockReceive(), MockSend())
    assert app.response.status == 204


@pytest.mark.parametrize(
    "query,expected_value",
    [
        (b"a=2", [2.0]),
        (b"a=2.5&a=44.12", [2.5, 44.12]),
        (b"a=1&a=5.55556&a=18.656", [1, 5.55556, 18.656]),
    ],
)
async def test_handler_query_value_binding_list_of_floats(query, expected_value, app):
    @app.router.get("/")
    async def home(a: List[float]):
        assert a == expected_value

    await app(get_example_scope("GET", "/", query=query), MockReceive(), MockSend())
    assert app.response.status == 204


async def test_handler_normalize_sync_method(app):
    @app.router.get("/")
    def home(request):
        pass

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())
    assert app.response.status == 204


async def test_handler_normalize_sync_method_from_header(app):
    @app.router.get("/")
    def home(request, xx: FromHeader[str]):
        assert xx.value == "Hello World"

    await app(
        get_example_scope("GET", "/", [(b"XX", b"Hello World")]),
        MockReceive(),
        MockSend(),
    )
    assert app.response.status == 204


async def test_handler_normalize_sync_method_from_header_name_compatible(app):
    class AcceptLanguageHeader(FromHeader[str]):
        name = "accept-language"

    @inject()
    @app.router.get("/")
    def home(accept_language: AcceptLanguageHeader):
        assert accept_language.value == "en-US,en;q=0.9,it-IT;q=0.8,it;q=0.7"

    await app(
        get_example_scope("GET", "/", []),
        MockReceive(),
        MockSend(),
    )
    assert app.response.status == 204


async def test_handler_normalize_sync_method_from_query(app):
    @app.router.get("/")
    def home(xx: FromQuery[int]):
        assert xx.value == 20

    await app(get_example_scope("GET", "/", query=b"xx=20"), MockReceive(), MockSend())
    assert app.response.status == 204


async def test_handler_normalize_sync_method_from_query_implicit_default(app):
    @app.router.get("/")
    def get_products(
        page: int = 1,
        size: int = 30,
        search: str = "",
    ):
        return text(f"Page: {page}; size: {size}; search: {search}")

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == "Page: 1; size: 30; search: "

    await app(get_example_scope("GET", "/", query=b"page=2"), MockReceive(), MockSend())

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == "Page: 2; size: 30; search: "

    await app(
        get_example_scope("GET", "/", query=b"page=2&size=50"),
        MockReceive(),
        MockSend(),
    )

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == "Page: 2; size: 50; search: "

    await app(
        get_example_scope("GET", "/", query=b"page=2&size=50&search=foo"),
        MockReceive(),
        MockSend(),
    )

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == "Page: 2; size: 50; search: foo"


async def test_handler_normalize_sync_method_from_query_default(app):
    @app.router.get("/")
    def get_products(
        page: FromQuery[int] = FromQuery(1),
        size: FromQuery[int] = FromQuery(30),
        search: FromQuery[str] = FromQuery(""),
    ):
        return text(f"Page: {page.value}; size: {size.value}; search: {search.value}")

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == "Page: 1; size: 30; search: "

    await app(get_example_scope("GET", "/", query=b"page=2"), MockReceive(), MockSend())

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == "Page: 2; size: 30; search: "

    await app(
        get_example_scope("GET", "/", query=b"page=2&size=50"),
        MockReceive(),
        MockSend(),
    )

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == "Page: 2; size: 50; search: "

    await app(
        get_example_scope("GET", "/", query=b"page=2&size=50&search=foo"),
        MockReceive(),
        MockSend(),
    )

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == "Page: 2; size: 50; search: foo"


async def test_handler_normalize_list_sync_method_from_query_default(app):
    @app.router.get("/")
    def example(
        a: FromQuery[List[int]] = FromQuery([1, 2, 3]),
        b: FromQuery[List[int]] = FromQuery([4, 5, 6]),
        c: FromQuery[List[str]] = FromQuery(["x"]),
    ):
        return text(f"A: {a.value}; B: {b.value}; C: {c.value}")

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == f"A: {[1, 2, 3]}; B: {[4, 5, 6]}; C: {['x']}"

    await app(get_example_scope("GET", "/", query=b"a=1349"), MockReceive(), MockSend())

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == f"A: {[1349]}; B: {[4, 5, 6]}; C: {['x']}"

    await app(
        get_example_scope("GET", "/", query=b"a=1349&c=Hello&a=55"),
        MockReceive(),
        MockSend(),
    )

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == f"A: {[1349, 55]}; B: {[4, 5, 6]}; C: {['Hello']}"

    await app(
        get_example_scope("GET", "/", query=b"a=1349&c=Hello&a=55&b=10"),
        MockReceive(),
        MockSend(),
    )

    response = app.response
    content = await response.text()

    assert response.status == 200
    assert content == f"A: {[1349, 55]}; B: {[10]}; C: {['Hello']}"


async def test_handler_normalize_sync_method_without_arguments(app):
    @app.router.get("/")
    def home():
        return

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())
    assert app.response.status == 204


async def test_handler_normalize_sync_method_from_query_optional(app):
    @app.router.get("/")
    def home(xx: FromQuery[Optional[int]], yy: FromQuery[Optional[int]]):
        assert xx.value is None
        assert yy.value == 20

    await app(get_example_scope("GET", "/", query=b"yy=20"), MockReceive(), MockSend())
    assert app.response.status == 204


async def test_handler_normalize_optional_binder(app):
    @app.router.get("/1")
    def home1(xx: Optional[FromQuery[int]], yy: Optional[FromQuery[int]]):
        assert xx is None
        assert yy.value == 20

    @app.router.get("/2")
    def home2(xx: Optional[FromQuery[int]]):
        assert xx is not None
        assert xx.value == 10

    @app.router.get("/3")
    def home3(xx: Optional[FromQuery[Optional[int]]]):
        assert xx is not None
        assert xx.value == 10

    await app(get_example_scope("GET", "/1", query=b"yy=20"), MockReceive(), MockSend())
    assert app.response.status == 204

    await app(get_example_scope("GET", "/2", query=b"xx=10"), MockReceive(), MockSend())
    assert app.response.status == 204

    await app(get_example_scope("GET", "/3", query=b"xx=10"), MockReceive(), MockSend())
    assert app.response.status == 204


async def test_handler_normalize_sync_method_from_query_optional_list(app):
    @app.router.get("/")
    def home(xx: FromQuery[Optional[List[int]]], yy: FromQuery[Optional[List[int]]]):
        assert xx.value is None
        assert yy.value == [20, 55, 64]

    await app(
        get_example_scope("GET", "/", query=b"yy=20&yy=55&yy=64"),
        MockReceive(),
        MockSend(),
    )
    assert app.response.status == 204


@pytest.mark.parametrize(
    "query,expected_values",
    [
        [b"xx=hello&xx=world&xx=lorem&xx=ipsum", ["hello", "world", "lorem", "ipsum"]],
        [b"xx=1&xx=2", ["1", "2"]],
        [b"xx=1&yy=2", ["1"]],
    ],
)
async def test_handler_normalize_sync_method_from_query_default_type(
    query, expected_values, app
):
    @app.router.get("/")
    def home(request, xx: FromQuery):
        assert xx.value == expected_values

    await app(get_example_scope("GET", "/", query=query), MockReceive(), MockSend())
    assert app.response.status == 204


async def test_handler_normalize_method_without_input(app):
    @app.router.get("/")
    async def home():
        pass

    await app(get_example_scope("GET", "/"), MockReceive(), MockSend())
    assert app.response.status == 204


@pytest.mark.parametrize(
    "value,expected_value",
    [["dashboard", "dashboard"], ["hello_world", "hello_world"]],
)
async def test_handler_from_route(value, expected_value, app):
    @app.router.get("/:area")
    async def home(request, area: FromRoute[str]):
        assert area.value == expected_value

    await app(get_example_scope("GET", "/" + value), MockReceive(), MockSend())
    assert app.response.status == 204


@pytest.mark.parametrize(
    "value_one,value_two,expected_value_one,expected_value_two",
    [
        ["en", "dashboard", "en", "dashboard"],
        ["it", "hello_world", "it", "hello_world"],
    ],
)
async def test_handler_two_routes_parameters(
    value_one: str,
    value_two: str,
    expected_value_one: str,
    expected_value_two: str,
    app,
):
    @app.router.get("/:culture_code/:area")
    async def home(culture_code: FromRoute[str], area: FromRoute[str]):
        assert culture_code.value == expected_value_one
        assert area.value == expected_value_two

    await app(
        get_example_scope("GET", "/" + value_one + "/" + value_two),
        MockReceive(),
        MockSend(),
    )
    assert app.response.status == 204


@pytest.mark.parametrize(
    "value_one,value_two,expected_value_one,expected_value_two",
    [
        ["en", "dashboard", "en", "dashboard"],
        ["it", "hello_world", "it", "hello_world"],
    ],
)
async def test_handler_two_routes_parameters_implicit(
    value_one: str,
    value_two: str,
    expected_value_one: str,
    expected_value_two: str,
    app,
):
    @app.router.get("/:culture_code/:area")
    async def home(culture_code, area):
        assert culture_code == expected_value_one
        assert area == expected_value_two

    await app(
        get_example_scope("GET", "/" + value_one + "/" + value_two),
        MockReceive(),
        MockSend(),
    )
    assert app.response.status == 204


async def test_handler_from_json_parameter(app):
    @app.router.post("/")
    async def home(item: FromJSON[Item]):
        assert item is not None
        value = item.value
        assert value.a == "Hello"
        assert value.b == "World"
        assert value.c == 10

    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type", b"application/json"), (b"content-length", b"32")],
        ),
        MockReceive([b'{"a":"Hello","b":"World","c":10}']),
        MockSend(),
    )
    assert app.response.status == 204


async def test_handler_from_json_annotated_parameter(app):
    @app.router.post("/")
    async def home(item: Annotated[Item, FromJSON]):
        assert item is not None
        value = item
        assert value.a == "Hello"
        assert value.b == "World"
        assert value.c == 10

    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type", b"application/json"), (b"content-length", b"32")],
        ),
        MockReceive([b'{"a":"Hello","b":"World","c":10}']),
        MockSend(),
    )
    assert app.response.status == 204


async def test_handler_from_json_without_annotation(app):
    @app.router.post("/")
    async def home(item: FromJSON):
        assert item is not None
        assert isinstance(item.value, dict)
        value = item.value
        assert value == {"a": "Hello", "b": "World", "c": 10}

    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type", b"application/json"), (b"content-length", b"32")],
        ),
        MockReceive([b'{"a":"Hello","b":"World","c":10}']),
        MockSend(),
    )
    assert app.response.status == 204


async def test_handler_from_json_parameter_dict(app):
    @app.router.post("/")
    async def home(item: FromJSON[dict]):
        assert item is not None
        assert isinstance(item.value, dict)
        value = item.value
        assert value == {"a": "Hello", "b": "World", "c": 10}

    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type", b"application/json"), (b"content-length", b"32")],
        ),
        MockReceive([b'{"a":"Hello","b":"World","c":10}']),
        MockSend(),
    )
    assert app.response.status == 204


async def test_handler_from_json_parameter_dict_unannotated(app):
    @app.router.post("/")
    async def home(item: FromJSON[Dict]):
        assert item is not None
        assert isinstance(item.value, dict)
        value = item.value
        assert value == {"a": "Hello", "b": "World", "c": 10}

    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type", b"application/json"), (b"content-length", b"32")],
        ),
        MockReceive([b'{"a":"Hello","b":"World","c":10}']),
        MockSend(),
    )
    assert app.response.status == 204


async def test_handler_from_json_parameter_dict_annotated(app):
    @app.router.post("/")
    async def home(item: FromJSON[Dict[str, Any]]):
        assert item is not None
        assert isinstance(item.value, dict)
        value = item.value
        assert value == {"a": "Hello", "b": "World", "c": 10}

    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type", b"application/json"), (b"content-length", b"32")],
        ),
        MockReceive([b'{"a":"Hello","b":"World","c":10}']),
        MockSend(),
    )
    assert app.response.status == 204


@pytest.mark.parametrize(
    "value",
    [
        "Lorem ipsum dolor sit amet",
        "Hello, World",
        "Lorem ipsum dolor sit amet\n" * 200,
    ],
)
async def test_handler_from_text_parameter(value: str, app):
    @app.router.post("/")
    async def home(text: FromText):
        assert text.value == value

    await app(
        get_example_scope(
            "POST",
            "/",
            [
                (b"content-type", b"text/plain; charset=utf-8"),
                (b"content-length", str(len(value)).encode()),
            ],
        ),
        MockReceive([value.encode("utf8")]),
        MockSend(),
    )
    assert app.response.status == 204


@pytest.mark.parametrize(
    "value",
    [
        b"Lorem ipsum dolor sit amet",
        b"Hello, World",
        b"Lorem ipsum dolor sit amet\n" * 200,
    ],
)
async def test_handler_from_bytes_parameter(value: bytes, app):
    @app.router.post("/")
    async def home(text: FromBytes):
        assert text.value == value

    await app(
        get_example_scope(
            "POST",
            "/",
            [
                (b"content-type", b"text/plain; charset=utf-8"),
                (b"content-length", str(len(value)).encode()),
            ],
        ),
        MockReceive([value]),
        MockSend(),
    )
    assert app.response.status == 204


async def test_handler_from_files(app):
    @app.router.post("/")
    async def home(files: FromFiles):
        assert files is not None
        assert files.value is not None
        assert len(files.value) == 4
        file1 = files.value[0]
        file2 = files.value[1]
        file3 = files.value[2]
        file4 = files.value[3]

        assert file1.name == b"file1"
        assert file1.file_name == b"a.txt"
        assert file1.data == b"Content of a.txt.\r\n"

        assert file2.name == b"file2"
        assert file2.file_name == b"a.html"
        assert file2.data == b"<!DOCTYPE html><title>Content of a.html.</title>\r\n"

        assert file3.name == b"file2"
        assert file3.file_name == b"a.html"
        assert file3.data == b"<!DOCTYPE html><title>Content of a.html.</title>\r\n"

        assert file4.name == b"file3"
        assert file4.file_name == b"binary"
        assert file4.data == b"a\xcf\x89b"

    boundary = b"---------------------0000000000000000000000001"

    content = b"\r\n".join(
        [
            boundary,
            b'Content-Disposition: form-data; name="text1"',
            b"",
            b"text default",
            boundary,
            b'Content-Disposition: form-data; name="text2"',
            b"",
            "aωb".encode("utf8"),
            boundary,
            b'Content-Disposition: form-data; name="file1"; filename="a.txt"',
            b"Content-Type: text/plain",
            b"",
            b"Content of a.txt.",
            b"",
            boundary,
            b'Content-Disposition: form-data; name="file2"; filename="a.html"',
            b"Content-Type: text/html",
            b"",
            b"<!DOCTYPE html><title>Content of a.html.</title>",
            b"",
            boundary,
            b'Content-Disposition: form-data; name="file2"; filename="a.html"',
            b"Content-Type: text/html",
            b"",
            b"<!DOCTYPE html><title>Content of a.html.</title>",
            b"",
            boundary,
            b'Content-Disposition: form-data; name="file3"; filename="binary"',
            b"Content-Type: application/octet-stream",
            b"",
            "aωb".encode("utf8"),
            boundary + b"--",
        ]
    )

    await app(
        get_example_scope(
            "POST",
            "/",
            [
                (b"content-length", str(len(content)).encode()),
                (b"content-type", b"multipart/form-data; boundary=" + boundary),
            ],
        ),
        MockReceive([content]),
        MockSend(),
    )
    assert app.response.status == 204


async def _multipart_mix_scenario(app):

    content = read_multipart_mix_dat()

    await app(
        get_example_scope(
            "POST",
            "/",
            [
                (b"content-length", str(len(content)).encode()),
                (
                    b"content-type",
                    b"multipart/form-data; boundary=----WebKitFormBoundarygKWtIe0dRcq6RJaJ",
                ),
            ],
        ),
        MockReceive([content]),
        MockSend(),
    )
    assert app.response.status == 204


async def test_handler_from_files_and_form(app):
    """
    Tests proper handling of a separate FromFiles and FromForm binders, with class
    definition for the FromForm - not including the files.
    """

    @dataclass(init=False)
    class OtherInput:
        textfield: str
        checkbox1: bool
        checkbox2: bool

        def __init__(
            self,
            textfield: str,
            checkbox1: Optional[str],
            checkbox2: Optional[str] = None,
            **kwargs,
        ):
            self.textfield = textfield
            self.checkbox1 = checkbox1 == "on"
            self.checkbox2 = checkbox2 == "on"

    @app.router.post("/")
    async def home(files: FromFiles, other: FromForm[OtherInput]):
        assert files is not None
        assert files.value is not None
        assert len(files.value) == 1
        file1 = files.value[0]

        assert file1.name == b"files"
        assert file1.file_name == b"red-dot.png"

        assert other.value.checkbox1 is True
        assert other.value.checkbox2 is False
        assert other.value.textfield == "Hello World!"

    await _multipart_mix_scenario(app)


async def test_handler_from_form_handling_whole_multipart_with_class(app):
    """
    Tests proper handling of a single FromForm binder, handling multipart with files
    and other input.
    """

    @dataclass(init=False)
    class WholeInput:
        textfield: str
        checkbox1: bool
        checkbox2: bool
        files: list

        def __init__(
            self,
            textfield: str,
            checkbox1: Optional[str] = None,
            checkbox2: Optional[str] = None,
            files: Optional[List[FormPart]] = None,
            **kwargs,
        ):
            self.textfield = textfield
            self.checkbox1 = checkbox1 == "on"
            self.checkbox2 = checkbox2 == "on"
            self.files = files or []

    @app.router.post("/")
    async def home(data: FromForm[WholeInput]):
        files = data.value.files
        assert files is not None
        assert len(files) == 1
        file1 = files[0]

        assert file1.name == b"files"
        assert file1.file_name == b"red-dot.png"

        assert data.value.checkbox1 is True
        assert data.value.checkbox2 is False
        assert data.value.textfield == "Hello World!"

    await _multipart_mix_scenario(app)


async def test_handler_from_form_handling_whole_multipart_without_class(app):
    """
    Tests proper handling of a single FromForm binder, handling multipart with files
    and other input with dictionary.
    """

    @app.router.post("/")
    async def home(data: FromForm):
        files = data.value.get("files")
        assert files is not None
        assert len(files) == 1
        file1 = files[0]

        assert file1.name == b"files"
        assert file1.file_name == b"red-dot.png"

        assert data.value.get("checkbox1") == "on"
        assert data.value.get("checkbox2") is None
        assert data.value.get("textfield") == "Hello World!"

    await _multipart_mix_scenario(app)


async def test_handler_from_files_and_form_dict(app):
    """
    Tests proper handling of a separate FromFiles and FromForm binders, without class
    definition for the FromForm - not including the files.
    """

    @app.router.post("/")
    async def home(files: FromFiles, other: FromForm):
        assert files is not None
        assert files.value is not None
        assert len(files.value) == 1
        file1 = files.value[0]

        assert file1.name == b"files"
        assert file1.file_name == b"red-dot.png"

        assert other.value.get("checkbox1") == "on"
        assert other.value.get("checkbox2") is None
        assert other.value.get("textfield") == "Hello World!"

    await _multipart_mix_scenario(app)


async def test_handler_from_files_handles_empty_body(app):
    @app.router.post("/")
    async def home(files: FromFiles):
        assert files.value == []

    await app(
        get_example_scope(
            "POST",
            "/",
            [],
        ),
        MockReceive([]),
        MockSend(),
    )
    assert app.response.status == 204


async def test_handler_from_json_parameter_missing_property(app):
    @app.router.post("/")
    async def home(item: FromJSON[Item]): ...

    # Note: the following example is missing one of the properties
    # required by the constructor
    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type", b"application/json"), (b"content-length", b"25")],
        ),
        MockReceive([b'{"a":"Hello","b":"World"}']),
        MockSend(),
    )
    assert app.response.status == 400
    assert (
        b"Bad Request: invalid parameter in request payload"
        in app.response.content.body
    )


async def test_handler_json_response_implicit(app):
    @app.router.get("/")
    async def get_item() -> Item2:
        return Item2("Hello", "World", "!")

    # Note: the following example missing one of the properties
    # required by the constructor
    await app(
        get_example_scope(
            "GET",
            "/",
            [],
        ),
        MockReceive(),
        MockSend(),
    )
    assert app.response.status == 200
    data = await app.response.json()
    assert data == Item2("Hello", "World", "!").__dict__


async def test_handler_json_response_implicit_no_annotation(app):
    @app.router.get("/")
    async def get_item():
        return Item2("Hello", "World", "!")

    # Note: the following example missing one of the properties
    # required by the constructor
    await app(
        get_example_scope(
            "GET",
            "/",
            [],
        ),
        MockReceive(),
        MockSend(),
    )
    assert app.response.status == 200
    data = await app.response.json()
    assert data == Item2("Hello", "World", "!").__dict__


async def test_handler_text_response_implicit(app):
    @app.router.get("/")
    async def get_lorem():
        return "Lorem ipsum"

    # Note: the following example missing one of the properties
    # required by the constructor
    await app(
        get_example_scope(
            "GET",
            "/",
            [],
        ),
        MockReceive(),
        MockSend(),
    )
    assert app.response.status == 200
    data = await app.response.text()
    assert data == "Lorem ipsum"


async def test_handler_from_json_parameter_missing_property_complex_type(app):
    @inject()
    @app.router.post("/")
    async def home(item: FromJSON[Foo]): ...

    # Note: the following example missing one of the properties
    # required by the constructor
    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type", b"application/json"), (b"content-length", b"34")],
        ),
        MockReceive([b'{"item":{"a":"Hello","b":"World"}}']),
        MockSend(),
    )
    assert app.response.status == 400
    assert (
        b"Bad Request: invalid parameter in request payload."
        in app.response.content.body
    )


async def test_handler_from_json_parameter_missing_property_array(app):
    @app.router.post("/")
    async def home(item: FromJSON[List[Item]]): ...

    # Note: the following example missing one of the properties
    # required by the constructor
    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type", b"application/json"), (b"content-length", b"25")],
        ),
        MockReceive([b'[{"a":"Hello","b":"World"}]']),
        MockSend(),
    )
    assert app.response.status == 400
    assert (
        b"Bad Request: invalid parameter in request payload."
        in app.response.content.body
    )


async def test_handler_from_json_parameter_handles_request_without_body(app):
    @app.router.post("/")
    async def home(item: FromJSON[Item]):
        return Response(200)

    await app(
        get_example_scope(
            "POST",
            "/",
            [],
        ),
        MockReceive([]),
        MockSend(),
    )
    assert app.response.status == 400
    assert app.response.content.body == b"Bad Request: Expected request content"


async def test_handler_from_json_list_of_objects(app):
    @app.router.post("/")
    async def home(item: FromJSON[List[Item]]):
        assert item is not None
        value = item.value

        item_one = value[0]
        item_two = value[1]
        assert item_one.a == "Hello"
        assert item_one.b == "World"
        assert item_one.c == 10

        assert item_two.a == "Lorem"
        assert item_two.b == "ipsum"
        assert item_two.c == 55

    await app(
        get_example_scope(
            "POST",
            "/",
            [[b"content-type", b"application/json"], [b"content-length", b"32"]],
        ),
        MockReceive(
            [
                b'[{"a":"Hello","b":"World","c":10},'
                + b'{"a":"Lorem","b":"ipsum","c":55}]'
            ]
        ),
        MockSend(),
    )
    assert app.response.status == 204


@pytest.mark.parametrize(
    "expected_type,request_body,expected_result",
    [
        [
            List,
            b'["one","two","three"]',
            ["one", "two", "three"],
        ],
        [
            List[bytes],
            b'["lorem ipsum", "hello world", "Three"]',
            [b"lorem ipsum", b"hello world", b"Three"],
        ],
        [
            List[str],
            b'["one","two","three"]',
            ["one", "two", "three"],
        ],
        [
            List[int],
            b"[20, 10, 0, 200, 12, 64]",
            [20, 10, 0, 200, 12, 64],
        ],
        [
            List[float],
            b"[20.4, 10.23, 0.12, 200.00, 12.12, 64.01]",
            [20.4, 10.23, 0.12, 200.00, 12.12, 64.01],
        ],
        [
            List[bool],
            b"[true, false, true, true, 1, 0]",
            [True, False, True, True, True, False],
        ],
        [
            List[datetime],
            b'["2020-10-24", "2020-10-24T18:46:19.313346", "2019-05-30"]',
            [
                datetime(2020, 10, 24),
                datetime(2020, 10, 24, 18, 46, 19, 313346),
                datetime(2019, 5, 30),
            ],
        ],
        [
            List[date],
            b'["2020-10-24", "2020-10-24", "2019-05-30"]',
            [date(2020, 10, 24), date(2020, 10, 24), date(2019, 5, 30)],
        ],
        [
            List[UUID],
            b'["d1e7745f-2a20-4181-8249-b7fef73592dd",'
            + b'"0bfWe}; B: {b.value};0-24T18:46:19.31334d",'
 0, 10, 24), date(2019, 5, 30)],
     0-24T18:46:19.31334d",'
         List[UUID],
            b'["d            [
                datrk.parametrize(
    "value",
    
    assert aprimitpe(      [orem","b":"ips um","c":55}]' 
            ]
 ["1", "2"]],
ta = await app.response.text()
    assert data == "Lorem ipsum"


asyorem","b":"ip assert app.response.status == 204


async def test_handler_from_json_parameter(app @app.router.    ]
t]),
        MockSend(),
    )
    assert app.response.status == 204


async def _multipart_mix_scenario(app):
rt item_two.b == "ipsum"
        assertx_scenario(app):
rt item_twot = read_multiparum","c":55}]at()

    a] (
                    b"content-type",
         um","c":55}]ert files.value == []

    await app(
        get_example_scope(
            "POST",
            "/",
 part_with_nse.status part_with
    """
  FoomForm bindeoosingle FromForufo - not incluata = await app.response.text()
    assert data == "Lorem ipsum"


async defsert app.response.status == 204


async def test_handler_from_json_parameter(app)eoo@app.router.post("/")
    async dufo
        == "World"
        assert item_one.c == 10

        assert item_two.a == "Lorem"
        assert item_two.b == "ipsum"
        assert item_two.c == 55

    await app(
        get_example_scope(
     
             ufo":12.1",
            [(b"content-type", b"application/json"), (b"content-length", b"32")],
        ),
        MockReceive( assert response.status == 20 payload."
        in app.response.content.body
 ample(
ent.(ody
("O      T  [b"3))assert app.response.status == 204


async def test_handler_from_json_parameter(app):
    O   .post("/")
    async def homT  [: Annotated[Item, FromJSON]3rom_json_parameter_handles_request_without_body(app):
    @app.router.post("/")
    async def home(item: FromJSON[Item]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-length", b"32")],
        ),
        MockReceive( asser_overridet response.status == 20 payload."
        in app.response.content.body
 ample(
ent.(ody
("O      T  [b"3))assert app.response.status == 204


async def test_handler_from_json_parameter(app):
    router.post("/")
    async def home(item: Annotated[Item, FromJSON]):
        assert item is not None
        value = item
        assert value.a == "Hello"
      rt item_two.b == "ipsum"
        assert item_two.c == 55

    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type", b"application/json"), (b"content-length", b"32")],
        ),
        MockReceivese.status == 200
    data = awa payload."
        in app.response.ody
s == 204


async def test_handler_from_json_parametandl[Item]]):
        assert item is None
        value = item.value
mJSON]):
        assert item is not None
        value = item
        assert value.a == "Hello"
      rt item_two.b == "ipsum"
        assert item_two.c == 55

    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type", b"application/json"), (b"content-length", b"32")],
        ),
        MockReceivese.statue( assert response.status == 20 payload."
        in app.response.ody
       (ceive())s == 204


async def test_handler_from_json_parametandl[Item1      assert item is None
2 value = item.value
mJSON]3rom_json_parameter_handles_request_without_body(app):
    @app.router.post("/")
    async def home(item: FromJSON[Item]):
      , 55]}; B: {[4, 5, 6]}; C: {[, b"application/json"), (b"content-length", b"32")],
        ),
    wrongit app(g    MockReceives_rs_null_if_example_scope("GET", "/"), MockReceive(pp):<--- NB: wrong http t app(st_ha payter_o","b":s"
        in app.response.content.b       se: Expected request content"
y_optional_listasync def get_lorem():
        return "Lorem ipsum"

    # Note: the following example missirt item_two.b == "ipsum"
        assert item_two.c == 55

    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type"[, b"application/json"), (b"content-length", b"32")],
        ),
    wrongit app(g    MockReceives_rs_bad b"Bad Rscope("GET", "/"), MockReceive(pp):<--- NB: wrong http t app(st_ha payter_o","b":s"
        in app.res], ["hellckSend(),
    )
    assert app.response.sty_optional_listasync def get_lorem():
        return "Lorem ipsum"

    # Note: the following example missirt item_two.b == "ipsum"
        assert item_two.c == 55

    await app(
        get_example_scope(
            "POST",
            "/",
            [(b"content-type"[, b"#(
   becauseouter 200
    d.content.body
 amakesouteref teREQUIRED;ait app(
        get_example_scope(
         get_example_sc,
            "/",
            ckReceive(),    [],
        ),
        MockReceive([]},'
                + b'{"a":"LockReceive:"ipsockReceiv

    await app(get_exa[date],
  sum d
        M      st[date],
  inell"ert r, ceivet[date],
       ll"er.2r, ce.2uery,expectednot   Trpp(g     uery,expectednot   1(g     uery,expecte       se        1(g     uery,expecte       se        (g _lisuery,expectednot   .12, "12.12, 64.01],
   e       se        .12, "12.12, 64.01],
   e ],
4, 18, 4
                ] [
            Lie ],
4, 18, 41-1             ]cei1)64.01],
   e       se        (g _lisuery,expecte
:46:19.313346", "201ote: the followrue, true, 1, 0]",
         
 List[datetime],
            b'["2020-10-24", "2020-10-24T18:46:uery,expectednot   0"12.12, 64.01],
   e
:46:19.31334d",'ote: the follow54b2587a-0afc-40ec-a03d-13223d4bb04d  
 List[datetid",'
 54b2587a-0afc-40ec-a03d-13223d4bb04d )              datrk.parametrize(
     Mockld", "lockReceivepvalu{"a":"ockReceive:"ips"ockReceivk.parametrize(
    "v, "2"]],
ta = await app.response.tuery), MockReceive(), MockSeeoosic def testockReceive:"ipbox1 == "on"
       oot_handler_from_route(valu)


async def tple_scr,
  ler_from_json_parameter_handles_request_without_es, app
):
  ho    @apf 
  ={ockReceiv}"()

    await app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0([]},'
                + b'{"a":"LockReceive:"ipsockReceiv

    await app(get_exa[date],
  sum d
        M      st[date],
  inell"ert r, ceivet[date],
       ll"er.2r, ce.2uery,expectednot   Trpp(g     uery,expectednot   1(g     uery,expecte       se        1(g     uery,expecte       se        (g _lisuery,expectednot   .12, "12.12, 64.01],
   e       se        .12, "12.12, 64.01],
   e ],
4, 18, 4
                ] [
            Lie ],
4, 18, 41-1             ]cei1)64.01],
   e       se        (g _lisuery,expecte
:46:19.313346", "201ote: the followrue, true, 1, 0]",
         
 List[datetime],
            b'["2020-10-24", "2020-10-24T18:46:uery,expectednot   0"12.12, 64.01],
   e
:46:19.31334d",'ote: the follow54b2587a-0afc-40ec-a03d-13223d4bb04d  
 List[datetid",'
 54b2587a-0afc-40ec-a03d-13223d4bb04d )              datrk.parametrize(
     MocklcookielockReceivepvalu{"a":"ockReceive:"ips"ockReceivk.parametrize(
    "v, "2"]],
ta = await app.response.tuery), MockReceive(), MockSeeoosic deCookietockReceive:"ipbox1 == "on"
       oot_handler_from_route(valu)


async def tple_scr,
  ler_from_json_parameter_handles_request_without_es, app
):
  y theokie:
 f 
  ={ockReceiv}"()

    aw]he properties
    # required by the constructor
    await app(
        get_example_scope(
[]},'
                + b'{"a":"LockReceive:"ipsockReceivs

    await app(get_exa[date],
      ) [
        MockRec]) [
        MockRec]64.01],
   ees],
      [
        MockRec]) [
        MockRec]64.01],
   ees],
 ],
   [
rt r
   ceive64.01],
   ees],
 ],
   [

    "   3r
   ceive(),64.01],
   ees],
         [
.1 "   2.     "3.55r
   c, 0, 2.  e().55,64.01],
   ees],
        [

   0
   0
   1r
    [20.4, 10.23, 10.23, 0.]    datetime(2020, 10, 24),
                datet[ 18, 4
      13346)
      1334841-1 ]          datetime(2019, 5"]',
    ],
        [
      ],
    8 ]cei1)64.01],
        ],
        [
            List[bool],
           [true, true, 1, 0]",
            [Trutrue, 1, 0]",
        ], True, True, True, False],
        ],
        [
    2020-10-24", "2020-10-24T18:46:19.313346", "2019-05-30[
    2020-10-24", "2020-10-24T18:46:19.3]              datrk.parametrize(
     Mockld", "lockReceiveasserpvalu{"a":"ockReceive:"ips"ockReceivsk.parametrize(
    "v, "2"]],
ta = await app.response.tuery), MockReceive(), MockSeeoosic def testockReceive:"ipbox1 == "on"
       oot_handler_from_route(valu)


async def tple_scr,
  ler_from_jsd", "xam"&e_name f 
  ={ockReceiv}"st_ha ceive([b'[{"ockReceivsfrom_json_parameter_handles_request_without_es, app
):
  ho    @ap   @a()

    await app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0([]},'
                + b'{"a":"LockReceive:"ipsockReceiv(get_exa[date],
  inell"nout"et[date],
       ll"nout"et[date],
   ],
4, nout"et[date],
         se        nout"et[date],
   ],
"201o  nout"et[date],
  d",'o  nout"et[daterk.parametrize(
       Mockld", "lockReceive400(ockReceive:"ips"ockReceivk. 200
    data = await app.response.tuery), MockReceive(), MockSeeoosic def testockReceive:"ipbox1 == "on"c def tple_scr,
  ler_from_json_parameter_handles_request_without_es, app
):
  ho    @apf 
  ={ockReceiv}"()

    await app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content
         get_example_sc,
            "/",
            ,    [],
     I  MockR_handl['nout']st_ha ceive([b'`
  `;"'[{"  get_e([]},'
                + b'{"a":"LockReceive:"ipsockReceiv

    await app(get_exa[date],
  sum d
        M      st[date],
  inell"ert r, ceivet[date],
       ll"er.2r, ce.2uery,expectednot   Trpp(g     uery,expectednot   1(g     uery,expectednot   .12, "12.12, 64.01],
   e ],
4, 18, 4
                ] [
            Lie
:46:19.313346", "201ote: the followrue, true, 1, 0]",
         
 List[datetime],
            b'["2020-10-24", "2020-10-24T18:46:uery,expectednot   0"12.12, 64.01],
   e
:46:19.31334d",'ote: the follow54b2587a-0afc-40ec-a03d-13223d4bb04d  
 List[datetid",'
 54b2587a-0afc-40ec-a03d-13223d4bb04d )              datrk.parametrize(
     MocklponselockReceivepvalu{"a":"ockReceive:"ips"ockReceivk.parametrize(
    "v, "2"]],
ta = await app.response.tuery),:
   MockReceive(), MockSeeoosic de str,
ockReceive:"ipbox1 == "on"
       oot_handler_from_route(valu)


async def tple_scr,
  ler_from_json_parameter_handles_request_without_es, app
): +"ockReceivk.[]wait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0([]},'
                + b'{"a":"LockReceive:"ipsockReceiv

    await app(get_exa[date],
  sum d
        M      st[date],
  inell"ert r, ceivet[date],
       ll"er.2r, ce.2uery,expectednot   Trpp(g     uery,expectednot   1(g     uery,expectednot   .12, "12.12, 64.01],
   e ],
4, 18, 4
                ] [
            Lie
:46:19.313346", "201ote: the followrue, true, 1, 0]",
         
 List[datetime],
            b'["2020-10-24", "2020-10-24T18:46:uery,expectednot   0"12.12, 64.01],
   e
:46:19.31334d",'ote: the follow54b2587a-0afc-40ec-a03d-13223d4bb04d  
 List[datetid",'
 54b2587a-0afc-40ec-a03d-13223d4bb04d )              datrk.parametrize(
     MocklheadivepvaReceivepvalu{"a":"ockReceive:"ips"ockReceivk.parametrize(
    "v, "2"]],TxamtitlVar("Tf test_h"""
  XFooHeadiv(c deHeadiv[Tbox1 == "on"alue i "X-Foo"
    data = await app.response.tuery), MockReceive(), MockSex_eoosiXFooHeadiv
ockReceive:"ipbox1 == "on"
      x_eoot_handler_from_route(valu)


async def tple_scr,
  ler_from_json_parameter_handles_request_without_es, app
):
  y tX-Foo"s"ockReceiv()

    aw]he properties
    # required by the constructor
    'Hellapplication/json"), (b"content-l0([]},'
                + b'{"a":"LockReceive:"ipsockReceiv    MockReceive:      MockSend(),
  sum d
        MWe,value_two,],
  inell"ert r, "164"et[date],
       ll"1.2r, "er.3"et[date],
   dolor b"quest_w"r b"quest_w"uery,expectednot  00, 12.12, 64.01],
   e
:46:19.31334d",'ote: the follow54b2587a-0afc-40ec-a03d-13223d4bb04d  
 List[dateti"8ffd8e17-1a38-462f-ba71-3d92e52edf1f"              datrk.parametrize(
     Mockld", "lockReceiv(ockReceive:"ips"ockReceiv    M ockReceive:  k. 200
    data = await app.response.tuery), MockReceive(), MockSeeoosic def testockReceive:"ipbox1 == "on"_parameter_dict_aneoot_hand,"ockReceive:"iples
    anifeter_dict_aneoot_hand,"br sit amet\n" *async def t "/",f"Go   {eoot_hand.de
    'tion')}iles
    anc def t "/",f"Go   {eoot_hand}f test_hanfinglingstextfie"br si creayter_nglingnc p/jst_e    ds amet\ifeter_dict_anockReceiv    M br sit amet\n" *ockReceiv     i ockReceiv    .de
    ition: amet\ifeter_dict_anockReceiv :  k.br sit amet\n" *ockReceiv 
    aockReceiv 
  .de
    ition: aom_json_parameter_handles_request_without_es, app
):
  ho    @apf 
  ={ockReceiv    }"()

    await app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()f"Go   {ockReceiv    }"tasync def get_lorem():
        return "Lorem ipsum"

    # Nop
):
  ho    @apf 
  ={ockReceiv    }&
  ={ockReceiv 
  }"()

    ame(item: FromJSON[Item]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()f"Go   {ockReceiv    }"ta]},'
                + b'{"a":"LockReceive:"ipsockReceiv    MockReceive:      MockSend(),
  sum d
        MWe,value_two,],
  inell"ert r, "164"et[date],
       ll"1.2r, "er.3"et[date],
   not  00, 12.12, 64.01],
   e
:46:19.31334d",'ote: the follow54b2587a-0afc-40ec-a03d-13223d4bb04d  
 List[dateti"8ffd8e17-1a38-462f-ba71-3d92e52edf1f"              datrk.parametrize(
     Mockld", "lockReceivese.status"a":"ockReceive:"ips"ockReceiv    M ockReceive:  k. 20, "2"]],
ta = await app.response.tuery), MockReceive(), MockSe], ["helleoosiockReceive:"iplx1 == "on"_parameter_dict_aneoo,"ockReceive:"iples
    anc def t "/",f"Go   {eoo}: aom_json_parameter_handles_request_without_es, app
):
  ho    @apf 
  ={ockReceiv    }"()

    await app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()f"Go   {ockReceiv    }"tasync def get_lorem():
        return "Lorem ipsum"

    # Nop
):
  ho    @apf 
  ={ockReceiv    }&
  ={ockReceiv 
  }"()

    ame(item: FromJSON[Item]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()f"Go   {ockReceiv    }"ta]rametrize(
     Mockld", "lockReceiveasserof_inescope("GET"from_route(vals_From ceive"GET"from_route(vals_2rom ceiv24"64extfield = textfieluery), MockReceive(), MockSeeoosic def testes],
 ],
box1 == "on"c def t "/",f"Go   {eoot_hand}f test_hon_parameter_handles_request_without_es, app
):
  ho    @apb 
  =ert rFromJSON[Item]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()f"Go   {from_route(vals_F}"tasync def get_lorem():
        return "Lores, app
):
  ho    @apb 
  =ert &
  =164"FromJSON[Item]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()f"Go   {from_route(vals_2}"ta]rametrize(
       Mockld", "lockReceiveinescope("GET"p.response.tuery), MockReceive(), MockSe], ["helleoosic def test ],
   )


async def get_lorem():
        return "Lorem ipsum"

    # Note: the following example missing one of the properties
    # required by the constructor
    ait app(
        get_example_scope(
         get_example_sc,
            "/",
            ckReceive(),    [],
     Mameter_d", "x ceive([b'`
  `"tasync def get_lorem():
        return "Lores, app
):
  ho    @apb 
  =xxx"he properties
    # required by the constructor
    ait app(
        get_example_scope(
         get_example_sc,
            "/",
            lorem():
 ckReceive(),    [],
     I  MockR_handl['xxx']st_ha ceive([b'`
  `;   value = Lorem","b a  MockR ],"World")tasync def get_lorem():
        return "Lores, app
):
  ho    @apb 
  =xxx&
  =yyy"he properties
    # required by the constructor
    ait app(
        get_example_scope(
         get_example_sc,
            "/",
            lorem():
 ckReceive(),    [],
     I  MockR_handl['xxx', 'yyy']st_ha ceive([b'`
  `;   value = Lorem","b a  MockR ],"World")ta]rametrize(
       Mockld", "lockReceive     scope("GET"p.response.tuery), MockReceive(), MockSe], ["helleoosic def test         )


async def get_lorem():
        return "Lorem ipsum"

    # Note: the following example missing one of the properties
    # required by the constructor
    ait app(
        get_example_scope(
         get_example_sc,
            "/",
            ckReceive(),    [],
     Mameter_d", "x ceive([b'`
  `"tasync def get_lorem():
        return "Lores, app
):
  ho    @apb 
  =xxx"he properties
    # required by the constructor
    ait app(
        get_example_scope(
         get_example_sc,
            "/",
            lorem():
 ckReceive(),    [],
     I  MockR_handl['xxx']st_ha ceive([b'`
  `;   value = Lorem","b a  MockR     "World")tasync def get_lorem():
        return "Lores, app
):
  ho    @apb 
  =xxx&
  =yyy"he properties
    # required by the constructor
    ait app(
        get_example_scope(
         get_example_sc,
            "/",
            lorem():
 ckReceive(),    [],
     I  MockR_handl['xxx', 'yyy']st_ha ceive([b'`
  `;   value = Lorem","b a  MockR     "World")ta]rametrize(
       Mockld", "lockReceive notscope("GET"p.response.tuery), MockReceive(), MockSe], ["helleoosic def test        )


async def get_lorem():
        return "Lorem ipsum"

    # Note: the following example missing one of the properties
    # required by the constructor
    ait app(
        get_example_scope(
         get_example_sc,
            "/",
            ckReceive(),    [],
     Mameter_d", "x ceive([b'`
  `"tasync def get_lorem():
        return "Lores, app
):
  ho    @apb 
  =xxx"he properties
    # required by the constructor
    ait app(
        get_example_scope(
         get_example_sc,
            "/",
            lorem():
 ckReceive(),    [],
     I  MockR_handl['xxx']st_ha ceive([b'`
  `;   value = Lorem","b a  MockR    "World")tasync def get_lorem():
        return "Lores, app
):
  ho    @apb 
  =xxx&
  =yyy"he properties
    # required by the constructor
    ait app(
        get_example_scope(
         get_example_sc,
            "/",
            lorem():
 ckReceive(),    [],
     I  MockR_handl['xxx', 'yyy']st_ha ceive([b'`
  `;   value = Lorem","b a  MockR    "World")ta]rametrize(
       Mockld", "lockReceiveuuidscope("GET"p.response.tuery), MockReceive(), MockSe], ["helleoosic def test-10-2ox1 == "on"c def t "/",f"Go   {eoot_hand}f test_h_hand_From"99cb720c-26f2-43dd-89ea-"tasync def get_lorem():
        return "Lores, app
):
  ho    @apb 
  =: +"mult_hand_F)()

    await app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content
         get_example_sc,
            "/",
            ckReceive()lorem():
 f,    [],
     I  MockR_handl['{_hand_F}']st_ha  value = L ceive([b'`
  `; orem","b a  MockR-10-"World")ta]rametrize(
     MocklponselockReceiveuuidscope("GET"p.response.tuery),:
   MockReceive(), MockSe], ["helleoosic de str,
-10-2ox1 == "on"c def t "/",f"Go   {eoot_hand}f test_h_hand_Fromuuid4(from_json_parameter_handles_request_without_es, app
): +"mult_hand_F)k.[]wait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()f"Go   {_hand_F}"ta]rametrize(
     MocklponselockReceiveuuid_2scope("GET"p.response.tuery),:a_id/:b_id MockReceive(), MockSe], ["hella_idsic de str,
-10-2, b_idsic de str,
-10-2ox1 == "on"c def t "/",f"Go   {a_idt_hand}  awa{b_idt_hand}f test_h_hand_Fromuuid4(frst_h_hand_2romuuid4(from_json_parameter_handles_request_without_es, appf"/{_hand_F}/{_hand_2}"k.[]wait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()f"Go   {_hand_F}  awa{_hand_2}"ta]rametrize(
     MocklheadivepvaReceiveuuid_assescope("GET"p.response.tuery), MockReceive(), MockSe], ["hellx_eoosic deHeadiv["2020-10-22ox1 == "on"c def t "/",f"Go   {x_eoot_hand}f test_h_hand_Fromuuid4(frst_h_hand_2romuuid4(from_json_parameter_handles_request_without_em ipsum"

    # Note: the following example missi(b"x_eooad_mult_hand_F)()

    awa (b"x_eooad_mult_hand_2)()

    awhome(item: FromJSON[Item]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()f"Go   {[_hand_F,h_hand_2]}"ta]rametrize(
       MocklponselockReceiveuuidscope("GET"p.response.tuery),:documcei_id MockReceive(), MockSe], ["helldocumcei_idsic de str,
-10-2ox1 == "on"c def t "/",f"Go   {documcei_idt_hand}f test_h_hand_From"abc"rom_json_parameter_handles_request_without_es, app
): +"mult_hand_F)k.[]wait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content
         get_example_sc,
            "/",
            ckReceive()lorem():
 f,    [],
     I  MockR_handl['{_hand_F}']st_ha  value = L ceive([b'`documcei_id`; orem","b a  MockR-10-"World")ta]rametrize(
     MocklponselockReceiveuuidnse.status == 200
    data = await app:
   MockReceive(), MockSe], ["helleoosi-10-ox1 == "on"c def t "/",f"Go   {eoo}f test_h_hand_Fromuuid4(from_json_parameter_handles_request_without_es, app
): +"mult_hand_F)k.[]wait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()f"Go   {_hand_F}"ta]rametrize(
    ponsel   olu   d_ordiv( == 200
    data = await app:id MockReceive(), Mquest_wia(ox1 == "on"c def t "/","Af test_h  data = await appquect MockReceive(), Mquest_wib(ox1 == "on"c def t "/","Bf test_h  data = await app:
  /:ufo"MockReceive(), Mquest_wic(ox1 == "on"c def t "/","Cf test_h  data = await app:
  /quect MockReceive(), Mquest_wid(ox1 == "on"c def t "/","Df test_hon_parameter_handles_request_without_es, app
)quect k.[]wait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()"Bftest_hon_parameter_handles_request_without_es, app
)aaa)quect k.[]wait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()"Dftest_hon_parameter_handles_request_without_es, app
)aaa)quect/ k.[]wait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()"Dftest_hon_parameter_handles_request_without_es, app
)aaa)bbb k.[]wait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()"C"ta]rametrize(
    clicei_   viveinfo_partingsscope("GET"p.response.tuery), MockReceive(), MockSeclicei: CliceiInfod_m  viv: S  vivInfoox1 == "on"c def t "/",f"Clicei: {cliceit_hand}; S  viv: {m  vivt_hand}f test_hthoutxam       return "Lores, app
):
  h)est_hon_parameter_handlen "Loait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hellapplication/json"), (b"content-l0(      get_example_sc,
            "/",
            ckReceive()lorem():
 f,Clicei: {tuetu(n "Lotuery'clicei', ''))};   value = f"S  viv: {tuetu(n "Lotuery'm  viv', ''))}World")ta]rametrize(
    m  vice_partingssox1 == ckReain[b'= CkReain[b(from_js
ta = await ap"""
  Bx1 == "on"ize(__ def__(selfoad"
_lis amet\n" *asynself)eoo@a  
   rom_js
ta = await ap"""
  Ax1 == "on"ize(__ def__(self, b: Boad"
_lis amet\n" *asynself)dep@a b
1 == ckReain[b.addrn "Lod(A)1 == ckReain[b.addrn "Lod(B{['Hellapp@a FakeAum"
      (m  vices=ckReain[b)
    data = await app.response.tuery),orestatu MockReceive(), Mqu.status sic deS  vices[Abox1 == "on"_parameter_dict_anat_hand,"A)1 == "on"_parameter_dict_anat_hand)dep, Bo1 == "on"_parameat_hand)dep)eoo@app.
   r == "on"c def t "/","OK")
    data = await app.response.tuery),se.statu MockReceive(), Mse.status :"A)x1 == "on"_parameter_dict_ana,"A)1 == "on"_parameter_dict_anatdep, Bo1 == "on"_parameatdep)eoo@app.
   r == "on"c def t "/","OK")
    dt_ha cth'[{"{),orestatu pp
)se.statu }:er_handlen "Loxam       return "Lores, app cth
  h)est_hst_hon_parameter_handlendlen "Loait app(
 p(
 em]):
      , 55]}; B:  B: {[4, 5, 6]}; C:  C: {['HellHellapplication/json"),est_handler_from_json  get_example_sc,
            "/",
                ckReceive()"OK"'HellHellapplication/json"), (b"content-l0([]rametrize(
    di_middleware_enab    n "Lod m  vices_ d       _sign"coresox1 == ckReain[b'= CkReain[b(from_js"""
  Oper     CkRe"/"x1 == "on"ize(__ def__(selfoad"
_lis amet\n" *asynself)trace_ckRomuuid4(from_jsckReain[b.addrn "Lod(Oper     CkRe"/")
    dtirseroper     :        seOper     CkRe"/" amp_listasync pp@a FakeAum"
      (m  vices=ckReain[b)
sync pp.middlewares. pp5, 6di_n "Lo_middleware)
    data = await app.response.tuery), MockReceive(), MockSea: Oper     CkRe"/", b: Oper     CkRe"/")x1 == "on"_parameaest_b1 == "on"aonlocaldtirseroper     es
    anifetirseroper     onal_lis amet\n" *asyntirseroper     oampamet\n" *elss amet\n" *asynix_scenarrseroper     onalhanda
r == "on"c def t "/","OK")
    dt_ha_'[{"aange(2):er_handlen "Loxam       return "Lores, app
):
  h)est_hst_hon_parameter_handlendlen "Loait app(
 p(
 em]):
      , 55]}; B:  B: {[4, 5, 6]}; C:  C: {[HellHellapplication/json"),est_handler_from_json  get_example_sc,
            "/",
                ckReceive()"OK"'HellHellapplication/json"), (b"content-l0([]rametrize(
    quest: idi_middleware_no_support_t_h n "Lod mvcs_ d       r_sign"coresox1 == ckReain[b'= CkReain[b(from_js"""
  Oper     CkRe"/"x1 == "on"ize(__ def__(selfoad"
_lis amet\n" *asynself)trace_ckRomuuid4(from_jsckReain[b.addrn "Lod(Oper     CkRe"/")
Hellapp@a FakeAum"
      (m  vices=ckReain[b)
    data = await app.response.tuery), MockReceive(), MockSea: Oper     CkRe"/", b: Oper     CkRe"/")x1 == "on"_parameaest_handbr == "on"c def t "/","OK")
    dt_ha_'[{"aange(2):er_handlen "Loxam       return "Lores, app
):
  h)est_hst_hon_parameter_handlendlen "Loait app(
 p(
 em]):
      , 55]}; B:  B: {[4, 5, 6]}; C:  C: {[from_json  get_example_sc,
            "/",
                ckReceive()"OK"'HellHellapplication/json"), (b"content-l0([]rametrize(
    m  vice_partingse( assert):er_ha# Extremely unlikely, but still supportednifeuterum  rizein[seae( asser m  vice1 == ckReain[b'= CkReain[b(from_js"""
  Bx1 == "on"ize(__ def__(selfoad"
_lis amet\n" *asynself)eoo@a  
   rom_js
ta = await ap"""
  Ax1 == "on"ize(__ def__(self, b: Boad"
_lis amet\n" *asynself)dep@a b
1 == app@a FakeAum"
      (m  vices=ckReain[b)
    data = await app.response.tuery),orestatu MockReceive(), Mqu.status sic deS  vices[Abample(
S  vices(A(B()))assert app.responseer_dict_anat_hand,"A)1 == "on"_parameter_dict_anat_hand)dep, Bo1 == "on"_parameat_hand)dep)eoo@app.
   r == "on"c def t "/","OK")
    data = await app.response.tuery),se.statu MockReceive(), Mse.status :"AampA(B()))x1 == "on"_parameter_dict_ana,"A)1 == "on"_parameter_dict_anatdep, Bo1 == "on"_parameatdep)eoo@app.
   r == "on"c def t "/","OK")
    dt_ha cth'[{"{),orestatu pp
)se.statu }:er_handlen "Loxam       return "Lores, app cth
  h)est_hst_hon_parameter_handlendlen "Loait app(
 p(
 em]):
      , 55]}; B:  B: {[4, 5, 6]}; C:  C: {[from_json  get_example_sc,
            "/",
                ckReceive()"OK"'HellHellapplication/json"), (b"content-l0([]rametrize(
    m  vice_partingse( asser_overridet):er_ha# Extremely unlikely, but still supportednifeuterum  rizein[seae( asser m  vice1 == ckReain[b'= CkReain[b(from_js
ta = await ap"""
  Bx1 == "on"ize(__ def__(self,h_handsingload"
_lis amet\n" *asynself)eoo@a _list_of_ob
ta = await ap"""
  Ax1 == "on"ize(__ def__(self, b: Boad"
_lis amet\n" *asynself)dep@a b
1 ==  def test_haregisse.ednm  viceest_um kR ]sseadsing_pro( asser func    oargumceiom_jsckReain[b.addrr_dict_anA(B( ufo")))om_jsckReain[b.addrr_dict_anB( oof"))
1 == app@a FakeAum"
      (m  vices=ckReain[b)
    data = await app.response.tuery),orestatu MockReceive(), Mqu.status sic deS  vices[Abample(
S  vices(A(B(.
   )))assert app.responseer_dict_anat_hand,"A)1 == "on"_parameter_dict_anat_hand)dep, Bo1 == "on"_parameat_hand)dep)eoo@app.ufo"r == "on"c def t "/","OK")
    data = await app.response.tuery),se.statu MockReceive(), Mse.status :"AampA(B(.
   )))x1 == "on"_parameter_dict_ana,"A)1 == "on"_parameter_dict_anatdep, Bo1 == "on"_parameatdep)eoo@app.ufo"r == "on"c def t "/","OK")
    dt_ha cth'[{"{),orestatu pp
)se.statu }:er_handlen "Loxam       return "Lores, app cth
  h)est_hst_hon_parameter_handlendlen "Loait app(
 p(
 em]):
      , 55]}; B:  B: {[4, 5, 6]}; C:  C: {[from_json  get_example_sc,
            "/",
                ckReceive()"OK"'HellHellapplication/json"), (b"content-l0([]rametrize(
    um  _partingscope("GET""""
  {[4,AuthH     r(Authcei
      H     r)x1 == "on"_pmetrize(authcei
   e(self, ckRe"/")x1 == "on"""""headiveef test_ckRe"/"tuer_arrserheadiv(b"Authoriz     iles
    an  anifeheadiveef te:24T18:46:19.313346",ast_ ass."b":s(urlsafe_p64de
    headiveef te).de
    ition: )24T18:46:19.31334c def tIdcei
ty(6",a   TESTiles
    an  anelss amet\n" *asyn1334c def t_listasync pp.um _authcei
      ().add({[4,AuthH     r() test_h  data = await appqueretu-1 MockReceive(), Mquest_w(um  : [],
   Us r)x1 == "on"_pplicaum  y_optionalhandler_from_json_parameum  y_opti.authcei
      _m   f homTESTi1 == "on"c def t "/",f"Us r"alue: {um  y_opti."""ims['alue']}" test_h  data = await appqueretu-2 MockReceive(), Mquest_wi2(um  : Us r)x1 == "on"_pplicaum  onalhandler_from_json_parameum  yauthcei
      _m   f homTESTi1 == "on"c def t "/",f"Us r"alue: {um  y"""ims['alue']}" test_h  data = await appqueretu-3 MockReceive(), Mquest_wi3(um  : Idcei
ty)x1 == "on"_pplicaum  onalhandler_from_json_parameum  yauthcei
      _m   f homTESTi1 == "on"c def t "/",f"Us r"alue: {um  y"""ims['alue']}" test_h"""imsst_{"id": "00

   alue": "Charlie Brown
   role": "um  "}
    dt_ha cth'[{"[ppqueretu-1 pp
)queretu-2 pp
)queretu-3"]:er_handlen "Loxam       return "Lorem ipsum"

    # Note: the follo cth
 example missi(b"Authoriz     i, urlsafe_p64)

     ass.dumps("""ims)()

    ition: )whome(item: Fest_hst_hon_parameter_handlendlen "Loait app(
 p(
 em]):
      , 55]}; B:  B: {[4, 5, 6]}; C:  C: {[from_json  get_example_sc,
            "/",
                tion/json"), (b"content-l0(               ckReceive()"Us r"alue: Charlie Brown
ta]rametrize(
    pm","c":5artingscope("GET"p.response.tuery), MockReceive(), Mquest_w(pm": [],
   )x1 == "on"_parameter_dict_anpm", [],
   )1 == "on"c def t"Foo"
    d def get_lorem():
        return "Lores, app
):
  hwait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hell  get_example_sc,
            "/",
            tion/json"), (b"content-l0(           ckReceive()"Foo"
 ]rametrize(
    um _auth_raises_ f_tio_is_already_(b"rtedscope("GET""""
  {[4,AuthH     r(Authcei
      H     r)x1 == "on"_pmetrize(authcei
   e(self, ckRe"/")x1 == "on"""""headiveef test_ckRe"/"tuer_arrserheadiv(b"Authoriz     iles
    an  anifeheadiveef te:24T18:46:19.313346",ast_ ass."b":s(urlsafe_p64de
    headiveef te).de
    ition: )24T18:46:19.31334c def tIdcei
ty(6",a   TESTiles
    an  anelss amet\n" *asyn1334c def t_listasync le_sc,
  (b"rt,
     ques ,'
    raises(Run
   Error)x1 == "on"_pp.um _authcei
      ()
     ques ,'
    raises(Run
   Error)x1 == "on"_pp.um _authoriz     ()ta]rametrize(
    ( asser_headivsscope("GET"_pp.( asser_headivsst_(("Euest_w"r "Foo"),{['Hellapplication( asser_headivsstt_(("Euest_w"r "Foo"),{['Hellp.response.tponsey), MockReceive(), MockSeox1 == "on"c def t "/","      We,val)
    d def get_lorem():
        return "Lores, app
):
  hwait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hell/json"),e= tion/json"),'Hellapplica/json"), (b"content-l0(           /json"), headivstuer_arrse(b"Euest_w")tentb"Foo"
 ]rametrize(
    (b"rt (bop_evceisscope("GET"  _(b"rt called@a Fal),'Hell  _afeive(b"rt called@a Fal),'Hell  _(bop_called@a Fal),'ockReceive(), Mbet_hee(b"rt(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(b"rt called, == "on"  _(b"rt called@a      == "Wopmetrize(afeive(b"rt(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _afeive(b"rt called, == "on"  _afeive(b"rt called@a      == "Wopmetrize(  _(bop(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(bop_called, == "on"  _(bop_called@a      == "Woion  _(b"rt +=Mbet_hee(b"rt== "Woionafeive(b"rt +=Mafeive(b"rt== "Woion  _(bop +=M  _(boptasync le_sc,
  (b"rt,
 (             _(b"rt called@                     _afeive(b"rt called@                     _(bop_called@   Fal),'ockRecle_sc,
  (bop(
 (             _(b"rt called@                     _afeive(b"rt called@                     _(bop_called@        =]},'
                + b'{"t app(:
  "envir  i, "orestatu ]parametrize(
    moun
ed_tio_auto_evceisst app(singlo amet\ifet app(se()"envir  i amet\n" *os.envir  ["APP_MOUNT_AUTO_EVENTS"bamp"1"
    d   cei_app@a FakeAum"
      (
 (    ifet app(se()"erestatu  amet\n" *ockcei_app.moun
_auto_evceis@a      == "Woio@a FakeAum"
      (
 (    ockcei_app.moun
(
):
 cope
"GET"  _(b"rt called@a Fal),'Hell  _afeive(b"rt called@a Fal),'Hell  _(bop_called@a Fal),'ockReceive(), Mbet_hee(b"rt(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(b"rt called, == "on"  _(b"rt called@a      == "Wopmetrize(afeive(b"rt(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _afeive(b"rt called, == "on"  _afeive(b"rt called@a      == "Wopmetrize(  _(bop(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(bop_called, == "on"  _(bop_called@a      == "Woion  _(b"rt +=Mbet_hee(b"rt== "Woionafeive(b"rt +=Mafeive(b"rt== "Woion  _(bop +=M  _(boptasync le_scockcei_app.(b"rt,
 (             _(b"rt called@                     _afeive(b"rt called@                     _(bop_called@   Fal),'ockRecle_scockcei_app.(bop(
 (             _(b"rt called@                     _afeive(b"rt called@                     _(bop_called@        =]rametrize(
    (b"rt (bop_mserieturevceisscope("GET"  _(b"rt coun
@a 0'Hell  _(bop_coun
@a 0'ockReceive(), Mbet_hee(b"rt_1(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(b"rt coun
, == "on"  _(b"rt coun
@+em1 ockReceive(), Mbet_hee(b"rt_2(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(b"rt coun
, == "on"  _(b"rt coun
@+em1 ockReceive(), Mbet_hee(b"rt_3(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(b"rt coun
, == "on"  _(b"rt coun
@+em1 ockReceive(), M  _(bop_1(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(bop_coun
, == "on"  _(bop_coun
@+em1 ockReceive(), M  _(bop_2(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(bop_coun
, == "on"  _(bop_coun
@+em1 ockRecion  _(b"rt +=Mbet_hee(b"rt_1ockRecion  _(b"rt +=Mbet_hee(b"rt_2ockRecion  _(b"rt +=Mbet_hee(b"rt_3== "Woion  _(bop +=M  _(bop_1ockRecion  _(bop +=M  _(bop_2tasync le_sc,
  (b"rt,
 (             _(b"rt coun
@a= 3              _(bop_coun
@a= 0'ockRecle_sc,
  (bop(
 (             _(b"rt coun
@a= 3              _(bop_coun
@a= 2 =]rametrize(
    (b"rt (bop_mserieturevceis_ueter_de
 ratovsscop: Aum"
      o("GET"  _(b"rt coun
@a 0'Hell  _(bop_coun
@a 0'ockRe@cion  _(b"rtockReceive(), Mbet_hee(b"rt_1(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(b"rt coun
, == "on"  _(b"rt coun
@+em1 ockRe@cion  _(b"rtockReceive(), Mbet_hee(b"rt_2(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(b"rt coun
, == "on"  _(b"rt coun
@+em1 ockRe@cion  _(b"rtockReceive(), Mbet_hee(b"rt_3(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(b"rt coun
, == "on"  _(b"rt coun
@+em1 ockRe@cion  _(bopockReceive(), M  _(bop_1(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(bop_coun
, == "on"  _(bop_coun
@+em1 ockRe@cion  _(bopockReceive(), M  _(bop_2(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(bop_coun
, == "on"  _(bop_coun
@+em1 ockRecle_sc,
  (b"rt,
 (             _(b"rt coun
@a= 3              _(bop_coun
@a= 0'ockRecle_sc,
  (bop(
 (             _(b"rt coun
@a= 3              _(bop_coun
@a= 2 =]rametrize(
      _middlewares_configuredrevceiscop: Aum"
      o("GET"  _middlewares_configur     _coun
@a 0'ockRe@cion  _middlewares_configur     
"on"ize(  _middlewares_configur     _1(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _middlewares_configur     _coun
, == "on"  _middlewares_configur     _coun
@+em1 ockRe@cion  _middlewares_configur     
"on"ize(  _middlewares_configur     _2(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _middlewares_configur     _coun
, == "on"  _middlewares_configur     _coun
@+em1 ockRecle_sc,
  (b"rt,
 (             _middlewares_configur     _coun
@a= 2 =]rametrize(
    tio_evceis_de
 ratov_args_supportscop: Aum"
      o("GET"@cion  _(b"rtockReceive(), Mbet_hee(b"rt_1(sum"
      : FakeAum"
      oad"
_lis  )


async@cion  _(b"rt()ockReceive(), Mbet_hee(b"rt_2(sum"
      : FakeAum"
      oad"
_lis  )


a]rametrize(
    (b"rt (bop_removurevcei       rsscope("GET"  _(b"rt coun
@a 0'Hell  _(bop_coun
@a 0'ockReceive(), Mbet_hee(b"rt_1(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(b"rt coun
, == "on"  _(b"rt coun
@+em1 ockReceive(), Mbet_hee(b"rt_2(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(b"rt coun
, == "on"  _(b"rt coun
@+em1 ockReceive(), M  _(bop_1(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(bop_coun
, == "on"  _(bop_coun
@+em1 ockReceive(), M  _(bop_2(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(bop_coun
, == "on"  _(bop_coun
@+em1 ockRecion  _(b"rt +=Mbet_hee(b"rt_1ockRecion  _(b"rt +=Mbet_hee(b"rt_2ockRecion  _(bop +=M  _(bop_1ockRecion  _(bop +=M  _(bop_2tasync ion  _(b"rt -=Mbet_hee(b"rt_2ockRecion  _(bop -=M  _(bop_2tasync le_sc,
  (b"rt,
 (             _(b"rt coun
@a= 1              _(bop_coun
@a= 0'ockRecle_sc,
  (bop(
 (             _(b"rt coun
@a= 1              _(bop_coun
@a= 1
a]rametrize(
    (b"rt runs   _anaume("GET"  _(b"rt coun
@a 0'ockReceive(), Mbet_hee(b"rt(sum"
      : FakeAum"
      oad"
_lis amet\n" *_parameter_dict_anaum"
      , FakeAum"
      o                tio"
      onal 20, == "on"aonlocald  _(b"rt coun
, == "on"  _(b"rt coun
@+em1 ockRecion  _(b"rt +=Mbet_hee(b"rt=async le_sc,
  (b"rt,
 (             _(b"rt coun
@a= 1 async le_sc,
  (b"rt,
 (             _(b"rt coun
@a= 1 a]rametrize(
          s   _(b"rt error_asgi_lifespanscope("GET"_eive(), Mbet_hee(b"rt(sum"
      : FakeAum"
      oad"
_lis amet\n" *raise Run
   Error("Crash!") == "Woion  _(b"rt +=Mbet_hee(b"rt== "Wmock_send@a {[4, 5, 6]== "Woionauto_(b"rt = Fal),'ockRecle_sc,
 lorem():
 {":"ip": "lifespani, "messagp": "lifespan (b"rtup"}ait app(
 em]):
       example missiamet\n" *asyn1334{":"ip": "lifespan (b"rtup"}ait app(
 asyn1334{":"ip": "lifespan (hutdown
}ait app(
 asyn]me(item: FromJSON[Itmock_send}; C: {['Hellapplicamock_send.messagps[0]@a= {":"ip": "lifespan (b"rtup.failed"}
 ]rametrize(
    tio_ques moun
s       s   _(b"rt error_asgi_lifespanscop: Aum"
      o("GET"_eive(), Mbet_hee(b"rt(sum"
      : FakeAum"
      oad"
_lis amet\n" *raise Run
   Error("Crash!") == "W), Mfooeox1 == "on"c def t 
   rom_jsother_app@a Aum"
      (
 m_jsother_appsponse.taddruery),eooad_eoo) == "Woionmoun
(
)eooad_other_app)ockRecion  _(b"rt +=Mbet_hee(b"rt=asyncmock_r
     @a {[4,:
       example [{":"ip": "lifespan (b"rtup"}a4{":"ip": "lifespan (hutdown
}]
em: Fest_hmock_send@a {[4, 5, 6]=ockRecle_sc,
 lorem():
 {":"ip": "lifespani, "messagp": "lifespan (b"rtup"}acmock_r
     ,hmock_send; C: {['Hellapplicamock_send.messagps[0]@a= {":"ip": "lifespan (b"rtup.failed"}
 ]ize(
    pmgisse._controllive:"ips       _empty_assescope("GET"       tion/jgisse._controllivs([])onal_lista]rametrize(
    pmson"),_normaliz     _wr pp5dscope("GET"_pp.um _covss          llow_t app(s=es,  POST DELETE:
 cllow_origr_d="https://www.neose.oi.devWorld")tasync), Moeadivsscddi     s_headivs)x1 == "on"ize(de
 ratov(nexi       r)x1 == "on"""""@wr ps(nexi       r)amet\n" *asynixmetrize(wr pp5ds*args, **kwargsoad"
Rmson"), amet\n" *asyn1334c son"),e= ensure pmson"),(cle_scnexi       rs*args, **kwargso{[from_jsonn" *asyntor"alue,h_hand'[{"cddi     s_headivs amet\n" *asyn13341334c son"),taddrheadiv(alue()

    a,h_hand()

    aw
amet\n" *asyn1334c def t/json"),'amet\n" *async def twr pp5d
r == "on"c def tde
 ratovxtfield = textfieluery), MockRe@oeadivss((tX-Foo"s""Foo"),{MockReceive(), MockSeox1 == "on"c def t"     , We,val
    d def get_lorem():
        return "Lores, app
):
  hwait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hell/json"),e= tion/json"),'Hellapplica/json"), (b"content-l0(           /json"), headivstuer_eterley tX-Foo")tentb"Foo"
           /json"), ckRecei.bodytentb"     , We,val
 ]rametrize(
    pmson"),_normaliz     _wues covsscope("GET"_pp.um _covss          llow_t app(s=es,  POST DELETE:
 cllow_origr_d="https://www.neose.oi.devWorld")tasyncp.response.tuery), MockReceive(), MockSeox1 == "on"c def t"     , We,val
    d def get_lorem():
        return "Lores, app
):
  hwait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hell/json"),e= tion/json"),'Hellapplica/json"), (b"content-l0(           /json"), ckRecei.bodytentb"     , We,val
 m_json_parameter_handles_request_without_es, app
):
  y tOrigr_"r b"https://www.neose.oi.devW)hwait app(
 em]):
      , 55]}; B: {[4, 5, 6]}; C: {['Hell/json"),e= tion/json"),'Hellapplica/json"), (b"content-l0(           /json"), ckRecei.bodytentb"     , We,val
 ]rametrize(
    tametrevcei raises_t_h fire t app(eox1 == evcei@a Aum"
      SmetEvceis_lis)
     ques ,'
    raises(T"ipError)x1 == "on"_n_parevcei.fire()ta]rametrize(
    sum"
       raises_t_h un      drn "Loe:"ipscope("GET"ques ,'
    raises(T"ipError)    tioe:"ip error:est_hst_hon_parameter_handlendle{":"ip": "eooa}ait app(
 p(
 em]):
      , 55]}; B:  B: {[4, 5, 6]}; C:  C: {[from_       multtioe:"ip errory_opti)ve()"Unsupportednn "Lox:"ip: 
   ro
ize(
    moun
ter_self raisesscope("GET"ques ,'
    raises(T"ipError)x1 == "on"_pp.moun
(
)n"Lo:
 cope
"]},'
                + b'{"     :
  404,def Found]parametrize(
    custom       r_t_h 404_not_t_undscop,"ockRe):er_ha# Issnd'#538asyncp.resexce            rsockRe)ockReceive(), Mnot_t_und       rs
n" *asynself: FakeAum"
      , r],
     R, ["hellexc:def Found; C: {ad"
Rmson"), amet\n" *aonlocald 20, == "on"       melfonal 20, == "on"_parameter_dict_anexc,def Found)1 == "on"c def tRmson"),(-l0, ckRecei=TexiCkRecei("Called"))tasyncp.response.tuery), MockReceive(), MockSeox1 == "on"caise ef Found6]=ockRecle_sc,
 ls_request_without_es, app
):a,hem]):
      ,  {[4, 5, 6]{['Hellapplication/json"),onalhandler_from_/json"),:tRmson"),e= tion/json"),'(           /json"),(     ctu s_pmson"),_ "/"xample_sc          "/",
            tctu s_pmson"),_ "/"xa()"Called"
"]},'
                + b'{"     :
  404,def Found]parametrize(
    http_exce            re:"ip    olu   dscop,"ockRe):er_ha# https://guesub ckm/Neose.oi/Bla4, heep/issnds/538#issndckmmcei-2867564293
1 ==  dTHIS IS NOT RECOMMENDED! IT IS NOT RECOMMENDED TO USE A CATCH-ALL EXCEPTION1 ==  dHANDLER LIKEdTHE ONE BELOW. BLACKSHEEP AUTOMATICALLYdHANDLES NON-HANDLEDer_ha# EXCEPTIONS USINGdTHE DIAGNOSTIC PAGES IF SHOW_ERROR_DETAILS IS ENABLED, AND USING1 ==  dTHE INTERNAL SERVER ERRORdHANDLER OTHERWISE!1 ==  dUSE INSTEAD:er_ha# p.resexce            rs500) or"p.resexce            rsIRecr  sS  vivError)asyncp.resexce            rsExce     MockReceive(), M   ch_all(self: FakeAum"
      , r],
     R, ["hellexc:def Foundox1 == "on"c def tRmson"),(5l0, ckRecei=TexiCkRecei("Oh,def!"))tasyncp.resexce            rsockRe)ockReceive(), Mnot_t_und       rs
n" *asynself: FakeAum"
      , r],
     R, ["hellexc:def Found; C: {ad"
Rmson"), amet\n" *c def tRmson"),(-l0, ckRecei=TexiCkRecei("Called"))tasyncp.response.tuery), MockReceive(), MockSeox1 == "on"caise ef Found6]=ockRecle_sc,
 ls_request_without_es, app
):a,hem]):
      ,  {[4, 5, 6]{['Hellapplication/json"),onalhandler_from_/json"),:tRmson"),e= tion/json"),'(           /json"),(     ctu s_pmson"),_ "/"xample_sc          "/",
            tctu s_pmson"),_ "/"xa()"Called"
"]},'
                + b'{"     :
  CkRf"
 ell409]parametrize(
    http_exce            re:"ip    olu   d_inheriict_anaum,"ockRe):er_ha# https://guesub ckm/Neose.oi/Bla4, heep/issnds/538#issndckmmcei-2867564293
1 == p.resexce            rsockRe)ockReceive(), M   ch_ckRf"
 es(self: FakeAum"
      , r],
     R, ["hellexc:dCkRf"
 eox1 == "on"c def tRmson"),(55]}; B:  B: 409, ckRecei=TexiCkRecei(f"Custom {:"ipsexc).__alue__} H     r!iles
    anfrom_js"""
  FooCkRf"
 e(CkRf"
 eox1 == "on"p"
 rom_js"""
  UfoCkRf"
 e(CkRf"
 eox1 == "on"p"
 rom_jsp.response.tuery),
   MockReceive(), Mfooeox1 == "on"caise FooCkRf"
 e()tasyncp.response.tuery),ufo"MockReceive(), Mufoeox1 == "on"caise UfoCkRf"
 e()tasyncorem",     sst_{ value = L,
   : "Custom FooCkRf"
 e H     r!i, value = L,ufo": "Custom UfoCkRf"
 e H     r!i, valu}
    dt_hakey,h_hand'[{"orem",     s.items():est_hst_hon_paramets_request_without_es, appkeya,hem]):
      ,  {[4, 5, 6]{['HellHellapplication/json"),est_handler_from_json/json"),:tRmson"),e= tion/json"),'(               /json"),(         ctu s_pmson"),_ "/"xample_sc          "/",
                tctu s_pmson"),_ "/"xa()_list_o]},'
                + b'{"     :
  5l0, IRecr  sS  vivError]parametrize(
    custom       r_t_h 5l0einecr  s_   viveerrorscop,"ockRe):er_ha# Issnd'#538asyncp.resexce            rsockRe)ockReceive(), Mun      drexce            rs
n" *asynself: FakeAum"
      , r],
     R, ["hellexc:dIRecr  sS  vivError; C: {ad"
Rmson"), amet\n" *aonlocald 20, == "on"       melfonal 20, == "on"_parameter_dict_anexc,dIRecr  sS  vivError)async"on"_parameter_dict_anexc.sourcp error, T"ipError)amet\n" *c def tRmson"),(-l0, ckRecei=TexiCkRecei("Called"))tasyncp.response.tuery), MockReceive(), MockSeox1 == "on"caise T"ipError6]=ockRecle_sc,
 ls_request_without_es, app
):a,hem]):
      ,  {[4, 5, 6]{['Hellapplication/json"),onalhandler_from_/json"),:tRmson"),e= tion/json"),'(           /json"),(     ctu s_pmson"),_ "/"xample_sc          "/",
            tctu s_pmson"),_ "/"xa()"Called"
"]), Ms_repydaei
 eerrorscls,46",a{ad"
str:est_horem","beerroramp_listasynctryx1 == "on"cls(**6",a{est_horce   VMock     Error    vMock      error:est_hst_horem","beerrorampvMock      error. ass,
 (           ter_dict_anexem","beerrord_mul)
n" *c def texem","beerrorta]rametrize(
    sum"
       pydaei
 e asseerrorscope("GET""""
  CreateCatInput(BaseModelox1 == "on"alue: mul1 == "on":"ip: mul1asyncp.response.tposry),api/    MockReceive(), Mcreate_   (6",a: CreateCatInput   )


async#    Mock JSON:'Hell  get_examb'{"eooa:"hand Mock"}'
est_horem","beerroramps_repydaei
 eerrorsCreateCatInputa4{"
   : "hand Mock"}from_json_parameter_handles_request_without_em ipsum"

   POSTNote: the followiapi/    , example missiamet\n" *asyn1334(b"  get_e-lengthad_multlen(  get_e))()

    await app(
 asyn1334(b"  get_e-:"ip"r b"sum"
      / ass"wait app(
 asynhome(item: FromJSON[Item]):
      [  get_e], 55]}; B: {[4, 5, 6]}; C: {['Hell/json"),e= tion/json"),'Hellapplica/json"), (b"content4l0(           /json"), ckRecei.body.de
    )ve()exem","beerrorta]rametrize(
    sum_fallback_ronseycope("GET"), Mnot_t_und       rsox1 == "on"c def t "/","Euest_w"r 404) == "Woionponse.tfallbacke= not_t_und       r
 m_json_parameter_handles_request_without_es, app
)not-regisse.ed:
  hwahem]):
      ,  {[4, 5, 6]; C: {['Hell/json"),e= tion/json"),'Hellapplica/json"), (b"content4l4            lple_sc          "/",
)ve()"Euest_w" a]rametrize(
     sts_middlewarescope("GET"p.response.tuery), MockReceive(), MockSeox1 == "on"c def t"OK"'
sync pp.middlewares. pp5, 6HSTSMiddlewares)]=ockRecle_sc,
 ls_request_without_es, app
):
  hwahem]):
      ,  {[4, 5, 6]{['Hell/json"),e= tion/json"),'Hellapplica/json"), (b"content-l0(           lple_sc          "/",
)ve()"OK"'Hellmul
 e_transporte= /json"), headivstuer_arrse(b"Sul
 e-Transport-Securiiy"{[from_       mul
 e_transporte=ntb"max-age=31536000;   cludeSubDomar_d;"
"]},'
         skipif(sys.vivs  d_info < (3, 10), r]aass="r],
i/js ,'
hon3.10 or"higher"parametrize(
    pep_593scope("GET""""'HellT   seaescenario that w   reportedn   bug her, amet\https://guesub ckm/Neose.oi/Bla4, heep/issnds/257[from_Aum"
       (b"rt-up failed"GET""""'Hellfrom 6",a"""
 js importe6",a"""
 1asyncp6",a"""
 1GET""""
  Petx1 == "on"alue: mul1 == "on"age:   t |p_listasyncp.response.tuery),pets MockReize(pets({ad"
"2020Pet]x1 == "on"c def tiamet\n" *asynPet(alue="Re_"r age=_lis),amet\n" *asynPet(alue="Stimpy"r age=3),amet\n" *]tasync)ocsst_Op5,APIH     r(info=Info(title="Euest_w API"r vivs  d="0.0.1: )24T18)ocs.5art sum(cope
"GET"cle_sc,
 ls_request_without_es, app
)pets 
  hwahem]):
      ,  {[4, 5, 6]{['Hell/json"),e= tion/json"),'Hellapplica/json"), (b"content-l0(           lple_sc          ass,
)ve()[orem():
 {"alue": "Re_"r "agp": _lis}ait app(
 {"alue": "Stimpy"r "agp": 3}ait ap] a]rametrize(
    lifespanrevceiscop: Aum"
      o("GET" defialized@a Fal),'Helldi   sed@a Fal),'ockRep.reslifespanockReceive(), MsckS tametrgen() amet\n" *aonlocald defializedamet\n" *aonlocalddi   sed'(         defialized@a              yieldamet\n" *di   sed@a      == "Wole_sc,
  (b"rt,
 (            defialized@                   di   sed@   Fal),'ockRecle_sc,
  (bop(
 (            defialized@                   di   sed@        =]ize(
    moun
ter_,
 s_ueter_thwitlue_ponse. raises_errors):er_ha# :
 reatesg_proscenario h pp5,ter wheng_pro( asser eterlet   ponse.est_um kRfor; C: # boes ,ckceiWoio@ awachildl 20, == # https://guesub ckm/Neose.oi/Bla4, heep/issnds/443     eterle_ponse.@a  str,r6]; C: Aum"
      (ponse.=eterle_ponse.)
     ques ,'
    raises(Shckcd str,rError)x1 == "on"Aum"
      (ponse.=eterle_ponse.)
 ]rametrize(
    sum"
       sub_ponse. normaliz     s):er_haponse.@a  str,r6]; C: oio@a FakeAum"
      (ponse.= str,r6sub_ponse.s=[ponse.]]{['Hell# https://guesub ckm/Neose.oi/Bla4, heep/issnds/466asyncp6",a"""
 1GET""""
  Perassx1 == "on"idsi       se  t amp_list == "on"alue: mulamp" rom_js
ponse.tposry), MockReceive(), Mo    (r],
     R, ["hellp: Perassox1 == "on"c def tf"{r],
   .clicei_ip}:     , {p.alue}!"
'Hell  get_examb'{"id": 1   alue": "Charlie Brown
}'
est_hon_parameter_handles_request_without_em ipsum"

   POSTNote: the followi , example missiamet\n" *asyn1334(b"  get_e-lengthad_multlen(  get_e))()

    await app(
 asyn1334(b"  get_e-:"ip"r b"sum"
      / ass"wait app(
 asynhome(item: FromJSON[Item]):
      [  get_e], 55]}; B: {[4, 5, 6]}; C: {['Hell/json"),e= tion/json"),'Hellapplica/json"),onalhandler_from_applica/json"), (b"content-l0("]},'
         skipif(est_h_hack  e_callonal_lis, r]aass="Pydaei
  v1h_hack  e_argumceisonalhandsupported"
parametrize(
    pydaei
 e_hack  e_call_scenario(e("GET"_pp@a FakeAum"
      (mhow error_details=    , ponse.= str,r6 )24T18s_re= tion/onse.tuerrom_js
uery),
   1 MockRe@_hack  e_callockReceive(), MsckSthingsi: Anhan  ede  t, Fieldls_=1  le=10) amp1ox1 == "on"c def tf"i={i}"rom_js
uery),
   2 MockRe@_hack  e_callockReceive(), MsckSthing_wues pmson"),_anhan     (1 == "on"i: Anhan  ede  t, Fieldls_=1  le=10) amp1,; C: {ad"
Rmson"), amet\n" *c def t "/",f"i={i}")tasyncorem",     sst_iamet\n" *(""r -l0, "i=1"wait app(
 ("i=5"r -l0, "i=5"wait app(
 ("i=-3"r 400, "Input mhouldlbe greater than or"],
aldto 1"wait app(
 ("i=20"r 400, "Input mhouldlbe less than or"],
aldto 10"wait ap]
    dt_ha5, po  t [{"[pp
   1 pp
)
   2 ]x1 == "on"t_ha,
 ryd_mu"con, pmson"),_ "/"x[{"orem",     s amet\n" *asynin_parameter_handlendlendles_request_without_es, app5, po  t,a,
 ry=,
 rywait app(
 asyn1334em]):
      , 55]}; B:  B:  B: {[4, 5, 6]}; C:  C: em: Fest_hst_hHell/json"),e= tion/json"),'Hell               /json"),est_handler_from_jsonrom_applica/json"), (b"content(b"con
es
    an  anife  t(PYDANTIC_LIB_VERSION[0]) > 1 amet\n" *asyn1334applica/json"),_ "/"x[{"lple_sc          "/",
)("]},'
         skipif(est_h  t(PYDANTIC_LIB_VERSION[0]) < 2, r]aass="Rung_pst_
    only ques Pydaei
  v2"
parametrize(
    refs_characse.s      ingse("GET"_pp@a FakeAum"
      (mhow error_details=    , ponse.= str,r6 )24T18s_re= tion/onse.tuerrom_js# TODO: whengsupport"t_haP'
hon < 3.12est_dropp5d,om_js# _profollowter can bharewritet_ quest:  T"ipVar  lik, amet\#om_js# """
  Rmson"),[D",aT](BaseModelox1 == #rom_jsD",aT@a  "ipVar("D",aT"from_js"""
  Rmson"),(BaseModel, Generic[D",aT])x1 == "on"i",a: D",aTrom_js"""
  Cat(BaseModelox1 == "on"idsiin
, == "on"alue: mul1 == "on" reat    
   :"i",e
   tasync)ocsst_Op5,APIH     r(info=Info(title="Euest_w API"r vivs  d="0.0.1: )24T18)ocs.5art sum(cope
"GET"
uery),    MockRe), Ms_nericequest_w({ad"
Rmson"),[Cat]  )


async@uery),   s MockRe), Ms_nericeasseequest_w({ad"
asse[Rmson"),[Cat]]  )


asyncole_sc,
  (b"rt,
 (     asse)ocsst_)ocs._ asse)ocs.de
    ition: (    yamle)ocsst_)ocs._yamle)ocs.de
    ition: (    sem"st_ ass."b":s( asse)ocs{['Hell# "$ref": "#/ckmon"ceis/schemas/Cat"    dt_hakeyx[{"sem"["ckmon"ceis"]["schemas"].keys():est_hst_hopplica/j   tch_em ipsum"

   ^[a-zA-Z0-9-_.]+$appkeyme(item: Fr "$ref)_lists mu     tch /^[a-zA-Z0-9-_.]+$/"'HellHellapplicaf'"$ref": "#/ckmon"ceis/schemas/{key}"'x[{" asse)ocs'HellHellapplicaf"$ref: '#/ckmon"ceis/schemas/{key}'"x[{"yamle)ocs
 ]rametrize(
    sum"
       sse(e("GET"_pp@a FakeAum"
      (mhow error_details=    , ponse.= str,r6 )24T18s_re= tion/onse.tuerrom_js
uery),evceis MockReceive(), Mqvceis_      rsoad"
AeiveIse.ab  [S  viv 5,tEvcei]x1 == "on"t_hai'[{"aange(3)x1 == "on"""""yield S  viv 5,tEvcei({"messagp": f"      We,va {i}"})amet\n" *asynin_paraeiveio.sleep(0.05{['Helln "Loxam       return "Lores, app
)evceis 
  h)est_hmock_send@a {[4, 5, 6]=ockRecle_sc,
 ln "Loahem]):
      ,  mock_send{['Hell# A      /json"),e(b"con
Hell/json"),e= tion/json"),'Hellapplica/json"),onalhandler_from_applica/json"), (b"content-l0("Hell# A      CkRecei- "ipMoeadiv(           /json"), headivstuer_arrse(b"  get_e-:"ip")tentb" "/")evcei-muleam"("Hell# A      muleamedMqvceis'Hellmuleamed_6",ast_b"".jo    example [msg["body"]"t_hamsg'[{"mock_send.messagpsnife"body"'[{"msg]
em: Fest_hexem","beevceis@a   example 'i",a: {"messagp":"      We,va 0"}\n\n' example 'i",a: {"messagp":"      We,va 1"}\n\n' example 'i",a: {"messagp":"      We,va 2"}\n\n' exam)from_       muleamed_6",a.de
    itio-8")ve()exem","beevceis' ]rametrize(
    sum"
       sse_plain_ "/",
("GET"_pp@a FakeAum"
      (mhow error_details=    , ponse.= str,r6 )24T18s_re= tion/onse.tuerrom_js
uery),evceis MockReceive(), Mqvceis_      rsoad"
AeiveIse.ab  [S  viv 5,tEvcei]x1 == "on"t_hai'[{"aange(3)x1 == "on"""""yield TexiS  viv 5,tEvcei(f"      We,va {i}")amet\n" *asynin_paraeiveio.sleep(0.05{['Helln "Loxam       return "Lores, app
)evceis 
  h)est_hmock_send@a {[4, 5, 6]=ockRecle_sc,
 ln "Loahem]):
      ,  mock_send{['Hell# A      /json"),e(b"con
Hell/json"),e= tion/json"),'Hellapplica/json"),onalhandler_from_applica/json"), (b"content-l0("Hell# A      CkRecei- "ipMoeadiv(           /json"), headivstuer_arrse(b"  get_e-:"ip")tentb" "/")evcei-muleam"("Hell# A      muleamedMqvceis'Hellmuleamed_6",ast_b"".jo    example [msg["body"]"t_hamsg'[{"mock_send.messagpsnife"body"'[{"msg]
em: Fest_hexem","beevceis@a   example "i",a:       We,va 0\n\n" "i",a:       We,va 1\n\n" "i",a:       We,va 2\n\n" exam)from_       muleamed_6",a.de
    itio-8")ve()exem","beevceis' ]rametrize(
    middlewares_execnse_t_h no_ponse_bye( assert):er_ha"""'HellT    that middlewares are execnsedntor"ao  ckRfigured ponses byo( asser.er_ha"""'Hell# issnd'#619; C: oio@a FakeAum"
      (ponse.= str,r6]{['Hellmiddleware_called@a Fal),'ockReceive(), Mmiddlewaresr, ["hellnexi       r)x1 == "on"aonlocaldmiddleware_calledomJSON[Itmiddleware_called@a              c def tcle_scnexi       rsr],
   )1
sync pp.middlewares. pp5, 6middlewaree
"GET"cle_sc,
 ls_request_without_es, app
)not_t_und 
  hwahem]):
      ,  {[4, 5, 6]{['Hell/json"),e= tion/json"),'Hellapplica/json"),onalhandler_from_applica/json"), (b"content4l4 'Hellapplicamiddleware_called@                                                                                                                                                              