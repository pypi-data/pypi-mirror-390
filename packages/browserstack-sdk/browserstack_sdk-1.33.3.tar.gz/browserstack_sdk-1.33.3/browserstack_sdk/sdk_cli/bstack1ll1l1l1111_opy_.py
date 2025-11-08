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
import logging
import abc
from browserstack_sdk.sdk_cli.bstack1lllllll1l1_opy_ import bstack1lllllll1ll_opy_
class bstack1lll1111lll_opy_(abc.ABC):
    bin_session_id: str
    bstack1lllllll1l1_opy_: bstack1lllllll1ll_opy_
    def __init__(self):
        self.bstack1lll1l1lll1_opy_ = None
        self.config = None
        self.bin_session_id = None
        self.bstack1lllllll1l1_opy_ = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def bstack1lll1l111ll_opy_(self):
        return (self.bstack1lll1l1lll1_opy_ != None and self.bin_session_id != None and self.bstack1lllllll1l1_opy_ != None)
    def configure(self, bstack1lll1l1lll1_opy_, config, bin_session_id: str, bstack1lllllll1l1_opy_: bstack1lllllll1ll_opy_):
        self.bstack1lll1l1lll1_opy_ = bstack1lll1l1lll1_opy_
        self.config = config
        self.bin_session_id = bin_session_id
        self.bstack1lllllll1l1_opy_ = bstack1lllllll1l1_opy_
        if self.bin_session_id:
            self.logger.debug(bstack1111l1_opy_ (u"ࠣ࡝ࡾ࡭ࡩ࠮ࡳࡦ࡮ࡩ࠭ࢂࡣࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡧࡧࠤࡲࡵࡤࡶ࡮ࡨࠤࢀࡹࡥ࡭ࡨ࠱ࡣࡤࡩ࡬ࡢࡵࡶࡣࡤ࠴࡟ࡠࡰࡤࡱࡪࡥ࡟ࡾ࠼ࠣࡦ࡮ࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࡁࠧቯ") + str(self.bin_session_id) + bstack1111l1_opy_ (u"ࠤࠥተ"))
    def bstack1ll11111l1l_opy_(self):
        if not self.bin_session_id:
            raise ValueError(bstack1111l1_opy_ (u"ࠥࡦ࡮ࡴ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࠤࡨࡧ࡮࡯ࡱࡷࠤࡧ࡫ࠠࡏࡱࡱࡩࠧቱ"))
    @abc.abstractmethod
    def is_enabled(self) -> bool:
        return False