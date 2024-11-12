import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Crawl data with parameters.")
    parser.add_argument('--param1', type=int, required=True, help="Parameter 1")
    return parser.parse_args()

args = parse_arguments()
print(f"{args.param1}")


def get_airflow_path():
    # Kiểm tra các dấu hiệu thường gặp của môi trường Docker
    if os.path.exists('/.dockerenv') or os.path.isfile('/proc/self/cgroup'):
        return "/opt/airflow"
    else:
        return "."

# Sử dụng hàm để thiết lập AIRFLOW_PATH
AIRFLOW_PATH = get_airflow_path()
print(f"AIRFLOW_PATH is set to: {AIRFLOW_PATH}")

# AIRFLOW_PATH = "/opt/airflow"
# # AIRFLOW_PATH = "."


data_store=(f'{AIRFLOW_PATH}/')
product_link = (f'{AIRFLOW_PATH}/data/raw/ProductDetail{args.param1}.csv')
comment_link = (f'{AIRFLOW_PATH}/data/raw/Comment{args.param1}.csv')
recommend_link = (f'{AIRFLOW_PATH}/data/proceed/final_pair.csv')

host="host.docker.internal"
port = 5432
database = "tikidb"
user = 'airflow'
password = 'airflow'

file_path=product_link

def praser(main_category,json):
  d = dict()
  d['main_category'] = main_category
  d['product_id'] = json['id']
  d['sku'] = json['sku']
  d['name'] = json['name']
  d['short_description'] = json['short_description']
  d['long_description'] = BeautifulSoup(json['description'], 'lxml').get_text()
  d['price'] = json['price']
  d['list_price'] = json['list_price']
  d['discount'] = json['discount']
  d['discount_rate'] = json['discount_rate']
  d['review_count'] = json['review_count']
  d['inventory_status'] = json['inventory_status']
  d['stock_item_qty'] = json['stock_item']['qty']
  d['stock_item_max_sale_qty'] = json['stock_item']['max_sale_qty']
  d['stock_item_min_sale_qty'] = json['stock_item']['min_sale_qty']
  try :
    d['qty_sold'] = json['quantity_sold']['value']
  except :
    d['qty_sold'] = 0
  d['brand_id'] = json['brand']['id']
  d['brand_name'] = json['brand']['name']
  d['rating_average'] = json['rating_average']
  d['day_ago_created'] = json['day_ago_created']
  d['web_link'] = json['short_url']
  d['picture'] = json['thumbnail_url']
  d['categories_id'] = json['categories']['id']
  d['categories_name'] = json['categories']['name']
  return d

def praser_comments(id,json):
  d = dict()
  d['product_id'] = id
  d['comment_id'] = json['id']
  d['title'] = json['title']
  d['content'] = json['content']
  d['thank_count'] = json['thank_count']
  d['customer_id'] = json['customer_id']
  d['rating'] = json['rating']
  d['created_at'] = json['created_at']
  d['customer_name'] = json['created_by']['full_name']
  d['is_buyed'] = json['created_by']['purchased']
  d['purchased_at'] = json['created_by']['purchased_at']
  return d

def craw_data_function(page,limit_product,category_id,page_comment,file_path,time_sleep = 0.1):
  '''
  page : Số trang cào dữ liệu
  limit_product : Số sản phẩm cào mỗi trang
  category_id : Các category cào dữ liệu [(1789,'dien-thoai-may-tinh-bang'),(1815,'thiet-bi-kts-phu-kien-so'),(1846,'laptop-may-vi-tinh-linh-kien')]
  page_comment : Số trang lấy comment
  file_path : Đường dẫn lưu dữ liệu
  time_sleep : Thời gian chờ giữa mỗi lần cào dữ liệu
  '''
  #Hàm cào dữ liệu sản phẩm.
  def get_productdata(page,limit_product,category_id):
    product_data = []
    # Tổng số lượt lặp dựa trên số danh mục, số trang và số sản phẩm mỗi trang
    total_iterations = len(category_id) * page * limit_product

    # Tiến trình với tqdm
    with tqdm(total=total_iterations) as pbar:
        for category in category_id:
            for p in range(3, page + 3):
                headers = {'accept': 'application/json, text/plain, */*','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                    'x-guest-token': 'VhpcjE82CRObQgMxU7GJHamIsDv160Yl'}

                params = {'limit': limit_product,'include': 'advertisement','aggregations': 2,'version': 'home-persionalized',
                    'trackity_id': '924411c8-58cf-9481-669b-610dbd1649e0','category': category[0],'page': p,}
                headers_detail = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                      'accept':'application/json, text/plain, */*','accept-language':'en-GB-oxendict,en-US;q=0.9,en;q=0.8','x-guest-token':'VhpcjE82CRObQgMxU7GJHamIsDv160Yl'}
                params_detail = {'platform': 'web','spid': 44434177,'version': 3}

                # Gửi request để lấy danh sách sản phẩm
                response = requests.get('https://tiki.vn/api/personalish/v1/blocks/listings', params=params, headers=headers)
                if response.status_code == 200:
                    # Lặp qua từng sản phẩm trong danh sách
                    for record in response.json().get('data'):
                        product_id = record['id']
                        # Gửi request để lấy chi tiết sản phẩm
                        response_detail = requests.get(f'https://tiki.vn/api/v2/products/{product_id}', params=params_detail, headers=headers_detail)
                        time.sleep(time_sleep)  # Tạm dừng giữa các request để tránh bị chặn

                        if response_detail.status_code == 200:
                            try:
                                # Xử lý dữ liệu chi tiết sản phẩm
                                product_data.append(praser(category[1],response_detail.json()))  # Thay 'praser' bằng hàm thực tế của bạn
                            except Exception as e:
                                print(f"Error parsing product {product_id}: {e}")

                        # Cập nhật tiến trình sau mỗi sản phẩm (đúng với tổng số sản phẩm dự kiến)
                        pbar.update(1)
    return product_data
  
  #Hàm cào comment
  def get_comment(page,product_list):
    product_comment = []
    for id in product_list:

      headers_comment = {'accept': 'application/json, text/plain, */*','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36','x-guest-token': 'VhpcjE82CRObQgMxU7GJHamIsDv160Yl'}
      for p in range(1,page + 1):
        params_comment = {'limit': 5,'include': 'comments,contribute_info,attribute_vote_summary','sort': 'score|desc,id|desc,stars|all','page': p,'product_id': id}
        response_comment = requests.get('https://tiki.vn/api/v2/reviews', params=params_comment, headers=headers_comment)
        for comment in response_comment.json()['data']:
          try :
            product_comment.append(praser_comments(id,comment))
          except Exception as e:
            print(id,'error:',e)
    return product_comment

  print('Cào dữ liệu id sản phẩm:')
  product_data = get_productdata(page,limit_product,category_id)
  product_data = pd.DataFrame(product_data)
  product_data .to_csv(product_link,index=False)
  print('Cào dữ liệu comment sản phẩm:')
  product_id_list = product_data.product_id.to_list()
  comment_data = get_comment(page_comment,product_id_list)
  comment_data = pd.DataFrame(comment_data)
  comment_data.to_csv(comment_link,index=False)
  return True


if __name__ == "__main__":
  page = 20
  limit_product = 40
  page_comment = 4
  file_path = data_store
  category_id = [(1789,'dien-thoai-may-tinh-bang'),(1815,'thiet-bi-kts-phu-kien-so'),(1846,'laptop-may-vi-tinh-linh-kien')]
  category_inuse = [category_id[args.param1]]
  craw_data_function(page,limit_product,category_inuse,page_comment,file_path,time_sleep = 0.01)