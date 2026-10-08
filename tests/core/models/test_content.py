import os

from evp.core.models.content import LocalMedia


def test_url_resolves_relative_path_to_absolute_file_uri(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    relative_path = os.path.join("subdir", "sample.jpg")
    absolute_file = tmp_path / relative_path
    absolute_file.parent.mkdir(parents=True)
    absolute_file.write_bytes(b"fake-image-bytes")

    media = LocalMedia(path=relative_path)

    assert media.url == f"file://{tmp_path / relative_path}"
