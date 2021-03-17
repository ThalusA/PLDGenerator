def adapt_content(content: list = []) -> list:
    content_len = len(content)
    cut_at_each = 6
    for i in range(content_len):
        string_len = len(content[i])
        if string_len > cut_at_each:
            last_space = 0
            next_space = string_len
            j = 0
            while j < string_len:
                if content[i][j] == ' ': 
                    last_space = j
                    for k in range(j, string_len):
                        if content[i][k] == ' ':
                            next_space = k
                            break
                    else:
                        next_space = string_len
                else:
                    if j != 0 and j % cut_at_each == 0 and content[i][j] != '\\':
                        if next_space != string_len and content[i][next_space] != '\\' and abs(next_space - j) < abs(j - last_space):
                            content[i] = content[i][:next_space] + "\\\\" + content[i][next_space + 1:]
                            string_len = len(content[i])
                        elif last_space != 0 and content[i][last_space] != '\\' and abs(next_space - j) >= abs(j - last_space):
                            content[i] = content[i][:last_space] + "\\\\" + content[i][last_space + 1:]
                            string_len = len(content[i])
                j += 1
    return content


def depth_to_string(depth: list = []):
    return '.'.join(map(str, depth)) + ' '


def escape_str(string: str) -> str:
    return string.replace("\\", "\\textbackslash").replace("&", "\\&").replace("%", "\\%").replace("$", "\\$").replace("#", "\\#").replace("_", "\\_").replace("{", "\\{").replace("}", "\\}").replace("~", "\\textasciitilde").replace("^", "\\textasciicircum")