# TKurses

tkurses is a library for tkinter like interface in curses

# basic program

```
import curses
import tkurses.core as core
import tkurses.widgets as widgits

def main(stdscr):
    app = core.App(screen, "theme.json", "settings.json") # leave either of these blank to get a defaul writen to a defaultTheme.json or defaultSettings.jdon
    app.addWidget(app.Label("Hello World!", 0,0))

    app.main_loop()

curses.wrapper(main)
```

## Widgets

global functions

```
widget.delete() # delete a widget you have created and un-render it and remove it from the apps widgets allong with all its children
```

### Label

Declaring one

```
app.Label("what To Write",posX,posY)
```

### Button

Declaring one

```
app.Button("what To Write",(posX,posY),(sizeX,sizeY),on_press=function_to_run)
```

### Input prompt

declaring one

```
app.Input("prompt",(posX,posY),(sizeX,sizeY),on_press=function_to_run_on_enter_pressed)

```

### TextBox (Experemental)

Declaring one

```
app.TextBox((PosX,posY),(sizeX,sizeY),enterOnEnter=true)
```

getting current Contents

```
currentTextbox.text
```

## adding Widgets to app

```
app.add_widget(Variable)
```

## Theming files

### example Theme

```
{
    "colors": {
        "background": "black",
        "forground": "white"
    },
    "input": {
        "style": "default",
        "colors": {
            "focused": {
                "background": "black",
                "forground": "white"
            }, "not-focused": {
                "forground": "black",
                "background": "white"
            }
        }
    },
    "text": {
        "colors": {
            "background": "blue",
            "forground": "black"
        },
        "theme": "None",
        "quitKeys": ["Enter","shift-enter"]
    },
    "buttons": {
        "colors": {
            "focused": { "background": "white", "forground": "black"},
            "not-focused": {"background": "black","forground": "white"}
        },
        "start": {"focused":"[","not-focused":"<"},
        "end": {"focused": "]","not-focused":">"}
    }
}
```

Theme options
| key | options | explination |
|-----|---------|-------------|
| ["input"]["style"] | "box"/"default" | box shows inpu as a box and defalut shows it like python input |
| ["text"]["theme"] | Anything you please | Not a thing yet... to be filled in |

## Settings and keybinds

A recent adition to this library is the ability to add settings.json to your program (or rather the requirmen too)
here is an example of what you have to have so far (not all of them work yet but will in future updates)

```
{
    "keybindings": {
        "Move-Focus-Forward": "TAB",
        "Move-Focus-Back": "None",
        "Move-Focus-In-Frame-Forward": "CTRL+D",
        "Move-Focus-In-Frame-Backward": "None",
        "Exit-Text-box": "CTRL+M",
        "Quit-Program": "ESC"
    }
}
```
