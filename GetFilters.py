import json
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument(('-headless'))

def extract_argument_value(args, key):
    start_index = -1
    for i in range(len(args)):
        if args[i] == key:
            start_index = i + 1
            break
    if start_index == -1 or start_index >= len(args):
        return None
    end_index = start_index + 1
    while end_index < len(args) and not args[end_index].startswith('-'):
        end_index += 1
    return ' '.join(args[start_index:end_index])

def get_product_filters(searchtext):
    browser = webdriver.Firefox(options)
    url = "https://www.amazon.in/s?k=" + searchtext
    browser.get(url)

    wait = WebDriverWait(browser, 8)
    wait.until(EC.presence_of_element_located((By.ID, 'priceRefinements')))
    wait.until(EC.presence_of_element_located((By.ID, 'filters')))

    html = browser.page_source
    browser.quit()

    soup = BeautifulSoup(html, 'lxml')
    price = soup.find('div', id='priceRefinements', recursive=True)
    filters = soup.find('div', id='filters', recursive=True)

    filterheadings = filters.find_all('div', class_='a-section a-spacing-small')
    filterlists = filters.find_all('ul', class_='a-unordered-list a-nostyle a-vertical a-spacing-medium')

    f_headings = []
    filter_json = {}

    for filterheading in filterheadings:
        f_headings.append(filterheading.text.strip())

    if 'Colour' in f_headings:
        f_headings.remove('Colour')

    i = 0
    for filterlist in filterlists:
        f_list = []
        list_items = filterlist.find_all('li', class_='a-spacing-micro')
        for list_item in list_items:
            l_id = list_item.get('id')
            if l_id is None:
                continue
            new_l_id = l_id.replace('/', ':')
            f_list.append({'text': list_item.text.strip(), 'id': new_l_id})
        filter_json[f_headings[i]] = f_list
        i += 1

    # Convert the filter_json object to a JSON string
    filter_json_str = json.dumps(filter_json, indent=4)
    print(filter_json_str)

searchtext = extract_argument_value(sys.argv, '-st')
get_product_filters(searchtext)