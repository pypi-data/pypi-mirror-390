from __future__ import annotations
import typing
from typing_extensions import TypedDict, Unpack
import copy
from instaui import ui
from instaui_tdesign.components._icon_param_utils import make_icon_for_bool_or_str
from ._base_element import BaseElement
from instaui.event.event_mixin import EventMixin
from ._utils import handle_props, handle_event_from_props


class Notification(BaseElement):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        **kwargs: Unpack[TNotificationProps],
    ):
        """
        Displays a notification message with configurable content and behavior.

        Creates a temporary notification element that can display messages, titles, icons,
        and optional footer content. Supports different themes and automatic dismissal.

        Args:
            content (Optional[str]): The main message content of the notification.
            title (Optional[str]): The title displayed at the top of the notification.
            icon (Union[str, bool, None]): Icon to display. Can be a string identifier,
                                        boolean to show/hide default icon, or None.
            **kwargs (Unpack[TNotificationProps]): Additional notification properties:
                close_btn (Union[str, bool]): Custom close button content or boolean to toggle.
                duration (float): Auto-close duration in milliseconds. 0 means no auto-close.
                footer (str): Footer content displayed at the bottom.
                theme (Literal["info", "success", "warning", "error"]): Visual theme.
                on_close_btn_click (EventMixin): Event handler when close button is clicked.
                on_duration_end (EventMixin): Event handler when auto-close duration ends.

        Example:
        .. code-block:: python
            from instaui_tdesign import td
            from instaui import ui

            # Basic notification
            td.notification("Operation completed successfully")

            # Notification with title and theme
            td.notification(
                content="File uploaded successfully",
                title="Success",
                theme="success"
            )

            # Controlled notification with events
            show_notify = ui.state(False)
            td.switch(show_notify)

            with ui.vif(show_notify):
                td.notification(
                    "This will auto-close",
                    duration=2000
                ).on_duration_end(
                    ui.js_event(outputs=[show_notify], code="()=> false")
                )
        """
        super().__init__("t-notification")
        title = kwargs.pop("title", None)
        icon = kwargs.pop("icon", None)

        self.props({"content": content, "title": title})
        make_icon_for_bool_or_str(self, "icon", icon)
        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_close_btn_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "close-btn-click",
            handler,
            extends=extends,
        )
        return self

    def on_duration_end(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "duration-end",
            handler,
            extends=extends,
        )
        return self


