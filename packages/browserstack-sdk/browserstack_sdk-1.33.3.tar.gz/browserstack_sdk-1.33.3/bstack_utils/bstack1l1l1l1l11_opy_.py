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
from collections import deque
from bstack_utils.constants import *
class bstack11l1l1l1_opy_:
    def __init__(self):
        self._1llllllllll1_opy_ = deque()
        self._111111111ll_opy_ = {}
        self._11111111l1l_opy_ = False
        self._lock = threading.RLock()
    def bstack1lllllllllll_opy_(self, test_name, bstack11111111lll_opy_):
        with self._lock:
            bstack11111111111_opy_ = self._111111111ll_opy_.get(test_name, {})
            return bstack11111111111_opy_.get(bstack11111111lll_opy_, 0)
    def bstack1111111l1l1_opy_(self, test_name, bstack11111111lll_opy_):
        with self._lock:
            bstack1111111l11l_opy_ = self.bstack1lllllllllll_opy_(test_name, bstack11111111lll_opy_)
            self.bstack1111111l111_opy_(test_name, bstack11111111lll_opy_)
            return bstack1111111l11l_opy_
    def bstack1111111l111_opy_(self, test_name, bstack11111111lll_opy_):
        with self._lock:
            if test_name not in self._111111111ll_opy_:
                self._111111111ll_opy_[test_name] = {}
            bstack11111111111_opy_ = self._111111111ll_opy_[test_name]
            bstack1111111l11l_opy_ = bstack11111111111_opy_.get(bstack11111111lll_opy_, 0)
            bstack11111111111_opy_[bstack11111111lll_opy_] = bstack1111111l11l_opy_ + 1
    def bstack1l11l1l111_opy_(self, bstack11111111l11_opy_, bstack1111111111l_opy_):
        bstack11111111ll1_opy_ = self.bstack1111111l1l1_opy_(bstack11111111l11_opy_, bstack1111111111l_opy_)
        event_name = bstack11l1l1llll1_opy_[bstack1111111111l_opy_]
        bstack1l1l11ll1ll_opy_ = bstack1111l1_opy_ (u"ࠣࡽࢀ࠱ࢀࢃ࠭ࡼࡿࠥᾈ").format(bstack11111111l11_opy_, event_name, bstack11111111ll1_opy_)
        with self._lock:
            self._1llllllllll1_opy_.append(bstack1l1l11ll1ll_opy_)
    def bstack1l1llll111_opy_(self):
        with self._lock:
            return len(self._1llllllllll1_opy_) == 0
    def bstack1l11111111_opy_(self):
        with self._lock:
            if self._1llllllllll1_opy_:
                bstack111111111l1_opy_ = self._1llllllllll1_opy_.popleft()
                return bstack111111111l1_opy_
            return None
    def capturing(self):
        with self._lock:
            return self._11111111l1l_opy_
    def bstack11l1lll1ll_opy_(self):
        with self._lock:
            self._11111111l1l_opy_ = True
    def bstack111l1ll1l_opy_(self):
        with self._lock:
            self._11111111l1l_opy_ = False