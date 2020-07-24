from process import *

def add_page_style(logo_path: str = "logo.svg", sublogo_path: str = "sublogo.svg") -> str:
    return f"""
\\renewcommand{{\\familydefault}}{{\\sfdefault}}
\\pagestyle{{fancy}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\fancyhf{{}}
\\lhead{{\\includesvg[width = 30pt]{{{logo_path}}}}}
\\rhead{{\\Large Project Log Document}}
\\rfoot{{Page \\thepage \\space of \\pageref{{LastPage}}}}
\\lfoot{{\\includesvg[width = 100pt]{{{sublogo_path}}}}}

\\fancypagestyle{{plain}}{{
    \\renewcommand{{\\headrulewidth}}{{0pt}}
    \\fancyhf{{}}
    \\rfoot{{Page \\thepage \\space of \\pageref{{LastPage}}}}
    \\lfoot{{\\includesvg[width = 100pt]{{{sublogo_path}}}}}
}}
"""

def add_depth_title(title: str = "", depth: int = 0, last: bool = False) -> str:
    if depth == 0: return f"\\section{{{title}}}\n"
    if depth == 1: return f"\\subsection{{{title}}}\n"
    if depth == 2: return f"\\subsubsection{{{title}}}\n"
    if depth == 3: return f"\\paragraph{{{title}}}\n" if last == False else f"\\paragraph{{{title}}}\\mbox{{}}\\\\\n"
    if depth == 4: return f"\\subparagraph{{{title}}}\n" if last == False else f"\\subparagraph{{{title}}}\\mbox{{}}\\\\\n"

def add_toc_name(name: str = "Table des matières") -> str:
    return f"\\renewcommand*\\contentsname{{{name}}}\n"

def add_document_info(title: str = "Project Log Document", date: str = "", author: str = "") -> str:
    return f"\\title{{{title}}}\n\\date{{{date}}}\n\\author{{{author}}}\n"

def setcounter(key: str, value: int) -> str:
    return f"\\setcounter{{{key}}}{{{value}}}\n"

def add_chunk(content: str = "", chunk_type: str = "") -> str:
    return f"\\begin{{chunk}}{{{chunk_type}}}\n{content}\\end{{chunk}}\n"

def add_cell_color(color: str = "", transparency: float = 0.0, content: str = "", colorization: str = "cell") -> str:
    if colorization == "cell": return f"\\cellcolor[{color}]{{{transparency}}}{content}"
    elif colorization == "row": return f"\\rowcolor[{color}]{{{transparency}}}{content}"
    else: return content

def add_multicolumn(expanded_cell: int = 1, options: str = "", content: str = "") -> str:
    return f"\\multicolumn{{{expanded_cell}}}{{{options}}}{{{content}}}"

def add_tabularx(options: str = "", content: list = [[]], table_type: str = "\\textwidth") -> str:
    final_str = f"\\begin{{tabularx}}{{{table_type}}}{{{options}}}\n"
    for row in content:
        final_str += f"\t\\hline {' & '.join(row)}\\\\\n"
    final_str += f"\t\\hline\n\\end{{tabularx}}\n"
    return final_str

def add_arraystreching(value: float = 0.0) -> str:
    return f"\\renewcommand{{\\arraystretch}}{{{value}}}\n"

def add_itemization(content: list = []) -> str:
    final_str = f"\\begin{{itemize}}\n"
    for element in content:
        final_str += f"\t\t\\item {element}\n"
    final_str += f"\t\\end{{itemize}}"
    return final_str

def add_forest(title: str = "", content: list = [], spacing: str = "15mm") -> str:
    final_str = f"\\adjustbox{{max width=\linewidth}}{'{'}\n\\begin{{forest}}\n\tfor tree={{draw, align=center, l={spacing}}},\n\t[{title}\n"
    content = adapt_content(content)
    for index, subtitle in enumerate(content):
        final_str += f"\t\t[{index + 1} {subtitle}]\n"
    final_str += f"\t]\n\\end{{forest}}{'}'}"
    return final_str

def add_content_centering(content: str = "") -> str:
    return f"\\centering\n{content}\n" 

def add_page_centered(content: str = "") -> str:
    return f"\\clearpage\n\\vspace*{{\\fill}}\n\\begin{{center}}\n{content}\\end{{center}}\n\\vfill\n\\clearpage\n"

def add_newpage(content: str = "") -> str:
    return f"\\clearpage\n{content}\n"

def add_figure(image_path: str = "logo.svg", customs_data: list = None) -> str:
    final_str = f"\\begin{{figure}}[htbp]\n\t\\centering\n\t\\includesvg{{{image_path}}}"
    if customs_data != None:
        for custom_data in customs_data:
            final_str += f"\n\t{custom_data}\n"
    final_str += f"\\end{{figure}}\n"
    return final_str

def add_shortstack(content: str = "", align: str = "l") -> str:
    if align == "l" or align == "c" or align == "r": return f"\shortstack[{align}]{{{content}}}"
    else: return content

def add_space(spacetype: str = "vertical", size: str = "") -> str:
    if spacetype == "vertical": return f"\\vspace{{{size}}}\n"
    elif spacetype == "horizontal": return f"\\hspace{{{size}}}\n"
    else: return ""

def add_style(style: str, content: str, newline: bool = True) -> str:
    if style == "bold": return f"\\textbf{{{content}}}\n" if newline == True else f"\\textbf{{{content}}}"
    elif style == "italize": return f"\\textit{{{content}}}\n" if newline == True else f"\\textit{{{content}}}"
    elif style == "underline": return f"\\underline{{{content}}}\n" if newline == True else f"\\underline{{{content}}}"
    elif style == "emphasised": return f"\\emph{{{content}}}\n" if newline == True else f"\\emph{{{content}}}"
    else: return content

def add_size(size: str = "normalsize", content: str = "") -> str:
    return f"\\{size} {content}"

def add_geometry_options(options: object) -> str:
    final_str = "\\geometry{"
    for key, value in options.items():
        final_str += f"{key}," if value == None else f"{key}={value},"
    final_str += "}\n"
    return final_str

def add_chunk_environ() -> str:
    return """
\\raggedbottom
\\newlength\\chunktotheight
\\NewEnviron{chunk}[1]{
    \\settototalheight{\\chunktotheight}{
        \\begin{minipage}{\\textwidth}
        \\BODY
        \\end{minipage}
    }
    \\ifdim\\chunktotheight>\\textheight
    \\else
    \\needspace{\\chunktotheight}
    \\fi
    \\def\\temp{#1}\\ifx\\temp\\empty\\else
        \\addtocounter{#1}{-1}
    \\fi
    \\BODY
}{}
"""

def add_wrapper(typename: str = "", content: str = "") -> str:
    return f"\\begin{{{typename}}}\n{content}\\end{{{typename}}}\n"

def add_new_command(name: str = "", expr: str = "") -> str:
    return f"\\newcommand{{{name}}}{{{expr}}}\n"

def add_document_class(document_type: str = "article", document_options: str = "") -> str:
    return f"\\documentclass{{{document_type}}}\n" if document_options == "" else f"\\documentclass[{document_options}]{{{document_type}}}\n"

def add_tikz_library(library_type: str = "fit") -> str:
    return f"\\usetikzlibrary{{{library_type}}}\n"

def add_package(package_name, options: str = None) -> str:
    return f"\\usepackage{{{package_name}}}\n" if options == None else f"\\usepackage[{options}]{{{package_name}}}\n"