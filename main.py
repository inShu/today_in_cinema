#! /usr/bin/env python3
import requests
import traceback
import operator
import json
import time


def make_get(url):
    resp = requests.get(url)

    if resp.status_code != 200:
        res = "Error while GET'ing of {0}. Code [{1}]: {2}".format(url, resp.status_code, resp.text)
        print(res)
        raise BaseException(res)

    return resp.text


def get_cinema():
    html = make_get("https://www.kinopoisk.ru/afisha/new/city/2/sort_by/date/")


def main():
    return 0

main()