
corpus = {"1.html": {"2.html", "3.html"}, "2.html": {"3.html"}, "3.html": {"2.html"}}
page = "2.html"
link_to_page = {}

for page0 in corpus:
    for linkedPage in corpus[page0]:
        if linkedPage not in link_to_page:
            link_to_page[linkedPage] = set()
            link_to_page[linkedPage].add(page0)
        else:
            link_to_page[linkedPage].add(page0)

print(link_to_page)
