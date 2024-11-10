# -*- coding: utf-8 -*-
import requests
import pandas as pd
from io import StringIO
from sentence_transformers import SentenceTransformer, util

# ID của Google Sheet (chỉ lấy phần giữa /d/ và /edit)
spreadsheet_id = '1ij3EJNsanCMh5xXFRxNTAi2nEmshLg3h'
sheet_name = 'Product Detail'
AIRFLOW_PATH = "/opt/airflow"

# Đường dẫn đến file trong hệ thống tệp
file_path = './data/raw/ProductDetail.xlsx'
# url=(f'{AIRFLOW_PATH}/data/raw/ProductDetail.xlsx)')

try:
    # Đọc dữ liệu từ file Excel
    df = pd.read_csv(file_path)
    
    # Xử lý các bước tiếp theo như trước
    df['short_description'] = df['short_description'].str.replace('...', '', regex=False).str.strip()
    df = df.dropna(subset=['long_description', 'short_description'], how='all')
    print(df)
except Exception as e:
    print(f"Lỗi khi đọc dữ liệu từ file Excel: {e}")

"""# Thống kê mô tả"""

df['main_category'].value_counts()


"""# Mô hình PhoBERT"""


def similarity_pairs(df, threshold=0.83):
    # Giới hạn số lượng hàng
    #df = df.head(20)

    # Tải mô hình PhoBERT
    model = SentenceTransformer('vinai/phobert-base')

    # Nhóm các giá trị theo main_category
    grouped = df.groupby('main_category')['name'].apply(list).to_dict()

    pairs = []

    # So sánh các danh sách trong cùng một main_category
    for category, descriptions in grouped.items():
        print(f"Comparing names in category '{category}':")
        print("Names:", descriptions)

        # Lấy embeddings cho danh sách mô tả
        embeddings = model.encode(descriptions, convert_to_tensor=True)
        print("Embeddings:", embeddings)

        # Tính toán cosine similarity
        similarities = util.pytorch_cos_sim(embeddings, embeddings)
        print("Similarity matrix:", similarities)

        # Lưu trữ các cặp độ tương đồng
        similarity_pairs = []

        for i, row in enumerate(similarities):
            for j, similarity in enumerate(row):
                #if i != j and similarity > threshold:  # Tránh so sánh chính nó
                if similarity > threshold:
                    similarity_pairs.append((i, j, similarity.item()))

        # Sắp xếp các cặp theo độ tương đồng giảm dần
        similarity_pairs.sort(key=lambda x: x[2], reverse=True)

        # Ghép nối mô tả dựa trên độ tương đồng cao nhất
        for i in range(len(descriptions)):
            count = 0  # Đếm số cặp đã thêm cho sản phẩm ở cột đầu tiên
            for j, (index_i, index_j, similarity) in enumerate(similarity_pairs):
                if index_i == i and count < 10:  # Nếu sản phẩm ở cột đầu tiên và chưa đạt 10 cặp
                    pairs.append({
                        'Index_List': (index_i, index_j),
                        'Similarity': similarity,
                        'Main_Category': category,
                        'Name_1': descriptions[index_i],
                        'Name_2': descriptions[index_j]
                    })
                    count += 1  # Tăng số lượng cặp đã thêm
                    #print(f"Added pair: Index_List={index_i}, Similarity={similarity}, Main_Category={category}, Names=({descriptions[index_i]}, {descriptions[index_j]})")

    return pairs

# Gọi hàm
results = similarity_pairs(df)

# Hiển thị kết quả
print("\nFinal pairs:")
for pair in results:
    print(pair)



# Lưu kết quả hiển thị vào CSV với độ tương đồng được làm tròn và tách chỉ số
results_df = pd.dataframe(results)
# results_df.assign(
#     Index_1=lambda x: x['Index_List'].apply(lambda idx: idx[0]),
#     Index_2=lambda x: x['Index_List'].apply(lambda idx: idx[1]),
#     Similarity=lambda x: x['Similarity'].round(4)
# ).drop(columns='Index_List')[['product_id1', 'product_id2', 'similarity']].to_csv(f'{AIRFLOW_PATH}/data/proceed/new_final_pairs.csv', index=False)
results_df.assign(
    Index_1=lambda x: x['Index_List'].apply(lambda idx: idx[0]),
    Index_2=lambda x: x['Index_List'].apply(lambda idx: idx[1]),
    Similarity=lambda x: x['Similarity'].round(4)
).drop(columns='Index_List')[['product_id1', 'product_id2', 'similarity']].to_csv('./data/proceed/new_final_pairs.csv', index=False)