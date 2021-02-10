#!/usr/bin/env python3
from sys import argv
from json import load
from subprocess import Popen
from generator import generate_pld
from os import path

def retrieve_json(filepath: str) -> object:
    with open(filepath, "r") as json_file:
        json_obj = load(json_file)
        return json_obj

if __name__ == "__main__":
    argc = len(argv)
    flag = "-f" in argv
    if "-h" in argv or argc != 2 + flag:
        print(f"USAGE\n\t{argv[0]} json_file\n\nDESCRIPTION\n\tjson_file\tpath of the json file which describes the PLD\n\t-f\t\tdon't generate files based on json file name")
        quit(2)
    else:
        try:
            name = "out" if "-f" in argv else path.splitext(path.basename(argv[1]))[0]
            json = retrieve_json(argv[1])
            tex = generate_pld(json)
            with open(f"{name}.tex", "w") as tex_file:
                tex_file.write(tex)
            print(f"LaTeX file saved at ./{name}.tex")
            process = Popen(["latexmk", "-shell-escape", f"-jobname={name}", "-pdf", "-quiet", "-f", f"./{name}.tex"])
            ret = process.wait()
            if ret != 0:
                quit(ret)
            print(f"PDF file saved at ./{name}.pdf")
        except:
            quit(1)
    quit(0)
    
