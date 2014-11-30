from PyQt4.QtCore import pyqtSignal, pyqtSlot, QObject, QThread
from PyQt4.QtCore import Qt
from pizco import Signal, LOGGER
#Application
from PyQt4.QtGui import QApplication

__all__ = ["resync_proxy","SignalResync"]

resync_manager = None
qapp_global = None

def init_resync_manager():
    global resync_manager
    if resync_manager is None:
        resync_manager = QThread()
        resync_manager.start()

def init_qapplication():
    global qapp_global
    LOGGER.debug("instance {}".format(QApplication.instance()))
    if QApplication.instance() is None:
        LOGGER.warning("Automatically starting a QApplication in another thread, as Qapp not present at QObject creation")
        from threading import Thread, Event
        started_event = Event()
        def remote_qapp_thread():
            qapp_global = QApplication([])
            started_event.set()
            qapp_global.exec_()
        t = Thread(None,remote_qapp_thread,"remote_qapp_thread",args=())
        t.start()
        started_event.wait()


class AltThreadEmitter(QObject):
    #ensure the signal is emitted from a QObject
    #moreover ensure it is emitted from one which is not in the main thread
    generic_sig = pyqtSignal(tuple,dict)
    init_sig = pyqtSignal()
    def __init__(self, main_thread_receiver):
        super(AltThreadEmitter,self).__init__()
        init_resync_manager()
        self.moveToThread(resync_manager)
        LOGGER.debug("moving object to resync thread")
        self.generic_sig.connect(main_thread_receiver.generic_slot, Qt.QueuedConnection)
    def emit_(self,args,kwargs):
        #get thread id
        self.generic_sig.emit(args,kwargs)

class MainThreadEmitter(QObject):
    #ensure the signal is received in the main thread
    generic_sig = pyqtSignal(tuple,dict)
    def __init__(self, base_signal):
        init_qapplication()
        LOGGER.debug("creating the emitter")
        super(MainThreadEmitter,self).__init__()
        self.moveToThread(QApplication.instance().thread())
        LOGGER.debug("moving object to main thread")
        self.generic_sig.connect(self.generic_slot)
        self._base_signal = base_signal
    def emit_(self,args,kwargs):
        self.generic_sig.emit(args,kwargs)
    @pyqtSlot(tuple,dict)
    def generic_slot(self,args,kwargs):
        #get thread id
        self._base_signal.resync_emit(args,kwargs)

class SignalResync(Signal):
    #does it need a __setstate__, __getstate__, to avoid trying to transfer ?
    #it needs to be put in list
    def __init__(self,nargs,connection_type=Qt.AutoConnection, intermediate_thread=False):
        super(SignalResync,self).__init__(nargs)
        self._connection_type = connection_type
        self._intermediate_thread = intermediate_thread
        self._main_thread_emitter = MainThreadEmitter(self)
        if intermediate_thread:
            self._alt_thread_emitter = AltThreadEmitter(self._main_thread_emitter)
            self._emitter = self._alt_thread_emitter
        else:
            self._emitter = self._main_thread_emitter
    @staticmethod
    def Auto(connection_type=Qt.AutoConnection, intermediate_thread=False):
        return SignalResync(nargs=-1, connection_type=connection_type, intermediate_thread=intermediate_thread)
    def emit(self, *args,**kwargs):
        self._emitter.emit_(args, kwargs)
    def resync_emit(self, args, kwargs):
        super(SignalResync,self).emit(*args,**kwargs)
    def __pushback__(self):
        LOGGER.debug("pickle only the same as from_base_signal + connection_type,intermediate thread, mainthread emitter")
    def __get_state__(self):
        LOGGER.debug("getting state")
    def __set_state__(self,state):
        LOGGER.debug("setting state")
    @staticmethod
    def from_base_signal(signalbase, connection_type=Qt.AutoConnection, intermediate_thread=True):
        signalsync = SignalResync(signalbase._nargs, connection_type=connection_type, intermediate_thread=intermediate_thread)
        signalsync.slots = signalbase.slots
        signalsync._kwargs = signalbase._kwargs
        signalsync._varargs = signalbase._varargs
        signalsync._varkwargs = signalbase._varkwargs
        return signalsync


def resync_proxy(pxy):
    from pizco import Proxy
    assert(isinstance(pxy,Proxy))
    for signals in pxy._proxy_agent._signals:
        if not isinstance(pxy._proxy_agent._signals[signals],SignalResync) and isinstance(pxy._proxy_agent._signals[signals],Signal):
            pxy._proxy_agent._signals[signals] = SignalResync.from_base_signal(pxy._proxy_agent._signals[signals])

import unittest
#create a python thread, ensure the signal is received in the main thread.
#by creating a slot which is outputing thread id.
#create a pizco object and ensure there is no issues for the initialization of the object

class TestSync(QObject):
    update_curve_sig = pyqtSignal()
    def __init__(self):
        super(TestSync,self).__init__()
        self.update_curve_sig.connect(self.receiver)
        self._internal_value = 0
    @pyqtSlot()
    def initialize_subobject(self,parent):
        self.parent = parent
        from guiqwt.builder import make
        self.curve =  make.curve([], [])
        parent.plot.add_item(self.curve)
    @pyqtSlot()
    def update_curve(self):
        self.update_curve_sig.emit()
    @pyqtSlot()
    def receiver(self):
        import numpy as np
        self.initialize_subobject(self.parent)
        self.curve.set_data(np.linspace(0,100,1024),np.random.random(1024)*30)
    @pyqtSlot(int)
    def receiver_int(self,value):
        print(value)
        import numpy as np
        self._internal_value = value
        self.initialize_subobject(self.parent)
        self.curve.set_data(np.linspace(0,100,1024),np.random.random(1024)*20)
        self.parent.plot.do_autoscale(False)
        self.parent.plot.replot()

