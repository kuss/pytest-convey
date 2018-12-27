import os
import sys


if __name__ == '__main__':
    sys.path.append(os.path.dirname(__file__))

    from pytest_board.command import main
    main()
