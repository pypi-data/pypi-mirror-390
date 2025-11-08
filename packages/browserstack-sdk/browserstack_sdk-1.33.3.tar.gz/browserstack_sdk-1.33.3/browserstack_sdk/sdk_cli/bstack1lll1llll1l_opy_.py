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
import traceback
from typing import Dict, Tuple, Callable, Type, List, Any
from urllib.parse import urlparse
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1lllll11l11_opy_,
    bstack1llll1l11l1_opy_,
    bstack1llll1ll11l_opy_,
    bstack1lllll11111_opy_,
)
import copy
from datetime import datetime, timezone, timedelta
class bstack1ll1ll1111l_opy_(bstack1lllll11l11_opy_):
    bstack1l111lllll1_opy_ = bstack1111l1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝ࠨᐻ")
    bstack1l1l1111lll_opy_ = bstack1111l1_opy_ (u"ࠢࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡪࡹࡳࡪࡱࡱࡣ࡮ࡪࠢᐼ")
    bstack1l1l1111l1l_opy_ = bstack1111l1_opy_ (u"ࠣࡪࡸࡦࡤࡻࡲ࡭ࠤᐽ")
    bstack1l1l111l1l1_opy_ = bstack1111l1_opy_ (u"ࠤࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᐾ")
    bstack1l11l111111_opy_ = bstack1111l1_opy_ (u"ࠥࡻ࠸ࡩࡥࡹࡧࡦࡹࡹ࡫ࡳࡤࡴ࡬ࡴࡹࠨᐿ")
    bstack1l111llll11_opy_ = bstack1111l1_opy_ (u"ࠦࡼ࠹ࡣࡦࡺࡨࡧࡺࡺࡥࡴࡥࡵ࡭ࡵࡺࡡࡴࡻࡱࡧࠧᑀ")
    NAME = bstack1111l1_opy_ (u"ࠧࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠤᑁ")
    bstack1l111llllll_opy_: Dict[str, List[Callable]] = dict()
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1lll1111111_opy_: Any
    bstack1l111lll1ll_opy_: Dict
    def __init__(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        methods=[bstack1111l1_opy_ (u"ࠨ࡬ࡢࡷࡱࡧ࡭ࠨᑂ"), bstack1111l1_opy_ (u"ࠢࡤࡱࡱࡲࡪࡩࡴࠣᑃ"), bstack1111l1_opy_ (u"ࠣࡰࡨࡻࡤࡶࡡࡨࡧࠥᑄ"), bstack1111l1_opy_ (u"ࠤࡦࡰࡴࡹࡥࠣᑅ"), bstack1111l1_opy_ (u"ࠥࡨ࡮ࡹࡰࡢࡶࡦ࡬ࠧᑆ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.platform_index = platform_index
        self.bstack1llll11ll11_opy_(methods)
    def bstack1lllll11lll_opy_(self, instance: bstack1llll1l11l1_opy_, method_name: str, bstack1llll1ll1ll_opy_: timedelta, *args, **kwargs):
        pass
    def bstack1lllllll11l_opy_(
        self,
        target: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ) -> Callable[..., Any]:
        instance, method_name = exec
        bstack1llll11lll1_opy_, bstack1l111llll1l_opy_ = bstack1llll1ll1l1_opy_
        bstack1l111lll1l1_opy_ = bstack1ll1ll1111l_opy_.bstack1l111lll111_opy_(bstack1llll1ll1l1_opy_)
        if bstack1l111lll1l1_opy_ in bstack1ll1ll1111l_opy_.bstack1l111llllll_opy_:
            bstack1l111lll11l_opy_ = None
            for callback in bstack1ll1ll1111l_opy_.bstack1l111llllll_opy_[bstack1l111lll1l1_opy_]:
                try:
                    bstack1l11l11111l_opy_ = callback(self, target, exec, bstack1llll1ll1l1_opy_, result, *args, **kwargs)
                    if bstack1l111lll11l_opy_ == None:
                        bstack1l111lll11l_opy_ = bstack1l11l11111l_opy_
                except Exception as e:
                    self.logger.error(bstack1111l1_opy_ (u"ࠦࡪࡸࡲࡰࡴࠣ࡭ࡳࡼ࡯࡬࡫ࡱ࡫ࠥࡩࡡ࡭࡮ࡥࡥࡨࡱ࠺ࠡࠤᑇ") + str(e) + bstack1111l1_opy_ (u"ࠧࠨᑈ"))
                    traceback.print_exc()
            if bstack1l111llll1l_opy_ == bstack1lllll11111_opy_.PRE and callable(bstack1l111lll11l_opy_):
                return bstack1l111lll11l_opy_
            elif bstack1l111llll1l_opy_ == bstack1lllll11111_opy_.POST and bstack1l111lll11l_opy_:
                return bstack1l111lll11l_opy_
    def bstack1llllll1lll_opy_(
        self, method_name, previous_state: bstack1llll1ll11l_opy_, *args, **kwargs
    ) -> bstack1llll1ll11l_opy_:
        if method_name == bstack1111l1_opy_ (u"࠭࡬ࡢࡷࡱࡧ࡭࠭ᑉ") or method_name == bstack1111l1_opy_ (u"ࠧࡤࡱࡱࡲࡪࡩࡴࠨᑊ") or method_name == bstack1111l1_opy_ (u"ࠨࡰࡨࡻࡤࡶࡡࡨࡧࠪᑋ"):
            return bstack1llll1ll11l_opy_.bstack1llllll1l11_opy_
        if method_name == bstack1111l1_opy_ (u"ࠩࡧ࡭ࡸࡶࡡࡵࡥ࡫ࠫᑌ"):
            return bstack1llll1ll11l_opy_.bstack1lllll1llll_opy_
        if method_name == bstack1111l1_opy_ (u"ࠪࡧࡱࡵࡳࡦࠩᑍ"):
            return bstack1llll1ll11l_opy_.QUIT
        return bstack1llll1ll11l_opy_.NONE
    @staticmethod
    def bstack1l111lll111_opy_(bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_]):
        return bstack1111l1_opy_ (u"ࠦ࠿ࠨᑎ").join((bstack1llll1ll11l_opy_(bstack1llll1ll1l1_opy_[0]).name, bstack1lllll11111_opy_(bstack1llll1ll1l1_opy_[1]).name))
    @staticmethod
    def bstack1ll111111ll_opy_(bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_], callback: Callable):
        bstack1l111lll1l1_opy_ = bstack1ll1ll1111l_opy_.bstack1l111lll111_opy_(bstack1llll1ll1l1_opy_)
        if not bstack1l111lll1l1_opy_ in bstack1ll1ll1111l_opy_.bstack1l111llllll_opy_:
            bstack1ll1ll1111l_opy_.bstack1l111llllll_opy_[bstack1l111lll1l1_opy_] = []
        bstack1ll1ll1111l_opy_.bstack1l111llllll_opy_[bstack1l111lll1l1_opy_].append(callback)
    @staticmethod
    def bstack1ll11l1l111_opy_(method_name: str):
        return True
    @staticmethod
    def bstack1ll11l1ll11_opy_(method_name: str, *args) -> bool:
        return True
    @staticmethod
    def bstack1ll11l1ll1l_opy_(instance: bstack1llll1l11l1_opy_, default_value=None):
        return bstack1lllll11l11_opy_.bstack1lllll111l1_opy_(instance, bstack1ll1ll1111l_opy_.bstack1l1l111l1l1_opy_, default_value)
    @staticmethod
    def bstack1l1lll1ll11_opy_(instance: bstack1llll1l11l1_opy_) -> bool:
        return True
    @staticmethod
    def bstack1ll11lll1l1_opy_(instance: bstack1llll1l11l1_opy_, default_value=None):
        return bstack1lllll11l11_opy_.bstack1lllll111l1_opy_(instance, bstack1ll1ll1111l_opy_.bstack1l1l1111l1l_opy_, default_value)
    @staticmethod
    def bstack1ll11l1111l_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1l1lllllll1_opy_(method_name: str, *args):
        if not bstack1ll1ll1111l_opy_.bstack1ll11l1l111_opy_(method_name):
            return False
        if not bstack1ll1ll1111l_opy_.bstack1l11l111111_opy_ in bstack1ll1ll1111l_opy_.bstack1l11l1l1l1l_opy_(*args):
            return False
        bstack1l1llllll11_opy_ = bstack1ll1ll1111l_opy_.bstack1l1llll1ll1_opy_(*args)
        return bstack1l1llllll11_opy_ and bstack1111l1_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧᑏ") in bstack1l1llllll11_opy_ and bstack1111l1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸࠢᑐ") in bstack1l1llllll11_opy_[bstack1111l1_opy_ (u"ࠢࡴࡥࡵ࡭ࡵࡺࠢᑑ")]
    @staticmethod
    def bstack1ll111ll111_opy_(method_name: str, *args):
        if not bstack1ll1ll1111l_opy_.bstack1ll11l1l111_opy_(method_name):
            return False
        if not bstack1ll1ll1111l_opy_.bstack1l11l111111_opy_ in bstack1ll1ll1111l_opy_.bstack1l11l1l1l1l_opy_(*args):
            return False
        bstack1l1llllll11_opy_ = bstack1ll1ll1111l_opy_.bstack1l1llll1ll1_opy_(*args)
        return (
            bstack1l1llllll11_opy_
            and bstack1111l1_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࠣᑒ") in bstack1l1llllll11_opy_
            and bstack1111l1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡣࡳ࡫ࡳࡸࠧᑓ") in bstack1l1llllll11_opy_[bstack1111l1_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࠥᑔ")]
        )
    @staticmethod
    def bstack1l11l1l1l1l_opy_(*args):
        return str(bstack1ll1ll1111l_opy_.bstack1ll11l1111l_opy_(*args)).lower()