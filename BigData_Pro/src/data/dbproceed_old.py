from psycopg2 import sql
import psycopg2
import pandas as pd
import datetime  # để đọc dữ liệu thời gian dạng Unix time
import pytz     # để chuyển đổi sang các múi giờ UTC, hay Viet nam ...
from psycopg2.extras import execute_values

AIRFLOW_PATH = "/opt/airflow"
product_link=(f'{AIRFLOW_PATH}/data/raw/ProductDeatail.xlxs')
comment_link=(f'{AIRFLOW_PATH}/data/raw/Comment.xlxs')
recommend_link=(f'{AIRFLOW_PATH}/data/proceed/final_pair.csv')
host="localhost"
port=5432
database="tikidb"
user='airflow'
password='airflow'

def update_database(product_link=product_link,
                    comment_link=comment_link,
                    recommend_link=recommend_link,
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password= password):

    '''
    product_link : link file chứa sản phẩm
    comment_link : link file chứa comment
    recomend_link : link file chứa gợi ý (File của Quang - schema : product_id1|product_id2|similarity)
    host : hostname
    port : cổng sử dụng
    database : cơ sở dữ liệu sử dụng
    user : tên tài khoản
    password : password tài khoản
    '''
    
    # Kết nối đến PostgreSQL
    conn = psycopg2.connect(
        dbname="", user=user, password=password, host=host, port=port)
    
    cur = conn.cursor()

    # Kiểm tra nếu cơ sở dữ liệu "tikidb" tồn tại
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database}'")
    exists = cur.fetchone()

    # Nếu cơ sở dữ liệu không tồn tại, tạo mới
    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("tikidb")))
        print("Cơ sở dữ liệu 'tikidb' đã được tạo.")
    else:
        print("Cơ sở dữ liệu 'tikidb' đã tồn tại.")


    #Xoá các table nếu nó đã tồn tại.
    # cur.execute(f"DROP TABLE IF EXISTS {"ProductCategory"}")
    # cur.execute(f"DROP TABLE IF EXISTS {"ProductBrand"}")
    # cur.execute(f"DROP TABLE IF EXISTS {"Inventory"}")
    # cur.execute(f"DROP TABLE IF EXISTS {"Comment"}")
    # cur.execute(f"DROP TABLE IF EXISTS {"Brand"}")
    # cur.execute(f"DROP TABLE IF EXISTS {"Category"}")
    # cur.execute(f"DROP TABLE IF EXISTS {"Customer"} CASCADE") # xóa các bảng phụ thuộc vào bảng customer
    # cur.execute(f"DROP TABLE IF EXISTS {"Customer"}")
    # cur.execute(f"DROP TABLE IF EXISTS {"Product"} CASCADE") # xóa các bảng phụ thuộc vào bảng product
    # cur.execute(f"DROP TABLE IF EXISTS {"Product"}")
    # cur.execute(f"DROP TABLE IF EXISTS {"Recommend"}")

    # tables = [
    #     "ProductCategory", "ProductBrand", "Inventory", "Comment", 
    #     "Brand", "Category", "Customer", "Product", "Recommend"
    # ]
    # for table in tables:
    #     cur.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(table)))

    #Load table cần extract
    product_detail_df = pd.read_excel(product_link)   # file excel chứa bảng dữ liệu ProductDetail
    comment_df = pd.read_excel(comment_link)          # file excel chứa bảng dữ liệu Comment
    recommend_df = pd.read_csv(recommend_link)

    ##########################################################Tạo bảng##############################################################
    # 1-Tạo bảng Product
    cur.execute('''
        CREATE TABLE Product (
            product_id INTEGER PRIMARY KEY,
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
            comment_id integer PRIMARY KEY,
            product_id INTEGER REFERENCES Product(product_id),
            customer_id INTEGER REFERENCES Customer(customer_id),
            title VARCHAR(255),
            content TEXT,
            thank_count INTEGER,
            rating NUMERIC,
            created_at varchar(255), 
            is_buyed BOOLEAN,
            purchased_at varchar(255) 
        )
    ''')



    # 5-Tạo bảng Category
    cur.execute('''
        CREATE TABLE Category (
            categories_id  integer PRIMARY KEY,
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
            brand_id  integer PRIMARY KEY,
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
            product_id1 INTEGER ,
            product_id2 INTEGER ,
            similarity  FLOAT
        )
    ''') 


    # Thêm dữ liệu vào bảng Brand
    brand_data = product_detail_df[['brand_id', 'brand_name']].drop_duplicates() ; print("Số lượng dòng trong product_detail_df:", product_detail_df.shape[0])
    brand_insert = brand_data.values.tolist(); print("Số lượng phần tử trong brand_insert:", len(brand_insert))
    execute_values(cur, "INSERT INTO Brand (brand_id, brand_name) VALUES %s ON CONFLICT DO NOTHING", brand_insert)
    # ON CONFLICT DO NOTHING: Tránh lỗi khi có xung đột khoá chính
    # drop_duplicates() để đảm bảo không thêm dữ liệu trùng.



    # Thêm dữ liệu vào bảng Product
    product_data = product_detail_df[['product', 'sku', 'name', 'short_description', 'long_description', 'price', 'list_price', 'discount', 'discount_rate', 'rating_average', 'review_count', 'day_ago_created', 'web_link', 'picture']]
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



    # Thêm dữ liệu vào bảng Inventory  # phải chèn DL bảng product trước thì mới chèn được bảng này
    inventory_data = product_detail_df[['product', 'inventory_status', 'stock_item_qty', 'stock_item_max_sale_qty', 'stock_item_min_sale_qty', 'qty_sold']]
    inventory_insert = inventory_data.values.tolist()
    execute_values(cur, "INSERT INTO Inventory (product_id, inventory_status, stock_item_qty, stock_item_max_sale_qty, stock_item_min_sale_qty, qty_sold) VALUES %s ON CONFLICT DO NOTHING", inventory_insert)


    # Thêm dữ liệu vào bảng ProductCategory  # phải chèn DL vào bảng product và category rồi mới chèn bảng này
    product_category_data = product_detail_df[['product', 'categories_id']].drop_duplicates()
    product_category_insert = product_category_data.values.tolist()
    execute_values(cur, "INSERT INTO ProductCategory (product_id, categories_id) VALUES %s ON CONFLICT DO NOTHING", product_category_insert)



    # Thêm dữ liệu vào bảng ProductBrand  #phải chèn DL bảng product và brand thì mới chèn bảng này được
    product_brand_data = product_detail_df[['product', 'brand_id']].drop_duplicates()
    product_brand_insert = product_brand_data.values.tolist()
    execute_values(cur, "INSERT INTO ProductBrand (product_id, brand_id) VALUES %s ON CONFLICT DO NOTHING", product_brand_insert)


    # Thêm dữ liệu vào bảng Comment  # phải chèn DL bảng product, customer, rồi mới chèn được bảng này
    comment_data = comment_df[['comment_id', 'product_id', 'customer_id', 'title', 'content', 'thank_count', 'rating', 'created_at', 'is_buyed', 'purchased_at']]   # chọn các cột cần thiết từ DataFrame comment_df và gán vào biến comment_data
    # Lấy các product_id từ bảng product
    cur.execute("SELECT product_id FROM product")
    product_ids = set(row[0] for row in cur.fetchall())

    # Lọc dữ liệu trong comment_data chỉ lấy dòng có product_id nằm trong bảng product
    comment_data = comment_data[comment_data['product_id'].isin(product_ids)]

    #comment_data.loc[:, 'created_at'] = pd.to_datetime(comment_data['created_at'], unit='s')
    #comment_data['created_at'] = comment_data['created_at'].replace('NaT', pd.to_datetime('today'))
    #comment_data.loc[:, 'purchased_at'] = pd.to_datetime(comment_data['purchased_at'], unit='s')
    #comment_data['purchased_at'] = comment_data['purchased_at'].replace('NaT', pd.to_datetime('today'))
    #comment_data['created_at'] = comment_data['created_at'].apply(pd.to_datetime, unit='s')
    #comment_data['created_at'] = pd.to_datetime(comment_data['created_at'], unit='s')  #  chuyển đổi các gtrị trong cột created_at thành kiểu dữ liệu timestamp
    #comment_data['purchased_at'] = pd.to_datetime(comment_data['purchased_at'], unit='s')  # Trước khi chèn dl vào CSDL, bạn cần chuyển đổi các gtrị trong cột purchased_at thành kiểu dữ liệu timestamp
    # errors='ignore': Nếu có giá trị không thể chuyển đổi thành datetime (ví dụ: null hoặc giá trị không hợp lệ), thì sẽ bỏ qua giá trị đó


    comment_insert = comment_data.values.tolist()       #  chuyển đổi DataFrame comment_data thành một danh sách các danh sách. Mỗi danh sách con đại diện cho một hàng dữ liệu sẽ được chèn vào cơ sở dữ liệu.
    try:
        execute_values(cur, "INSERT INTO Comment (comment_id, product_id, customer_id, title, content, thank_count, rating, created_at, is_buyed, purchased_at) VALUES %s ON CONFLICT DO NOTHING", comment_insert)  # on conflic do nothing: Câu lệnh này cho biết nếu có xung đột khi chèn thì không làm gì cả
    except  Exception as e: # bắt tất cả các lỗi
        print("Lỗi khi chèn dữ liệu vào bảng Comment: ", e)


    #Thêm dữ liệu comment
    recommend_data = recommend_df[['product_id1','product_id2','similarity']]
    recommend_insert = recommend_data.values.tolist()
    execute_values(cur, "INSERT INTO Recommend (product_id1, product_id2,similarity) VALUES %s ON CONFLICT DO NOTHING", recommend_insert)

      
    # Đóng kết nối
    conn.commit()
    cur.close()
    conn.close()



    return True

update_database()
