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
from bstack_utils.bstack1llll1llll_opy_ import bstack1llll11l111_opy_
from bstack_utils.constants import EVENTS
class bstack1lll111l1l1_opy_(bstack1lllll11l11_opy_):
    bstack1l111lllll1_opy_ = bstack1111l1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡍࡓࡊࡅ࡙ࠤᖣ")
    NAME = bstack1111l1_opy_ (u"ࠥࡷࡪࡲࡥ࡯࡫ࡸࡱࠧᖤ")
    bstack1l1l1111l1l_opy_ = bstack1111l1_opy_ (u"ࠦ࡭ࡻࡢࡠࡷࡵࡰࠧᖥ")
    bstack1l1l1111lll_opy_ = bstack1111l1_opy_ (u"ࠧ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡨࡷࡸ࡯࡯࡯ࡡ࡬ࡨࠧᖦ")
    bstack11lll1ll111_opy_ = bstack1111l1_opy_ (u"ࠨࡩ࡯ࡲࡸࡸࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᖧ")
    bstack1l1l111l1l1_opy_ = bstack1111l1_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᖨ")
    bstack1l11l111l11_opy_ = bstack1111l1_opy_ (u"ࠣ࡫ࡶࡣࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢ࡬ࡺࡨࠢᖩ")
    bstack11lll1l1lll_opy_ = bstack1111l1_opy_ (u"ࠤࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹࠨᖪ")
    bstack11lll1llll1_opy_ = bstack1111l1_opy_ (u"ࠥࡩࡳࡪࡥࡥࡡࡤࡸࠧᖫ")
    bstack1ll11l11ll1_opy_ = bstack1111l1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡥࡩ࡯ࡦࡨࡼࠧᖬ")
    bstack1l11l11llll_opy_ = bstack1111l1_opy_ (u"ࠧࡴࡥࡸࡵࡨࡷࡸ࡯࡯࡯ࠤᖭ")
    bstack11lll1l1ll1_opy_ = bstack1111l1_opy_ (u"ࠨࡧࡦࡶࠥᖮ")
    bstack1l1ll111ll1_opy_ = bstack1111l1_opy_ (u"ࠢࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠦᖯ")
    bstack1l11l111111_opy_ = bstack1111l1_opy_ (u"ࠣࡹ࠶ࡧࡪࡾࡥࡤࡷࡷࡩࡸࡩࡲࡪࡲࡷࠦᖰ")
    bstack1l111llll11_opy_ = bstack1111l1_opy_ (u"ࠤࡺ࠷ࡨ࡫ࡸࡦࡥࡸࡸࡪࡹࡣࡳ࡫ࡳࡸࡦࡹࡹ࡯ࡥࠥᖱ")
    bstack11lll1ll11l_opy_ = bstack1111l1_opy_ (u"ࠥࡵࡺ࡯ࡴࠣᖲ")
    bstack11lll1lll1l_opy_: Dict[str, List[Callable]] = dict()
    bstack1l11l1l1111_opy_: str
    platform_index: int
    options: Any
    desired_capabilities: Any
    bstack1lll1111111_opy_: Any
    bstack1l111lll1ll_opy_: Dict
    def __init__(
        self,
        bstack1l11l1l1111_opy_: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        classes: List[Type],
        bstack1lll1111111_opy_: Dict[str, Any],
        methods=[bstack1111l1_opy_ (u"ࠦࡤࡥࡩ࡯࡫ࡷࡣࡤࠨᖳ"), bstack1111l1_opy_ (u"ࠧࡹࡴࡢࡴࡷࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠧᖴ"), bstack1111l1_opy_ (u"ࠨࡥࡹࡧࡦࡹࡹ࡫ࠢᖵ"), bstack1111l1_opy_ (u"ࠢࡲࡷ࡬ࡸࠧᖶ")],
    ):
        super().__init__(
            framework_name,
            framework_version,
            classes,
        )
        self.bstack1l11l1l1111_opy_ = bstack1l11l1l1111_opy_
        self.platform_index = platform_index
        self.bstack1llll11ll11_opy_(methods)
        self.bstack1lll1111111_opy_ = bstack1lll1111111_opy_
    @staticmethod
    def session_id(target: object, strict=True):
        return bstack1lllll11l11_opy_.get_data(bstack1lll111l1l1_opy_.bstack1l1l1111lll_opy_, target, strict)
    @staticmethod
    def hub_url(target: object, strict=True):
        return bstack1lllll11l11_opy_.get_data(bstack1lll111l1l1_opy_.bstack1l1l1111l1l_opy_, target, strict)
    @staticmethod
    def bstack11lll1lllll_opy_(target: object, strict=True):
        return bstack1lllll11l11_opy_.get_data(bstack1lll111l1l1_opy_.bstack11lll1ll111_opy_, target, strict)
    @staticmethod
    def capabilities(target: object, strict=True):
        return bstack1lllll11l11_opy_.get_data(bstack1lll111l1l1_opy_.bstack1l1l111l1l1_opy_, target, strict)
    @staticmethod
    def bstack1l1lll1ll11_opy_(instance: bstack1llll1l11l1_opy_) -> bool:
        return bstack1lllll11l11_opy_.bstack1lllll111l1_opy_(instance, bstack1lll111l1l1_opy_.bstack1l11l111l11_opy_, False)
    @staticmethod
    def bstack1ll11lll1l1_opy_(instance: bstack1llll1l11l1_opy_, default_value=None):
        return bstack1lllll11l11_opy_.bstack1lllll111l1_opy_(instance, bstack1lll111l1l1_opy_.bstack1l1l1111l1l_opy_, default_value)
    @staticmethod
    def bstack1ll11l1ll1l_opy_(instance: bstack1llll1l11l1_opy_, default_value=None):
        return bstack1lllll11l11_opy_.bstack1lllll111l1_opy_(instance, bstack1lll111l1l1_opy_.bstack1l1l111l1l1_opy_, default_value)
    @staticmethod
    def bstack1l1llll1l1l_opy_(hub_url: str, bstack11lll1lll11_opy_=bstack1111l1_opy_ (u"ࠣ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱࠧᖷ")):
        try:
            bstack11lll1ll1ll_opy_ = str(urlparse(hub_url).netloc) if hub_url else None
            return bstack11lll1ll1ll_opy_.endswith(bstack11lll1lll11_opy_)
        except:
            pass
        return False
    @staticmethod
    def bstack1ll11l1l111_opy_(method_name: str):
        return method_name == bstack1111l1_opy_ (u"ࠤࡨࡼࡪࡩࡵࡵࡧࠥᖸ")
    @staticmethod
    def bstack1ll11l1ll11_opy_(method_name: str, *args):
        return (
            bstack1lll111l1l1_opy_.bstack1ll11l1l111_opy_(method_name)
            and bstack1lll111l1l1_opy_.bstack1l11l1l1l1l_opy_(*args) == bstack1lll111l1l1_opy_.bstack1l11l11llll_opy_
        )
    @staticmethod
    def bstack1l1lllllll1_opy_(method_name: str, *args):
        if not bstack1lll111l1l1_opy_.bstack1ll11l1l111_opy_(method_name):
            return False
        if not bstack1lll111l1l1_opy_.bstack1l11l111111_opy_ in bstack1lll111l1l1_opy_.bstack1l11l1l1l1l_opy_(*args):
            return False
        bstack1l1llllll11_opy_ = bstack1lll111l1l1_opy_.bstack1l1llll1ll1_opy_(*args)
        return bstack1l1llllll11_opy_ and bstack1111l1_opy_ (u"ࠥࡷࡨࡸࡩࡱࡶࠥᖹ") in bstack1l1llllll11_opy_ and bstack1111l1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᖺ") in bstack1l1llllll11_opy_[bstack1111l1_opy_ (u"ࠧࡹࡣࡳ࡫ࡳࡸࠧᖻ")]
    @staticmethod
    def bstack1ll111ll111_opy_(method_name: str, *args):
        if not bstack1lll111l1l1_opy_.bstack1ll11l1l111_opy_(method_name):
            return False
        if not bstack1lll111l1l1_opy_.bstack1l11l111111_opy_ in bstack1lll111l1l1_opy_.bstack1l11l1l1l1l_opy_(*args):
            return False
        bstack1l1llllll11_opy_ = bstack1lll111l1l1_opy_.bstack1l1llll1ll1_opy_(*args)
        return (
            bstack1l1llllll11_opy_
            and bstack1111l1_opy_ (u"ࠨࡳࡤࡴ࡬ࡴࡹࠨᖼ") in bstack1l1llllll11_opy_
            and bstack1111l1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࡥࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡷࡨࡸࡩࡱࡶࠥᖽ") in bstack1l1llllll11_opy_[bstack1111l1_opy_ (u"ࠣࡵࡦࡶ࡮ࡶࡴࠣᖾ")]
        )
    @staticmethod
    def bstack1l11l1l1l1l_opy_(*args):
        return str(bstack1lll111l1l1_opy_.bstack1ll11l1111l_opy_(*args)).lower()
    @staticmethod
    def bstack1ll11l1111l_opy_(*args):
        return args[0] if args and type(args) in [list, tuple] and isinstance(args[0], str) else None
    @staticmethod
    def bstack1l1llll1ll1_opy_(*args):
        return args[1] if len(args) > 1 and isinstance(args[1], dict) else None
    @staticmethod
    def bstack11l1ll11l_opy_(driver):
        command_executor = getattr(driver, bstack1111l1_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧᖿ"), None)
        if not command_executor:
            return None
        hub_url = str(command_executor) if isinstance(command_executor, (str, bytes)) else None
        hub_url = str(command_executor._url) if not hub_url and getattr(command_executor, bstack1111l1_opy_ (u"ࠥࡣࡺࡸ࡬ࠣᗀ"), None) else None
        if not hub_url:
            client_config = getattr(command_executor, bstack1111l1_opy_ (u"ࠦࡤࡩ࡬ࡪࡧࡱࡸࡤࡩ࡯࡯ࡨ࡬࡫ࠧᗁ"), None)
            if not client_config:
                return None
            hub_url = getattr(client_config, bstack1111l1_opy_ (u"ࠧࡸࡥ࡮ࡱࡷࡩࡤࡹࡥࡳࡸࡨࡶࡤࡧࡤࡥࡴࠥᗂ"), None)
        return hub_url
    def bstack1l11ll1l1l1_opy_(self, instance, driver, hub_url: str):
        result = False
        if not hub_url:
            return result
        command_executor = getattr(driver, bstack1111l1_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤᗃ"), None)
        if command_executor:
            if isinstance(command_executor, (str, bytes)):
                setattr(driver, bstack1111l1_opy_ (u"ࠢࡤࡱࡰࡱࡦࡴࡤࡠࡧࡻࡩࡨࡻࡴࡰࡴࠥᗄ"), hub_url)
                result = True
            elif hasattr(command_executor, bstack1111l1_opy_ (u"ࠣࡡࡸࡶࡱࠨᗅ")):
                setattr(command_executor, bstack1111l1_opy_ (u"ࠤࡢࡹࡷࡲࠢᗆ"), hub_url)
                result = True
        if result:
            self.bstack1l11l1l1111_opy_ = hub_url
            bstack1lll111l1l1_opy_.bstack1lllll1l1l1_opy_(instance, bstack1lll111l1l1_opy_.bstack1l1l1111l1l_opy_, hub_url)
            bstack1lll111l1l1_opy_.bstack1lllll1l1l1_opy_(
                instance, bstack1lll111l1l1_opy_.bstack1l11l111l11_opy_, bstack1lll111l1l1_opy_.bstack1l1llll1l1l_opy_(hub_url)
            )
        return result
    @staticmethod
    def bstack1l111lll111_opy_(bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_]):
        return bstack1111l1_opy_ (u"ࠥ࠾ࠧᗇ").join((bstack1llll1ll11l_opy_(bstack1llll1ll1l1_opy_[0]).name, bstack1lllll11111_opy_(bstack1llll1ll1l1_opy_[1]).name))
    @staticmethod
    def bstack1ll111111ll_opy_(bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_], callback: Callable):
        bstack1l111lll1l1_opy_ = bstack1lll111l1l1_opy_.bstack1l111lll111_opy_(bstack1llll1ll1l1_opy_)
        if not bstack1l111lll1l1_opy_ in bstack1lll111l1l1_opy_.bstack11lll1lll1l_opy_:
            bstack1lll111l1l1_opy_.bstack11lll1lll1l_opy_[bstack1l111lll1l1_opy_] = []
        bstack1lll111l1l1_opy_.bstack11lll1lll1l_opy_[bstack1l111lll1l1_opy_].append(callback)
    def bstack1lllll11lll_opy_(self, instance: bstack1llll1l11l1_opy_, method_name: str, bstack1llll1ll1ll_opy_: timedelta, *args, **kwargs):
        if not instance or method_name in (bstack1111l1_opy_ (u"ࠦࡸࡺࡡࡳࡶࡢࡷࡪࡹࡳࡪࡱࡱࠦᗈ")):
            return
        cmd = args[0] if method_name == bstack1111l1_opy_ (u"ࠧ࡫ࡸࡦࡥࡸࡸࡪࠨᗉ") and args and type(args) in [list, tuple] and isinstance(args[0], str) else None
        bstack11lll1ll1l1_opy_ = bstack1111l1_opy_ (u"ࠨ࠺ࠣᗊ").join(map(str, filter(None, [method_name, cmd])))
        instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠢࡥࡴ࡬ࡺࡪࡸ࠺ࠣᗋ") + bstack11lll1ll1l1_opy_, bstack1llll1ll1ll_opy_)
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
        bstack1l111lll1l1_opy_ = bstack1lll111l1l1_opy_.bstack1l111lll111_opy_(bstack1llll1ll1l1_opy_)
        self.logger.debug(bstack1111l1_opy_ (u"ࠣࡱࡱࡣ࡭ࡵ࡯࡬࠼ࠣࡱࡪࡺࡨࡰࡦࡢࡲࡦࡳࡥ࠾ࡽࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫ࡽࠡࡪࡲࡳࡰࡥࡩ࡯ࡨࡲࡁࢀ࡮࡯ࡰ࡭ࡢ࡭ࡳ࡬࡯ࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠ࡬ࡹࡤࡶ࡬ࡹ࠽ࠣᗌ") + str(kwargs) + bstack1111l1_opy_ (u"ࠤࠥᗍ"))
        if bstack1llll11lll1_opy_ == bstack1llll1ll11l_opy_.QUIT:
            if bstack1l111llll1l_opy_ == bstack1lllll11111_opy_.PRE:
                bstack1ll11l111ll_opy_ = bstack1llll11l111_opy_.bstack1ll11ll11l1_opy_(EVENTS.bstack1l1l11ll11_opy_.value)
                bstack1lllll11l11_opy_.bstack1lllll1l1l1_opy_(instance, EVENTS.bstack1l1l11ll11_opy_.value, bstack1ll11l111ll_opy_)
                self.logger.debug(bstack1111l1_opy_ (u"ࠥ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡽࠡ࡯ࡨࡸ࡭ࡵࡤࡠࡰࡤࡱࡪࡃࡻࡾࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࢃࠠࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࢃࠢᗎ").format(instance, method_name, bstack1llll11lll1_opy_, bstack1l111llll1l_opy_))
        if bstack1llll11lll1_opy_ == bstack1llll1ll11l_opy_.bstack1llllll1l11_opy_:
            if bstack1l111llll1l_opy_ == bstack1lllll11111_opy_.POST and not bstack1lll111l1l1_opy_.bstack1l1l1111lll_opy_ in instance.data:
                session_id = getattr(target, bstack1111l1_opy_ (u"ࠦࡸ࡫ࡳࡴ࡫ࡲࡲࡤ࡯ࡤࠣᗏ"), None)
                if session_id:
                    instance.data[bstack1lll111l1l1_opy_.bstack1l1l1111lll_opy_] = session_id
        elif (
            bstack1llll11lll1_opy_ == bstack1llll1ll11l_opy_.bstack1lllll111ll_opy_
            and bstack1lll111l1l1_opy_.bstack1l11l1l1l1l_opy_(*args) == bstack1lll111l1l1_opy_.bstack1l11l11llll_opy_
        ):
            if bstack1l111llll1l_opy_ == bstack1lllll11111_opy_.PRE:
                hub_url = bstack1lll111l1l1_opy_.bstack11l1ll11l_opy_(target)
                if hub_url:
                    instance.data.update(
                        {
                            bstack1lll111l1l1_opy_.bstack1l1l1111l1l_opy_: hub_url,
                            bstack1lll111l1l1_opy_.bstack1l11l111l11_opy_: bstack1lll111l1l1_opy_.bstack1l1llll1l1l_opy_(hub_url),
                            bstack1lll111l1l1_opy_.bstack1ll11l11ll1_opy_: int(
                                os.environ.get(bstack1111l1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠧᗐ"), str(self.platform_index))
                            ),
                        }
                    )
                bstack1l1llllll11_opy_ = bstack1lll111l1l1_opy_.bstack1l1llll1ll1_opy_(*args)
                bstack11lll1lllll_opy_ = bstack1l1llllll11_opy_.get(bstack1111l1_opy_ (u"ࠨࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᗑ"), None) if bstack1l1llllll11_opy_ else None
                if isinstance(bstack11lll1lllll_opy_, dict):
                    instance.data[bstack1lll111l1l1_opy_.bstack11lll1ll111_opy_] = copy.deepcopy(bstack11lll1lllll_opy_)
                    instance.data[bstack1lll111l1l1_opy_.bstack1l1l111l1l1_opy_] = bstack11lll1lllll_opy_
            elif bstack1l111llll1l_opy_ == bstack1lllll11111_opy_.POST:
                if isinstance(result, dict):
                    framework_session_id = result.get(bstack1111l1_opy_ (u"ࠢࡷࡣ࡯ࡹࡪࠨᗒ"), dict()).get(bstack1111l1_opy_ (u"ࠣࡵࡨࡷࡸ࡯࡯࡯ࡋࡧࠦᗓ"), None)
                    if framework_session_id:
                        instance.data.update(
                            {
                                bstack1lll111l1l1_opy_.bstack1l1l1111lll_opy_: framework_session_id,
                                bstack1lll111l1l1_opy_.bstack11lll1l1lll_opy_: datetime.now(tz=timezone.utc),
                            }
                        )
        elif (
            bstack1llll11lll1_opy_ == bstack1llll1ll11l_opy_.bstack1lllll111ll_opy_
            and bstack1lll111l1l1_opy_.bstack1l11l1l1l1l_opy_(*args) == bstack1lll111l1l1_opy_.bstack11lll1ll11l_opy_
            and bstack1l111llll1l_opy_ == bstack1lllll11111_opy_.POST
        ):
            instance.data[bstack1lll111l1l1_opy_.bstack11lll1llll1_opy_] = datetime.now(tz=timezone.utc)
        if bstack1l111lll1l1_opy_ in bstack1lll111l1l1_opy_.bstack11lll1lll1l_opy_:
            bstack1l111lll11l_opy_ = None
            for callback in bstack1lll111l1l1_opy_.bstack11lll1lll1l_opy_[bstack1l111lll1l1_opy_]:
                try:
                    bstack1l11l11111l_opy_ = callback(self, target, exec, bstack1llll1ll1l1_opy_, result, *args, **kwargs)
                    if bstack1l111lll11l_opy_ == None:
                        bstack1l111lll11l_opy_ = bstack1l11l11111l_opy_
                except Exception as e:
                    self.logger.error(bstack1111l1_opy_ (u"ࠤࡨࡶࡷࡵࡲࠡ࡫ࡱࡺࡴࡱࡩ࡯ࡩࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯࠿ࠦࠢᗔ") + str(e) + bstack1111l1_opy_ (u"ࠥࠦᗕ"))
                    traceback.print_exc()
            if bstack1llll11lll1_opy_ == bstack1llll1ll11l_opy_.QUIT:
                if bstack1l111llll1l_opy_ == bstack1lllll11111_opy_.POST:
                    bstack1ll11l111ll_opy_ = bstack1lllll11l11_opy_.bstack1lllll111l1_opy_(instance, EVENTS.bstack1l1l11ll11_opy_.value)
                    if bstack1ll11l111ll_opy_!=None:
                        bstack1llll11l111_opy_.end(EVENTS.bstack1l1l11ll11_opy_.value, bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᗖ"), bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᗗ"), True, None)
            if bstack1l111llll1l_opy_ == bstack1lllll11111_opy_.PRE and callable(bstack1l111lll11l_opy_):
                return bstack1l111lll11l_opy_
            elif bstack1l111llll1l_opy_ == bstack1lllll11111_opy_.POST and bstack1l111lll11l_opy_:
                return bstack1l111lll11l_opy_
    def bstack1llllll1lll_opy_(
        self, method_name, previous_state: bstack1llll1ll11l_opy_, *args, **kwargs
    ) -> bstack1llll1ll11l_opy_:
        if method_name == bstack1111l1_opy_ (u"ࠨ࡟ࡠ࡫ࡱ࡭ࡹࡥ࡟ࠣᗘ") or method_name == bstack1111l1_opy_ (u"ࠢࡴࡶࡤࡶࡹࡥࡳࡦࡵࡶ࡭ࡴࡴࠢᗙ"):
            return bstack1llll1ll11l_opy_.bstack1llllll1l11_opy_
        if method_name == bstack1111l1_opy_ (u"ࠣࡳࡸ࡭ࡹࠨᗚ"):
            return bstack1llll1ll11l_opy_.QUIT
        if method_name == bstack1111l1_opy_ (u"ࠤࡨࡼࡪࡩࡵࡵࡧࠥᗛ"):
            if previous_state != bstack1llll1ll11l_opy_.NONE:
                command_name = bstack1lll111l1l1_opy_.bstack1l11l1l1l1l_opy_(*args)
                if command_name == bstack1lll111l1l1_opy_.bstack1l11l11llll_opy_:
                    return bstack1llll1ll11l_opy_.bstack1llllll1l11_opy_
            return bstack1llll1ll11l_opy_.bstack1lllll111ll_opy_
        return bstack1llll1ll11l_opy_.NONE