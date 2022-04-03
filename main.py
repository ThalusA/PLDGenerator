#!/usr/bin/env python3
import json
import argparse
import locale

from src.generator import generate_pld
from pathlib import Path

from src.schema import PLDSchema, LocaleDictionary

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--schema", help="only generate json schema", action='store_true')
    parser.add_argument("-f", "--filepath", help="filepath of the json file which describe the PLD")
    parser.add_argument("-o", "--output", help="filepath of the outputted pdf and tex file")
    parser.add_argument("-l", "--locale", help="specify in which locale your PLD is (ex: fr_FR)",
                        default=locale.getlocale()[0])
    args = parser.parse_args()
    if args.schema:
        with open("pld_schema.json", "w") as file:
            file.write(PLDSchema.schema_json(indent=2))
        with open("locale_schema.json", "w") as file:
            file.write(LocaleDictionary.schema_json(indent=2))
    elif args.path and args.output:
        locale_args = json.loads(str(Path("src/locale").joinpath(args.locale)))
        locale = LocaleDictionary(**locale_args)
        schema_args = json.loads(args.filepath)
        schema = PLDSchema(**schema_args)
        document = generate_pld(schema, locale)
        tex_filepath = str(Path(args.output).with_suffix('.tex'))
        pdf_filepath = str(Path(args.output).with_suffix('.pdf'))
        document.generate_tex(tex_filepath)
        document.generate_pdf(pdf_filepath, clean_tex=True)
        print(f"LaTeX file saved at ./{tex_filepath}.pdf")
        print(f"PDF file saved at ./{pdf_filepath}.pdf")
    else:
        parser.print_help()
    quit(0)
