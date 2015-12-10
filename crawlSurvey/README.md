# Crawl responses using Selenium from SurveyMonkey and process them.

1. crawl.py crawls the SurveyMonkey responses using Selenium and into raw data:
    * Input: surveymonkey.com
    * Output: output/rawResponseData.json
    
2. parseResponess.py parses the raw output given by crawl.py.
    * Input: output/rawResponseData.json
    * Output: output/parsedResponses.json, output/parsedResponses.tsv

# TODOs:

* Invalidate some responses. E.g.:
    * Gibberish responses
* Read and analyze responses
* Statistical patterns