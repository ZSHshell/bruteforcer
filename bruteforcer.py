# Directory brute forcing tool written in pure python

import socket
import requests
import sys
from optparse import OptionParser
import threading


parser = OptionParser()

parser.add_option('-i', '--interface', dest='interface', type='string',
                  help='server you want to directory-scan')
parser.add_option('-p', '--port', dest='port', type='int',
                  help='server you want to directory-scan')
parser.add_option('-l', '--wordlist', dest='word_list', type='string',
                  help='the word list file you want to use to attack the website')
parser.add_option('-t', '--threads', dest='threads', type='int',
                  help='server you want to directory-scan')

options, args = parser.parse_args()

if options.interface and options.port and options.word_list and options.threads:
    interface = options.interface
    port = options.port
    word_list = options.word_list
    threads_number = options.threads
else:
    parser.print_help()


class DirMonster:
    def __init__(self):
        self.interface = interface
        self.port = port
        self. word_list = word_list
        self.threads_number = threads_number

    def check_server_validity(self, host, port_number):
        """
        simple function to test if the server to attack is online and exists
        """
        print('[*] checking [{0}] validity...\r'.format(host))

        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            server_status = test_socket.connect_ex((host, port_number))
            test_socket.close()

            if server_status == 0:
                print('[*] host [{0}] is valid\r'.format(host))
                return True
            else:
                print('[!] host [{0}] does not seem to be available, exiting now\r'.format(host))
                sys.exit()

        except socket.error:
            print('[!] your host does not seem to exist\r')
            sys.exit()

    def check_directory(self, directories_to_check):
        """
        takes a list of directory names to check in parameters and repeat the check
        process for the number of items in the parsed list
        """
        for directory in directories_to_check:
            try:
                server_response = requests.get('http://' + self.interface + '/' + directory.replace('\n', '')).status_code
            except Exception:
                print('[!] an unexpected error occurred\r')
                sys.exit()

            if server_response == 200:
                print('[*] valid path found: {0}\r'.format('http://' + self.interface + '/' + directory))

    def load_wordlist(self, wordlist_file):
        """
        this function simply prepare all items of the list to be tested
        """
        print('[*] loading wordlist...\r')

        try:
            wordlist = open(wordlist_file).readlines()
            print('[*] wordlist has been correctly loaded\r')
            print('[*] total items to check: {0}\r'.format(str(len(wordlist))))
            return wordlist

        except IOError:
            print('[*] failed to read the parsed file: {0}\r'.format(wordlist_file))
            sys.exit()

    def segment_list(self, wordlist_file, thread_count):
        """
        mapping the wordlist in function of the number of threads parsed by the user
        """
        excess = len(wordlist_file) % thread_count
        # return the rest of the division of the
        # length of the word list by the number of threads
        if excess:
            excess, wordlist = wordlist_file[-excess:], wordlist_file[:-excess]
            # defining the excess part of the word list using list object operations
            # same for the word list variable
        else:
            excess = []

        segments = []
        for i in range(0, len(wordlist_file), thread_count):
            # using a for loop here going from 0 to the number of words in the word list
            # incrementing each time by the number of threads to divide the task in a more
            # equal way
            segments.append(wordlist_file[i:i + thread_count])
            # each time segments append a part of the word list from i (starts at 0 to the number of threads)
        return len(segments), segments
        # finally we return a tuple, the length of the segments list which is the number of threads to be used
        # and the segments to do the threads assignments

    def threads_handling(self, wordlist_file):
        threads = self.segment_list(wordlist_file, self.threads_number)[0]
        segments = self.segment_list(wordlist_file, self.threads_number)[1]

        if self.threads_number != threads:
            print('[*] creating one more thread to handle other items from the file\r')
            # this is to prevent the user that we are creating 1 more thread to handle
            # left items of the word list during the equal division of the words to treat
            # between the number of requested threads

        for value in segments:
            thread = threading.Thread(target=self.check_directory, args=(value, ))
            thread.start()

    def main(self):
        if self.check_server_validity(self.interface, self.port):
            wordlist = self.load_wordlist(self.word_list)
            self.threads_handling(wordlist)


dirmonster = DirMonster()
dirmonster.main()
