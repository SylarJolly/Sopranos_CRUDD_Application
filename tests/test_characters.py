import pytest

# ------------------------------------HAPPY PATHS-------------------------------------------


# 1. TEST FOR EMPTY CHARACTERS
def test_list_characters_empty(client):

    # Act
    response = client.get("/characters/")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


# 2. TEST FOR GETTING A SEEDED CHARACTER
def test_get_seeded_character(client, seeded_db):
    # Arrange: seeded_db has already loaded the 12 characters (Tony Soprano is first)
    expected = {"id": 1, **seeded_db[0]}

    # Act
    response = client.get("/characters/1")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


# 3. TEST FOR CREATING A CHARACTER
def test_create_character(client, sample_character):

    # Act
    response = client.post("/characters/", json=sample_character)

    # Assert
    assert response.status_code == 201

    character = response.json()

    assert isinstance(character["id"], int)
    assert character["id"] > 0
    assert {
        key: value for key, value in character.items() if key != "id"
    } == sample_character


# 4. TEST FOR CHECKING IF A CREATED CHARACTER WAS SAVED
def test_create_character_is_saved(client, created_character):

    # Act
    character_id = created_character["id"]
    response = client.get(f"/characters/{character_id}")

    # Assert
    assert response.status_code == 200
    assert response.json() == created_character


# 5. TEST FOR UPDATING A CHARACTER
def test_update_character(client, created_character, updated_character):

    # Arrange
    character_id = created_character["id"]
    expected = {"id": character_id, **updated_character}

    # Act
    response = client.put(f"/characters/{character_id}", json=updated_character)

    # Assert
    assert response.status_code == 200
    assert response.json() == expected

    get_response = client.get(f"/characters/{character_id}")

    assert get_response.status_code == 200
    assert get_response.json() == expected


# 6. TEST FOR DELETING A CHARACTER
def test_delete_character(client, created_character):

    # Arrange
    character_id = created_character["id"]

    # Act
    response = client.delete(f"/characters/{character_id}")

    # Assert
    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(f"/characters/{character_id}")

    assert get_response.status_code == 404


# ------------------------------------UNHAPPY PATHS-------------------------------------------


# 7. TEST FOR CHARACTER NOT FOUND
@pytest.mark.parametrize(
    "method, use_body",
    [
        ("get", False),
        ("put", True),
        ("delete", False),
    ],
    ids=["get", "put", "delete"],
)
def test_character_not_found(client, sample_character, method, use_body):
    kwargs = {"json": sample_character} if use_body else {}
    response = client.request(method, "/characters/9999", **kwargs)
    assert response.status_code == 404
    assert response.json() == {"detail": "Character not found"}


# 8. TEST FOR NON-INTEGER CHARACTER ID
def test_non_integer_id(client):

    # Act
    response = client.get("/characters/tony-soprano")

    # Assert
    assert response.status_code == 422


# 9. TEST FOR CREATING A DUPLICATE CHARACTER
def test_create_duplicate(client, created_character, sample_character):

    # Act
    response = client.post("/characters/", json=sample_character)

    # Assert
    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "A character with that name and actor already exists"
    )


# 10. TEST FOR DUPLICATE CHARACTER IGNORING CASE
def test_create_duplicate_ignores_case(client, created_character, sample_character):

    # Arrange
    duplicate_character = sample_character.copy()
    duplicate_character["name"] = duplicate_character["name"].upper()
    duplicate_character["actor"] = duplicate_character["actor"].lower()

    # Act
    response = client.post("/characters/", json=duplicate_character)

    # Assert
    assert response.status_code == 409


# 11. TEST FOR UPDATING A CHARACTER INTO A DUPLICATE
def test_update_into_duplicate(client, seeded_db):

    # Arrange
    duplicate_character = seeded_db[0].copy()

    # Act
    response = client.put("/characters/2", json=duplicate_character)

    # Assert
    assert response.status_code == 409

    # Check that character 2 was not changed
    get_response = client.get("/characters/2")

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Carmela Soprano"
    assert get_response.json()["actor"] == "Edie Falco"


# 12. TEST FOR UPDATING A CHARACTER WITHOUT CREATING A DUPLICATE
def test_update_same_name_and_actor_is_allowed(client, created_character):

    # Arrange
    updated_character = created_character.copy()
    updated_character["role"] = "Soldier"

    # Act
    character_id = created_character["id"]
    response = client.put(f"/characters/{character_id}", json=updated_character)

    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == created_character["name"]
    assert response.json()["actor"] == created_character["actor"]
    assert response.json()["role"] == "Soldier"


# 13. TEST FOR CREATING A CHARACTER WITH A MISSING FIELD
@pytest.mark.parametrize(
    "missing_field",
    ["name", "actor", "role", "status", "first_season", "last_season"],
    ids=["name", "actor", "role", "status", "first-season", "last-season"],
)
def test_create_missing_field(client, sample_character, missing_field):

    # Arrange
    character = sample_character.copy()
    character.pop(missing_field)

    # Act
    response = client.post("/characters/", json=character)

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", missing_field]


# 14. TEST FOR CREATING A CHARACTER WITH AN INVALID VALUE
@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("first_season", 7),
        ("last_season", 0),
        ("last_season", "season-four"),
        ("name", ""),
    ],
    ids=["season-too-high", "season-too-low", "season-not-int", "empty-name"],
)
def test_create_invalid_value(client, sample_character, field, invalid_value):

    # Arrange
    character = sample_character.copy()
    character[field] = invalid_value

    # Act
    response = client.post("/characters/", json=character)

    # Assert
    assert response.status_code == 422


# 15. TEST FOR PAGINATION COUNTS
@pytest.mark.parametrize(
    "skip, limit, expected_count",
    [
        (0, 3, 3),  # First 3 characters
        (3, 3, 3),  # Skip 3, return next 3
        (0, 0, 0),  # Limit of 0
        (20, 3, 0),  # Skip past the end of the data
    ],
    ids=["first-three", "next-three", "zero-limit", "skip-past-end"],
)
def test_pagination_counts(client, seeded_db, skip, limit, expected_count):

    # Act
    response = client.get("/characters/", params={"skip": skip, "limit": limit})

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == expected_count


# 16. TEST FOR INVALID PAGINATION VALUES
@pytest.mark.parametrize(
    "params",
    [
        {"skip": -1},  # Skip cannot be negative
        {"limit": 101},  # Limit cannot be above 100
    ],
    ids=["negative-skip", "limit-too-high"],
)
def test_pagination_invalid(client, seeded_db, params):

    # Act
    response = client.get("/characters/", params=params)

    # Assert
    assert response.status_code == 422


# 17. TEST FOR FILTERING CHARACTERS BY NAME
@pytest.mark.parametrize(
    "name, expected_names",
    [
        ("Tony Soprano", ["Tony Soprano"]),
        (
            "soprano",
            [
                "Tony Soprano",
                "Carmela Soprano",
                "Junior Soprano",
                "Livia Soprano",
                "Meadow Soprano",
                "A.J. Soprano",
            ],
        ),
        ("Not a Character", []),
    ],
    ids=["full-name", "partial-lowercase", "no-results"],
)
def test_filter_by_name(client, seeded_db, name, expected_names):

    # Act
    response = client.get("/characters/", params={"name": name})

    # Assert
    assert response.status_code == 200

    actual_names = [character["name"] for character in response.json()]
    assert actual_names == expected_names
