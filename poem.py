import updater_http


def print_poem():
    title = "黄鹤楼送孟浩然之广陵"
    author = "李白"
    content = [
        "故人西辞黄鹤楼，",
        "烟花三月下扬州",
        "孤帆远影碧空尽",
        "唯见长江天际流"
    ]
    
    print(f"《{title}》")
    print(f"作者：{author}")
    print("-" * 15)
    for line in content:
        print(line)

if __name__ == "__main__":
    updater_http.check_and_update()
    print_poem()
