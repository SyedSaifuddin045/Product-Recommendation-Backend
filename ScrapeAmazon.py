import json
import sys
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import threading

# Create options object for Firefox
options = Options()
options.add_argument('-headless')

products = []
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

def get_product_id(url):
    if '/dp/' in url:
        start_index = url.index('/dp/') + 4
        end_index = -1
        qm_index = url.find('?', start_index)
        if qm_index > 0:
            end_index = qm_index
        bs_index = url.find('/', start_index)
        if bs_index > 0:
            end_index = bs_index
        if end_index == -1:
            end_index = len(url)
        return url[start_index:end_index]

    if '%2Fdp%2F' in url:
        start_index = url.index('%2Fdp%2F') + 8
        end_index = url.find('%2F', start_index)
        if end_index == -1:
            end_index = len(url)
        return url[start_index:end_index]

    return None

def extract_numbers(text):
    numbers = ''
    for char in text:
        if char.isspace():
            break
        if char.isdigit():
            numbers += char
    return int(numbers) if numbers else 0

def Rate_Product(site_rating,positive_ratings,total_ratings):
    w1 = 0.8
    w2 = 0.8
    w3 = 0.9
    w4 = 0.5
    site_rating = extract_numbers(site_rating)
    rating = (w1 * (positive_ratings / total_ratings) ) + (w2 * total_ratings) + (w3 * positive_ratings) + (w4 * site_rating)  
    return rating

def process_results(page_link,products):
    # Create a new instance of the browser
    browser = webdriver.Firefox(options)
    browser.get(page_link)

    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.ID, 'search')))
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 's-result-item')))

    html = browser.page_source
    browser.quit()

    soup = BeautifulSoup(html, 'lxml')
    results = soup.find_all('div', class_='s-result-item')

    # Add the results to the Products list
    for result in results:
        item_name_elem = result.find('span', class_='a-text-normal')
        item_price = result.find('span', class_='a-price-whole')
        item_rating = result.find('span', class_='a-icon-alt')
        item_url = result.find('a', class_='a-link-normal')
        item_image = result.find('img',class_='s-image')
        
        # Skip the item if any of the elements are null
        if item_name_elem is None or item_price is None or item_url is None or item_rating is None or item_image is None:
            continue

        # Extract the text from the elements
        image_url = item_image.get('src')
        item_name = item_name_elem.text
        price = item_price.text
        rating = item_rating.text
        product_id = get_product_id(item_url.get('href'))

        # Skip the item if the product ID is not found
        if product_id is None:
            continue

        link = website_address + '/dp/' + product_id
        review_link = website_address + f'/product-reviews/{product_id}' + '/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=positive'
        # Add a row for each item to the products list
        print(("Adding product from Page"))
        product = {
            "item_name": item_name,
            "image_url":image_url,
            "price": price,
            "rating": rating,
            "link": link,
            "product_id": product_id,
            "review_link": review_link,
            "positive_reviews": "",
            "total_reviews": "",
            "rating_value": ""
        }
        products.append(product)

def process_review(page_link,index):
    # Create a new instance of the browser
    browser = webdriver.Firefox(options)
    browser.get(page_link)

    wait = WebDriverWait(browser, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'reviewNumericalSummary')))
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'averageStarRatingNumerical')))

    html = browser.page_source
    browser.quit()

    soup = BeautifulSoup(html, 'lxml')
    Total_reviews = soup.find('div', class_='averageStarRatingNumerical')
    Total_reviews_text = Total_reviews.find('span', class_='a-size-base').text
    Positive_reviews = soup.find('div', id='filter-info-section')
    Positive_reviews_text = Positive_reviews.find('div', class_='a-spacing-base').text.strip()

    total_ratings = extract_numbers(Total_reviews_text)
    positive_ratings = extract_numbers(Positive_reviews_text)

    review_results.append((positive_ratings, total_ratings, index))
    print(f"Getting Rating for product number : {index}")    

# Read the search text from command-line arguments
searchtext = extract_argument_value(sys.argv, '-st')
print(f'Search Text : {searchtext}')

website_address = "https://www.amazon.in"
search_url = website_address + f'/s?k={searchtext}'

print("Search Started on Amazon.")
# List to store page links
page_links = []

# Adding page urls
for i in range(1, 3):
    search_url += f'&page={i}'
    page_links.append(search_url)

# Create and start threads for processing results of other pages
threads = []
for link in page_links:
    thread = threading.Thread(target=process_results, args=(link,products))
    thread.start()
    threads.append(thread)

# Wait for all threads to complete
for thread in threads:
    thread.join()

print(f"Got {len(products)} Products")
# List to store review links
review_links = []

# Read each row in the csvrows list
for row in products:
    review_link = row["review_link"]  # Assuming review link is in the 6th column
    review_links.append(review_link)

# Create and start threads for processing review links
review_results = []
threads = []
max_threads = 8
current_threads = 0

print("Getting reviews of Products")
i = 0
for link in review_links:
    # Check if maximum threads limit is reached
    if current_threads >= max_threads:
        # Wait for a thread to finish before starting a new one
        threads[0].join()
        threads.pop(0)
        current_threads -= 1

    thread = threading.Thread(target=process_review, args=(link,i))
    thread.start()
    threads.append(thread)
    current_threads += 1
    
    i+=1
# Wait for all threads to complete
for thread in threads:
    thread.join()

# Update the positive reviews, total reviews, and rating in the corresponding rows of csvrows
for positive_reviews, total_reviews, row_index in review_results:
    # print(f"Row Index: {row_index}")
    # print(f"CSV Rows Length: {len(csvrows)}")
    if row_index < len(products):
        products[row_index]["positive_reviews"] = positive_reviews
        products[row_index]["total_reviews"] = total_reviews
        products[row_index]["rating_value"] = Rate_Product(products[row_index]["rating"], positive_reviews, total_reviews)
    else:
        print("Invalid row index")

products.sort(key=lambda product:product["rating_value"],reverse=True)
print("Rating Completed!")

json_string = json.dumps(products,indent=4)

file_path = f"{searchtext}.json"  # specify the file path
with open(file_path, "w") as outfile:
    outfile.write(json_string)

#print(f"Search Completed for : {searchtext}")