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
import requests
from urllib.parse import urljoin, urlencode
from datetime import datetime
import os
import logging
import json
from bstack_utils.constants import bstack11l1l1l111l_opy_
logger = logging.getLogger(__name__)
class bstack11l1lllll1l_opy_:
    @staticmethod
    def results(builder,params=None):
        bstack1lllll11ll1l_opy_ = urljoin(builder, bstack1111l1_opy_ (u"ࠩ࡬ࡷࡸࡻࡥࡴࠩ "))
        if params:
            bstack1lllll11ll1l_opy_ += bstack1111l1_opy_ (u"ࠥࡃࢀࢃࠢ ").format(urlencode({bstack1111l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫ "): params.get(bstack1111l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬ "))}))
        return bstack11l1lllll1l_opy_.bstack1lllll1l11l1_opy_(bstack1lllll11ll1l_opy_)
    @staticmethod
    def bstack11ll11111ll_opy_(builder,params=None):
        bstack1lllll11ll1l_opy_ = urljoin(builder, bstack1111l1_opy_ (u"࠭ࡩࡴࡵࡸࡩࡸ࠳ࡳࡶ࡯ࡰࡥࡷࡿࠧ "))
        if params:
            bstack1lllll11ll1l_opy_ += bstack1111l1_opy_ (u"ࠢࡀࡽࢀࠦ ").format(urlencode({bstack1111l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨ "): params.get(bstack1111l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡳࡷࡱࡣࡺࡻࡩࡥࠩ "))}))
        return bstack11l1lllll1l_opy_.bstack1lllll1l11l1_opy_(bstack1lllll11ll1l_opy_)
    @staticmethod
    def bstack1lllll1l11l1_opy_(bstack1lllll11llll_opy_):
        bstack1lllll11l1ll_opy_ = os.environ.get(bstack1111l1_opy_ (u"ࠪࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠨ "), os.environ.get(bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣࡏ࡝ࡔࠨ "), bstack1111l1_opy_ (u"ࠬ࠭ ")))
        headers = {bstack1111l1_opy_ (u"࠭ࡁࡶࡶ࡫ࡳࡷ࡯ࡺࡢࡶ࡬ࡳࡳ࠭​"): bstack1111l1_opy_ (u"ࠧࡃࡧࡤࡶࡪࡸࠠࡼࡿࠪ‌").format(bstack1lllll11l1ll_opy_)}
        response = requests.get(bstack1lllll11llll_opy_, headers=headers)
        bstack1lllll11lll1_opy_ = {}
        try:
            bstack1lllll11lll1_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack1111l1_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵࡧࡲࡴࡧࠣࡎࡘࡕࡎࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠽ࠤࢀࢃࠢ‍").format(e))
            pass
        if bstack1lllll11lll1_opy_ is not None:
            bstack1lllll11lll1_opy_[bstack1111l1_opy_ (u"ࠩࡱࡩࡽࡺ࡟ࡱࡱ࡯ࡰࡤࡺࡩ࡮ࡧࠪ‎")] = response.headers.get(bstack1111l1_opy_ (u"ࠪࡲࡪࡾࡴࡠࡲࡲࡰࡱࡥࡴࡪ࡯ࡨࠫ‏"), str(int(datetime.now().timestamp() * 1000)))
            bstack1lllll11lll1_opy_[bstack1111l1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ‐")] = response.status_code
        return bstack1lllll11lll1_opy_
    @staticmethod
    def bstack1lllll1l11ll_opy_(bstack1lllll11l1l1_opy_, data):
        logger.debug(bstack1111l1_opy_ (u"ࠧࡖࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡕࡩࡶࡻࡥࡴࡶࠣࡪࡴࡸࠠࡵࡧࡶࡸࡔࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࡗࡵࡲࡩࡵࡖࡨࡷࡹࡹࠢ‑"))
        return bstack11l1lllll1l_opy_.bstack1lllll1l1111_opy_(bstack1111l1_opy_ (u"࠭ࡐࡐࡕࡗࠫ‒"), bstack1lllll11l1l1_opy_, data=data)
    @staticmethod
    def bstack1lllll11ll11_opy_(bstack1lllll11l1l1_opy_, data):
        logger.debug(bstack1111l1_opy_ (u"ࠢࡑࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡗ࡫ࡱࡶࡧࡶࡸࠥ࡬࡯ࡳࠢࡪࡩࡹ࡚ࡥࡴࡶࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࡑࡵࡨࡪࡸࡥࡥࡖࡨࡷࡹࡹࠢ–"))
        res = bstack11l1lllll1l_opy_.bstack1lllll1l1111_opy_(bstack1111l1_opy_ (u"ࠨࡉࡈࡘࠬ—"), bstack1lllll11l1l1_opy_, data=data)
        return res
    @staticmethod
    def bstack1lllll1l1111_opy_(method, bstack1lllll11l1l1_opy_, data=None, params=None, extra_headers=None):
        bstack1lllll11l1ll_opy_ = os.environ.get(bstack1111l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭―"), bstack1111l1_opy_ (u"ࠪࠫ‖"))
        headers = {
            bstack1111l1_opy_ (u"ࠫࡦࡻࡴࡩࡱࡵ࡭ࡿࡧࡴࡪࡱࡱࠫ‗"): bstack1111l1_opy_ (u"ࠬࡈࡥࡢࡴࡨࡶࠥࢁࡽࠨ‘").format(bstack1lllll11l1ll_opy_),
            bstack1111l1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬ’"): bstack1111l1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪ‚"),
            bstack1111l1_opy_ (u"ࠨࡃࡦࡧࡪࡶࡴࠨ‛"): bstack1111l1_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬ“")
        }
        if extra_headers:
            headers.update(extra_headers)
        url = bstack11l1l1l111l_opy_ + bstack1111l1_opy_ (u"ࠥ࠳ࠧ”") + bstack1lllll11l1l1_opy_.lstrip(bstack1111l1_opy_ (u"ࠫ࠴࠭„"))
        try:
            if method == bstack1111l1_opy_ (u"ࠬࡍࡅࡕࠩ‟"):
                response = requests.get(url, headers=headers, params=params, json=data)
            elif method == bstack1111l1_opy_ (u"࠭ࡐࡐࡕࡗࠫ†"):
                response = requests.post(url, headers=headers, json=data)
            elif method == bstack1111l1_opy_ (u"ࠧࡑࡗࡗࠫ‡"):
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(bstack1111l1_opy_ (u"ࠣࡗࡱࡷࡺࡶࡰࡰࡴࡷࡩࡩࠦࡈࡕࡖࡓࠤࡲ࡫ࡴࡩࡱࡧ࠾ࠥࢁࡽࠣ•").format(method))
            logger.debug(bstack1111l1_opy_ (u"ࠤࡒࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠢࡵࡩࡶࡻࡥࡴࡶࠣࡱࡦࡪࡥࠡࡶࡲࠤ࡚ࡘࡌ࠻ࠢࡾࢁࠥࡽࡩࡵࡪࠣࡱࡪࡺࡨࡰࡦ࠽ࠤࢀࢃࠢ‣").format(url, method))
            bstack1lllll11lll1_opy_ = {}
            try:
                bstack1lllll11lll1_opy_ = response.json()
            except Exception as e:
                logger.debug(bstack1111l1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡰࡢࡴࡶࡩࠥࡐࡓࡐࡐࠣࡶࡪࡹࡰࡰࡰࡶࡩ࠿ࠦࡻࡾࠢ࠰ࠤࢀࢃࠢ․").format(e, response.text))
            if bstack1lllll11lll1_opy_ is not None:
                bstack1lllll11lll1_opy_[bstack1111l1_opy_ (u"ࠫࡳ࡫ࡸࡵࡡࡳࡳࡱࡲ࡟ࡵ࡫ࡰࡩࠬ‥")] = response.headers.get(
                    bstack1111l1_opy_ (u"ࠬࡴࡥࡹࡶࡢࡴࡴࡲ࡬ࡠࡶ࡬ࡱࡪ࠭…"), str(int(datetime.now().timestamp() * 1000))
                )
                bstack1lllll11lll1_opy_[bstack1111l1_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭‧")] = response.status_code
            return bstack1lllll11lll1_opy_
        except Exception as e:
            logger.error(bstack1111l1_opy_ (u"ࠢࡐࡴࡦ࡬ࡪࡹࡴࡳࡣࡷ࡭ࡴࡴࠠࡳࡧࡴࡹࡪࡹࡴࠡࡨࡤ࡭ࡱ࡫ࡤ࠻ࠢࡾࢁࠥ࠳ࠠࡼࡿࠥ ").format(e, url))
            return None
    @staticmethod
    def bstack11l11llll1l_opy_(bstack1lllll11llll_opy_, data):
        bstack1111l1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤ࡙ࠥࡥ࡯ࡦࡶࠤࡦࠦࡐࡖࡖࠣࡶࡪࡷࡵࡦࡵࡷࠤࡹࡵࠠࡴࡶࡲࡶࡪࠦࡴࡩࡧࠣࡪࡦ࡯࡬ࡦࡦࠣࡸࡪࡹࡴࡴࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨ ")
        bstack1lllll11l1ll_opy_ = os.environ.get(bstack1111l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭‪"), bstack1111l1_opy_ (u"ࠪࠫ‫"))
        headers = {
            bstack1111l1_opy_ (u"ࠫࡦࡻࡴࡩࡱࡵ࡭ࡿࡧࡴࡪࡱࡱࠫ‬"): bstack1111l1_opy_ (u"ࠬࡈࡥࡢࡴࡨࡶࠥࢁࡽࠨ‭").format(bstack1lllll11l1ll_opy_),
            bstack1111l1_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬ‮"): bstack1111l1_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪ ")
        }
        response = requests.put(bstack1lllll11llll_opy_, headers=headers, json=data)
        bstack1lllll11lll1_opy_ = {}
        try:
            bstack1lllll11lll1_opy_ = response.json()
        except Exception as e:
            logger.debug(bstack1111l1_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵࡧࡲࡴࡧࠣࡎࡘࡕࡎࠡࡴࡨࡷࡵࡵ࡮ࡴࡧ࠽ࠤࢀࢃࠢ‰").format(e))
            pass
        logger.debug(bstack1111l1_opy_ (u"ࠤࡕࡩࡶࡻࡥࡴࡶࡘࡸ࡮ࡲࡳ࠻ࠢࡳࡹࡹࡥࡦࡢ࡫࡯ࡩࡩࡥࡴࡦࡵࡷࡷࠥࡸࡥࡴࡲࡲࡲࡸ࡫࠺ࠡࡽࢀࠦ‱").format(bstack1lllll11lll1_opy_))
        if bstack1lllll11lll1_opy_ is not None:
            bstack1lllll11lll1_opy_[bstack1111l1_opy_ (u"ࠪࡲࡪࡾࡴࡠࡲࡲࡰࡱࡥࡴࡪ࡯ࡨࠫ′")] = response.headers.get(
                bstack1111l1_opy_ (u"ࠫࡳ࡫ࡸࡵࡡࡳࡳࡱࡲ࡟ࡵ࡫ࡰࡩࠬ″"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1lllll11lll1_opy_[bstack1111l1_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬ‴")] = response.status_code
        return bstack1lllll11lll1_opy_
    @staticmethod
    def bstack11l11lllll1_opy_(bstack1lllll11llll_opy_):
        bstack1111l1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡗࡪࡴࡤࡴࠢࡤࠤࡌࡋࡔࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡷࡳࠥ࡭ࡥࡵࠢࡷ࡬ࡪࠦࡣࡰࡷࡱࡸࠥࡵࡦࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡶࡨࡷࡹࡹࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦ‵")
        bstack1lllll11l1ll_opy_ = os.environ.get(bstack1111l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡌ࡚ࡈ࡟ࡋ࡙ࡗࠫ‶"), bstack1111l1_opy_ (u"ࠨࠩ‷"))
        headers = {
            bstack1111l1_opy_ (u"ࠩࡤࡹࡹ࡮࡯ࡳ࡫ࡽࡥࡹ࡯࡯࡯ࠩ‸"): bstack1111l1_opy_ (u"ࠪࡆࡪࡧࡲࡦࡴࠣࡿࢂ࠭‹").format(bstack1lllll11l1ll_opy_),
            bstack1111l1_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪ›"): bstack1111l1_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨ※")
        }
        response = requests.get(bstack1lllll11llll_opy_, headers=headers)
        bstack1lllll11lll1_opy_ = {}
        try:
            bstack1lllll11lll1_opy_ = response.json()
            logger.debug(bstack1111l1_opy_ (u"ࠨࡒࡦࡳࡸࡩࡸࡺࡕࡵ࡫࡯ࡷ࠿ࠦࡧࡦࡶࡢࡪࡦ࡯࡬ࡦࡦࡢࡸࡪࡹࡴࡴࠢࡵࡩࡸࡶ࡯࡯ࡵࡨ࠾ࠥࢁࡽࠣ‼").format(bstack1lllll11lll1_opy_))
        except Exception as e:
            logger.debug(bstack1111l1_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡦࡸࡳࡦࠢࡍࡗࡔࡔࠠࡳࡧࡶࡴࡴࡴࡳࡦ࠼ࠣࡿࢂࠦ࠭ࠡࡽࢀࠦ‽").format(e, response.text))
            pass
        if bstack1lllll11lll1_opy_ is not None:
            bstack1lllll11lll1_opy_[bstack1111l1_opy_ (u"ࠨࡰࡨࡼࡹࡥࡰࡰ࡮࡯ࡣࡹ࡯࡭ࡦࠩ‾")] = response.headers.get(
                bstack1111l1_opy_ (u"ࠩࡱࡩࡽࡺ࡟ࡱࡱ࡯ࡰࡤࡺࡩ࡮ࡧࠪ‿"), str(int(datetime.now().timestamp() * 1000))
            )
            bstack1lllll11lll1_opy_[bstack1111l1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ⁀")] = response.status_code
        return bstack1lllll11lll1_opy_
    @staticmethod
    def bstack1111ll1ll1l_opy_(bstack11ll1111ll1_opy_, payload):
        bstack1111l1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࠥࠦࠠࠡࡏࡤ࡯ࡪࡹࠠࡢࠢࡓࡓࡘ࡚ࠠࡳࡧࡴࡹࡪࡹࡴࠡࡶࡲࠤࡹ࡮ࡥࠡࡥࡲࡰࡱ࡫ࡣࡵ࠯ࡥࡹ࡮ࡲࡤ࠮ࡦࡤࡸࡦࠦࡥ࡯ࡦࡳࡳ࡮ࡴࡴ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡅࡷ࡭ࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡦࡰࡧࡴࡴ࡯࡮ࡵࠢࠫࡷࡹࡸࠩ࠻ࠢࡗ࡬ࡪࠦࡁࡑࡋࠣࡩࡳࡪࡰࡰ࡫ࡱࡸࠥࡶࡡࡵࡪ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡳࡥࡾࡲ࡯ࡢࡦࠣࠬࡩ࡯ࡣࡵࠫ࠽ࠤ࡙࡮ࡥࠡࡴࡨࡵࡺ࡫ࡳࡵࠢࡳࡥࡾࡲ࡯ࡢࡦ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡘࡥࡵࡷࡵࡲࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡪࡩࡤࡶ࠽ࠤࡗ࡫ࡳࡱࡱࡱࡷࡪࠦࡦࡳࡱࡰࠤࡹ࡮ࡥࠡࡃࡓࡍ࠱ࠦ࡯ࡳࠢࡑࡳࡳ࡫ࠠࡪࡨࠣࡪࡦ࡯࡬ࡦࡦ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣ⁁")
        try:
            url = bstack1111l1_opy_ (u"ࠧࢁࡽ࠰ࡽࢀࠦ⁂").format(bstack11l1l1l111l_opy_, bstack11ll1111ll1_opy_)
            bstack1lllll11l1ll_opy_ = os.environ.get(bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡊࡘࡖࠪ⁃"), bstack1111l1_opy_ (u"ࠧࠨ⁄"))
            headers = {
                bstack1111l1_opy_ (u"ࠨࡣࡸࡸ࡭ࡵࡲࡪࡼࡤࡸ࡮ࡵ࡮ࠨ⁅"): bstack1111l1_opy_ (u"ࠩࡅࡩࡦࡸࡥࡳࠢࡾࢁࠬ⁆").format(bstack1lllll11l1ll_opy_),
                bstack1111l1_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱࡙ࡿࡰࡦࠩ⁇"): bstack1111l1_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧ⁈")
            }
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            bstack1lllll1l111l_opy_ = [200, 202]
            if response.status_code in bstack1lllll1l111l_opy_:
                return response.json()
            else:
                logger.error(bstack1111l1_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡥࡲࡰࡱ࡫ࡣࡵࠢࡥࡹ࡮ࡲࡤࠡࡦࡤࡸࡦ࠴ࠠࡔࡶࡤࡸࡺࡹ࠺ࠡࡽࢀ࠰ࠥࡘࡥࡴࡲࡲࡲࡸ࡫࠺ࠡࡽࢀࠦ⁉").format(
                    response.status_code, response.text))
                return None
        except Exception as e:
            logger.error(bstack1111l1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡯ࡴࡶࡢࡧࡴࡲ࡬ࡦࡥࡷࡣࡧࡻࡩ࡭ࡦࡢࡨࡦࡺࡡ࠻ࠢࡾࢁࠧ⁊").format(e))
            return None