import json
import os
import requests
import sys
import time
from docx import Document

def displayFooter():
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
    tl_folder_path = os.path.abspath(input("\t>> "))
    os.makedirs(tl_folder_path, exist_ok=True)
    print("="*50)
    displayFooter()
    return raw_folder_path, tl_folder_path


def getChoice():
    os.system("cls")
    print("="*50)
    print("[*] Do you want to update the translator specification?")
    print("="*50)
    while True:
        print("[*] Enter 'y' if yes, or 'n' if no:")
        choice = input("\t>> ").lower()
        print("="*50)
        if choice in ['y', 'n']:
            displayFooter
            return choice


def getAISpecs(choice, specs_file="specs.json"):
    with open(specs_file, "r", encoding="utf-8") as file:
        specs = json.load(file)

    if choice == 'y':
            specs["in_lang"], specs["out_lang"] = _getLanguages()
            specs["instruction"] = _getInstruction()
            specs["context"] = _getContext()
            specs["retries"] = _getNumOfRetries()
            with open(specs_file, "w", encoding="utf-8") as file:
                json.dump(specs, file, indent=4, ensure_ascii=False)
    
    messages = []
    messages.append(
        {"role": "system", "content": f"you are a professional novel translator of {specs["in_lang"]} to {specs["out_lang"]}"}
    )
    messages.append(
        {"role": "assistant", 
        "content": f"Understood. I will follow this instruction: {specs["instruction"]}\nAnd I will base my translation from this context: {specs["context"]}"}
    )
    return messages, specs["retries"]

def _getLanguages():
    os.system("cls")
    print("="*50)
    in_lang = input("[*] Enter input Language: ")
    out_lang = input("[*] Enter output Language: ")
    print("="*50)
    displayFooter()
    return in_lang, out_lang

def _getInstruction():
    os.system("cls")
    print("="*50)
    print("[*] Enter the instruction for guiding the Translator.")
    print("[*] Press {Enter} >> {Ctrl + Z} >> {Enter} in order once done.")
    print("="*50)
    instruction = sys.stdin.read().strip()
    print("="*50)
    displayFooter()
    return '{' + instruction + '}'

def _getContext():
    os.system("cls")
    print("="*50)
    print("[*] Enter the context/settings for the Translation.")
    print("[*] Press {Enter} >> {Ctrl + Z} >> {Enter} in order once done.")
    print("="*50)
    context = sys.stdin.read().strip()
    print("="*50)
    displayFooter()
    return '{' + context + '}'

def _getNumOfRetries():
    os.system("cls")
    print("="*50)
    while True:
        try:
            print("[*] Enter number of re-tries for translation failure of each chapter.")
            print("[*] Enter '0' if you don't want to re-try any translation failure.")
            retries = int(float(input("\t>> ")))
        except ValueError:
            print("[!] Error: Invalid input. Only enter an integer.")
            continue
        print("="*50)
        displayFooter()
        return retries


def getFileNames(raw_folder_path):
    files = os.listdir(raw_folder_path)
    file_names = []
    for name in files[:]:
        if ("~$" not in name) and (name != ".git"):
            file_names.append(name)
    return file_names


def getChaps(raw_folder_path, file_names):
    chaps = {}
    for name in file_names:
        i = name.index(".")
        document = Document(f"{raw_folder_path}\\{name}")
        content = "\n".join([p.text for p in document.paragraphs])
        chaps[name[:i]] = content
    return chaps


def getTranslation(url, key, model, messages, content):
    messages_cp = messages[:]
    messages_cp.append({"role": "user", "content" : f"translate this:\n{content}"})
    response = requests.post(
        url=url,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": model,
            "messages": messages_cp
        })
    )
    response_json = response.json()
    if "choices" in response_json.keys():
        chap_translation = response_json["choices"][0]["message"]["content"]
        return chap_translation


def saveChap(text, folder_path, file_name):
    document = Document()
    document.add_heading(file_name)
    document.add_paragraph(text)
    document.save(f"{folder_path}\\{file_name}.docx")


def main():
    url="https://openrouter.ai/api/v1/chat/completions"
    # key = "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"
    # model = "deepseek/deepseek-r1:free"
    key = "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"
    model="deepseek/deepseek-chat:free"

    raw_folder_path, tl_folder_path = getFolderPaths()
    choice = getChoice()
    messages, retries = getAISpecs(choice)
    file_names = getFileNames(raw_folder_path)
    if not file_names:
        os.system("cls")
        print("="*50)
        print("[!] Error: Folder containing the raw chapters is empty")
        print("[*] Exiting the program ...")
        print("="*50)
        return

    chaps = getChaps(raw_folder_path, file_names)

    prev = time.time()
    os.system("cls")
    
    print("="*50)
    print("[*] Results")
    print("="*50)
   
    for name in chaps.keys():
        chap_translation = getTranslation(url, key, model, messages, chaps[name])
        for i in range(retries + 1):
            if (chap_translation not in ["", None]) and ("**CHAPTER END**" in chap_translation):
                saveChap(chap_translation, tl_folder_path, name)
                print(f"[*] Successful translation - {name}")
                break
            elif (chap_translation in ["", None]):
                print(f"[!] Error: No response - {name} >> Restarting translation ...")
            else:
                print(f"[!] Error: Incomplete translation - {name} >> Restarting translation ...")
            chap_translation = getTranslation(url, key, model, messages, chaps[name])
  
    curr = time.time()
    elapsed = curr - prev

    print("="*50)
    print(f"[*] Elapsed time is {elapsed}")
    print(f"[*] Output path is '{tl_folder_path}'")
    print("="*50)
            

if __name__ == "__main__":
    main()