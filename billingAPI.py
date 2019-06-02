'''
Created on 01-Jun-2019

@author: rohit
'''
import cherrypy
from utils.log_utils import OneLineExceptionFormatter
import logging
import sys
from collections import defaultdict
import time
import socket
import string
import random
from UI.bot_api import botUI
from items import add_initial_items
import requests


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Customer(object):
    api_start_time = time.time()
    LOG_FORMAT_STRING = '%(asctime)s [%(levelname)s] %(message)s'
    LOG_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, items=None):
        self.all_items = items if items else add_initial_items()
        self.name = ""
        self.purchased_items = {}
        self.maximum_amount = 0
        self.total_amount = 0
        root.info("API Start Time= {}s".format(time.time() -
                                               Customer.api_start_time))

    def purchase_item(self, name, quantity, unit):
        purchase_amounts = self.all_items.get_purchase_money_of_an_item(
            name, quantity, unit)
        if name not in self.purchased_items:
            self.purchased_items[name] = [
                quantity, purchase_amounts[0], self.all_items.get_item(name)
                .unit
            ]
        else:
            self.purchased_items[name][0] += purchase_amounts[
                1] / self.all_items.get_item(name).price
            self.purchased_items[name][1] += purchase_amounts[0]
        self.total_amount += purchase_amounts[0]
        self.maximum_amount += purchase_amounts[1]

    def remove_all_items(self):
        self.name = ""
        self.purchased_items = {}
        self.maximum_amount = 0
        self.total_amount = 0

    def get_bill(self):
        res = requests.post(
            "http://localhost:8080/receipt",
            json={
                "Customer Name": self.name,
                "Items": self.purchased_items,
                "MRP": self.maximum_amount,
                "Total Price": self.total_amount
            }).content
        self.remove_all_items()
        return res

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def webhook(self):
        cherrypy.response.headers['Content-Type'] = "application/json"
        cherrypy.response.headers['Connection'] = "close"

        params = defaultdict(dict)
        if cherrypy.request.method == "POST":
            params = cherrypy.request.json

        if "name" in params:
            self.name = params["name"]
        err = ""
        if "items" in params:
            corrupted_items = []
            for i, item in enumerate(params["items"]):
                if "iName" in item and "iQuantity" in item and "iUnit" in item:
                    self.purchase_item(item["iName"], item["iQuantity"],
                                       item["iUnit"])
                else:
                    corrupted_items.append(i)
            if corrupted_items:
                err = "Items from indexes {} does not have all required parameters:{iName, iQuantity, iUnit}".format(
                    corrupted_items)
        else:
            err = "Unable to Add Items due to missing Parameters (items = [{iName, iQuantity, iUnit}])"

        return {"fullfillment": err if err else self.get_bill()}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def monitor(self):
        cherrypy.response.headers['Content-Type'] = "application/json"
        cherrypy.response.headers['Connection'] = "close"
        cherrypy.response.status = 200
        thread_id = id_generator()
        response_json = {
            "containerId": socket.gethostname(),
            "threadId": thread_id
        }
        return response_json


if __name__ == "__main__":
    logging_handler = logging.StreamHandler(sys.stdout)
    log_format = OneLineExceptionFormatter(Customer.LOG_FORMAT_STRING,
                                           Customer.LOG_TIME_FORMAT)
    logging_handler.setFormatter(log_format)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(logging_handler)
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080,
        'server.thread_pool_max': 1,
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'response.timeout': 600,
        'server.socket_queue_size': 10,
        'engine.timeout_monitor.on': False,
        'log.screen': False,
        'log.access_file': '',
        'log.error_log_propagate': False,
        'log.accrss_log.propagate': False,
        'log.error_file': ''
    })

    cherrypy.tree.mount(Customer(), '/customer', config={'/': {}})
    cherrypy.tree.mount(botUI(), '/', config={'/': {}})
    cherrypy.engine.start()
    cherrypy.engine.block()