class RemotePizcoEmitterResync(object):
    def __init__(self):
        self.std_signal = SignalResync.Auto()
        self._nframe = 0
    def emission(self):
        self._nframe += 1
        self.std_signal.emit(self._nframe+1)

class RemotePizcoEmitter(object):
    std_signal = Signal.Auto()
    def __init__(self):
        self._nframe = 0
    def emission(self):
        self._nframe += 1
        self.std_signal.emit(self._nframe)

class TestSignalResync(unittest.TestCase):
    def test_normal_case(self):
        app = QApplication([])
        from threading import Thread
        from PyQt4.QtGui import QProgressBar
        import time
        pg = QProgressBar()
        def test_thread():
            std_signal = Signal(1)
            test_built_in = Signal(2)
            std_signal.connect(pg.setValue)
            test_built_in.connect(pg.setRange)
            v_int = 0
            while True:
                v_int += 1
                std_signal.emit(v_int)
                test_built_in.emit(0,10)
                time.sleep(0.5)
                if v_int == 5:
                    break
            pg.close()
        t = Thread(None,test_thread)
        t.start()
        pg.show()
        app.exec_()
    def test_guiqwt_case(self):
        app = QApplication([])
        from threading import Thread
        import numpy as np
        from guiqwt.plot import ImageWidget
        from guiqwt.builder import make
        import time
        im = ImageWidget()
        im.register_all_curve_tools()
        ts = TestSync()

        def test_thread():
            ts.initialize_subobject(im)
            std_signal = SignalResync(1)
            std_signal.connect(ts.receiver_int)
            #std_signal.connect(pg.setValue)
            #test_built_in.connect(pg.setRange)
            v_int = 0
            while True:
                v_int += 1
                #ts.update_curve() goes through a non generic signal
                std_signal.emit(v_int)
                time.sleep(0.5)
                if v_int == 5:
                    break
                im.close()
        t = Thread(None,test_thread)
        t.start()
        im.show()
        app.exec_()
        assert(ts._internal_value != 0)
    def test_guiqwt_case_altthread(self):
        app = QApplication([])
        from threading import Thread
        import numpy as np
        from guiqwt.plot import ImageWidget
        from guiqwt.builder import make
        import time
        im = ImageWidget()
        im.register_all_curve_tools()
        ts = TestSync()
        def test_thread():
            ts.initialize_subobject(im)
            std_signal = SignalResync.Auto(intermediate_thread=True)
            std_signal.connect(ts.receiver_int)
            v_int = 0
            while True:
                v_int += 1
                std_signal.emit(v_int)
                time.sleep(0.5)
                if v_int==5:
                    break
            im.close()
        t = Thread(None,test_thread)
        t.start()
        im.show()
        app.exec_()
        assert(ts._internal_value != 0)
    def test_qwt_case(self):
        app = QApplication([])
        from threading import Thread
        import numpy as np
        from PyQt4.Qwt5 import QwtThermo
        import time
        im = QwtThermo()
        def test_thread():
            std_signal = SignalResync.Auto(intermediate_thread=False)
            std_signal.connect(im.setValue)
            v_int = 0
            while True:
                v_int += 1
                std_signal.emit(v_int/10.)
                time.sleep(0.5)
                if v_int==5:
                    break
        t = Thread(None,test_thread)
        t.start()
        im.show()
        app.exec_()
        assert(ts._internal_value != 0)

    def test_proxy_resync(self):
        from pizco import Server
        pxy = Server.serve_in_process(RemotePizcoEmitter,(),{},rep_endpoint="tcp://127.0.0.1:1111")
        app = QApplication([])
        resync_proxy(pxy)
        from threading import Thread
        import numpy as np
        from guiqwt.plot import ImageWidget
        from guiqwt.builder import make
        import time
        im = ImageWidget()
        im.register_all_curve_tools()
        ts = TestSync()
        def test_thread():
            ts.initialize_subobject(im)
            pxy.std_signal.connect(ts.receiver_int)
            #std_signal.connect(pg.setValue)
            #test_built_in.connect(pg.setRange)
            v_int = 0
            while True:
                v_int += 1
                #ts.update_curve() goes through a non generic signal
                pxy.emission()
                time.sleep(0.5)
                if v_int==5:
                    break
            im.close()
        t = Thread(None,test_thread)
        t.start()
        im.show()
        app.exec_()
        pxy._proxy_stop_server()
        pxy._proxy_stop_me()
        assert(ts._internal_value != 0)

    def test_server_resync(self):
        from pizco import Server
        app = QApplication([])
        srv = RemotePizcoEmitterResync()
        pizco_srv = Server(srv,rep_endpoint="tcp://127.0.0.1:1211")
        from threading import Thread
        import numpy as np
        from guiqwt.plot import ImageWidget
        from guiqwt.builder import make
        import time
        im = ImageWidget()
        im.register_all_curve_tools()
        ts = TestSync()
        def test_thread():
            ts.initialize_subobject(im)
            srv.std_signal.connect(ts.receiver_int)
            v_int = 0
            while True:
                v_int += 1
                srv.emission()
                time.sleep(0.5)
                if v_int==5:
                    break
            im.close()
        t = Thread(None,test_thread)
        t.start()
        im.show()
        app.exec_()
        pizco_srv.stop()
        assert(ts._internal_value != 0)


if __name__=="__main__":
    unittest.main()