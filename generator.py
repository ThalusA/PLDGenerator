#!/usr/bin/env python3
from sys import argv
from json import load
from pylatex import Document, Tabular, Section

def retrieve_json(filepath: str) -> object:
    with open(filepath, "r") as json_file:
        json_obj = load(json_file)
        return json_obj

def generate_table_of_contents(json_obj: object) -> list:
    pass

def generate_document_desc(doc: Document, doc_desc: object) -> Document:
    with doc.create(Section("Description du document", numbering=False)):
        with doc.create(Tabular('l|l')) as table:
            table.add_row(("Titre", doc_desc['title']))
            table.add_row(("Description", doc_desc['description']))
            table.add_row(("Auteur", doc_desc['authors']))
            table.add_row(("Promotion", doc_desc['promotion']))
            table.add_row(("Date de mise à jour", doc_desc['date']))
            table.add_row(("Version du modèle", doc_desc['version']))
    return doc

def generate_document_revision_table(doc: Document, rev_desc: list) -> Document:
    with doc.create(Section("Tableau des révisions", numbering=False)):
        with doc.create(Tabular('l|l|l|l|l')) as table:
            table.add_row(("Date", "Version", "Auteur", "Sections", "Commentaire"))
            for revision in rev_desc:
                table.add_row((revision['date'], revision['version'], revision['authors'], revision['sections'], revision['comments']))
    return doc

def tree_array_to_tree_string(tree: list) -> str:
    return f"{tree[0]}." if len(tree) == 1 else ".".join(map(str, tree))

def generate_document_table_of_content_recursive(table: Tabular, depth: list, contents: list):
    tree_string = tree_array_to_tree_string(depth)
    depth_len = len(depth)
    tabulation_shift = "\t" * (depth_len - 1)
    table.add_row((f"{tabulation_shift}{tree_string} {contents[0]}", contents[1]))
    if len(contents) == 3 and contents[2] != None:
        depth.append(0)
        for cnt, snd_contents in enumerate(contents[2]):
            depth[depth_len] = cnt + 1
            generate_document_table_of_content_recursive(table, depth, snd_contents)

def generate_document_table_of_content(doc: Document, table_of_content: list) -> Document:
    with doc.create(Section("Tableau des matières", numbering=False)):
        with doc.create(Tabular('l|r')) as table:
            table.add_row(("Description du document", 2))
            table.add_row(("Tableau des révisions", 2))
            table.add_row(("Table des matières", 3))
            shift_time = 0
            for counter, major_title in enumerate(table_of_content):
                generate_document_table_of_content_recursive(table, [counter + 1], major_title)

def initialize_document() -> Document:
    geometry_options = {
        "tmargin": "1cm",
        "lmargin": "10cm"
    }
    doc = Document(geometry_options=geometry_options)

if __name__ == "__main__":
    argc = len(argv)
    if "-h" in argv or argc != 2:
        print(f"USAGE\n\t{argv[0]} json_file\n\nDESCRIPTION\n\tjson_file\tpath of the json file which describes the PLD")
        quit(1)
    else:
        json = retrieve_json(argv[1])
    quit(0)
    
