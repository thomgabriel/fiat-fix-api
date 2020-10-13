import quickfix as fix
import quickfix44 as fixnn
import time
import logging
from util.logger import setup_logger
import json
import math
import statistics 
from flask import Flask,jsonify

app = Flask(__name__)

# Needed for single main.py file
THREADED_RUN = True

# Make 80 for AWS EC2, default is 5000
PORT = 80

# Make 0.0.0.0 to IP redirect, default is 127.0.0.1
HOST = '0.0.0.0'

DEBUG_SERVER = False

# Logger
setup_logger('logfix', 'Logs/message.log')
logfix = logging.getLogger('logfix')

cosmo_constant = 3
currencies = ["GBP/USD","EUR/USD","USD/CHF","USD/JPY","USD/CAD","USD/SGD","AUD/USD","NZD/USD","USD/ILS","USD/PLN","USD/TRY","USD/CNH","USD/HKD","USD/NOK","USD/SEK","USD/ZAR","USD/MXN","USD/THB"]
currjson = {
    "GBP":0.0,
    "EUR":0.0,
    "CHF":0.0,
    "JPY":0.0,
    "CAD":0.0,
    "SGD":0.0,
    "AUD":0.0,
    "NZD":0.0,
    "ILS":0.0,
    "PLN":0.0,
    "TRY":0.0,
    "CNH":0.0,
    "HKD":0.0,
    "NOK":0.0,
    "SEK":0.0,
    "ZAR":0.0,
    "MXN":0.0,
    "THB":0.0,
    }
index = {}
gauge = None

class Application(fix.Application):
    """FIX Application"""

    def onCreate(self, sessionID):
        self.sessionID = sessionID
        return
    def onLogon(self, sessionID):
        self.sessionID = sessionID
        print ("Successful Logon to session '%s'." % sessionID.toString())

        for curr in currencies:
            self.get_quote(curr)

        return
    def onLogout(self, sessionID): 
        return

    def toAdmin(self, message, sessionID):
        msgType = fix.MsgType ()
        message.getHeader().getField(msgType)
        if (msgType.getValue () == fix.MsgType_Logon):
            print('Logging on.')
   
            message.setField(fix.Password('DEMO032019'))
            message.setField(fix.Username('APPLEBY_DMFX_QS'))        
            message.setField (fix.ResetSeqNumFlag (True))   

        # logfix.info("S toAdmin >> %s" % message.toString())
        return

    def fromAdmin(self, message, sessionID):
        return

    def toApp(self, message, sessionID):
        logfix.info("\nSent the following message: %s" % message.toString())
        return

    def fromApp(self, message, sessionID):
        global currjson
        # logfix.info("\nReceived the following message: %s" % message.toString())

        if message.getField(55)[:3] == "USD":
            try:
                logfix.info('{}: {}'.format(message.getField(55)[-3:],round(1/float(message.getField(132)),5)))
                currjson[message.getField(55)[-3:]] = round(1/float(message.getField(132)),5)
            except:
                pass
        else:
            logfix.info('{}: {}'.format(message.getField(55)[:3],round(float(message.getField(132)),5)))
            currjson[message.getField(55)[:3]] = round(float(message.getField(132)),5)
        return

    def get_quote(self,curr):
        print("\nSubscribe {} Quote:".format(curr))
        quote = fix.Message()

        quote.getHeader().setField(fix.BeginString(fix.BeginString_FIX44)) 
        quote.getHeader().setField(fix.MsgType(fix.MsgType_QuoteRequest)) 
        
        quote.setField(fix.MsgType(fix.MsgType_QuoteRequest))
        quote.setField(fix.Symbol(curr)) 
        quote.setField(fix.QuoteReqID(curr))
        quote.setField(fix.QuoteRequestType(True))
    
        fix.Session.sendToTarget(quote, self.sessionID)

    # def marketDataRequest(self,curr):
    #     print("\nMarket Data Request for {}:".format(curr))
    #     marketData = fix.Message()

    #     marketData.getHeader().setField(fix.BeginString(fix.BeginString_FIX44)) 
    #     marketData.getHeader().setField(fix.MsgType(fix.MsgType_MarketDataRequest))

    #     marketData.setField(fix.MDReqID(curr)) 
    #     marketData.setField(fix.SubscriptionRequestType(fix.SubscriptionRequestType_SNAPSHOT_PLUS_UPDATES)) 
    #     marketData.setField(fix.MarketDepth(1))

    #     marketData.setField(fix.MDUpdateType(0))
    #     marketData.setField(fix.NoMDEntryTypes(2))
    #     marketData.setField(fix.NoRelatedSym(1))
        
    #     group = fixnn.MarketDataRequest().NoMDEntryTypes()
        
    #     group.setField(fix.MDEntryType(fix.MDEntryType_BID))
    #     marketData.addGroup(group)
        
    #     group.setField(fix.MDEntryType(fix.MDEntryType_OFFER))
    #     marketData.addGroup(group)

    #     symbol = fixnn.MarketDataRequest().NoRelatedSym()
       
    #     symbol.setField(fix.Symbol(curr))
    #     marketData.addGroup(symbol)

    #     fix.Session.sendToTarget(marketData, self.sessionID)

    def run(self):
        global gauge

        """Run"""
        while 1:
            if all(currjson.values()):
                try:
                    if all(curr for curr in currjson if currjson[curr] != 0.0):
                    # if len(currjson) == len(currencies):
                        for curr in list(enumerate(currjson)):
                            index[curr[1]] = round((currjson[curr[1]]+1)* math.exp((-(((cosmo_constant/len(currjson))*(curr[0]))**2))) +1,5)

                        gauge = round(statistics.mean(list(index[curr] for curr in index)),5)

                except:
                    pass

@app.route('/', methods=['GET'])
def data():
    return jsonify({'GAU': gauge, 'index' : index, 'currencies': currjson})

def run_server():
    print("Flask server started running.")
    app.run(host=HOST, port=PORT, debug=DEBUG_SERVER, threaded=THREADED_RUN)
