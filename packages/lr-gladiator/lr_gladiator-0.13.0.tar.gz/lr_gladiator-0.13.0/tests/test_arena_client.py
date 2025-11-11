# tests/test_arena_client.py
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from requests.structures import CaseInsensitiveDict
from collections.abc import Mapping

from gladiator.config import LoginConfig
from gladiator.arena import ArenaClient, ArenaError


@pytest.fixture
def cfg():
    return LoginConfig(arena_subdomain="dummy", api_key="x")


@pytest.fixture
def tmpout(tmp_path):
    """Provide a temporary output directory."""
    return tmp_path


def test_client_instantiates(cfg):
    c = ArenaClient(cfg)
    # headers is a CaseInsensitiveDict, which implements Mapping
    assert isinstance(c.session.headers, (CaseInsensitiveDict, Mapping))
    assert "Arena-Usage-Reason" in c.session.headers
    assert c.session.headers["Arena-Usage-Reason"] == "gladiator/cli"


def test_version_of(cfg):
    c = ArenaClient(cfg)
    assert c._version_of({"version": "3"}) == 3
    assert c._version_of({"revision": "B"}) == 2
    assert c._version_of({}) == -1


###
# ArenaClient._timestamp_of()
###


def test_timestamp_of(cfg):
    c = ArenaClient(cfg)
    now = datetime.now(timezone.utc)
    f = {"updatedAt": now.isoformat()}
    assert isinstance(c._timestamp_of(f), datetime)
    assert c._timestamp_of({}) is None


def test_timestamp_of_with_wrong_format(cfg):
    c = ArenaClient(cfg)
    now = datetime.now(timezone.utc)
    f = {"updatedAt": "invalid-timestamp-format"}
    assert c._timestamp_of(f) is None


###
# ArenaClient._ensure_json()
###


def test_ensure_json_accepts_json_dict(cfg):
    c = ArenaClient(cfg)
    resp = MagicMock()
    resp.headers = {"Content-Type": "application/json"}
    payload = {"ok": True, "n": 1}
    resp.json.return_value = payload
    assert c._ensure_json(resp) == payload


def test_ensure_json_accepts_json_list(cfg):
    c = ArenaClient(cfg)
    resp = MagicMock()
    resp.headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = [1, 2, 3]
    resp.json.return_value = payload
    assert c._ensure_json(resp) == payload  # returns list as-is


def test_ensure_json_non_json_content_type_raises(cfg):
    c = ArenaClient(cfg)
    resp = MagicMock()
    resp.headers = {"Content-Type": "text/html"}
    resp.text = "<html>oops</html>"
    resp.url = "https://example.test/endpoint"
    resp.status_code = 500
    with pytest.raises(ArenaError) as ei:
        c._ensure_json(resp)
    msg = str(ei.value)
    assert "Expected JSON" in msg
    assert "text/html" in msg
    assert "Status 500" in msg
    assert "https://example.test/endpoint" in msg


def test_ensure_json_missing_content_type_raises_unknown(cfg):
    c = ArenaClient(cfg)
    resp = MagicMock()
    resp.headers = {}  # no Content-Type header
    resp.text = "plain text body"
    resp.url = "https://example.test/no-ctype"
    resp.status_code = 200
    with pytest.raises(ArenaError) as ei:
        c._ensure_json(resp)
    msg = str(ei.value)
    assert "Expected JSON" in msg
    assert "unknown" in msg  # falls back to 'unknown' when header missing
    assert "https://example.test/no-ctype" in msg


def test_ensure_json_parse_error_raises_with_cause(cfg):
    c = ArenaClient(cfg)
    resp = MagicMock()
    resp.headers = {"Content-Type": "application/json"}
    resp.url = "https://example.test/bad-json"
    # Simulate JSON parsing failure
    resp.json.side_effect = ValueError("malformed")
    with pytest.raises(ArenaError) as ei:
        c._ensure_json(resp)
    msg = str(ei.value)
    assert "Failed to parse JSON from https://example.test/bad-json" in msg
    # Ensure the original exception is chained as the cause
    assert isinstance(ei.value.__cause__, ValueError)


###


###
# ArenaClient._try_json()
###
def test_try_json_non_json_content_type(cfg):
    c = ArenaClient(cfg)
    resp = MagicMock()
    resp.headers = {"Content-Type": "text/plain"}
    # json() shouldn't be called
    resp.json.side_effect = AssertionError("json() should not be called for non-json")
    assert c._try_json(resp) is None


