from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
PDF_EXTENSIONS = {"pdf"}
IMAGE_PURPOSES = {"avatar", "project_cover", "certificate_image"}
PDF_PURPOSES = {"resume"}


class UploadError(ValueError):
    pass


def extension_for(filename: str) -> str:
    safe_name = secure_filename(filename or "")
    if "." not in safe_name:
        return ""
    return safe_name.rsplit(".", 1)[1].lower()


def max_size_for(purpose: str) -> int:
    if purpose in PDF_PURPOSES:
        return current_app.config["MAX_PDF_UPLOAD_MB"] * 1024 * 1024
    return current_app.config["MAX_IMAGE_UPLOAD_MB"] * 1024 * 1024


def allowed_extensions_for(purpose: str) -> set[str]:
    if purpose in PDF_PURPOSES:
        return PDF_EXTENSIONS
    if purpose in IMAGE_PURPOSES:
        return IMAGE_EXTENSIONS
    raise UploadError("未知的上传用途。")


def save_upload(file: FileStorage, purpose: str) -> dict:
    ext = extension_for(file.filename)
    if ext not in allowed_extensions_for(purpose):
        raise UploadError("不支持的文件类型。")

    file.stream.seek(0, 2)
    size = file.stream.tell()
    file.stream.seek(0)

    if size > max_size_for(purpose):
        raise UploadError("文件大小超过限制。")

    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_filename = f"{uuid4().hex}.{ext}"
    saved_path = upload_dir / saved_filename
    file.save(saved_path)

    return {
        "original_filename": file.filename,
        "saved_filename": saved_filename,
        "file_path": f"uploads/{saved_filename}",
        "mime_type": file.content_type or "application/octet-stream",
        "file_size": size,
        "upload_purpose": purpose,
    }
