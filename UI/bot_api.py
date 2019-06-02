import cherrypy
from bs4 import BeautifulSoup


class botUI(object):
    def __init__(self):
        self.data = {}

    @cherrypy.expose
    def home(self):
        return open("UI/templates/index.html")

    @cherrypy.expose
    def items(self):
        return open("UI/templates/items.html")

    @cherrypy.expose
    def agentDomJs(self):
        return open("UI/jscripts/agentDemo.bundle.min.js")

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def receipt(self):
        cherrypy.response.headers['Content-Type'] = "application/json"
        cherrypy.response.headers['Connection'] = "close"

        if cherrypy.request.method == "POST":
            params = cherrypy.request.json

            cname = params["Customer Name"]
            details = params["Items"]
            mrp = params["MRP"]
            total = params["Total Price"]

            soup = BeautifulSoup(open("UI/templates/receipt.html"))

            m = soup.find('', {'id': "bill_details"})
            for k, v in details.items():
                row = soup.new_tag('tr')
                data = soup.new_tag('td')
                data.string = k
                row.append(data)
                data = soup.new_tag('td')
                data.string = "{} {}".format(v[0], v[2])
                row.append(data)
                data = soup.new_tag('td')
                data.string = str(v[1])
                row.append(data)
                m.append(row)
            m = soup.find('', {'id': "customer_name"})
            m.string = str(cname)
            m = soup.find('', {'id': "saving_details"})
            m.string = "{} - {}".format(mrp, total)
            m = soup.find('', {'id': "total_saving"})
            m.string = "= {}".format(mrp - total)
            m = soup.find('', {'id': "total_amount"})
            m.string = str(total)
        else:
            soup = "<h2>Request type should be POST...</h2>"

        return str(soup)
