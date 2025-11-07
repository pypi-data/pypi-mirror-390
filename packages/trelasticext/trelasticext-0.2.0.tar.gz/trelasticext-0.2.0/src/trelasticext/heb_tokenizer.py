#!/usr/bin/env python
# encoding: utf8

## Copyright 2010 Yoav Goldberg
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
 Robust Hebrew Tokenizer 

 works as a filter:
   hebtokenizer.py < in > out
   
 run as:
   hebtokenizer.py -h  
 for options

 KNOWN ISSUES:
     - NOT VERY FAST!!!

     - transition from hebrew words to numbers: ב-23:00  will be cut as ב-23 :00
     - deliberately not segmenting משהוכלב from start of words before numbers/quotes/dashes
     - emoticons are not supported (treated as punctuation)
     - ' is always kept at end of hebrew chunks (a document level pre/post processing could help here)
     - !!!!!!!111111 are split to !!!!!!!! 1111111
"""
#########
import re
import codecs

def heb(s,t): return ('HEB',t)
def lat(s,t): return ('LAT',t)
def ara(s,t): return ('ARA',t)
def el(s,t): return ('EL',t)
def num(s,t): return ('NUM',t)
def url(s,t): return ('URL',t)
def punct(s,t): return ('PUNCT',t)
def junk(s,t): return ('JUNK',t)

#### patterns
_NIKUD = u"\u05b0-\u05c4"
_TEAMIM= u"\u0591-\u05af"

undigraph = lambda x:x.replace(u"\u05f0",u"וו").replace(u"\u05f1",u"וי").replace("\u05f2","יי").replace("\ufb4f","אל").replace(u"\u200d","")

_heb_letter = u"([א-ת%s]|[דגזצתט]')" % _NIKUD

# a heb word including single quotes, dots and dashes  / this leaves last-dash out of the word
_heb_word_plus = u"[א-ת%s]([.'`\"\-/\\]?['`]?[א-ת%s0-9'`])*" % (_NIKUD,_NIKUD)

# English/French/German/latin words  (do not care about abbreviations vs. eos for english)
_spanish = "áéíóúüñç"
_german = "äöüÄÖÜß" # https://en.wikipedia.org/wiki/German_orthography
_french = "àâçéèêëîïôûùüÿñæœ"
# _lat_word = u"[a-zA-ZäöüÄÖÜßàâçéèêëîïôûùüÿñæœ][a-zA-Z0-9'.äöüÄÖÜßàâçéèêëîïôûùüÿñæœ]*"
_lat_word = u"[a-zA-Z%s%s%s][a-zA-Z0-9%s%s%s]*" % (_german, _french, _spanish, _german, _french, _spanish)
_lat_word_plus = u"[a-zA-Z%s%s%s]([.'`\"\-/\\]?['`]?[a-zA-Z0-9'.%s%s%s'`])*" % (_german, _french, _spanish, _german, _french, _spanish)

_ara_word = u"[\u0621-\u064A][\u0621-\u064A0-9]*"

# _el_word = u"[α-ωA-Ω][α-ωΑ-Ω0-9]*" # Greek https://en.wikipedia.org/wiki/Greek_diacritics
_el_word = u"[\u0370-\u03ff\u1f00-\u1fff][\u0370-\u03ff\u1f00-\u1fff0-9]*"

# numerical expression (numbers and various separators)
#_numeric = r"[+-]?[0-9.,/\-:]*[0-9%]"
_numeric = r"[+-]?([0-9][0-9.,/\-:]*)?[0-9]%?"

# url
_url = r"[a-z]+://\S+"

# punctuations
_opening_punc = r"[\[('`\"{ʼ]"
_closing_punc = r"[\])'`\"}ʼ]"
_eos_punct = r"[!?.·]+"
_internal_punct = r"[,;:\-&]"

# junk
#_junk = ur"[^א-ת%sa-zA-Z0-9%%&!?.,;:\-()\[\]{}\"'\/\\+]+" #% _NIKUD
_junk = u"[^א-ת%sa-zA-Z0-9!?.,:;\-()\[\]{}]+" % _NIKUD #%%&!?.,;:\-()\[\]{}\"'\/\\+]+" #% _NIKUD

is_all_heb = re.compile(u"^%s+$" % (_heb_letter),re.UNICODE).match

is_a_number = re.compile(r"^%s$" % _numeric ,re.UNICODE).match
is_all_lat= re.compile(r"^[a-zA-Z]+$",re.UNICODE).match
is_all_ara= re.compile(r"^[\u0621-\u064A0-9 ]+$",re.UNICODE).match
is_all_el= re.compile(r"^[α-ωΑ-Ω0-9 ]+$",re.UNICODE).match
is_sep = re.compile(r"^\|+$").match
is_punct = re.compile(r"^[.?!]+").match

def is_hebrew_token(token):
    if re.search(u"[א-ת%s]([.'`\"\-/\\]?['`]?[א-ת%s0-9'`])*" % (_NIKUD, _NIKUD), token):
        return True
    return False


#### scanner

scanner = re.Scanner([
    (r"\s+", None),
    (_url, url),
    (_heb_word_plus, heb),
    (_lat_word, lat),
    (_ara_word, ara),
    (_el_word, el),
    (_numeric,  num),
    (_opening_punc, punct),
    (_closing_punc, punct),
    (_eos_punct, punct),
    (_internal_punct, punct),
    (_junk, junk),
   ])

##### tokenize
def tokenize(sent, filters = None):
    tok = sent   
    if filters:
        FILTER = set(filters)
    parts,reminder = scanner.scan(tok)
    assert(not reminder)
    return parts

if __name__=='__main__':
   import sys
   from itertools import islice

   from optparse import OptionParser
   parser = OptionParser("%prog [options] < in_file > out_file")
   parser.add_option("-i","--ie",help="input encoding [default %default]",dest="in_enc",default="utf_8_sig")
   parser.add_option("-o","--oe",help="output encoding [default %default]",dest="out_enc",default="utf_8")
   opts, args = parser.parse_args()

   #FILTER = set(['JUNK','ENG'])
   FILTER = set()
   for sent in codecs.getreader(opts.in_enc)(sys.stdin):
      #print u"\n".join(["%s %s" % (which,tok) for which,tok in tokenize(sent) if which not in FILTER]).encode("utf8")
      print (" ".join([tok for (which,tok) in tokenize(sent)]).encode(opts.out_enc))
