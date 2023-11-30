import sys
from ingen.main import init

if __name__ == '__main__':
    print(sys.path)
    init(sys.argv[1:])
