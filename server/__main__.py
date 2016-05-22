# -*- coding:UTF-8 -*-
import tornadoredis
import json
import time
import logging

from datetime import datetime

from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.web import Application
from tornado.web import url
from tornado import gen
from tornado.websocket import WebSocketHandler

from argparse import ArgumentParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def make_message(msg, user):
    return {"from": user.name, "msg": str(msg),
            "type": "message", "avatar": user.avatar,
            "datetime": int(time.time())}


class UserRepository:

    def __init__(self, db):
        self.db = db

    @gen.coroutine
    def get(self, name):
        db = self.db

        user_json = yield gen.Task(db.get, "user:%s" % name)
        if not user_json:
            return None

        return User.from_dict(json.loads(user_json))

    @gen.coroutine
    def save(self, user):
        user_json = json.dumps(user.to_dict())
        yield gen.Task(self.db.set, "user_%s" % user.name, user_json)

    @gen.coroutine
    def remove(self, user):
        yield genTask(db.delete, "user:%s" % user.name)

class User:

    def __init__(self, id=None, name=None, avatar=""):
        self.name = name
        self.avatar = avatar
        self.id = id

    def to_dict(self):

        to_dict =  {"name": self.name, "avatar": self.avatar}
        if self.id:
            to_dict["id"] = self.id

        return to_dict

    @classmethod
    def from_dict(cls, data):

        id = str(data["id"])
        name = data["name"]
        avatar = data.get("avatar", "")

        obj = cls(id=id, name=name, avatar=avatar)
        return obj

    def __str__(self):
        return str({"id": str(self.id), "name": self.name})


class MessageWSHandler(WebSocketHandler):
    """ User messenger websocket """

    def __init__(self, *args, **kwargs):
        super(MessageWSHandler, self).__init__(*args, **kwargs)
        self.user_repo = UserRepository(self.settings['db'])
    @gen.coroutine
    def subscribe(self):
        self.subscription = tornadoredis.Client()
        self.subscription.connect()

        yield gen.Task(self.subscription.subscribe, "broadcast")
        self.subscription.listen(self.subscription_message)

    def subscription_message(self, message):

        if message.kind != "message":
            logger.info("Unable to handle message %s", str(message))
            return

        logger.info("Validating message %s" % message.body)

        self.write_message(message.body)

    def check_origin(self, origin):
        return True

    @gen.coroutine
    def open(self, name):
        logger.debug("new connection %s" % name)
        self.user = yield self.user_repo.get(name)

        yield self.subscribe()

        if not self.user:
            self.user = User(name)
            yield self.user_repo.save(self.user)
            logger.info("New user created! %s" % name)

    @gen.coroutine
    def on_message(self, data_json):
        logger.info(u"Message received: " + str(data_json))
        if not self.user:
            return

        data = json.loads(data_json)
        self.message_handler(data)

    def on_close(self):
        logger.debug("connection closed, user: %s" % str(self.user))
        super(self.__class__, self).on_close()
        self.subscription.unsubscribe('broadcast')

    def message_handler(self, data):
        message = make_message(data.get("message", ""), self.user)
        self.settings['db'].publish("broadcast", message)


def main():

    app = Application([url(r"/ws/(\w+)", MessageWSHandler)])

    parser = ArgumentParser()
    parser.add_argument("--redis", help="Redis host", default="localhost")
    parser.add_argument("--port", help="Server port", default=8888)
    parser.add_argument("--distance", help="Distance", default=1000)
    args = parser.parse_args()

    server = HTTPServer(app)
    server.bind(args.port)
    server.start()

    redis_connection = tornadoredis.Client(args.redis)
    redis_connection.connect()
    app.settings["db"] = redis_connection

    IOLoop.current().start()


if __name__ ==  "__main__":
    main()
