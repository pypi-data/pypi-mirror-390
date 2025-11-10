% clanker_score

This project contains two *Python3* scripts:

+ **ddg_results_by_kwd_density**
+ **keyword_density**

# **ddg_results_by_kwd_density**

This script ranks DuckDuckGo search results by keyword density.

Nowadays search results are dominated by Web pages showing high
keyword density, indicating they are search-engine-optimized or even
AI generated.  This script reads your search terms, retrieves search
results from *ddg* via *frogfind*, fetches each page, and computes the
keyword density there.  Please note that **frogfind.com** is rate
limited.

This script reads your search terms from standard input.

It writes a *markdown* report on standard output.

# **keyword_density**

This script reads a document from standard input.

It writes a report on standard output, showing keywords and their
average density.  Documents optimized for search-engine placement show
keyword density that is abnormally high (>= 0.02).  AI-generated text
also exhibits this characteristic.  Although AI text is
indistinguishable from human text in most regards, it is unlikely that
AI will ever be made less wordy.

# Installation

## Windows

    > python -m venv ClankerScore

    > ClankerScore\Scripts\activate

    > pip install clanker_score --upgrade

## Linux

    > python -m venv ~/ClankerScore
    
    > source ~/ClankerScore/bin/activate

    > pip install clanker_score --upgrade 

# How to ....

## Windows

    > ClankerScore\Scripts\activate

    > ddg_results_by_kwd_density

## Linux

    > source ~/ClankerScore/bin/activate

    > ddg_results_by_kwd_density

# Why ....

Type in your search terms.  **ddg_results_by_kwd_density** doesn't ask.

Press "enter."

**ddg_results_by_kwd_density** will do a DuckDuckGo search.  It will
visit each page in the search results so you don't have to.  It will
present a report of your search results showing the keyword density of
each page.  This is a clue to how piquant the content of each page is
likely to be.

Keywords are not taken from your search terms.  Instead they are the
seven words most commonly occuring on the page.  If these seven words
are seen to be repeated on the page to an unusual degree, then it is
a good assumption that the page was designed by the author to appear
high on search results.

Keyword density is a measure of "gloss."  Most people will read pages
with high keyword density as unusually glossy.  Keyword density is not
necessarily related to how genuine the page content appears to be
otherwise, but most people will look askance at a page that is too
glossy.

It should come as no big surprise that the pages that appear high on
search results have been designed that way.  They are deliberately
glossy with high keyword density.  You may consider whether to skip
reading them or even loading them in your browser.  Chances are good
that the glossy pages are mostly advertising.

Generally you will find interspersed in your results a handful of
sites with low keyword density.  These are likely from universities,
government sites, and research institutions that have sources of
revenue beyond advertising.  You may consider whether to load these up
and skim through them.  Probably they will show a publication date,
author, and list of references, which will move your research forward.

It can be noted that AI-generated sites often exhibit high keyword
density.  This is probably deliberate so that they garner advertising
revenue.  However, it may also be due to "bot 'splaining," which is
polly-paraphrasing a series of several (perhaps contradictory)
articles.

Keyword density is not the only measure of gloss.  There are others
that have been developed to measure ratios between parts of speech.
Unfortunately none of these distinguish sharply between pages that
naturally convey genuine information and pages that have been designed
to convey fluff for ulterior purposes.  It is unlikely that combining
measures of gloss will result in a tool that discriminates much better
than keyword density by itself.

+ Piskorski, Jakub, Marcin Sydow, and Weiss Weiss. "Exploring
  Linguistic Features for Web Spam Detection: A Preliminary Study."
  _Airweb '08: Proceedings of the 4th International Workshop on
  Adversarial Information Retrieval on the Web_. Ed.  Carlos Castillo,
  Kumar Chellapilla, and Dennis Fetterly. New York: ACM, Apr. 2008. 25-28. ISBN:9781605581590. DOI:10.1145/1451983.
  09 Nov. 2025 <[https://users.pja.edu.pl/~msyd/lingFeat08draft.pdf](https://users.pja.edu.pl/~msyd/lingFeat08draft.pdf)>.

**ddg_results_by_kwd_density** is cumbersome by design — too
cumbersome to be a daily driver.  We don't want to make this too easy
for just anyone to censor all his search results.  Rather, it is meant
as a learning tool.  It demonstrates generally how rotten search
results can be on one particular and not very compelling dimension.
It should not be necessary to download and scan each and every page.
You should be able to train yourself to ignore *a priori* results that
include handfuls of pages from unauthoritative sites.

This README file has a keyword density of approximately 0.026.

