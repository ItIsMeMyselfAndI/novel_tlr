from docx import Document
from ebooklib import epub
import os
import time
import winsound


def createBookOBJ(book_title):
    book = epub.EpubBook()
    book.set_identifier(f"id_101")
    book.set_title(book_title)
    book.set_language("en")
    book.add_author("Daul")
    book.add_author("phan2m", uid="translator")
    return book


def createChaps(tl_folder):
    chaps = {}
    filenames = [ch for ch in os.listdir(tl_folder) if ("~$" not in ch) and (ch != ".git")]
    for f in filenames:
        docx_path = os.path.join(tl_folder, f)
        content = []
        # paragraphs 
        text = [p.text for p in Document(docx_path).paragraphs]
        for t in text:
            content += t.split("\n")
        content = "\n".join([f"<p>{p}</p>" for p in content[:]]).split("**")
        # bolds
        for i, text in enumerate(content[:]):
            if i != 2:
                content[i] = f"<b>{text}</b>"
        # italics
        content = "".join(content).split("*")
        for i, text in enumerate(content[:]):
            if i != 2:
                content[i] = f"<i>{text}</i>"
        # create obj 
        content = "".join(content)
        title = f.split(".")[0]
        ch = epub.EpubHtml(title=title, file_name=f"{title}.xhtml", lang="en")
        ch.content = content
        chaps[title] = ch
    return chaps


def createTableOfContents(book, chaps):
    toc = []
    for i, title in enumerate(chaps.keys()):
        toc.append(
            epub.Link(f"{title}.xhtml", title, f"ch_{i:5>0}")
        )
    book.toc = tuple(toc)


def addDefaults(book, chaps):
    # add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    # add spine (order of content)
    book.spine = ['nav']
    for obj in chaps.values():
        book.spine.append(obj)


def createEpubFile(book, book_folder, book_title):
    os.makedirs(book_folder, exist_ok=True)
    book_folder = os.path.abspath(book_folder)
    book_path = os.path.join(book_folder, f"{book_title}.epub")

    epub.write_epub(book_path, book, {})
    
    if os.path.exists(book_path):
        print(f"[*] Successful creation - {book_title}.epub")
    else:
        print(f"[!] Unsuccessful creation - {book_title}.epub")


def main():
    prev = time.time()
    os.system("cls")
    print("="*50)
    print("[*] Creating Epub file ...")
    print("="*50)
    
    tl_folder = os.path.abspath(".\\tl")

    book_title = "Solo Leveling - Ragnarok"
    book = createBookOBJ(book_title)

    chaps = createChaps(tl_folder)
    for obj in chaps.values():
        book.add_item(obj)

    createTableOfContents(book, chaps)
    addDefaults(book, chaps)

    book_folder = os.path.join(".\\books")
    createEpubFile(book, book_folder, book_title)
    
    curr = time.time()
    elapsed = curr - prev
    print("="*50)
    print(f"[*] Elapsed time is {elapsed}")
    print(f"[*] Output path is '{book_folder}'")
    print("="*50)


if __name__ == "__main__":
    main()
    for i in range(3):
        winsound.Beep(1000, int(0.5*1000)) # hz, ms
        time.sleep(0.3)
    