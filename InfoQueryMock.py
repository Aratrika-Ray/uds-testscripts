from datetime import datetime
from flask import Flask, request
import json, ssl

app = Flask(__name__)

@app.route('/infoQuery', methods=['POST'])
def infoQuery():
    try:
        info = request.get_json()
        schemefile = open('schemenumbers.json')
        schemenumbers = json.loads(schemefile.read())
        if(info['apiSecToken'] == schemenumbers['apiSecToken'] and info['campaignId'] != "" and info['entId'] != ""):
            unitTest = info['requestId'].split('@')[0].replace('NeuralNetClassifier_', '')
            if(unitTest in schemenumbers):
                schemenumber = schemenumbers[unitTest]
                return {'result': [{
                    "lastEngagementTime": datetime.now(),
                    "variables": {
                        "schemenumber": schemenumber
                    },
                    "requestId": info['requestId']
                }, ]}, 200
            else: return {'error': 'unit test case/scheme number not found'}, 404
        else:
            return {'error': 'invalid request fields'}, 400
    except Exception as e:
        return {'error': f"infoQuery API error {e}"}, 500


if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain("cert.pem", "key.pem", 'ushur@1234')
    app.run(debug=True, ssl_context=context)
