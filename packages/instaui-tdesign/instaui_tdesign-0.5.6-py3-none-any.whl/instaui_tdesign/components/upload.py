from __future__ import annotations
import typing
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Upload(BaseElement):
    def __init__(
        self,
        **kwargs: Unpack[TUploadProps],
    ):
        super().__init__("t-upload")
        files = kwargs.pop("files", None)

        try_setup_vmodel(self, files, prop_name="files")
        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_cancel_upload(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "cancel-upload",
            handler,
            extends=extends,
        )
        return self

    def on_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "change",
            handler,
            extends=extends,
        )
        return self

    def on_dragenter(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "dragenter",
            handler,
            extends=extends,
        )
        return self

    def on_dragleave(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "dragleave",
            handler,
            extends=extends,
        )
        return self

    def on_drop(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "drop",
            handler,
            extends=extends,
        )
        return self

    def on_fail(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "fail",
            handler,
            extends=extends,
        )
        return self

    def on_one_file_fail(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "one-file-fail",
            handler,
            extends=extends,
        )
        return self

    def on_one_file_success(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "one-file-success",
            handler,
            extends=extends,
        )
        return self

    def on_preview(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "preview",
            handler,
            extends=extends,
        )
        return self

    def on_progress(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "progress",
            handler,
            extends=extends,
        )
        return self

    def on_remove(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "remove",
            handler,
            extends=extends,
        )
        return self

    def on_select_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "select-change",
            handler,
            extends=extends,
        )
        return self

    def on_success(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "success",
            handler,
            extends=extends,
        )
        return self

    def on_validate(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "validate",
            handler,
            extends=extends,
        )
        return self

    def on_waiting_upload_files_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "waiting_upload-files-change",
            handler,
            extends=extends,
        )
        return self


class TUploadSizeLimitObj(TypedDict, total=False):
    size: float
    unit: typing.Literal["B", "KB", "MB", "GB"]
    message: str


class TUploadProps(TypedDict, total=False):
    abridge_name: typing.List
    accept: str
    action: str
    allow_upload_duplicate_file: bool
    auto_upload: bool
    before_all_files_upload: str
    before_upload: str
    cancel_upload_button: typing.Union[str, dict]
    data: typing.Union[str, dict]
    default: str
    disabled: bool
    drag_content: str
    draggable: bool
    file_list_display: str
    files: typing.List
    default_files: typing.List
    format: str
    format_response: str
    headers: dict
    image_viewer_props: dict
    input_attributes: dict
    is_batch_upload: bool
    locale: dict
    max: float
    method: typing.Literal[
        "POST",
        "GET",
        "PUT",
        "OPTIONS",
        "PATCH",
        "post",
        "get",
        "put",
        "options",
        "patch",
    ]
    mock_progress_duration: float
    multiple: bool
    name: str
    placeholder: str
    request_method: str
    show_image_file_name: bool
    show_thumbnail: bool
    show_upload_progress: bool
    size_limit: typing.Union[float, TUploadSizeLimitObj]
    status: typing.Literal["default", "success", "warning", "error"]
    theme: typing.Literal[
        "custom", "file", "file-input", "file-flow", "image", "image-flow"
    ]
    tips: str
    trigger: str
    trigger_button_props: dict
    upload_all_files_in_one_request: bool
    upload_button: typing.Union[str, dict]
    upload_pasted_files: bool
    use_mock_progress: bool
    value: typing.List
    default_value: typing.List
    with_credentials: bool
    on_cancel_upload: EventMixin
    on_change: EventMixin
    on_dragenter: EventMixin
    on_dragleave: EventMixin
    on_drop: EventMixin
    on_fail: EventMixin
    on_one_file_fail: EventMixin
    on_one_file_success: EventMixin
    on_preview: EventMixin
    on_progress: EventMixin
    on_remove: EventMixin
    on_select_change: EventMixin
    on_success: EventMixin
    on_validate: EventMixin
    on_waiting_upload_files_change: EventMixin
