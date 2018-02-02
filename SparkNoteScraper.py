# scraper imports
import urllib
import urllib.request
from bs4 import BeautifulSoup
import time

# csv / dataframe inports
import pandas as pd

# theading
from threading import Thread, Condition, RLock
from queue import Queue

from argparse import ArgumentParser
import os


#the main function that's called in the script. searches through each line in the books.csv file in the same directory and performs the get_pages function on it
def build_url_queue(putput_dir='output'):
    books = pd.DataFrame.from_csv('books.csv', index_col=None)
    root_url = 'http://www.sparknotes.com/lit/'
    q = Queue()

    for i in range(len(books)):
        target_url = '{}{}'.format(root_url, books['extension'][i])

        name = '_'.join(books['name'][i].split())
        target_dir = os.path.join(putput_dir, name)
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        q.put((target_dir, target_url))

    return q


#from each base url, gets all of the URLS for specialized pages like context, characters, and various chapter summaries - up to 20
def get_subpages(base_url):

    # create list of subpages we care about.
    # if you have any additional subpages you'd like to add, insert the extension into the list.
    subpages = ['context.html', 'summary.html', 'characters.html', 'canalysis.html', 'themes.html']

    # create a list of full 'target' url paths using the subpages list
    targets = ['{}/{}'.format(base_url, subpage) for subpage in subpages]

    #adds 20 section summary URLs to the target urls
    for i in range(1, 21):
        target_urls.append("%ssection%s.rhtml" % (base_url, str(i)))
    for url in target_urls:
        #this is the naming convention used in the output text documents
        name = str(url.replace("http://www.sparknotes.com/lit/","").replace("/","_").replace(".","").replace("html","") + ".txt")
        print("Trying to scrape url: %s" % url)

        try:
            #performs the getplaintext function on each URL, also passing its name
            getplaintext(url, name)
        except:
            print("Failed.")
            continue


def getplaintext(url, name):
    #specifies the browser that is simulated interacting with the host server
    heeds = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; rv:5.0) Gecko/20100101 Firefox/5.0'}
    #creates a server request object to the target URL with the specified headers
    query = urllib.request.Request(url, headers = heeds)
    #opens the query server request object
    html = urllib.request.urlopen(query)
    #formats the html from the server using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    soup.prettify
    #gets rid of all the ads.  If there's another HTML element you want to get rid of, just decompose it from the soup variable
    for div in soup.find_all(class_="floatingad"):
        div.decompose()
    #navigates to the div in which all the text is located
    textboxs = soup.find(class_="studyGuideText")
    #gets all the text from the target div, replacing all the incomprehensible elements.  This is where you'd add stuff to get rid of punctuation as well
    texti = textboxs.get_text().replace("\u2192","").replace("\u2190","").replace("\u2019","'")
    #Creates a new file, since if Python calls "open" and there is no such file it'll make one.  Opens it in write mode.  If you wanted to re-open another file and append stuff to it, you'd open it in "a" mode, which would automatically add any information written to it to the end
    m = open(name, "w")
    #writes the relevant information to the file and then closes it
    m.write(texti)
    m.close()
    #waits to spoof human traffic
    time.sleep(1)


# only execute if this is the main function
if __name__ == '__main__':
    url_q = build_url_queue()

    print('ok')