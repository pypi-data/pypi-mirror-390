import fsspec
import stat

def main():
    filename = "./pyproject.toml"
    fs = fsspec.filesystem("file", path="bar")

    st = fs.stat(filename)
    can_read = stat.S_IRUSR & st['mode']
    can_write = stat.S_IRUSR & st['mode']
    other = stat.S_IROTH  & st['mode']

    print(st)


if __name__ == '__main__':
    main()