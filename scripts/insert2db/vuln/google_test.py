#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests

def get_num_google(keyword):
    url = "https://google.com/search?q={}".format(keyword)
    res = requests.get(url)
    html = res.text
    print(html)
    num_str = html.split(">&#32004; ")[1].split(" &#20214;")[0]
    num_str = "".join( [ str for str in num_str.split(",") ])
    return num_str

if __name__ == "__main__":
    num = get_num_google(sys.argv[1])
    print(num)

