import os


def clear_terminal():
    """
        Clears the terminal based on the type of operating system.
    """

    # the terminal clear command for linux
    if os.name == "posix":
        os.system("clear")

    # the console cls command for windows
    elif os.name == "nt":
        os.system("cls")

    # otherwise, just print 25 newlines
    else:
        for _ in range(25):
            print("")
