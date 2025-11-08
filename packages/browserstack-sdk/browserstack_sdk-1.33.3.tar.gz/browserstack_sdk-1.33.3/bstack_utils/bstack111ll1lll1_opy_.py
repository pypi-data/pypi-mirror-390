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
from bstack_utils.helper import bstack11ll11ll1l_opy_
from bstack_utils.constants import bstack11l1l1ll111_opy_, EVENTS, STAGE
from bstack_utils.bstack1lll1l11l_opy_ import get_logger
logger = get_logger(__name__)
class bstack1ll1111ll1_opy_:
    bstack1lllll1llll1_opy_ = None
    @classmethod
    def bstack11111111_opy_(cls):
        if cls.on() and os.getenv(bstack1111l1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠣ≍")):
            logger.info(
                bstack1111l1_opy_ (u"࡛ࠫ࡯ࡳࡪࡶࠣ࡬ࡹࡺࡰࡴ࠼࠲࠳ࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡧࡻࡩ࡭ࡦࡶ࠳ࢀࢃࠠࡵࡱࠣࡺ࡮࡫ࡷࠡࡤࡸ࡭ࡱࡪࠠࡳࡧࡳࡳࡷࡺࠬࠡ࡫ࡱࡷ࡮࡭ࡨࡵࡵ࠯ࠤࡦࡴࡤࠡ࡯ࡤࡲࡾࠦ࡭ࡰࡴࡨࠤࡩ࡫ࡢࡶࡩࡪ࡭ࡳ࡭ࠠࡪࡰࡩࡳࡷࡳࡡࡵ࡫ࡲࡲࠥࡧ࡬࡭ࠢࡤࡸࠥࡵ࡮ࡦࠢࡳࡰࡦࡩࡥࠢ࡞ࡱࠫ≎").format(os.getenv(bstack1111l1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤ࡛ࡕࡊࡆࠥ≏"))))
    @classmethod
    def on(cls):
        if os.environ.get(bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ≐"), None) is None or os.environ[bstack1111l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ≑")] == bstack1111l1_opy_ (u"ࠣࡰࡸࡰࡱࠨ≒"):
            return False
        return True
    @classmethod
    def bstack1llll11111ll_opy_(cls, bs_config, framework=bstack1111l1_opy_ (u"ࠤࠥ≓")):
        bstack11l1lll1ll1_opy_ = False
        for fw in bstack11l1l1ll111_opy_:
            if fw in framework:
                bstack11l1lll1ll1_opy_ = True
        return bstack11ll11ll1l_opy_(bs_config.get(bstack1111l1_opy_ (u"ࠪࡸࡪࡹࡴࡐࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧ≔"), bstack11l1lll1ll1_opy_))
    @classmethod
    def bstack1lll1lll1ll1_opy_(cls, framework):
        return framework in bstack11l1l1ll111_opy_
    @classmethod
    def bstack1llll11ll11l_opy_(cls, bs_config, framework):
        return cls.bstack1llll11111ll_opy_(bs_config, framework) is True and cls.bstack1lll1lll1ll1_opy_(framework)
    @staticmethod
    def current_hook_uuid():
        return getattr(threading.current_thread(), bstack1111l1_opy_ (u"ࠫࡨࡻࡲࡳࡧࡱࡸࡤ࡮࡯ࡰ࡭ࡢࡹࡺ࡯ࡤࠨ≕"), None)
    @staticmethod
    def bstack111ll1l1l1_opy_():
        if getattr(threading.current_thread(), bstack1111l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠩ≖"), None):
            return {
                bstack1111l1_opy_ (u"࠭ࡴࡺࡲࡨࠫ≗"): bstack1111l1_opy_ (u"ࠧࡵࡧࡶࡸࠬ≘"),
                bstack1111l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ≙"): getattr(threading.current_thread(), bstack1111l1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢࡸࡪࡹࡴࡠࡷࡸ࡭ࡩ࠭≚"), None)
            }
        if getattr(threading.current_thread(), bstack1111l1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣ࡭ࡵ࡯࡬ࡡࡸࡹ࡮ࡪࠧ≛"), None):
            return {
                bstack1111l1_opy_ (u"ࠫࡹࡿࡰࡦࠩ≜"): bstack1111l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪ≝"),
                bstack1111l1_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭≞"): getattr(threading.current_thread(), bstack1111l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡪࡲࡳࡰࡥࡵࡶ࡫ࡧࠫ≟"), None)
            }
        return None
    @staticmethod
    def bstack1lll1lll1l1l_opy_(func):
        def wrap(*args, **kwargs):
            if bstack1ll1111ll1_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def bstack1111ll11ll_opy_(test, hook_name=None):
        bstack1lll1lll1l11_opy_ = test.parent
        if hook_name in [bstack1111l1_opy_ (u"ࠨࡵࡨࡸࡺࡶ࡟ࡤ࡮ࡤࡷࡸ࠭≠"), bstack1111l1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡨࡲࡡࡴࡵࠪ≡"), bstack1111l1_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡰࡳࡩࡻ࡬ࡦࠩ≢"), bstack1111l1_opy_ (u"ࠫࡹ࡫ࡡࡳࡦࡲࡻࡳࡥ࡭ࡰࡦࡸࡰࡪ࠭≣")]:
            bstack1lll1lll1l11_opy_ = test
        scope = []
        while bstack1lll1lll1l11_opy_ is not None:
            scope.append(bstack1lll1lll1l11_opy_.name)
            bstack1lll1lll1l11_opy_ = bstack1lll1lll1l11_opy_.parent
        scope.reverse()
        return scope[2:]
    @staticmethod
    def bstack1lll1lll11ll_opy_(hook_type):
        if hook_type == bstack1111l1_opy_ (u"ࠧࡈࡅࡇࡑࡕࡉࡤࡋࡁࡄࡊࠥ≤"):
            return bstack1111l1_opy_ (u"ࠨࡓࡦࡶࡸࡴࠥ࡮࡯ࡰ࡭ࠥ≥")
        elif hook_type == bstack1111l1_opy_ (u"ࠢࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠦ≦"):
            return bstack1111l1_opy_ (u"ࠣࡖࡨࡥࡷࡪ࡯ࡸࡰࠣ࡬ࡴࡵ࡫ࠣ≧")
    @staticmethod
    def bstack1lll1lll1lll_opy_(bstack1111111l_opy_):
        try:
            if not bstack1ll1111ll1_opy_.on():
                return bstack1111111l_opy_
            if os.environ.get(bstack1111l1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡔࡈࡖ࡚ࡔࠢ≨"), None) == bstack1111l1_opy_ (u"ࠥࡸࡷࡻࡥࠣ≩"):
                tests = os.environ.get(bstack1111l1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡖࡊࡘࡕࡏࡡࡗࡉࡘ࡚ࡓࠣ≪"), None)
                if tests is None or tests == bstack1111l1_opy_ (u"ࠧࡴࡵ࡭࡮ࠥ≫"):
                    return bstack1111111l_opy_
                bstack1111111l_opy_ = tests.split(bstack1111l1_opy_ (u"࠭ࠬࠨ≬"))
                return bstack1111111l_opy_
        except Exception as exc:
            logger.debug(bstack1111l1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡲࡦࡴࡸࡲࠥ࡮ࡡ࡯ࡦ࡯ࡩࡷࡀࠠࠣ≭") + str(str(exc)) + bstack1111l1_opy_ (u"ࠣࠤ≮"))
        return bstack1111111l_opy_