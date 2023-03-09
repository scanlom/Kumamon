'''
Created on Nov 13, 2017
@author: scanlom
'''

from ibapi.wrapper import EWrapper
from ibapi.client import EClient, Contract
from threading import Thread
import queue
from lib_log import log

class TestWrapper(EWrapper):
    """
    The wrapper deals with the action coming back from the IB gateway or TWS instance
    We override methods in EWrapper that will get called when this action happens, like currentTime
    """

    ## error handling code
    def init_error(self):
        error_queue=queue.Queue()
        self._my_errors = error_queue

    def get_error(self, timeout=5):
        if self.is_error():
            try:
                return self._my_errors.get(timeout=timeout)
            except queue.Empty:
                return None

        return None

    def is_error(self):
        an_error_if=not self._my_errors.empty()
        return an_error_if

    def error(self, id, errorCode, errorString):
        ## Overriden method
        errormsg = "IB error id %d errorcode %d string %s" % (id, errorCode, errorString)
        self._my_errors.put(errormsg)

    ## Time telling code
    def init_time(self):
        time_queue=queue.Queue()
        self._time_queue = time_queue
        return time_queue

    def init_fun(self):
        fun_queue=queue.Queue()
        self._fun_queue = fun_queue
        return fun_queue

    def currentTime(self, time_from_server):
        ## Overriden method
        self._time_queue.put(time_from_server)
        super().currentTime(time_from_server)

    def fundamentalData(self, reqId, data):
        self._fun_queue.put(data)
        with open('/home/scanlom/tmp/mikey.xml', 'w+') as file:
            file.write(data)
        print("FundamentalData. ReqId:", reqId, "Data:", data)
        super().fundamentalData(reqId, data)

class TestClient(EClient):
    """
    The client method
    We don't override native methods, but instead call them from our own wrappers
    """
    def __init__(self, wrapper):
        ## Set up with a wrapper inside
        EClient.__init__(self, wrapper)

    def big_fundamental(self):
        contract = Contract()
        contract.symbol = "IBKR"
        contract.secType = "STK"
        contract.currency = "USD"
        #In the API side, NASDAQ is always defined as ISLAND in the exchange field
        contract.exchange = "ISLAND"

        fun_storage=self.wrapper.init_fun()

        self.reqFundamentalData(8001, contract, "RESC", [])

        MAX_WAIT_SECONDS = 10

        try:
            current_fun = fun_storage.get(timeout=MAX_WAIT_SECONDS)
        except queue.Empty:
            print("Exceeded maximum wait for wrapper to respond")
            current_fun = None

        while self.wrapper.is_error():
            print(self.get_error())

    def speaking_clock(self):
        """
        Basic example to tell the time
        :return: unix time, as an int
        """

        print("Getting the time from the server... ")

        ## Make a place to store the time we're going to return
        ## This is a queue
        time_storage=self.wrapper.init_time()

        ## This is the native method in EClient, asks the server to send us the time please
        self.reqCurrentTime()

        ## Try and get a valid time
        MAX_WAIT_SECONDS = 10

        try:
            current_time = time_storage.get(timeout=MAX_WAIT_SECONDS)
        except queue.Empty:
            print("Exceeded maximum wait for wrapper to respond")
            current_time = None

        while self.wrapper.is_error():
            print(self.get_error())

        return current_time

class TestApp(TestWrapper, TestClient):
    def __init__(self, ipaddress, portid, clientid):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper=self)

        self.connect(ipaddress, portid, clientid)

        thread = Thread(target = self.run)
        thread.start()

        setattr(self, "_thread", thread)

        self.init_error()

def main():
    log.info("Started...")
    ##
    ## Check that the port is the same as on the Gateway
    ## ipaddress is 127.0.0.1 if one same machine, clientid is arbitrary

    app = TestApp("127.0.0.1", 7496, 10)

    app.big_fundamental()

    current_time = app.speaking_clock()
    print(current_time)
    
    app.disconnect()
    log.info("Completed")

if __name__ == '__main__':
    try:
        main()    
    except Exception as err:
        log.exception(err)
        log.info("Aborted") 