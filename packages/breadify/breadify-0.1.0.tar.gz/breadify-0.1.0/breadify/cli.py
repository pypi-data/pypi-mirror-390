import argparse
from .breadify import bread, toast, donut, repeat

def main():
    parser = argparse.ArgumentParser(description="Breadify your text 🍞")
    parser.add_argument("text", help="text to breadify")
    parser.add_argument("--toast", action="store_true", help="toast mode")
    parser.add_argument("--donut", action="store_true", help="donut mode")
    parser.add_argument("--repeat", type=int, help="repeat bread pattern x times")

    args = parser.parse_args()
    text = args.text

    if args.toast:
        text = toast(text)
    if args.donut:
        text = donut(text)
    if args.repeat:
        text = repeat(text, args.repeat)

    print(bread(text))
