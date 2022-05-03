import requests
from pprint import PrettyPrinter

PP=PrettyPrinter(indent=2)


json_dict = {"requests": [
    { "rid": "08cbb8cf-545d-4fb6-8d04-4daf39b218e2",
        "analytic_input": { "id": "detectron2-organoid-model", "version": "0.1.0" }
        }
    ]
}


def send_modelreq():
    for x in range(0, 1):
        req = requests.post('http://backend.xilis.tools/analytics_management/run_analytics', json=json_dict)
        PP.pprint(req.__dict__)


def get_analytics():
    req = requests.get('http://backend.xilis.tools/analytics_management/get_available_analytics')
    PP.pprint(req.json())

def get_analytics_version():
    req = requests.get('http://backend.xilis.tools/analytics_management/')
    PP.pprint(req.content)


if __name__ == '__main__':
    send_modelreq()
    #get_analytics()
