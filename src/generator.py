import datetime
from hashlib import md5
from typing import Dict, Tuple, List

from pylatex import Document, Package, Command, NewLine, Center, VerticalSpace, LargeText, Figure, Section, Tabularx, \
    MultiColumn, NewPage, TikZ, TikZOptions, TikZNode, TikZDraw, TikZPathList, Subsection, MediumText, Subsubsection, \
    Itemize, MiniPage, Head, Foot, PageStyle, StandAloneGraphic, simple_page_number, UnsafeCommand
from pylatex.utils import bold, NoEscape

from src.schema import PLDSchema, Version, LocaleDictionary, UserStory


def generate_options(document: Document) -> Document:
    document.preamble.append(Command("raggedbottom"))
    document.preamble.append(Command("newlength"))
    document.preamble.append(Command("chunktoheight"))
    document.preamble.append(Command("setcounter", "secnumdepth", extra_arguments="0"))
    return document


def generate_style(schema: PLDSchema, locale: LocaleDictionary, document: Document) -> Document:
    document.preamble.append(UnsafeCommand("newcommand", Command("rowWidth"),
                                           extra_arguments=NoEscape("\\linewidth-(\\tabcolsep*2)")))
    document.preamble.append(
        Command('renewcommand', NoEscape('\\familydefault'), extra_arguments=NoEscape('\\sfdefault')))
    document.preamble.append(Command("graphicspath", NoEscape("{assets/}{../assets/}")))
    header = PageStyle("header")
    with header.create(Head("L")) as left_header:
        left_header: Head
        left_header.create(StandAloneGraphic("primary_logo.pdf", NoEscape("width=30pt")))
    with header.create(Head("R")) as right_header:
        right_header: Head
        right_header.append(LargeText(locale.project_log_document))
    with header.create(Foot("R")) as right_footer:
        right_footer: Foot
        right_footer.append(simple_page_number())
    with header.create(Foot("L")) as left_footer:
        left_footer: Foot
        left_footer.create(StandAloneGraphic("secondary_logo.pdf", NoEscape("width=100pt")))
    document.preamble.append(Command("title",
                                     NoEscape(StandAloneGraphic("primary_logo.pdf", NoEscape("width=100pt")).dumps() +
                                              "~\\\\[1cm]\n" +
                                              locale.project_log_document)))
    now = datetime.date.today()
    document.preamble.append(Command("date", f"{now.day}/{now.month}/{now.year}"))
    document.preamble.append(Command("author", NoEscape(", ".join(schema.authors))))
    document.preamble.append(header)
    document.change_document_style("header")

    return document


def generate_dependencies(document: Document) -> Document:
    dependencies: List[str] = ["svg", "amsmath", "fancyhdr", "hyperref", "tgbonum", "tabularx", "colortbl",
                               "environ", "calc", "needspace", "tocbibind", "adjustbox", "enumitem", "xcolor"]
    dependencies_with_options: List[Tuple[str, str]] = [("xcolor", "table"), ("forest", "linguistics")]
    for name, options in dependencies_with_options:
        document.packages.append(Package(name, options))
    for name in dependencies:
        document.packages.append(Package(name))
    document.packages.append(Command("usetikzlibrary", "fit,positioning"))
    return document


def generate_first_page(schema: PLDSchema, document: Document) -> Document:
    document.append(LargeText(Command("maketitle")))
    document.append(VerticalSpace("4cm"))
    document.append(Command("centering"))
    document.append(LargeText(bold(schema.subtitle)))
    return document


def get_user_story_priority(user_story: UserStory) -> int:
    return user_story.status.to_priority()


def generate_work_report_page(schema: PLDSchema, locale: LocaleDictionary, document: Document) -> Document:
    authors_user_stories = dict()
    for deliverable in schema.deliverables:
        for subset in deliverable.subsets:
            for user_story in subset.user_stories:
                for author in user_story.assignments:
                    for saved_author in schema.authors:
                        if author in saved_author:
                            if saved_author in authors_user_stories:
                                authors_user_stories[saved_author].append(user_story)
                            else:
                                authors_user_stories[saved_author] = [user_story]
    document.append(Command("setcounter", "secnumdepth", extra_arguments="0"))
    document.append(NewPage())
    with document.create(Section(title=locale.advancement_report)) as section:
        section: Section

        for author, user_stories in authors_user_stories.items():
            user_stories = sorted(user_stories, key=get_user_story_priority, reverse=True)
            print(user_stories)
            with section.create(Subsection(title=author)) as subsection:
                subsection: Subsection

                with subsection.create(Itemize()) as itemize:
                    itemize: Itemize

                    for user_story in user_stories:
                        itemize.add_item(f"{user_story.status.translate(locale)}: {user_story.name}")
    return document


