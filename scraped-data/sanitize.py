
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
    for opt, arg in opts:
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
    cleanup(inputcsv, intermcsv)
    # second pass sanitize:
    #   determine dictionary, sort entries by size,
    #   remove results that don't sufficiently intersect most
    #   seen vocabulary - don't want sentences with unseen words
    cleanvocab(intermcsv, outputcsv)
	
# cleanup cleanup everybody cleanup
def cleanup(inputfile, intermediate):
    with open(inputfile, 'rb') as f_in, open(intermediate, 'w+') as f_out:
        desc_col = 2
        user_col = 1
        link_col = 0
        rownum = 0
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        for row in reader:
            # double check format
            if rownum == 0:
                assert(row[0] == 'link')
                assert(row[1] == 'user')
                assert(row[2] == 'desc')
            # clean row, write to intermediate file
            else:
                username   = row[user_col]
                threadlink = row[link_col]
                comment    = row[desc_col]
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
                    row[desc_col] = comment
                    writer.writerow(row)   
            rownum += 1
			
# conform! conform! no unique words!
def cleanvocab(intermediate, outputfile):
	stats = "list of vocab cleanup stats"
	vocab = {}
    with open(intermediate, 'rb') as f_in, open(outputfile, 'w+') as f_out:
	    desc_col = 2
        user_col = 1
        link_col = 0
		reader = csv.reader(f_in)
		writer = csv.writere(f_out)
		# loop through, save vocab stats
		rownum = 0
		for row in reader:
		# double check format
			if rownum == 0:
				assert(row[0] == 'link')
				assert(row[1] == 'user')
				assert(row[2] == 'desc')
			else:
				username   = row[user_col]
                threadlink = row[link_col]
                comment    = row[desc_col]
				for word in comment:
					if word in vocab:
						vocab[word] += 1
					else:
						vocab[word] = 1
			rownum += 1
		# loop through, save to file 
		rownum = 0
		for row in reader:
			if rownum > 0:
				if no non-vocab words:
					writer.writerow(row)
			rownum += 1
		
		
	return stats

if __name__ == "__main__":
    main(sys.argv[1:])

