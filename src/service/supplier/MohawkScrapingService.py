from selenium.webdriver.phantomjs import webdriver
from selenium.webdriver.phantomjs.webdriver import WebDriver

from src.Config import logger
from src.service.common.CollectorService import get_soup_by_page_content, all_href_urls, \
    all_attributes_for_all_elements, tag_text, tags_text
from src.service.common.SeleniumCollectorService import get_page_source_until_selector

BASE_URL = 'https://www.mohawkflooring.com'
CARPET_URL = BASE_URL + '/carpet/search?page='

WOOD_CATEGORY_BASE_URL = BASE_URL + '/wood/search?page='
WOOD_PRODUCT_BASE_URL = '/engineered-wood/detail'

VINYL_URL = BASE_URL + '/vinyl/search?page='
TILE_URL = BASE_URL + '/tile/search?page='
RUGS_URL = BASE_URL + '/rugs/search?page='

VENDOR_NAME = 'Mohawk Flooring'
CARPET_CSV_FILE_NAME = 'mohawk-flooring-carpet-template.csv'
WOOD_CSV_FILE_NAME = 'mohawk-flooring-wood-template.csv'

TIME_OUT_DYNAMIC_DELAY = 2


def get_product_category_urls_per_page(driver: WebDriver, url: str, page_number: int):
    try:
        driver.get(url + str(page_number))
        page_content = get_page_source_until_selector(driver, '.product-image', TIME_OUT_DYNAMIC_DELAY)
        soup = get_soup_by_page_content(page_content)
        return [BASE_URL + url for url in all_href_urls('.style-tile', soup)]
    except Exception as e:
        logger.debug(
            'Did not find any page source on page for categories: {} with exception: {}'.format(page_number, e))
        return None


def get_all_product_category_urls(driver: WebDriver, url: str):
    category_urls = []
    i = 1
    while True:
        response = get_product_category_urls_per_page(driver, url, i)
        logger.debug('Get all product category urls for page: {}'.format(url + str(i)))
        if response is None:
            return category_urls
        i += 1
        category_urls.extend(response)


def get_product_urls_per_page(driver: WebDriver, category_url: str, category_base_url: str):
    try:
        driver.get(category_url)
        page_content = get_page_source_until_selector(driver, '#related-color', TIME_OUT_DYNAMIC_DELAY)
        soup = get_soup_by_page_content(page_content)
        data_style_ids = all_attributes_for_all_elements('.slider-container div>a', 'data-style-id', soup)
        data_color_ids = all_attributes_for_all_elements('.slider-container div>a', 'data-color-id', soup)
        product_category_title = tag_text('.column.main-info h2', soup).replace(' ', '-')
        products_titles = [text.replace(' ', '-') for text in
                           tags_text('.slider-container span[class^="ng-binding"]', soup)]
        return [
            BASE_URL + category_base_url + '/' + style_id + '-' + color_id + '/' + product_category_title + '-' + product_title
            for
            style_id, color_id, product_title in
            zip(data_style_ids, data_color_ids, products_titles)]
    except Exception as e:
        logger.debug('Fail to get product urls on category url: {} with exception: {}'.format(category_url, e))
        return None


def get_all_product_urls(driver: WebDriver, category_urls: [], category_base_url: str):
    products_urls = []
    for category_url in category_urls:
        product_category_urls = get_product_urls_per_page(driver,
                                                          category_url,
                                                          category_base_url)
        logger.debug('Get all product urls for category url: {}'.format(category_url))
        products_urls.extend(product_category_urls)
    return products_urls


def get_wood_products_details():
    driver = webdriver.WebDriver()
    category_urls = get_all_product_category_urls(driver, WOOD_CATEGORY_BASE_URL)
    product_urls = get_all_product_urls(driver, category_urls, WOOD_PRODUCT_BASE_URL)
    driver.quit()
    return None
