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
from collections import defaultdict
from threading import Lock
from dataclasses import dataclass
import logging
import traceback
from typing import List, Dict, Any
import os
@dataclass
class bstack1l1l1ll1_opy_:
    sdk_version: str
    path_config: str
    path_project: str
    test_framework: str
    frameworks: List[str]
    framework_versions: Dict[str, str]
    bs_config: Dict[str, Any]
@dataclass
class bstack11l11111_opy_:
    pass
class bstack11l11ll11_opy_:
    bstack11l11ll1ll_opy_ = bstack1111l1_opy_ (u"ࠥࡦࡴࡵࡴࡴࡶࡵࡥࡵࠨᆃ")
    CONNECT = bstack1111l1_opy_ (u"ࠦࡨࡵ࡮࡯ࡧࡦࡸࠧᆄ")
    bstack1l1111ll11_opy_ = bstack1111l1_opy_ (u"ࠧࡹࡨࡶࡶࡧࡳࡼࡴࠢᆅ")
    CONFIG = bstack1111l1_opy_ (u"ࠨࡣࡰࡰࡩ࡭࡬ࠨᆆ")
    bstack1ll1l11l11l_opy_ = bstack1111l1_opy_ (u"ࠢࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡶࠦᆇ")
    bstack1lll1111_opy_ = bstack1111l1_opy_ (u"ࠣࡧࡻ࡭ࡹࠨᆈ")
class bstack1ll1l111ll1_opy_:
    bstack1ll1l1111ll_opy_ = bstack1111l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡵࡷࡥࡷࡺࡥࡥࠤᆉ")
    FINISHED = bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡩ࡭ࡳ࡯ࡳࡩࡧࡧࠦᆊ")
class bstack1ll1l111l1l_opy_:
    bstack1ll1l1111ll_opy_ = bstack1111l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡳࡵࡣࡵࡸࡪࡪࠢᆋ")
    FINISHED = bstack1111l1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࠤᆌ")
class bstack1ll1l111l11_opy_:
    bstack1ll1l1111ll_opy_ = bstack1111l1_opy_ (u"ࠨࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡵࡷࡥࡷࡺࡥࡥࠤᆍ")
    FINISHED = bstack1111l1_opy_ (u"ࠢࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡩ࡭ࡳ࡯ࡳࡩࡧࡧࠦᆎ")
class bstack1ll1l11l111_opy_:
    bstack1ll1l111lll_opy_ = bstack1111l1_opy_ (u"ࠣࡥࡥࡸࡤࡹࡥࡴࡵ࡬ࡳࡳࡥࡣࡳࡧࡤࡸࡪࡪࠢᆏ")
class bstack1ll1l1111l1_opy_:
    _1lll1llllll_opy_ = None
    def __new__(cls):
        if not cls._1lll1llllll_opy_:
            cls._1lll1llllll_opy_ = super(bstack1ll1l1111l1_opy_, cls).__new__(cls)
        return cls._1lll1llllll_opy_
    def __init__(self):
        self._hooks = defaultdict(lambda: defaultdict(list))
        self._lock = Lock()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    def clear(self):
        with self._lock:
            self._hooks = defaultdict(list)
    def register(self, event_name, callback):
        with self._lock:
            if not callable(callback):
                raise ValueError(bstack1111l1_opy_ (u"ࠤࡆࡥࡱࡲࡢࡢࡥ࡮ࠤࡲࡻࡳࡵࠢࡥࡩࠥࡩࡡ࡭࡮ࡤࡦࡱ࡫ࠠࡧࡱࡵࠤࠧᆐ") + event_name)
            pid = os.getpid()
            self.logger.debug(bstack1111l1_opy_ (u"ࠥࡖࡪ࡭ࡩࡴࡶࡨࡶ࡮ࡴࡧࠡࡥࡤࡰࡱࡨࡡࡤ࡭ࠣࡪࡴࡸࠠࡦࡸࡨࡲࡹࠦࠧࡼࡧࡹࡩࡳࡺ࡟࡯ࡣࡰࡩࢂ࠭ࠠࡸ࡫ࡷ࡬ࠥࡶࡩࡥࠢࠥᆑ") + str(pid) + bstack1111l1_opy_ (u"ࠦࠧᆒ"))
            self._hooks[event_name][pid].append(callback)
    def invoke(self, event_name, *args, **kwargs):
        with self._lock:
            pid = os.getpid()
            callbacks = self._hooks.get(event_name, {}).get(pid, [])
            if not callbacks:
                self.logger.warning(bstack1111l1_opy_ (u"ࠧࡔ࡯ࠡࡥࡤࡰࡱࡨࡡࡤ࡭ࡶࠤ࡫ࡵࡲࠡࡧࡹࡩࡳࡺࠠࠨࡽࡨࡺࡪࡴࡴࡠࡰࡤࡱࡪࢃࠧࠡࡹ࡬ࡸ࡭ࠦࡰࡪࡦࠣࠦᆓ") + str(pid) + bstack1111l1_opy_ (u"ࠨࠢᆔ"))
                return
            self.logger.debug(bstack1111l1_opy_ (u"ࠢࡊࡰࡹࡳࡰ࡯࡮ࡨࠢࡾࡰࡪࡴࠨࡤࡣ࡯ࡰࡧࡧࡣ࡬ࡵࠬࢁࠥࡩࡡ࡭࡮ࡥࡥࡨࡱࡳࠡࡨࡲࡶࠥ࡫ࡶࡦࡰࡷࠤࠬࢁࡥࡷࡧࡱࡸࡤࡴࡡ࡮ࡧࢀࠫࠥࡽࡩࡵࡪࠣࡴ࡮ࡪࠠࠣᆕ") + str(pid) + bstack1111l1_opy_ (u"ࠣࠤᆖ"))
            for callback in callbacks:
                try:
                    self.logger.debug(bstack1111l1_opy_ (u"ࠤࡌࡲࡻࡵ࡫ࡦࡦࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯ࠥ࡬࡯ࡳࠢࡨࡺࡪࡴࡴࠡࠩࡾࡩࡻ࡫࡮ࡵࡡࡱࡥࡲ࡫ࡽࠨࠢࡺ࡭ࡹ࡮ࠠࡱ࡫ࡧࠤࠧᆗ") + str(pid) + bstack1111l1_opy_ (u"ࠥࠦᆘ"))
                    callback(event_name, *args, **kwargs)
                except Exception as e:
                    self.logger.error(bstack1111l1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࡼ࡯࡬࡫ࡱ࡫ࠥࡩࡡ࡭࡮ࡥࡥࡨࡱࠠࡧࡱࡵࠤࡪࡼࡥ࡯ࡶࠣࠫࢀ࡫ࡶࡦࡰࡷࡣࡳࡧ࡭ࡦࡿࠪࠤࡼ࡯ࡴࡩࠢࡳ࡭ࡩࠦࡻࡱ࡫ࡧࢁ࠿ࠦࠢᆙ") + str(e) + bstack1111l1_opy_ (u"ࠧࠨᆚ"))
                    traceback.print_exc()
bstack11l111l1_opy_ = bstack1ll1l1111l1_opy_()