from .main import main as _main
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument("fname")

    _main(parser.parse_args())
