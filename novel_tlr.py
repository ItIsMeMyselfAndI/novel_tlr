from docx import Document
import json
import os
import requests
import sys
import time
import winsound


def displayFooter():
    print("="*50)
    print("[*] Wait for a few moments ...")
    print("="*50)
    time.sleep(3)


def getFolderPaths():
    os.system("cls")
    print("="*50)
    while True:
        print("[*] Enter absolute folder path of the raw chapter(s):")
        raw_folder_path = os.path.abspath(input("\t>> "))
        if  not os.path.isdir(raw_folder_path):
            print("[!] Error: Folder path does not exist.")
            continue
        break
    print("[*] Enter absolute folder path to store the translated chapter(s):")
    tl_folder_path = os.path.abspath(input("\t>> ").strip())
    os.makedirs(tl_folder_path, exist_ok=True)
    displayFooter()
    return raw_folder_path, tl_folder_path


def getAISpecs(specs_file="specs.json"):
    try:
        with open(specs_file, "r", encoding="utf-8") as file:
            specs = json.load(file)
    except json.decoder.JSONDecodeError:
        specs = {
            "in_lang": "{auto}",
            "out_lang": "{english}",
            "instruction": "{None}",
            "context" : "{None}",
            "retries": 100
        }

    while True:
        choice = _getMenuChoice()
        if choice == '1': break
        if choice == '2': specs["in_lang"], specs["out_lang"] = _getLanguages()
        elif choice == '3': specs["instruction"] = _getInstruction()
        elif choice == '4': specs["context"] = _rmNewLine(_getContext())
        elif choice == '5': specs["retries"] = _getNumOfRetries()
        elif choice == 'q':
            print("[*] Exiting program ...")
            print("="*50)
            time.sleep(3)
            sys.exit()

    with open(specs_file, "w", encoding="utf-8") as file:
        json.dump(specs, file, indent=4, ensure_ascii=False)

    role = f"You are a professional novel translator of {specs["in_lang"]} to {specs["out_lang"]}."
    confirmation = (
        f"Understood. I will strictly follow this instructions: {specs["instruction"]}.\n"
        f"Then, I will cross-check the {specs["out_lang"]} translation and spelling of the names, "
        f"genders, titles, skills, and other keywords based from this context: {specs["context"]}."
    )
    messages = [
        {"role":"system", "content":role},
        {"role":"user", "content":"Translate something for me."},
        {"role":"assistant", "content": confirmation},
        {"role":"user", "content":""}
    ]
    return messages, specs["retries"]

def _getMenuChoice():
    while True:
        os.system("cls")
        print("="*50)
        print("[*] Menu")
        print("="*50)
        lines = (
            "\t1 - Proceed translating\n"
            "\t2 - Change input/output languages\n"
            "\t3 - Change instruction content\n"
            "\t4 - Change context/settings\n"
            "\t5 - Change number of re-tries\n"
            "\tq - Exit program"
        )
        print(lines)
        print("="*50)
        choice = input("[*] Enter menu choice (1-4): ")
        if choice in ['1', '2', '3', '4', '5', 'q']:
            print("="*50)
            return choice

def _getLanguages():
    os.system("cls")
    print("="*50)
    in_lang = input("[*] Enter input Language: ").strip()
    out_lang = input("[*] Enter output Language: ").strip()
    displayFooter()
    return '['+in_lang+']', '['+out_lang+']'

def _getInstruction():
    os.system("cls")
    print("="*50)
    print("[*] Enter the instruction for guiding the Translator.")
    print("[*] Press {Enter} >> {Ctrl + Z} >> {Enter} in order once done.")
    print("="*50)
    instruction = sys.stdin.read().strip()
    displayFooter()
    return '['+instruction+']'

def _getContext():
    os.system("cls")
    print("="*50)
    print("[*] Enter the context/settings for the Translation.")
    print("[*] Press {Enter} >> {Ctrl + Z} >> {Enter} in order once done.")
    print("="*50)
    context = sys.stdin.read().strip()
    displayFooter()
    return '['+context+']'

