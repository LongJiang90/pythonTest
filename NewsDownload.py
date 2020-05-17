import urllib2
import HTMLParser
import random


class GetList(HTMLParser.HTMLParser):  # get the url list of all articles
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.outputFlag = False
        self.count = 0
        self.link = ''
        self.linkList = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for key, value in attrs:
                if key == 'data-pb-field':
                    if value == 'web_headline':
                        self.outputFlag = True
                if key == 'href':
                    self.link = value

    def handle_data(self, data):
        if self.outputFlag:
            self.count += 1
            print
            self.count
            print
            data
            print
            self.link
            self.linkList.append(self.link)
            self.outputFlag = False


class GetArticle(HTMLParser.HTMLParser):  # get article content
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.list = ['headline', 'name']
        self.flag = False
        self.articleFlag = False

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == 'itemprop':
                if value in self.list:
                    self.flag = True
            if tag == 'article':
                self.articleFlag = True

    def handle_data(self, data):
        if self.articleFlag:
            print
            data
        elif self.flag:
            print
            data
            self.flag = False

    def handle_endtag(self, tag):
        if tag == 'article':
            self.articleFlag = False

if __name__ == '__main__':
    res = urllib2.urlopen('https://www.washingtonpost.com/')
    my = GetList()
    my.feed(res.read().decode('utf8'))
    print
    "------From WashingtonPost-----"
    print
    "------------------------------"
    res2 = urllib2.urlopen(my.linkList[random.randint(1, len(my.linkList))])
    ar = GetArticle()
