cnncmall.csv: cnncmall-spider.py
	scrapy runspider $< -o $@

deli.csv: deli-spider.py
	scrapy runspider $< -o $@

staples.csv: staples-spider.py
	scrapy runspider $< -o $@

jd-deli.csv: jd-deli-spider.py
	scrapy runspider $< -o $@

.PHONY: clean

clean:
		rm -f *.csv
