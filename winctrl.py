#!/usr/bin/python

from i3ipc import Connection, Event
from argparse import ArgumentParser

parser = ArgumentParser(description="i3 window maximize & close")


parser.add_argument(
    "-c",
    "--ctrl",
    type=str,
    help="maximize or close",
    default="maximize",
    choices=["title", "maximize", "close"],
)

default_icon = "ﬓ"
workspace_icon = ""
app_icon = {
    "xfce4-terminal": "",
    "code": "﬏",
    "google-chrome": "",
    "microsoft-edge": "",
    "firefox": "",
    "steam": "",
    "vmware": "",
    "nvim": "",
    "jetbrains-idea-ce": "",  # idea
    "jetbrains-studio": "",  # android studio
    "vlc": "嗢",  # android studio
}

argsv = parser.parse_args()

i3 = Connection()
action = argsv.ctrl


def window_focused():
    focused = i3.get_tree().find_focused()
    return focused


def format_title(title, wclass):
    icon = app_icon.get(wclass)

    if title.__contains__(" - "):
        title_components = title.split(" - ")
        application = title_components[len(title_components) - 1]
        information = title_components[0]
        icon = app_icon.get(application)
        if icon is None:
            icon = app_icon.get(wclass)
        if icon is None:
            icon = default_icon

        if wclass == "xfce4-terminal":
            if application is None or application == "":
                print("%s %s" % (icon, information))
            else:
                print("%s %s ( %s )" % (icon, information, application), flush=True)
                return
        print("%s %s ( %s )" % (icon, application, information), flush=True)
    else:
        icon = app_icon.get(wclass)
        if icon is None:
            icon = default_icon
        print(icon, title, flush=True)


def no_window():
    format_title("Desktop", "workspace")


def print_content(title, wclass):
    if action == "maximize":
        print("", flush=True)
        return
    elif action == "close":
        print("", flush=True)
        return
    elif action == "title":
        # components = focuse.split("-")
        format_title(title, wclass.lower())


def on_window_focus(i3, e):
    focused = window_focused()
    print_for_window(focused)  # type: ignore


def on_workspace_focus(i3, e):
    focused = window_focused()
    print_for_window(focused)  # type: ignore


def print_for_window(window):
    window_class = window.window_class
    window_name = window.name
    if window_class is None or window_class == "":
        no_window()
        return
    else:
        print_content(window_name, window_class)


i3.on(Event.WORKSPACE, on_workspace_focus)
i3.on(Event.WINDOW, on_window_focus)

print_for_window(window_focused())  # type:ignore
i3.main()
