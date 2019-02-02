#! /usr/bin/env python3
import requests
import datetime
import time
import html
import traceback
import os

from telegram.ext import Updater

proxy = {"http": "http://tor:8118"}
updater = Updater(
	token=os.environ["BOT_TOKEN"],
	request_kwargs=
	{
		"proxy_url":"http://tor:8118",
		"read_timeout": 60
	}
)
updater.start_polling()

class Movie:
    def __init__(self, name, date, id):
        self.date = date
        self.name = name
        self.id = id
        self.actors = []
        self.image = "https://st.kp.yandex.net/images/film_big/{0}.jpg".format(id)
        self.producer = ""
        self.description = ""


def make_get(url):
    resp = requests.get(url)

    if resp.status_code != 200:
        raise BaseException("Error while GET'ing of {0}. Code [{1}]".format(url, resp.status_code))

    return resp.text


def get_movie_data(movie):
    text = make_get("https://www.kinopoisk.ru/film/" + movie.id)
    print("Getting movie data for " + movie.name)

    index = text.find(">", text.find("<a href", text.find("itemprop=\"director")))
    end_index = text.find("<", index)
    movie.producer = text[index + 1:end_index]

    count = 4
    index = text.find("В главных ролях")
    if index > 0:
        index = text.find("ul", index)
        movie.actors.clear()
        while count > 0:
            index = text.find("\">", text.find("<a href", text.find("<li", index + 1)))
            end_index = text.find("<", index)
            movie.actors.append(text[index + 2:end_index])
            count -= 1
    else:
        index = 0

    index = text.find("\">", text.find("itemprop=\"description", index))
    end_index = text.find("<", index)
    movie.description = html.unescape(text[index + 2:end_index])


def get_cinema():
    text = make_get("https://www.kinopoisk.ru/afisha/new/city/2/sort_by/date/#sort")

    index = text.find("<div class=\"filmsListNew")
    end_items_index = text.find("<div class=\"moreFilmsButton", index)

    today = []

    while True:
        index = text.find("<div class=\"item", index)
        if index < 0 or index > end_items_index:
            break

        index = text.find("id=\"", index)
        end_index = text.find("\"", index + 5)
        movie_id = text[index + 4:end_index]

        index = text.find(">", text.find("class=\"film-link", text.find("<div class=\"name", index)))
        end_index = text.find("<", index + 1)
        movie_name = html.unescape(text[index + 1:end_index])

        index = text.find("<div class=\"date", index)
        date_index = text.find("dates/", index)
        date_end = text.find(".png", date_index)
        num1 = text[date_index + 6:date_end]

        index = text.find("dates/month_", index + 1)
        end_index = text.find(".png", index)
        month = text[index + 12:end_index]

        date_index = text.find("dates/", date_index + 1)

        if date_index > 0 and date_index < index:
            date_end = text.find(".png", date_index)
            num2 = text[date_index + 6:date_end]
            day = int(num1) * 10 + int(num2)
        else:
            day = int(num1)

        formatted_date = "{0:0>2d}-{1}".format(day, month)
        print("{0:0>2d}.{1} id {2} {3}".format(day, month, movie_id, movie_name))

        if datetime.datetime.today().strftime("%d-%m") == formatted_date:
            today.append(Movie(movie_name, formatted_date, movie_id))

    for movie in today:
        time.sleep(120)
        get_movie_data(movie)
        while movie.actors[0].find("html") > 0:
            print("Stuck for " + movie.name)
            time.sleep(600)
            get_movie_data(movie)

    return today


def announce_movie(movie):
    print("=================================")
    print("{0} {1} {2}".format(movie.name, movie.id, movie.date))
    print("{0}".format(movie.actors))
    print("{0}".format(movie.producer))
    print("{0}".format(movie.image))
    print("{0}".format(movie.description))
    print("=================================")

    actors_str = ""
    for actor in movie.actors:
        actors_str += actor + ", "
    actors_str = actors_str[:-2]
    msg = "Режиссёр: {0}\n".format(movie.producer)
    if len(movie.actors) > 0:
        msg += "В ролях: {0}\n".format(actors_str)
    msg += "Сюжет: \"{0}\"".format(movie.description)
    updater.bot.send_photo(chat_id="@todayincinemaru", photo=movie.image, caption=msg, timeout=180)


def check():
    try:
        today = datetime.datetime.today().strftime("%d-%m")

        file = open("check", "r")
        last = file.read()
        file.close()

        return today != last
    except BaseException:
        return True


def fix_check():
    today = datetime.datetime.today().strftime("%d-%m")

    file = open("check", "w")
    file.write(today)
    file.close()


def main():
    while True:
        try:
            if check():
                today = get_cinema()

                for movie in today:
                    print("Announce " + movie.name)
                    announce_movie(movie)
                    time.sleep(300)
                fix_check()
        except BaseException as exp:
            msg = "Traceback: " + traceback.format_exc() + "\n" + "Exception: " + str(exp)
            print("Traceback: " + traceback.format_exc())
            print("Exception: " + str(exp))
            updater.bot.send_message(chat_id=-1001416077726, text="today_in_cinema: " + msg, timeout=180)

        time.sleep(60*60)


main()
