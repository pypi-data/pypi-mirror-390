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
import datetime
import threading
from bstack_utils.helper import bstack11ll11lll11_opy_, bstack1l1l1l111_opy_, get_host_info, bstack11l11l11lll_opy_, \
 bstack1llllllll_opy_, bstack1l1ll111l_opy_, error_handler, bstack11l11111l11_opy_, bstack11l1l1111l_opy_
import bstack_utils.accessibility as bstack1ll1ll1l11_opy_
from bstack_utils.bstack11llll11l_opy_ import bstack11l111llll_opy_
from bstack_utils.bstack111ll1lll1_opy_ import bstack1ll1111ll1_opy_
from bstack_utils.percy import bstack111111ll_opy_
from bstack_utils.config import Config
bstack11ll1l111l_opy_ = Config.bstack1l1l1l1111_opy_()
logger = logging.getLogger(__name__)
percy = bstack111111ll_opy_()
@error_handler(class_method=False)
def bstack1llll11lll11_opy_(bs_config, bstack11ll111l1l_opy_):
  try:
    data = {
        bstack1111l1_opy_ (u"ࠬ࡬࡯ࡳ࡯ࡤࡸࠬ∂"): bstack1111l1_opy_ (u"࠭ࡪࡴࡱࡱࠫ∃"),
        bstack1111l1_opy_ (u"ࠧࡱࡴࡲ࡮ࡪࡩࡴࡠࡰࡤࡱࡪ࠭∄"): bs_config.get(bstack1111l1_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭∅"), bstack1111l1_opy_ (u"ࠩࠪ∆")),
        bstack1111l1_opy_ (u"ࠪࡲࡦࡳࡥࠨ∇"): bs_config.get(bstack1111l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ∈"), os.path.basename(os.path.abspath(os.getcwd()))),
        bstack1111l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡣ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ∉"): bs_config.get(bstack1111l1_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ∊")),
        bstack1111l1_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬ∋"): bs_config.get(bstack1111l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡄࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫ∌"), bstack1111l1_opy_ (u"ࠩࠪ∍")),
        bstack1111l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ∎"): bstack11l1l1111l_opy_(),
        bstack1111l1_opy_ (u"ࠫࡹࡧࡧࡴࠩ∏"): bstack11l11l11lll_opy_(bs_config),
        bstack1111l1_opy_ (u"ࠬ࡮࡯ࡴࡶࡢ࡭ࡳ࡬࡯ࠨ∐"): get_host_info(),
        bstack1111l1_opy_ (u"࠭ࡣࡪࡡ࡬ࡲ࡫ࡵࠧ∑"): bstack1l1l1l111_opy_(),
        bstack1111l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡥࡲࡶࡰࡢ࡭ࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ−"): os.environ.get(bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡗࡌࡐࡉࡥࡒࡖࡐࡢࡍࡉࡋࡎࡕࡋࡉࡍࡊࡘࠧ∓")),
        bstack1111l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࡡࡷࡩࡸࡺࡳࡠࡴࡨࡶࡺࡴࠧ∔"): os.environ.get(bstack1111l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡕࡉࡗ࡛ࡎࠨ∕"), False),
        bstack1111l1_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࡤࡩ࡯࡯ࡶࡵࡳࡱ࠭∖"): bstack11ll11lll11_opy_(),
        bstack1111l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ∗"): bstack1lll1lllll11_opy_(bs_config),
        bstack1111l1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡧࡩࡹࡧࡩ࡭ࡵࠪ∘"): bstack1llll11111l1_opy_(bstack11ll111l1l_opy_),
        bstack1111l1_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࡠ࡯ࡤࡴࠬ∙"): bstack1llll1111l1l_opy_(bs_config, bstack11ll111l1l_opy_.get(bstack1111l1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡺࡹࡥࡥࠩ√"), bstack1111l1_opy_ (u"ࠩࠪ∛"))),
        bstack1111l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬ∜"): bstack1llllllll_opy_(bs_config),
        bstack1111l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯ࠩ∝"): bstack1lll1llll11l_opy_(bs_config)
    }
    return data
  except Exception as error:
    logger.error(bstack1111l1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡳࡥࡾࡲ࡯ࡢࡦࠣࡪࡴࡸࠠࡕࡧࡶࡸࡍࡻࡢ࠻ࠢࠣࡿࢂࠨ∞").format(str(error)))
    return None
def bstack1llll11111l1_opy_(framework):
  return {
    bstack1111l1_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡐࡤࡱࡪ࠭∟"): framework.get(bstack1111l1_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥࠨ∠"), bstack1111l1_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴࠨ∡")),
    bstack1111l1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯࡛࡫ࡲࡴ࡫ࡲࡲࠬ∢"): framework.get(bstack1111l1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ∣")),
    bstack1111l1_opy_ (u"ࠫࡸࡪ࡫ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ∤"): framework.get(bstack1111l1_opy_ (u"ࠬࡹࡤ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪ∥")),
    bstack1111l1_opy_ (u"࠭࡬ࡢࡰࡪࡹࡦ࡭ࡥࠨ∦"): bstack1111l1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧ∧"),
    bstack1111l1_opy_ (u"ࠨࡶࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ∨"): framework.get(bstack1111l1_opy_ (u"ࠩࡷࡩࡸࡺࡆࡳࡣࡰࡩࡼࡵࡲ࡬ࠩ∩"))
  }
