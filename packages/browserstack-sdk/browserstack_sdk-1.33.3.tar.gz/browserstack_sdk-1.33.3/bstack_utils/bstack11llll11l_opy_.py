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
import tempfile
import math
from bstack_utils import bstack1lll1l11l_opy_
from bstack_utils.constants import bstack1l1l11l1ll_opy_, bstack11l1ll11l1l_opy_
from bstack_utils.helper import bstack11l11l1lll1_opy_, get_host_info
from bstack_utils.bstack11ll1111l11_opy_ import bstack11l1lllll1l_opy_
import json
import re
import sys
bstack1111l1llll1_opy_ = bstack1111l1_opy_ (u"ࠨࡲࡦࡶࡵࡽ࡙࡫ࡳࡵࡵࡒࡲࡋࡧࡩ࡭ࡷࡵࡩࠧẊ")
bstack1111ll11lll_opy_ = bstack1111l1_opy_ (u"ࠢࡢࡤࡲࡶࡹࡈࡵࡪ࡮ࡧࡓࡳࡌࡡࡪ࡮ࡸࡶࡪࠨẋ")
bstack1111l1l1ll1_opy_ = bstack1111l1_opy_ (u"ࠣࡴࡸࡲࡕࡸࡥࡷ࡫ࡲࡹࡸࡲࡹࡇࡣ࡬ࡰࡪࡪࡆࡪࡴࡶࡸࠧẌ")
bstack111l1111111_opy_ = bstack1111l1_opy_ (u"ࠤࡵࡩࡷࡻ࡮ࡑࡴࡨࡺ࡮ࡵࡵࡴ࡮ࡼࡊࡦ࡯࡬ࡦࡦࠥẍ")
bstack111l1111ll1_opy_ = bstack1111l1_opy_ (u"ࠥࡷࡰ࡯ࡰࡇ࡮ࡤ࡯ࡾࡧ࡮ࡥࡈࡤ࡭ࡱ࡫ࡤࠣẎ")
bstack1111l11lll1_opy_ = bstack1111l1_opy_ (u"ࠦࡷࡻ࡮ࡔ࡯ࡤࡶࡹ࡙ࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠣẏ")
bstack1111l1l1lll_opy_ = {
    bstack1111l1llll1_opy_,
    bstack1111ll11lll_opy_,
    bstack1111l1l1ll1_opy_,
    bstack111l1111111_opy_,
    bstack111l1111ll1_opy_,
    bstack1111l11lll1_opy_
}
bstack1111l1l1l1l_opy_ = {bstack1111l1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬẐ")}
logger = bstack1lll1l11l_opy_.get_logger(__name__, bstack1l1l11l1ll_opy_)
class bstack111l1111l1l_opy_:
    def __init__(self):
        self.enabled = False
        self.name = None
    def enable(self, name):
        self.enabled = True
        self.name = name
    def disable(self):
        self.enabled = False
        self.name = None
    def bstack1111lll1lll_opy_(self):
        return self.enabled
    def get_name(self):
        return self.name
class bstack11l111llll_opy_:
    _1lll1llllll_opy_ = None
    def __init__(self, config):
        self.bstack1111llll1l1_opy_ = False
        self.bstack1111llll111_opy_ = False
        self.bstack1111lll11ll_opy_ = False
        self.bstack1111lllll11_opy_ = False
        self.bstack111l11111l1_opy_ = None
        self.bstack1111l1lll11_opy_ = bstack111l1111l1l_opy_()
        self.bstack1111l1ll1ll_opy_ = None
        opts = config.get(bstack1111l1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪẑ"), {})
        self.bstack1111ll1ll11_opy_ = config.get(bstack1111l1_opy_ (u"ࠧࡴ࡯ࡤࡶࡹ࡙ࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࡇࡧࡤࡸࡺࡸࡥࡃࡴࡤࡲࡨ࡮ࡥࡴࡇࡑ࡚ࠬẒ"), bstack1111l1_opy_ (u"ࠣࠤẓ"))
        self.bstack1111lll1l11_opy_ = config.get(bstack1111l1_opy_ (u"ࠩࡶࡱࡦࡸࡴࡔࡧ࡯ࡩࡨࡺࡩࡰࡰࡉࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࡧࡶࡇࡑࡏࠧẔ"), bstack1111l1_opy_ (u"ࠥࠦẕ"))
        bstack1111ll1l11l_opy_ = opts.get(bstack1111l11lll1_opy_, {})
        bstack1111ll11l11_opy_ = None
        if bstack1111l1_opy_ (u"ࠫࡸࡵࡵࡳࡥࡨࠫẖ") in bstack1111ll1l11l_opy_:
            bstack1111l1ll111_opy_ = bstack1111ll1l11l_opy_[bstack1111l1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬẗ")]
            if bstack1111l1ll111_opy_ is None or bstack1111l1ll111_opy_ == bstack1111l1_opy_ (u"࠭ࠧẘ") or (isinstance(bstack1111l1ll111_opy_, list) and len(bstack1111l1ll111_opy_) == 0):
                bstack1111ll11l11_opy_ = []
            elif isinstance(bstack1111l1ll111_opy_, list):
                bstack1111ll11l11_opy_ = bstack1111l1ll111_opy_
            elif isinstance(bstack1111l1ll111_opy_, str) and bstack1111l1ll111_opy_.strip():
                bstack1111ll11l11_opy_ = bstack1111l1ll111_opy_
            else:
                logger.warning(bstack1111l1_opy_ (u"ࠢࡊࡰࡹࡥࡱ࡯ࡤࠡࡵࡲࡹࡷࡩࡥࠡࡸࡤࡰࡺ࡫ࠠࡪࡰࠣࡧࡴࡴࡦࡪࡩ࠽ࠤࢀࢃ࠮ࠡࡆࡨࡪࡦࡻ࡬ࡵ࡫ࡱ࡫ࠥࡺ࡯ࠡࡧࡰࡴࡹࡿࠠ࡭࡫ࡶࡸ࠳ࠨẙ").format(bstack1111l1ll111_opy_))
                bstack1111ll11l11_opy_ = []
        self.__1111l1lllll_opy_(
            bstack1111ll1l11l_opy_.get(bstack1111l1_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡥࠩẚ"), False),
            bstack1111ll1l11l_opy_.get(bstack1111l1_opy_ (u"ࠩࡰࡳࡩ࡫ࠧẛ"), bstack1111l1_opy_ (u"ࠪࡶࡪࡲࡥࡷࡣࡱࡸࡋ࡯ࡲࡴࡶࠪẜ")),
            bstack1111ll11l11_opy_
        )
        self.__1111ll1111l_opy_(opts.get(bstack1111l1l1ll1_opy_, False))
        self.__1111ll11111_opy_(opts.get(bstack111l1111111_opy_, False))
        self.__1111ll111l1_opy_(opts.get(bstack111l1111ll1_opy_, False))
    @classmethod
    def bstack1l1l1l1111_opy_(cls, config=None):
        if cls._1lll1llllll_opy_ is None and config is not None:
            cls._1lll1llllll_opy_ = bstack11l111llll_opy_(config)
        return cls._1lll1llllll_opy_
    @staticmethod
    def bstack111l1l11l_opy_(config: dict) -> bool:
        bstack1111l1l111l_opy_ = config.get(bstack1111l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡑࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࡐࡲࡷ࡭ࡴࡴࡳࠨẝ"), {}).get(bstack1111l1llll1_opy_, {})
        return bstack1111l1l111l_opy_.get(bstack1111l1_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭ẞ"), False)
    @staticmethod
    def bstack1l111l1111_opy_(config: dict) -> int:
        bstack1111l1l111l_opy_ = config.get(bstack1111l1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪẟ"), {}).get(bstack1111l1llll1_opy_, {})
        retries = 0
        if bstack11l111llll_opy_.bstack111l1l11l_opy_(config):
            retries = bstack1111l1l111l_opy_.get(bstack1111l1_opy_ (u"ࠧ࡮ࡣࡻࡖࡪࡺࡲࡪࡧࡶࠫẠ"), 1)
        return retries
    @staticmethod
    def bstack1111ll1l1_opy_(config: dict) -> dict:
        bstack1111ll1l111_opy_ = config.get(bstack1111l1_opy_ (u"ࠨࡶࡨࡷࡹࡕࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲࡔࡶࡴࡪࡱࡱࡷࠬạ"), {})
        return {
            key: value for key, value in bstack1111ll1l111_opy_.items() if key in bstack1111l1l1lll_opy_
        }
    @staticmethod
    def bstack1111ll1l1l1_opy_():
        bstack1111l1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡃࡩࡧࡦ࡯ࠥ࡯ࡦࠡࡶ࡫ࡩࠥࡧࡢࡰࡴࡷࠤࡧࡻࡩ࡭ࡦࠣࡪ࡮ࡲࡥࠡࡧࡻ࡭ࡸࡺࡳ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨẢ")
        return os.path.exists(os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"ࠥࡥࡧࡵࡲࡵࡡࡥࡹ࡮ࡲࡤࡠࡽࢀࠦả").format(os.getenv(bstack1111l1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠤẤ")))))
    @staticmethod
    def bstack111l111111l_opy_(test_name: str):
        bstack1111l1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡆ࡬ࡪࡩ࡫ࠡ࡫ࡩࠤࡹ࡮ࡥࠡࡣࡥࡳࡷࡺࠠࡣࡷ࡬ࡰࡩࠦࡦࡪ࡮ࡨࠤࡪࡾࡩࡴࡶࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤấ")
        bstack1111lll111l_opy_ = os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࡥࡴࡦࡵࡷࡷࡤࢁࡽ࠯ࡶࡻࡸࠧẦ").format(os.getenv(bstack1111l1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠧầ"))))
        with open(bstack1111lll111l_opy_, bstack1111l1_opy_ (u"ࠨࡣࠪẨ")) as file:
            file.write(bstack1111l1_opy_ (u"ࠤࡾࢁࡡࡴࠢẩ").format(test_name))
    @staticmethod
    def bstack1111llllll1_opy_(framework: str) -> bool:
       return framework.lower() in bstack1111l1l1l1l_opy_
    @staticmethod
    def bstack11l1l1111ll_opy_(config: dict) -> bool:
        bstack1111ll11l1l_opy_ = config.get(bstack1111l1_opy_ (u"ࠪࡸࡪࡹࡴࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࡏࡱࡶ࡬ࡳࡳࡹࠧẪ"), {}).get(bstack1111ll11lll_opy_, {})
        return bstack1111ll11l1l_opy_.get(bstack1111l1_opy_ (u"ࠫࡪࡴࡡࡣ࡮ࡨࡨࠬẫ"), False)
    @staticmethod
    def bstack11l1l111l11_opy_(config: dict, bstack11l11ll1ll1_opy_: int = 0) -> int:
        bstack1111l1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡊࡩࡹࠦࡴࡩࡧࠣࡪࡦ࡯࡬ࡶࡴࡨࠤࡹ࡮ࡲࡦࡵ࡫ࡳࡱࡪࠬࠡࡹ࡫࡭ࡨ࡮ࠠࡤࡣࡱࠤࡧ࡫ࠠࡢࡰࠣࡥࡧࡹ࡯࡭ࡷࡷࡩࠥࡴࡵ࡮ࡤࡨࡶࠥࡵࡲࠡࡣࠣࡴࡪࡸࡣࡦࡰࡷࡥ࡬࡫࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡄࡶ࡬ࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡣࡰࡰࡩ࡭࡬ࠦࠨࡥ࡫ࡦࡸ࠮ࡀࠠࡕࡪࡨࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤࡩ࡯ࡣࡵ࡫ࡲࡲࡦࡸࡹ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡵࡱࡷࡥࡱࡥࡴࡦࡵࡷࡷࠥ࠮ࡩ࡯ࡶࠬ࠾࡚ࠥࡨࡦࠢࡷࡳࡹࡧ࡬ࠡࡰࡸࡱࡧ࡫ࡲࠡࡱࡩࠤࡹ࡫ࡳࡵࡵࠣࠬࡷ࡫ࡱࡶ࡫ࡵࡩࡩࠦࡦࡰࡴࠣࡴࡪࡸࡣࡦࡰࡷࡥ࡬࡫࠭ࡣࡣࡶࡩࡩࠦࡴࡩࡴࡨࡷ࡭ࡵ࡬ࡥࡵࠬ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡒࡦࡶࡸࡶࡳࡹ࠺ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡩ࡯ࡶ࠽ࠤ࡙࡮ࡥࠡࡨࡤ࡭ࡱࡻࡲࡦࠢࡷ࡬ࡷ࡫ࡳࡩࡱ࡯ࡨ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥẬ")
        bstack1111ll11l1l_opy_ = config.get(bstack1111l1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡒࡴࡹ࡯࡯࡯ࡵࠪậ"), {}).get(bstack1111l1_opy_ (u"ࠧࡢࡤࡲࡶࡹࡈࡵࡪ࡮ࡧࡓࡳࡌࡡࡪ࡮ࡸࡶࡪ࠭Ắ"), {})
        bstack1111ll1llll_opy_ = 0
        bstack1111ll1l1ll_opy_ = 0
        if bstack11l111llll_opy_.bstack11l1l1111ll_opy_(config):
            bstack1111ll1l1ll_opy_ = bstack1111ll11l1l_opy_.get(bstack1111l1_opy_ (u"ࠨ࡯ࡤࡼࡋࡧࡩ࡭ࡷࡵࡩࡸ࠭ắ"), 5)
            if isinstance(bstack1111ll1l1ll_opy_, str) and bstack1111ll1l1ll_opy_.endswith(bstack1111l1_opy_ (u"ࠩࠨࠫẰ")):
                try:
                    percentage = int(bstack1111ll1l1ll_opy_.strip(bstack1111l1_opy_ (u"ࠪࠩࠬằ")))
                    if bstack11l11ll1ll1_opy_ > 0:
                        bstack1111ll1llll_opy_ = math.ceil((percentage * bstack11l11ll1ll1_opy_) / 100)
                    else:
                        raise ValueError(bstack1111l1_opy_ (u"࡙ࠦࡵࡴࡢ࡮ࠣࡸࡪࡹࡴࡴࠢࡰࡹࡸࡺࠠࡣࡧࠣࡴࡷࡵࡶࡪࡦࡨࡨࠥ࡬࡯ࡳࠢࡳࡩࡷࡩࡥ࡯ࡶࡤ࡫ࡪ࠳ࡢࡢࡵࡨࡨࠥࡺࡨࡳࡧࡶ࡬ࡴࡲࡤࡴ࠰ࠥẲ"))
                except ValueError as e:
                    raise ValueError(bstack1111l1_opy_ (u"ࠧࡏ࡮ࡷࡣ࡯࡭ࡩࠦࡰࡦࡴࡦࡩࡳࡺࡡࡨࡧࠣࡺࡦࡲࡵࡦࠢࡩࡳࡷࠦ࡭ࡢࡺࡉࡥ࡮ࡲࡵࡳࡧࡶ࠾ࠥࢁࡽࠣẳ").format(bstack1111ll1l1ll_opy_)) from e
            else:
                bstack1111ll1llll_opy_ = int(bstack1111ll1l1ll_opy_)
        logger.info(bstack1111l1_opy_ (u"ࠨࡍࡢࡺࠣࡪࡦ࡯࡬ࡶࡴࡨࡷࠥࡺࡨࡳࡧࡶ࡬ࡴࡲࡤࠡࡵࡨࡸࠥࡺ࡯࠻ࠢࡾࢁࠥ࠮ࡦࡳࡱࡰࠤࡨࡵ࡮ࡧ࡫ࡪ࠾ࠥࢁࡽࠪࠤẴ").format(bstack1111ll1llll_opy_, bstack1111ll1l1ll_opy_))
        return bstack1111ll1llll_opy_
    def bstack1111lllll1l_opy_(self):
        return self.bstack1111lllll11_opy_
    def bstack1111l1lll1l_opy_(self):
        return self.bstack111l11111l1_opy_
    def bstack111l11111ll_opy_(self):
        return self.bstack1111l1ll1ll_opy_
    def __1111l1lllll_opy_(self, enabled, mode, source=None):
        try:
            self.bstack1111lllll11_opy_ = bool(enabled)
            if mode not in [bstack1111l1_opy_ (u"ࠧࡳࡧ࡯ࡩࡻࡧ࡮ࡵࡈ࡬ࡶࡸࡺࠧẵ"), bstack1111l1_opy_ (u"ࠨࡴࡨࡰࡪࡼࡡ࡯ࡶࡒࡲࡱࡿࠧẶ")]:
                logger.warning(bstack1111l1_opy_ (u"ࠤࡌࡲࡻࡧ࡬ࡪࡦࠣࡷࡲࡧࡲࡵࠢࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠥࡳ࡯ࡥࡧࠣࠫࢀࢃࠧࠡࡲࡵࡳࡻ࡯ࡤࡦࡦ࠱ࠤࡉ࡫ࡦࡢࡷ࡯ࡸ࡮ࡴࡧࠡࡶࡲࠤࠬࡸࡥ࡭ࡧࡹࡥࡳࡺࡆࡪࡴࡶࡸࠬ࠴ࠢặ").format(mode))
                mode = bstack1111l1_opy_ (u"ࠪࡶࡪࡲࡥࡷࡣࡱࡸࡋ࡯ࡲࡴࡶࠪẸ")
            self.bstack111l11111l1_opy_ = mode
            if source is None:
                self.bstack1111l1ll1ll_opy_ = None
            elif isinstance(source, list):
                self.bstack1111l1ll1ll_opy_ = source
            elif isinstance(source, str) and source.endswith(bstack1111l1_opy_ (u"ࠫ࠳ࡰࡳࡰࡰࠪẹ")):
                self.bstack1111l1ll1ll_opy_ = self._1111lllllll_opy_(source)
            self.__1111lll11l1_opy_()
        except Exception as e:
            logger.error(bstack1111l1_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡹ࡭ࡢࡴࡷࠤࡸ࡫࡬ࡦࡥࡷ࡭ࡴࡴࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠠ࠮ࠢࡨࡲࡦࡨ࡬ࡦࡦ࠽ࠤࢀࢃࠬࠡ࡯ࡲࡨࡪࡀࠠࡼࡿ࠯ࠤࡸࡵࡵࡳࡥࡨ࠾ࠥࢁࡽ࠯ࠢࡈࡶࡷࡵࡲ࠻ࠢࡾࢁࠧẺ").format(enabled, mode, source, e))
    def bstack1111l1l11ll_opy_(self):
        return self.bstack1111llll1l1_opy_
    def __1111ll1111l_opy_(self, value):
        self.bstack1111llll1l1_opy_ = bool(value)
        self.__1111lll11l1_opy_()
    def bstack1111l1l11l1_opy_(self):
        return self.bstack1111llll111_opy_
    def __1111ll11111_opy_(self, value):
        self.bstack1111llll111_opy_ = bool(value)
        self.__1111lll11l1_opy_()
    def bstack1111l11llll_opy_(self):
        return self.bstack1111lll11ll_opy_
    def __1111ll111l1_opy_(self, value):
        self.bstack1111lll11ll_opy_ = bool(value)
        self.__1111lll11l1_opy_()
    def __1111lll11l1_opy_(self):
        if self.bstack1111lllll11_opy_:
            self.bstack1111llll1l1_opy_ = False
            self.bstack1111llll111_opy_ = False
            self.bstack1111lll11ll_opy_ = False
            self.bstack1111l1lll11_opy_.enable(bstack1111l11lll1_opy_)
        elif self.bstack1111llll1l1_opy_:
            self.bstack1111llll111_opy_ = False
            self.bstack1111lll11ll_opy_ = False
            self.bstack1111lllll11_opy_ = False
            self.bstack1111l1lll11_opy_.enable(bstack1111l1l1ll1_opy_)
        elif self.bstack1111llll111_opy_:
            self.bstack1111llll1l1_opy_ = False
            self.bstack1111lll11ll_opy_ = False
            self.bstack1111lllll11_opy_ = False
            self.bstack1111l1lll11_opy_.enable(bstack111l1111111_opy_)
        elif self.bstack1111lll11ll_opy_:
            self.bstack1111llll1l1_opy_ = False
            self.bstack1111llll111_opy_ = False
            self.bstack1111lllll11_opy_ = False
            self.bstack1111l1lll11_opy_.enable(bstack111l1111ll1_opy_)
        else:
            self.bstack1111l1lll11_opy_.disable()
    def bstack1lll1lll1l_opy_(self):
        return self.bstack1111l1lll11_opy_.bstack1111lll1lll_opy_()
    def bstack1l11l11ll_opy_(self):
        if self.bstack1111l1lll11_opy_.bstack1111lll1lll_opy_():
            return self.bstack1111l1lll11_opy_.get_name()
        return None
    def _1111lllllll_opy_(self, bstack1111l1ll1l1_opy_):
        bstack1111l1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡔࡦࡸࡳࡦࠢࡍࡗࡔࡔࠠࡴࡱࡸࡶࡨ࡫ࠠࡤࡱࡱࡪ࡮࡭ࡵࡳࡣࡷ࡭ࡴࡴࠠࡧ࡫࡯ࡩࠥࡧ࡮ࡥࠢࡩࡳࡷࡳࡡࡵࠢ࡬ࡸࠥ࡬࡯ࡳࠢࡶࡱࡦࡸࡴࠡࡵࡨࡰࡪࡩࡴࡪࡱࡱ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡷࡴࡻࡲࡤࡧࡢࡪ࡮ࡲࡥࡠࡲࡤࡸ࡭ࠦࠨࡴࡶࡵ࠭࠿ࠦࡐࡢࡶ࡫ࠤࡹࡵࠠࡵࡪࡨࠤࡏ࡙ࡏࡏࠢࡦࡳࡳ࡬ࡩࡨࡷࡵࡥࡹ࡯࡯࡯ࠢࡩ࡭ࡱ࡫ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࡮࡬ࡷࡹࡀࠠࡇࡱࡵࡱࡦࡺࡴࡦࡦࠣࡰ࡮ࡹࡴࠡࡱࡩࠤࡷ࡫ࡰࡰࡵ࡬ࡸࡴࡸࡹࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࡴࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨẻ")
        if not os.path.isfile(bstack1111l1ll1l1_opy_):
            logger.error(bstack1111l1_opy_ (u"ࠢࡔࡱࡸࡶࡨ࡫ࠠࡧ࡫࡯ࡩࠥ࠭ࡻࡾࠩࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷ࠲ࠧẼ").format(bstack1111l1ll1l1_opy_))
            return []
        data = None
        try:
            with open(bstack1111l1ll1l1_opy_, bstack1111l1_opy_ (u"ࠣࡴࠥẽ")) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(bstack1111l1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡲࡤࡶࡸ࡯࡮ࡨࠢࡍࡗࡔࡔࠠࡧࡴࡲࡱࠥࡹ࡯ࡶࡴࡦࡩࠥ࡬ࡩ࡭ࡧࠣࠫࢀࢃࠧ࠻ࠢࡾࢁࠧẾ").format(bstack1111l1ll1l1_opy_, e))
            return []
        _1111ll1lll1_opy_ = None
        _1111lll1111_opy_ = None
        def _1111lll1ll1_opy_():
            bstack1111llll11l_opy_ = {}
            bstack111l1111l11_opy_ = {}
            try:
                if self.bstack1111ll1ll11_opy_.startswith(bstack1111l1_opy_ (u"ࠪࡿࠬế")) and self.bstack1111ll1ll11_opy_.endswith(bstack1111l1_opy_ (u"ࠫࢂ࠭Ề")):
                    bstack1111llll11l_opy_ = json.loads(self.bstack1111ll1ll11_opy_)
                else:
                    bstack1111llll11l_opy_ = dict(item.split(bstack1111l1_opy_ (u"ࠬࡀࠧề")) for item in self.bstack1111ll1ll11_opy_.split(bstack1111l1_opy_ (u"࠭ࠬࠨỂ")) if bstack1111l1_opy_ (u"ࠧ࠻ࠩể") in item) if self.bstack1111ll1ll11_opy_ else {}
                if self.bstack1111lll1l11_opy_.startswith(bstack1111l1_opy_ (u"ࠨࡽࠪỄ")) and self.bstack1111lll1l11_opy_.endswith(bstack1111l1_opy_ (u"ࠩࢀࠫễ")):
                    bstack111l1111l11_opy_ = json.loads(self.bstack1111lll1l11_opy_)
                else:
                    bstack111l1111l11_opy_ = dict(item.split(bstack1111l1_opy_ (u"ࠪ࠾ࠬỆ")) for item in self.bstack1111lll1l11_opy_.split(bstack1111l1_opy_ (u"ࠫ࠱࠭ệ")) if bstack1111l1_opy_ (u"ࠬࡀࠧỈ") in item) if self.bstack1111lll1l11_opy_ else {}
            except json.JSONDecodeError as e:
                logger.error(bstack1111l1_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡶࡡࡳࡵ࡬ࡲ࡬ࠦࡦࡦࡣࡷࡹࡷ࡫ࠠࡣࡴࡤࡲࡨ࡮ࠠ࡮ࡣࡳࡴ࡮ࡴࡧࡴ࠼ࠣࡿࢂࠨỉ").format(e))
            logger.debug(bstack1111l1_opy_ (u"ࠢࡇࡧࡤࡸࡺࡸࡥࠡࡤࡵࡥࡳࡩࡨࠡ࡯ࡤࡴࡵ࡯࡮ࡨࡵࠣࡪࡷࡵ࡭ࠡࡧࡱࡺ࠿ࠦࡻࡾ࠮ࠣࡇࡑࡏ࠺ࠡࡽࢀࠦỊ").format(bstack1111llll11l_opy_, bstack111l1111l11_opy_))
            return bstack1111llll11l_opy_, bstack111l1111l11_opy_
        if _1111ll1lll1_opy_ is None or _1111lll1111_opy_ is None:
            _1111ll1lll1_opy_, _1111lll1111_opy_ = _1111lll1ll1_opy_()
        def bstack1111llll1ll_opy_(name, bstack1111ll11ll1_opy_):
            if name in _1111lll1111_opy_:
                return _1111lll1111_opy_[name]
            if name in _1111ll1lll1_opy_:
                return _1111ll1lll1_opy_[name]
            if bstack1111ll11ll1_opy_.get(bstack1111l1_opy_ (u"ࠨࡨࡨࡥࡹࡻࡲࡦࡄࡵࡥࡳࡩࡨࠨị")):
                return bstack1111ll11ll1_opy_[bstack1111l1_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࠩỌ")]
            return None
        if isinstance(data, dict):
            bstack1111l1ll11l_opy_ = []
            bstack1111lll1l1l_opy_ = re.compile(bstack1111l1_opy_ (u"ࡵࠫࡣࡡࡁ࠮࡜࠳࠱࠾ࡥ࡝ࠬࠦࠪọ"))
            for name, bstack1111ll11ll1_opy_ in data.items():
                if not isinstance(bstack1111ll11ll1_opy_, dict):
                    continue
                if not bstack1111ll11ll1_opy_.get(bstack1111l1_opy_ (u"ࠫࡺࡸ࡬ࠨỎ")):
                    logger.warning(bstack1111l1_opy_ (u"ࠧࡘࡥࡱࡱࡶ࡭ࡹࡵࡲࡺࠢࡘࡖࡑࠦࡩࡴࠢࡰ࡭ࡸࡹࡩ࡯ࡩࠣࡪࡴࡸࠠࡴࡱࡸࡶࡨ࡫ࠠࠨࡽࢀࠫ࠿ࠦࡻࡾࠤỏ").format(name, bstack1111ll11ll1_opy_))
                    continue
                if not bstack1111lll1l1l_opy_.match(name):
                    logger.warning(bstack1111l1_opy_ (u"ࠨࡉ࡯ࡸࡤࡰ࡮ࡪࠠࡴࡱࡸࡶࡨ࡫ࠠࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠤ࡫ࡵࡲ࡮ࡣࡷࠤ࡫ࡵࡲࠡࠩࡾࢁࠬࡀࠠࡼࡿࠥỐ").format(name, bstack1111ll11ll1_opy_))
                    continue
                if len(name) > 30 or len(name) < 1:
                    logger.warning(bstack1111l1_opy_ (u"ࠢࡔࡱࡸࡶࡨ࡫ࠠࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠤࠬࢁࡽࠨࠢࡰࡹࡸࡺࠠࡩࡣࡹࡩࠥࡧࠠ࡭ࡧࡱ࡫ࡹ࡮ࠠࡣࡧࡷࡻࡪ࡫࡮ࠡ࠳ࠣࡥࡳࡪࠠ࠴࠲ࠣࡧ࡭ࡧࡲࡢࡥࡷࡩࡷࡹ࠮ࠣố").format(name))
                    continue
                bstack1111ll11ll1_opy_ = bstack1111ll11ll1_opy_.copy()
                bstack1111ll11ll1_opy_[bstack1111l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭Ồ")] = name
                bstack1111ll11ll1_opy_[bstack1111l1_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࡅࡶࡦࡴࡣࡩࠩồ")] = bstack1111llll1ll_opy_(name, bstack1111ll11ll1_opy_)
                if not bstack1111ll11ll1_opy_.get(bstack1111l1_opy_ (u"ࠪࡪࡪࡧࡴࡶࡴࡨࡆࡷࡧ࡮ࡤࡪࠪỔ")):
                    logger.warning(bstack1111l1_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩࠥࡨࡲࡢࡰࡦ࡬ࠥࡴ࡯ࡵࠢࡶࡴࡪࡩࡩࡧ࡫ࡨࡨࠥ࡬࡯ࡳࠢࡶࡳࡺࡸࡣࡦࠢࠪࡿࢂ࠭࠺ࠡࡽࢀࠦổ").format(name, bstack1111ll11ll1_opy_))
                    continue
                if bstack1111ll11ll1_opy_.get(bstack1111l1_opy_ (u"ࠬࡨࡡࡴࡧࡅࡶࡦࡴࡣࡩࠩỖ")) and bstack1111ll11ll1_opy_[bstack1111l1_opy_ (u"࠭ࡢࡢࡵࡨࡆࡷࡧ࡮ࡤࡪࠪỗ")] == bstack1111ll11ll1_opy_[bstack1111l1_opy_ (u"ࠧࡧࡧࡤࡸࡺࡸࡥࡃࡴࡤࡲࡨ࡮ࠧỘ")]:
                    logger.warning(bstack1111l1_opy_ (u"ࠣࡈࡨࡥࡹࡻࡲࡦࠢࡥࡶࡦࡴࡣࡩࠢࡤࡲࡩࠦࡢࡢࡵࡨࠤࡧࡸࡡ࡯ࡥ࡫ࠤࡨࡧ࡮࡯ࡱࡷࠤࡧ࡫ࠠࡵࡪࡨࠤࡸࡧ࡭ࡦࠢࡩࡳࡷࠦࡳࡰࡷࡵࡧࡪࠦࠧࡼࡿࠪ࠾ࠥࢁࡽࠣộ").format(name, bstack1111ll11ll1_opy_))
                    continue
                bstack1111l1ll11l_opy_.append(bstack1111ll11ll1_opy_)
            return bstack1111l1ll11l_opy_
        return data
    def bstack111l111llll_opy_(self):
        data = {
            bstack1111l1_opy_ (u"ࠩࡵࡹࡳࡥࡳ࡮ࡣࡵࡸࡤࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠨỚ"): {
                bstack1111l1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫớ"): self.bstack1111lllll1l_opy_(),
                bstack1111l1_opy_ (u"ࠫࡲࡵࡤࡦࠩỜ"): self.bstack1111l1lll1l_opy_(),
                bstack1111l1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬờ"): self.bstack111l11111ll_opy_()
            }
        }
        return data
    def bstack1111ll111ll_opy_(self, config):
        bstack1111l1l1111_opy_ = {}
        bstack1111l1l1111_opy_[bstack1111l1_opy_ (u"࠭ࡲࡶࡰࡢࡷࡲࡧࡲࡵࡡࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠬỞ")] = {
            bstack1111l1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨở"): self.bstack1111lllll1l_opy_(),
            bstack1111l1_opy_ (u"ࠨ࡯ࡲࡨࡪ࠭Ỡ"): self.bstack1111l1lll1l_opy_()
        }
        bstack1111l1l1111_opy_[bstack1111l1_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࡠࡲࡵࡩࡻ࡯࡯ࡶࡵ࡯ࡽࡤ࡬ࡡࡪ࡮ࡨࡨࠬỡ")] = {
            bstack1111l1_opy_ (u"ࠪࡩࡳࡧࡢ࡭ࡧࡧࠫỢ"): self.bstack1111l1l11l1_opy_()
        }
        bstack1111l1l1111_opy_[bstack1111l1_opy_ (u"ࠫࡷࡻ࡮ࡠࡲࡵࡩࡻ࡯࡯ࡶࡵ࡯ࡽࡤ࡬ࡡࡪ࡮ࡨࡨࡤ࡬ࡩࡳࡵࡷࠫợ")] = {
            bstack1111l1_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭Ụ"): self.bstack1111l1l11ll_opy_()
        }
        bstack1111l1l1111_opy_[bstack1111l1_opy_ (u"࠭ࡳ࡬࡫ࡳࡣ࡫ࡧࡩ࡭࡫ࡱ࡫ࡤࡧ࡮ࡥࡡࡩࡰࡦࡱࡹࠨụ")] = {
            bstack1111l1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨỦ"): self.bstack1111l11llll_opy_()
        }
        if self.bstack111l1l11l_opy_(config):
            bstack1111l1l1111_opy_[bstack1111l1_opy_ (u"ࠨࡴࡨࡸࡷࡿ࡟ࡵࡧࡶࡸࡸࡥ࡯࡯ࡡࡩࡥ࡮ࡲࡵࡳࡧࠪủ")] = {
                bstack1111l1_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡦࠪỨ"): True,
                bstack1111l1_opy_ (u"ࠪࡱࡦࡾ࡟ࡳࡧࡷࡶ࡮࡫ࡳࠨứ"): self.bstack1l111l1111_opy_(config)
            }
        if self.bstack11l1l1111ll_opy_(config):
            bstack1111l1l1111_opy_[bstack1111l1_opy_ (u"ࠫࡦࡨ࡯ࡳࡶࡢࡦࡺ࡯࡬ࡥࡡࡲࡲࡤ࡬ࡡࡪ࡮ࡸࡶࡪ࠭Ừ")] = {
                bstack1111l1_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡩ࠭ừ"): True,
                bstack1111l1_opy_ (u"࠭࡭ࡢࡺࡢࡪࡦ࡯࡬ࡶࡴࡨࡷࠬỬ"): self.bstack11l1l111l11_opy_(config)
            }
        return bstack1111l1l1111_opy_
    def bstack11l1ll1l1_opy_(self, config):
        bstack1111l1_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࠡࠢࠣࠤࡈࡵ࡬࡭ࡧࡦࡸࡸࠦࡢࡶ࡫࡯ࡨࠥࡪࡡࡵࡣࠣࡦࡾࠦ࡭ࡢ࡭࡬ࡲ࡬ࠦࡡࠡࡥࡤࡰࡱࠦࡴࡰࠢࡷ࡬ࡪࠦࡣࡰ࡮࡯ࡩࡨࡺ࠭ࡣࡷ࡬ࡰࡩ࠳ࡤࡢࡶࡤࠤࡪࡴࡤࡱࡱ࡬ࡲࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡵࡪ࡮ࡧࡣࡺࡻࡩࡥࠢࠫࡷࡹࡸࠩ࠻ࠢࡗ࡬ࡪࠦࡕࡖࡋࡇࠤࡴ࡬ࠠࡵࡪࡨࠤࡧࡻࡩ࡭ࡦࠣࡸࡴࠦࡣࡰ࡮࡯ࡩࡨࡺࠠࡥࡣࡷࡥࠥ࡬࡯ࡳ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷ࠿ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࡩ࡯ࡣࡵ࠼ࠣࡖࡪࡹࡰࡰࡰࡶࡩࠥ࡬ࡲࡰ࡯ࠣࡸ࡭࡫ࠠࡤࡱ࡯ࡰࡪࡩࡴ࠮ࡤࡸ࡭ࡱࡪ࠭ࡥࡣࡷࡥࠥ࡫࡮ࡥࡲࡲ࡭ࡳࡺࠬࠡࡱࡵࠤࡓࡵ࡮ࡦࠢ࡬ࡪࠥ࡬ࡡࡪ࡮ࡨࡨ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠣࠤࠥử")
        if not (config.get(bstack1111l1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫỮ"), None) in bstack11l1ll11l1l_opy_ and self.bstack1111lllll1l_opy_()):
            return None
        bstack1111l1l1l11_opy_ = os.environ.get(bstack1111l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧữ"), None)
        logger.debug(bstack1111l1_opy_ (u"ࠥ࡟ࡨࡵ࡬࡭ࡧࡦࡸࡇࡻࡩ࡭ࡦࡇࡥࡹࡧ࡝ࠡࡅࡲࡰࡱ࡫ࡣࡵ࡫ࡱ࡫ࠥࡨࡵࡪ࡮ࡧࠤࡩࡧࡴࡢࠢࡩࡳࡷࠦࡢࡶ࡫࡯ࡨ࡛ࠥࡕࡊࡆ࠽ࠤࢀࢃࠢỰ").format(bstack1111l1l1l11_opy_))
        try:
            bstack11ll1111ll1_opy_ = bstack1111l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠰ࡣࡳ࡭࠴ࡼ࠱࠰ࡤࡸ࡭ࡱࡪࡳ࠰ࡽࢀ࠳ࡨࡵ࡬࡭ࡧࡦࡸ࠲ࡨࡵࡪ࡮ࡧ࠱ࡩࡧࡴࡢࠤự").format(bstack1111l1l1l11_opy_)
            payload = {
                bstack1111l1_opy_ (u"ࠧࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠥỲ"): config.get(bstack1111l1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫỳ"), bstack1111l1_opy_ (u"ࠧࠨỴ")),
                bstack1111l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠦỵ"): config.get(bstack1111l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬỶ"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡔࡸࡲࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣỷ"): os.environ.get(bstack1111l1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠥỸ"), bstack1111l1_opy_ (u"ࠧࠨỹ")),
                bstack1111l1_opy_ (u"ࠨ࡮ࡰࡦࡨࡍࡳࡪࡥࡹࠤỺ"): int(os.environ.get(bstack1111l1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡎࡐࡆࡈࡣࡎࡔࡄࡆ࡚ࠥỻ")) or bstack1111l1_opy_ (u"ࠣ࠲ࠥỼ")),
                bstack1111l1_opy_ (u"ࠤࡷࡳࡹࡧ࡬ࡏࡱࡧࡩࡸࠨỽ"): int(os.environ.get(bstack1111l1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡓ࡙ࡇࡌࡠࡐࡒࡈࡊࡥࡃࡐࡗࡑࡘࠧỾ")) or bstack1111l1_opy_ (u"ࠦ࠶ࠨỿ")),
                bstack1111l1_opy_ (u"ࠧ࡮࡯ࡴࡶࡌࡲ࡫ࡵࠢἀ"): get_host_info(),
            }
            logger.debug(bstack1111l1_opy_ (u"ࠨ࡛ࡤࡱ࡯ࡰࡪࡩࡴࡃࡷ࡬ࡰࡩࡊࡡࡵࡣࡠࠤࡘ࡫࡮ࡥ࡫ࡱ࡫ࠥࡨࡵࡪ࡮ࡧࠤࡩࡧࡴࡢࠢࡳࡥࡾࡲ࡯ࡢࡦ࠽ࠤࢀࢃࠢἁ").format(payload))
            response = bstack11l1lllll1l_opy_.bstack1111ll1ll1l_opy_(bstack11ll1111ll1_opy_, payload)
            if response:
                logger.debug(bstack1111l1_opy_ (u"ࠢ࡜ࡥࡲࡰࡱ࡫ࡣࡵࡄࡸ࡭ࡱࡪࡄࡢࡶࡤࡡࠥࡈࡵࡪ࡮ࡧࠤࡩࡧࡴࡢࠢࡦࡳࡱࡲࡥࡤࡶ࡬ࡳࡳࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠻ࠢࡾࢁࠧἂ").format(response))
                return response
            else:
                logger.error(bstack1111l1_opy_ (u"ࠣ࡝ࡦࡳࡱࡲࡥࡤࡶࡅࡹ࡮ࡲࡤࡅࡣࡷࡥࡢࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡦࡳࡱࡲࡥࡤࡶࠣࡦࡺ࡯࡬ࡥࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡧࡻࡩ࡭ࡦ࡙࡚ࠣࡏࡄ࠻ࠢࡾࢁࠧἃ").format(bstack1111l1l1l11_opy_))
                return None
        except Exception as e:
            logger.error(bstack1111l1_opy_ (u"ࠤ࡞ࡧࡴࡲ࡬ࡦࡥࡷࡆࡺ࡯࡬ࡥࡆࡤࡸࡦࡣࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡣࡰ࡮࡯ࡩࡨࡺࡩ࡯ࡩࠣࡦࡺ࡯࡬ࡥࠢࡧࡥࡹࡧࠠࡧࡱࡵࠤࡧࡻࡩ࡭ࡦ࡙࡚ࠣࡏࡄࠡࡽࢀ࠾ࠥࢁࡽࠣἄ").format(bstack1111l1l1l11_opy_, e))
            return None