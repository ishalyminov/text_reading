import codecs
import os
import xml.sax
import sys
import re

MAX_SENTS = 1000000000
WRITE_GRAMMAR_TAGS = False
LOWERCASE = True


# extracts sentences as lists of wordforms from SynTagRus
class SynTagRusHandler(xml.sax.handler.ContentHandler):
    def __init__(self, out_destination):
        self.sentences = []
        self.__in_sentence = False
        self.__in_word = False

    def characters(self, in_content):
        content = re.sub('\s', ' ', in_content)
        if self.__in_word:
            self.sentences[-1][-1] += (content)
        elif self.__in_sentence:
            self.sentences[-1].append(content)

    def ignorableWhitespace(self, in_content):
        self.characters(content)

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, tag, in_attrs):
        if tag == 'W':
            self.__in_word = True
            self.sentences[-1].append('')
        if tag == 'S':
            self.__in_sentence = True
            self.sentences.append([])

    def endElement(self, tag):
        if tag == 'W':
            self.__in_word = False
        if tag == 'S':
            self.__in_sentence = False


def syntagrus_to_plaintext(in_sentences, out_stream):
    for sentence in in_sentences:
        print >>out_stream, ''.join(sentence)


def convert(in_source, out_destination, in_serialize_function):
    out = out_destination
    if isinstance(out_destination, str):
        out = codecs.getwriter('utf-8')(open(out_destination, 'wb'))
    handler = SynTagRusHandler(out)
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(in_source)
    in_serialize_function(handler.sentences, out_destination)


def convert_directory(in_texts_root, in_result_root, in_serialize_function):
    if not os.path.isdir(in_result_root):
        os.makedirs(in_result_root)
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        local_root = root[len(in_texts_root) + 1:]
        result_root = os.path.join(in_result_root, local_root)
        if not os.path.isdir(result_root):
            os.makedirs(result_root)
        for filename in files:
            if os.path.splitext(filename)[1] == '.tgt':
                tgt_file_name = os.path.join(root, filename)
                out_file_name = os.path.join(result_root, filename)
                print '%s -> %s' % (tgt_file_name, out_file_name)
                out_stream = codecs.getwriter('utf-8')(open(out_file_name, 'w'))
                convert(tgt_file_name, out_stream, in_serialize_function)
                out_stream.close()


def main():
    if len(sys.argv) < 3:
        print 'Usage: syntagrus.py <source> <destination>'
        exit()
    source, destination = sys.argv[1:3]
    if os.path.isdir(source):
        convert_directory(source, destination, syntagrus_to_plaintext)
    else:
        convert(source, destination, syntagrus_to_plaintext)

if __name__ == '__main__':
    main()