def test_try_json_dict_pass_through(cfg):
    c = ArenaClient(cfg)
    resp = MagicMock()
    resp.headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {"ok": True, "value": 42}
    resp.json.return_value = payload
    assert c._try_json(resp) == payload


def test_try_json_list_wrapped(cfg):
    c = ArenaClient(cfg)
    resp = MagicMock()
    resp.headers = {"Content-Type": "application/json"}
    payload = [1, 2, 3]
    resp.json.return_value = payload
    assert c._try_json(resp) == {"data": payload}


def test_try_json_parse_error_returns_none(cfg):
    c = ArenaClient(cfg)
    resp = MagicMock()
    resp.headers = {"Content-Type": "application/json"}
    resp.json.side_effect = ValueError("malformed")
    assert c._try_json(resp) is None


###


def test_latest_files_picks_highest_version(cfg):
    c = ArenaClient(cfg)
    files = [
        {"filename": "a.hex", "version": 1, "updatedAt": "2024-01-01T00:00:00Z"},
        {"filename": "a.hex", "version": 2, "updatedAt": "2024-02-01T00:00:00Z"},
        {"filename": "b.hex", "version": 1, "updatedAt": "2024-01-01T00:00:00Z"},
    ]
    latest = c._latest_files(files)
    # Should keep only one per filename, highest version
    names = {f["filename"] for f in latest}
    assert names == {"a.hex", "b.hex"}
    a = next(f for f in latest if f["filename"] == "a.hex")
    assert a["version"] == 2


def test_get_latest_approved_revision_picks_effective(monkeypatch, cfg):
    c = ArenaClient(cfg)
    c._api_resolve_item_guid = MagicMock(return_value="ITEMGUID")

    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {
        "results": [
            {"guid": "R1", "revisionStatus": "EFFECTIVE", "number": "A"},
            {"guid": "R2", "revisionStatus": "WORKING", "number": "B"},
        ]
    }
    fake_resp.headers = {"Content-Type": "application/json"}
    c.session.get = MagicMock(return_value=fake_resp)

    rev = c.get_latest_approved_revision("510-1005")
    assert rev == "A"


def test_get_latest_approved_revision_raises_if_none(monkeypatch, cfg):
    c = ArenaClient(cfg)
    c._api_resolve_item_guid = MagicMock(return_value="ITEMGUID")

    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = {
        "results": [{"guid": "R1", "revisionStatus": "WORKING"}]
    }
    fake_resp.headers = {"Content-Type": "application/json"}
    c.session.get = MagicMock(return_value=fake_resp)

    with pytest.raises(ArenaError):
        c.get_latest_approved_revision("510-1005")


def test_upload_file_to_working_delegates(monkeypatch, tmp_path, cfg):
    # Create dummy file
    p = tmp_path / "dummy.txt"
    p.write_text("hello")

    c = ArenaClient(cfg)
    called = {}

    def fake_api_upload(**kw):
        called.update(kw)
        return {"ok": True, "fileGuid": "ABC"}

    monkeypatch.setattr(c, "_api_upload_or_update_file", fake_api_upload)

    result = c.upload_file_to_working("510-1005", p, title="dummy")
    assert result["ok"]
    assert called["title"] == "dummy"
    assert called["file_path"] == p


def make_fake_resp(content: bytes = b"data", status: int = 200):
    """Return a mock of requests.Response supporting context manager & iter_content."""
    r = MagicMock()
    r.__enter__.return_value = r
    r.__exit__.return_value = None
    r.status_code = status
    r.headers = {"Content-Type": "application/octet-stream"}
    r.iter_content = lambda size: [content]
    r.raise_for_status = MagicMock()
    return r


###
# ArenaClient.download_files()
###


def test_download_files_no_files(monkeypatch, cfg, tmpout):
    c = ArenaClient(cfg)
    # list_files() returns nothing
    c.list_files = MagicMock(return_value=[])

    downloaded = c.download_files("123-0001", out_dir=tmpout)
    assert downloaded == []  # nothing downloaded
    # Should not even attempt to GET anything
    c.session.get = MagicMock()
    c.session.get.assert_not_called()


