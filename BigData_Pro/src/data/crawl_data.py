import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

AIRFLOW_PATH = "/opt/airflow/"

class ProductScraper:
    def __init__(self, category_id, limit_per_page=1, page_count=1):
        self.category_id = category_id
        self.limit_per_page = limit_per_page
        self.page_count = page_count
        self.base_url = 'https://tiki.vn/api'
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'x-guest-token': 'VhpcjE82CRObQgMxU7GJHamIsDv160Yl'
        }

    def fetch_data(self, endpoint, params):
        """Make a GET request to the specified endpoint with given parameters."""
        response = requests.get(f"{self.base_url}/{endpoint}", params=params, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()

    def parse_product_data(self, category, json):
        """Parse product data from JSON response."""
        return {
            'main_category': category,
            'id': json.get('id'),
            'sku': json.get('sku'),
            'name': json.get('name'),
            'short_description': json.get('short_description'),
            'long_description': BeautifulSoup(json.get('description', ''), 'lxml').get_text(),
            'price': json.get('price'),
            'list_price': json.get('list_price'),
            'discount': json.get('discount'),
            'discount_rate': json.get('discount_rate'),
            'review_count': json.get('review_count'),
            'inventory_status': json.get('inventory_status'),
            'stock_item_qty': json['stock_item'].get('qty', 0),
            'stock_item_max_sale_qty': json['stock_item'].get('max_sale_qty', 0),
            'stock_item_min_sale_qty': json['stock_item'].get('min_sale_qty', 0),
            'qty_sold': json.get('quantity_sold', {}).get('value', 0),
            'brand_id': json['brand'].get('id', 0),
            'brand_name': json['brand'].get('name', ''),
            'rating_average': json.get('rating_average'),
            'day_ago_created': json.get('day_ago_created'),
            'web_link': json.get('short_url'),
            'picture': json.get('thumbnail_url'),
            'categories_id': json['categories'].get('id', []),
            'categories_name': json['categories'].get('name', [])
        }

    def parse_comment_data(self, product_id, json):
        """Parse comment data from JSON response."""
        return {
            'product_id': product_id,
            'comment_id': json.get('id'),
            'title': json.get('title'),
            'content': json.get('content'),
            'thank_count': json.get('thank_count'),
            'customer_id': json.get('customer_id'),
            'rating': json.get('rating'),
            'created_at': json.get('created_at'),
            'customer_name': json.get('created_by', {}).get('full_name', ''),
            'is_buyed': json.get('created_by', {}).get('purchased', False),
            'purchased_at': json.get('created_by', {}).get('purchased_at', '')
        }

    def get_product_data(self):
        """Fetch product data for the given category and return as a list of dictionaries."""
        product_data = []

        for category in self.category_id:
            for p in range(3, self.page_count + 3):  # Adjusting page range to start from 3
                params = {
                    'limit': self.limit_per_page,
                    'include': 'advertisement',
                    'aggregations': 2,
                    'version': 'home-persionalized',
                    'trackity_id': '924411c8-58cf-9481-669b-610dbd1649e0',
                    'category': category[0],
                    'page': p
                }

                # Fetch product listings
                try:
                    listings = self.fetch_data('personalish/v1/blocks/listings', params).get('data', [])
                    for record in listings:
                        product_id = record['id']
                        # Fetch product details
                        product_details = self.fetch_data(f'v2/products/{product_id}', {'platform': 'web', 'spid': 44434177, 'version': 3})
                        product_data.append(self.parse_product_data(category[1], product_details))
                        time.sleep(0.3)  # Rate limit
                except requests.HTTPError as e:
                    print(f"Error fetching data for category {category[1]}: {e}")

        return product_data

    def get_comments(self, product_list):
        """Fetch comments for a list of products."""
        product_comments = []

        for product_id in product_list:
            for p in range(1, 11):  # Assuming a fixed page count for comments
                params_comment = {
                    'limit': 5,
                    'include': 'comments,contribute_info,attribute_vote_summary',
                    'sort': 'score|desc,id|desc,stars|all',
                    'page': p,
                    'product_id': product_id
                }

                # Fetch comments
                try:
                    comments = self.fetch_data('v2/reviews', params_comment).get('data', [])
                    for comment in comments:
                        product_comments.append(self.parse_comment_data(product_id, comment))
                except requests.HTTPError as e:
                    print(f"Error fetching comments for product {product_id}: {e}")

        return product_comments

def main():
    CATEGORY_ID = [
        (1789, 'dien-thoai-may-tinh-bang'),
        (1815, 'thiet-bi-kts-phu-kien-so'),
        (1846, 'laptop-may-vi-tinh-linh-kien')
    ]

    scraper = ProductScraper(CATEGORY_ID)
    # Fetch product data
    product_data = scraper.get_product_data()

    # Convert to DataFrame and save to CSV
    product_df = pd.DataFrame(product_data)
    product_df.to_csv('/opt/airflow/data/raw/data.csv', encoding='utf-8-sig', index=False)

    # Extract product ID list
    product_id_list = product_df['id'].tolist()

    # Fetch comments for the products
    comments_data = scraper.get_comments(product_id_list)

    # Convert comments to DataFrame and save to CSV
    comments_df = pd.DataFrame(comments_data)
    comments_df.to_csv('/opt/airflow/data/raw/comment.csv', encoding='utf-8-sig', index=False)

    print("Data scraping completed. Product data and comments have been saved to CSV files.")

if __name__ == "__main__":
    main()
