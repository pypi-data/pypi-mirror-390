from datasette.app import Datasette
import pathlib
import pytest
import pytest_asyncio
import sqlite_utils


@pytest_asyncio.fixture
async def ds(tmpdir):
    one = str(tmpdir / "one.db")
    two = str(tmpdir / "two.db")
    sqlite_utils.Database(one).vacuum()
    sqlite_utils.Database(two).vacuum()
    ds = Datasette(
        files=[one, two], config={"permissions": {"remove-database": {"id": "root"}}}
    )
    ds._db_paths = [pathlib.Path(one), pathlib.Path(two)]
    await ds.invoke_startup()
    return ds


async def dbs(ds) -> set:
    databases = (await ds.client.get("/-/databases.json")).json()
    return {db["name"] for db in databases}


@pytest.mark.asyncio
@pytest.mark.parametrize("delete_configured", (True, False))
@pytest.mark.parametrize("enable_wal", (True, False))
async def test_remove_database(ds, delete_configured, enable_wal):
    if delete_configured:
        ds.config["plugins"] = {"datasette-remove-database": {"delete": True}}
    if enable_wal:
        one_path = ds._db_paths[0]
        sqlite_utils.Database(one_path).enable_wal()
    # Should start with two databases
    assert await dbs(ds) == {"one", "two"}
    # Remove one
    cookies = {"ds_actor": ds.client.actor_cookie({"id": "root"})}
    response = await ds.client.get("/-/remove-database/one", cookies=cookies)
    assert response.status_code == 200
    assert "<h1>Remove database: one</h1>" in response.text
    # POST to remove it
    csrftoken = response.cookies["ds_csrftoken"]
    cookies["ds_csrftoken"] = csrftoken
    response = await ds.client.post(
        "/-/remove-database/one", cookies=cookies, data={"csrftoken": csrftoken}
    )
    assert response.status_code == 302
    assert await dbs(ds) == {"two"}
    if delete_configured:
        # Should have been deleted
        for path in ds._db_paths:
            if path.name == "one.db":
                assert not path.exists()
                # Check for .db-shm and .db-wal too
                assert not path.with_suffix(".db-shm").exists()
                assert not path.with_suffix(".db-wal").exists()
            else:
                assert path.exists()
    else:
        # Should not have been deleted
        for path in ds._db_paths:
            assert path.exists()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,actor,delete_enabled,expected_status,expected_fragment,not_fragment",
    (
        # Permission denied for anonymous user
        ("/-/remove-database/one", None, False, 403, "Permission denied", ""),
        # root user gets page
        (
            "/-/remove-database/one",
            "root",
            False,
            200,
            ">Remove database: one<",
            "The following files will be deleted",
        ),
        # if delete is on they get that extra message:
        (
            "/-/remove-database/one",
            "root",
            True,
            200,
            "The following files will be deleted",
            "",
        ),
        # anonymous user cannot see Remove database link
        ("/one", None, False, 200, "one", ">Remove database"),
        # root user can see Remove database link
        (
            "/one",
            "root",
            False,
            200,
            ">Remove database",
            "and delete the database file",
        ),
        # root user sees "and delete ..." if delete is turned on
        ("/one", "root", True, 200, "and delete the database file", ""),
    ),
)
async def test_remove_database_permissions(
    ds, path, actor, delete_enabled, expected_status, expected_fragment, not_fragment
):
    # Check permissions and visibility of menu items
    ds.config["plugins"] = {"datasette-remove-database": {"delete": delete_enabled}}
    cookies = {}
    if actor:
        cookies["ds_actor"] = ds.client.actor_cookie({"id": actor})
    response = await ds.client.get(path, cookies=cookies)
    assert response.status_code == expected_status
    assert expected_fragment in response.text
    if not_fragment:
        assert not_fragment not in response.text
