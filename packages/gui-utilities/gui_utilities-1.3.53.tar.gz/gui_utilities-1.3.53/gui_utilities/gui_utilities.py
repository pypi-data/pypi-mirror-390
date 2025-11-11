from PyQt6.QtCore import Qt, QObject, QEvent, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QDialog, QToolButton, QWidgetAction, QCheckBox, QTableWidget, QHeaderView, QApplication, QStyle, QStyledItemDelegate
from PyQt6.QtGui import QIcon, QTextDocument
import re
import requests
import importlib.resources

main_dir = importlib.resources.files("gui_utilities")
icons_dir = main_dir / "icons"
tlds_path = main_dir / "tlds"

def latex_to_html(expression):
    html_expression = expression
    html_expression = re.sub(r"\\frac\{(.*?)\}\{(.*?)\}", r"<span style='font-size:90%;'>\1⁄\2</span>", html_expression)
    html_expression = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", html_expression)
    html_expression = re.sub(r"\^\{([^}]+)\}", r"<sup>\1</sup>", html_expression)
    html_expression = re.sub(r"_([a-zA-Z0-9]+)", r"<sub>\1</sub>", html_expression)
    html_expression = re.sub(r"\^([a-zA-Z0-9]+)", r"<sup>\1</sup>", html_expression)
    html_expression = html_expression.replace(" ", "&nbsp;")
    return html_expression

def create_window(title, background_color = "#1e1e1e", parent = None):
    window = QWidget(parent)
    window.setObjectName("window")
    window.setWindowTitle(title)
    window.setStyleSheet(f"#window {{background-color: {background_color};}}")
    main_layout = QVBoxLayout(window)
    window.setLayout(main_layout)
    return window

def create_menu(
    ui_instance,
    buttons,
    title,
    title_font_family = "Segoe UI",
    title_font_size = 36,
    title_font_color = "#ffffff",
    title_background_color = "#1e1e1e",
    title_padding = 15,
    title_padding_left = None,
    title_padding_top = None,
    title_padding_right = None,
    title_padding_bottom = None,
    title_border_width = 0,
    title_border_color = "#ffffff",
    title_border_radius = 0,
    math_expression = False,
    title_alignment = Qt.AlignmentFlag.AlignCenter
):
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(25, 25, 25, 25)
    main_layout.addLayout(create_title(
        text = title,
        font_family = title_font_family,
        font_size = title_font_size,
        font_color = title_font_color,
        background_color = title_background_color,
        padding = title_padding,
        padding_left = title_padding_left,
        padding_top = title_padding_top,
        padding_right = title_padding_right,
        padding_bottom = title_padding_bottom,
        border_width = title_border_width,
        border_color = title_border_color,
        border_radius = title_border_radius,
        math_expression = math_expression,
        alignment = title_alignment
    ))
    body_layout = QHBoxLayout()
    main_layout.addLayout(body_layout)
    body_layout.setSpacing(25)
    menu_layout = QVBoxLayout()
    body_layout.addLayout(menu_layout)
    menu_layout.setSpacing(10)
    normal_buttons = []
    special_buttons = []
    for button_properties in buttons:
        if button_properties.get("text") in ["Atrás", "Salir"]: special_buttons.append(button_properties)
        else: normal_buttons.append(button_properties)
    for button_properties in normal_buttons:
        button_properties_copy = button_properties.copy()
        callback = button_properties_copy.pop("callback", None)
        button = create_button(**button_properties_copy)
        if callback: button.clicked.connect(callback)
        menu_layout.addWidget(button)
    menu_layout.addStretch()
    for button_properties in special_buttons:
        button_properties_copy = button_properties.copy()
        callback = button_properties_copy.pop("callback", None)
        button_properties_copy.setdefault("font_size", 16)
        button = create_button(**button_properties_copy)
        if callback: button.clicked.connect(callback)
        menu_layout.addWidget(button)
    ui_instance.content_widget = QWidget()
    ui_instance.content_widget.setLayout(QVBoxLayout())
    body_layout.addWidget(ui_instance.content_widget)
    ui_instance.content_widget.setStyleSheet("background-color: #333333;")
    body_layout.setStretch(0, 1)
    body_layout.setStretch(1, 4)
    return main_layout

def create_header(
    title,
    margin_left = 25,
    margin_top = 25,
    margin_right = 25,
    margin_bottom = 25,
    title_font_family = "Segoe UI",
    title_font_size = 36,
    title_font_color = "#ffffff",
    title_background_color = "#1e1e1e",
    title_padding = 15,
    title_padding_left = None,
    title_padding_top = None,
    title_padding_right = None,
    title_padding_bottom = None,
    title_border_width = 0,
    title_border_color = "#ffffff",
    title_border_radius = 0,
    math_expression = False,
    title_alignment = Qt.AlignmentFlag.AlignCenter
):
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(margin_left, margin_top, margin_right, margin_bottom)
    title_layout = create_title(
        text = title,
        font_family = title_font_family,
        font_size = title_font_size,
        font_color = title_font_color,
        background_color = title_background_color,
        padding = title_padding,
        padding_left = title_padding_left,
        padding_top = title_padding_top,
        padding_right = title_padding_right,
        padding_bottom = title_padding_bottom,
        border_width = title_border_width,
        border_color = title_border_color,
        border_radius = title_border_radius,
        math_expression = math_expression,
        alignment = title_alignment
    )
    main_layout.addLayout(title_layout)
    main_layout.addStretch()
    return main_layout

