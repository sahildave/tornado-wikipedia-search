import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen

import os.path

import urllib
import json
import datetime
import time

from tornado.options import define, options

define("port", default=8888, type=int, help="runs on port")


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        print "in indexHandler"
        self.render('index.html')


class SearchHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        print "in searchHandler"
        query = self.get_argument('q')
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, "http://en.wikipedia.org/w/api.php?" +
                                          urllib.urlencode({"action": "query", "list": "search", "srsearch": query,
                                                            "format": "json", "srprop": "timestamp|snippet",
                                                            "continue": ""}))
        body = json.loads(response.body)

        queryJSON = body["query"]
        # print queryJSON
        # print "------"

        searchJSON = queryJSON["search"]
        # print searchJSON

        search_count = len(searchJSON)
        # print "------"
        # print search_count

        for page in searchJSON:
            title = page["title"]
            snippet = page["snippet"]
            timestamp = page["timestamp"]
            # timeTornado = datetime.datetime.strptime(timestamp, "%Y-%M-%DT%H:%M:%SZ")
            print title
            print timestamp
            # print timeTornado

        self.render(
            "results.html",
            searchResult=searchJSON
        )


class ResultItemModule(tornado.web.UIModule):
    def render(self, resultItem):
        return self.render_string(
            "modules/resultItem.html",
            resultItem=resultItem
        )


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[(r"/", IndexHandler), (r"/result", SearchHandler)],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        ui_modules={"ResultItem": ResultItemModule},
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()