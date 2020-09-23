#!/usr/bin/env python3
from sys import argv
from json import load
from subprocess import Popen
from generator import generate_pld

def retrieve_json(filepath: str) -> object:
    with open(filepath, "r") as json_file:
        json_obj = load(json_file)
        return json_obj

if __name__ == "__main__":
    argc = len(argv)
    if "-h" in argv or argc != 2:
        print(f"USAGE\n\t{argv[0]} json_file\n\nDESCRIPTION\n\tjson_file\tpath of the json file which describes the PLD")
        quit(2)
    else:
        try:
            json = retrieve_json(argv[1])
            tex = generate_pld(json)
            with open('out.tex', "w") as tex_file:
                tex_file.write(tex)
            print("LaTeX file saved at ./out.tex")
            process = Popen(["latexmk", "-shell-escape", "-pdf", "-quiet", "./out.tex"])
            ret = process.wait()
            if ret != 0:
                quit(ret)
            print("PDF file saved at ./out.pdf")
        except:
            quit(1)
    quit(0)
    
