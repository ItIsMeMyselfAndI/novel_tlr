import os


def add_context(file_path, new):
    with open(file_path, "r", encoding="utf-8") as file:
        context = file.readlines()

    for i, c in enumerate(context):
        if "Chapter" in c:
            context[i] = f"{c}- {new}\n"

    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(context)


def truncate_context(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        context = file.readlines()#

    for i, line in enumerate(context):
        context[i] = line.split(":")[0] + "\n"

    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(context)


def reformat(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        context = file.read()

    context = context.replace("\n- ", " ; ", -1)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(context)
    print(context)


if __name__ == "__main__":
    title = "SL"
    series_folder = f".\\books\\{title}"
    file_path = os.path.join(series_folder, "ch_dictionary.txt")
    # new = "성수호: \"Sung Suho\" (male)"
    # new = "소군주님: \"Young Monarch\" (refers only to Suho)"
    # new = "일어나라: \"Arise\""
    # new = "생기다: \"Arise\""
    new = "입수 난이도: \"Acquisition Difficulty\""
    
    i = 9
    # i = 3
    if i == 0:
        add_context(file_path, new)
    elif i == 1:
        truncate_context(file_path)
    elif i == 2:
        reformat(file_path)