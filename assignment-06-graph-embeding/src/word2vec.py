from gensim.models import Word2Vec
from itertools import combinations

def main():
    # ----------------------------------------
    # 1. Dataset (simulate context)
    # ----------------------------------------
    sentences = [
        ["I", "live", "in", "Vietnam"],
        ["I", "love", "VietNam"],
        ["VN", "is", "beautiful"],
        ["Vietnam", "has", "good", "food"],
        ["Thailand", "is", "beautiful"],
        ["ThaiLand", "has", "good", "food"],
        ["USA", "is", "a", "big", "country"],
        ["UnitedStates", "has", "many", "cities"]
    ]

    # ----------------------------------------
    # 2. Train model
    # ----------------------------------------
    model = Word2Vec(
        sentences=sentences,
        vector_size=20,
        window=3,
        min_count=1,
        workers=1,
        epochs=200
    )

    # ----------------------------------------
    # 3. Danh sách tên cần kiểm tra
    # ----------------------------------------
    names = [
        "Vietnam", "VietNam", "VN",
        "Thailand", "ThaiLand",
        "USA", "UnitedStates"
    ]

    print("\n===== SIMILAR NAME PAIRS =====\n")

    # ----------------------------------------
    # 4. So sánh từng cặp
    # ----------------------------------------
    threshold = 0.6  # ngưỡng giống nhau

    for w1, w2 in combinations(names, 2):
        if w1 in model.wv and w2 in model.wv:
            sim = model.wv.similarity(w1, w2)

            if sim >= threshold:
                print(f"{w1:15s} ~ {w2:15s} -> similarity: {sim:.4f}")

    # ----------------------------------------
    # 5. In similar words cho từng tên
    # ----------------------------------------
    print("\n===== TOP SIMILAR WORDS =====\n")

    for name in names:
        if name in model.wv:
            print(f"\n{name}:")
            similar = model.wv.most_similar(name, topn=3)
            for word, score in similar:
                print(f"  {word:15s} -> {score:.4f}")


if __name__ == "__main__":
    main()