def bstack1lll1llll11l_opy_(bs_config):
  bstack1111l1_opy_ (u"ࠥࠦࠧࠐࠠࠡࡔࡨࡸࡺࡸ࡮ࡴࠢࡷ࡬ࡪࠦࡴࡦࡵࡷࠤࡴࡸࡣࡩࡧࡶࡸࡷࡧࡴࡪࡱࡱࠤࡩࡧࡴࡢࠢࡩࡳࡷࠦࡢࡶ࡫࡯ࡨࠥࡹࡴࡢࡴࡷ࠲ࠏࠦࠠࠣࠤࠥ∪")
  if not bs_config:
    return {}
  bstack1111ll1l111_opy_ = bstack11l111llll_opy_(bs_config).bstack1111ll111ll_opy_(bs_config)
  return bstack1111ll1l111_opy_
def bstack111lll1l1l_opy_(bs_config, framework):
  bstack111lllll_opy_ = False
  bstack1l1l1l1ll1_opy_ = False
  bstack1llll1111111_opy_ = False
  if bstack1111l1_opy_ (u"ࠫࡹࡻࡲࡣࡱࡖࡧࡦࡲࡥࠨ∫") in bs_config:
    bstack1llll1111111_opy_ = True
  elif bstack1111l1_opy_ (u"ࠬࡧࡰࡱࠩ∬") in bs_config:
    bstack111lllll_opy_ = True
  else:
    bstack1l1l1l1ll1_opy_ = True
  bstack1l1lll1lll_opy_ = {
    bstack1111l1_opy_ (u"࠭࡯ࡣࡵࡨࡶࡻࡧࡢࡪ࡮࡬ࡸࡾ࠭∭"): bstack1ll1111ll1_opy_.bstack1llll11111ll_opy_(bs_config, framework),
    bstack1111l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧ∮"): bstack1ll1ll1l11_opy_.bstack1llll1l11l_opy_(bs_config),
    bstack1111l1_opy_ (u"ࠨࡲࡨࡶࡨࡿࠧ∯"): bs_config.get(bstack1111l1_opy_ (u"ࠩࡳࡩࡷࡩࡹࠨ∰"), False),
    bstack1111l1_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩࠬ∱"): bstack1l1l1l1ll1_opy_,
    bstack1111l1_opy_ (u"ࠫࡦࡶࡰࡠࡣࡸࡸࡴࡳࡡࡵࡧࠪ∲"): bstack111lllll_opy_,
    bstack1111l1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦࠩ∳"): bstack1llll1111111_opy_
  }
  return bstack1l1lll1lll_opy_
