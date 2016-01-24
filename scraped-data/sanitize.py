#todo: throw out links (http)?import sys, getoptimport csvimport reimport string
import loggingimport cPickleimport randomimport numpy as npfrom nltk import tokenize
logging.basicConfig(filename='sanitize.log',level=logging.DEBUG, filemode='w')def main(argv):    inputcsv = ''    outputcsv = ''    intermcsv = ''    # get input and output files, csv format    try:        opts, args = getopt.getopt(argv, "hi:o:")    except getopt.GetoptError:        print "sanitize.py -i <inputcsvfile> -o <outputtxtfile>"        sys.exit(2)    for opt, arg in opts:        if opt == '-h':            print "sanitize.py -i <inputcsvfile> -o <outputtxtfile>"        elif opt == '-i':            inputcsv = arg        elif opt == '-o':            outputcsv = arg            intermcsv = arg[:-4] + "-intermediate" + ".csv"    # first pass sanitize:    #   whitespace, special characters,    #   empty or noncomplete results, links,    #   attempt to throw out jibberish, non-sentences    cleanup(inputcsv, intermcsv)    # second pass sanitize:    #   determine dictionary, sort entries by size,    #   remove results that don't sufficiently intersect most    #   seen vocabulary - don't want sentences with unseen words    stats = cleanvocab(intermcsv, outputcsv)    min_freq = stats['min_freq']    datadump = createtestdata(outputcsv, stats, outputcsv[:-4] + 'data.pk')    if datadump == 1:        print "No data was dumped, all comments were thrown out in sanitization."    else:        print "Data dumped to " + str(datadump)    print "Vocab stats -----------"    print "Most frequent words(preview): "    stats_view = [ (v,k) for k,v in stats.iteritems() ]    stats_view.sort(reverse=True) # natively sort tuples by first element    # trim vocab below threshold    for v,k in stats_view:        if v < min_freq:            del stats[k]    print "Size: " + str( len(stats) )    i = 0    for v,k in stats_view:        print "%s: %d" % (k,v)        i +=1        if i == 25:            break    print "Least frequent words(preview): "    stats_view = [ (v,k) for k,v in stats.iteritems() ]    stats_view.sort(reverse=False) # natively sort tuples by first element    i = 0    for v,k in stats_view:        print "%s: %d" % (k,v)        i +=1        if i == 25:            break            def makesentency(comment):    # if the last char of comment is white space, strip    if comment[-1] == ' ':        comment = comment[:-1]    # if last char of comment is not end of sentence punc, strip white space and replace with period    punc_list = list("!.?")    if (comment[-1] not in punc_list) and (comment[-1] in list(string.punctuation)):        comment = comment[:-1] + '.'    if comment[-1] == ' ':        comment = comment[:-1]    if comment[-1] in list(string.letters + string.digits):        comment = comment + ' .'    # if first char of comment is lowercase, capitalize it    if comment[0].islower():        comment = comment[0].upper() + comment[1:]    return comment# for every single digit number (0-9) that is its own word, replace it# with the text version:# I am number 1. -> I am number one.# I am1 number 11. -> I am1 number 11.def wordifynumbers(comment):    comment = re.sub(' 0 ', ' zero ',  comment)    comment = re.sub(' 1 ', ' one ',   comment)    comment = re.sub(' 2 ', ' two ',   comment)    comment = re.sub(' 3 ', ' three ', comment)    comment = re.sub(' 4 ', ' four ',  comment)    comment = re.sub(' 5 ', ' five ',  comment)    comment = re.sub(' 6 ', ' six ',   comment)    comment = re.sub(' 7 ', ' seven ', comment)    comment = re.sub(' 8 ', ' eight ', comment)    comment = re.sub(' 9 ', ' nine ',  comment)    return comment    # cleanup cleanup everybody cleanupdef cleanup(inputfile, intermediate):    with open(inputfile, 'rb') as f_in, open(intermediate, 'w+') as f_out:        desc_col = 2        user_col = 1        link_col = 0        rownum = 0        reader = csv.reader(f_in)        writer = csv.writer(f_out)        for row in reader:            if rownum % 10000 == 0:                print "Sanitized " + str(rownum) + " comments..", sys.stdout.flush() #debug            # double check format            if rownum == 0:                print "row0: " + str(row)                assert(row[0] == 'link')                assert(row[1] == 'user')                assert(row[2] == 'desc')                writer.writerow(row)            # clean row, write to intermediate file            else:                username   = row[user_col]                threadlink = row[link_col]                comment    = row[desc_col]                if rownum > 0:                    is_sentence = True                    logging.debug("User: " + username)                    logging.debug("Comment(Original): " + repr(comment))                    # check for reddit specific comment deleted case                    if (comment == "[deleted]") and ("reddit" in inputfile):                        is_sentence = False                    # remove newlines and return cairrage                    comment = re.sub('[\n\r]+', '', comment)                    # replace semicolon with comma (removed to test data with more punc)                    #comment = re.sub (';', ',', comment)                    # filter out non-alphanumeric/punctuation                    #allowed = string.digits + string.letters + string.punctuation + ' '                    #punc = ".,?'"                    punc = ".,;:-?'"                    allowed = string.digits + string.letters + punc + ' '                    comment = filter(allowed.__contains__, comment)                    # replace all whitespace with single space                    comment = re.sub('\s+', ' ', comment).strip()                    # replace multiple punctuation marks with just 1                    # replace spaced out repeated punctuation                    # ie: " . . , . ! !!'                    comment = re.sub(r'([^\w\s])\s+(?=[^\w\s])', r'\1', comment)                    # replace multiple DIFFERENT punctuation with first                    comment = re.sub(r'([^\w\s])([^\w\s]+)', r'\1', comment)                    # put 1 space between base word and contraction word, remove                    # apostrophe. ie: don't -> do nt                    # n't needs special rule otherwise it becomes don t                    comment = re.sub(r"(\w+)n'(t)", r'\1 nt', comment)                    comment = re.sub(r"(\w+)'([^\Ws]+)", r'\1 \2', comment)                    comment = re.sub(r"(\w+)'(\s)", r'\1\2', comment)                    #comment = re.sub(r"(\s)'(\w+)", r'\1\2', comment)
                    
                    if len(comment) > 0:
                        comment = makesentency(comment)                        # if first char of comment is not word char, throw out                        word_chars = [c for c in (string.letters + string.digits)]                        if comment[0] not in word_chars:                            is_sentence = False                    else:
                        is_sentence = False                                        sentences = tokenize.sent_tokenize(comment)                    for sentence in sentences:                        #check beginning and ending again for ea. sentence                        if len(sentence) > 0:                            sentence = makesentency(sentence)                            # if first char of comment is not word char, throw out                            word_chars = [c for c in (string.letters + string.digits)]                            if sentence[0] not in word_chars:                                is_sentence = False                        else:                            is_sentence = False
                        # put 1 space between words and punctuation, and between a word and " 's "
                        # not between ' and s
                        sentence = re.sub(r'(\w+)([^\w\s])', r'\1 \2', sentence)
                        sentence = re.sub(r"([^\w\s'])(\w+)", r'\1 \2', sentence)
                        # keep "their own word" single digits by turning them into                         # characters instead of digits                        sentence = wordifynumbers(sentence)                                                logging.debug("Sentence(Sanitized): " + repr(sentence))                        logging.debug("..")                                                # throw out results with digits, inflates vocab too much                        for word in sentence.split():                            if re.search('\d', word) != None:                                is_sentence = False                        #output to intermediate file                        row[desc_col] = sentence                        if is_sentence:                            writer.writerow(row)            rownum += 1    # conform! conform! no unique words!def cleanvocab(intermediate, outputfile):    stats = "list of vocab cleanup stats"    vocab = {}    # the minimum frequency of a word in data    # to be counted in final vocab    min_freq = 500    with open(intermediate, 'rb') as f_in, open(outputfile, 'w+') as f_out:        desc_col = 2        user_col = 1        link_col = 0        reader = csv.reader(f_in)        # loop through, save vocab stats        rownum = 0        for row in reader:            # double check format            if rownum == 0:                assert(row[0] == 'link')                assert(row[1] == 'user')                assert(row[2] == 'desc')            else:                username   = row[user_col]                threadlink = row[link_col]                sentence   = row[desc_col]                for word in str.split(sentence):                    word = word.lower() #ignore case                    if word in vocab:                        vocab[word] += 1                    else:                        vocab[word] = 1            rownum += 1        # loop through, save to file if vocab requirements met        rownum = 0        f_in.seek(0)        for row in reader:            if rownum > 0:                username   = row[user_col]                threadlink = row[link_col]                sentence   = row[desc_col]                good_vocab = True                for word in str.split(sentence):                    word = word.lower() #ignore case                    if (word not in vocab) or (vocab[word] < min_freq):                        good_vocab = False                        #print "Word not in vocab: " + word                if good_vocab:                    # only use sentences with 3 or more words                    if len(sentence.translate(None, string.punctuation).split()) >= 3:                        f_out.write(sentence + '\n')            rownum += 1    # trim vocab to the words that made the cut    stats = vocab    for word in stats.keys():        if stats[word] < min_freq:            del stats[word]    stats['min_freq'] = (-1) * min_freq    return stats# take parsed and sanitized data from cleanvocab() and split into 3-grams with target# values split up into training, validation, and test data, each having corresponding# target array def createtestdata(rawtext, vocab, outputfile="data.pk"):    # for each sentence in train range    #   for each rolling 4-gram from [0,3] to [end - 4, end]    #       save 3-gram to inputs[], 4th word to targets[]        # split into training, validation range and test range (50,25,25)    # save all to individual arrays:    #        train_inputs, train_targets = data_obj['train_inputs'], data_obj['train_targets']    #        valid_inputs, valid_targets = data_obj['valid_inputs'], data_obj['valid_targets']    #        test_inputs, test_targets = data_obj['test_inputs'], data_obj['test_targets']        # save arrays to file with cpickle        #TODO: vocab should only include min_freq(alt: top X) words    total_inputs  = []    total_targets = []    train_inputs  = []    valid_inputs  = []    test_inputs   = []    train_targets = []    valid_targets = []    test_targets  = []    # remove indicator entry for min word frequency    if 'min_freq' in vocab:        del vocab['min_freq']    vocab = vocab.keys()        with open(rawtext, 'rb') as f_in:        # read each line (1 line = 1 sentence)        sentence_count = 0 #debug        for sentence in f_in:            sentence_count += 1 #debug            if sentence_count % 1000 == 0:                print "Processed " + str(sentence_count) + " sentences of trigrams..", sys.stdout.flush() #debug            i = 0            #words = [x.lower() for x in sentence.split()] # map pushes to c compiler            words = map(str.lower, sentence.split())            # take every 4-gram left to right            while i <= (len(words) - 4):                trigram = words[i:(i+3)]                target = words[i+3]                total_inputs.append([vocab.index(trigram[0]), vocab.index(trigram[1]), vocab.index(trigram[2])])                total_targets.append(vocab.index(target))                i += 1        # randomize the order to reduce training bias (keep same order between the 2 lists)    if len(total_inputs) > 0 and len(total_targets) > 0:        c = list(zip(total_inputs, total_targets))        random.shuffle(c)        total_inputs, total_targets = zip(*c)        total_inputs = list(total_inputs)        total_targets = list(total_targets)    else:        return 1        # use 80/20 split for reddit - much larger set means validation takes way too long with big split    if 'reddit' in rawtext:        # split into test/vald/train sets        input_len = len(total_inputs)        assert(input_len == len(total_targets))        # first 80%        train_inputs, train_targets = total_inputs[:(4*input_len/5)], total_targets[:(4*input_len/5)]        # 80-90%        valid_inputs, valid_targets = total_inputs[(4*input_len/5):(9*input_len/10)], total_targets[(4*input_len/5):(9*input_len/10)]        # 90-100%        test_inputs, test_targets = total_inputs[(9*input_len/10):], total_targets[(9*input_len/10):]    else:        # split into test/vald/train sets        input_len = len(total_inputs)        assert(input_len == len(total_targets))        # first half        train_inputs, train_targets = total_inputs[:input_len/2], total_targets[:input_len/2]        # third quarter        valid_inputs, valid_targets = total_inputs[(input_len/2):(3*input_len/4)], total_targets[(input_len/2):(3*input_len/4)]        # fourth quarter        test_inputs, test_targets = total_inputs[(3*input_len/4):], total_targets[(3*input_len/4):]        # round data down to multiples of 100, batch size must be multiple of datapoint size    rounded_len = round_down(len(train_inputs), 100)    del train_inputs[rounded_len:]    del train_targets[rounded_len:]    rounded_len = round_down(len(valid_inputs), 100)    del valid_inputs[rounded_len:]    del valid_targets[rounded_len:]    rounded_len = round_down(len(test_inputs), 100)    del test_inputs[rounded_len:]    del test_targets[rounded_len:]        # output to file    data = {'vocab':         vocab,            'train_targets': np.array(train_targets),            'train_inputs':  np.array(train_inputs),            'test_targets':  np.array(test_targets),            'test_inputs':   np.array(test_inputs),            'valid_targets': np.array(valid_targets),            'valid_inputs':  np.array(valid_inputs)            }    cPickle.dump(data, open(outputfile, 'wb'))    return outputfile# round down num to nearest multiple of divisordef round_down(num, divisor):    return num - (num%divisor)    if __name__ == "__main__":    main(sys.argv[1:])