def test_download_files_one_file(monkeypatch, cfg, tmpout):
    c = ArenaClient(cfg)
    # Return one fake file record
    c.list_files = MagicMock(
        return_value=[
            {
                "filename": "f1.txt",
                "downloadUrl": "https://api.example.com/f1",
                "haveContent": True,
            }
        ]
    )

    fake_resp = make_fake_resp(b"hello world\n")
    c.session.get = MagicMock(return_value=fake_resp)

    result = c.download_files("123-0001", out_dir=tmpout)

    # A single file should be downloaded
    assert len(result) == 1
    outpath = result[0]
    assert outpath.exists()
    assert outpath.read_bytes() == b"hello world\n"
    c.session.get.assert_called_once_with(
        "https://api.example.com/f1",
        stream=True,
        headers={"arena_session_id": ""},
    )


def test_download_files_multiple_files(monkeypatch, cfg, tmpout):
    c = ArenaClient(cfg)
    files = [
        {
            "filename": "a.txt",
            "downloadUrl": "https://api.example.com/a",
            "haveContent": True,
        },
        {
            "filename": "b.txt",
            "downloadUrl": "https://api.example.com/b",
            "haveContent": True,
        },
    ]
    c.list_files = MagicMock(return_value=files)

    # Simulate GET returning different content for each file
    def fake_get(url, *args, **kwargs):
        return make_fake_resp(content=(url.encode() + b"\n"))

    c.session.get = MagicMock(side_effect=fake_get)

    result = c.download_files("123-0001", out_dir=tmpout)

    # Expect both files written
    names = sorted(p.name for p in result)
    assert names == ["a.txt", "b.txt"]
    for p in result:
        assert p.exists()
        assert p.read_bytes().startswith(b"https://api.example.com/")
    # session.get called twice
    assert c.session.get.call_count == 2


###
# ArenaClient.list_files()
###
def test_list_files_no_files(monkeypatch, cfg):
    c = ArenaClient(cfg)
    # Mock dependencies
    c._api_resolve_revision_guid = MagicMock(return_value="REVGUID")
    c._api_list_files_by_item_guid = MagicMock(return_value=[])
    c._latest_files = MagicMock(return_value=[])

    result = c.list_files("510-0001")
    assert result == []
    c._api_resolve_revision_guid.assert_called_once_with("510-0001", "EFFECTIVE")
    c._api_list_files_by_item_guid.assert_called_once_with("REVGUID")


def test_list_files_one_file(monkeypatch, cfg):
    c = ArenaClient(cfg)
    c._api_resolve_revision_guid = MagicMock(return_value="REVGUID")
    fake_files = [
        {
            "filename": "fw.hex",
            "fileGuid": "XYZ",
            "edition": "A1B2",
            "size": 1234,
            "updatedAt": "2025-11-05T12:00:00Z",
        }
    ]
    c._api_list_files_by_item_guid = MagicMock(return_value=fake_files)
    c._latest_files = MagicMock(side_effect=lambda x: x)

    result = c.list_files("510-0001", revision="WORKING")
    assert len(result) == 1
    f = result[0]
    assert f["filename"] == "fw.hex"
    assert f["edition"] == "A1B2"
    c._api_resolve_revision_guid.assert_called_once_with("510-0001", "WORKING")


def test_list_files_multiple_files_dedup(monkeypatch, cfg):
    c = ArenaClient(cfg)
    c._api_resolve_revision_guid = MagicMock(return_value="REVGUID")

    # Same filename, different versions
    fake_files = [
        {"filename": "app.hex", "version": 1},
        {"filename": "app.hex", "version": 2},
        {"filename": "boot.hex", "version": 1},
    ]
    c._api_list_files_by_item_guid = MagicMock(return_value=fake_files)

    # Use the real _latest_files logic
    result = c.list_files("510-0001")

    names = {f["filename"] for f in result}
    assert names == {"app.hex", "boot.hex"}
    app = next(f for f in result if f["filename"] == "app.hex")
    assert app["version"] == 2


###
# ArenaClient.get_latest_approved_revision()
###


def test_get_latest_approved_revision_happy_path(monkeypatch, cfg):
    """Should return the number/name of the effective revision."""
    c = ArenaClient(cfg)

    # Mock the lower-level call to avoid HTTP
    c._api_get_latest_approved = MagicMock(return_value="B2")

    result = c.get_latest_approved_revision("510-0001")
    assert result == "B2"
    c._api_get_latest_approved.assert_called_once_with("510-0001")


def test_get_latest_approved_revision_no_effective(monkeypatch, cfg):
    """Should raise ArenaError when no approved revisions exist."""
    c = ArenaClient(cfg)

    # Simulate internal method raising
    def raise_err(item_number):
        raise ArenaError("No approved/released revisions for item 510-0001")

    c._api_get_latest_approved = MagicMock(side_effect=raise_err)

    with pytest.raises(ArenaError, match="No approved/released"):
        c.get_latest_approved_revision("510-0001")


