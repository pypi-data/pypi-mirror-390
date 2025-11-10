import os

__all__ = [
    'fRed',
    'fGre',
    'red',
    'gre',
    'blu',
    'yel',
    'pur',
    'cya',
    'dkred',
    'dkgre',
    'dkblu',
    'dkyel',
    'dkpur',
    'dkcya',
    'h1',
    'info',
    'warn',
    'error',
]


class Colors:
    """
    顯示方式：
        預設值：0
        高亮：1
        非粗體：22
        下劃線：4
        非下劃線：24
        閃爍：5
        非閃爍：25
        反顯：7
        非反顯：27

    前景色：字型顯示的顏色
        黑色：30
        紅色：31
        綠色：32
        黃色：33
        藍色：34
        洋紅：35
        青色：36
        白色：37

    背景色：字型的背景顏色
        黑色：40
        紅色：41
        綠色：42
        黃色：43
        藍色：44
        洋紅：45
        青色：46
        白色：47
    """
    END = "\033[0m"

    BRIGHT = "\033[1m"
    DIM = "\033[2m"
    UNDERSCORE = "\033[4m"
    BLINK = "\033[5m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BACK_RED = "\033[41m"
    BACK_GREEN = "\033[42m"
    BACK_YELLOW = "\033[43m"
    BACK_BLUE = "\033[44m"
    BACK_MAGENTA = "\033[45m"
    BACK_CYAN = "\033[46m"
    BACK_WHITE = "\033[47m"

    BRIGHT_WHHITE_BACK_BLUE = "\033[1;44;37m"
    BRIGHT_GREEN_BACK_BLUE = "\033[1;42;37m"
    BRIGHT_RED_BACK_BLUE = "\033[1;41;37m"


timers = {}


def fmt(iterable):
    return " ".join(str(i) for i in iterable)


def fRed(*args):
    print(Colors.BLINK + Colors.WHITE + Colors.BACK_RED, fmt(args), Colors.END)


def fGre(*args):
    print(Colors.BLINK + Colors.WHITE + Colors.BACK_GREEN, fmt(args), Colors.END)


def red(*args):
    print(Colors.RED, fmt(args), Colors.END)


def gre(*args):
    print(Colors.GREEN, fmt(args), Colors.END)


def blu(*args):
    print(Colors.BLUE, fmt(args), Colors.END)


def yel(*args):
    print(Colors.YELLOW, fmt(args), Colors.END)


def pur(*args):
    print(Colors.MAGENTA, fmt(args), Colors.END)


def cya(*args):
    print(Colors.CYAN, fmt(args), Colors.END)


def dkred(*args):
    print(Colors.BACK_RED, fmt(args), Colors.END)


def dkgre(*args):
    print(Colors.BACK_GREEN, fmt(args), Colors.END)


def dkblu(*args):
    print(Colors.BACK_BLUE, fmt(args), Colors.END)


def dkyel(*args):
    print(Colors.BACK_YELLOW, fmt(args), Colors.END)


def dkpur(*args):
    print(Colors.BACK_MAGENTA, fmt(args), Colors.END)


def dkcya(*args):
    print(Colors.BACK_CYAN, fmt(args), Colors.END)


def h1(*args):
    print(Colors.BRIGHT, fmt(args), Colors.END)


def info(*args):
    print(Colors.DIM + "\t", fmt(args), Colors.END)


def warn(*args):
    print(Colors.BACK_CYAN + "WARN:" + Colors.END + Colors.CYAN, fmt(args), Colors.END)


def error(*args):
    print(Colors.BACK_RED + Colors.BLINK + "ERROR:" + Colors.END + Colors.RED, fmt(args), Colors.END)


def wait(*args):
    return str.lower(input(Colors.BLUE + fmt(args) + Colors.END))


def notify(*args):
    # Play bell
    print('\a')
    # Attempt to send a notification (will fail, but not crash, if not on macOS)
    os.system("""
          osascript -e 'display notification "{}" with title "{}"'
          """.format(args[0], fmt(args[1:])))


def color_test(text='Thanks for using kudio packages!'):
    try:
        for f in __all__:
            eval(f'{f}(text)')
        return True
    except Exception as e:
        print(e)
        return False
