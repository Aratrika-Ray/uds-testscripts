from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/infoQuery', methods=['POST'])
def infoQuery():
    try:
        info = request.get_json()
        schemefile = open('schemenumbers.json')
        schemenumbers = json.loads(schemefile.read())
        if(info['apiSecToken'] == schemenumbers['apiSecToken'] and info['campaignId'] != "" and info['enterpriseId'] != ""):
            unitTest = info['requestMsgId'].replace('reqMsg_', '')
            return {'schemeNumber': schemenumbers[unitTest], 'unitTest': unitTest}
        else: return {'error': 'invalid request fields'}
    except Exception as e:
        return {'error': f"infoQuery API error {e}"}

if __name__ == "__main__":
    app.run(debug=True)