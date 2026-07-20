from fastapi.testclient import TestClient

from fastapi.testclient import TestClient


def lookup(client: TestClient, word: str, language: str):
    return client.post(
        "/dictionary/lookup",
        json={
            "word": word,
            "language": language,
        },
    )
def test_dictionary_lookup_success(client: TestClient):
    response = client.post(
        "/dictionary/lookup",
        json={
            "word": "こんにちは",
            "language": "ja"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["word"] == "こんにちは"
    assert data["language"] == "ja"

    assert "readings" in data
    assert "senses" in data

    assert len(data["readings"]) > 0
    assert len(data["senses"]) > 0
def test_dictionary_lookup_invalid_request(client):
    response = client.post(
        "/dictionary/lookup",
        json={
            "word": "",
            "language": "ja",
        },
    )

    assert response.status_code == 422    
def test_dictionary_lookup_missing_word(client):
    response = client.post(
        "/dictionary/lookup",
        json={
            "language": "ja"
        },
    )

    assert response.status_code == 422
def test_dictionary_lookup_arbitrary_language(client):
    response = client.post(
        "/dictionary/lookup",
        json={
            "word": "hello",
            "language": "xyz",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["word"] == "hello"
    assert data["language"] == "xyz"
def test_dictionary_lookup_english(client):
    response = client.post(
        "/dictionary/lookup",
        json={
            "word": "computer",
            "language": "en",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["word"] == "computer"
    assert data["language"] == "en"

    assert "readings" in data
    assert "senses" in data        