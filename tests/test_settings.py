"""Define test suite for pynote.settings"""

from pathlib import Path

# from ..src.libs.objects import Return, Settings, Status
from ..src.libs.interface import Return, Settings, Status
test_dir = Path(__file__).parent.name


def test_status():
    assert Status.OK.value == 200
    assert Status.CREATED.value == 201
    assert Status.ACCEPTED.value == 202
    assert Status.NO_CONTENT.value == 204
    assert Status.MOVED_PERMANENTLY.value == 301
    assert Status.FOUND.value == 302
    assert Status.NOT_MODIFIED.value == 304
    assert Status.BAD_REQUEST.value == 400
    assert Status.UNAUTHORIZED.value == 401
    assert Status.FORBIDDEN.value == 403
    assert Status.NOT_FOUND.value == 404
    assert Status.METHOD_NOT_ALLOWED.value == 405
    assert Status.CONFLICT.value == 409
    assert Status.INTERNAL_SERVER_ERROR.value == 500
    assert Status.NOT_IMPLEMENTED.value == 501
    assert Status.BAD_GATEWAY.value == 502
    assert Status.SERVICE_UNAVAILABLE.value == 503


def test_return():
    r = Return(code=Status.OK, obj="test", msg="test")
    assert r.code == Status.OK
    assert r.obj == "test"
    assert r.msg == "test"


def test_settings():
    s = Settings(test_dir)
    editor, wiki_dir, notebook_dir = s["editor"], s["wiki_dir"], s["notebook_dir"]
    assert editor == "nvim"
    assert wiki_dir == "~/wiki"
    assert notebook_dir == "~/wiki/notes"
