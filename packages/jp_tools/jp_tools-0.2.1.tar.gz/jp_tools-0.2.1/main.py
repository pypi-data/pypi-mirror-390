from jp_tools import download


def main():
    download(
        url="https://raw.githubusercontent.com/gitinference/jp-qcew/refs/heads/main/.gitignore",
        filename=".gitignore",
    )


if __name__ == "__main__":
    main()
