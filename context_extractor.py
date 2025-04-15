from docx import Document
import requests
import json
import os
import time
import winsound


def getContextsList(series_folder):
    context_file_1 = os.path.join(series_folder, "context_1.txt")
    context_file_2 = os.path.join(series_folder, "context_2.txt")
    context_files = [context_file_1, context_file_2]
    contexts_list = [] 
    for c_file in context_files:
        with open(context_file_1, "r", encoding="utf-8") as file:
            c = file.read().strip()
        contexts_list.append(c)
    return [f.split("\\")[-1].split(".")[0] for f in context_files], contexts_list


def extractContext(messages, ch, i, context_file):
    url="https://openrouter.ai/api/v1/chat/completions"
    # key = "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"
    key = "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"
    # key = "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"
    # key = "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"
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
        response_json = response.json()
        usage = response_json.get("usage", {})
        extracted = ""
        if "choices" in response_json.keys():
            extracted = response_json["choices"][0]["message"]["content"].strip()
            if "- End: \"End\"" in extracted:
                print(f"[*] Successful extraction - {ch} [{context_file}: {i}]")
                winsound.Beep(1000, 1*1000) # hz, ms
                return f"### Chapter {ch} [{context_file}: {i}]\n{extracted}", usage
            print(f"[!] Error: Incomplete extraction - {ch} [{context_file}: {i}] >> Restarting ...")
        else:
            print(f"[!] Error: No response - {ch} [{context_file}: {i}] >> Restarting ...")
        winsound.Beep(1000, int(1.5*1000)) # hz, ms
    return None, usage 


def getMessages(context, in_lang, out_lang):
    sys_role = f"You are an expert reader and context writer of both {in_lang} and {out_lang}."
    
    with open("extractor_instruction.txt", "r")as file:
        instruction = file.read()
    
    with open("extractor_confirmation.txt", "r")as file:
        confirmation = f"Understood. I will use this context as a guide - Context/Dictionary:\n[\n{context}\n]\n"
        confirmation += file.read()
    
    messages = [
        {"role":"system", "content":sys_role},
        {"role":"user", "content":instruction},
        {"role":"assistant", "content":confirmation},
        {"role":"user", "content":""} # context
    ]
    return messages


def appendContextNonRepeats(ch_contexts, new_context):
    lines = new_context.split("- ")
    for line in lines:
        existing = [key.split(":")[0] for key in ch_contexts]
        if (line.split(":")[0] not in existing) or ("End" in line) or ("####" in line):
            ch_contexts.append(line)
            # print(line, end="")


def displayUsageInfo(usage):
    # completion = usage.get("completion_tokens_details", {})
    info = (
        f"{"":>4}>> Prompt: {usage.get("prompt_tokens"):<8}"
        f"Output: {usage.get("completion_tokens", 0):<8}"
        # f"\t\tReasoning tokens: {completion.get("reasoning_tokens", 0)}\n"
        # f"\t\tAccepted prediction tokens: {completion.get("accepted_prediction_tokens", 0)}\n"
        # f"\t\tRejected Prediction tokens: {completion.get("rejected_prediction_tokens", 0)}\n"
        f"Total: {usage.get("total_tokens")}"
    )
    print(info)


def main():
    title = "SL"
    in_lang, out_lang = "hangul", "english"

    series_folder = f".\\books\\{title}"
    raw_folder = os.path.join(series_folder, "raw1")
    
    ch_dictionary_file = os.path.join(series_folder, "ch_dictionary.txt")
    
    files = os.listdir(raw_folder)
    chaps = []
    for chap in files[:]:
        if ("~$" not in chap) and (chap != ".git"):
            chaps.append(chap.split(".")[0])

    context_files, contexts_list = getContextsList(series_folder)
    for ch in chaps:
        print()
        ch_contexts = []

        for i, context in enumerate(contexts_list):
            messages = getMessages(context, in_lang, out_lang)  
            document = Document(os.path.join(raw_folder, f"{ch}.docx"))
            text = "\n".join([p.text for p in document.paragraphs])
            # print(len(text))
            one, two, three, four = len(text)//5, len(text)//5 * 2, len(text)//5 * 3, len(text)//5 * 4
            text_list = [text[:one], text[one:two], text[two:three], text[three:four], text[four:]]
            # print(len(text_list[0]) + len(text_list[1]) + len(text_list[2]) + len(text_list[3]))
            # print(len(text_list[0]), len(text_list[1]), len(text_list[2]), len(text_list[3]), len(text_list[4]))

            new_context = ""
            for j, text in enumerate(text_list):
                messages[3]["content"] = f"{in_lang.upper()} text:\n\n{text}"
                extracted, usage = extractContext(messages, ch, j, context_files[i])
                if extracted in ["", None]:
                    print(f"[!] Unsuccessful extraction - {ch} [{context_files[i]}: {j}]")
                    continue
                new_context += f"\n\n{extracted}"
                displayUsageInfo(usage)
            print()
            appendContextNonRepeats(ch_contexts, new_context)
        
        # update context file
        ch_contexts = "\n\n---" + "- ".join(ch_contexts)
        with open(ch_dictionary_file, "a", encoding="utf-8") as file:
            file.write(ch_contexts)
        time.sleep(0.5)
        print("-"*50)

    # alarm
    for i in range(3):
        winsound.Beep(1000, int(0.5*1000))
        time.sleep(0.3)
    return ch_dictionary_file


if __name__ == "__main__":
    os.system("cls")
    prev = time.time()
    print("="*50)
    print("[*] Extracting new context ...")
    print("="*50)
    
    out_path = main()
    
    print("="*50)
    curr = time.time()
    elapsed = curr - prev
    print(f"[*] Elapsed time is {elapsed}s")
    print(f"[*] Output path is '{out_path}'")
    print("="*50)

    