def create_title(
    text,
    font_family = "Segoe UI",
    font_size = 36,
    font_color = "#ffffff",
    background_color = "transparent",
    padding = 15,
    padding_left = None,
    padding_top = None,
    padding_right = None,
    padding_bottom = None,
    border_width = 0,
    border_color = "#ffffff",
    border_radius = 0,
    math_expression = False,
    alignment = Qt.AlignmentFlag.AlignCenter
):
    title_layout = QHBoxLayout()
    title_layout.setContentsMargins(0, 0, 0, 25)
    title_label = create_label(
        text = text,
        font_family = font_family,
        font_size = font_size,
        font_color = font_color,
        font_weight = "bold",
        background_color = background_color,
        padding = padding,
        padding_left = padding_left,
        padding_top = padding_top,
        padding_right = padding_right,
        padding_bottom = padding_bottom,
        border_width = border_width,
        border_color = border_color,
        border_radius = border_radius,
        math_expression = math_expression,
        alignment = alignment
    )
    title_layout.addWidget(title_label)
    return title_layout

def create_label(
        text,
        font_family = "Segoe UI",
        font_size = 14,
        font_color = "#ffffff",
        font_weight = "normal",
        background_color = "transparent",
        padding = 15,
        padding_left = None,
        padding_top = None,
        padding_right = None,
        padding_bottom = None,
        border_width = 0,
        border_color = "#5c5c5c",
        border_radius = 0,
        hover_background_color = "transparent",
        hover_border_width = 0,
        hover_border_color = "#777777",
        disabled_font_color = "#888888",
        disabled_background_color = "transparent",
        disabled_border_width = 0,
        disabled_border_color = "#4a4a4a",
        math_expression = False,
        transparent_for_mouse = False,
        alignment = None,
        word_wrap = False,
        parent = None
):
    if math_expression:
        label = QLabel(latex_to_html(text), parent)
        label.setTextFormat(Qt.TextFormat.RichText)
    else: label = QLabel(text, parent)
    if transparent_for_mouse: label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    if alignment: label.setAlignment(alignment)
    if word_wrap: label.setWordWrap(True)
    padding_left_value = padding_left if padding_left is not None else padding
    padding_top_value = padding_top if padding_top is not None else padding
    padding_right_value = padding_right if padding_right is not None else padding
    padding_bottom_value = padding_bottom if padding_bottom is not None else padding
    style = f"""
        QLabel {{
            font-family: {font_family};
            font-size: {font_size}px;
            color: {font_color};
            font-weight: {font_weight};
            background-color: {background_color};
            padding-left: {padding_left_value}px;
            padding-top: {padding_top_value}px;
            padding-right: {padding_right_value}px;
            padding-bottom: {padding_bottom_value}px;
            border: {border_width}px solid {border_color};
            border-radius: {border_radius}px;
        }}
        QLabel:hover{{
            background-color: {hover_background_color};
            border: {hover_border_width}px solid {hover_border_color};
        }}
        QLabel:disabled{{
            color: {disabled_font_color};
            background-color: {disabled_background_color};
            border: {disabled_border_width}px solid {disabled_border_color};
        }}
    """
    label.setStyleSheet(style)
    return label

def create_button(
    text,
    font_family = "Segoe UI",
    font_size = 14,
    font_color = "#ffffff",
    font_weight = "bold",
    background_color = "#1e1e1e",
    padding = 15,
    padding_left = None,
    padding_top = None,
    padding_right = None,
    padding_bottom = None,
    border_width = 2,
    border_color = "#5c5c5c",
    border_radius = 0,
    hover_background_color = "#333333",
    hover_border_width = 3,
    hover_border_color = "#777777",
    pressed_background_color = "#4a4a4a",
    pressed_border_width = 3,
    pressed_border_color = "#0078d7",
    disabled_font_color = "#888888",
    disabled_background_color = "#2d2d2d",
    disabled_border_width = 2,
    disabled_border_color = "#4a4a4a",
    maximum_width = 360,
    math_expression = False,
    parent = None
):
    button = QPushButton(parent)
    if maximum_width is not None: button.setMaximumWidth(maximum_width)
    main_layout = QVBoxLayout()
    button.setLayout(main_layout)
    main_layout.setContentsMargins(0, 0, 0, 0)
    label = create_label(
        text = text,
        font_size = font_size,
        font_color = font_color,
        font_weight = "bold",
        padding = padding,
        padding_left = padding_left,
        padding_top = padding_top,
        padding_right = padding_right,
        padding_bottom = padding_bottom,
        disabled_border_width = disabled_border_width,
        transparent_for_mouse = True,
        alignment = Qt.AlignmentFlag.AlignCenter,
        math_expression = math_expression
    )
    label.setWordWrap(True)
    main_layout.addWidget(label)
    button.setFixedHeight(main_layout.sizeHint().height() + 2 * border_width)
    padding_left_value = padding_left if padding_left is not None else padding
    padding_top_value = padding_top if padding_top is not None else padding
    padding_right_value = padding_right if padding_right is not None else padding
    padding_bottom_value = padding_bottom if padding_bottom is not None else padding
    style_sheet = f"""
        QPushButton {{
            font-family: {font_family};
            font-size: {font_size}px;
            color: {font_color};
            font-weight: {font_weight};
            background-color: {background_color};
            padding-left: {padding_left_value}px;
            padding-top: {padding_top_value}px;
            padding-right: {padding_right_value}px;
            padding-bottom: {padding_bottom_value}px;
            border: {border_width}px solid {border_color};
            border-radius: {border_radius}px;
        }}
        QPushButton:hover {{
            background-color: {hover_background_color};
            border: {hover_border_width}px solid {hover_border_color};
        }}
        QPushButton:pressed {{
            background-color: {pressed_background_color};
            border: {pressed_border_width}px solid {pressed_border_color};
        }}
        QPushButton:disabled {{
            color: {disabled_font_color};
            background-color: {disabled_background_color};
            border: {disabled_border_width}px solid {disabled_border_color};
        }}
    """
    button.setStyleSheet(style_sheet)
    return button

