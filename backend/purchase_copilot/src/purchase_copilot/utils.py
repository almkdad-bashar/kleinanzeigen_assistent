from PIL import Image
import pytesseract
from playwright.async_api import async_playwright


def extract_text_from_image(path:str) -> str:
        image = Image.open(path)
        text = pytesseract.image_to_string(image)
        return text


async def take_screenshot(url, output_path="screenshot.png"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']  # Important for some environments
        )
        page = await browser.new_page()
        # Set a reasonable timeout and user agent
        await page.goto(url, timeout=60000)
        await page.screenshot(path=output_path, full_page=True)
        await browser.close()
        return output_path

def read_file(path):
     with open(path) as f:
        return str(f.read())

def write_file(content, path='output.txt'):
    with open(path, 'w') as file:
        file.writelines(content)

def trim(content:str):
    remove_after_list = [
        'Das könnte dich auch interessieren',
        'Andere Anzeigen des Anbieters',
        'Alle Anzeigen des Anbieters'
    ]
    for phrase in remove_after_list:
        index = content.find(phrase)
        if index != -1:  # Found the phrase
            return content[:index].strip()
    return content
     
def extract_item_list(text: str) -> list:
    url = "https://www.kleinanzeigen.de/s-anzeige/"
    mark = 'data-href="/s-anzeige/'
    item_list = []
    mark_len = len(mark)
    
    i = 0
    while i < len(text):
        # Find the next occurrence of the mark
        mark_pos = text.find(mark, i)
        if mark_pos == -1:
            break
            
        # Find the closing quote after the mark
        quote_pos = text.find('"', mark_pos + mark_len)
        if quote_pos == -1:
            break
            
        # Extract the path and construct the full URL
        path = text[mark_pos + mark_len:quote_pos]
        full_url = url + path
        item_list.append(full_url)
        
        # Move past this match
        i = quote_pos + 1
        
    return item_list

import re

def generate_page_list(number: int, path: str):
    result = []
    match = re.search(r'seite:(\d+)/', path)
    if match:
        start = int(match.group(1))
    else:
        start = 1  # fallback if 'seite:' not found
    for i in range(start, start + number):
        page_url = re.sub(r'seite:\d+/', f'seite:{i}/', path)
        result.append(page_url)
    return result