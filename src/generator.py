from src.templates import *
from typing import Dict, Tuple, Union
from datetime import datetime
import numpy as np


def generate_options() -> str:
    final_str = add_chunk_environ()
    final_str += add_geometry_options({"a4paper": None, "total": "{170mm,257mm}", "left": "20mm", "top": "20mm"})
    final_str += setcounter("secnumdepth", 0)
    return final_str


def generate_style(title: str) -> str:
    final_str = add_new_command("\\rowWidth", "\\linewidth-(\\tabcolsep*2)")
    final_str += add_page_style()
    final_str += add_toc_name()
    final_str += add_document_info(title)
    return final_str


def generate_dependencies() -> str:
    final_str = add_document_class("extarticle", "12pt")
    dependencies = [("svg", None), ("amsmath", None), ("fontenc", "T1"), ("inputenc", "utf8"), ("fancyhdr", None), ("lastpage", None),
                    ("hyperref", None), ("tgbonum", None), ("tabularx", None), ("colortbl", None), ("geometry", None), ("environ", None),
                    ("calc", None), ("needspace", None), ("tocbibind", None), ("xcolor", None), ("forest", "linguistics"), ("adjustbox", None), ("enumitem", None)]
    for name, opt in dependencies:
        final_str += add_package(name, opt)
    final_str += add_tikz_library()
    return final_str


def generate_first_page(subtitle: str = "") -> str:
    return add_page_centered(add_figure(customs_data=["\\item\\maketitle"]) + add_space(size="4cm") + add_style("bold", add_size("Large",
        escape_str(subtitle)))) if subtitle != "" else add_page_centered(add_figure(customs_data=["\\item\\maketitle"]))


def generate_stats(json: object) -> Tuple[str, str]:
    authors_score = dict(zip(json.get("authors"), [float(0.0)] * len(json.get("authors"))))
    total_score = float(0.0)
    for deliverable in json.get("deliverables"):
        for subset in deliverable.get("subsets"):
            for userStory in subset.get("userStories"):
                total_score += userStory.get("estimatedDuration")
                for author in userStory.get("assignments"):
                    for saved_author in json.get("authors"):
                        if author in saved_author:
                            authors_score[saved_author] += userStory.get("estimatedDuration")
                            break
    return  f"{total_score:g}", "\\newline ".join(map(lambda value: f"{escape_str(value[0])}: {value[1]:g}", authors_score.items()))

def generate_work_report_page(json: object) -> str:
    authors_user_stories = dict()
    for deliverable in json.get("deliverables"):
        for subset in deliverable.get("subsets"):
            for userStory in subset.get("userStories"):
                for author in userStory.get("assignments"):
                    for saved_author in json.get("authors"):
                        if author in saved_author:
                            if saved_author in authors_user_stories:
                                authors_user_stories[saved_author].append(userStory)
                            else:
                                authors_user_stories[saved_author] = [userStory]
    user_story_status_translations = {"WIP": "En cours", "Done": "Terminé", "To do": "A faire", "Abandoned": "Abandonnée"}
    user_story_status_priority = {"En cour": 3, "Terminé": 4, "A faire": 2, "Abandon": 1}
    return add_newpage(add_chunk(add_depth_title("Rapport d'avancement") + "\n".join(map(
        lambda author_user_stories: add_depth_title(author_user_stories[0], 1) + add_itemization(
            sorted(
                map(
                    lambda user_story: user_story_status_translations.get(user_story.get("status")) + ": " + user_story.get("name"),
                    author_user_stories[1]
                ),
                key=lambda status: user_story_status_priority[status[:7]], reverse=True
            ), ['noitemsep']
        ), authors_user_stories.items()))))

def generate_document_description(doc_desc: object, last_version_desc: object, local: str = "fr_FR.UTF-8") -> str:
    total_jours_hommes, distributions_jours_hommes = generate_stats(doc_desc)
    return add_chunk(add_depth_title("Description du document") + add_arraystreching(1.4) + add_tabularx("|l|X|", [
        [add_cell_color("gray", 0.95, "Titre"), escape_str(doc_desc.get("title"))], [add_cell_color("gray", 0.95, "Description"), escape_str(doc_desc.get("description"))],
        [add_cell_color("gray", 0.95, "Auteur"), escape_str(", ".join(doc_desc.get("authors")))],
        [add_cell_color("gray", 0.95, "Date de mise à jour"), last_version_desc.get("date")],
        [add_cell_color("gray", 0.95, "Version du modèle"), escape_str(last_version_desc.get("version"))],
        [add_multicolumn(2, "|>{\\columncolor[gray]{0.95}\\centering}m{\\rowWidth}|", add_style("bold", "Statistiques", newline=False))],
        [add_cell_color("gray", 0.95, "Distributions jours-hommes"), distributions_jours_hommes],
        [add_cell_color("gray", 0.95, "Total jours-hommes"), total_jours_hommes]]))


