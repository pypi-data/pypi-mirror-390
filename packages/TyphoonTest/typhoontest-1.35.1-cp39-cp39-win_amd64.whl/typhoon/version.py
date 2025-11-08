def get_typhoontest_version():
    """Typhoontest official version is registered in this function"""
    import importlib.metadata

    return importlib.metadata.version("typhoontest")


if __name__ == "__main__":
    print(get_typhoontest_version())