def test_api_get_latest_approved_selects_current(monkeypatch, cfg):
    """Test the internal _api_get_latest_approved logic with mocked responses."""
    c = ArenaClient(cfg)
    c._api_resolve_item_guid = MagicMock(return_value="ITEMGUID")

    # Fake JSON with one effective (no supersededDateTime)
    payload = {
        "results": [
            {"guid": "R1", "revisionStatus": "EFFECTIVE", "number": "A"},
            {"guid": "R2", "revisionStatus": "WORKING", "number": "B"},
        ]
    }

    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = payload
    fake_resp.headers = {"Content-Type": "application/json"}
    c.session.get = MagicMock(return_value=fake_resp)

    rev = c._api_get_latest_approved("510-0001")
    assert rev == "A"
    c._api_resolve_item_guid.assert_called_once_with("510-0001")
    c.session.get.assert_called_once()
    assert isinstance(rev, str)


def test_api_get_latest_approved_prefers_unsuperseded(monkeypatch, cfg):
    """If multiple EFFECTIVE revisions, prefer the one without supersededDateTime."""
    c = ArenaClient(cfg)
    c._api_resolve_item_guid = MagicMock(return_value="ITEMGUID")

    payload = {
        "results": [
            {
                "guid": "R1",
                "revisionStatus": "EFFECTIVE",
                "number": "A",
                "supersededDateTime": "2024-01-01T00:00:00Z",
            },
            {"guid": "R2", "revisionStatus": "EFFECTIVE", "number": "B"},
        ]
    }

    fake_resp = MagicMock()
    fake_resp.status_code = 200
    fake_resp.json.return_value = payload
    fake_resp.headers = {"Content-Type": "application/json"}
    c.session.get = MagicMock(return_value=fake_resp)

    rev = c._api_get_latest_approved("510-0001")
    assert rev == "B"  # prefers unsuperseded


###
# ArenaClient.download_files_recursive()
###


def test_download_files_recursive_no_children(monkeypatch, cfg, tmpout):
    c = ArenaClient(cfg)

    # 1) Root files only
    def fake_download_files(item_number, revision=None, out_dir=Path(".")):
        p = out_dir / "root.bin"
        out_dir.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"root")
        return [p]

    c.download_files = MagicMock(side_effect=fake_download_files)
    c.get_bom = MagicMock(return_value=[])

    result = c.download_files_recursive("510-ROOT", out_dir=tmpout)

    # Only the root file should be present
    assert len(result) == 1
    assert result[0].exists()
    assert result[0].read_bytes() == b"root"
    # Root download called once
    c.download_files.assert_called_once()
    # get_bom called with recursive=False and default max_depth=None
    c.get_bom.assert_called_once_with("510-ROOT", None, recursive=False, max_depth=None)


def test_download_files_recursive_multiple_children_dedup_and_skip_self(
    monkeypatch, cfg, tmpout
):
    c = ArenaClient(cfg)

    # Fake BOM with duplicates and a self-reference (should be skipped)
    bom_rows = [
        {"itemNumber": "510-ROOT"},  # self, should be skipped
        {"itemNumber": "510-CH-A"},
        {"itemNumber": "510-CH-A"},  # duplicate, should be deduped
        {"itemNumber": "510-CH-B"},
    ]

    def fake_get_bom(item_number, revision=None, *, recursive=False, max_depth=None):
        assert recursive is False
        assert max_depth is None
        if item_number == "510-ROOT":
            return bom_rows
        return []

    c.get_bom = MagicMock(side_effect=fake_get_bom)

    # Download behavior per item
    def fake_download(item_number, revision=None, out_dir=Path(".")):
        out_dir.mkdir(parents=True, exist_ok=True)
        if item_number == "510-ROOT":
            p = out_dir / "root.txt"
            p.write_text("root")
            return [p]
        elif item_number == "510-CH-A":
            p = out_dir / "a.txt"
            p.write_text("A")
            return [p]
        elif item_number == "510-CH-B":
            p = out_dir / "b.txt"
            p.write_text("B")
            return [p]
        else:
            raise AssertionError(f"Unexpected item_number: {item_number}")

    c.download_files = MagicMock(side_effect=fake_download)

    result = c.download_files_recursive("510-ROOT", out_dir=tmpout)

    # Expect 3 files: root + two children
    assert len(result) == 3
    # Paths should be: <tmpout>/root.txt, <tmpout>/510-CH-A/a.txt, <tmpout>/510-CH-B/b.txt
    expected = {
        (tmpout / "root.txt").resolve(),
        (tmpout / "510-CH-A" / "a.txt").resolve(),
        (tmpout / "510-CH-B" / "b.txt").resolve(),
    }
    assert {p.resolve() for p in result} == expected

    # Child directories created
    assert (tmpout / "510-CH-A").is_dir()
    assert (tmpout / "510-CH-B").is_dir()

    # Called once for root + once per unique child (A, B) = 3
    assert c.download_files.call_count == 3
    # Ensure get_bom was queried for root and each child
    calls = c.get_bom.call_args_list
    assert len(calls) == 3
    assert calls[0].args == ("510-ROOT", None)
    assert calls[0].kwargs == {"recursive": False, "max_depth": None}
    assert calls[1].args == ("510-CH-A", None)
    assert calls[1].kwargs == {"recursive": False, "max_depth": None}
    assert calls[2].args == ("510-CH-B", None)
    assert calls[2].kwargs == {"recursive": False, "max_depth": None}


