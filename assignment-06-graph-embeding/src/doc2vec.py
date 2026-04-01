# ============================================
# DOC2VEC - PRINT DỄ HIỂU (EXPLAINABLE OUTPUT)
# ============================================

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np


def print_line():
    print("=" * 60)


def explain_similarity(score):
    if score >= 0.85:
        return "RẤT GIỐNG NHAU"
    elif score >= 0.75:
        return "GIỐNG NHAU"
    elif score >= 0.6:
        return "KHÁ GIỐNG"
    else:
        return "KHÔNG GIỐNG"


def main():

    # ----------------------------------------
    # 1. Dữ liệu
    # ----------------------------------------
    documents = {
        "Task_A_Credit": """
        Nhân viên quan hệ khách hàng tiếp nhận hồ sơ vay vốn từ khách hàng cá nhân.
        Thực hiện kiểm tra tính đầy đủ của các chứng từ pháp lý và bảng lương.
        Sau đó tiến hành nhập dữ liệu lên hệ thống để khởi tạo yêu cầu xét duyệt hạn mức tín dụng
        và đánh giá tài sản đảm bảo.
        """,

        "Task_B_Card": """
        Bộ phận vận hành thẻ tiếp nhận yêu cầu phát hành thẻ tín dụng mới.
        Thực hiện xác minh danh tính khách hàng qua hệ thống KYC.
        Sau khi phê duyệt tiến hành khởi tạo thông số thẻ trên phôi vật lý
        và gửi thông báo kích hoạt mã PIN qua ứng dụng ngân hàng số cho người dùng.
        """,

        "Task_C_International_Payment": """
        Chuyên viên thanh toán quốc tế kiểm tra bộ chứng từ xuất nhập khẩu
        và yêu cầu phát hành thư tín dụng LC.
        Thực hiện đối chiếu các điều khoản thanh toán với quy định của ngân hàng trung ương.
        Sau khi xác nhận tính hợp lệ lệnh chuyển tiền ngoại tệ sẽ được phê duyệt qua hệ thống SWIFT.
        """
    }

    # ----------------------------------------
    # 2. TaggedDocument
    # ----------------------------------------
    tagged_data = []
    for tag, text in documents.items():
        words = text.lower().split()
        tagged_data.append(TaggedDocument(words=words, tags=[tag]))

    # ----------------------------------------
    # 3. Train model
    # ----------------------------------------
    model = Doc2Vec(vector_size=50, window=5, min_count=1, workers=1, epochs=300)
    model.build_vocab(tagged_data)
    model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)

    # ----------------------------------------
    # 4. VECTOR (giải thích rõ)
    # ----------------------------------------
    print_line()
    print("VECTOR BIỂU DIỄN CHO MỖI TASK (chỉ in 5 chiều đầu)\n")

    for tag in documents.keys():
        print(f"Task: {tag}")
        print(f"Vector: {model.dv[tag][:5]}")
        print("→ Đây là vector đại diện cho nội dung của task\n")

    # ----------------------------------------
    # 5. SIMILARITY (giải thích)
    # ----------------------------------------
    print_line()
    print("PHÂN TÍCH ĐỘ TƯƠNG ĐỒNG GIỮA CÁC TASK\n")

    tasks = list(documents.keys())

    for i in range(len(tasks)):
        for j in range(i + 1, len(tasks)):
            t1 = tasks[i]
            t2 = tasks[j]

            v1 = model.dv[t1]
            v2 = model.dv[t2]

            sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            label = explain_similarity(sim)

            print(f"{t1} ↔ {t2}")
            print(f"→ Similarity = {sim:.4f}")
            print(f"→ Đánh giá: {label}\n")

    # ----------------------------------------
    # 6. MOST SIMILAR (giải thích)
    # ----------------------------------------
    print_line()
    print("TASK GIỐNG NHAU NHẤT CHO MỖI TASK\n")

    for tag in tasks:
        print(f"\nTask: {tag}")

        similar = model.dv.most_similar(tag, topn=2)

        for sim_tag, score in similar:
            label = explain_similarity(score)

            print(f"→ Gần nhất: {sim_tag}")
            print(f"   Similarity: {score:.4f}")
            print(f"   Đánh giá: {label}")


if __name__ == "__main__":
    main()