#!/usr/bin/env python3
import json
import argparse
import glob

from src.generator import generate_pld
from pathlib import Path

from src.schema import PLDSchema, LocaleDictionary

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--schema", help="only generate json schema", action='store_true')
    args = parser.parse_args()
    if args.schema:
        with open("pld_schema.json", "w") as file:
            file.write(PLDSchema.schema_json(indent=2))
        with open("locale_schema.json", "w") as file:
            file.write(LocaleDictionary.schema_json(indent=2))
    else:
        schema_args = json.loads(glob.glob("assets/*.json")[0])
        schema = PLDSchema(**schema_args)
        locale_args = json.loads(str(Path("src/locale").joinpath(f"{schema.locale}.json")))
        locale = LocaleDictionary(**locale_args)
        document = generate_pld(schema, locale)
        tex_filepath = "build/pld.tex"
        pdf_filepath = "build/pld.pdf"
        document.generate_tex(tex_filepath)
        document.generate_pdf(pdf_filepath, clean_tex=True)
        print(f"LaTeX file saved at ./{tex_filepath}")
        print(f"PDF file saved at ./{pdf_filepath}")
    quit(0)
