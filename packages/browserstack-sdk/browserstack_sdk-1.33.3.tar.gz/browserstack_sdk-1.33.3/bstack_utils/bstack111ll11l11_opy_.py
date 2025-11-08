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
import json
import logging
import os
import datetime
import threading
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.helper import bstack11ll11lllll_opy_, bstack11ll1ll111l_opy_, bstack111llll11_opy_, error_handler, bstack111llllll11_opy_, bstack111ll1l11l1_opy_, bstack11l11111l11_opy_, bstack11l1l1111l_opy_, bstack1l1ll111l_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1lllll1llll1_opy_ import bstack1lllll1lll1l_opy_
import bstack_utils.bstack11l1lll11l_opy_ as bstack11ll11l11l_opy_
from bstack_utils.bstack111ll1lll1_opy_ import bstack1ll1111ll1_opy_
import bstack_utils.accessibility as bstack1ll1ll1l11_opy_
from bstack_utils.bstack1l1l11l11_opy_ import bstack1l1l11l11_opy_
from bstack_utils.bstack111l1ll1l1_opy_ import bstack1111llll1l_opy_
from bstack_utils.constants import bstack1l11l11l1l_opy_
bstack1llll11l1l1l_opy_ = bstack1111l1_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡩ࡯࡭࡮ࡨࡧࡹࡵࡲ࠮ࡱࡥࡷࡪࡸࡶࡢࡤ࡬ࡰ࡮ࡺࡹ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰࠫ℅")
logger = logging.getLogger(__name__)
class bstack1ll11111_opy_:
    bstack1lllll1llll1_opy_ = None
    bs_config = None
    bstack11ll111l1l_opy_ = None
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack11l1l1l1lll_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def launch(cls, bs_config, bstack11ll111l1l_opy_):
        cls.bs_config = bs_config
        cls.bstack11ll111l1l_opy_ = bstack11ll111l1l_opy_
        try:
            cls.bstack1llll1111lll_opy_()
            bstack11ll11lll1l_opy_ = bstack11ll11lllll_opy_(bs_config)
            bstack11ll1l11111_opy_ = bstack11ll1ll111l_opy_(bs_config)
            data = bstack11ll11l11l_opy_.bstack1llll11lll11_opy_(bs_config, bstack11ll111l1l_opy_)
            config = {
                bstack1111l1_opy_ (u"ࠬࡧࡵࡵࡪࠪ℆"): (bstack11ll11lll1l_opy_, bstack11ll1l11111_opy_),
                bstack1111l1_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧℇ"): cls.default_headers()
            }
            response = bstack111llll11_opy_(bstack1111l1_opy_ (u"ࠧࡑࡑࡖࡘࠬ℈"), cls.request_url(bstack1111l1_opy_ (u"ࠨࡣࡳ࡭࠴ࡼ࠲࠰ࡤࡸ࡭ࡱࡪࡳࠨ℉")), data, config)
            if response.status_code != 200:
                bstack1l111ll1ll_opy_ = response.json()
                if bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪℊ")] == False:
                    cls.bstack1llll11lll1l_opy_(bstack1l111ll1ll_opy_)
                    return
                cls.bstack1llll11l11l1_opy_(bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪℋ")])
                cls.bstack1llll11l111l_opy_(bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫℌ")])
                return None
            bstack1llll11l11ll_opy_ = cls.bstack1llll111l1l1_opy_(response)
            return bstack1llll11l11ll_opy_, response.json()
        except Exception as error:
            logger.error(bstack1111l1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡥࡹ࡮ࡲࡤࠡࡨࡲࡶ࡚ࠥࡥࡴࡶࡋࡹࡧࡀࠠࡼࡿࠥℍ").format(str(error)))
            return None
    @classmethod
    @error_handler(class_method=True)
    def stop(cls, bstack1llll11l1ll1_opy_=None):
        if not bstack1ll1111ll1_opy_.on() and not bstack1ll1ll1l11_opy_.on():
            return
        if os.environ.get(bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪℎ")) == bstack1111l1_opy_ (u"ࠢ࡯ࡷ࡯ࡰࠧℏ") or os.environ.get(bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ℐ")) == bstack1111l1_opy_ (u"ࠤࡱࡹࡱࡲࠢℑ"):
            logger.error(bstack1111l1_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡸࡴࡶࠠࡣࡷ࡬ࡰࡩࠦࡲࡦࡳࡸࡩࡸࡺࠠࡵࡱࠣࡘࡪࡹࡴࡉࡷࡥ࠾ࠥࡓࡩࡴࡵ࡬ࡲ࡬ࠦࡡࡶࡶ࡫ࡩࡳࡺࡩࡤࡣࡷ࡭ࡴࡴࠠࡵࡱ࡮ࡩࡳ࠭ℒ"))
            return {
                bstack1111l1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫℓ"): bstack1111l1_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ℔"),
                bstack1111l1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧℕ"): bstack1111l1_opy_ (u"ࠧࡕࡱ࡮ࡩࡳ࠵ࡢࡶ࡫࡯ࡨࡎࡊࠠࡪࡵࠣࡹࡳࡪࡥࡧ࡫ࡱࡩࡩ࠲ࠠࡣࡷ࡬ࡰࡩࠦࡣࡳࡧࡤࡸ࡮ࡵ࡮ࠡ࡯࡬࡫࡭ࡺࠠࡩࡣࡹࡩࠥ࡬ࡡࡪ࡮ࡨࡨࠬ№")
            }
        try:
            cls.bstack1lllll1llll1_opy_.shutdown()
            data = {
                bstack1111l1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭℗"): bstack11l1l1111l_opy_()
            }
            if not bstack1llll11l1ll1_opy_ is None:
                data[bstack1111l1_opy_ (u"ࠩࡩ࡭ࡳ࡯ࡳࡩࡧࡧࡣࡲ࡫ࡴࡢࡦࡤࡸࡦ࠭℘")] = [{
                    bstack1111l1_opy_ (u"ࠪࡶࡪࡧࡳࡰࡰࠪℙ"): bstack1111l1_opy_ (u"ࠫࡺࡹࡥࡳࡡ࡮࡭ࡱࡲࡥࡥࠩℚ"),
                    bstack1111l1_opy_ (u"ࠬࡹࡩࡨࡰࡤࡰࠬℛ"): bstack1llll11l1ll1_opy_
                }]
            config = {
                bstack1111l1_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧℜ"): cls.default_headers()
            }
            bstack11ll1111ll1_opy_ = bstack1111l1_opy_ (u"ࠧࡢࡲ࡬࠳ࡻ࠷࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿ࠲ࡷࡹࡵࡰࠨℝ").format(os.environ[bstack1111l1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉࠨ℞")])
            bstack1llll11ll1ll_opy_ = cls.request_url(bstack11ll1111ll1_opy_)
            response = bstack111llll11_opy_(bstack1111l1_opy_ (u"ࠩࡓ࡙࡙࠭℟"), bstack1llll11ll1ll_opy_, data, config)
            if not response.ok:
                raise Exception(bstack1111l1_opy_ (u"ࠥࡗࡹࡵࡰࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡱࡳࡹࠦ࡯࡬ࠤ℠"))
        except Exception as error:
            logger.error(bstack1111l1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡷࡹࡵࡰࠡࡤࡸ࡭ࡱࡪࠠࡳࡧࡴࡹࡪࡹࡴࠡࡶࡲࠤ࡙࡫ࡳࡵࡊࡸࡦ࠿ࡀࠠࠣ℡") + str(error))
            return {
                bstack1111l1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ™"): bstack1111l1_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ℣"),
                bstack1111l1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨℤ"): str(error)
            }
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll111l1l1_opy_(cls, response):
        bstack1l111ll1ll_opy_ = response.json() if not isinstance(response, dict) else response
        bstack1llll11l11ll_opy_ = {}
        if bstack1l111ll1ll_opy_.get(bstack1111l1_opy_ (u"ࠨ࡬ࡺࡸࠬ℥")) is None:
            os.environ[bstack1111l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭Ω")] = bstack1111l1_opy_ (u"ࠪࡲࡺࡲ࡬ࠨ℧")
        else:
            os.environ[bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨℨ")] = bstack1l111ll1ll_opy_.get(bstack1111l1_opy_ (u"ࠬࡰࡷࡵࠩ℩"), bstack1111l1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫK"))
        os.environ[bstack1111l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡖࡗࡌࡈࠬÅ")] = bstack1l111ll1ll_opy_.get(bstack1111l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪℬ"), bstack1111l1_opy_ (u"ࠩࡱࡹࡱࡲࠧℭ"))
        logger.info(bstack1111l1_opy_ (u"ࠪࡘࡪࡹࡴࡩࡷࡥࠤࡸࡺࡡࡳࡶࡨࡨࠥࡽࡩࡵࡪࠣ࡭ࡩࡀࠠࠨ℮") + os.getenv(bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩℯ")));
        if bstack1ll1111ll1_opy_.bstack1llll11ll11l_opy_(cls.bs_config, cls.bstack11ll111l1l_opy_.get(bstack1111l1_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡷࡶࡩࡩ࠭ℰ"), bstack1111l1_opy_ (u"࠭ࠧℱ"))) is True:
            bstack1lllll11l1ll_opy_, build_hashed_id, bstack1llll111l11l_opy_ = cls.bstack1llll11l1111_opy_(bstack1l111ll1ll_opy_)
            if bstack1lllll11l1ll_opy_ != None and build_hashed_id != None:
                bstack1llll11l11ll_opy_[bstack1111l1_opy_ (u"ࠧࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠧℲ")] = {
                    bstack1111l1_opy_ (u"ࠨ࡬ࡺࡸࡤࡺ࡯࡬ࡧࡱࠫℳ"): bstack1lllll11l1ll_opy_,
                    bstack1111l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠࡪࡤࡷ࡭࡫ࡤࡠ࡫ࡧࠫℴ"): build_hashed_id,
                    bstack1111l1_opy_ (u"ࠪࡥࡱࡲ࡯ࡸࡡࡶࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹࡹࠧℵ"): bstack1llll111l11l_opy_
                }
            else:
                bstack1llll11l11ll_opy_[bstack1111l1_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫℶ")] = {}
        else:
            bstack1llll11l11ll_opy_[bstack1111l1_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬℷ")] = {}
        bstack1llll11llll1_opy_, build_hashed_id = cls.bstack1llll11ll111_opy_(bstack1l111ll1ll_opy_)
        if bstack1llll11llll1_opy_ != None and build_hashed_id != None:
            bstack1llll11l11ll_opy_[bstack1111l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ℸ")] = {
                bstack1111l1_opy_ (u"ࠧࡢࡷࡷ࡬ࡤࡺ࡯࡬ࡧࡱࠫℹ"): bstack1llll11llll1_opy_,
                bstack1111l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪ℺"): build_hashed_id,
            }
        else:
            bstack1llll11l11ll_opy_[bstack1111l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩ℻")] = {}
        if bstack1llll11l11ll_opy_[bstack1111l1_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪℼ")].get(bstack1111l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭ℽ")) != None or bstack1llll11l11ll_opy_[bstack1111l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬℾ")].get(bstack1111l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨℿ")) != None:
            cls.bstack1llll11l1lll_opy_(bstack1l111ll1ll_opy_.get(bstack1111l1_opy_ (u"ࠧ࡫ࡹࡷࠫ⅀")), bstack1l111ll1ll_opy_.get(bstack1111l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪ⅁")))
        return bstack1llll11l11ll_opy_
    @classmethod
    def bstack1llll11l1111_opy_(cls, bstack1l111ll1ll_opy_):
        if bstack1l111ll1ll_opy_.get(bstack1111l1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ⅂")) == None:
            cls.bstack1llll11l11l1_opy_()
            return [None, None, None]
        if bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ⅃")][bstack1111l1_opy_ (u"ࠫࡸࡻࡣࡤࡧࡶࡷࠬ⅄")] != True:
            cls.bstack1llll11l11l1_opy_(bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠬࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠬⅅ")])
            return [None, None, None]
        logger.debug(bstack1111l1_opy_ (u"࠭ࡻࡾࠢࡅࡹ࡮ࡲࡤࠡࡥࡵࡩࡦࡺࡩࡰࡰࠣࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲࠡࠨⅆ").format(bstack1l11l11l1l_opy_))
        os.environ[bstack1111l1_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡇ࡛ࡉࡍࡆࡢࡇࡔࡓࡐࡍࡇࡗࡉࡉ࠭ⅇ")] = bstack1111l1_opy_ (u"ࠨࡶࡵࡹࡪ࠭ⅈ")
        if bstack1l111ll1ll_opy_.get(bstack1111l1_opy_ (u"ࠩ࡭ࡻࡹ࠭ⅉ")):
            os.environ[bstack1111l1_opy_ (u"ࠪࡇࡗࡋࡄࡆࡐࡗࡍࡆࡒࡓࡠࡈࡒࡖࡤࡉࡒࡂࡕࡋࡣࡗࡋࡐࡐࡔࡗࡍࡓࡍࠧ⅊")] = json.dumps({
                bstack1111l1_opy_ (u"ࠫࡺࡹࡥࡳࡰࡤࡱࡪ࠭⅋"): bstack11ll11lllll_opy_(cls.bs_config),
                bstack1111l1_opy_ (u"ࠬࡶࡡࡴࡵࡺࡳࡷࡪࠧ⅌"): bstack11ll1ll111l_opy_(cls.bs_config)
            })
        if bstack1l111ll1ll_opy_.get(bstack1111l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡤ࡮ࡡࡴࡪࡨࡨࡤ࡯ࡤࠨ⅍")):
            os.environ[bstack1111l1_opy_ (u"ࠧࡃࡕࡢࡘࡊ࡙ࡔࡐࡒࡖࡣࡇ࡛ࡉࡍࡆࡢࡌࡆ࡙ࡈࡆࡆࡢࡍࡉ࠭ⅎ")] = bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪ࡟ࡩࡣࡶ࡬ࡪࡪ࡟ࡪࡦࠪ⅏")]
        if bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠩࡲࡦࡸ࡫ࡲࡷࡣࡥ࡭ࡱ࡯ࡴࡺࠩ⅐")].get(bstack1111l1_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫ⅑"), {}).get(bstack1111l1_opy_ (u"ࠫࡦࡲ࡬ࡰࡹࡢࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡳࠨ⅒")):
            os.environ[bstack1111l1_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡄࡐࡑࡕࡗࡠࡕࡆࡖࡊࡋࡎࡔࡊࡒࡘࡘ࠭⅓")] = str(bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭⅔")][bstack1111l1_opy_ (u"ࠧࡰࡲࡷ࡭ࡴࡴࡳࠨ⅕")][bstack1111l1_opy_ (u"ࠨࡣ࡯ࡰࡴࡽ࡟ࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࡷࠬ⅖")])
        else:
            os.environ[bstack1111l1_opy_ (u"ࠩࡅࡗࡤ࡚ࡅࡔࡖࡒࡔࡘࡥࡁࡍࡎࡒ࡛ࡤ࡙ࡃࡓࡇࡈࡒࡘࡎࡏࡕࡕࠪ⅗")] = bstack1111l1_opy_ (u"ࠥࡲࡺࡲ࡬ࠣ⅘")
        return [bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠫ࡯ࡽࡴࠨ⅙")], bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ⅚")], os.environ[bstack1111l1_opy_ (u"࠭ࡂࡔࡡࡗࡉࡘ࡚ࡏࡑࡕࡢࡅࡑࡒࡏࡘࡡࡖࡇࡗࡋࡅࡏࡕࡋࡓ࡙࡙ࠧ⅛")]]
    @classmethod
    def bstack1llll11ll111_opy_(cls, bstack1l111ll1ll_opy_):
        if bstack1l111ll1ll_opy_.get(bstack1111l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ⅜")) == None:
            cls.bstack1llll11l111l_opy_()
            return [None, None]
        if bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨ⅝")][bstack1111l1_opy_ (u"ࠩࡶࡹࡨࡩࡥࡴࡵࠪ⅞")] != True:
            cls.bstack1llll11l111l_opy_(bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪ⅟")])
            return [None, None]
        if bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫⅠ")].get(bstack1111l1_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡸ࠭Ⅱ")):
            logger.debug(bstack1111l1_opy_ (u"࠭ࡔࡦࡵࡷࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡇࡻࡩ࡭ࡦࠣࡧࡷ࡫ࡡࡵ࡫ࡲࡲ࡙ࠥࡵࡤࡥࡨࡷࡸ࡬ࡵ࡭ࠣࠪⅢ"))
            parsed = json.loads(os.getenv(bstack1111l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨⅣ"), bstack1111l1_opy_ (u"ࠨࡽࢀࠫⅤ")))
            capabilities = bstack11ll11l11l_opy_.bstack1llll111lll1_opy_(bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩⅥ")][bstack1111l1_opy_ (u"ࠪࡳࡵࡺࡩࡰࡰࡶࠫⅦ")][bstack1111l1_opy_ (u"ࠫࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪⅧ")], bstack1111l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪⅨ"), bstack1111l1_opy_ (u"࠭ࡶࡢ࡮ࡸࡩࠬⅩ"))
            bstack1llll11llll1_opy_ = capabilities[bstack1111l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡔࡰ࡭ࡨࡲࠬⅪ")]
            os.environ[bstack1111l1_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭Ⅻ")] = bstack1llll11llll1_opy_
            if bstack1111l1_opy_ (u"ࠤࡤࡹࡹࡵ࡭ࡢࡶࡨࠦⅬ") in bstack1l111ll1ll_opy_ and bstack1l111ll1ll_opy_.get(bstack1111l1_opy_ (u"ࠥࡥࡵࡶ࡟ࡢࡷࡷࡳࡲࡧࡴࡦࠤⅭ")) is None:
                parsed[bstack1111l1_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬⅮ")] = capabilities[bstack1111l1_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭Ⅿ")]
            os.environ[bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧⅰ")] = json.dumps(parsed)
            scripts = bstack11ll11l11l_opy_.bstack1llll111lll1_opy_(bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧⅱ")][bstack1111l1_opy_ (u"ࠨࡱࡳࡸ࡮ࡵ࡮ࡴࠩⅲ")][bstack1111l1_opy_ (u"ࠩࡶࡧࡷ࡯ࡰࡵࡵࠪⅳ")], bstack1111l1_opy_ (u"ࠪࡲࡦࡳࡥࠨⅴ"), bstack1111l1_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࠬⅵ"))
            bstack1l1l11l11_opy_.bstack11l11l11l1_opy_(scripts)
            commands = bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬⅶ")][bstack1111l1_opy_ (u"࠭࡯ࡱࡶ࡬ࡳࡳࡹࠧⅷ")][bstack1111l1_opy_ (u"ࠧࡤࡱࡰࡱࡦࡴࡤࡴࡖࡲ࡛ࡷࡧࡰࠨⅸ")].get(bstack1111l1_opy_ (u"ࠨࡥࡲࡱࡲࡧ࡮ࡥࡵࠪⅹ"))
            bstack1l1l11l11_opy_.bstack11ll1l1lll1_opy_(commands)
            bstack11ll11l11ll_opy_ = capabilities.get(bstack1111l1_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧⅺ"))
            bstack1l1l11l11_opy_.bstack11ll111l11l_opy_(bstack11ll11l11ll_opy_)
            bstack1l1l11l11_opy_.store()
        return [bstack1llll11llll1_opy_, bstack1l111ll1ll_opy_[bstack1111l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡫ࡥࡸ࡮ࡥࡥࡡ࡬ࡨࠬⅻ")]]
    @classmethod
    def bstack1llll11l11l1_opy_(cls, response=None):
        os.environ[bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩⅼ")] = bstack1111l1_opy_ (u"ࠬࡴࡵ࡭࡮ࠪⅽ")
        os.environ[bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪⅾ")] = bstack1111l1_opy_ (u"ࠧ࡯ࡷ࡯ࡰࠬⅿ")
        os.environ[bstack1111l1_opy_ (u"ࠨࡄࡖࡣ࡙ࡋࡓࡕࡑࡓࡗࡤࡈࡕࡊࡎࡇࡣࡈࡕࡍࡑࡎࡈࡘࡊࡊࠧↀ")] = bstack1111l1_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨↁ")
        os.environ[bstack1111l1_opy_ (u"ࠪࡆࡘࡥࡔࡆࡕࡗࡓࡕ࡙࡟ࡃࡗࡌࡐࡉࡥࡈࡂࡕࡋࡉࡉࡥࡉࡅࠩↂ")] = bstack1111l1_opy_ (u"ࠦࡳࡻ࡬࡭ࠤↃ")
        os.environ[bstack1111l1_opy_ (u"ࠬࡈࡓࡠࡖࡈࡗ࡙ࡕࡐࡔࡡࡄࡐࡑࡕࡗࡠࡕࡆࡖࡊࡋࡎࡔࡊࡒࡘࡘ࠭ↄ")] = bstack1111l1_opy_ (u"ࠨ࡮ࡶ࡮࡯ࠦↅ")
        cls.bstack1llll11lll1l_opy_(response, bstack1111l1_opy_ (u"ࠢࡰࡤࡶࡩࡷࡼࡡࡣ࡫࡯࡭ࡹࡿࠢↆ"))
        return [None, None, None]
    @classmethod
    def bstack1llll11l111l_opy_(cls, response=None):
        os.environ[bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ↇ")] = bstack1111l1_opy_ (u"ࠩࡱࡹࡱࡲࠧↈ")
        os.environ[bstack1111l1_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨ↉")] = bstack1111l1_opy_ (u"ࠫࡳࡻ࡬࡭ࠩ↊")
        os.environ[bstack1111l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠩ↋")] = bstack1111l1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫ↌")
        cls.bstack1llll11lll1l_opy_(response, bstack1111l1_opy_ (u"ࠢࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠢ↍"))
        return [None, None, None]
    @classmethod
    def bstack1llll11l1lll_opy_(cls, jwt, build_hashed_id):
        os.environ[bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡌ࡚ࡘࠬ↎")] = jwt
        os.environ[bstack1111l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧ↏")] = build_hashed_id
    @classmethod
    def bstack1llll11lll1l_opy_(cls, response=None, product=bstack1111l1_opy_ (u"ࠥࠦ←")):
        if response == None or response.get(bstack1111l1_opy_ (u"ࠫࡪࡸࡲࡰࡴࡶࠫ↑")) == None:
            logger.error(product + bstack1111l1_opy_ (u"ࠧࠦࡂࡶ࡫࡯ࡨࠥࡩࡲࡦࡣࡷ࡭ࡴࡴࠠࡧࡣ࡬ࡰࡪࡪࠢ→"))
            return
        for error in response[bstack1111l1_opy_ (u"࠭ࡥࡳࡴࡲࡶࡸ࠭↓")]:
            bstack11l11l11l1l_opy_ = error[bstack1111l1_opy_ (u"ࠧ࡬ࡧࡼࠫ↔")]
            error_message = error[bstack1111l1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ↕")]
            if error_message:
                if bstack11l11l11l1l_opy_ == bstack1111l1_opy_ (u"ࠤࡈࡖࡗࡕࡒࡠࡃࡆࡇࡊ࡙ࡓࡠࡆࡈࡒࡎࡋࡄࠣ↖"):
                    logger.info(error_message)
                else:
                    logger.error(error_message)
            else:
                logger.error(bstack1111l1_opy_ (u"ࠥࡈࡦࡺࡡࠡࡷࡳࡰࡴࡧࡤࠡࡶࡲࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࠦ↗") + product + bstack1111l1_opy_ (u"ࠦࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡪࡵࡦࠢࡷࡳࠥࡹ࡯࡮ࡧࠣࡩࡷࡸ࡯ࡳࠤ↘"))
    @classmethod
    def bstack1llll1111lll_opy_(cls):
        if cls.bstack1lllll1llll1_opy_ is not None:
            return
        cls.bstack1lllll1llll1_opy_ = bstack1lllll1lll1l_opy_(cls.bstack1llll11ll1l1_opy_)
        cls.bstack1lllll1llll1_opy_.start()
    @classmethod
    def bstack1111llll11_opy_(cls):
        if cls.bstack1lllll1llll1_opy_ is None:
            return
        cls.bstack1lllll1llll1_opy_.shutdown()
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll11ll1l1_opy_(cls, bstack111l1l1111_opy_, event_url=bstack1111l1_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡨࡡࡵࡥ࡫ࠫ↙")):
        config = {
            bstack1111l1_opy_ (u"࠭ࡨࡦࡣࡧࡩࡷࡹࠧ↚"): cls.default_headers()
        }
        logger.debug(bstack1111l1_opy_ (u"ࠢࡱࡱࡶࡸࡤࡪࡡࡵࡣ࠽ࠤࡘ࡫࡮ࡥ࡫ࡱ࡫ࠥࡪࡡࡵࡣࠣࡸࡴࠦࡴࡦࡵࡷ࡬ࡺࡨࠠࡧࡱࡵࠤࡪࡼࡥ࡯ࡶࡶࠤࢀࢃࠢ↛").format(bstack1111l1_opy_ (u"ࠨ࠮ࠣࠫ↜").join([event[bstack1111l1_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭↝")] for event in bstack111l1l1111_opy_])))
        response = bstack111llll11_opy_(bstack1111l1_opy_ (u"ࠪࡔࡔ࡙ࡔࠨ↞"), cls.request_url(event_url), bstack111l1l1111_opy_, config)
        bstack11ll11l1l11_opy_ = response.json()
    @classmethod
    def bstack1l11l1ll11_opy_(cls, bstack111l1l1111_opy_, event_url=bstack1111l1_opy_ (u"ࠫࡦࡶࡩ࠰ࡸ࠴࠳ࡧࡧࡴࡤࡪࠪ↟")):
        logger.debug(bstack1111l1_opy_ (u"ࠧࡹࡥ࡯ࡦࡢࡨࡦࡺࡡ࠻ࠢࡄࡸࡹ࡫࡭ࡱࡶ࡬ࡲ࡬ࠦࡴࡰࠢࡤࡨࡩࠦࡤࡢࡶࡤࠤࡹࡵࠠࡣࡣࡷࡧ࡭ࠦࡷࡪࡶ࡫ࠤࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥ࠻ࠢࡾࢁࠧ↠").format(bstack111l1l1111_opy_[bstack1111l1_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ↡")]))
        if not bstack11ll11l11l_opy_.bstack1llll11lllll_opy_(bstack111l1l1111_opy_[bstack1111l1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ↢")]):
            logger.debug(bstack1111l1_opy_ (u"ࠣࡵࡨࡲࡩࡥࡤࡢࡶࡤ࠾ࠥࡔ࡯ࡵࠢࡤࡨࡩ࡯࡮ࡨࠢࡧࡥࡹࡧࠠࡸ࡫ࡷ࡬ࠥ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦ࠼ࠣࡿࢂࠨ↣").format(bstack111l1l1111_opy_[bstack1111l1_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭↤")]))
            return
        bstack1l1lll1lll_opy_ = bstack11ll11l11l_opy_.bstack1llll111llll_opy_(bstack111l1l1111_opy_[bstack1111l1_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧ↥")], bstack111l1l1111_opy_.get(bstack1111l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳ࠭↦")))
        if bstack1l1lll1lll_opy_ != None:
            if bstack111l1l1111_opy_.get(bstack1111l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴࠧ↧")) != None:
                bstack111l1l1111_opy_[bstack1111l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࠨ↨")][bstack1111l1_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࡠ࡯ࡤࡴࠬ↩")] = bstack1l1lll1lll_opy_
            else:
                bstack111l1l1111_opy_[bstack1111l1_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࡡࡰࡥࡵ࠭↪")] = bstack1l1lll1lll_opy_
        if event_url == bstack1111l1_opy_ (u"ࠩࡤࡴ࡮࠵ࡶ࠲࠱ࡥࡥࡹࡩࡨࠨ↫"):
            cls.bstack1llll1111lll_opy_()
            logger.debug(bstack1111l1_opy_ (u"ࠥࡷࡪࡴࡤࡠࡦࡤࡸࡦࡀࠠࡂࡦࡧ࡭ࡳ࡭ࠠࡥࡣࡷࡥࠥࡺ࡯ࠡࡤࡤࡸࡨ࡮ࠠࡸ࡫ࡷ࡬ࠥ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦ࠼ࠣࡿࢂࠨ↬").format(bstack111l1l1111_opy_[bstack1111l1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ↭")]))
            cls.bstack1lllll1llll1_opy_.add(bstack111l1l1111_opy_)
        elif event_url == bstack1111l1_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࡵࠪ↮"):
            cls.bstack1llll11ll1l1_opy_([bstack111l1l1111_opy_], event_url)
    @classmethod
    @error_handler(class_method=True)
    def bstack11ll111ll_opy_(cls, logs):
        for log in logs:
            bstack1llll111l1ll_opy_ = {
                bstack1111l1_opy_ (u"࠭࡫ࡪࡰࡧࠫ↯"): bstack1111l1_opy_ (u"ࠧࡕࡇࡖࡘࡤࡒࡏࡈࠩ↰"),
                bstack1111l1_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧ↱"): log[bstack1111l1_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨ↲")],
                bstack1111l1_opy_ (u"ࠪࡸ࡮ࡳࡥࡴࡶࡤࡱࡵ࠭↳"): log[bstack1111l1_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧ↴")],
                bstack1111l1_opy_ (u"ࠬ࡮ࡴࡵࡲࡢࡶࡪࡹࡰࡰࡰࡶࡩࠬ↵"): {},
                bstack1111l1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧ↶"): log[bstack1111l1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨ↷")],
            }
            if bstack1111l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ↸") in log:
                bstack1llll111l1ll_opy_[bstack1111l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ↹")] = log[bstack1111l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ↺")]
            elif bstack1111l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ↻") in log:
                bstack1llll111l1ll_opy_[bstack1111l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ↼")] = log[bstack1111l1_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭↽")]
            cls.bstack1l11l1ll11_opy_({
                bstack1111l1_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡴࡺࡲࡨࠫ↾"): bstack1111l1_opy_ (u"ࠨࡎࡲ࡫ࡈࡸࡥࡢࡶࡨࡨࠬ↿"),
                bstack1111l1_opy_ (u"ࠩ࡯ࡳ࡬ࡹࠧ⇀"): [bstack1llll111l1ll_opy_]
            })
    @classmethod
    @error_handler(class_method=True)
    def bstack1llll111ll1l_opy_(cls, steps):
        bstack1llll1111ll1_opy_ = []
        for step in steps:
            bstack1llll111ll11_opy_ = {
                bstack1111l1_opy_ (u"ࠪ࡯࡮ࡴࡤࠨ⇁"): bstack1111l1_opy_ (u"࡙ࠫࡋࡓࡕࡡࡖࡘࡊࡖࠧ⇂"),
                bstack1111l1_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ⇃"): step[bstack1111l1_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬ⇄")],
                bstack1111l1_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪ⇅"): step[bstack1111l1_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫ⇆")],
                bstack1111l1_opy_ (u"ࠩࡰࡩࡸࡹࡡࡨࡧࠪ⇇"): step[bstack1111l1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫ⇈")],
                bstack1111l1_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳ࠭⇉"): step[bstack1111l1_opy_ (u"ࠬࡪࡵࡳࡣࡷ࡭ࡴࡴࠧ⇊")]
            }
            if bstack1111l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭⇋") in step:
                bstack1llll111ll11_opy_[bstack1111l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧ⇌")] = step[bstack1111l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ⇍")]
            elif bstack1111l1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ⇎") in step:
                bstack1llll111ll11_opy_[bstack1111l1_opy_ (u"ࠪ࡬ࡴࡵ࡫ࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⇏")] = step[bstack1111l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ⇐")]
            bstack1llll1111ll1_opy_.append(bstack1llll111ll11_opy_)
        cls.bstack1l11l1ll11_opy_({
            bstack1111l1_opy_ (u"ࠬ࡫ࡶࡦࡰࡷࡣࡹࡿࡰࡦࠩ⇑"): bstack1111l1_opy_ (u"࠭ࡌࡰࡩࡆࡶࡪࡧࡴࡦࡦࠪ⇒"),
            bstack1111l1_opy_ (u"ࠧ࡭ࡱࡪࡷࠬ⇓"): bstack1llll1111ll1_opy_
        })
    @classmethod
    @error_handler(class_method=True)
    @measure(event_name=EVENTS.bstack1llll1ll11_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def bstack1l1ll11111_opy_(cls, screenshot):
        cls.bstack1l11l1ll11_opy_({
            bstack1111l1_opy_ (u"ࠨࡧࡹࡩࡳࡺ࡟ࡵࡻࡳࡩࠬ⇔"): bstack1111l1_opy_ (u"ࠩࡏࡳ࡬ࡉࡲࡦࡣࡷࡩࡩ࠭⇕"),
            bstack1111l1_opy_ (u"ࠪࡰࡴ࡭ࡳࠨ⇖"): [{
                bstack1111l1_opy_ (u"ࠫࡰ࡯࡮ࡥࠩ⇗"): bstack1111l1_opy_ (u"࡚ࠬࡅࡔࡖࡢࡗࡈࡘࡅࡆࡐࡖࡌࡔ࡚ࠧ⇘"),
                bstack1111l1_opy_ (u"࠭ࡴࡪ࡯ࡨࡷࡹࡧ࡭ࡱࠩ⇙"): datetime.datetime.utcnow().isoformat() + bstack1111l1_opy_ (u"࡛ࠧࠩ⇚"),
                bstack1111l1_opy_ (u"ࠨ࡯ࡨࡷࡸࡧࡧࡦࠩ⇛"): screenshot[bstack1111l1_opy_ (u"ࠩ࡬ࡱࡦ࡭ࡥࠨ⇜")],
                bstack1111l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠪ⇝"): screenshot[bstack1111l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ⇞")]
            }]
        }, event_url=bstack1111l1_opy_ (u"ࠬࡧࡰࡪ࠱ࡹ࠵࠴ࡹࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࡵࠪ⇟"))
    @classmethod
    @error_handler(class_method=True)
    def bstack11l1l1l111_opy_(cls, driver):
        current_test_uuid = cls.current_test_uuid()
        if not current_test_uuid:
            return
        cls.bstack1l11l1ll11_opy_({
            bstack1111l1_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ⇠"): bstack1111l1_opy_ (u"ࠧࡄࡄࡗࡗࡪࡹࡳࡪࡱࡱࡇࡷ࡫ࡡࡵࡧࡧࠫ⇡"),
            bstack1111l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࠪ⇢"): {
                bstack1111l1_opy_ (u"ࠤࡸࡹ࡮ࡪࠢ⇣"): cls.current_test_uuid(),
                bstack1111l1_opy_ (u"ࠥ࡭ࡳࡺࡥࡨࡴࡤࡸ࡮ࡵ࡮ࡴࠤ⇤"): cls.bstack111l1llll1_opy_(driver)
            }
        })
    @classmethod
    def bstack111ll1l1ll_opy_(cls, event: str, bstack111l1l1111_opy_: bstack1111llll1l_opy_):
        bstack111l111ll1_opy_ = {
            bstack1111l1_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨ⇥"): event,
            bstack111l1l1111_opy_.bstack111l1111ll_opy_(): bstack111l1l1111_opy_.bstack1111ll1lll_opy_(event)
        }
        cls.bstack1l11l1ll11_opy_(bstack111l111ll1_opy_)
        result = getattr(bstack111l1l1111_opy_, bstack1111l1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ⇦"), None)
        if event == bstack1111l1_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧ⇧"):
            threading.current_thread().bstackTestMeta = {bstack1111l1_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ⇨"): bstack1111l1_opy_ (u"ࠨࡲࡨࡲࡩ࡯࡮ࡨࠩ⇩")}
        elif event == bstack1111l1_opy_ (u"ࠩࡗࡩࡸࡺࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ⇪"):
            threading.current_thread().bstackTestMeta = {bstack1111l1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ⇫"): getattr(result, bstack1111l1_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫ⇬"), bstack1111l1_opy_ (u"ࠬ࠭⇭"))}
    @classmethod
    def on(cls):
        if (os.environ.get(bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ⇮"), None) is None or os.environ[bstack1111l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ⇯")] == bstack1111l1_opy_ (u"ࠣࡰࡸࡰࡱࠨ⇰")) and (os.environ.get(bstack1111l1_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧ⇱"), None) is None or os.environ[bstack1111l1_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨ⇲")] == bstack1111l1_opy_ (u"ࠦࡳࡻ࡬࡭ࠤ⇳")):
            return False
        return True
    @staticmethod
    def bstack1llll111l111_opy_(func):
        def wrap(*args, **kwargs):
            if bstack1ll11111_opy_.on():
                return func(*args, **kwargs)
            return
        return wrap
    @staticmethod
    def default_headers():
        headers = {
            bstack1111l1_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡔࡺࡲࡨࠫ⇴"): bstack1111l1_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩ⇵"),
            bstack1111l1_opy_ (u"࡙ࠧ࠯ࡅࡗ࡙ࡇࡃࡌ࠯ࡗࡉࡘ࡚ࡏࡑࡕࠪ⇶"): bstack1111l1_opy_ (u"ࠨࡶࡵࡹࡪ࠭⇷")
        }
        if os.environ.get(bstack1111l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭⇸"), None):
            headers[bstack1111l1_opy_ (u"ࠪࡅࡺࡺࡨࡰࡴ࡬ࡾࡦࡺࡩࡰࡰࠪ⇹")] = bstack1111l1_opy_ (u"ࠫࡇ࡫ࡡࡳࡧࡵࠤࢀࢃࠧ⇺").format(os.environ[bstack1111l1_opy_ (u"ࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡊࡘࡆࡤࡐࡗࡕࠤ⇻")])
        return headers
    @staticmethod
    def request_url(url):
        return bstack1111l1_opy_ (u"࠭ࡻࡾ࠱ࡾࢁࠬ⇼").format(bstack1llll11l1l1l_opy_, url)
    @staticmethod
    def current_test_uuid():
        return getattr(threading.current_thread(), bstack1111l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡶࡨࡷࡹࡥࡵࡶ࡫ࡧࠫ⇽"), None)
    @staticmethod
    def bstack111l1llll1_opy_(driver):
        return {
            bstack111llllll11_opy_(): bstack111ll1l11l1_opy_(driver)
        }
    @staticmethod
    def bstack1llll11l1l11_opy_(exception_info, report):
        return [{bstack1111l1_opy_ (u"ࠨࡤࡤࡧࡰࡺࡲࡢࡥࡨࠫ⇾"): [exception_info.exconly(), report.longreprtext]}]
    @staticmethod
    def bstack11111111l1_opy_(typename):
        if bstack1111l1_opy_ (u"ࠤࡄࡷࡸ࡫ࡲࡵ࡫ࡲࡲࠧ⇿") in typename:
            return bstack1111l1_opy_ (u"ࠥࡅࡸࡹࡥࡳࡶ࡬ࡳࡳࡋࡲࡳࡱࡵࠦ∀")
        return bstack1111l1_opy_ (u"࡚ࠦࡴࡨࡢࡰࡧࡰࡪࡪࡅࡳࡴࡲࡶࠧ∁")