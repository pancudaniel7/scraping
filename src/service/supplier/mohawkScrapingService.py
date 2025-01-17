from selenium.webdriver.phantomjs import webdriver
from selenium.webdriver.phantomjs.webdriver import WebDriver

from config import logger
from model.Product import Product
from service.collector.collectorService import get_soup_by_content, all_href_urls, attribute_value_for_all_elements, \
    tag_text, tags_text, inner_html_str_index_0, extract_product_details_from_html
from service.html import htmlTemplateService
from service.supplier.seleniumCollectorService import get_page_source_until_selector_with_delay, \
    get_page_source_until_selector

BASE_URL = 'https://www.mohawkflooring.com'

WOOD_CATEGORY_BASE_URL = BASE_URL + '/wood/search?page='
WOOD_PRODUCT_BASE_URL = '/engineered-wood/detail'
WOOD_CSV_FILE_NAME = 'mohawk-flooring-wood-template.csv'

VINYL_CATEGORY_BASE_URL = BASE_URL + '/vinyl/search?page='
VINYL_PRODUCT_BASE_URL = '/luxury-vinyl-tile/detail'
VINYL_CSV_FILE_NAME = 'mohawk-flooring-vinyl-template.csv'

TILE_CATEGORY_BASE_URL = BASE_URL + '/tile/search?page='
TILE_PRODUCT_BASE_URL = '/tile/detail'
TILE_CSV_FILE_NAME = 'mohawk-flooring-tile-template.csv'

RUGS_URL = BASE_URL + '/rugs/search?page='

VENDOR_NAME = 'Mohawk Flooring'

TIME_OUT_DYNAMIC = 5
TIME_OUT_PRODUCT = 3
TIME_OUT_CATEGORY_URL = 10
TIME_CATEGORY_URLS_DELAY = 5
TIME_DELAY = 1


def get_product_category_urls_per_page(driver: WebDriver, url: str, page_number: int):
    driver.get(url + str(page_number))
    page_content = get_page_source_until_selector_with_delay(driver, '.product-image img', TIME_OUT_CATEGORY_URL,
                                                             TIME_CATEGORY_URLS_DELAY)
    soup = get_soup_by_content(page_content)
    return [BASE_URL + url for url in all_href_urls('.style-tile', soup)]


def get_all_product_category_urls(driver: WebDriver, url: str):
    return get_product_category_urls_per_page(driver, url, 100)


def get_product_urls_per_page(driver: WebDriver, category_url: str, category_base_url: str):
    driver.get(category_url)
    page_content = get_page_source_until_selector(driver, '#related-color', TIME_OUT_DYNAMIC)
    soup = get_soup_by_content(page_content)
    data_style_ids = attribute_value_for_all_elements('.slider-container div > a', 'data-style-id', soup)
    data_color_ids = attribute_value_for_all_elements('.slider-container div > a', 'data-color-id', soup)
    product_category_title = tag_text('.column.main-info h2', soup).replace(' ', '-')
    products_titles = [text.replace(' ', '-') for text in
                       tags_text('.slider-container span[class^="ng-binding"]', soup)]
    return [
        BASE_URL + category_base_url + '/' + style_id + '-' + color_id + '/' + product_category_title + '-' + product_title
        for
        style_id, color_id, product_title in
        zip(data_style_ids, data_color_ids, products_titles)]


def get_all_product_urls(driver: WebDriver, category_urls: [], category_base_url: str):
    products_urls = []
    for category_url in category_urls:
        product_category_urls = get_product_urls_per_page(driver,
                                                          category_url,
                                                          category_base_url)
        logger.debug('Get all product urls for category url: {}'.format(category_url))
        products_urls.extend(product_category_urls)
    return products_urls


def get_product_details(driver: WebDriver, product_url: str):
    driver.get(product_url)
    page_content = get_page_source_until_selector_with_delay(driver, '.swatch-image', TIME_OUT_PRODUCT, TIME_DELAY)
    soup = get_soup_by_content(page_content)
    image = attribute_value_for_all_elements('.swatch-image', 'back-img', soup)[0]
    product_category_title = tag_text('.column.main-info h2', soup)
    product_title = tag_text('.product-details .column.swatches-section h2', soup)
    product_details = inner_html_str_index_0('.content .specifications-table', soup)
    product_details_fields = extract_product_details_from_html(product_details, '.key', '.val')
    product_details = htmlTemplateService.create_product_template(product_details_fields[0],
                                                                  product_details_fields[1])
    collection = tag_text('#product-details > section:nth-child(2) > div.row.collapse > div.column.main-info > h3',
                          soup)
    tags = ','.join(tags_text('.val span', soup))
    if collection != '': tags += ',' + collection
    return Product(product_title, image, image, product_category_title + ' ' + product_title, VENDOR_NAME, '', '',
                   product_details,
                   tags)


def get_all_products_details(driver: WebDriver, product_urls: []):
    products = []
    logger.debug('Product number: {}'.format(len(product_urls)))
    id = 1
    for product_url in product_urls:
        logger.debug('Get product details for url: {}'.format(product_url))
        product = get_product_details(driver, product_url)
        product.id += str(id)
        products.append(product)
        id += 1
    return products


def get_wood_products_details():
    driver = webdriver.WebDriver()
    category_urls = get_all_product_category_urls(driver, WOOD_CATEGORY_BASE_URL)
    product_urls = get_all_product_urls(driver, category_urls, WOOD_PRODUCT_BASE_URL)
    product_details = get_all_products_details(driver, product_urls)
    driver.quit()
    return product_details


def get_vinyl_products_details():
    driver = webdriver.WebDriver()
    category_urls = get_all_product_category_urls(driver, VINYL_CATEGORY_BASE_URL)
    product_urls = get_all_product_urls(driver, category_urls, VINYL_PRODUCT_BASE_URL)
    product_details = get_all_products_details(driver, product_urls)
    driver.quit()
    return product_details


def get_tile_products_details():
    driver = webdriver.WebDriver()
    category_urls = get_all_product_category_urls(driver, TILE_CATEGORY_BASE_URL)
    product_urls = get_all_product_urls(driver, category_urls, TILE_PRODUCT_BASE_URL)
    product_details = get_all_products_details(driver, product_urls)
    driver.quit()
    return product_details
