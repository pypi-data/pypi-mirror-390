import pytest


def test_create_app(mocker, dokku):
    mocker.patch("dokku_wrapper.services.apps.run_command", return_value="App created")
    result = dokku.apps.create("myapp")
    assert result["name"] == "myapp"


def test_create_app_already_exists(mocker, dokku):
    mocker.patch(
        "dokku_wrapper.services.apps.run_command",
        side_effect=Exception("App already exists")
    )
    with pytest.raises(Exception):
        dokku.apps.create("myapp")


def test_destroy_app(mocker, dokku):
    mocker.patch(
        "dokku_wrapper.services.apps.run_command",
        return_value="App Destroyed")
    result = dokku.apps.destroy("myapp")
    assert result == "App Destroyed"