def test_download_files_recursive_respects_max_depth(monkeypatch, cfg, tmpout):
    c = ArenaClient(cfg)

    # Keep it simple—no children; we only verify the call signature
    c.get_bom = MagicMock(return_value=[])
    c.download_files = MagicMock(
        side_effect=lambda item_number, revision=None, out_dir=Path("."): [
            out_dir / "x.bin"
        ]
    )

    result = c.download_files_recursive("510-ROOT", out_dir=tmpout, max_depth=1)

    assert len(result) == 1
    # Verify propagation of max_depth to get_bom
    c.get_bom.assert_called_once_with("510-ROOT", None, recursive=False, max_depth=None)


def test_download_files_recursive_nested_directories(monkeypatch, cfg, tmpout):
    c = ArenaClient(cfg)

    bom_map = {
        "510-ROOT": [
            {"itemNumber": "510-CH-A"},
            {"itemNumber": "510-CH-B"},
        ],
        "510-CH-A": [{"itemNumber": "510-CH-A1"}],
        "510-CH-B": [],
        "510-CH-A1": [],
    }

    def fake_get_bom(item_number, revision=None, *, recursive=False, max_depth=None):
        assert recursive is False
        assert max_depth is None
        return bom_map[item_number]

    c.get_bom = MagicMock(side_effect=fake_get_bom)

    def fake_download(item_number, revision=None, out_dir=Path(".")):
        out_dir.mkdir(parents=True, exist_ok=True)
        p = out_dir / f"{item_number.replace('-', '_')}.txt"
        p.write_text(item_number)
        return [p]

    c.download_files = MagicMock(side_effect=fake_download)

    result = c.download_files_recursive("510-ROOT", out_dir=tmpout)

    expected_paths = {
        (tmpout / "510_ROOT.txt").resolve(),
        (tmpout / "510-CH-A" / "510_CH_A.txt").resolve(),
        (tmpout / "510-CH-A" / "510-CH-A1" / "510_CH_A1.txt").resolve(),
        (tmpout / "510-CH-B" / "510_CH_B.txt").resolve(),
    }

    assert {p.resolve() for p in result} == expected_paths

    # Ensure directory hierarchy exists
    assert (tmpout / "510-CH-A" / "510-CH-A1").is_dir()
    assert (tmpout / "510-CH-B").is_dir()

    # download_files called once per unique node in the tree
    assert c.download_files.call_count == 4


###
# ArenaClient.get_bom()
###


def test_get_bom_non_recursive(monkeypatch, cfg):
    c = ArenaClient(cfg)

    # Root BOM has two lines
    root_rows = [
        {
            "guid": "L1",
            "lineNumber": 1,
            "itemNumber": "510-CH-A",
            "itemName": "Child A",
            "itemRevision": "A",
            "itemRevisionStatus": "EFFECTIVE",
        },
        {
            "guid": "L2",
            "lineNumber": 2,
            "itemNumber": "510-CH-B",
            "itemName": "Child B",
            "itemRevision": "A",
            "itemRevisionStatus": "EFFECTIVE",
        },
    ]

    # Only the root is fetched when recursive=False
    c._fetch_bom_normalized = MagicMock(return_value=root_rows)

    out = c.get_bom("510-ROOT", revision="EFFECTIVE", recursive=False)
    # Should equal root_rows plus level & parentNumber annotations (level=0)
    assert len(out) == 2
    assert all(r["level"] == 0 for r in out)
    assert all(r["parentNumber"] == "510-ROOT" for r in out)
    # Ensure we fetched the correct selector
    c._fetch_bom_normalized.assert_called_once_with("510-ROOT", "EFFECTIVE")


