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
import json
import logging
logger = logging.getLogger(__name__)
class BrowserStackSdk:
    def get_current_platform():
        bstack1l11llll1_opy_ = {}
        bstack111lll11l1_opy_ = os.environ.get(bstack1111l1_opy_ (u"ࠨࡅࡘࡖࡗࡋࡎࡕࡡࡓࡐࡆ࡚ࡆࡐࡔࡐࡣࡉࡇࡔࡂ༙ࠩ"), bstack1111l1_opy_ (u"ࠩࠪ༚"))
        if not bstack111lll11l1_opy_:
            return bstack1l11llll1_opy_
        try:
            bstack111lll111l_opy_ = json.loads(bstack111lll11l1_opy_)
            if bstack1111l1_opy_ (u"ࠥࡳࡸࠨ༛") in bstack111lll111l_opy_:
                bstack1l11llll1_opy_[bstack1111l1_opy_ (u"ࠦࡴࡹࠢ༜")] = bstack111lll111l_opy_[bstack1111l1_opy_ (u"ࠧࡵࡳࠣ༝")]
            if bstack1111l1_opy_ (u"ࠨ࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠥ༞") in bstack111lll111l_opy_ or bstack1111l1_opy_ (u"ࠢࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠥ༟") in bstack111lll111l_opy_:
                bstack1l11llll1_opy_[bstack1111l1_opy_ (u"ࠣࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠦ༠")] = bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠤࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳࠨ༡"), bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠥࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳࠨ༢")))
            if bstack1111l1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࠧ༣") in bstack111lll111l_opy_ or bstack1111l1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠥ༤") in bstack111lll111l_opy_:
                bstack1l11llll1_opy_[bstack1111l1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠦ༥")] = bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࠣ༦"), bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠣࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪࠨ༧")))
            if bstack1111l1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠦ༨") in bstack111lll111l_opy_ or bstack1111l1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠦ༩") in bstack111lll111l_opy_:
                bstack1l11llll1_opy_[bstack1111l1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠧ༪")] = bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠧࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠢ༫"), bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠨࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠢ༬")))
            if bstack1111l1_opy_ (u"ࠢࡥࡧࡹ࡭ࡨ࡫ࠢ༭") in bstack111lll111l_opy_ or bstack1111l1_opy_ (u"ࠣࡦࡨࡺ࡮ࡩࡥࡏࡣࡰࡩࠧ༮") in bstack111lll111l_opy_:
                bstack1l11llll1_opy_[bstack1111l1_opy_ (u"ࠤࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪࠨ༯")] = bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠥࡨࡪࡼࡩࡤࡧࠥ༰"), bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠦࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠣ༱")))
            if bstack1111l1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࠢ༲") in bstack111lll111l_opy_ or bstack1111l1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠧ༳") in bstack111lll111l_opy_:
                bstack1l11llll1_opy_[bstack1111l1_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪࠨ༴")] = bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠣࡲ࡯ࡥࡹ࡬࡯ࡳ࡯༵ࠥ"), bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠤࡳࡰࡦࡺࡦࡰࡴࡰࡒࡦࡳࡥࠣ༶")))
            if bstack1111l1_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡤࡼࡥࡳࡵ࡬ࡳࡳࠨ༷") in bstack111lll111l_opy_ or bstack1111l1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳࠨ༸") in bstack111lll111l_opy_:
                bstack1l11llll1_opy_[bstack1111l1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴ༹ࠢ")] = bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠨࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠤ༺"), bstack111lll111l_opy_.get(bstack1111l1_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤ༻")))
            if bstack1111l1_opy_ (u"ࠣࡥࡸࡷࡹࡵ࡭ࡗࡣࡵ࡭ࡦࡨ࡬ࡦࡵࠥ༼") in bstack111lll111l_opy_:
                bstack1l11llll1_opy_[bstack1111l1_opy_ (u"ࠤࡦࡹࡸࡺ࡯࡮ࡘࡤࡶ࡮ࡧࡢ࡭ࡧࡶࠦ༽")] = bstack111lll111l_opy_[bstack1111l1_opy_ (u"ࠥࡧࡺࡹࡴࡰ࡯࡙ࡥࡷ࡯ࡡࡣ࡮ࡨࡷࠧ༾")]
        except Exception as error:
            logger.error(bstack1111l1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡸࡪ࡬ࡰࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡤࡷࡵࡶࡪࡴࡴࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡨࡦࡺࡡ࠻ࠢࠥ༿") +  str(error))
        return bstack1l11llll1_opy_