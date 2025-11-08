# coding: UTF-8
import sys
bstack1l11l1l_opy_ = sys.version_info [0] == 2
bstack1_opy_ = 2048
bstack11llll_opy_ = 7
def bstack1111l1_opy_ (bstack11l1ll_opy_):
    global bstack1l111ll_opy_
    bstackl_opy_ = ord (bstack11l1ll_opy_ [-1])
    bstack1l1111_opy_ = bstack11l1ll_opy_ [:-1]
    bstack1ll1l11_opy_ = bstackl_opy_ % len (bstack1l1111_opy_)
    bstack111ll_opy_ = bstack1l1111_opy_ [:bstack1ll1l11_opy_] + bstack1l1111_opy_ [bstack1ll1l11_opy_:]
    if bstack1l11l1l_opy_:
        bstack1l11111_opy_ = unicode () .join ([unichr (ord (char) - bstack1_opy_ - (bstack1l1l_opy_ + bstackl_opy_) % bstack11llll_opy_) for bstack1l1l_opy_, char in enumerate (bstack111ll_opy_)])
    else:
        bstack1l11111_opy_ = str () .join ([chr (ord (char) - bstack1_opy_ - (bstack1l1l_opy_ + bstackl_opy_) % bstack11llll_opy_) for bstack1l1l_opy_, char in enumerate (bstack111ll_opy_)])
    return eval (bstack1l11111_opy_)
import threading
import logging
logger = logging.getLogger(__name__)
bstack1lllll1ll1l1_opy_ = 1000
bstack1lllll1lll11_opy_ = 2
class bstack1lllll1lll1l_opy_:
    def __init__(self, handler, bstack1lllll1ll11l_opy_=bstack1lllll1ll1l1_opy_, bstack1lllll1l1l1l_opy_=bstack1lllll1lll11_opy_):
        self.queue = []
        self.handler = handler
        self.bstack1lllll1ll11l_opy_ = bstack1lllll1ll11l_opy_
        self.bstack1lllll1l1l1l_opy_ = bstack1lllll1l1l1l_opy_
        self.lock = threading.Lock()
        self.timer = None
        self.bstack1llllllllll_opy_ = None
    def start(self):
        if not (self.timer and self.timer.is_alive()):
            self.bstack1lllll1ll1ll_opy_()
    def bstack1lllll1ll1ll_opy_(self):
        self.bstack1llllllllll_opy_ = threading.Event()
        def bstack1lllll1l1ll1_opy_():
            self.bstack1llllllllll_opy_.wait(self.bstack1lllll1l1l1l_opy_)
            if not self.bstack1llllllllll_opy_.is_set():
                self.bstack1lllll1l1lll_opy_()
        self.timer = threading.Thread(target=bstack1lllll1l1ll1_opy_, daemon=True)
        self.timer.start()
    def bstack1lllll1l1l11_opy_(self):
        try:
            if self.bstack1llllllllll_opy_ and not self.bstack1llllllllll_opy_.is_set():
                self.bstack1llllllllll_opy_.set()
            if self.timer and self.timer.is_alive() and self.timer != threading.current_thread():
                self.timer.join()
        except Exception as e:
            logger.debug(bstack1111l1_opy_ (u"ࠫࡠࡹࡴࡰࡲࡢࡸ࡮ࡳࡥࡳ࡟ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࡀࠠࠨΏ") + (str(e) or bstack1111l1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡥࡲࡹࡱࡪࠠ࡯ࡱࡷࠤࡧ࡫ࠠࡤࡱࡱࡺࡪࡸࡴࡦࡦࠣࡸࡴࠦࡳࡵࡴ࡬ࡲ࡬ࠨῼ")))
        finally:
            self.timer = None
    def bstack1lllll1ll111_opy_(self):
        if self.timer:
            self.bstack1lllll1l1l11_opy_()
        self.bstack1lllll1ll1ll_opy_()
    def add(self, event):
        with self.lock:
            self.queue.append(event)
            if len(self.queue) >= self.bstack1lllll1ll11l_opy_:
                threading.Thread(target=self.bstack1lllll1l1lll_opy_).start()
    def bstack1lllll1l1lll_opy_(self, source = bstack1111l1_opy_ (u"࠭ࠧ´")):
        with self.lock:
            if not self.queue:
                self.bstack1lllll1ll111_opy_()
                return
            data = self.queue[:self.bstack1lllll1ll11l_opy_]
            del self.queue[:self.bstack1lllll1ll11l_opy_]
        self.handler(data)
        if source != bstack1111l1_opy_ (u"ࠧࡴࡪࡸࡸࡩࡵࡷ࡯ࠩ῾"):
            self.bstack1lllll1ll111_opy_()
    def shutdown(self):
        self.bstack1lllll1l1l11_opy_()
        while self.queue:
            self.bstack1lllll1l1lll_opy_(source=bstack1111l1_opy_ (u"ࠨࡵ࡫ࡹࡹࡪ࡯ࡸࡰࠪ῿"))