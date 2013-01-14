import xml
import re
import nltk.tokenize

def get_text_raw(in_file, in_output_encoding = 'utf-8'):
    parser = xml.sax.make_parser()
    handler = RuscorporaRawTextParser(encode_to = in_output_encoding)
    parser.setContentHandler(handler)
    parser.parse(in_file)
    text = handler.char_buffer
    result = []
    for sentence in nltk.sent_tokenize(text):
        result.append([word.lower() for word in nltk.word_tokenize(sentence) \
                       if not re.match('^[^\w]+$', word, re.UNICODE)])
    return result

# raw text in ruscorpora is a set of paragraphs enclosed in <p> </p> tags
# and some <meta>-attributes in the header
class RuscorporaRawTextParser(xml.sax.handler.ContentHandler):
    def __init__(self, encode_to = None):
        self.within_body = False
        self.sentences = []
        self.char_buffer = ''
        self.output_encoding = encode_to

    def startElement(self, name, attrs):
        if name == 'body':
            self.within_body = True
            self.char_buffer = ''

    def endElement(self, name):
        if name == 'body':
            self.within_body = False

    def characters(self, ch):
        # only collect word forms char-by-char
        if self.within_body:
            self.char_buffer += ch

# annotated text is divided into sentences (<se> ... </se>); each sentence's raw words
# stored as raw text in its node
class RuscorporaAnnotatedTextParser(xml.sax.handler.ContentHandler):
    def __init__(self, encode_to = None):
        self.within_sentence = False
        self.within_word = False
        self.sentences = []
        self.words_buffer = []
        self.char_buffer = ''
        self.out_encoding = encode_to
        self.text_info = {'grauthor':'', 'words':0, 'sentences':0, 'header':''}

    def startElement(self, name, attrs):
        if name == 'se':
            self.within_sentence = True
        if name == 'w':
            self.within_word = True
        if name == 'meta':
            if 'name' in attrs:
                for key in self.text_info:
                    if attrs['name'] == key:
                        self.text_info[key] = attrs['content']

    def endElement(self, name):
        if name == 'w':
            self.within_word = False
            self.char_buffer = self.char_buffer.lower()
            if self.out_encoding:
                self.add_word(self.char_buffer)
            self.char_buffer = ''
        if name == 'se':
            self.within_sentence = False
            if len(self.words_buffer):
                self.sentences.append(self.words_buffer)
            self.words_buffer = []

    def add_word(self, in_word):
        in_word = re.sub('^\W+|\W+$', '', in_word, flags = re.UNICODE)
        if len(in_word) and not in_word.isdigit():
            if self.out_encoding:
                in_word = in_word.encode(self.out_encoding)
            self.words_buffer.append(in_word)

    def characters(self, ch):
        # only collect word forms char-by-char
        if self.within_sentence and self.within_word:
            self.char_buffer += ch
