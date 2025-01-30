import pytest
from memobase_server.auth.token import (
    generate_project_id,
    generate_secret_key,
    parse_project_id,
    set_project_secret,
    check_project_secret,
)
from memobase_server.controllers import project


@pytest.mark.asyncio
async def test_auth_token(db_env):
    project_id = generate_project_id()
    key = generate_secret_key(project_id)
    print(key)
    p = parse_project_id(key)
    assert p.ok()
    assert p.data() == project_id

    p = await project.create_project(project_id, key)
    assert p.ok(), p.msg()

    p = await check_project_secret(project_id, key)
    assert p.ok(), p.msg()
    assert p.data()

    key2 = generate_secret_key(project_id)
    assert key2 != key
    print(key2)
    p = await set_project_secret(project_id, key2)
    assert p.ok(), p.msg()

    p = await check_project_secret(project_id, key2)
    assert p.ok(), p.msg()
    assert p.data()

    p = await check_project_secret(project_id, key)
    assert p.ok(), p.msg()
    assert not p.data()