class NotifyPlugin:
    @staticmethod
    def info(**options: Unpack[TNotificationOptions]):
        """
        Displays an informational notification using the global notification plugin.

        Shows a temporary notification message at a specified screen position with
        configurable content, styling, and behavior. Unlike regular notifications,
        this uses a global plugin that can display multiple notifications simultaneously.

        Args:
            **options (Unpack[TNotificationOptions]): Configuration options for the notification:
                content (str): The main message content to display.
                title (str): Optional title for the notification.
                attach (str): CSS selector of the element to attach the notification to.
                offset (tuple[Union[str, int], Union[str, int]]): Pixel offset from the placement position.
                placement (Literal["top-right", "top-left", "bottom-right", "bottom-left"]):
                    Screen position where the notification appears. Defaults to "top-right".
                zIndex (int): Z-index for the notification container.
                close_btn (Union[str, bool]): Close button configuration or boolean to toggle.
                duration (float): Auto-close duration in milliseconds. 0 means persistent.
                footer (str): Footer content displayed at the bottom.

        Returns:
            EventMixin: A JavaScript event that triggers the notification when executed.

        Example:
        .. code-block:: python
            from instaui_tdesign import td

            # Simple info notification
            td.button("Show Info").on_click(
                td.notify_plugin.info(content="Operation completed")
            )

            # Notification with custom placement and close button
            td.button("Show Custom").on_click(
                td.notify_plugin.info(
                    content="File uploaded successfully",
                    title="Success",
                    placement="top-left",
                    close_btn=True,
                    duration=3000
                )
            )

            # Persistent notification with footer
            td.button("Show Persistent").on_click(
                td.notify_plugin.info(
                    content="Processing request...",
                    footer="Click close to dismiss",
                    duration=0,
                    close_btn="Close"
                )
            )
        """
        return ui.js_event(
            inputs=[_handle_notification_options(typing.cast(dict, options))],
            code=r"(options)=> $tdesign.NotifyPlugin.info(options)",
        )

    @staticmethod
    def warning(**options: Unpack[TNotificationOptions]):
        """
        Displays a warning notification using the global notification plugin.

        Shows a temporary warning-style notification message with yellow/yellow-themed styling
        to indicate cautionary or attention-required information. Supports multiple simultaneous
        notifications with configurable positioning and behavior.

        Args:
            **options (Unpack[TNotificationOptions]): Configuration options for the warning notification:
                content (str): The main warning message content to display.
                title (str): Optional title for the notification.
                attach (str): CSS selector of the element to attach the notification to.
                offset (tuple[Union[str, int], Union[str, int]]): Pixel offset from the placement position.
                placement (Literal["top-right", "top-left", "bottom-right", "bottom-left"]):
                    Screen position where the notification appears. Defaults to "top-right".
                zIndex (int): Z-index for the notification container.
                close_btn (Union[str, bool]): Close button configuration or boolean to toggle.
                duration (float): Auto-close duration in milliseconds. 0 means persistent.
                footer (str): Footer content displayed at the bottom.

        Returns:
            EventMixin: A JavaScript event that triggers the warning notification when executed.

        Example:
        .. code-block:: python
            from instaui_tdesign import td

            # Simple warning notification
            td.button("Show Warning").on_click(
                td.notify_plugin.warning(content="Please check your input")
            )

            # Warning with title and custom placement
            td.button("Show Custom Warning").on_click(
                td.notify_plugin.warning(
                    content="Disk space is running low",
                    title="System Warning",
                    placement="top-left",
                    duration=5000
                )
            )

            # Persistent warning with close button
            td.button("Show Persistent Warning").on_click(
                td.notify_plugin.warning(
                    content="This action cannot be undone",
                    close_btn=True,
                    duration=0
                )
            )
        """
        return ui.js_event(
            inputs=[_handle_notification_options(typing.cast(dict, options))],
            code=r"(options)=> $tdesign.NotifyPlugin.warning(options)",
        )

    @staticmethod
    def error(**options: Unpack[TNotificationOptions]):
        """
        Displays an error notification using the global notification plugin.

        Shows a temporary error-style notification message with red/red-themed styling
        to indicate critical failures or error conditions. Supports multiple simultaneous
        notifications with configurable positioning and behavior.

        Args:
            **options (Unpack[TNotificationOptions]): Configuration options for the error notification:
                content (str): The main error message content to display.
                title (str): Optional title for the notification.
                attach (str): CSS selector of the element to attach the notification to.
                offset (tuple[Union[str, int], Union[str, int]]): Pixel offset from the placement position.
                placement (Literal["top-right", "top-left", "bottom-right", "bottom-left"]):
                    Screen position where the notification appears. Defaults to "top-right".
                zIndex (int): Z-index for the notification container.
                close_btn (Union[str, bool]): Close button configuration or boolean to toggle.
                duration (float): Auto-close duration in milliseconds. 0 means persistent.
                footer (str): Footer content displayed at the bottom.

        Returns:
            EventMixin: A JavaScript event that triggers the error notification when executed.

        Example:
        .. code-block:: python
            from instaui_tdesign import td

            # Simple error notification
            td.button("Show Error").on_click(
                td.notify_plugin.error(content="Operation failed")
            )

            # Error with title and custom placement
            td.button("Show Custom Error").on_click(
                td.notify_plugin.error(
                    content="Unable to connect to server",
                    title="Connection Error",
                    placement="top-left"
                )
            )
        """
        return ui.js_event(
            inputs=[_handle_notification_options(typing.cast(dict, options))],
            code=r"(options)=> $tdesign.NotifyPlugin.error(options)",
        )

    @staticmethod
    def success(**options: Unpack[TNotificationOptions]):
        """
        Displays a success notification using the global notification plugin.

        Shows a temporary success-style notification message with green/green-themed styling
        to indicate successful operations or positive outcomes. Supports multiple simultaneous
        notifications with configurable positioning and behavior.

        Args:
            **options (Unpack[TNotificationOptions]): Configuration options for the success notification:
                content (str): The main success message content to display.
                title (str): Optional title for the notification.
                attach (str): CSS selector of the element to attach the notification to.
                offset (tuple[Union[str, int], Union[str, int]]): Pixel offset from the placement position.
                placement (Literal["top-right", "top-left", "bottom-right", "bottom-left"]):
                    Screen position where the notification appears. Defaults to "top-right".
                zIndex (int): Z-index for the notification container.
                close_btn (Union[str, bool]): Close button configuration or boolean to toggle.
                duration (float): Auto-close duration in milliseconds. 0 means persistent.
                footer (str): Footer content displayed at the bottom.

        Returns:
            EventMixin: A JavaScript event that triggers the success notification when executed.

        Example:
        .. code-block:: python
            from instaui_tdesign import td

            # Simple success notification
            td.button("Show Success").on_click(
                td.notify_plugin.success(content="Operation completed successfully")
            )

            # Success with title and auto-close
            td.button("Show Custom Success").on_click(
                td.notify_plugin.success(
                    content="Data saved successfully",
                    title="Success",
                    duration=3000
                )
            )
        """
        return ui.js_event(
            inputs=[_handle_notification_options(typing.cast(dict, options))],
            code=r"(options)=> $tdesign.NotifyPlugin.success(options)",
        )

    @staticmethod
    def close_all():
        """
        Closes all currently displayed notifications from the notification plugin.

        Immediately dismisses every active notification regardless of their individual
        durations or close button settings. Useful for clearing the notification area
        when performing bulk operations or page state changes.

        Returns:
            EventMixin: A JavaScript event that closes all notifications when executed.

        Example:
        .. code-block:: python
            from instaui_tdesign import td

            # Close all notifications on button click
            td.button("Clear All Notifications").on_click(
                td.notify_plugin.close_all()
            )

            # Usage with multiple notifications
            td.button("Show Multiple").on_click(
                td.notify_plugin.info(content="Notification 1", duration=0)
            ).on_click(
                td.notify_plugin.warning(content="Notification 2", duration=0)
            ).on_click(
                td.notify_plugin.success(content="Notification 3", duration=0)
            )

            td.button("Close All").on_click(
                td.notify_plugin.close_all()
            )
        """
        return ui.js_event(
            code=r"()=> $tdesign.NotifyPlugin.closeAll()",
        )


class TNotificationProps(TypedDict, total=False):
    title: str
    icon: typing.Union[str, bool]
    close_btn: typing.Union[str, bool]
    duration: float
    footer: str
    theme: typing.Literal["info", "success", "warning", "error"]
    on_close_btn_click: EventMixin
    on_duration_end: EventMixin


class TNotificationOptions(TypedDict, total=False):
    content: str
    title: str
    attach: str
    offset: tuple[typing.Union[str, int], typing.Union[str, int]]
    placement: typing.Literal["top-right", "top-left", "bottom-right", "bottom-left"]
    zIndex: int

    close_btn: typing.Union[str, bool]
    duration: float
    footer: str


def _handle_notification_options(options: dict):
    options = copy.deepcopy(options)
    if "close_btn" in options:
        options["closeBtn"] = options.pop("close_btn")

    return ui.unwrap_reactive(options)
