from .main import main as _main
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument("fname")
    parser.add_argument("--no-jump-compression",
            action="store_true", default=False,
            help="disable jump compression optimization")
    parser.add_argument("--no-unreachable",
            action="store_true", default=False,
            help="disable unreachable code optimization")

    _main(parser.parse_args())
