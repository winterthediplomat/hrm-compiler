from .main import main as _main
from .main import calculate_optimized_ast
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
    parser.add_argument("--no-jmp-then-label",
            action="store_true", default=False,
            help="disable an optimization to remove jumps followed by the label referenced from the jump")

    _main(parser.parse_args())
