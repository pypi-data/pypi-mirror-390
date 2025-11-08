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
import os
import threading
import os
from typing import Dict, Any
from dataclasses import dataclass
from collections import defaultdict
from datetime import timedelta
@dataclass
class bstack1lllll1ll11_opy_:
    id: str
    hash: str
    thread_id: int
    process_id: int
    type: str
class bstack1lllll11l1l_opy_:
    bstack11lll1l1l11_opy_ = bstack1111l1_opy_ (u"ࠢࡣࡧࡱࡧ࡭ࡳࡡࡳ࡭ࠥᘊ")
    context: bstack1lllll1ll11_opy_
    data: Dict[str, Any]
    platform_index: int
    def __init__(self, context: bstack1lllll1ll11_opy_):
        self.context = context
        self.data = dict({bstack1lllll11l1l_opy_.bstack11lll1l1l11_opy_: defaultdict(lambda: timedelta(microseconds=0))})
        self.platform_index = int(os.environ.get(bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨᘋ"), bstack1111l1_opy_ (u"ࠩ࠳ࠫᘌ")))
    def ref(self) -> str:
        return str(self.context.id)
    def bstack1llll1lll1l_opy_(self, target: object):
        return bstack1lllll11l1l_opy_.create_context(target) == self.context
    def bstack1l1llll1111_opy_(self, context: bstack1lllll1ll11_opy_):
        return context and context.thread_id == self.context.thread_id and context.process_id == self.context.process_id
    def bstack1l11ll1l11_opy_(self, key: str, value: timedelta):
        self.data[bstack1lllll11l1l_opy_.bstack11lll1l1l11_opy_][key] += value
    def bstack1ll1lllllll_opy_(self) -> dict:
        return self.data[bstack1lllll11l1l_opy_.bstack11lll1l1l11_opy_]
    @staticmethod
    def create_context(
        target: object,
        thread_id=threading.get_ident(),
        process_id=os.getpid(),
    ):
        return bstack1lllll1ll11_opy_(
            id=hash(target),
            hash=hash(target),
            thread_id=thread_id,
            process_id=process_id,
            type=target,
        )