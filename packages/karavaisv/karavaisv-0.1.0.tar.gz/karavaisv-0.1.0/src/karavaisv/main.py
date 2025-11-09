from .parsing_args import setup_parser
from .util_funcs import read_params_from_yaml, read_source_from_file, write_rendered_to_file
from .rendering import render


def main():
    parser = setup_parser()
    args = parser.parse_args()

    input_file: str = args.input
    output_file: str = args.output
    parameters_file: str | None = args.parameters
    enable_logging: bool = args.logging

    content = read_source_from_file(input_file)

    parameters: dict = {}
    if parameters_file is not None:
        parameters = read_params_from_yaml(parameters_file)

    rendered_content: str = render(content, parameters, logging=enable_logging, filepath=input_file)
    write_rendered_to_file(rendered_content, output_file)


if __name__ == "__main__":
    main()
