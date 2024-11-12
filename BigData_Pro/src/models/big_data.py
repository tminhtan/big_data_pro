import pandas as pd
from sentence_transformers import SentenceTransformer, util
import os

# Đường dẫn đến file CSV trong hệ thống tệp
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
product_link = (f'{AIRFLOW_PATH}/data/raw/ProductDetail.csv')
comment_link = (f'{AIRFLOW_PATH}/data/raw/Comment.csv')
recommend_link = (f'{AIRFLOW_PATH}/data/proceed/final_pair.csv')

host="host.docker.internal"
port = 5432
database = "tikidb"
user = 'airflow'
password = 'airflow'

file_path=product_link

    # Đọc dữ liệu từ file CSV
df = pd.read_csv(file_path)  # Bỏ qua các dòng có lỗi nếu có

    # Xử lý các bước tiếp theo như trước
df['short_description'] = df['short_description'].str.replace('...', '', regex=False).str.strip()
df = df.dropna(subset=['long_description', 'short_description'], how='all')
print(df)

"""# Thống kê mô tả"""

df['main_category'].value_counts()


"""# Mô hình PhoBERT"""

def similarity_pairs(df, threshold=0.83):
    model = SentenceTransformer('vinai/phobert-base')
    grouped = df.groupby('main_category')['name'].apply(list).to_dict()
    pairs = []

    for category, descriptions in grouped.items():
        embeddings = model.encode(descriptions, convert_to_tensor=True)
        similarities = util.pytorch_cos_sim(embeddings, embeddings)
        similarity_pairs = []

        for i, row in enumerate(similarities):
            for j, similarity in enumerate(row):
                if similarity > threshold:
                    similarity_pairs.append((i, j, similarity.item()))

        similarity_pairs.sort(key=lambda x: x[2], reverse=True)

        for i in range(len(descriptions)):
            count = 0
            for j, (index_i, index_j, similarity) in enumerate(similarity_pairs):
                if index_i == i and count < 10:
                    pairs.append({
                        'Index_List': (index_i, index_j),
                        'Similarity': similarity,
                        'Main_Category': category,
                        'Name_1': descriptions[index_i],
                        'Name_2': descriptions[index_j]
                    })
                    count += 1

    return pairs

# Gọi hàm và hiển thị kết quả
results = similarity_pairs(df)
print("\nFinal pairs:")
for pair in results:
    print(pair)

# Lưu kết quả vào CSV
results_df = pd.DataFrame(results)
results_df = results_df.assign(
    product_id1_temp=lambda x: x['Index_List'].apply(lambda idx: idx[0]),
    product_id2_temp=lambda x: x['Index_List'].apply(lambda idx: idx[1]),
    similarity=lambda x: x['Similarity'].round(4)
).drop(columns='Index_List')[['product_id1_temp', 'product_id2_temp', 'similarity']]#to_csv(recommend_link, index=False)
df = df[['product_id']]
merged_df = pd.merge(results_df, df, left_on='product_id1_temp', right_index=True, how='inner')
merged_df.rename(columns={'product_id': 'product_id1'}, inplace=True)
merged_df = pd.merge(merged_df, df, left_on='product_id2_temp', right_index=True, how='inner')
merged_df.rename(columns={'product_id': 'product_id2'}, inplace=True)
merged_df = merged_df.drop(columns=['product_id1_temp', 'product_id2_temp'])
merged_df = merged_df[['product_id1','product_id2','similarity']]
merged_df.to_csv(recommend_link, index=False)