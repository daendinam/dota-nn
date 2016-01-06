import sys, getopt

if __name__ == "__main__":
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "hi:o:")
    except getopt.GetoptError:
        print "checkstats.py -i <inputfile>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print "checkstats.py -i <inputfile>"
        elif opt == '-i':
            inputfile = arg
            
    print "Vocab stats -----------"
    stats = {}
    with open(inputfile, 'r') as f:
        for line in f:
            for word in str.split(line):
                if word in stats:
                    stats[word] += 1
                else:
                    stats[word] = 1
    stats_view = [ (v,k) for k,v in stats.iteritems() ]
    print "Most frequent words(preview): "
    stats_view.sort(reverse=True) # natively sort tuples by first element
    i = 0
    for v,k in stats_view:
        print "%s: %d" % (k,v)
        i +=1
        if i == 25:
            break
    print "Least frequent words(preview): "
    stats_view.sort(reverse=False) # natively sort tuples by first element
    i = 0
    for v,k in stats_view:
        print "%s: %d" % (k,v)
        i +=1
        if i == 25:
            break
    print "Size: " + str(len(stats))
    