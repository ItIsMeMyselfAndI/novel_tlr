from docx import Document
import requests
import json
import os
import time
import winsound

def extractContext(messages, chap):
    url="https://openrouter.ai/api/v1/chat/completions"
    # key = "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"
    # key = "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"
    key = "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"
    model="deepseek/deepseek-chat:free"
        
    for _ in range(10):
        response = requests.post(
            url = url,
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            data = json.dumps({
                "model": model,
                "messages": messages
            })
        )
        new_context = ""
        response_json = response.json()
        if "choices" in response_json.keys():
            new_context = response_json["choices"][0]["message"]["content"].strip()
            if ('{' in new_context) and '}' in new_context:
                print(f"[*] Successful extraction - {chap}")
                _displayUsageInfo(response_json)
                winsound.Beep(1000, 1*1000) # hz, ms
                return f"Chapter {chap}: {new_context}"
            print(f"[!] Error: Incomplete extraction - {chap} >> Restarting ...")
        else:
            print(f"[!] Error: No response - {chap} >> Restarting ...")
        _displayUsageInfo(response_json)


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


def main():
    os.system("cls")
    prev = time.time()
    print("="*50)
    print("[*] Extracting new context ...")
    print("="*50)
    
    in_lang, out_lang = "hangul", "english"
    raw_folder_path = ".\\raw"
    context_file = "context.txt"
    
    files = os.listdir(raw_folder_path)
    chaps = []
    for chap in files[:]:
        if ("~$" not in chap) and (chap != ".git"):
            chaps.append(chap.split(".")[0])
    
    sys_role = f"You are an expert reader and context writer of both {in_lang} and {out_lang}."
    instruction = f"I want you to extract new nouns that don't exist in the {in_lang} text that I will give you by cross-checking the context/dictionary you've previously created."
    
    with open(context_file, "r", encoding="utf-8") as file:
        context = file.read().strip()
    
    confirmation = (
        f"Understood. I will extract only the relevant nouns to the context that doesn't exist in this dictionary:\n"
        f"[\n{context}\n]\n"
        f"Then, I will translate it to {out_lang} and will only respond strictly with this format display, nothing else:\n"
        "\t{\"hangul1\" – \"english1\". \"hangul2\" – \"english2\" \"hangul3\" – \"english3\".};\n"
        "However, if there's no new noun, I will just display:\n"
        "\t{None};\n"
        "For name (unique/personal identity)  only, add male or female to it. Example:\n"
        "\t\"hangul3\" – \"english3\", male"
    )
    messages = [
        {"role":"system", "content":sys_role},
        {"role":"user", "content":instruction},
        {"role":"assistant", "content":confirmation},
        {"role":"user", "content":""}
    ]
    
    extracted_context = context
    for i in chaps:
        document = Document(os.path.join(raw_folder_path, f"{i}.docx"))
        text = "\n".join([p.text for p in document.paragraphs])
        messages[3]["content"] = f"{in_lang.upper()} text:\n\n{text}"
        new_context = extractContext(messages, i)

        if new_context in ["", None]:
            print(f"[!] Unsuccessful extraction - {i}")
            continue

        extracted_context += f"\n\n{new_context}"
        confirmation = f"{confirmation[:-1]} {new_context}]"
        messages[2]["content"] = confirmation

        # update context file
        with open(context_file, "w", encoding="utf-8") as file:
            file.write(extracted_context)
        # update context in memory
        with open(context_file, "r", encoding="utf-8") as file:
            context = file.read().strip()

    print("="*50)
    curr = time.time()
    elapsed = curr - prev
    print(f"[*] Elapsed time is {elapsed}")
    print("="*50)


if __name__ == "__main__":
    main()
    for i in range(3):
        winsound.Beep(1000, int(0.5*1000))
        time.sleep(0.5)

    