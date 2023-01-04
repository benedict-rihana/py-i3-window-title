#!/usr/bin/python

from i3ipc import Connection, Event
from argparse import ArgumentParser
import yaml
import os

parser = ArgumentParser(description="i3 window maximize & close")

config_path = os.environ.get("XDG_CONFIG_HOME")

if config_path is None:
    config_path = "~/.config/winctrl"
else:
    config_path = config_path + "/winctrl"
config_file = open(config_path + "/config.yaml")
config = yaml.safe_load(config_file)

parser.add_argument(
    "-c",
    "--ctrl",
    type=str,
    help="maximize or close",
    default="maximize",
    choices=["title", "maximize", "close"],
)

defauls = config.get("defaults")
app_icons = config.get("icons")
terminal_apps = config.get("terminal-class")
min_title_length = config.get("min-title-length")
default_icon = defauls.get("default-icon")
workspace_icon = defauls.get("default-workspace-icon")

argsv = parser.parse_args()

i3 = Connection()
action = argsv.ctrl


def window_focused():
    focused = i3.get_tree().find_focused()
    return focused


def print_terminal_window_title(title, wclass):
    application = title
    if title.find(" - ") > 0:
        title_components = title.split(" - ")
        application = title_components[len(title_components) - 1]
        information = title_components[0]
        icon = default_icon
        app_title = extract_app_from_information(application)
        icon = app_icons.get(app_title)
        if icon is None:
            icon = app_icons.get(wclass)
            if icon is None:
                icon = default_icon
            if application is None or application == "":
                print("%s  %s" % (icon, information), flush=True)
            else:
                print("%s  %s" % (icon, application), flush=True)
        else:
            print("%s  %s" % (icon, format_win_title(app_title.title())), flush=True)
    else:
        print("%s  %s" % (icon, application), flush=True)


def format_title(title, wclass):
    is_terminal = is_terminal_app(title, wclass)
    if is_terminal:
        print_terminal_window_title(title, wclass)
    elif wclass != "workspace":
        icon = app_icons.get(wclass)
        if icon is None:
            icon = default_icon
        print("%s  %s" % (icon, format_win_title(title)), flush=True)
    else:
        print("%s  %s" % (workspace_icon, title), flush=True)


def is_terminal_app(title, winclass):
    return winclass in terminal_apps


## Thinking about making this configurable
def extract_app_from_information(application: str):
    if application.startswith("nvim"):
        return "nvim"
    elif application.startswith("vim"):
        return "vim"
    else:
        return application


def format_win_title(title: str):
    if len(title) < min_title_length:
        return title.ljust(min_title_length, " ")
    return title


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
    window_type = window.type
    if window_type == "workspace":
        if action == "title":
            no_window()
            return
        else:
            print("", flush=True)
            return
    else:
        print_content(window_name, window_class)


i3.on(Event.WORKSPACE, on_workspace_focus)
i3.on(Event.WINDOW, on_window_focus)

print_for_window(window_focused())  # type:ignore
i3.main()
