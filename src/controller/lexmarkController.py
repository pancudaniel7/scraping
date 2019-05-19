from config import csv_template_dir, url_file_dir, TEMPLATE_FILE_NAME
from service.csv import csvService
from service.supplier import lexmarkScrappigService
from transformer import productToShopifyCsvTransformer


def lexmark_carpet_collecting(counter: int):
    products_details = lexmarkScrappigService.get_products_details(lexmarkScrappigService.CARPET_URL, "Carpet",
                                                                       1000, counter,
                                                                       url_file_dir() + lexmarkScrappigService.LEXMARK_CARPET_URL_FILE_NAME)
    csvService.clean_csv_file(csv_template_dir() + TEMPLATE_FILE_NAME,
                              csv_template_dir() + lexmarkScrappigService.LEXMARK_CARPET_CSV_FILE_NAME)
    shopify_csv_array = [productToShopifyCsvTransformer.product_to_shopify(product) for product in products_details]
    products_details.clear()
    csvService.append_csv_array_to_file(
        csv_template_dir() + lexmarkScrappigService.LEXMARK_CARPET_CSV_FILE_NAME,
        shopify_csv_array)