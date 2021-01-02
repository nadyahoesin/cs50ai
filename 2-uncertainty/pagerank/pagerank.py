import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    transModel = {}

    # If page has no outgoing link, all pages in corpus should have equal probability
    if len(corpus[page]) == 0:
        damping_factor = 0
    
    for page0 in corpus:
        if page0 in corpus[page]:
            transModel[page0] = damping_factor / len(corpus[page]) + (1 - damping_factor) / len(corpus)
        else:
            transModel[page0] = (1 - damping_factor) / len(corpus)

    return transModel


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    visited_times = {}

    # Get a randomly generated first sample and the transition model
    sample = random.choice(list(corpus))
    visited_times[sample] = 1
    transModel = transition_model(corpus, sample, damping_factor)

    # Sample n times to find out how many times are each page visited (first sample already generated so n - 1)
    for i in range(n - 1):
        sample = random.choices(list(transModel), weights=list(transModel.values()))[0]
        if sample not in visited_times:
            visited_times[sample] = 1
        else:
            visited_times[sample] += 1

        transModel = transition_model(corpus, sample, damping_factor)

    # Divide the times each page is visited by n to find out the probability
    for Sample in visited_times:
        visited_times[Sample] /= n

    return visited_times


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    PageRank = {}

    # Dictionary that maps a page to pages that linked to the aforementioned page
    link_to_page = {}

    for page in corpus:
        # Assign an initial rank of 1/(total number of pages) to every page
        PageRank[page] = 1 / len(corpus)

        # Get each possible page that links to each page
        for linkedPage in corpus[page]:
            if linkedPage not in link_to_page:
                link_to_page[linkedPage] = set()
                link_to_page[linkedPage].add(page)
            else:
                link_to_page[linkedPage].add(page)

    while True:
        value_change = {}

        for page in corpus:
            value_change[page] = PageRank[page]
            
            # PageRank formula
            PageRank[page] = (1 - damping_factor) / len(corpus)
            for Page in link_to_page[page]:
                PageRank[page] += damping_factor * (PageRank[Page] / len(corpus[Page]))

            value_change[page] -= PageRank[page]

        # If no PageRank values change by more than 0.001, return the PageRank
        i = 0
        for page in value_change:
            i += 1
            if abs(value_change[page]) > 0.001:
                break

            if i == len(value_change) - 1:
                return PageRank


if __name__ == "__main__":
    main()
