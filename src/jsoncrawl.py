#!/usr/bin/env python
import logging
import json

from settings import settings
import module

class JsonCrawl(module.Crawler):
    def __init__(self, path):
        module.Crawler.__init__(self)
        self.path = path

    def crawl(self):
        for l in open(self.path):
            yield json.loads(l)

if __name__ == '__main__':
    module.main(JsonCrawl)