def generate_document_versions_table(versions: list) -> str:
    content_list = [[add_cell_color("gray", 0.95, "Date", "row"), "Version", "Auteur", "Sections", "Commentaire"]]
    for version in versions:
        content_list.append([escape_str(version["date"]), escape_str(version["version"]), escape_str(', '.join(version["authors"])), escape_str(version["sections"]), escape_str(version["comment"])])
    return add_chunk(add_depth_title("Tableau des révisions") + add_arraystreching(1.4) + add_tabularx("|l|l|X|X|X|", content_list))


def generate_toc() -> str:
    return add_toc_name("Table des matières") + add_newpage("\\tableofcontents")
 

def generate_organigram(title: str, delivrables: list) -> str:
    return add_newpage(add_chunk(add_depth_title("Organigramme des livrables") + add_content_centering(add_forest(escape_str(title), delivrables)), "section"))


def generate_recursively_delivrables(data: object = {}, depth: list = [], content: list = []) -> list:
    content.append(escape_str(f"{depth_to_string(depth)}{data.get('name')}"))
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
    for delivrable in delivrables:
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
        contents.append([[add_multicolumn(length, '|c|', add_cell_color("gray", 0.95, escape_str(delivrable.get("name"))))]] + np.transpose(subarrays).tolist())
    for i in range(len(contents)):
        final_str += add_chunk(add_depth_title(escape_str(delivrables[i].get("name")), 1) + add_arraystreching(1.4) + add_tabularx(options[i], contents[i]),
            'subsection')
    return final_str


def generate_user_story(userStory: object) -> str:
    return add_chunk(add_arraystreching(1.4) + add_tabularx("|X|X|", [
        [add_multicolumn(2, "|>{\\columncolor[gray]{0.9}\\centering}m{\\rowWidth}|", add_style("bold", escape_str(userStory.get("name")), newline=False))],
        [add_cell_color("gray", 0.95, "En tant que :", "row"), "Je veux :"], [escape_str(userStory.get("user")), escape_str(userStory.get("action"))],
        [add_multicolumn(2, "|>{\\columncolor[gray]{0.95}}p{\\rowWidth}|", f"Description :\\newline {escape_str(userStory.get('description'))}")],
        [add_multicolumn(2, "|p{\\rowWidth}|", f"Definition of Done : {add_itemization(userStory.get('definitionOfDone'))}")],
        [add_multicolumn(2, "|>{\\columncolor[gray]{0.95}}p{\\rowWidth}|", f"Assignation : {escape_str(', '.join(userStory.get('assignments')))}")],
        ["Charge estimée :", f"{userStory.get('estimatedDuration')} jours-hommes ({int(userStory.get('estimatedDuration') * 8)} heures)"],
        [add_cell_color("gray", 0.95, "Status :", "row"), f"{escape_str(userStory.get('status'))}"],
        [add_multicolumn(2, "|p{\\rowWidth}|", f"Commentaires :\\newline {generate_comments(userStory.get('comments'))}")]]))


def generate_comments(comments: Union[None, str, list]) -> str:
    result = ""
    if comments == None:
       return ""
    if isinstance(comments, str):
        comments = [comments]
    for idx, comment in enumerate(comments):
        result += "- " + escape_str(comment)
        if idx < len(comments) - 1:
            result += "\\newline"
    return result


def generate_recursively_user_stories(data: list, depth: int = 1) -> str:
    if data == None: return ""
    content = ""
    for element in data:
        if element.get("type") == "userStory":
            content += add_depth_title(escape_str(element.get("name")), depth, True)
            content += generate_user_story(element)
        else:
            content += add_depth_title(escape_str(element.get("name")), depth)
            if element.get("description") is not None:
                content += escape_str(element.get("description"))
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
    return generate_dependencies() + generate_options() + generate_style(json["title"]) + add_wrapper("document", generate_first_page(
        json.get("subTitle")) + generate_document_description(isolate_json_tags(json, ["title", "description", "authors", "deliverables"]),
        isolate_json_tags(json["versions"][-1], ["date", "version"])) + generate_document_versions_table(json.get("versions")) + setcounter(
        "secnumdepth", 50) + setcounter("tocdepth", 50) + generate_toc() + generate_organigram("D4DATA",
        list(map(lambda x: escape_str(x["name"]), json.get("deliverables")))) + generate_delivrables(json.get("deliverables")) + generate_user_stories(
        json.get("deliverables")) + setcounter("secnumdepth", 0) + generate_work_report_page(
        isolate_json_tags(json, ["title", "description", "authors", "deliverables"])))