import requests
from requests import Session

from config import logger
from model.Product import Product
from service.collector.collectorImageService import first_img_url_under_pixel_limit, \
    SHOPIFY_MEGA_PIXELS_IMAGE_RESOLUTION_LIMIT
from service.collector.collectorService import all_href_urls, get_page_soup, images_src, tag_text, \
    inner_html_str_index_0, tags_text

PRODUCTS_URL = 'http://johnsonhardwood.com/products/'
VENDOR_NAME = 'Johnson Hardwood'
WOOD_CSV_FILE_NAME = 'johnson-hardwood-template.csv'


def get_all_categories_products_urls(session: Session, url: str):
    category_urls = all_href_urls('#filter-container .serieses', get_page_soup(session, url))
    logger.debug('Finish getting category urls from: ' + url)

    products_urls = []
    for category_url in category_urls:
        products_urls.extend(all_href_urls('#filter-container .products', get_page_soup(session, category_url)))
    return products_urls


def get_product_details(session: Session, product_url: str):
    soup = get_page_soup(session, product_url)
    image = images_src('#product-gallery .item.active .image-wrapper', soup)[0]
    variant_image_urls = images_src('#product-gallery .item .image-wrapper', soup)[1:]
    variant_image_url = first_img_url_under_pixel_limit(variant_image_urls, SHOPIFY_MEGA_PIXELS_IMAGE_RESOLUTION_LIMIT,
                                                        session)
    title = tag_text('.main .container .header-wrapper h1', soup)
    product_code = tag_text('.main .container .header-wrapper h1 + span', soup)
    product_details = inner_html_str_index_0('.main .entry-content.container .details', soup)
    collection = tag_text('.series-logo .sr-only', soup)
    tags = ",".join(tags_text('.main .entry-content.container .details span', soup))
    tags += "," + collection
    return Product(title, image, variant_image_url,
                   title, VENDOR_NAME,
                   product_code, '',
                   product_details, tags)


def get_products_details():
    session = requests.session()
    products_urls = get_all_categories_products_urls(session, PRODUCTS_URL)
    products_details = [get_product_details(session, url) for url in products_urls]
    session.close()
    return products_details
