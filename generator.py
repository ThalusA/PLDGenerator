from templates import *
import numpy as np
from datetime import datetime

def generate_options() -> str:
    final_str = add_chunk_environ()
    final_str += add_geometry_options({"a4paper": None, "total":"{170mm,257mm}", "left":"20mm", "top":"20mm"})
    final_str += setcounter("secnumdepth", 0)
    return final_str

def generate_style() -> str:
    final_str = add_new_command("\\rowWidth", "\\linewidth-(\\tabcolsep*2)")
    final_str += add_page_style()
    final_str += add_toc_name()
    final_str += add_document_info("D4DATA PLD - Project Log Document")
    return final_str

def generate_dependencies() -> str:
    final_str = add_document_class("extarticle", "12pt")
    dependencies = [
        ("svg", None),
        ("amsmath", None),
        ("fontenc", "T1"),
        ("inputenc", "utf8"),
        ("fancyhdr", None),
        ("lastpage", None),
        ("hyperref", None),
        ("tgbonum", None),
        ("tabularx", None),
        ("colortbl", None),
        ("geometry", None),
        ("environ", None),
        ("calc", None),
        ("needspace", None),
        ("tocbibind", None),
        ("xcolor", None),
        ("forest", "linguistics"),
        ("adjustbox", None)
    ]
    for name, opt in dependencies:
        final_str += add_package(name, opt)
    final_str += add_tikz_library()
    return final_str

def generate_first_page(subtitle: str = "") -> str:
    return add_page_centered(
        add_figure(customs_data=["\\item\\maketitle"]) +
        add_space(size="4cm") +
        add_style("bold", add_size("Large", subtitle))
    ) if subtitle != "" else add_page_centered(
        add_figure(customs_data=["\\item\\maketitle"])
    )

def generate_document_description(doc_desc: object, last_version_desc: object, local: str = "fr_FR.UTF-8") -> str:
    return add_chunk(add_depth_title("Description du document") + add_arraystreching(1.4) + add_tabularx("|l|X|", [
        [add_cell_color("gray", 0.95, "Titre"), doc_desc.get("title")],
        [add_cell_color("gray", 0.95, "Description"), doc_desc.get("description")],
        [add_cell_color("gray", 0.95, "Auteur"), ", ".join(doc_desc.get("authors"))],
        [add_cell_color("gray", 0.95, "Date de mise à jour"), last_version_desc.get("date")],
        [add_cell_color("gray", 0.95, "Version du modèle"), last_version_desc.get("version")]
    ]))

def generate_document_versions_table(versions: list) -> str:
    content_list = [[add_cell_color("gray", 0.95, "Date", "row"), "Version", "Auteur", "Sections", "Commentaire"]]
    for version in versions:
        content_list.append([version["date"], version["version"], ', '.join(version["author"]), version["sections"], version["comment"]])
    return add_chunk(add_depth_title("Tableau des révisions") + add_arraystreching(1.4) + add_tabularx("|l|l|X|X|X|", content_list))

def generate_toc() -> str:
    return add_toc_name("Table des matières") + add_newpage("\\tableofcontents")

def generate_organigram(title: str, delivrables: list) -> str:
    return add_newpage(add_chunk(add_depth_title("Organigramme des livrables") + add_content_centering(
        add_forest(title, delivrables)
    ), "section"))

def generate_recursively_delivrables(data: object = {}, depth: list = [], content: list = []) -> list:
    content.append(f"{depth_to_string(depth)}{data.get('name')}")
    to_process = data.get('subsets') or data.get('userStories')
    if to_process != None:
        length = len(depth)
        depth.append(0)
        for index, element in enumerate(to_process):
            depth[length] = index + 1
            content = generate_recursively_delivrables(element, depth, content)
    return content

def generate_delivrables(delivrables: list) -> str:
    final_str = add_depth_title("Carte des livrables")
    contents = []
    options = []
    for idx, delivrable in enumerate(delivrables):
        length = len(delivrable.get("subsets"))
        options.append(f"|{'|'.join(['X'] * length if length != 0 else 'X')}|")
        subarrays = []
        max_length = 0
        for subidx, subset in enumerate(delivrable.get("subsets")):
            data = generate_recursively_delivrables(subset, [subidx + 1], [])
            data_len = len(data)
            if data_len > max_length: max_length = data_len
            subarrays.append(data)
        subarrays = list(map(lambda x: np.pad(x, (0, max_length - len(x)), 'constant', constant_values='').tolist(), subarrays))
        contents.append([[add_multicolumn(length, '|c|', add_cell_color("gray", 0.95, delivrable.get("name")))]] + np.transpose(subarrays).tolist())
    for i in range(len(contents)):
        final_str += add_chunk(add_depth_title(delivrables[i].get("name"), 1) + add_arraystreching(1.4) + add_tabularx(options[i], contents[i]), 'subsection')
    return final_str


def generate_user_story(userStory: object) -> str:
    return add_chunk(add_arraystreching(1.4) + add_tabularx("|X|X|", [
        [add_multicolumn(2, "|>{\\columncolor[gray]{0.9}\\centering}m{\\rowWidth}|", add_style("bold", userStory.get("name"), newline=False))],
        [add_cell_color("gray", 0.95, "En tant que :", "row"), "Je veux :"],
        [userStory.get("user"), userStory.get("action")],
        [add_multicolumn(2, "|>{\\columncolor[gray]{0.95}}p{\\rowWidth}|", f"Description :\\newline {userStory.get('description')}")],
        [add_multicolumn(2, "|p{\\rowWidth}|", f"Definition of Done : {add_itemization(userStory.get('definitionOfDone'))}")],
        [add_cell_color("gray", 0.95, "Charge estimée :", "row"), f"{userStory.get('estimatedDuration')} jours-homme ({int(userStory.get('estimatedDuration') * 8)} heures)"], 
    ]))

def generate_recursively_user_stories(data: list, depth: int = 1) -> str:
    if data == None: return ""
    content = ""
    for element in data:
        if element.get("type") == "userStory":
            content += add_depth_title(element.get("name"), depth, True)
            content += generate_user_story(element)
        else:
            content += add_depth_title(element.get("name"), depth)
            content += generate_recursively_user_stories(element.get("subsets") or element.get("userStories"), depth + 1)
    return content

def generate_user_stories(delivrables: list) -> str:
    return add_newpage(add_depth_title("User stories")) + generate_recursively_user_stories(delivrables)

def isolate_json_tags(data: object, tags: list) -> object:
    isolated_object = {}
    for tag in tags:
        isolated_object[tag] = data.get(tag)
    return isolated_object

def generate_pld(json: object) -> str:
    json["versions"] = sorted(json.get("versions") or [], key=lambda x: int(datetime.timestamp(datetime.strptime(x.get("date"), "%d/%m/%y"))))
    return generate_dependencies() + generate_options() + generate_style() + add_wrapper("document",
        generate_first_page(json.get("subTitle")) +
        generate_document_description(isolate_json_tags(json, ["title", "description", "authors"]), isolate_json_tags(json["versions"][-1], ["date", "version"])) +
        generate_document_versions_table(json.get("versions")) +
        setcounter("secnumdepth", 50) + setcounter("tocdepth", 50) +
        generate_toc() +
        generate_organigram("D4DATA", list(map(lambda x: x["name"], json.get("deliverables")))) +
        generate_delivrables(json.get("deliverables")) +
        generate_user_stories(json.get("deliverables"))
    )

from json import load

with open('template.json') as json_file:
    data = load(json_file)
    out = generate_pld(data)
    with open('out.tex', "w") as tex_file:
        tex_file.write(out)