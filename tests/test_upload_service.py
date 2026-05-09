from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage

from app.services.upload_service import UploadError, save_upload


def make_file(filename, content_type, content=b"file-content"):
    return FileStorage(stream=BytesIO(content), filename=filename, content_type=content_type)


def test_save_upload_accepts_image(app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    with app.app_context():
        result = save_upload(make_file("avatar.png", "image/png"), "avatar")

    assert result["original_filename"] == "avatar.png"
    assert result["saved_filename"].endswith(".png")
    assert result["file_path"].startswith("uploads/")
    assert (tmp_path / result["saved_filename"]).exists()


def test_save_upload_rejects_disallowed_extension(app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    with app.app_context():
        with pytest.raises(UploadError, match="不支持的文件类型"):
            save_upload(make_file("shell.exe", "application/octet-stream"), "avatar")


def test_save_upload_rejects_mismatched_mime_type(app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)

    with app.app_context():
        with pytest.raises(UploadError, match="MIME 类型不匹配"):
            save_upload(make_file("avatar.png", "application/pdf"), "avatar")


def test_save_upload_rejects_large_pdf(app, tmp_path):
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    app.config["MAX_PDF_UPLOAD_MB"] = 1

    with app.app_context():
        with pytest.raises(UploadError, match="文件大小超过限制"):
            save_upload(make_file("resume.pdf", "application/pdf", b"x" * (1024 * 1024 + 1)), "resume")
