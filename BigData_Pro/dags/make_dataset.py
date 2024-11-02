import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime
from tqdm import tqdm

category_id = [(1789,'dien-thoai-may-tinh-bang'),(1815,'thiet-bi-kts-phu-kien-so'),(1846,'laptop-may-vi-tinh-linh-kien')]

#1789 - https://tiki.vn/dien-thoai-may-tinh-bang/c1789
#1815 - https://tiki.vn/thiet-bi-kts-phu-kien-so/c1815
#1846 - https://tiki.vn/laptop-may-vi-tinh-linh-kien/c1846

AIRFLOW_PATH = "/opt/airflow/"
NUM_DATA = 40

time_run =  datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')



def praser(main_category,json):
  d = dict()
  d['main_category'] = main_category
  d['id'] = json['id']
  d['sku'] = json['sku']
  d['name'] = json['name']
  d['short_description'] = json['short_description']
  d['long_description'] = soup = BeautifulSoup(json['description'], 'lxml').get_text()
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


def get_productdata(page,limit_product,category_id):
  product_data = []
  # Tổng số lượt lặp dựa trên số danh mục, số trang và số sản phẩm mỗi trang
  total_iterations = len(category_id) * page * limit_product

  # Tiến trình với tqdm
  with tqdm(total=total_iterations) as pbar:
      for category in category_id:
          for p in range(3, page + 3):
              headers = {
                  'accept': 'application/json, text/plain, */*',
                  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                  'x-guest-token': 'VhpcjE82CRObQgMxU7GJHamIsDv160Yl'
              }

              params = {
                  'limit': limit_product,
                  'include': 'advertisement',
                  'aggregations': 2,
                  'version': 'home-persionalized',
                  'trackity_id': '924411c8-58cf-9481-669b-610dbd1649e0',
                  'category': category[0],
                  'page': p,
              }

              headers_detail = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                    'accept':'application/json, text/plain, */*',
                    'accept-language':'en-GB-oxendict,en-US;q=0.9,en;q=0.8',
                    'x-guest-token':'VhpcjE82CRObQgMxU7GJHamIsDv160Yl'}
              params_detail = {'platform': 'web','spid': 44434177,'version': 3}

              # Gửi request để lấy danh sách sản phẩm
              response = requests.get('https://tiki.vn/api/personalish/v1/blocks/listings', params=params, headers=headers)
              if response.status_code == 200:
                  # Lặp qua từng sản phẩm trong danh sách
                  for record in response.json().get('data'):
                      product_id = record['id']
                      # Gửi request để lấy chi tiết sản phẩm
                      response_detail = requests.get(f'https://tiki.vn/api/v2/products/{product_id}', params=params_detail, headers=headers_detail)
                      time.sleep(0.3)  # Tạm dừng giữa các request để tránh bị chặn

                      if response_detail.status_code == 200:
                          try:
                              # Xử lý dữ liệu chi tiết sản phẩm
                              product_data.append(praser(category[1],response_detail.json()))  # Thay 'praser' bằng hàm thực tế của bạn
                          except Exception as e:
                              print(f"Error parsing product {product_id}: {e}")

                      # Cập nhật tiến trình sau mỗi sản phẩm (đúng với tổng số sản phẩm dự kiến)
                      pbar.update(1)
  return product_data


data = get_productdata(NUM_DATA,NUM_DATA,category_id)


product_data = pd.DataFrame(data)
product_data

headers_detail = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                    'accept':'application/json, text/plain, */*',
                    'accept-language':'en-GB-oxendict,en-US;q=0.9,en;q=0.8',
                    'x-guest-token':'VhpcjE82CRObQgMxU7GJHamIsDv160Yl'}
params_detail = {'platform': 'web','spid': 44434177,'version': 3}
BeautifulSoup(requests.get('https://tiki.vn/api/v2/products/88265782', params=params_detail, headers=headers_detail).json()['description'], 'lxml').get_text()

product_data.to_csv(f'{AIRFLOW_PATH}/data/raw/data_{time_run}.csv',encoding = 'utf-8-sig')

product_id_list = product_data.id.to_list()

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

def get_comment(page,product_list):
  product_comment = []
  for id in product_list:

    headers_comment = {
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'x-guest-token': 'VhpcjE82CRObQgMxU7GJHamIsDv160Yl'
    }

    for p in range(1,page + 1):

      params_comment = {
          'limit': 5,
          'include': 'comments,contribute_info,attribute_vote_summary',
          'sort': 'score|desc,id|desc,stars|all',
          'page': p,
          'product_id': id
      }


      response_comment = requests.get('https://tiki.vn/api/v2/reviews', params=params_comment, headers=headers_comment)
      for comment in response_comment.json()['data']:
        try :
          product_comment.append(praser_comments(id,comment))
        except Exception as e:
          print(id,'error:',e)
  return product_comment

comment = get_comment(10,product_id_list)

df = pd.DataFrame(comment)


df.to_csv(f'{AIRFLOW_PATH}/data/raw/comment_{time_run}.csv',encoding = 'utf-8-sig')