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
import time
from bstack_utils.bstack11ll1111l11_opy_ import bstack11l1lllll1l_opy_
from bstack_utils.constants import bstack11l1l1l111l_opy_
from bstack_utils.helper import get_host_info, bstack11l11l1lll1_opy_
class bstack111l11l1l11_opy_:
    bstack1111l1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࡎࡡ࡯ࡦ࡯ࡩࡸࠦࡴࡦࡵࡷࠤࡴࡸࡤࡦࡴ࡬ࡲ࡬ࠦ࡯ࡳࡥ࡫ࡩࡸࡺࡲࡢࡶ࡬ࡳࡳࠦࡷࡪࡶ࡫ࠤࡹ࡮ࡥࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡴࡧࡵࡺࡪࡸ࠮ࠋࠢࠣࠤࠥࠨࠢࠣ⃀")
    def __init__(self, config, logger):
        bstack1111l1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣ࠾ࡵࡧࡲࡢ࡯ࠣࡧࡴࡴࡦࡪࡩ࠽ࠤࡩ࡯ࡣࡵ࠮ࠣࡸࡪࡹࡴࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮ࠡࡥࡲࡲ࡫࡯ࡧࠋࠢࠣࠤࠥࠦࠠࠡࠢ࠽ࡴࡦࡸࡡ࡮ࠢࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡡࡶࡸࡷࡧࡴࡦࡩࡼ࠾ࠥࡹࡴࡳ࠮ࠣࡸࡪࡹࡴࠡࡱࡵࡨࡪࡸࡩ࡯ࡩࠣࡷࡹࡸࡡࡵࡧࡪࡽࠥࡴࡡ࡮ࡧࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢ⃁")
        self.config = config
        self.logger = logger
        self.bstack1llll1l11l1l_opy_ = bstack1111l1_opy_ (u"ࠢࡵࡧࡶࡸࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱ࠳ࡦࡶࡩ࠰ࡸ࠴࠳ࡸࡶ࡬ࡪࡶ࠰ࡸࡪࡹࡴࡴࠤ⃂")
        self.bstack1llll1l1l1l1_opy_ = None
        self.bstack1llll1ll1111_opy_ = 60
        self.bstack1llll1l11lll_opy_ = 5
        self.bstack1llll1l1111l_opy_ = 0
    def bstack111l111l1ll_opy_(self, test_files, orchestration_strategy, orchestration_metadata={}):
        bstack1111l1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡏ࡮ࡪࡶ࡬ࡥࡹ࡫ࡳࠡࡶ࡫ࡩࠥࡹࡰ࡭࡫ࡷࠤࡹ࡫ࡳࡵࡵࠣࡶࡪࡷࡵࡦࡵࡷࠤࡦࡴࡤࠡࡵࡷࡳࡷ࡫ࡳࠡࡶ࡫ࡩࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠠࡥࡣࡷࡥࠥ࡬࡯ࡳࠢࡳࡳࡱࡲࡩ࡯ࡩ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣ⃃")
        self.logger.debug(bstack1111l1_opy_ (u"ࠤ࡞ࡷࡵࡲࡩࡵࡖࡨࡷࡹࡹ࡝ࠡࡋࡱ࡭ࡹ࡯ࡡࡵ࡫ࡱ࡫ࠥࡹࡰ࡭࡫ࡷࠤࡹ࡫ࡳࡵࡵࠣࡻ࡮ࡺࡨࠡࡵࡷࡶࡦࡺࡥࡨࡻ࠽ࠤࢀࢃࠢ⃄").format(orchestration_strategy))
        try:
            bstack1llll1l1ll1l_opy_ = []
            bstack1111l1_opy_ (u"ࠥࠦࠧ࡝ࡥࠡࡹ࡬ࡰࡱࠦ࡮ࡰࡶࠣࡪࡪࡺࡣࡩࠢࡪ࡭ࡹࠦ࡭ࡦࡶࡤࡨࡦࡺࡡࠡ࡫ࡶࠤࡸࡵࡵࡳࡥࡨࠤ࡮ࡹࠠࡵࡻࡳࡩࠥࡵࡦࠡࡣࡵࡶࡦࡿࠠࡢࡰࡧࠤ࡮ࡺࠧࡴࠢࡨࡰࡪࡳࡥ࡯ࡶࡶࠤࡦࡸࡥࠡࡱࡩࠤࡹࡿࡰࡦࠢࡧ࡭ࡨࡺࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡥࡤࡣࡸࡷࡪࠦࡩ࡯ࠢࡷ࡬ࡦࡺࠠࡤࡣࡶࡩ࠱ࠦࡵࡴࡧࡵࠤ࡭ࡧࡳࠡࡲࡵࡳࡻ࡯ࡤࡦࡦࠣࡱࡺࡲࡴࡪ࠯ࡵࡩࡵࡵࠠࡴࡱࡸࡶࡨ࡫ࠠࡸ࡫ࡷ࡬ࠥ࡬ࡥࡢࡶࡸࡶࡪࡈࡲࡢࡰࡦ࡬ࠥ࡯࡮ࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠢࠣࠤ⃅")
            source = orchestration_metadata[bstack1111l1_opy_ (u"ࠫࡷࡻ࡮ࡠࡵࡰࡥࡷࡺ࡟ࡴࡧ࡯ࡩࡨࡺࡩࡰࡰࠪ⃆")].get(bstack1111l1_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬ⃇"), [])
            bstack1llll1l111ll_opy_ = isinstance(source, list) and all(isinstance(src, dict) and src is not None for src in source) and len(source) > 0
            if orchestration_metadata[bstack1111l1_opy_ (u"࠭ࡲࡶࡰࡢࡷࡲࡧࡲࡵࡡࡶࡩࡱ࡫ࡣࡵ࡫ࡲࡲࠬ⃈")].get(bstack1111l1_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡤࠨ⃉"), False) and not bstack1llll1l111ll_opy_:
                bstack1llll1l1ll1l_opy_ = bstack11l11l1lll1_opy_(source) # bstack1llll1l111l1_opy_-repo is handled bstack1llll1l1ll11_opy_
            payload = {
                bstack1111l1_opy_ (u"ࠣࡶࡨࡷࡹࡹࠢ⃊"): [{bstack1111l1_opy_ (u"ࠤࡩ࡭ࡱ࡫ࡐࡢࡶ࡫ࠦ⃋"): f} for f in test_files],
                bstack1111l1_opy_ (u"ࠥࡳࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࡖࡸࡷࡧࡴࡦࡩࡼࠦ⃌"): orchestration_strategy,
                bstack1111l1_opy_ (u"ࠦࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡑࡪࡺࡡࡥࡣࡷࡥࠧ⃍"): orchestration_metadata,
                bstack1111l1_opy_ (u"ࠧࡴ࡯ࡥࡧࡌࡲࡩ࡫ࡸࠣ⃎"): int(os.environ.get(bstack1111l1_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡔࡏࡅࡇࡢࡍࡓࡊࡅ࡙ࠤ⃏")) or bstack1111l1_opy_ (u"ࠢ࠱ࠤ⃐")),
                bstack1111l1_opy_ (u"ࠣࡶࡲࡸࡦࡲࡎࡰࡦࡨࡷࠧ⃑"): int(os.environ.get(bstack1111l1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡒࡘࡆࡒ࡟ࡏࡑࡇࡉࡤࡉࡏࡖࡐࡗ⃒ࠦ")) or bstack1111l1_opy_ (u"ࠥ࠵⃓ࠧ")),
                bstack1111l1_opy_ (u"ࠦࡵࡸ࡯࡫ࡧࡦࡸࡓࡧ࡭ࡦࠤ⃔"): self.config.get(bstack1111l1_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪ⃕"), bstack1111l1_opy_ (u"࠭ࠧ⃖")),
                bstack1111l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠥ⃗"): self.config.get(bstack1111l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨ⃘ࠫ"), os.path.basename(os.path.abspath(os.getcwd()))),
                bstack1111l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡓࡷࡱࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸ⃙ࠢ"): os.environ.get(bstack1111l1_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅ࡙ࡎࡒࡄࡠࡔࡘࡒࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠤ⃚"), bstack1111l1_opy_ (u"ࠦࠧ⃛")),
                bstack1111l1_opy_ (u"ࠧ࡮࡯ࡴࡶࡌࡲ࡫ࡵࠢ⃜"): get_host_info(),
                bstack1111l1_opy_ (u"ࠨࡰࡳࡆࡨࡸࡦ࡯࡬ࡴࠤ⃝"): bstack1llll1l1ll1l_opy_
            }
            self.logger.debug(bstack1111l1_opy_ (u"ࠢ࡜ࡵࡳࡰ࡮ࡺࡔࡦࡵࡷࡷࡢࠦࡓࡦࡰࡧ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥ࡬ࡩ࡭ࡧࡶ࠾ࠥࢁࡽࠣ⃞").format(payload))
            response = bstack11l1lllll1l_opy_.bstack1lllll1l11ll_opy_(self.bstack1llll1l11l1l_opy_, payload)
            if response:
                self.bstack1llll1l1l1l1_opy_ = self._1llll1l11ll1_opy_(response)
                self.logger.debug(bstack1111l1_opy_ (u"ࠣ࡝ࡶࡴࡱ࡯ࡴࡕࡧࡶࡸࡸࡣࠠࡔࡲ࡯࡭ࡹࠦࡴࡦࡵࡷࡷࠥࡸࡥࡴࡲࡲࡲࡸ࡫࠺ࠡࡽࢀࠦ⃟").format(self.bstack1llll1l1l1l1_opy_))
            else:
                self.logger.error(bstack1111l1_opy_ (u"ࠤ࡞ࡷࡵࡲࡩࡵࡖࡨࡷࡹࡹ࡝ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤ࡬࡫ࡴࠡࡵࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡲࡦࡵࡳࡳࡳࡹࡥ࠯ࠤ⃠"))
        except Exception as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠥ࡟ࡸࡶ࡬ࡪࡶࡗࡩࡸࡺࡳ࡞ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡵࡨࡲࡩ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࡸࡀ࠺ࠡࡽࢀࠦ⃡").format(e))
    def _1llll1l11ll1_opy_(self, response):
        bstack1111l1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡒࡵࡳࡨ࡫ࡳࡴࡧࡶࠤࡹ࡮ࡥࠡࡵࡳࡰ࡮ࡺࠠࡵࡧࡶࡸࡸࠦࡁࡑࡋࠣࡶࡪࡹࡰࡰࡰࡶࡩࠥࡧ࡮ࡥࠢࡨࡼࡹࡸࡡࡤࡶࡶࠤࡷ࡫࡬ࡦࡸࡤࡲࡹࠦࡦࡪࡧ࡯ࡨࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦ⃢")
        bstack1l111ll1ll_opy_ = {}
        bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࠨ⃣")] = response.get(bstack1111l1_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࠢ⃤"), self.bstack1llll1ll1111_opy_)
        bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡊࡰࡷࡩࡷࡼࡡ࡭ࠤ⃥")] = response.get(bstack1111l1_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡋࡱࡸࡪࡸࡶࡢ࡮⃦ࠥ"), self.bstack1llll1l11lll_opy_)
        bstack1llll1l1l1ll_opy_ = response.get(bstack1111l1_opy_ (u"ࠤࡵࡩࡸࡻ࡬ࡵࡗࡵࡰࠧ⃧"))
        bstack1llll1l11111_opy_ = response.get(bstack1111l1_opy_ (u"ࠥࡸ࡮ࡳࡥࡰࡷࡷ࡙ࡷࡲ⃨ࠢ"))
        if bstack1llll1l1l1ll_opy_:
            bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷ࡙ࡷࡲࠢ⃩")] = bstack1llll1l1l1ll_opy_.split(bstack11l1l1l111l_opy_ + bstack1111l1_opy_ (u"ࠧ࠵⃪ࠢ"))[1] if bstack11l1l1l111l_opy_ + bstack1111l1_opy_ (u"ࠨ࠯⃫ࠣ") in bstack1llll1l1l1ll_opy_ else bstack1llll1l1l1ll_opy_
        else:
            bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࡕࡳ࡮⃬ࠥ")] = None
        if bstack1llll1l11111_opy_:
            bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࡗࡵࡰ⃭ࠧ")] = bstack1llll1l11111_opy_.split(bstack11l1l1l111l_opy_ + bstack1111l1_opy_ (u"ࠤ࠲⃮ࠦ"))[1] if bstack11l1l1l111l_opy_ + bstack1111l1_opy_ (u"ࠥ࠳⃯ࠧ") in bstack1llll1l11111_opy_ else bstack1llll1l11111_opy_
        else:
            bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸ࡚ࡸ࡬ࠣ⃰")] = None
        if (
            response.get(bstack1111l1_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࠨ⃱")) is None or
            response.get(bstack1111l1_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࡉ࡯ࡶࡨࡶࡻࡧ࡬ࠣ⃲")) is None or
            response.get(bstack1111l1_opy_ (u"ࠢࡵ࡫ࡰࡩࡴࡻࡴࡖࡴ࡯ࠦ⃳")) is None or
            response.get(bstack1111l1_opy_ (u"ࠣࡴࡨࡷࡺࡲࡴࡖࡴ࡯ࠦ⃴")) is None
        ):
            self.logger.debug(bstack1111l1_opy_ (u"ࠤ࡞ࡴࡷࡵࡣࡦࡵࡶࡣࡸࡶ࡬ࡪࡶࡢࡸࡪࡹࡴࡴࡡࡵࡩࡸࡶ࡯࡯ࡵࡨࡡࠥࡘࡥࡤࡧ࡬ࡺࡪࡪࠠ࡯ࡷ࡯ࡰࠥࡼࡡ࡭ࡷࡨࠬࡸ࠯ࠠࡧࡱࡵࠤࡸࡵ࡭ࡦࠢࡤࡸࡹࡸࡩࡣࡷࡷࡩࡸࠦࡩ࡯ࠢࡶࡴࡱ࡯ࡴࠡࡶࡨࡷࡹࡹࠠࡂࡒࡌࠤࡷ࡫ࡳࡱࡱࡱࡷࡪࠨ⃵"))
        return bstack1l111ll1ll_opy_
    def bstack111l111l11l_opy_(self):
        if not self.bstack1llll1l1l1l1_opy_:
            self.logger.error(bstack1111l1_opy_ (u"ࠥ࡟࡬࡫ࡴࡐࡴࡧࡩࡷ࡫ࡤࡕࡧࡶࡸࡋ࡯࡬ࡦࡵࡠࠤࡓࡵࠠࡳࡧࡴࡹࡪࡹࡴࠡࡦࡤࡸࡦࠦࡡࡷࡣ࡬ࡰࡦࡨ࡬ࡦࠢࡷࡳࠥ࡬ࡥࡵࡥ࡫ࠤࡴࡸࡤࡦࡴࡨࡨࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴ࠰ࠥ⃶"))
            return None
        bstack1llll1l1l11l_opy_ = None
        test_files = []
        bstack1llll1l1l111_opy_ = int(time.time() * 1000) # bstack1llll1l1llll_opy_ sec
        bstack1llll1l11l11_opy_ = int(self.bstack1llll1l1l1l1_opy_.get(bstack1111l1_opy_ (u"ࠦࡹ࡯࡭ࡦࡱࡸࡸࡎࡴࡴࡦࡴࡹࡥࡱࠨ⃷"), self.bstack1llll1l11lll_opy_))
        bstack1llll1l1lll1_opy_ = int(self.bstack1llll1l1l1l1_opy_.get(bstack1111l1_opy_ (u"ࠧࡺࡩ࡮ࡧࡲࡹࡹࠨ⃸"), self.bstack1llll1ll1111_opy_)) * 1000
        bstack1llll1l11111_opy_ = self.bstack1llll1l1l1l1_opy_.get(bstack1111l1_opy_ (u"ࠨࡴࡪ࡯ࡨࡳࡺࡺࡕࡳ࡮ࠥ⃹"), None)
        bstack1llll1l1l1ll_opy_ = self.bstack1llll1l1l1l1_opy_.get(bstack1111l1_opy_ (u"ࠢࡳࡧࡶࡹࡱࡺࡕࡳ࡮ࠥ⃺"), None)
        if bstack1llll1l1l1ll_opy_ is None and bstack1llll1l11111_opy_ is None:
            return None
        try:
            while bstack1llll1l1l1ll_opy_ and (time.time() * 1000 - bstack1llll1l1l111_opy_) < bstack1llll1l1lll1_opy_:
                response = bstack11l1lllll1l_opy_.bstack1lllll11ll11_opy_(bstack1llll1l1l1ll_opy_, {})
                if response and response.get(bstack1111l1_opy_ (u"ࠣࡶࡨࡷࡹࡹࠢ⃻")):
                    bstack1llll1l1l11l_opy_ = response.get(bstack1111l1_opy_ (u"ࠤࡷࡩࡸࡺࡳࠣ⃼"))
                self.bstack1llll1l1111l_opy_ += 1
                if bstack1llll1l1l11l_opy_:
                    break
                time.sleep(bstack1llll1l11l11_opy_)
                self.logger.debug(bstack1111l1_opy_ (u"ࠥ࡟࡬࡫ࡴࡐࡴࡧࡩࡷ࡫ࡤࡕࡧࡶࡸࡋ࡯࡬ࡦࡵࡠࠤࡋ࡫ࡴࡤࡪ࡬ࡲ࡬ࠦ࡯ࡳࡦࡨࡶࡪࡪࠠࡵࡧࡶࡸࡸࠦࡦࡳࡱࡰࠤࡷ࡫ࡳࡶ࡮ࡷࠤ࡚ࡘࡌࠡࡣࡩࡸࡪࡸࠠࡸࡣ࡬ࡸ࡮ࡴࡧࠡࡨࡲࡶࠥࢁࡽࠡࡵࡨࡧࡴࡴࡤࡴ࠰ࠥ⃽").format(bstack1llll1l11l11_opy_))
            if bstack1llll1l11111_opy_ and not bstack1llll1l1l11l_opy_:
                self.logger.debug(bstack1111l1_opy_ (u"ࠦࡠ࡭ࡥࡵࡑࡵࡨࡪࡸࡥࡥࡖࡨࡷࡹࡌࡩ࡭ࡧࡶࡡࠥࡌࡥࡵࡥ࡫࡭ࡳ࡭ࠠࡰࡴࡧࡩࡷ࡫ࡤࠡࡶࡨࡷࡹࡹࠠࡧࡴࡲࡱࠥࡺࡩ࡮ࡧࡲࡹࡹࠦࡕࡓࡎࠥ⃾"))
                response = bstack11l1lllll1l_opy_.bstack1lllll11ll11_opy_(bstack1llll1l11111_opy_, {})
                if response and response.get(bstack1111l1_opy_ (u"ࠧࡺࡥࡴࡶࡶࠦ⃿")):
                    bstack1llll1l1l11l_opy_ = response.get(bstack1111l1_opy_ (u"ࠨࡴࡦࡵࡷࡷࠧ℀"))
            if bstack1llll1l1l11l_opy_ and len(bstack1llll1l1l11l_opy_) > 0:
                for bstack111l1ll1l1_opy_ in bstack1llll1l1l11l_opy_:
                    file_path = bstack111l1ll1l1_opy_.get(bstack1111l1_opy_ (u"ࠢࡧ࡫࡯ࡩࡕࡧࡴࡩࠤ℁"))
                    if file_path:
                        test_files.append(file_path)
            if not bstack1llll1l1l11l_opy_:
                return None
            self.logger.debug(bstack1111l1_opy_ (u"ࠣ࡝ࡪࡩࡹࡕࡲࡥࡧࡵࡩࡩ࡚ࡥࡴࡶࡉ࡭ࡱ࡫ࡳ࡞ࠢࡒࡶࡩ࡫ࡲࡦࡦࠣࡸࡪࡹࡴࠡࡨ࡬ࡰࡪࡹࠠࡳࡧࡦࡩ࡮ࡼࡥࡥ࠼ࠣࡿࢂࠨℂ").format(test_files))
            return test_files
        except Exception as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠤ࡞࡫ࡪࡺࡏࡳࡦࡨࡶࡪࡪࡔࡦࡵࡷࡊ࡮ࡲࡥࡴ࡟ࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡩࡩࡹࡩࡨࡪࡰࡪࠤࡴࡸࡤࡦࡴࡨࡨࠥࡺࡥࡴࡶࠣࡪ࡮ࡲࡥࡴ࠼ࠣࡿࢂࠨ℃").format(e))
            return None
    def bstack111l111l111_opy_(self):
        bstack1111l1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳࠡࡶ࡫ࡩࠥࡩ࡯ࡶࡰࡷࠤࡴ࡬ࠠࡴࡲ࡯࡭ࡹࠦࡴࡦࡵࡷࡷࠥࡇࡐࡊࠢࡦࡥࡱࡲࡳࠡ࡯ࡤࡨࡪ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦ℄")
        return self.bstack1llll1l1111l_opy_