from bs4 import BeautifulSoup
from docx import Document
import requests
import os

# URL of the webpage
# os.system("cls")
# print("=" * 50)
# print("Enter the URL of the webpage:")
# page_url = input("\t>> ")
# print("What is your starting chapter number?")
# chap_lower = int(float(input("\tEnter integer: ")))
# print("What is your ending chapter number?")
# chap_upper = int(float(input("\tEnter integer: ")))
# print("How many lines from the top of the page do you want to exclude? ")
# page_lower = int(float(input("\tEnter integer: ")))
# print("How many lines from the bottom of the page do you want to exclude? ")
# page_upper = int(float(input("\tEnter integer: "))) * -1
# print("Enter the folder path where you want to store the output(s):")
# path = input("\t>> ")
# print("=" * 50)
# print("[*] Connecting to the webpage...")
# print("=" * 50)

title = "SL"
series_folder_path = f".\\books\\{title}"
all_raw_folder_path = os.path.join(series_folder_path, "all_raw")
os.makedirs(all_raw_folder_path, exist_ok=True)

page_url = f"https://www.fortuneeternal.com/novel/solo-leveling-ragnarok-raw-novel/chapter-"
chap_lower = 169
chap_upper = 308
page_lower = 728
page_upper = -382

for i in range(chap_lower, chap_upper + 1):
    # edit this part for specific websites
    chap_url = f"{page_url}{i}/"

    # get the page content
    response = requests.get(chap_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # extract all text from the page
        page = soup.get_text()
        page = page.split("\n")
        if page_upper == 0:
            text = [line for line in page if line != ""][page_lower:]
        else:
            text = [line for line in page if line != ""][page_lower:page_upper]
        output = os.path.join(all_raw_folder_path, f"{i-1}.docx")
        document = Document()
        for line in text:
            document.add_paragraph(line)
        document.save(output)
        print(f"[*] Copied [Chapter {i-1}] successfully.")

    else:
        print(f"[*] Failed to retrieve the page. Status code: {response.status_code}")
        print("\t>> You might want to modify the script or the URL is invalid.")