@error_handler(class_method=False)
def bstack1lll1lllll11_opy_(bs_config):
  try:
    bstack1llll1111l11_opy_ = json.loads(os.getenv(bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧ∴"), bstack1111l1_opy_ (u"ࠧࡼࡿࠪ∵")))
    bstack1llll1111l11_opy_ = bstack1lll1lllll1l_opy_(bs_config, bstack1llll1111l11_opy_)
    return {
        bstack1111l1_opy_ (u"ࠨࡵࡨࡸࡹ࡯࡮ࡨࡵࠪ∶"): bstack1llll1111l11_opy_
    }
  except Exception as error:
    logger.error(bstack1111l1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡨࡸࡥࡢࡶ࡬ࡲ࡬ࠦࡧࡦࡶࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡷࡪࡺࡴࡪࡰࡪࡷࠥ࡬࡯ࡳࠢࡗࡩࡸࡺࡈࡶࡤ࠽ࠤࠥࢁࡽࠣ∷").format(str(error)))
    return {}
def bstack1lll1lllll1l_opy_(bs_config, bstack1llll1111l11_opy_):
  if ((bstack1111l1_opy_ (u"ࠪࡸࡺࡸࡢࡰࡕࡦࡥࡱ࡫ࠧ∸") in bs_config or not bstack1llllllll_opy_(bs_config)) and bstack1ll1ll1l11_opy_.bstack1llll1l11l_opy_(bs_config)):
    bstack1llll1111l11_opy_[bstack1111l1_opy_ (u"ࠦ࡮ࡴࡣ࡭ࡷࡧࡩࡊࡴࡣࡰࡦࡨࡨࡊࡾࡴࡦࡰࡶ࡭ࡴࡴࠢ∹")] = True
  return bstack1llll1111l11_opy_
def bstack1llll111lll1_opy_(array, bstack1lll1llll1ll_opy_, bstack1lll1llll1l1_opy_):
  result = {}
  for o in array:
    key = o[bstack1lll1llll1ll_opy_]
    result[key] = o[bstack1lll1llll1l1_opy_]
  return result
def bstack1llll11lllll_opy_(bstack1ll1llll1l_opy_=bstack1111l1_opy_ (u"ࠬ࠭∺")):
  bstack1lll1llllll1_opy_ = bstack1ll1ll1l11_opy_.on()
  bstack1lll1llll111_opy_ = bstack1ll1111ll1_opy_.on()
  bstack1llll111111l_opy_ = percy.bstack1l11lll1l1_opy_()
  if bstack1llll111111l_opy_ and not bstack1lll1llll111_opy_ and not bstack1lll1llllll1_opy_:
    return bstack1ll1llll1l_opy_ not in [bstack1111l1_opy_ (u"࠭ࡃࡃࡖࡖࡩࡸࡹࡩࡰࡰࡆࡶࡪࡧࡴࡦࡦࠪ∻"), bstack1111l1_opy_ (u"ࠧࡍࡱࡪࡇࡷ࡫ࡡࡵࡧࡧࠫ∼")]
  elif bstack1lll1llllll1_opy_ and not bstack1lll1llll111_opy_:
    return bstack1ll1llll1l_opy_ not in [bstack1111l1_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩ∽"), bstack1111l1_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫ∾"), bstack1111l1_opy_ (u"ࠪࡐࡴ࡭ࡃࡳࡧࡤࡸࡪࡪࠧ∿")]
  return bstack1lll1llllll1_opy_ or bstack1lll1llll111_opy_ or bstack1llll111111l_opy_
@error_handler(class_method=False)
def bstack1llll111llll_opy_(bstack1ll1llll1l_opy_, test=None):
  bstack1lll1lllllll_opy_ = bstack1ll1ll1l11_opy_.on()
  if not bstack1lll1lllllll_opy_ or bstack1ll1llll1l_opy_ not in [bstack1111l1_opy_ (u"࡙ࠫ࡫ࡳࡵࡔࡸࡲࡋ࡯࡮ࡪࡵ࡫ࡩࡩ࠭≀")] or test == None:
    return None
  return {
    bstack1111l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬ≁"): bstack1lll1lllllll_opy_ and bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"࠭ࡡ࠲࠳ࡼࡔࡱࡧࡴࡧࡱࡵࡱࠬ≂"), None) == True and bstack1ll1ll1l11_opy_.bstack11l1ll111l_opy_(test[bstack1111l1_opy_ (u"ࠧࡵࡣࡪࡷࠬ≃")])
  }
def bstack1llll1111l1l_opy_(bs_config, framework):
  bstack111lllll_opy_ = False
  bstack1l1l1l1ll1_opy_ = False
  bstack1llll1111111_opy_ = False
  if bstack1111l1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬ≄") in bs_config:
    bstack1llll1111111_opy_ = True
  elif bstack1111l1_opy_ (u"ࠩࡤࡴࡵ࠭≅") in bs_config:
    bstack111lllll_opy_ = True
  else:
    bstack1l1l1l1ll1_opy_ = True
  bstack1l1lll1lll_opy_ = {
    bstack1111l1_opy_ (u"ࠪࡳࡧࡹࡥࡳࡸࡤࡦ࡮ࡲࡩࡵࡻࠪ≆"): bstack1ll1111ll1_opy_.bstack1llll11111ll_opy_(bs_config, framework),
    bstack1111l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫ≇"): bstack1ll1ll1l11_opy_.bstack1ll11l1l1l_opy_(bs_config),
    bstack1111l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫ≈"): bs_config.get(bstack1111l1_opy_ (u"࠭ࡰࡦࡴࡦࡽࠬ≉"), False),
    bstack1111l1_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡦࠩ≊"): bstack1l1l1l1ll1_opy_,
    bstack1111l1_opy_ (u"ࠨࡣࡳࡴࡤࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ≋"): bstack111lllll_opy_,
    bstack1111l1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡴࡥࡤࡰࡪ࠭≌"): bstack1llll1111111_opy_
  }
  return bstack1l1lll1lll_opy_