import json

from app.storage.settings import JsonStorage


def test_settings_and_history_persist_in_application_directory(tmp_path):
    storage = JsonStorage(tmp_path)
    settings = storage.load_settings()
    settings["theme"] = "dark"
    storage.save_settings(settings)
    history = [{"expression": "1+1", "result": "2"}]
    storage.save_history(history)

    assert storage.load_settings()["theme"] == "dark"
    assert storage.load_history() == history


def test_history_is_capped_at_one_hundred_entries(tmp_path):
    storage = JsonStorage(tmp_path)
    entries = [{"expression": str(index)} for index in range(105)]
    storage.save_history(entries)

    assert len(storage.load_history()) == 100
    assert storage.load_history()[0]["expression"] == "5"
