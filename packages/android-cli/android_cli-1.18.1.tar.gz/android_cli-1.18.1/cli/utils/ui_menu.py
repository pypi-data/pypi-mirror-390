from cli.entities.app import App
from cli.utils.ui import UI, UIMenuOptions
from cli.utils.singleton import singleton


@singleton
class UIMenu:

    @staticmethod
    def print_item_not_implemented():
        UI().pfooter_message('<y>ERROR: </y><y>Not implemented yet</y>')

    def print_sub_menu(self, menu: UIMenuOptions):
        while True:
            try:
                result = self.print_menu(menu)
                if result == -1:
                    return
            except KeyboardInterrupt:
                return

    @staticmethod
    def print_menu(menu: UIMenuOptions):

        UI().clear()
        UI().init(menu)

        # Options
        for identifier, description, _ in menu.options:
            UI().ptext(f"│ <g>{identifier}.</g> {description}")

        if menu.type == "main_menu":
            UI().ptext(f"│ <g>0.</g> <r>Exit</r>")
        if menu.type == "sub_menu":
            UI().ptext(f"│ <g>0.</g> Back")

        UI().pline(20)

        choice = input(UI().ptext("<gray>Option</gray>: ", True))
        option_dict = dict((id_, callback) for id_, _, callback in menu.options)

        if choice in option_dict:
            option_dict[choice]()
        else:
            if choice == "0" and menu.type == "main_menu":
                App().close()
            if choice == "0" and menu.type == "sub_menu":
                return -1
            if choice == "":
                return
            # if choice == f"{base64.b64decode('Li4u').decode('utf-8')}":
            #     Decode()
            #     return
            else:
                UI().perror('<r>Invalid option</r>')
                return
