import argparse as ap


def setup_parser() -> ap.ArgumentParser:
    parser = ap.ArgumentParser(
            prog="karavaisv",
            description="This is a simple CLI interface for KaravaiSV templating engine, which allows to render one file per time using parameters from a YAML file with ease.",
            epilog="Learn more about KaravaiSV at 'https://github.com/BIG-Denis/karavaisv' and master the art of templating!")

    parser.add_argument("-i", "--input", type=str, required=True, help="Input file path")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output file path")
    parser.add_argument("-p", "--parameters", type=str, required=False, default=None, help="Parameters file path (YAML)")
    parser.add_argument("-l", "--logging", action='store_true', required=False, default=True, help="Enable logging in the console")

    return parser
