from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define categories with ID and slug
CATEGORY_ID = [
    (1789, 'dien-thoai-may-tinh-bang'),
    (1815, 'thiet-bi-kts-phu-kien-so'),
    (1846, 'laptop-may-vi-tinh-linh-kien')
]

def parse_product_data(main_category, json):
    """Parse product data from JSON response."""
    data = {
        'main_category': main_category,
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
    return data

def get_product_data(**kwargs):
    """Fetch product data for given categories and return as a list of dictionaries."""
    product_data = []

    for category in CATEGORY_ID:
        for p in range(3, 4):  # Adjusting page range to start from 3
            headers = {
                'accept': 'application/json, text/plain, */*',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                'x-guest-token': 'VhpcjE82CRObQgMxU7GJHamIsDv160Yl'
            }

            params = {
                'limit': 1,  # Set limit for demonstration purposes
                'include': 'advertisement',
                'aggregations': 2,
                'version': 'home-persionalized',
                'trackity_id': '924411c8-58cf-9481-669b-610dbd1649e0',
                'category': category[0],
                'page': p
            }

            response = requests.get('https://tiki.vn/api/personalish/v1/blocks/listings', params=params, headers=headers)

            if response.status_code == 200:
                for record in response.json().get('data', []):
                    product_id = record['id']
                    response_detail = requests.get(f'https://tiki.vn/api/v2/products/{product_id}', params={'platform': 'web', 'spid': 44434177, 'version': 3}, headers=headers)
                    time.sleep(0.3)  # Rate limit

                    if response_detail.status_code == 200:
                        try:
                            product_data.append(parse_product_data(category[1], response_detail.json()))
                            logging.info(f"Successfully fetched product ID: {product_id}")
                        except Exception as e:
                            logging.error(f"Error parsing product {product_id}: {e}")
            else:
                logging.error(f"Failed to fetch products for category {category[1]}: {response.status_code}")

    # Save product data to XCom for use in downstream tasks
    kwargs['ti'].xcom_push(key='product_data', value=product_data)

def get_comments(**kwargs):
    """Fetch comments for a list of products."""
    product_data = kwargs['ti'].xcom_pull(key='product_data', task_ids='get_product_data')
    product_comments = []

    for product in product_data:
        product_id = product['id']
        headers_comment = {
            'accept': 'application/json, text/plain, */*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'x-guest-token': 'VhpcjE82CRObQgMxU7GJHamIsDv160Yl'
        }

        for p in range(1, 11):  # Fetching 10 pages of comments for demonstration
            params_comment = {
                'limit': 5,
                'include': 'comments,contribute_info,attribute_vote_summary',
                'sort': 'score|desc,id|desc,stars|all',
                'page': p,
                'product_id': product_id
            }

            response_comment = requests.get('https://tiki.vn/api/v2/reviews', params=params_comment, headers=headers_comment)

            if response_comment.status_code == 200:
                for comment in response_comment.json().get('data', []):
                    try:
                        product_comments.append(parse_comment_data(product_id, comment))
                    except Exception as e:
                        logging.error(f"Error parsing comment for product {product_id}: {e}")
            else:
                logging.error(f"Failed to fetch comments for product {product_id}: {response_comment.status_code}")

    # Save comments data to CSV
    comments_df = pd.DataFrame(product_comments)
    comments_df.to_csv('/opt/airflow/data/raw/comment.csv', encoding='utf-8-sig', index=False)
    logging.info("Comments data saved to CSV.")

def parse_comment_data(product_id, json):
    """Parse comment data from JSON response."""
    data = {
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
    return data

# Define the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 19),
    'retries': 1,
}

dag = DAG(
    'crawl_data',
    default_args=default_args,
    description='A DAG to scrape product and comment data',
    schedule_interval='@daily',
)

get_product_task = PythonOperator(
    task_id='get_product_data',
    python_callable=get_product_data,
    provide_context=True,
    dag=dag,
)

get_comments_task = PythonOperator(
    task_id='get_comments',
    python_callable=get_comments,
    provide_context=True,
    dag=dag,
)

get_product_task >> get_comments_task
