import pytest
from memobase_server.auth.token import (
    generate_secret_key,
    parse_project_id,
    set_project_secret,
    check_project_secret,
)


@pytest.mark.asyncio
async def test_auth_token(db_env):
    project_id = "mb-xxxxxx"
    key = generate_secret_key(project_id)
    print(key)
    p = parse_project_id(key)
    assert p.ok()
    assert p.data() == project_id

    await set_project_secret(project_id, key)
    p = await check_project_secret(project_id, key)
    assert p.ok()
    assert p.data()
