import types


def is_encrypted(filepath):
    infile = open(filepath, 'r')
    text = infile.readlines()
    print(text[0])


def main():
    filepath = r"c:\Users\Vasily\OneDrive\Macro\PYTHON\SETUP_read\CFGs\TestPlots.ig~.bjson"
    is_encrypted(filepath)


if __name__ == '__main__':
    main()
