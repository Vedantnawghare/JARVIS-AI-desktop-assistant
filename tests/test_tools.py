from app.tools.browser import open_url


def main():
    result = open_url("https://www.youtube.com")
    print(result)


if __name__ == "__main__":
    main()