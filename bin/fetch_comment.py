# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(__file__)+"/..")
import nico_comment_import

def main():
    nicovideo = nico_comment_import.NicovideoSevice(nico_comment_import.Config())
    for comment in nicovideo.get_vieo("1397552685").comments(100):
        print(comment.text)


if __name__ == '__main__':
    main()
