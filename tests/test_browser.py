from app.browser.browser import search_youtube


def main():
    result = search_youtube("OSI model")
    print(result)


if __name__ == "__main__":
    main()