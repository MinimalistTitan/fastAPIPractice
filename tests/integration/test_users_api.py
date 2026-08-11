from httpx import AsyncClient


async def test_user_registration_and_lookup(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/users",
        json={"email": "ada@example.com", "display_name": "Ada Lovelace"},
        headers={"x-request-id": "test-request-id"},
    )

    assert create_response.status_code == 201
    assert create_response.headers["x-request-id"] == "test-request-id"
    created = create_response.json()
    assert created["email"] == "ada@example.com"
    assert created["display_name"] == "Ada Lovelace"

    get_response = await client.get(f"/api/v1/users/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json() == created


async def test_duplicate_email_returns_problem_details(client: AsyncClient) -> None:
    payload = {"email": "ada@example.com", "display_name": "Ada Lovelace"}
    assert (await client.post("/api/v1/users", json=payload)).status_code == 201

    response = await client.post("/api/v1/users", json=payload)

    assert response.status_code == 409
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["type"] == "urn:problem:email_already_registered"


async def test_operational_endpoints(client: AsyncClient) -> None:
    assert (await client.get("/health/live")).json() == {"status": "ok"}
    assert (await client.get("/health/ready")).json() == {"status": "ok"}

    metrics_response = await client.get("/metrics")
    assert metrics_response.status_code == 200
    assert "http_requests_total" in metrics_response.text