def create_text_box(
    placeholder_text,
    font_family = "Segoe UI",
    font_size = 14,
    font_color = "#ffffff",
    font_weight = "normal",
    background_color = "#1e1e1e",
    padding = 15,
    padding_left = None,
    padding_top = None,
    padding_right = None,
    padding_bottom = None,
    border_width = 2,
    border_color = "#5c5c5c",
    border_radius = 0,
    placeholder_font_color = "#888888",
    hover_background_color = "#333333",
    hover_border_width = 3,
    hover_border_color = "#777777",
    focus_font_color = "#000000",
    focus_background_color = "#ffffff",
    focus_border_width = 3,
    focus_border_color = "#0078d7",
    disabled_background_color = "#2d2d2d",
    disabled_border_width = 2,
    disabled_border_color = "#4a4a4a",
    show_text_icon_url = str(icons_dir / "show_text_icon.png"),
    hide_text_icon_url = str(icons_dir / "hide_text_icon.png"),
    focused_show_text_icon_url = str(icons_dir / "focused_show_text_icon.png"),
    focused_hide_text_icon_url = str(icons_dir / "focused_hide_text_icon.png"),
    hide_text = False,
    math_expression = False,
    parent = None
):
    text_box = QLineEdit(parent)
    padding_left_value = padding_left if padding_left is not None else padding
    padding_top_value = padding_top if padding_top is not None else padding
    padding_right_value = padding_right if padding_right is not None else padding
    padding_bottom_value = padding_bottom if padding_bottom is not None else padding
    style_sheet = f"""
        QLineEdit {{
            font-family: {font_family};
            font-size: {font_size}px;
            color: {font_color};
            font-weight: {font_weight};
            background-color: {background_color};
            padding-left: {padding_left_value}px;
            padding-top: {padding_top_value}px;
            padding-right: {padding_right_value}px;
            padding-bottom: {padding_bottom_value}px;
            border: {border_width}px solid {border_color};
            border-radius: {border_radius}px;
        }}
        QLineEdit:hover {{
            background-color: {hover_background_color};
            border: {hover_border_width}px solid {hover_border_color};
        }}
        QLineEdit:focus {{
            color: {focus_font_color};
            background-color: {focus_background_color};
            border: {focus_border_width}px solid {focus_border_color};
        }}
        QLineEdit:disabled {{
            background-color: {disabled_background_color};
            border: {disabled_border_width}px solid {disabled_border_color};
        }}
    """
    text_box.setStyleSheet(style_sheet)
    if hide_text:
        show_text_icon = QIcon(show_text_icon_url)
        hide_text_icon = QIcon(hide_text_icon_url)
        focused_show_text_icon = QIcon(focused_show_text_icon_url)
        focused_hide_text_icon = QIcon(focused_hide_text_icon_url)
        text_box.setEchoMode(QLineEdit.EchoMode.Password)
        toggle_text_visibility_button = QToolButton(text_box)
        toggle_text_visibility_button.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle_text_visibility_button.setAutoRaise(True)
        toggle_text_visibility_button.setIcon(hide_text_icon)
        toggle_text_visibility_button.setIconSize(QSize(25, 25))
        toggle_text_visibility_action = QWidgetAction(text_box)
        toggle_text_visibility_action.setDefaultWidget(toggle_text_visibility_button)
        text_box.addAction(toggle_text_visibility_action, QLineEdit.ActionPosition.TrailingPosition)
        toggle_text_visibility_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                margin-right: 10px;
            }
        """)
        
        def update_icon():
            is_password = text_box.echoMode() == QLineEdit.EchoMode.Password
            if text_box.hasFocus(): icon = focused_hide_text_icon if is_password else focused_show_text_icon
            else: icon = hide_text_icon if is_password else show_text_icon
            toggle_text_visibility_button.setIcon(icon)
        
        def toggle_visibility():
            if text_box.echoMode() == QLineEdit.EchoMode.Password: text_box.setEchoMode(QLineEdit.EchoMode.Normal)
            else: text_box.setEchoMode(QLineEdit.EchoMode.Password)
            update_icon()
        
        toggle_text_visibility_button.clicked.connect(toggle_visibility)

        class _IconFocusWatcher(QObject):

            def __init__(self, watched, on_focus_change):
                super().__init__(watched)
                self._watched = watched
                self._on_focus_change = on_focus_change
            
            def eventFilter(self, watched, event):
                if watched is self._watched and event.type() in (QEvent.Type.FocusIn, QEvent.Type.FocusOut):
                    if callable(self._on_focus_change): self._on_focus_change()
                return super().eventFilter(watched, event)
        
        icon_focus_watcher = _IconFocusWatcher(text_box, update_icon)
        text_box.installEventFilter(icon_focus_watcher)
        setattr(text_box, "_icon_focus_watcher", icon_focus_watcher)
    
    placeholder_label = create_label(
        text = placeholder_text,
        font_family = font_family,
        font_size = font_size,
        font_color = placeholder_font_color,
        font_weight = font_weight,
        padding = padding,
        padding_left = padding_left,
        padding_top = padding_top,
        padding_right = padding_right,
        padding_bottom = padding_bottom,
        math_expression = math_expression,
        transparent_for_mouse = True,
        parent = text_box
    )
    placeholder_label.move(0, 2)
    
    def update_placeholder_visibility():
        has_text = bool(text_box.text().strip())
        has_focus = text_box.hasFocus()
        placeholder_label.setVisible(not has_text and not has_focus)
        if hide_text: update_icon()
    
    class _PlaceholderFocusWatcher(QObject):

        def __init__(self, watched, on_focus_change):
            super().__init__(watched)
            self._watched = watched
            self._on_focus_change = on_focus_change
        
        def eventFilter(self, watched, event):
            if watched is self._watched and event.type() in (QEvent.Type.FocusIn, QEvent.Type.FocusOut):
                if callable(self._on_focus_change): self._on_focus_change()
            return super().eventFilter(watched, event)
    
    placeholder_focus_watcher = _PlaceholderFocusWatcher(text_box, update_placeholder_visibility)
    text_box.installEventFilter(placeholder_focus_watcher)
    setattr(text_box, "_placeholder_focus_watcher", placeholder_focus_watcher)
    update_placeholder_visibility()
    return text_box

def create_combo_box(
    placeholder_text,
    items,
    font_family = "Segoe UI",
    font_size = 14,
    placeholder_font_color = "#888888",
    font_color = "#ffffff",
    background_color = "#1e1e1e",
    padding = 15,
    padding_left = None,
    padding_top = None,
    padding_right = None,
    padding_bottom = None,
    border_width = 2,
    border_color = "#5c5c5c",
    border_radius = 0,
    hover_background_color = "#333333",
    hover_border_width = 3,
    hover_border_color = "#777777",
    on_font_color = "#000000",
    on_background_color = "#ffffff",
    on_border_width = 3,
    on_border_color = "#0078d7",
    dropdown_font_color = "#ffffff",
    dropdown_background_color = "#1e1e1e",
    dropdown_selection_background_color = "#0078d7",
    dropdown_border_width = 1,
    dropdown_border_color = "#5c5c5c",
    math_expression = False,
    parent = None
):
    combo_box = QComboBox(parent)
    combo_box.setAccessibleName("combo_box")
    padding_left_value = padding_left if padding_left is not None else padding
    padding_top_value = padding_top if padding_top is not None else padding
    padding_right_value = padding_right if padding_right is not None else padding
    padding_bottom_value = padding_bottom if padding_bottom is not None else padding
    if math_expression:
        placeholder_label = create_label(
            text = placeholder_text,
            font_family = font_family,
            font_size = font_size,
            font_color = placeholder_font_color,
            padding = padding,
            padding_left = padding_left,
            padding_top = padding_top,
            padding_right = padding_right,
            padding_bottom = padding_bottom,
            math_expression = True,
            transparent_for_mouse = True,
            parent = combo_box
        )
        placeholder_label.move(0, 2)

        def update_placeholder_visibility():
            has_selection = combo_box.currentIndex() != -1
            placeholder_label.setVisible(not has_selection)

        combo_box.currentIndexChanged.connect(update_placeholder_visibility)
        update_placeholder_visibility()

        class RichTextDelegate(QStyledItemDelegate):
            def __init__(
                self,
                parent = None,
                font_color = "#ffffff",
                selection_font_color = "#ffffff"
            ):
                super().__init__(parent)
                self.font_color = font_color
                self.selection_font_color = selection_font_color

            def paint(self, painter, option, index):
                if option.state & QStyle.StateFlag.State_Selected: text_color = self.selection_font_color
                else: text_color = self.font_color
                document = QTextDocument()
                html = f"<span style = \"color:{text_color};\">{index.data(Qt.ItemDataRole.DisplayRole)}</span>"
                document.setHtml(html)
                option.text = ""
                QApplication.style().drawControl(QStyle.ControlElement.CE_ItemViewItem, option, painter)
                painter.save()
                painter.translate(option.rect.left(), option.rect.top() + (option.rect.height() - document.size().height()) / 2)
                document.drawContents(painter)
                painter.restore()
        
        delegate = RichTextDelegate(
            parent = combo_box,
            font_color = dropdown_font_color,
            selection_font_color = font_color
        )
        combo_box.setItemDelegate(delegate)
        combo_box.clear()
        for item in items: combo_box.addItem(latex_to_html(item))
        combo_box.view().setTextElideMode(Qt.TextElideMode.ElideNone)
    else:
        combo_box.setPlaceholderText(placeholder_text)
        combo_box.addItems(items)
    combo_box.setCurrentIndex(-1)
    if math_expression:
        selected_item_label = create_label(
            text = "",
            font_family = font_family,
            font_size = font_size,
            font_color = font_color,
            padding = padding,
            padding_left = padding_left,
            padding_top = padding_top,
            padding_right = padding_right,
            padding_bottom = padding_bottom,
            math_expression = True,
            transparent_for_mouse = True,
            alignment = Qt.AlignmentFlag.AlignCenter,
            parent = combo_box
        )
        selected_item_label.setVisible(False)

        def update_selected_item_display(index):
            if index != -1:
                html_text = combo_box.itemText(index)
                selected_item_label.setText(html_text)
                selected_item_label.setVisible(True)
            else:
                selected_item_label.setVisible(False)

        combo_box.currentIndexChanged.connect(update_selected_item_display)
    
    def get_stylesheet(font_color):
        return f"""
            QComboBox[accessibleName="combo_box"] {{
                font-family: {font_family};
                font-size: {font_size}px;
                color: {font_color};
                background-color: {background_color};
                padding-left: {padding_left_value}px;
                padding-top: {padding_top_value}px;
                padding-right: {padding_right_value}px;
                padding-bottom: {padding_bottom_value}px;
                border: {border_width}px solid {border_color};
                border-radius: {border_radius}px;
            }}
            QComboBox[accessibleName="combo_box"]:hover {{
                background-color: {hover_background_color};
                border: {hover_border_width}px solid {hover_border_color};
            }}
            QComboBox[accessibleName="combo_box"]:on {{
                color: {"transparent" if math_expression else on_font_color};
                background-color: {on_background_color};
                border: {on_border_width}px solid {on_border_color};
            }}
            QComboBox QAbstractItemView {{
                color: {dropdown_font_color};
                background-color: {dropdown_background_color};
                selection-background-color: {dropdown_selection_background_color};
                border: {dropdown_border_width}px solid {dropdown_border_color};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """

    def change_color(index):
        if index == -1:
            text_color = "transparent" if math_expression else placeholder_font_color
            combo_box.setStyleSheet(get_stylesheet(text_color))
        else:
            text_color = "transparent" if math_expression else font_color
            combo_box.setStyleSheet(get_stylesheet(text_color))
    
    combo_box.currentIndexChanged.connect(change_color)
    change_color(-1)
    return combo_box

def create_checkbox(
    text,
    font_family = "Segoe UI",
    font_size = 14,
    font_color = "#ffffff",
    background_color = "#1e1e1e",
    padding = 5,
    padding_left = None,
    padding_top = None,
    padding_right = None,
    padding_bottom = None,
    indicator_background_color = "#1e1e1e",
    indicator_border_width = 1,
    indicator_border_color = "#5c5c5c",
    indicator_border_radius = 8,
    hover_indicator_background_color = "#333333",
    hover_indicator_border_width = 2,
    hover_indicator_border_color = "#777777",
    pressed_indicator_background_color = "#4a4a4a",
    pressed_indicator_border_width = 2,
    pressed_indicator_border_color = "#0078d7",
    checked_indicator_background_color = "#ffffff",
    checked_indicator_border_width = 1,
    checked_indicator_border_color = "#5c5c5c",
    disabled_font_color = "#888888",
    disabled_background_color = "#2d2d2d",
    disabled_border_width = 1,
    disabled_border_color = "#4a4a4a",
    parent = None
):
    check_box = QCheckBox(text, parent)
    padding_left_value = padding_left if padding_left is not None else padding
    padding_top_value = padding_top if padding_top is not None else padding
    padding_right_value = padding_right if padding_right is not None else padding
    padding_bottom_value = padding_bottom if padding_bottom is not None else padding
    style_sheet = f"""
        QCheckBox {{
            font-family: {font_family};
            font-size: {font_size}px;
            color: {font_color};
            background-color: {background_color};
            padding-left: {padding_left_value}px;
            padding-top: {padding_top_value}px;
            padding-right: {padding_right_value}px;
            padding-bottom: {padding_bottom_value}px;
        }}
        QCheckBox::indicator {{
            image: none;
            width: {font_size}px;
            height: {font_size}px;
            background-color: {indicator_background_color};
            border: {indicator_border_width}px solid {indicator_border_color};
            border-radius: {indicator_border_radius}px;
        }}
        QCheckBox::indicator:hover {{
            background-color: {hover_indicator_background_color};
            border: {hover_indicator_border_width}px solid {hover_indicator_border_color};
        }}
        QCheckBox::indicator:pressed {{
            background-color: {pressed_indicator_background_color};
            border: {pressed_indicator_border_width}px solid {pressed_indicator_border_color};
        }}
        QCheckBox::indicator:checked {{
            background-color: {checked_indicator_background_color};
            border: {checked_indicator_border_width}px solid {checked_indicator_border_color};
        }}
        QCheckBox:disabled {{
            color: {disabled_font_color};
        }}
        QCheckBox::indicator:disabled {{
            background-color: {disabled_background_color};
            border: {disabled_border_width}px solid {disabled_border_color};
        }}
    """ 
    check_box.setStyleSheet(style_sheet)
    return check_box

def create_information_message_box(
    text,
    left_margin = 25,
    top_margin = 25,
    right_margin = 25,
    bottom_margin = 25,
    spacing = 10,
    background_color = "#1e1e1e",
    border_width = 2,
    border_color = "#5c5c5c",
    border_radius = 0,
    label_font_family = "Segoe UI",
    label_font_size = 14,
    label_font_color = "#ffffff",
    label_padding = 15,
    label_padding_left = None,
    label_padding_top = None,
    label_padding_right = None,
    label_padding_bottom = None,
    label_border_width = 0,
    label_border_color = "#ffffff",
    label_border_radius = 0,
    button_text = "Aceptar",
    button_font_family = "Segoe UI",
    button_font_size = 14,
    button_font_color = "#ffffff",
    button_background_color = "#1e1e1e",
    button_padding = 15,
    button_padding_left = None,
    button_padding_top = None,
    button_padding_right = None,
    button_padding_bottom = None,
    button_border_width = 2,
    button_border_color = "#5c5c5c",
    button_border_radius = 0,
    button_hover_background_color = "#333333",
    button_hover_border_width = 3,
    button_hover_border_color = "#777777",
    button_pressed_background_color = "#4a4a4a",
    button_pressed_border_width = 3,
    button_pressed_border_color = "#0078d7",
    button_disabled_font_color = "#888888",
    button_disabled_background_color = "#2d2d2d",
    button_disabled_border_width = 2,
    button_disabled_border_color = "#4a4a4a",
    parent = None
):
    message_box = QDialog(parent)
    message_box.setObjectName("message_box")
    message_box.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    message_box.setFixedWidth(360)
    style_sheet = f"""
        QDialog#message_box {{
            background-color: {background_color};
            border: {border_width}px solid {border_color};
            border-radius: {border_radius}px;
        }}
    """
    message_box.setStyleSheet(style_sheet)
    main_layout = QVBoxLayout(message_box)
    message_box.setLayout(main_layout)
    main_layout.setContentsMargins(left_margin, top_margin, right_margin, bottom_margin)
    main_layout.setSpacing(spacing)
    text_label = create_label(
        text = text,
        font_family = label_font_family,
        font_size = label_font_size,
        font_color=  label_font_color,
        background_color = "transparent",
        padding = label_padding,
        padding_left = label_padding_left,
        padding_top = label_padding_top,
        padding_right = label_padding_right,
        padding_bottom = label_padding_bottom,
        border_width = label_border_width,
        border_color = label_border_color,
        border_radius = label_border_radius,
        alignment = Qt.AlignmentFlag.AlignCenter
    )
    main_layout.addWidget(text_label)
    text_label.setWordWrap(True)
    accept_button = create_button(
        text = button_text,
        font_family = button_font_family,
        font_size = button_font_size,
        font_color = button_font_color,
        background_color = button_background_color,
        padding = button_padding,
        padding_left = button_padding_left,
        padding_top = button_padding_top,
        padding_right = button_padding_right,
        padding_bottom = button_padding_bottom,
        border_width = button_border_width,
        border_color = button_border_color,
        border_radius = button_border_radius,
        hover_background_color = button_hover_background_color,
        hover_border_width = button_hover_border_width,
        hover_border_color = button_hover_border_color,
        pressed_background_color = button_pressed_background_color,
        pressed_border_width = button_pressed_border_width,
        pressed_border_color = button_pressed_border_color,
        disabled_font_color = button_disabled_font_color,
        disabled_background_color = button_disabled_background_color,
        disabled_border_width = button_disabled_border_width,
        disabled_border_color = button_disabled_border_color
    )
    main_layout.addWidget(accept_button)
    accept_button.clicked.connect(message_box.accept)
    return message_box
    
def create_confirmation_message_box(
    text,
    left_margin = 25,
    top_margin = 25,
    right_margin = 25,
    bottom_margin = 25,
    main_spacing = 10,
    button_spacing = 10,
    background_color = "#1e1e1e",
    border_width = 2,
    border_color = "#5c5c5c",
    border_radius = 0,
    label_font_family = "Segoe UI",
    label_font_size = 14,
    label_font_color = "#ffffff",
    label_padding = 15,
    label_padding_left = None,
    label_padding_top = None,
    label_padding_right = None,
    label_padding_bottom = None,
    label_border_width = 0,
    label_border_color = "#ffffff",
    label_border_radius = 0,
    button_font_family = "Segoe UI",
    button_font_size = 14,
    button_font_color = "#ffffff",
    button_background_color = "#1e1e1e",
    button_padding = 15,
    button_padding_left = None,
    button_padding_top = None,
    button_padding_right = None,
    button_padding_bottom = None,
    button_border_width = 2,
    button_border_color = "#5c5c5c",
    button_border_radius = 0,
    button_hover_background_color = "#333333",
    button_hover_border_width = 3,
    button_hover_border_color = "#777777",
    button_pressed_background_color = "#4a4a4a",
    button_pressed_border_width = 3,
    button_pressed_border_color = "#0078d7",
    button_disabled_font_color = "#888888",
    button_disabled_background_color = "#2d2d2d",
    button_disabled_border_width = 2,
    button_disabled_border_color = "#4a4a4a",
    parent = None
):
    confirm_message_box = QDialog(parent)
    confirm_message_box.setObjectName("confirm_message_box")
    confirm_message_box.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    confirm_message_box.setFixedWidth(360)
    style_sheet = f"""
        QDialog#confirm_message_box {{
            background-color: {background_color};
            border: {border_width}px solid {border_color};
            border-radius: {border_radius}px;
        }}
    """
    confirm_message_box.setStyleSheet(style_sheet)
    main_layout = QVBoxLayout(confirm_message_box)
    confirm_message_box.setLayout(main_layout)
    main_layout.setContentsMargins(left_margin, top_margin, right_margin, bottom_margin)
    main_layout.setSpacing(main_spacing)
    text_label = create_label(
        text = text,
        font_family = label_font_family,
        font_size = label_font_size,
        font_color = label_font_color,
        background_color = "transparent",
        padding = label_padding,
        padding_left = label_padding_left,
        padding_top = label_padding_top,
        padding_right = label_padding_right,
        padding_bottom = label_padding_bottom,
        border_width = label_border_width,
        border_color = label_border_color,
        border_radius = label_border_radius,
        alignment = Qt.AlignmentFlag.AlignCenter
    )
    main_layout.addWidget(text_label)
    text_label.setWordWrap(True)
    buttons_layout = QHBoxLayout()
    main_layout.addLayout(buttons_layout)
    buttons_layout.setSpacing(button_spacing)
    confirm_button = create_button(
        text = "Sí",
        font_family = button_font_family,
        font_size = button_font_size,
        font_color = button_font_color,
        background_color = button_background_color,
        padding = button_padding,
        padding_left = button_padding_left,
        padding_top = button_padding_top,
        padding_right = button_padding_right,
        padding_bottom = button_padding_bottom,
        border_width = button_border_width,
        border_color = button_border_color,
        border_radius = button_border_radius,
        hover_background_color = button_hover_background_color,
        hover_border_width = button_hover_border_width,
        hover_border_color = button_hover_border_color,
        pressed_background_color = button_pressed_background_color,
        pressed_border_width = button_pressed_border_width,
        pressed_border_color = button_pressed_border_color,
        disabled_font_color = button_disabled_font_color,
        disabled_background_color = button_disabled_background_color,
        disabled_border_width = button_disabled_border_width,
        disabled_border_color = button_disabled_border_color
    )
    buttons_layout.addWidget(confirm_button)
    confirm_button.clicked.connect(confirm_message_box.accept)
    decline_button = create_button(
        text = "No",
        font_family = button_font_family,
        font_size = button_font_size,
        font_color = button_font_color,
        background_color = button_background_color,
        padding = button_padding,
        padding_left = button_padding_left,
        padding_top = button_padding_top,
        padding_right = button_padding_right,
        padding_bottom = button_padding_bottom,
        border_width = button_border_width,
        border_color = button_border_color,
        border_radius = button_border_radius,
        hover_background_color = button_hover_background_color,
        hover_border_width = button_hover_border_width,
        hover_border_color = button_hover_border_color,
        pressed_background_color = button_pressed_background_color,
        pressed_border_width = button_pressed_border_width,
        pressed_border_color = button_pressed_border_color,
        disabled_font_color = button_disabled_font_color,
        disabled_background_color = button_disabled_background_color,
        disabled_border_width = button_disabled_border_width,
        disabled_border_color = button_disabled_border_color
    )
    buttons_layout.addWidget(decline_button)
    decline_button.clicked.connect(confirm_message_box.reject)
    return confirm_message_box

def create_list_table(
    items_data,
    column_headers,
    column_proportions,
    row_populator_function,
    font_family = "Segoe UI",
    font_size = 14,
    font_color = "#ffffff",
    background_color = "#1e1e1e",
    border_width = 2,
    border_color = "#5c5c5c",
    item_font_color = "#ffffff",
    item_background_color = "#1e1e1e",
    selected_item_background_color = "#0078d7",
    header_font_family = "Segoe UI",
    header_font_size = 14,
    header_font_color = "#ffffff",
    header_font_weight = "bold",
    header_background_color = "#1e1e1e",
    header_border_width = 1,
    header_border_color = "#191919",
    hover_header_background_color = "#333333",
    hover_header_border_width = 3,
    hover_header_border_color = "#777777",
    pressed_header_background_color = "#4a4a4a",
    pressed_header_border_width = 3,
    pressed_header_border_color = "#0078d7",
    scrollbar_background_color = "#1e1e1e",
    scrollbar_handle_background_color = "#333333",
    hover_scrollbar_handle_background_color = "#4a4a4a",
    hover_scrollbar_handle_border_width = 3,
    hover_scrollbar_handle_border_color = "#777777",
    pressed_scrollbar_handle_background_color = "#4a4a4a",
    pressed_scrollbar_handle_border_width = 3,
    pressed_scrollbar_handle_border_color = "#0078d7",
    parent = None
):
    list_table = QTableWidget(parent)
    list_table.verticalHeader().setVisible(False)
    list_table.setColumnCount(len(column_headers))
    list_table.setHorizontalHeaderLabels(column_headers)
    header = list_table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    
    def resize_columns():
        total_width = list_table.viewport().width()
        if total_width == 0: return
        for i, proportion in enumerate(column_proportions):
            list_table.setColumnWidth(i, int(total_width * proportion))
    
    resize_columns()
    original_resize_event = list_table.resizeEvent

    def on_resize(event):
        resize_columns()
        if original_resize_event: original_resize_event(event)
    
    list_table.resizeEvent = on_resize
    style_sheet = f"""
        QTableWidget {{
            color: {font_color};
            background-color: {background_color};
            font-family: {font_family};
            font-size: {font_size}px;
            border: {border_width}px solid {border_color};
        }}
        QTableWidget::item {{
            color: {item_font_color};
            background-color: {item_background_color};
            border: none;
        }}
        QTableWidget::item:selected {{
            background-color: {selected_item_background_color};
        }}
        QHeaderView::section {{
            color: {header_font_color};
            background-color: {header_background_color};
            font-family: {header_font_family};
            font-size: {header_font_size}px;
            font-weight: {header_font_weight};
            border: {header_border_width}px solid {header_border_color};
        }}
        QHeaderView::section:hover {{
            background-color: {hover_header_background_color};
            border: {hover_header_border_width}px solid {hover_header_border_color};
        }}
        QHeaderView::section:pressed {{
            background-color: {pressed_header_background_color};
            border: {pressed_header_border_width}px solid {pressed_header_border_color};
        }}
        QScrollBar:vertical {{
            background-color: {scrollbar_background_color};
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background-color: {scrollbar_handle_background_color};
            border: none;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {hover_scrollbar_handle_background_color};
            border: {hover_scrollbar_handle_border_width}px solid {hover_scrollbar_handle_border_color};
        }}
        QScrollBar::handle:vertical:pressed {{
            background-color: {pressed_scrollbar_handle_background_color};
            border: {pressed_scrollbar_handle_border_width}px solid {pressed_scrollbar_handle_border_color};
        }}
    """
    list_table.setStyleSheet(style_sheet)
    list_table.setRowCount(len(items_data))
    for row, item_data in enumerate(items_data):
        items = row_populator_function(item_data)
        for item in items:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        for column, item in enumerate(items):
            list_table.setItem(row, column, item)
    return list_table

def confirm_exit(
    window,
    background_color = "#1e1e1e",
    border_width = 2,
    border_color = "#5c5c5c",
    border_radius = 0,
    label_font_family = "Segoe UI",
    label_font_size = 14,
    label_font_color = "#ffffff",
    label_padding = 15,
    label_padding_top = None,
    label_padding_right = None,
    label_padding_bottom = None,
    label_padding_left = None,
    label_border_width = 0,
    label_border_color = "#ffffff",
    label_border_radius = 0,
    button_font_family = "Segoe UI",
    button_font_size = 14,
    button_font_color = "#ffffff",
    button_background_color = "#1e1e1e",
    button_padding = 15,
    button_padding_top = None,
    button_padding_right = None,
    button_padding_bottom = None,
    button_padding_left = None,
    button_border_width = 2,
    button_border_color = "#5c5c5c",
    button_border_radius = 0,
    button_hover_background_color = "#333333",
    button_hover_border_width = 3,
    button_hover_border_color = "#777777",
    button_pressed_background_color = "#4a4a4a",
    button_pressed_border_width = 3,
    button_pressed_border_color = "#0078d7",
    button_disabled_font_color = "#888888",
    button_disabled_background_color = "#2d2d2d",
    button_disabled_border_width = 2,
    button_disabled_border_color = "#4a4a4a"
):
    confirmation_message_box = create_confirmation_message_box(
        text = "¿Está seguro de querer salir del programa?",
        background_color = background_color,
        border_width = border_width,
        border_color = border_color,
        border_radius = border_radius,
        label_font_family = label_font_family,
        label_font_size = label_font_size,
        label_font_color = label_font_color,
        label_padding = label_padding,
        label_padding_top = label_padding_top,
        label_padding_right = label_padding_right,
        label_padding_bottom = label_padding_bottom,
        label_padding_left = label_padding_left,
        label_border_width = label_border_width,
        label_border_color = label_border_color,
        label_border_radius = label_border_radius,
        button_font_family = button_font_family,
        button_font_size = button_font_size,
        button_font_color = button_font_color,
        button_background_color = button_background_color,
        button_padding = button_padding,
        button_padding_top = button_padding_top,
        button_padding_right = button_padding_right,
        button_padding_bottom = button_padding_bottom,
        button_padding_left = button_padding_left,
        button_border_width = button_border_width,
        button_border_color = button_border_color,
        button_border_radius = button_border_radius,
        button_hover_background_color = button_hover_background_color,
        button_hover_border_width = button_hover_border_width,
        button_hover_border_color = button_hover_border_color,
        button_pressed_background_color = button_pressed_background_color,
        button_pressed_border_width = button_pressed_border_width,
        button_pressed_border_color = button_pressed_border_color,
        button_disabled_font_color = button_disabled_font_color,
        button_disabled_background_color = button_disabled_background_color,
        button_disabled_border_width = button_disabled_border_width,
        button_disabled_border_color = button_disabled_border_color
    )
    result = confirmation_message_box.exec()
    if result == QDialog.DialogCode.Accepted: window.close()

def switch_instance(gui_instance, menu_function):
    new_widget = QWidget()
    new_layout = menu_function()
    new_widget.setLayout(new_layout)
    if gui_instance.central_widget is not None:
        gui_instance.window.layout().replaceWidget(gui_instance.central_widget, new_widget)
        gui_instance.central_widget.deleteLater()
    else: gui_instance.window.layout().addWidget(new_widget)
    gui_instance.central_widget = new_widget

def switch_content_widget(content_widget):
    def clear_layout(layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                child_layout = item.layout()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
                elif child_layout is not None:
                    clear_layout(child_layout)
                    child_layout.setParent(None)
    
    if content_widget.layout() is not None: clear_layout(content_widget.layout())
    for child in content_widget.findChildren(QWidget):
        if child.parent() == content_widget: child.deleteLater()
    main_layout = content_widget.layout()
    main_layout.setContentsMargins(25, 25, 25, 25)
    main_layout.setSpacing(10)
    return main_layout

def get_responsive_width(window, fraction = 3.0):
    screen_width = window.screen().size().width()
    return round(screen_width / fraction)

def validate_string(string, suffix = "El", field = "campo"):
    if string and string.strip(): return None
    return f"{suffix} {field} no puede dejarse {"vacío" if suffix == "El" else "vacía"}."

def validate_integer(integer, suffix = "El", field = "campo"):
    if not integer or not integer.strip(): return f"{suffix} {field} no puede dejarse {"vacío" if suffix == "El" else "vacía"}."
    pattern = re.compile(r"^\d+$")
    unformatted_integer = integer.replace(".", "")
    if pattern.match(unformatted_integer): return None
    return f"No ha ingresado {"un" if suffix == "El" else "una"} {field} {"válido" if suffix == "El" else "válida"}."

def validate_float(number_str, suffix = "El", field = "campo"):
    if not number_str or not number_str.strip():
        return f"{suffix} {field} no puede dejarse {"vacío" if suffix == "El" else "vacía"}."
    try:
        float(number_str.replace(",", "."))
        return None
    except ValueError:
        return f"No ha ingresado {"un" if suffix == "El" else "una"} {field} {"válido" if suffix == "El" else "válida"}."

def validate_id(id_str):
    if not id_str or not id_str.strip(): return "El D.N.I. no puede dejarse vacio."
    pattern = re.compile(r"^(?:\d{8}|(?:\d{1,2}\.\d{3}\.\d{3}))$")
    if pattern.match(id_str): return None
    return "No ha ingresado un D.N.I. válido."

def validate_cellphone_number(cellphone_number):
    if not cellphone_number or not cellphone_number.strip(): return "El número telefónico no puede dejarse vacío."
    clean_number = "".join(filter(str.isdigit, cellphone_number))
    if len(clean_number) == 10: return None
    return "No ha ingresado un número telefónico válido."

tlds_list_path = main_dir / tlds_path / "tlds_list.txt"

def export_tlds(tlds_list):
    try:
        with open(tlds_list_path, "w", encoding = "utf-8") as saved_tlds: saved_tlds.write("\n".join(tlds_list))
    except IOError: pass

def import_tlds():
    try:
        with open(tlds_list_path, "r", encoding = "utf-8") as saved_tlds: return [tld.strip() for tld in saved_tlds]
    except FileNotFoundError: return []

def get_tlds():
    url = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
    try:
        response = requests.get(url, timeout = 10)
        response.raise_for_status()
        tlds_list = [tld.lower() for tld in response.text.splitlines()[1:] if tld]
        if tlds_list: export_tlds(tlds_list)
        return tlds_list
    except requests.exceptions.RequestException: return import_tlds()

def build_email_pattern(tlds_list):
    if not tlds_list:
        return re.compile(
            r"^(?P<local>[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+" 
            r"(?:\[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*)@" 
            r"(?P<dominio>(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
            r"[a-zA-Z]{2,63})$",
            re.IGNORECASE
        )
    tld_pattern = "|".join(re.escape(tld) for tld in sorted(tlds_list, key = len, reverse = True))
    return re.compile(
        r"^(?P<local>[a-zA-Z0-9!#$%&'+/=?^_{|}~-]+"
        r"(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*)@"
        r"(?P<dominio>(?:[a-zA-Z0-9-]+\.)+"
        r"(?:" + tld_pattern + r"))$", re.IGNORECASE
    )

email_pattern = build_email_pattern(get_tlds())

def validate_email(email):
    if not email or not email.strip(): return "El correo electrónico no puede dejarse vacío."
    if email_pattern.match(email): return None
    return "No ha ingresado un correo electrónico válido."

def decimal_format(number, decimal_places = None):
    if isinstance(number, int):
        return f"{number:,}".replace(",", "X").replace(".", ",").replace("X", ".")
    elif isinstance(number, float):
        if not decimal_places: formatted_str = f"{number:,}"
        else: formatted_str = f"{number:,.{decimal_places}f}"
        return formatted_str.replace(",", "X").replace(".", ",").replace("X", ".")
    return str(number)

def format_id(id_string):
    clean_id = id_string.replace(".", "")
    if len(clean_id) == 8: return f"{clean_id[0:2]}.{clean_id[2:5]}.{clean_id[5:8]}"
    elif len(clean_id) == 7: return f"{clean_id[0:1]}.{clean_id[1:4]}.{clean_id[4:7]}"
    return id_string

def format_cellphone_number(cellphone_number):
    clean_number = "".join(filter(str.isdigit, cellphone_number))
    if len(clean_number) == 10: return f"{clean_number[0:4]} - {clean_number[4:10]}"
    return cellphone_number

def format_date(date):
    day = f"{date.day:02d}"
    month = f"{date.month:02d}"
    year = f"{date.year:,}".replace(",", ".")
    return f"{day}/{month}/{year}"