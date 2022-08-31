# How to contribute to the Simple German Dataset
Our work constitutes only a first step towards an extensive and valuable text corpus for simple German language. There are different ways to contribute.

## Bugs and issues
While using our dataset, please report any bugs or problems you might encounter by creating an issue.
## Website Suggestions
Finding suitable websites is a prerequisite for extensions of our corpus. If you know any websites that offer their content in German as well as some simplified version of it, you can suggest them. 
Requirements:
- the website's content must be in German
- for each article in German there must be corresponding article in simple language
- the simplification should be according to [Einfache Sprache](https://de.wikipedia.org/wiki/Einfache_Sprache#H%C3%A4ufige_Empfehlungen_f%C3%BCr_Einfache_Sprache) or [Leichte Sprache](https://leichte-sprache.de/download/1988/); see also [this comparison](https://www.bpb.de/shop/zeitschriften/apuz/179341/leichte-und-einfache-sprache-versuch-einer-definition/) (these links lead to websites in German)
- all German and simple German articles should be linked more or less uniformly
- good to know: is the website continuously publishing new parallel articles?

Take a look at the Dataset folder in order to see which websites we've already covered.

## Additional Crawlers
If you have not only found a new online source, but would also like to contribute the corresponding crawler, you can find a template under crawler/crawler_template.py. The final crawler should create a new {source-url} folder containing a crawled folder with all html files. The script crawler/archive.py can be used to archive all urls with the WaybackMachine.

## Sentence Alignment
For our sentence alignment, we tested a variety of similarity measures and matching algorithms. We report the results and make a suggestion for the best possible alignment based on them. Still, the results are by no means perfect and we would love to extent the list of tested algorithems. 