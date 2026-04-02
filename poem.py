import updater_http


def print_poem():
    title = "静夜思"
    author = "李白白"
    content = [
        "床前明月光，",
        "疑是地上霜。",
        "举头望明月，",
        "低头思故乡。"
    ]
    
    print(f"《{title}》")
    print(f"作者：{author}")
    print("-" * 15)
    for line in content:
        print(line)

if __name__ == "__main__":
    updater_http.check_and_update()
    print_poem()
