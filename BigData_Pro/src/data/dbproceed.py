import pandas as pd
from psycopg2 import sql, connect
from psycopg2.extras import execute_values
import datetime
import pytz
import requests

AIRFLOW_PATH = "/opt/airflow"
# AIRFLOW_PATH = "."
product_link = (f'{AIRFLOW_PATH}/data/raw/ProductDetail.csv')
comment_link = (f'{AIRFLOW_PATH}/data/raw/Comment.csv')
recommend_link = (f'{AIRFLOW_PATH}/data/proceed/final_pair.csv')

host="host.docker.internal"
port = 5432
database = "tikidb"
user = 'superset'
password = 'superset'

# file_path = './data/raw/ProductDetail.xlsx'
file_path=product_link

def update_database():

    # Connect to checking database exist
    conn = connect(
        dbname="postgres", user=user, password=password, host=host, port=port)
    
    # Turn on autocommit to allow create DB outside of transaction
    conn.autocommit = True
    cur = conn.cursor()

    # Kiểm tra nếu cơ sở dữ liệu "tikidb" tồn tại
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database}'")
    exists = cur.fetchone()

    # Nếu cơ sở dữ liệu không tồn tại, tạo mới
    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
        print(f"Cơ sở dữ liệu '{database}' đã được tạo.")
    else:
        print(f"Cơ sở dữ liệu '{database}' đã tồn tại.")

    # Close checking section
    cur.close()
    conn.close()

    #=====#

    # New section to import data
    conn = connect(
        dbname=database, user=user, password=password, host=host, port=port)
    
    #turn on autocommmit to allow create db outside section
    conn.autocommit = True
    
    cur = conn.cursor()

    # Kiểm tra nếu cơ sở dữ liệu "tikidb" tồn tại
    # cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database}'")
    # exists = cur.fetchone()

    # Nếu cơ sở dữ liệu không tồn tại, tạo mới
    # if not exists:
    #     cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("tikidb")))
    #     print("Cơ sở dữ liệu 'tikidb' đã được tạo.")
    # else:
    #     print("Cơ sở dữ liệu 'tikidb' đã tồn tại.")

    # Xóa các bảng nếu đã tồn tại

    #Xoá các table nếu nó đã tồn tại.
    cur.execute(f"DROP TABLE IF EXISTS {"ProductCategory"}")
    cur.execute(f"DROP TABLE IF EXISTS {"ProductBrand"}")
    cur.execute(f"DROP TABLE IF EXISTS {"Inventory"}")
    cur.execute(f"DROP TABLE IF EXISTS {"Comment"}")
    cur.execute(f"DROP TABLE IF EXISTS {"Brand"}")
    cur.execute(f"DROP TABLE IF EXISTS {"Category"}")
    cur.execute(f"DROP TABLE IF EXISTS {"Customer"} CASCADE") # xóa các bảng phụ thuộc vào bảng customer
    cur.execute(f"DROP TABLE IF EXISTS {"Customer"}")
    cur.execute(f"DROP TABLE IF EXISTS {"Product"} CASCADE") # xóa các bảng phụ thuộc vào bảng product
    cur.execute(f"DROP TABLE IF EXISTS {"Product"}")
    cur.execute(f"DROP TABLE IF EXISTS {"Recommend"}")

        
    # Đọc dữ liệu từ file
    product_detail_df = pd.read_csv(product_link)
    comment_df = pd.read_csv(comment_link)
    recommend_df = pd.read_csv(recommend_link)

    ##########################################################
    # Tạo bảng
    ##########################################################

    # 1-Tạo bảng Product
    cur.execute('''
        CREATE TABLE Product (
            product_id BIGINT PRIMARY KEY,
            sku VARCHAR(50),
            name VARCHAR(255),
            short_description TEXT,
            long_description TEXT,
            price NUMERIC,
            list_price NUMERIC,
            discount NUMERIC,
            discount_rate NUMERIC,      
            rating_average NUMERIC,
            review_count INTEGER,
            day_ago_created INTEGER,
            web_link TEXT,
            picture TEXT
        )
    ''')

    # 2- Tạo bảng Inventory
    cur.execute('''
        CREATE TABLE Inventory (
            product_id INTEGER REFERENCES Product(product_id),
            inventory_status VARCHAR(50),
            stock_item_qty INTEGER,
            stock_item_max_sale_qty INTEGER,
            stock_item_min_sale_qty INTEGER,
            qty_sold INTEGER
        )
    ''')

    # 3 - Tạo bảng Customer
    cur.execute('''
        CREATE TABLE Customer (
            customer_id Integer PRIMARY KEY,
            customer_name VARCHAR(255)
        )
    ''')

    # 4-Tạo bảng Comment
    cur.execute('''
        CREATE TABLE Comment (
            comment_id INTEGER PRIMARY KEY,
            product_id INTEGER REFERENCES Product(product_id),
            customer_id INTEGER REFERENCES Customer(customer_id),
            title VARCHAR(255),
            content TEXT,
            thank_count INTEGER,
            rating NUMERIC,
            created_at TIMESTAMP, 
            is_buyed BOOLEAN,
            purchased_at TIMESTAMP
        )
    ''')

    # 5-Tạo bảng Category
    cur.execute('''
        CREATE TABLE Category (
            categories_id  INTEGER PRIMARY KEY,
            categories_name VARCHAR(255),
            main_category VARCHAR(255)
        )
    ''')

    # 6-Tạo bảng ProductCategory
    cur.execute('''
        CREATE TABLE ProductCategory (
            product_id INTEGER REFERENCES Product(product_id),
            categories_id INTEGER REFERENCES Category(categories_id)
        )
    ''')

    # 7-Tạo bảng Brand
    cur.execute('''
        CREATE TABLE Brand (
            brand_id  INTEGER PRIMARY KEY,
            brand_name VARCHAR(255)
        )
    ''')

    # 8-Tạo bảng ProductBrand
    cur.execute('''
        CREATE TABLE ProductBrand (
            product_id INTEGER REFERENCES Product(product_id),
            brand_id INTEGER REFERENCES Brand(brand_id)
        )
    ''')

    # 9-Tạo bảng Recommend
    cur.execute('''
        CREATE TABLE Recommend (
            product_id1 INTEGER,
            product_id2 INTEGER,
            similarity FLOAT
        )
    ''')

    ##########################################################
    # Thêm dữ liệu vào các bảng
    ##########################################################

    # Thêm dữ liệu vào bảng Brand
    brand_data = product_detail_df[['brand_id', 'brand_name']].drop_duplicates()
    brand_insert = brand_data.values.tolist()
    execute_values(cur, "INSERT INTO Brand (brand_id, brand_name) VALUES %s ON CONFLICT DO NOTHING", brand_insert)

    # Thêm dữ liệu vào bảng Product
    product_data = product_detail_df[['product_id', 'sku', 'name', 'short_description', 'long_description', 'price', 'list_price', 'discount', 'discount_rate', 'rating_average', 'review_count', 'day_ago_created', 'web_link', 'picture']]
    product_insert = product_data.values.tolist()
    execute_values(cur, "INSERT INTO Product (product_id, sku, name, short_description, long_description, price, list_price, discount, discount_rate, rating_average, review_count, day_ago_created, web_link, picture) VALUES %s ON CONFLICT DO NOTHING", product_insert)

    # Thêm dữ liệu vào bảng Customer
    customer_data = comment_df[['customer_id', 'customer_name']].drop_duplicates()
    customer_insert = customer_data.values.tolist()
    execute_values(cur, "INSERT INTO Customer (customer_id, customer_name) VALUES %s ON CONFLICT DO NOTHING", customer_insert)

    # Thêm dữ liệu vào bảng Category
    category_data = product_detail_df[['categories_id', 'categories_name', 'main_category']].drop_duplicates()
    category_insert = category_data.values.tolist()
    execute_values(cur, "INSERT INTO Category (categories_id, categories_name, main_category) VALUES %s ON CONFLICT DO NOTHING", category_insert)

    # Thêm dữ liệu vào bảng Inventory
    inventory_data = product_detail_df[['product_id', 'inventory_status', 'stock_item_qty', 'stock_item_max_sale_qty', 'stock_item_min_sale_qty', 'qty_sold']]
    inventory_insert = inventory_data.values.tolist()
    execute_values(cur, "INSERT INTO Inventory (product_id, inventory_status, stock_item_qty, stock_item_max_sale_qty, stock_item_min_sale_qty, qty_sold) VALUES %s ON CONFLICT DO NOTHING", inventory_insert)

    # Thêm dữ liệu vào bảng ProductCategory
    product_category_data = product_detail_df[['product_id', 'categories_id']].drop_duplicates()
    product_category_insert = product_category_data.values.tolist()
    execute_values(cur, "INSERT INTO ProductCategory (product_id, categories_id) VALUES %s ON CONFLICT DO NOTHING", product_category_insert)

    # Thêm dữ liệu vào bảng ProductBrand
    product_brand_data = product_detail_df[['product_id', 'brand_id']].drop_duplicates()
    product_brand_insert = product_brand_data.values.tolist()
    execute_values(cur, "INSERT INTO ProductBrand (product_id, brand_id) VALUES %s ON CONFLICT DO NOTHING", product_brand_insert)

    # Chuyển đổi các cột thời gian cho Comment
    comment_df['created_at'] = pd.to_datetime(comment_df['created_at'], errors='coerce')
    comment_df['purchased_at'] = pd.to_datetime(comment_df['purchased_at'], errors='coerce')

    # Thêm dữ liệu vào bảng Comment
    comment_data = comment_df[['comment_id', 'product_id', 'customer_id', 'title', 'content', 'thank_count', 'rating', 'created_at', 'is_buyed', 'purchased_at']]
    comment_insert = comment_data.values.tolist()
    execute_values(cur, "INSERT INTO Comment (comment_id, product_id, customer_id, title, content, thank_count, rating, created_at, is_buyed, purchased_at) VALUES %s ON CONFLICT DO NOTHING", comment_insert)

    # Thêm dữ liệu vào bảng Recommend
    recommend_data = recommend_df[['product_id1', 'product_id2', 'similarity']]
    recommend_insert = recommend_data.values.tolist()
    execute_values(cur, "INSERT INTO Recommend (product_id1, product_id2, similarity) VALUES %s ON CONFLICT DO NOTHING", recommend_insert)

    # List of tables to query
    tables = ['Product', 'Customer', 'Comment', 'Inventory', 'Category', 'ProductCategory', 'Brand', 'ProductBrand', 'Recommend']

    # Loop over each table and get the record count
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"Number records  {table}: {count}")

    #export database herre

    conn.commit()
    cur.close()
    conn.close()

    print("Data updated.")


update_database()