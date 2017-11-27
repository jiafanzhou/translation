#!/usr/bin/env python
# encoding=utf-8

'''
Created on Jul 11, 2014
The main module to start the CLI
@author: ejiafzh
'''

import codecs
import httplib2
import os
import re
import sys
import traceback
import urllib


class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class MyDictionary(object):
    '''
    Represents my dictionary in youdao CLI.
    '''

    def __init__(self, word):
        '''
        Constructor of MyDictionary
        '''
        self.word = word
        self.pronounce = None
        self.translate = None
        self.networkTranslation = None
        self.phrase = None
        self.synonym = None
        self.wiki = None
        self.sentence = None

    def __check_and_print__(self, target, mycolor=color.END):
        if target is not None:
            print mycolor + target + color.END

    def print_word(self):
        self.__check_and_print__(self.word)

    def print_pronounce(self):
        self.__check_and_print__(self.pronounce, color.BLUE)

    def print_translate(self):
        self.__check_and_print__(self.translate, color.RED)

    def print_network_translate(self):
        if self.networkTranslation is not None:
            print color.UNDERLINE + "\nNetwork translation:" + color.END
        self.__check_and_print__(self.networkTranslation)

    def print_phrase(self):
        self.__check_and_print__(self.phrase)

    def print_synonym(self):
        self.__check_and_print__(self.synonym)

    def print_wiki(self):
        self.__check_and_print__(self.wiki)

    def print_sentence(self):
        if self.sentence is not None:
            print color.UNDERLINE + "\nSentences:" + color.END
        self.__check_and_print__(self.sentence, color.CYAN)


h = httplib2.Http()
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.4 (KHTML, like \
Gecko) Chrome/22.0.1229.94 Safari/537.4"

mydict = None


def translate(word_input):
    '''
    Translate the given word
    English: http://dict.youdao.com/m/search?keyfrom=dict.mindex&vendor=&q=
    '''

    # replace speacial characters in word input
    word = urllib.quote(word_input)

    global mydict
    mydict = MyDictionary(word)

    url = 'http://dict.youdao.com/m/search?keyfrom=dict.mindex&vendor=&q=' + \
        word
    pc_url = 'http://dict.youdao.com/search?keyfrom=webwordbook&q=' + word

    response, content = h.request(url)

    # re.S -> make dot match newline
    # re.X -> # ignore whitespace and comments
    patten = re.compile(
        r'''
        <div><span><b>.*?</b></span>(.*?)
        <div\ class="content">(.*?)</div>
        ''', re.S | re.X
    )
    raw_result = patten.findall(content)

    if len(raw_result) != 0:
        # if basic result found

        result = raw_result[0]  # list of results

        # 1. find pronouncation
        # from a list of tuples
        pronouncePattern = re.compile(r'<span>(.*?)</span>', re.S)

        presult = pronouncePattern.findall(result[0])

        if len(presult) != 0:
            pronounce_part = presult[0]
            mydict.pronounce = pronounce_part

        # 2. find the translate
        translate_part = result[1]
        translate_part = translate_part.replace('\n', '').replace('\t', '') \
            .replace('<br/>', '\n').replace(' ', '')

        # for chinese search
        translate_part = translate_part.replace('&nbsp;', ' ')
        translate_part = translate_part.strip()
        mydict.translate = translate_part

    # 3. use the network translation
    networkTrPattern = re.compile(
        r'''
        <div\ class="category">网络释义</div>.*?<ul>(.*?)</ul>
        ''', re.S | re.X
    )
    raw_nwt_result = networkTrPattern.findall(content)

    if len(raw_nwt_result) != 0:
        nwt_result = raw_nwt_result[0]
        nwt_result = nwt_result.replace('<li>', '').replace('</li>', '') \
            .strip()
        spacePattern = re.compile(r'\n *')
        nwt_result = spacePattern.sub('\n', nwt_result)
        mydict.networkTranslation = nwt_result

    # 4. next we will get the sentences
    sentencePattern = re.compile(
        r'''
        <div\ class="category">例句</div>.*?<ul>(.*?)</ul>
        ''', re.S | re.X
    )
    raw_sentence_result = sentencePattern.findall(content)

    if len(raw_sentence_result) != 0:
        sentence_result = raw_sentence_result[0]
        sentence_result = sentence_result.replace('<li>', '') \
            .replace('</li>', '').strip()
        htmlTagPattern = re.compile(r'<[^>]+>')
        sentence_result = htmlTagPattern.sub('', sentence_result)
        sentence_result = spacePattern.sub('\n\n', sentence_result)
        mydict.sentence = sentence_result

    # finally we copy the url to clipboard
    copy_to_clipboard(pc_url)


def copy_to_clipboard(pc_url):
    # copy the url to the clipboard
    os.system("echo '%s' | xsel -b" % pc_url)


if __name__ == '__main__':

    is_display_basic = True
    is_display_network = True
    is_display_sentence = True

    # check if user enters a valid word to translate
    if len(sys.argv) == 1:
        print "Usage: en <word> [-b] [-n] [-s]"
        sys.exit()
    elif len(sys.argv) == 2:
        pass
    else:
        is_display_basic = "-b" in sys.argv
        is_display_network = "-n" in sys.argv
        is_display_sentence = "-s" in sys.argv

    word_input = sys.argv[1]

    try:
        translate(word_input)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        sys.exit()

    if is_display_basic:
        mydict.print_pronounce()
        mydict.print_translate()

    if is_display_network:
        mydict.print_network_translate()

    if is_display_sentence:
        mydict.print_sentence()

    print ''
