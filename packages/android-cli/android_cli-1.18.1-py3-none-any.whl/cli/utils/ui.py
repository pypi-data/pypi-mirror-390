import base64
import os
import re
import sys
import time

from cli.utils.singleton import singleton


class UIMenuOptions:
    def __init__(self, type, top, options):
        default_init = f"│ {base64.b64decode('PHk+QXV0aG9yPC95PjogPGdyYXk+SnVhbiBCYXJhZ2xpPC9ncmF5Pg==').decode('utf-8')}      │"

        self.type = type
        self.header = top
        self.conf = default_init
        self.options = options


@singleton
class UI:
    colors = {
        "r": "\033[31m",  # red
        "g": "\033[32m",  # green
        "y": "\033[33m",  # yellow
        "b": "\033[30m",  # black
        "w": "\033[37m",  # white
        "italic": "\033[3m",
        "underline": "\033[4m",
        "reverse": "\033[7m",
        "invisible": "\033[8m",
        "strikethrough": "\033[9m",
        "blink": "\033[5m",
        "bold": "\033[1m",
        "gray": "\033[90m",
        "blue": "\033[34m",
        "default": "\033[0m",
        "reset": "\033[0m"
    }

    def init(self, menu: UIMenuOptions):
        self.pline_top(self.tlen(menu.header) + 2)
        self.ptext(f"│ {menu.header} │")
        self.pline(count=29)
        self.ptext(menu.conf)
        self.pline_bottom(self.tlen(menu.header) + 2)

    def clear(self):
        os.system('printf "\033c"')
        os.system('cls' if os.name == 'nt' else 'clear')

    def clear_line(self):
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def pline_top(self, count=50, color='default'):
        print(f"{self.colors[color]}┌" + "─" * count + f"┐{self.colors['reset']}")

    def pline_top_(self, count=48, color='default'):
        print(f"{self.colors[color]}┌" + "─" * count + f"─{self.colors['reset']}")

    def pline_middle(self, count=50, color='default'):
        print(f"{self.colors[color]}├" + "─" * count + f"┤{self.colors['reset']}")

    def pline_middle_(self, count=48, color='default'):
        print(f"{self.colors[color]}├" + "─" * count + f"─{self.colors['reset']}")

    def pline_bottom(self, count=50, color='default'):
        print(f"{self.colors[color]}└" + "─" * count + f"┘{self.colors['reset']}")

    def pline_bottom_(self, count=48, color='default'):
        print(f"{self.colors[color]}└" + "─" * count + f"─{self.colors['reset']}")

    def pline(self, count=50, color='default'):
        print(f"{self.colors[color]}─" * count + f"{self.colors['reset']}")

    def pheader(self, title, leftText=''):
        self.pline_top(len(title) + 4)
        self.ptext(f"│ <reverse> {title} </reverse> │ <gray>{leftText}</gray>")

    def perror(self, message="<gray>Something went wrong</gray>"):
        text = f'<r>ERROR</r> {message}'
        self.pline(self.tlen(text) + 4)
        self.ptext(f'│ {text} │')
        self.pline_bottom(self.tlen(text) + 2)
        self.pcontinue()

    def pfooter_message(self, message="<gray>Something went wrong</gray>"):
        text = f'{message}'
        self.pline(self.tlen(text) + 4)
        self.ptext(f'│ {text} │')
        self.pline_bottom(self.tlen(text) + 2)
        self.pcontinue()

    def psuccess(self, message="<gray>Operation completed</gray>"):
        text = f'<g>SUCCESS</g> {message}'
        self.pline(self.tlen(text) + 4)
        self.ptext(f'│ {text} │')
        self.pline_bottom(self.tlen(text) + 2)
        self.pcontinue()

    def pcontinue(self):
        text = self.ptext(
            f"<gray>Press</gray> <y>[Enter]</y> <gray>to continue...</gray>", True)
        input(text)

    def tlen(self, text):
        def replace_tags_with_ansi(_text):
            def replacer(match):
                return self.colors.get(match.group(0), '')

            return re.sub(r'<[^>]+>', replacer, _text)

        text_with_ansi = replace_tags_with_ansi(text)

        result = len(text_with_ansi)
        for color_code in self.colors.values():
            result -= text_with_ansi.count(color_code) * len(color_code)
        return result

    def ptext(self, content, return_text=False):
        matches = re.findall(r'<(.*?)>(.*?)<\/\1>', content)

        for match in matches:
            color, text = match
            if color in self.colors:
                content = content.replace(
                    f"<{color}>{text}</{color}>", f"{self.colors[color]}{text}{self.colors['reset']}")

        if return_text:
            return content
        else:
            print(content)
            return content

    def loading(self, duration):
        end_time = time.time() + duration
        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏', ]
        while time.time() < end_time:
            for symbol in spinner:
                sys.stdout.write(
                    f"\r {self.colors['y']}{symbol}{self.colors['reset']} Loading")
                sys.stdout.flush()
                time.sleep(0.1)

        self.clear_line()
