
# todo:
# remove whitespace characters
# remove "unicode indicator", ie: { u'actual text'} -> {actual text}
# punctuation?
# throw out bad results
# extra white space trimming
# throw out links (http?)
# way to dismiss keyboard spam non-words versus non-dictionary legit words (ie. hero names)?
# after all post-by-post trimming, trim entire set by dictionary size results

import sys, getopt
import csv
import re
import string

def main(argv):
    inputcsv = ''
    outputcsv = ''
    intermcsv = ''
    # get input and output files, csv format
    try:
        opts, args = getopt.getopt(argv, "hi:o:")
    except getopt.GetoptError:
        print "sanitize.py -i <inputcsvfile> -o <outputcsvfile>"
        sys.exit(2)
    #for opt, arg in opts: <-- was only giving 1 tuple for some reason
    for pair in opts:
        print "pair: " + str(pair)
    for pair in opts:
        opt = pair[0]
        arg = pair[1]
        print "opt,arg: " + opt + ',' + arg
        print "pair: " + str(pair)
        if opt == '-h':
            print "sanitize.py -i <inputcsvfile> -o <outputcsvfile>"
        elif opt == '-i':
            inputcsv = arg
        elif opt == '-o':
            outputcsv = arg
            intermcsv = arg[:-4] + "-intermediate" + ".csv"
    # first pass sanitize:
    #   whitespace, special characters,
    #   empty or noncomplete results, links,
    #   attempt to throw out jibberish, non-sentences
    #try:
        cleanup(inputcsv, intermcsv)
    #except:
    #    print "Unexpected error handling first pass cleanup: ", \
    #            sys.exc_info()[0]
    #    sys.exit(1)
    # second pass sanitize:
    #   determine dictionary, sort entries by size,
    #   remove results that don't sufficiently intersect most
    #   seen vocabulary - don't want sentences with unseen words
    try:
        cleanvocab(intermcsv, outputcsv)
    except:
        print "Unexpected error handling second pass cleanup: ", \
                sys.exc_info()[0]
        sys.exit(1)

def cleanup(inputfile, intermediate):
    # cleanup cleanup everybody cleanup
    with open(inputfile, 'rb') as f_in: #, open(intermediate, 'w+') as f_out:
        print "intermediate: " + intermediate#debug
        desc_col = 2
        user_col = 1
        link_col = 0
        rownum = 0
        reader = csv.reader(f_in)
        for row in reader:
            # double check format
            if rownum == 0:
                print "Row is: " + str(type(row))
                assert(row[0] == 'link')
                assert(row[1] == 'user')
                assert(row[2] == 'desc')
            # clean row, write to intermediate file
            else:
                username = row[user_col]
                threadlink = row[link_col]
                comment = row[desc_col]
                # debug, don't do entire file yet
                if rownum > 9:
                    exit(0)
                if rownum > 0:
                    print "User: " + username
                    print "Comment(Original): " + repr(comment)
                    # remove newlines and return cairrage
                    comment = re.sub('[\n\r]+', '', comment)
                    # filter out non-alphanumeric/punctuation
                    allowed = string.digits + string.letters + string.punctuation + ' '
                    comment = filter(allowed.__contains__, comment)
                    # replace all whitespace with single space
                    comment = re.sub('\s+', ' ', comment).strip()
                    # replace excessive(?) repetiion with 1 'yeeees' -> 'yes'
                    # ^ can only really be done from 3+ to 3 i think

                    # replace multiple punctuation marks with just 1
                    # replace spaced out repeated punctuation
                    # ie: " . . , . ! !!'
                    comment = re.sub(r'([^\w\s])\s+(?=[^\w\s])', r'\1', comment)
                    # replace multiple DIFFERENT punctuation with first
                    comment = re.sub(r'([^\w\s])([^\w\s]+)', r'\1', comment)
                    # put 1 space between words and punctuation, and between a word and " 's "
                    # not between ' and s, remove non punc? (@^$ etc)
                    comment = re.sub(r"(\w+)([^\w\s])|([^\w\s'])(\w+)",
                            r'\1 \2', comment)

                    print "Comment(Sanitized): " + repr(comment)
                    print ".."

                    #output to intermediate file
            rownum += 1

def cleanvocab(intermediate, outputfile):
    # conform! conform! no unique words!
    return

if __name__ == "__main__":
    main(sys.argv[1:])