def generate_stats(schema: PLDSchema) -> Tuple[float, dict[str, float]]:
    authors_score: Dict[str, float] = dict(zip(schema.authors, [float(0.0)] * len(schema.authors)))
    total_score: float = float(0.0)
    for deliverable in schema.deliverables:
        for subset in deliverable.subsets:
            for user_story in subset.user_stories:
                total_score += user_story.estimated_duration
                for author in user_story.assignments:
                    for saved_author in schema.authors:
                        if author in saved_author:
                            authors_score[saved_author] += user_story.estimated_duration
                            break
    return total_score, authors_score


def generate_document_description(schema: PLDSchema, locale: LocaleDictionary, document: Document) -> Document:
    document.append(NewPage())
    total_man_days, man_days_distribution = generate_stats(schema)
    with document.create(MiniPage()) as minipage:
        minipage: MiniPage
        with minipage.create(Section(title=locale.document_description)) as section:
            section: Section
            with section.create(Tabularx(table_spec="|l|X|", row_height=1.4)) as tabularx:
                tabularx: Tabularx
                tabularx.add_row([MultiColumn(1, data=locale.title, color="gray"), schema.title])
                tabularx.add_row([MultiColumn(1, data=locale.description, color="gray"), schema.description])
                tabularx.add_row([MultiColumn(1, data=locale.authors, color="gray"), ", ".join(schema.authors)])
                tabularx.add_row([MultiColumn(1, data=locale.updated_date, color="gray"), schema.versions[-1].date])
                tabularx.add_row([MultiColumn(1, data=locale.model_version, color="gray"), schema.versions[-1].version])
                tabularx.add_row([MultiColumn(2, color="gray", data=bold(locale.stats))])
                tabularx.add_row([MultiColumn(1, data=locale.man_days_distribution, color="gray"), f"{NewLine()} ".join(
                    [f"{author}: {score:g}" for author, score in man_days_distribution.items()])])
                tabularx.add_row([MultiColumn(1, data=locale.total_man_days, color="gray"), f"{total_man_days:g}"])
    return document


def generate_document_versions_table(schema: PLDSchema, locale: LocaleDictionary, document: Document) -> Document:
    with document.create(Section(title=locale.revision_table)) as section:
        section: Section
        with section.create(Tabularx(table_spec="|l|l|X|X|X|", row_height="1.4")) as tabularx:
            tabularx: Tabularx
            tabularx.add_row([locale.date, locale.version, locale.authors, locale.sections, locale.comment],
                             color="gray")
            for version in schema.versions:
                tabularx.add_row(
                    [version.date, version.version, ', '.join(version.authors), version.sections, version.comment])
    return document


def generate_toc(locale: LocaleDictionary, document: Document) -> Document:
    document.append(Command("setcounter", "secnumdepth", extra_arguments="50"))
    document.append(Command("setcounter", "tocdepth", extra_arguments="50"))
    document.append(Command('renewcommand', Command("contentsname"), extra_arguments=locale.table_of_content))
    document.append(NewPage())
    document.append(Command("tableofcontents"))
    return document


def generate_organigram(schema: PLDSchema, locale: LocaleDictionary, document: Document) -> Document:
    document.append(NewPage())
    with document.create(Figure()) as figure:
        figure: Figure
        with figure.create(Section(title=locale.organigram)) as section:
            section: Section
            with section.create(TikZ()) as forest:
                forest: TikZ

                node_kwargs = {'align': 'center',
                               'minimum size': '20pt'}

                # noinspection PyTypeChecker
                top_box = TikZNode(text=schema.title,
                                   handle=f"project-box",
                                   options=TikZOptions('draw',
                                                        'rounded corners',
                                                        **node_kwargs))
                forest.append(top_box)
                last_box_handle = top_box.handle

                for n_deliverable, deliverable in enumerate(schema.deliverables, start=1):
                    # noinspection PyTypeChecker
                    box = TikZNode(text=f"{n_deliverable}. {deliverable.name}",
                                   handle=f"deliverable-box-{n_deliverable}",
                                   options=TikZOptions('draw',
                                                        'rounded corners',
                                                        f'below = of {last_box_handle}',
                                                        **node_kwargs))

                    last_box_handle = box.handle
                    # noinspection PyTypeChecker
                    path = TikZDraw(TikZPathList(
                        top_box.get_anchor_point("south"), "--", box.get_anchor_point("north")
                    ))
                    forest.append(box)
                    forest.append(path)
    document.append(VerticalSpace("2cm"))
    return document


