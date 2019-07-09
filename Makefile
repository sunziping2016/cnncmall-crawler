cnncmall.csv: cnncmall-spider.py
	scrapy runspider $< -o $@

.PHONY: clean

clean:
		rm -f *.csv
