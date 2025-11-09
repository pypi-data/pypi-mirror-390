from cli.entities.menu import Menu
from cli.entities.app import App


def main_function():

    try:
        App().init()
    finally:
        while True:
            try:
                Menu().main_menu()
            except KeyboardInterrupt:
                App().close()
                continue


if __name__ == '__main__':
    main_function()
