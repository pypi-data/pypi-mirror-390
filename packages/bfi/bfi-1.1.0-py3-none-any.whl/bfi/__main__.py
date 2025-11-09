import os
import argparse

from bfi import __version__, parse, interpret, BrainfuckSyntaxError, __file__

def main():
    parser = argparse.ArgumentParser(description="Brainfuck interpreter")

    parser.add_argument('file', type=str, nargs='?',
        help="Brainfuck source file to interpret")
    parser.add_argument('-v', '--version', action='store_true', dest='version',
        help="Print version information")
    parser.add_argument('-e', '--show-examples', action='store_true', dest='show_examples',
        help="Show included example file paths")
    parser.add_argument('-i', '--intermediate', dest='intermediate',
        action='store_true', help="Print intermediate opcode represenation "
        "instead of interpreting")
    parser.add_argument('-t', '--tape-size', dest='size', type=int,
        help="Tape size for brainfuck program", default=30000)
    parser.add_argument('-s', '--input-string', dest='input_string',
        help="Instead of reading input from stdin, read each subsequent byte from this string", default=None)


    args = parser.parse_args()

    if args.version:
        print('bfi %s' % __version__)
        return

    if args.show_examples:
        examples_path = os.path.join(os.path.split(__file__)[0], 'examples')
        for filename in os.listdir(examples_path):
            print(os.path.join(examples_path, filename))

        return

    if not args.file:
        print('Please specify a brainfuck source file')
        return

    with open(args.file, 'r') as fh:
        prog = fh.read()

    if args.intermediate:
        for opcode in parse(prog):
            print(opcode)
    else:
        try:
            interpret(prog, input_data=args.input_string, tape_size=args.size)
        except BrainfuckSyntaxError as e:
            print('Brainfuck syntax error: %s' % e)

if __name__ == "__main__":
    main()
