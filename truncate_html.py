import os
import time
from docx import Document

def truncate():
    title = "SL"
    series_folder_path = f".\\books\\{title}"
    html_folder_path = os.path.join(series_folder_path, "html")
    files = os.listdir(html_folder_path)
    
    all_raw_folder_path = os.path.join(series_folder_path, "all_raw")
    chaps = []
    for ch in files[:]:
        if ("~$" not in ch) and (ch != ".git") and (".html" in ch):
            chaps.append(ch)
    # print(chaps)
    # return
    for ch in chaps:
        filename = os.path.join(html_folder_path, ch)
        with open(filename, "r", encoding="utf-8") as file:
            content = file.readlines()
        ch_title = f"<h1>{content[8].split('"')[3]}</h1>"

        for i, line in enumerate(content):
            if "<p>" in line:
                break
        filtered = [ch_title] + content[i-5:]

        for i, line in enumerate(filtered):
            if "</div>" in line:
                break
        filtered = filtered[:i+5]
        
        # for i in range(len(content)-1, -1):
        #         if "</div" in content[i]:
        #             last = i + 2
        #             break

        filtered = "\n".join(filtered).split("<p>")
        filtered = "\n<p>".join(filtered)
        # print(ch_title)
        # print(content)
        # print()
        # with open(filename, "w", encoding="utf-8") as file:
        #     file.write(content)
        document = Document()
        document.add_paragraph(filtered)
        
        doc_file = f"{ch.split(".")[0]}.docx"
        document.save(f"{all_raw_folder_path}\\{doc_file}")
        if doc_file in os.listdir(all_raw_folder_path):
            print(f"[*] Successful truncation - {ch} >> {doc_file}")
        else:
            print(f"[!] Unsuccessful truncation - {ch}")


if __name__ == "__main__":
    os.system("cls")
    print("="*50)
    print("[*] Truncating html files ...")
    print("="*50)
    prev = time.time()
    truncate()
    curr = time.time()
    elapsed = curr - prev
    print("="*50)
    print(f"Elapsed time is {elapsed}s")
    print("="*50)