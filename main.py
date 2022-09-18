from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By


# initialize selenium driver
##service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome('chromedriver.exe')

BASE_URL = "https://www.amazon.com/"


def search_product(query_keyword: str) -> str:
    """ Scrapes Amazon search of given keyword and returns top (un-sponsored) product link. """

    full_url = BASE_URL + "s?k=" + query_keyword

    # grab webpage with this search query
    driver.get(full_url)

    # scrape details from webpage
    title = driver.title
    print('scraping:', title)

    driver.implicitly_wait(0.5)

    # grab results section of page
    results_class = 's-main-slot'
    results = driver.find_element(by=By.CLASS_NAME, value=results_class)

    # gets all the child divs of this level, nothing deeper
    products = results.find_elements(by=By.XPATH, value='./*')

    for product in products:
        classes = product.get_attribute(name='class')

        # skips element if it's sponsored, or if it's not a product
        if classes is not None and 'AdHolder' in classes:
            continue
        else:
            asin = product.get_attribute(name='data-asin')
            if asin is None or asin.strip() == '':
                continue

        # break once we get the first valid product
        top_product = asin
        break

    # returns URL to top result
    return BASE_URL + 'dp/' + top_product

def read_grocery_list(filename: str) -> list[str]:
    """ Reads textfile of grocery list and returns a list of the grocery items. """

    grocery_items = []

    # opens file containing grocery list
    with open(filename, 'r') as grocery_list:
        grocery_lines = grocery_list.readlines()

        # iterates over ever grocery item and adds it to return list
        for item in grocery_lines:
            # skips over empty lines
            if item.strip() == '':
                continue
            grocery_items.append(item.strip())

    return grocery_items

def get_grocery_links(filename: str) -> tuple[list[str], list[str]]:
    """ Reads textfile of grocery list, gets each item's Amazon link, and returns a list of the links. """

    grocery_items = []  # stores original item names
    grocery_links = []  # stores items' Amazon links

    # opens file containing grocery list
    with open(filename, 'r') as grocery_list:
        textfile_lines = grocery_list.readlines()

        # iterates over every grocery item in list
        for item in textfile_lines:
            # skips over empty lines
            if item.strip() == '':
                continue

            amazon_link = search_product(item.strip())  # fetch item Amazon link
            grocery_items.append(item.strip())  # append original item name
            grocery_links.append(amazon_link)  # append Amazon link

    return grocery_items, grocery_links

def export_grocery_links(filename: str, items: list[str], links: list[str]):
    """ Writes a textfile of the grocery list with each item's corresponding Amazon link. """

    export = ''

    # iterates over every item and corresponding link and writes them to the string we're building
    for item, link in zip(items, links):
        export += item + ': ' + link + '\n'  # ex. Glitter body gel: https://www.amazon.com/dp/AB2C3D3E4FH

    # write generated string to file
    with open(filename, 'w+') as grocery_list:
        grocery_list.write(export)


if __name__ == '__main__':
    grocery_items, grocery_links = get_grocery_links('groceries.txt')
    export_grocery_links('amazon_groceries.txt', grocery_items, grocery_links)

    # exit scraping page
    driver.quit()
