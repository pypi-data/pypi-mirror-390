from .speakers import James
from pathlib import Path

def main():
    James().print_name()
    with (Path(__file__).parent /"names.txt").open() as f:
        print(f.read())


if __name__ == "__main__":
    main()