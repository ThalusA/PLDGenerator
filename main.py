#!/usr/bin/env python3
from sys import argv
from json import load
from os import system
from generator import generate_pld

def retrieve_json(filepath: str) -> object:
    with open(filepath, "r") as json_file:
        json_obj = load(json_file)
        return json_obj

if __name__ == "__main__":
    argc = len(argv)
    if "-h" in argv or argc != 2:
        print(f"USAGE\n\t{argv[0]} json_file\n\nDESCRIPTION\n\tjson_file\tpath of the json file which describes the PLD")
        quit(1)
    else:
        json = retrieve_json(argv[1])
        tex = generate_pld(json)
        with open('out.tex', "w") as tex_file:
            tex_file.write(tex)
        print("LaTeX file saved at ./out.tex")
        system("pdflatex -shell-escape ./out.tex")
        print("PDF file saved at ./out.pdf")
    quit(0)
    