def generate_deliverables(schema: PLDSchema, locale: LocaleDictionary, document: Document) -> Document:
    with document.create(MiniPage()) as minipage:
        minipage: MiniPage
        with minipage.create(Section(title=locale.deliverable_map)) as section:
            section: Section

            for deliverable in schema.deliverables:
                with section.create(Subsection(title=locale.deliverable_map)) as subsection:
                    subsection: Subsection
                    subsets_length = len(deliverable.subsets)
                    tabular_length = subsets_length if subsets_length != 0 else 1
                    table_spec = f"|{'|'.join(['X'] * tabular_length)}|"
                    with subsection.create(Tabularx(table_spec=table_spec, row_height="1.4")) as tabularx:
                        tabularx: Tabularx
                        tabularx.add_row([MultiColumn(tabular_length, data=deliverable.name, color="gray")])

                        tabularx_contents: List[List[str]] = [[f"{subset_index} {subset.name}"] + [
                            f"{subset_index}.{user_story_index} {user_story.name}" for user_story_index, user_story in
                            enumerate(subset.user_stories, start=1)
                        ] for subset_index, subset in enumerate(deliverable.subsets, start=1)]
                        max_size = max([len(content) for content in tabularx_contents])
                        tabularx_contents: List[List[str]] = [content + ["" for _ in range(len(content), max_size)] for
                                                              content in tabularx_contents]
                        for row_contents in zip(*tabularx_contents):
                            tabularx.add_row([row_content for row_content in row_contents])
    return document


def generate_user_story(user_story: UserStory, locale: LocaleDictionary, subsubsection: Subsubsection) -> Subsubsection:
    with subsubsection.create(Tabularx(table_spec="|X|X|", row_height="1.4")) as tabularx:
        tabularx: Tabularx

        definitions_of_done = Itemize()
        for definition_of_done in user_story.definitions_of_done:
            definitions_of_done.add_item(definition_of_done)
        comments = Itemize()
        for comment in user_story.comments:
            comments.add_item(comment)

        tabularx.add_row([MultiColumn(2, data=bold(user_story.name), color="gray")])
        tabularx.add_row([f"{locale.as_user}: ", f"{locale.user_want}: "])
        tabularx.add_row([user_story.user, user_story.action])
        tabularx.add_row([MultiColumn(2, align="l", data=[f"{locale.description}: ",
                                                          user_story.description or ""], color="gray")])
        tabularx.add_row([MultiColumn(2, align=NoEscape("|p{\\rowWidth}|"), data=[f"{locale.definition_of_done}: ",
                                                                                  definitions_of_done])])
        tabularx.add_row([MultiColumn(2, align="l", data=[f"{locale.assignation}: ",
                                                          ", ".join(user_story.assignments)], color="gray")])
        tabularx.add_row([f"{locale.estimated_duration}: ",
                          f"{user_story.estimated_duration} {locale.man_days} ({int(user_story.estimated_duration * 8)}"
                          f" {locale.hours})"])
        tabularx.add_row([f"{locale.status}: ",
                          user_story.status.translate(locale)])
        tabularx.add_row([MultiColumn(2, align=NoEscape("|p{\\rowWidth}|"), data=[f"{locale.comments}: ",
                                                                                  comments], color="gray")])
    return subsubsection


def generate_user_stories(schema: PLDSchema, locale: LocaleDictionary, document: Document) -> Document:
    document.append(NewPage())

    with document.create(MiniPage()) as minipage:
        minipage: MiniPage

        for deliverable in schema.deliverables:
            with minipage.create(Section(title=deliverable.name)) as section:
                section: Section
                if deliverable.description is not None:
                    section.append(MediumText(data=deliverable.description))
                for subset in deliverable.subsets:
                    with section.create(Subsection(title=subset.name)) as subsection:
                        section: Subsection
                        if subset.description is not None:
                            subsection.append(MediumText(data=subset.description))
                        for user_story in subset.user_stories:
                            with subsection.create(Subsubsection(title=user_story.name)) as subsubsection:
                                subsubsection: Subsubsection
                                generate_user_story(user_story, locale, subsubsection)
    return document


def get_unix_timestamp_from_version(version: Version) -> float:
    return datetime.datetime.timestamp(datetime.datetime(version.date.year, version.date.month, version.date.day))


def generate_pld(schema: PLDSchema, locale: LocaleDictionary) -> Document:
    document = Document(f"PLD {datetime.date.today().year} - {schema.title}",
                        geometry_options={"left": "20mm", "top": "20mm"},
                        documentclass=Command("documentclass", arguments=["extarticle"],
                                              options=["a4paper", "12pt", "table"]),
                        fontenc="T1", inputenc="utf8", page_numbers=True)
    schema.versions = sorted(schema.versions, key=get_unix_timestamp_from_version)
    generate_dependencies(document)
    generate_options(document)
    generate_style(schema, locale, document)

    generate_first_page(schema, document)
    generate_document_description(schema, locale, document)
    generate_document_versions_table(schema, locale, document)
    generate_toc(locale, document)
    generate_organigram(schema, locale, document)
    generate_deliverables(schema, locale, document)
    generate_user_stories(schema, locale, document)
    generate_work_report_page(schema, locale, document)
    return document
