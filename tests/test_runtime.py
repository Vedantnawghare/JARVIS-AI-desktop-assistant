from app.core.runtime import JarvisRuntime


def main():
    runtime = JarvisRuntime()
    runtime.start()

    print(
        runtime.browser_tools.search_youtube(
            "OSI model"
        )
    )

    input("Press Enter to close JARVIS...")

    runtime.shutdown()


if __name__ == "__main__":
    main()