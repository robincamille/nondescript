from flask import Flask
from flask import request
from flask import render_template
from uniquefeatures import avgwordlength, avgsentlength
from numpy import mean
from collections import defaultdict
from sys import argv


app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template("simple-form.html")

@app.route('/', methods=['POST'])
def my_form_post():

    docraw = request.form['text']
    doc = docraw.split() #'text' is the textarea name
    s = [] #things to print

    #Set up word length calculator
    infile = open('train_wordlen.csv','r')
    totwlraw = infile.readlines()
    infile.close()

    totwl = []
    for i in totwlraw:
        totwl.append(float(i[:-1]))
        
    #Set up sentence length calculator
    infile = open('train_sentlen.csv','r')
    totslraw = infile.readlines()
    infile.close()

    totsl = []
    for i in totslraw:
        totsl.append(float(i[:-1]))

    #Set up word frequency compare-er
        #File from 70 authors' documents
    infile = open('train_all-freqs_smoothed_avg_2col.csv','r')
    allfreqraw = infile.readlines()
    infile.close()

    allfreq = {}
    for row in allfreqraw:
        row = row.split(',')
        allfreq[row[0][1:-1]] = float(row[1]) #row[0] is 'aaron' hence [1:-1]
    

    #Document length
    s.append('Document length: %d words' % len(doc))

    #Average word lengths
    totwlavg = mean(totwl)
    s.append('Word length is %.2fx average' % (avgwordlength(doc)/float(totwlavg)))

    #Average sent lengths
    totslavg = mean(totsl)
    s.append('Sentence length is %.2fx average' % (avgsentlength(doc)/float(totslavg)))

    #Top unusual words
    doccount = defaultdict(int)
    docfreq = defaultdict(int)

    #print 'Term counting'
    for word in doc:
        word = word.lower()
        doccount[word] += 1 #term count

    #print 'Term frequencies'
    for word in doccount:
        docfreq[word] = doccount[word] / float(len(doc)) #term frequency

    #print 'Comparing to all docs'
    compfreq = defaultdict(list)
    for word in docfreq:
        if word in allfreq.keys():
            compfreq[word] = [docfreq[word],allfreq[word]]
        else:
            pass

    compwords = []
    for word in compfreq:
        if compfreq[word][0] > compfreq[word][1]:
            if compfreq[word][1] == 0:
                v = compfreq[word][1] / 0.0000000176 #min freq from train/
            else:
                v = compfreq[word][0] / float(compfreq[word][1])
            compwords.append([v, word, doccount[word]])
        else:
            pass

    print '\nTop words:'
    compwordssort = sorted(compwords,reverse=True)
    
    for i in compwordssort[:30]:
        s.append('%15s %4.2fx more frequent than average document\t(%d times)' % (i[1],i[0],i[2]))


    return render_template("simple-output.html", output = s, repeatdoc = docraw)

if __name__ == '__main__':
    app.debug = True
    app.run()