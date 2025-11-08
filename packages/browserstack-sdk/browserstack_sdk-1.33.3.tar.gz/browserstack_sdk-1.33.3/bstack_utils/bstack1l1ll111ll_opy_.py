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
from bstack_utils.constants import *
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.bstack111l111lll1_opy_ import bstack111l11l1l11_opy_
from bstack_utils.bstack11llll11l_opy_ import bstack11l111llll_opy_
from bstack_utils.helper import bstack11ll11ll1l_opy_
import json
class bstack11l1111l_opy_:
    _1lll1llllll_opy_ = None
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.bstack111l11l11l1_opy_ = bstack111l11l1l11_opy_(self.config, logger)
        self.bstack11llll11l_opy_ = bstack11l111llll_opy_.bstack1l1l1l1111_opy_(config=self.config)
        self.bstack111l11l11ll_opy_ = {}
        self.bstack11111ll11l_opy_ = False
        self.bstack111l111l1l1_opy_ = (
            self.__111l1111lll_opy_()
            and self.bstack11llll11l_opy_ is not None
            and self.bstack11llll11l_opy_.bstack1lll1lll1l_opy_()
            and config.get(bstack1111l1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫṮ"), None) is not None
            and config.get(bstack1111l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪṯ"), os.path.basename(os.getcwd())) is not None
        )
    @classmethod
    def bstack1l1l1l1111_opy_(cls, config, logger):
        if cls._1lll1llllll_opy_ is None and config is not None:
            cls._1lll1llllll_opy_ = bstack11l1111l_opy_(config, logger)
        return cls._1lll1llllll_opy_
    def bstack1lll1lll1l_opy_(self):
        bstack1111l1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡊ࡯ࠡࡰࡲࡸࠥࡧࡰࡱ࡮ࡼࠤࡹ࡫ࡳࡵࠢࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡼ࡮ࡥ࡯࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡑ࠴࠵ࡾࠦࡩࡴࠢࡱࡳࡹࠦࡥ࡯ࡣࡥࡰࡪࡪࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡕࡲࡥࡧࡵ࡭ࡳ࡭ࠠࡪࡵࠣࡲࡴࡺࠠࡦࡰࡤࡦࡱ࡫ࡤࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠤ࡮ࡹࠠࡏࡱࡱࡩࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡦࡺ࡯࡬ࡥࡐࡤࡱࡪࠦࡩࡴࠢࡑࡳࡳ࡫ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦṰ")
        return self.bstack111l111l1l1_opy_ and self.bstack111l11l1l1l_opy_()
    def bstack111l11l1l1l_opy_(self):
        bstack111l111ll1l_opy_ = os.getenv(bstack1111l1_opy_ (u"ࠩࡉࡖࡆࡓࡅࡘࡑࡕࡏࡤ࡛ࡓࡆࡆࠪṱ"), self.config.get(bstack1111l1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭Ṳ"), None))
        return bstack111l111ll1l_opy_ in bstack11l1ll11l1l_opy_
    def __111l1111lll_opy_(self):
        bstack11l1lll1ll1_opy_ = False
        for fw in bstack11l1l1ll111_opy_:
            if fw in self.config.get(bstack1111l1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧṳ"), bstack1111l1_opy_ (u"ࠬ࠭Ṵ")):
                bstack11l1lll1ll1_opy_ = True
        return bstack11ll11ll1l_opy_(self.config.get(bstack1111l1_opy_ (u"࠭ࡴࡦࡵࡷࡓࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪṵ"), bstack11l1lll1ll1_opy_))
    def bstack111l111ll11_opy_(self):
        return (not self.bstack1lll1lll1l_opy_() and
                self.bstack11llll11l_opy_ is not None and self.bstack11llll11l_opy_.bstack1lll1lll1l_opy_())
    def bstack111l11l111l_opy_(self):
        if not self.bstack111l111ll11_opy_():
            return
        if self.config.get(bstack1111l1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡏࡣࡰࡩࠬṶ"), None) is None or self.config.get(bstack1111l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫṷ"), os.path.basename(os.getcwd())) is None:
            self.logger.info(bstack1111l1_opy_ (u"ࠤࡗࡩࡸࡺࠠࡓࡧࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡨࡧ࡮ࠨࡶࠣࡻࡴࡸ࡫ࠡࡣࡶࠤࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠠࡰࡴࠣࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠡ࡫ࡶࠤࡳࡻ࡬࡭࠰ࠣࡔࡱ࡫ࡡࡴࡧࠣࡷࡪࡺࠠࡢࠢࡱࡳࡳ࠳࡮ࡶ࡮࡯ࠤࡻࡧ࡬ࡶࡧ࠱ࠦṸ"))
        if not self.__111l1111lll_opy_():
            self.logger.info(bstack1111l1_opy_ (u"ࠥࡘࡪࡹࡴࠡࡔࡨࡳࡷࡪࡥࡳ࡫ࡱ࡫ࠥࡩࡡ࡯ࠩࡷࠤࡼࡵࡲ࡬ࠢࡤࡷࠥࡺࡥࡴࡶࡕࡩࡵࡵࡲࡵ࡫ࡱ࡫ࠥ࡯ࡳࠡࡦ࡬ࡷࡦࡨ࡬ࡦࡦ࠱ࠤࡕࡲࡥࡢࡵࡨࠤࡪࡴࡡࡣ࡮ࡨࠤ࡮ࡺࠠࡧࡴࡲࡱࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠡࡨ࡬ࡰࡪ࠴ࠢṹ"))
    def bstack111l11l1111_opy_(self):
        return self.bstack11111ll11l_opy_
    def bstack111111llll_opy_(self, bstack111l11l1ll1_opy_):
        self.bstack11111ll11l_opy_ = bstack111l11l1ll1_opy_
        self.bstack11111ll1ll_opy_(bstack1111l1_opy_ (u"ࠦࡦࡶࡰ࡭࡫ࡨࡨࠧṺ"), bstack111l11l1ll1_opy_)
    def bstack1111l1111l_opy_(self, test_files):
        try:
            if test_files is None:
                self.logger.debug(bstack1111l1_opy_ (u"ࠧࡡࡲࡦࡱࡵࡨࡪࡸ࡟ࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡶࡡࠥࡔ࡯ࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷࠥࡶࡲࡰࡸ࡬ࡨࡪࡪࠠࡧࡱࡵࠤࡴࡸࡤࡦࡴ࡬ࡲ࡬࠴ࠢṻ"))
                return None
            orchestration_strategy = None
            orchestration_metadata = self.bstack11llll11l_opy_.bstack111l111llll_opy_()
            if self.bstack11llll11l_opy_ is not None:
                orchestration_strategy = self.bstack11llll11l_opy_.bstack1l11l11ll_opy_()
            if orchestration_strategy is None:
                self.logger.error(bstack1111l1_opy_ (u"ࠨࡏࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡳࡵࡴࡤࡸࡪ࡭ࡹࠡ࡫ࡶࠤࡓࡵ࡮ࡦ࠰ࠣࡇࡦࡴ࡮ࡰࡶࠣࡴࡷࡵࡣࡦࡧࡧࠤࡼ࡯ࡴࡩࠢࡷࡩࡸࡺࠠࡰࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡴࡧࡶࡷ࡮ࡵ࡮࠯ࠤṼ"))
                return None
            self.logger.info(bstack1111l1_opy_ (u"ࠢࡓࡧࡲࡶࡩ࡫ࡲࡪࡰࡪࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡹ࡬ࡸ࡭ࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡳࡵࡴࡤࡸࡪ࡭ࡹ࠻ࠢࡾࢁࠧṽ").format(orchestration_strategy))
            if cli.is_running():
                self.logger.debug(bstack1111l1_opy_ (u"ࠣࡗࡶ࡭ࡳ࡭ࠠࡄࡎࡌࠤ࡫ࡲ࡯ࡸࠢࡩࡳࡷࠦࡴࡦࡵࡷࠤ࡫࡯࡬ࡦࡵࠣࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰ࠱ࠦṾ"))
                ordered_test_files = cli.test_orchestration_session(test_files, orchestration_strategy, json.dumps(orchestration_metadata))
            else:
                self.logger.debug(bstack1111l1_opy_ (u"ࠤࡘࡷ࡮ࡴࡧࠡࡵࡧ࡯ࠥ࡬࡬ࡰࡹࠣࡪࡴࡸࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠲ࠧṿ"))
                self.bstack111l11l11l1_opy_.bstack111l111l1ll_opy_(test_files, orchestration_strategy, orchestration_metadata)
                ordered_test_files = self.bstack111l11l11l1_opy_.bstack111l111l11l_opy_()
            if not ordered_test_files:
                return None
            self.bstack11111ll1ll_opy_(bstack1111l1_opy_ (u"ࠥࡹࡵࡲ࡯ࡢࡦࡨࡨ࡙࡫ࡳࡵࡈ࡬ࡰࡪࡹࡃࡰࡷࡱࡸࠧẀ"), len(test_files))
            self.bstack11111ll1ll_opy_(bstack1111l1_opy_ (u"ࠦࡳࡵࡤࡦࡋࡱࡨࡪࡾࠢẁ"), int(os.environ.get(bstack1111l1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡓࡕࡄࡆࡡࡌࡒࡉࡋࡘࠣẂ")) or bstack1111l1_opy_ (u"ࠨ࠰ࠣẃ")))
            self.bstack11111ll1ll_opy_(bstack1111l1_opy_ (u"ࠢࡵࡱࡷࡥࡱࡔ࡯ࡥࡧࡶࠦẄ"), int(os.environ.get(bstack1111l1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡏࡑࡇࡉࡤࡉࡏࡖࡐࡗࠦẅ")) or bstack1111l1_opy_ (u"ࠤ࠴ࠦẆ")))
            self.bstack11111ll1ll_opy_(bstack1111l1_opy_ (u"ࠥࡨࡴࡽ࡮࡭ࡱࡤࡨࡪࡪࡔࡦࡵࡷࡊ࡮ࡲࡥࡴࡅࡲࡹࡳࡺࠢẇ"), len(ordered_test_files))
            self.bstack11111ll1ll_opy_(bstack1111l1_opy_ (u"ࠦࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳࡂࡒࡌࡇࡦࡲ࡬ࡄࡱࡸࡲࡹࠨẈ"), self.bstack111l11l11l1_opy_.bstack111l111l111_opy_())
            return ordered_test_files
        except Exception as e:
            self.logger.debug(bstack1111l1_opy_ (u"ࠧࡡࡲࡦࡱࡵࡨࡪࡸ࡟ࡵࡧࡶࡸࡤ࡬ࡩ࡭ࡧࡶࡡࠥࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡰࡴࡧࡩࡷ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡤ࡮ࡤࡷࡸ࡫ࡳ࠻ࠢࡾࢁࠧẉ").format(e))
        return None
    def bstack11111ll1ll_opy_(self, key, value):
        self.bstack111l11l11ll_opy_[key] = value
    def bstack11l11ll111_opy_(self):
        return self.bstack111l11l11ll_opy_