def test_get_bom_recursive_with_max_depth(monkeypatch, cfg):
    c = ArenaClient(cfg)

    bom_map = {
        ("510-ROOT", "WORKING"): [
            {"guid": "L1", "lineNumber": 1, "itemNumber": "510-CH-A"},
            {"guid": "L2", "lineNumber": 2, "itemNumber": "510-CH-B"},
        ],
        ("510-CH-A", "WORKING"): [
            {"guid": "L3", "lineNumber": 1, "itemNumber": "510-CH-C"},
        ],
        ("510-CH-B", "WORKING"): [],
        ("510-CH-C", "WORKING"): [],
    }

    def fake_fetch(item_number, selector):
        return bom_map.get((item_number, selector), [])

    c._fetch_bom_normalized = MagicMock(side_effect=fake_fetch)

    out = c.get_bom("510-ROOT", revision="WORKING", recursive=True, max_depth=1)

    # Root's BOM lines (A,B) are at level 0
    assert any(
        r["itemNumber"] == "510-CH-A"
        and r["level"] == 0
        and r["parentNumber"] == "510-ROOT"
        for r in out
    )
    assert any(
        r["itemNumber"] == "510-CH-B"
        and r["level"] == 0
        and r["parentNumber"] == "510-ROOT"
        for r in out
    )

    # One level of recursion: A's BOM lines (C) show up at level 1, and we stop there
    assert any(
        r["itemNumber"] == "510-CH-C"
        and r["level"] == 1
        and r["parentNumber"] == "510-CH-A"
        for r in out
    )
    assert not any(r["level"] >= 2 for r in out)

    # We never fetch CH-C because at level 1 we hit the max_depth early-exit
    expected_calls = {
        ("510-ROOT", "WORKING"),
        ("510-CH-A", "WORKING"),
        ("510-CH-B", "WORKING"),
    }
    got_calls = {
        (args[0][0], args[0][1]) for args in c._fetch_bom_normalized.call_args_list
    }
    assert got_calls == expected_calls


def test_get_bom_recursive_cycle_avoidance(monkeypatch, cfg):
    c = ArenaClient(cfg)

    bom_map = {
        ("510-ROOT", "EFFECTIVE"): [
            {"guid": "L1", "lineNumber": 1, "itemNumber": "510-CH-A"},
        ],
        ("510-CH-A", "EFFECTIVE"): [
            {"guid": "L2", "lineNumber": 1, "itemNumber": "510-ROOT"},  # cycle back
        ],
    }

    def fake_fetch(item_number, selector):
        return bom_map.get((item_number, selector), [])

    c._fetch_bom_normalized = MagicMock(side_effect=fake_fetch)

    out = c.get_bom("510-ROOT", revision="EFFECTIVE", recursive=True)

    # Two rows: A at level 0 (parent ROOT), and ROOT at level 1 (parent A)
    assert len(out) == 2
    assert any(
        r["itemNumber"] == "510-CH-A"
        and r["level"] == 0
        and r["parentNumber"] == "510-ROOT"
        for r in out
    )
    assert any(
        r["itemNumber"] == "510-ROOT"
        and r["level"] == 1
        and r["parentNumber"] == "510-CH-A"
        for r in out
    )

    # Only two fetches due to cycle short-circuit
    calls = [tuple(args[0]) for args in c._fetch_bom_normalized.call_args_list]
    assert calls == [
        ("510-ROOT", "EFFECTIVE"),
        ("510-CH-A", "EFFECTIVE"),
    ]


def test_get_bom_selector_defaults_to_effective(monkeypatch, cfg):
    c = ArenaClient(cfg)

    seen = []

    def fake_fetch(item_number, selector):
        seen.append((item_number, selector))
        return []

    c._fetch_bom_normalized = MagicMock(side_effect=fake_fetch)

    # No revision passed -> defaults to EFFECTIVE
    out = c.get_bom("510-ROOT", recursive=False)
    assert out == []
    c._fetch_bom_normalized.assert_called_once_with("510-ROOT", "EFFECTIVE")
    assert seen == [("510-ROOT", "EFFECTIVE")]