def _getNumOfRetries():
    os.system("cls")
    print("="*50)
    while True:
        try:
            print("[*] Enter number of re-tries for translation failure of each chapter.")
            print("[*] Enter '0' if you don't want to re-try any translation failure.")
            retries = int(float(input("\t>> "))).strip()
        except ValueError:
            print("[!] Error: Invalid input. Only enter an integer.")
            continue
        displayFooter()
        return retries

def _rmNewLine(text):
    text_list = text.split("\n")
    new_text = ""
    for elem in text_list:
        if elem == "":
            continue
        new_text += elem
        if elem[-1] != " ":
            new_text += " "
    return new_text


def getFileNames(raw_folder_path):
    files = os.listdir(raw_folder_path)
    file_names = []
    for chap in files[:]:
        if ("~$" not in chap) and (chap != ".git"):
            file_names.append(chap)
    return file_names


def getChaps(raw_folder_path, file_names):
    chaps = {}
    for chap in file_names:
        i = chap.index(".")
        document = Document(f"{raw_folder_path}\\{chap}")
        content = "\n".join([p.text for p in document.paragraphs])
        chaps[chap[:i]] = content
    return chaps


def getTranslation(chap, messages, content, retries):
    url="https://openrouter.ai/api/v1/chat/completions"
    # key = "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"
    # model = "deepseek/deepseek-r1:free"
    key = "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"
    model="deepseek/deepseek-chat:free"

    messages[3]["content"] = f"translate this:\n{content}"
    for _ in range(retries + 1):
        response = requests.post(
            url=url,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": model,
                "messages": messages
            })
        )
        response_json = response.json()
        if "choices" in response_json.keys():
            chap_translation = response_json["choices"][0]["message"]["content"]
            if "**CHAPTER END**" in chap_translation:
                print(f"[*] Successful translation - {chap}")
                _displayUsageInfo(response_json)
                return chap_translation
            print(f"[!] Error: Incomplete extraction - {chap} >> Restarting ...")
        else:
            print(f"[!] Error: No response - {chap} >> Restarting ...")
        _displayUsageInfo(response_json["usage"])

def _displayUsageInfo(response_json):
    usage = response_json.get("usage", {})
    completion = usage.get("completion_tokens_details", {})
    info = (
        f"\tPrompt tokens: {usage.get("prompt_tokens")}\n"
        f"\tCompletion tokens: {usage.get("completion_tokens", 0)}\n"
        f"\t\tReasoning tokens: {completion.get("reasoning_tokens", 0)}\n"
        f"\t\tAccepted prediction tokens: {completion.get("accepted_prediction_tokens", 0)}\n"
        f"\t\tRejected Prediction tokens: {completion.get("rejected_prediction_tokens", 0)}\n"
        f"\tTotal tokens: {usage.get("total_tokens")}"
    )
    print(info)


def saveChap(text, folder_path, file_name):
    document = Document()
    document.add_heading(file_name)
    document.add_paragraph(text)
    document.save(f"{folder_path}\\{file_name}.docx")


def main():
    raw_folder_path, tl_folder_path = getFolderPaths()
    messages, retries = getAISpecs()
    file_names = getFileNames(raw_folder_path)
    if not file_names:
        os.system("cls")
        print("="*50)
        print("[!] Error: Folder containing the raw chapters is empty")
        print("[*] Exiting the program ...")
        print("="*50)
        time.sleep(3)
        return

    chaps = getChaps(raw_folder_path, file_names)

    prev = time.time()
    os.system("cls")
    
    print("="*50)
    print("[*] Results")
    print("="*50)
   
    for chap in chaps.keys():
        chap_translation = getTranslation(chap, messages, chaps[chap], retries)
        if chap_translation in ["", None]:
            print(f"[!] Unsuccessful extraction - {chap}")
            continue
        saveChap(chap_translation, tl_folder_path, chap)
  
    curr = time.time()
    elapsed = curr - prev

    print("="*50)
    print(f"[*] Elapsed time is {elapsed}")
    print(f"[*] Output path is '{tl_folder_path}'")
    print("="*50)

            
if __name__ == "__main__":
    main()
    winsound.Beep(1000, 1*1000) # hz, ms
