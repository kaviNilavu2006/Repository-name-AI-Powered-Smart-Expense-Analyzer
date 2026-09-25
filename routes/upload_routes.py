"""
Upload Routes
--------------
POST /api/upload/receipt

Standalone receipt upload endpoint (also used inline by expense
creation/update). Useful for uploading a receipt before deciding
which expense to attach it to.
"""

from flask import Blueprint, request

from services.s3_service import s3_service
from utils.validators import is_allowed_file, is_file_size_allowed
from utils.helpers import login_required, get_current_user_id, json_success, json_error

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")


@upload_bp.route("/receipt", methods=["POST"])
@login_required
def upload_receipt():
    user_id = get_current_user_id()
    uploaded_file = request.files.get("receipt")

    if not uploaded_file or not uploaded_file.filename:
        return json_error("No receipt file provided.", 400)

    if not is_allowed_file(uploaded_file.filename):
        return json_error("Receipt must be a JPG, JPEG, PNG, or PDF file.", 400)

    uploaded_file.seek(0, 2)
    size = uploaded_file.tell()
    uploaded_file.seek(0)
    if not is_file_size_allowed(size):
        return json_error("Receipt file size must not exceed 5 MB.", 400)

    try:
        result = s3_service.upload_receipt(uploaded_file, user_id)
    except RuntimeError as exc:
        return json_error(str(exc), 502)

    return json_success(data=result, message="Receipt uploaded successfully.")
