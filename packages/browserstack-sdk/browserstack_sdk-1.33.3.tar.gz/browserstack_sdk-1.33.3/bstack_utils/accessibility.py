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
import requests
import logging
import threading
import bstack_utils.constants as bstack11ll1l1ll1l_opy_
from urllib.parse import urlparse
from bstack_utils.constants import bstack11ll1l111l1_opy_ as bstack11ll11l111l_opy_, EVENTS
from bstack_utils.bstack1l1l11l11_opy_ import bstack1l1l11l11_opy_
from bstack_utils.helper import bstack11l1l1111l_opy_, bstack1111ll1l1l_opy_, bstack1llllllll_opy_, bstack11ll11lllll_opy_, \
  bstack11ll1ll111l_opy_, bstack1l1l1l111_opy_, get_host_info, bstack11ll11lll11_opy_, bstack111llll11_opy_, error_handler, bstack11ll1ll11l1_opy_, bstack11ll1ll1lll_opy_, bstack1l1ll111l_opy_
from browserstack_sdk._version import __version__
from bstack_utils.bstack1lll1l11l_opy_ import get_logger
from bstack_utils.bstack1llll1llll_opy_ import bstack1llll11l111_opy_
from selenium.webdriver.chrome.options import Options as ChromeOptions
from browserstack_sdk.sdk_cli.cli import cli
from bstack_utils.constants import *
logger = get_logger(__name__)
bstack1llll1llll_opy_ = bstack1llll11l111_opy_()
@error_handler(class_method=False)
def _11ll11l1l1l_opy_(driver, bstack11111lll11_opy_):
  response = {}
  try:
    caps = driver.capabilities
    response = {
        bstack1111l1_opy_ (u"࠭࡯ࡴࡡࡱࡥࡲ࡫ࠧᙁ"): caps.get(bstack1111l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪ࠭ᙂ"), None),
        bstack1111l1_opy_ (u"ࠨࡱࡶࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬᙃ"): bstack11111lll11_opy_.get(bstack1111l1_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬᙄ"), None),
        bstack1111l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡳࡧ࡭ࡦࠩᙅ"): caps.get(bstack1111l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩᙆ"), None),
        bstack1111l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧᙇ"): caps.get(bstack1111l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᙈ"), None)
    }
  except Exception as error:
    logger.debug(bstack1111l1_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡦࡦࡶࡦ࡬࡮ࡴࡧࠡࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࠣࡨࡪࡺࡡࡪ࡮ࡶࠤࡼ࡯ࡴࡩࠢࡨࡶࡷࡵࡲࠡ࠼ࠣࠫᙉ") + str(error))
  return response
def on():
    if os.environ.get(bstack1111l1_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᙊ"), None) is None or os.environ[bstack1111l1_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᙋ")] == bstack1111l1_opy_ (u"ࠥࡲࡺࡲ࡬ࠣᙌ"):
        return False
    return True
def bstack1llll1l11l_opy_(config):
  return config.get(bstack1111l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᙍ"), False) or any([p.get(bstack1111l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᙎ"), False) == True for p in config.get(bstack1111l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩᙏ"), [])])
def bstack11lll1l111_opy_(config, bstack1l1ll1ll1l_opy_):
  try:
    bstack11ll1l11l11_opy_ = config.get(bstack1111l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠧᙐ"), False)
    if int(bstack1l1ll1ll1l_opy_) < len(config.get(bstack1111l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫᙑ"), [])) and config[bstack1111l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬᙒ")][bstack1l1ll1ll1l_opy_]:
      bstack11ll11l1lll_opy_ = config[bstack1111l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᙓ")][bstack1l1ll1ll1l_opy_].get(bstack1111l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᙔ"), None)
    else:
      bstack11ll11l1lll_opy_ = config.get(bstack1111l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᙕ"), None)
    if bstack11ll11l1lll_opy_ != None:
      bstack11ll1l11l11_opy_ = bstack11ll11l1lll_opy_
    bstack11ll11l1111_opy_ = os.getenv(bstack1111l1_opy_ (u"࠭ࡂࡔࡡࡄ࠵࠶࡟࡟ࡋ࡙ࡗࠫᙖ")) is not None and len(os.getenv(bstack1111l1_opy_ (u"ࠧࡃࡕࡢࡅ࠶࠷࡙ࡠࡌ࡚ࡘࠬᙗ"))) > 0 and os.getenv(bstack1111l1_opy_ (u"ࠨࡄࡖࡣࡆ࠷࠱࡚ࡡࡍ࡛࡙࠭ᙘ")) != bstack1111l1_opy_ (u"ࠩࡱࡹࡱࡲࠧᙙ")
    return bstack11ll1l11l11_opy_ and bstack11ll11l1111_opy_
  except Exception as error:
    logger.debug(bstack1111l1_opy_ (u"ࠪࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡹࡩࡷ࡯ࡦࡺ࡫ࡱ࡫ࠥࡺࡨࡦࠢࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡶࡩࡸࡹࡩࡰࡰࠣࡻ࡮ࡺࡨࠡࡧࡵࡶࡴࡸࠠ࠻ࠢࠪᙚ") + str(error))
  return False
def bstack11l1ll111l_opy_(test_tags):
  bstack1ll11111lll_opy_ = os.getenv(bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡠࡃࡆࡇࡊ࡙ࡓࡊࡄࡌࡐࡎ࡚࡙ࡠࡅࡒࡒࡋࡏࡇࡖࡔࡄࡘࡎࡕࡎࡠ࡛ࡐࡐࠬᙛ"))
  if bstack1ll11111lll_opy_ is None:
    return True
  bstack1ll11111lll_opy_ = json.loads(bstack1ll11111lll_opy_)
  try:
    include_tags = bstack1ll11111lll_opy_[bstack1111l1_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪᙜ")] if bstack1111l1_opy_ (u"࠭ࡩ࡯ࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫᙝ") in bstack1ll11111lll_opy_ and isinstance(bstack1ll11111lll_opy_[bstack1111l1_opy_ (u"ࠧࡪࡰࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬᙞ")], list) else []
    exclude_tags = bstack1ll11111lll_opy_[bstack1111l1_opy_ (u"ࠨࡧࡻࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ᙟ")] if bstack1111l1_opy_ (u"ࠩࡨࡼࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧᙠ") in bstack1ll11111lll_opy_ and isinstance(bstack1ll11111lll_opy_[bstack1111l1_opy_ (u"ࠪࡩࡽࡩ࡬ࡶࡦࡨࡘࡦ࡭ࡳࡊࡰࡗࡩࡸࡺࡩ࡯ࡩࡖࡧࡴࡶࡥࠨᙡ")], list) else []
    excluded = any(tag in exclude_tags for tag in test_tags)
    included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
    return not excluded and included
  except Exception as error:
    logger.debug(bstack1111l1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡹࡥࡱ࡯ࡤࡢࡶ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦࠢࡩࡳࡷࠦࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡢࡦࡨࡲࡶࡪࠦࡳࡤࡣࡱࡲ࡮ࡴࡧ࠯ࠢࡈࡶࡷࡵࡲࠡ࠼ࠣࠦᙢ") + str(error))
  return False
def bstack11ll11llll1_opy_(config, bstack11ll11ll11l_opy_, bstack11ll1l1l11l_opy_, bstack11ll11ll111_opy_):
  bstack11ll11lll1l_opy_ = bstack11ll11lllll_opy_(config)
  bstack11ll1l11111_opy_ = bstack11ll1ll111l_opy_(config)
  if bstack11ll11lll1l_opy_ is None or bstack11ll1l11111_opy_ is None:
    logger.error(bstack1111l1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡷࡩࡸࡺࠠࡳࡷࡱࠤ࡫ࡵࡲࠡࡄࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࠠࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱ࠾ࠥࡓࡩࡴࡵ࡬ࡲ࡬ࠦࡡࡶࡶ࡫ࡩࡳࡺࡩࡤࡣࡷ࡭ࡴࡴࠠࡵࡱ࡮ࡩࡳ࠭ᙣ"))
    return [None, None]
  try:
    settings = json.loads(os.getenv(bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧᙤ"), bstack1111l1_opy_ (u"ࠧࡼࡿࠪᙥ")))
    data = {
        bstack1111l1_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ᙦ"): config[bstack1111l1_opy_ (u"ࠩࡳࡶࡴࡰࡥࡤࡶࡑࡥࡲ࡫ࠧᙧ")],
        bstack1111l1_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ᙨ"): config.get(bstack1111l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧᙩ"), os.path.basename(os.getcwd())),
        bstack1111l1_opy_ (u"ࠬࡹࡴࡢࡴࡷࡘ࡮ࡳࡥࠨᙪ"): bstack11l1l1111l_opy_(),
        bstack1111l1_opy_ (u"࠭ࡤࡦࡵࡦࡶ࡮ࡶࡴࡪࡱࡱࠫᙫ"): config.get(bstack1111l1_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡊࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪᙬ"), bstack1111l1_opy_ (u"ࠨࠩ᙭")),
        bstack1111l1_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩ᙮"): {
            bstack1111l1_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡔࡡ࡮ࡧࠪᙯ"): bstack11ll11ll11l_opy_,
            bstack1111l1_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࡖࡦࡴࡶ࡭ࡴࡴࠧᙰ"): bstack11ll1l1l11l_opy_,
            bstack1111l1_opy_ (u"ࠬࡹࡤ࡬ࡘࡨࡶࡸ࡯࡯࡯ࠩᙱ"): __version__,
            bstack1111l1_opy_ (u"࠭࡬ࡢࡰࡪࡹࡦ࡭ࡥࠨᙲ"): bstack1111l1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧᙳ"),
            bstack1111l1_opy_ (u"ࠨࡶࡨࡷࡹࡌࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨᙴ"): bstack1111l1_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰࠫᙵ"),
            bstack1111l1_opy_ (u"ࠪࡸࡪࡹࡴࡇࡴࡤࡱࡪࡽ࡯ࡳ࡭࡙ࡩࡷࡹࡩࡰࡰࠪᙶ"): bstack11ll11ll111_opy_
        },
        bstack1111l1_opy_ (u"ࠫࡸ࡫ࡴࡵ࡫ࡱ࡫ࡸ࠭ᙷ"): settings,
        bstack1111l1_opy_ (u"ࠬࡼࡥࡳࡵ࡬ࡳࡳࡉ࡯࡯ࡶࡵࡳࡱ࠭ᙸ"): bstack11ll11lll11_opy_(),
        bstack1111l1_opy_ (u"࠭ࡣࡪࡋࡱࡪࡴ࠭ᙹ"): bstack1l1l1l111_opy_(),
        bstack1111l1_opy_ (u"ࠧࡩࡱࡶࡸࡎࡴࡦࡰࠩᙺ"): get_host_info(),
        bstack1111l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠪᙻ"): bstack1llllllll_opy_(config)
    }
    headers = {
        bstack1111l1_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡘࡾࡶࡥࠨᙼ"): bstack1111l1_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ᙽ"),
    }
    config = {
        bstack1111l1_opy_ (u"ࠫࡦࡻࡴࡩࠩᙾ"): (bstack11ll11lll1l_opy_, bstack11ll1l11111_opy_),
        bstack1111l1_opy_ (u"ࠬ࡮ࡥࡢࡦࡨࡶࡸ࠭ᙿ"): headers
    }
    response = bstack111llll11_opy_(bstack1111l1_opy_ (u"࠭ࡐࡐࡕࡗࠫ "), bstack11ll11l111l_opy_ + bstack1111l1_opy_ (u"ࠧ࠰ࡸ࠵࠳ࡹ࡫ࡳࡵࡡࡵࡹࡳࡹࠧᚁ"), data, config)
    bstack11ll11l1l11_opy_ = response.json()
    if bstack11ll11l1l11_opy_[bstack1111l1_opy_ (u"ࠨࡵࡸࡧࡨ࡫ࡳࡴࠩᚂ")]:
      parsed = json.loads(os.getenv(bstack1111l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡥࡁࡄࡅࡈࡗࡘࡏࡂࡊࡎࡌࡘ࡞ࡥࡃࡐࡐࡉࡍࡌ࡛ࡒࡂࡖࡌࡓࡓࡥ࡙ࡎࡎࠪᚃ"), bstack1111l1_opy_ (u"ࠪࡿࢂ࠭ᚄ")))
      parsed[bstack1111l1_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᚅ")] = bstack11ll11l1l11_opy_[bstack1111l1_opy_ (u"ࠬࡪࡡࡵࡣࠪᚆ")][bstack1111l1_opy_ (u"࠭ࡳࡤࡣࡱࡲࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧᚇ")]
      os.environ[bstack1111l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡔࡆࡕࡗࡣࡆࡉࡃࡆࡕࡖࡍࡇࡏࡌࡊࡖ࡜ࡣࡈࡕࡎࡇࡋࡊ࡙ࡗࡇࡔࡊࡑࡑࡣ࡞ࡓࡌࠨᚈ")] = json.dumps(parsed)
      bstack1l1l11l11_opy_.bstack11l11l11l1_opy_(bstack11ll11l1l11_opy_[bstack1111l1_opy_ (u"ࠨࡦࡤࡸࡦ࠭ᚉ")][bstack1111l1_opy_ (u"ࠩࡶࡧࡷ࡯ࡰࡵࡵࠪᚊ")])
      bstack1l1l11l11_opy_.bstack11ll1l1lll1_opy_(bstack11ll11l1l11_opy_[bstack1111l1_opy_ (u"ࠪࡨࡦࡺࡡࠨᚋ")][bstack1111l1_opy_ (u"ࠫࡨࡵ࡭࡮ࡣࡱࡨࡸ࠭ᚌ")])
      bstack1l1l11l11_opy_.store()
      return bstack11ll11l1l11_opy_[bstack1111l1_opy_ (u"ࠬࡪࡡࡵࡣࠪᚍ")][bstack1111l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࡚࡯࡬ࡧࡱࠫᚎ")], bstack11ll11l1l11_opy_[bstack1111l1_opy_ (u"ࠧࡥࡣࡷࡥࠬᚏ")][bstack1111l1_opy_ (u"ࠨ࡫ࡧࠫᚐ")]
    else:
      logger.error(bstack1111l1_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡷࡻ࡮࡯࡫ࡱ࡫ࠥࡈࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࠤࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮࠻ࠢࠪᚑ") + bstack11ll11l1l11_opy_[bstack1111l1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫᚒ")])
      if bstack11ll11l1l11_opy_[bstack1111l1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᚓ")] == bstack1111l1_opy_ (u"ࠬࡏ࡮ࡷࡣ࡯࡭ࡩࠦࡣࡰࡰࡩ࡭࡬ࡻࡲࡢࡶ࡬ࡳࡳࠦࡰࡢࡵࡶࡩࡩ࠴ࠧᚔ"):
        for bstack11ll111llll_opy_ in bstack11ll11l1l11_opy_[bstack1111l1_opy_ (u"࠭ࡥࡳࡴࡲࡶࡸ࠭ᚕ")]:
          logger.error(bstack11ll111llll_opy_[bstack1111l1_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᚖ")])
      return None, None
  except Exception as error:
    logger.error(bstack1111l1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡧࡷ࡫ࡡࡵ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡶࡺࡴࠠࡧࡱࡵࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴ࠺ࠡࠤᚗ") +  str(error))
    return None, None
def bstack11ll1l111ll_opy_():
  if os.getenv(bstack1111l1_opy_ (u"ࠩࡅࡗࡤࡇ࠱࠲࡛ࡢࡎ࡜࡚ࠧᚘ")) is None:
    return {
        bstack1111l1_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪᚙ"): bstack1111l1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᚚ"),
        bstack1111l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭᚛"): bstack1111l1_opy_ (u"࠭ࡂࡶ࡫࡯ࡨࠥࡩࡲࡦࡣࡷ࡭ࡴࡴࠠࡩࡣࡧࠤ࡫ࡧࡩ࡭ࡧࡧ࠲ࠬ᚜")
    }
  data = {bstack1111l1_opy_ (u"ࠧࡦࡰࡧࡘ࡮ࡳࡥࠨ᚝"): bstack11l1l1111l_opy_()}
  headers = {
      bstack1111l1_opy_ (u"ࠨࡃࡸࡸ࡭ࡵࡲࡪࡼࡤࡸ࡮ࡵ࡮ࠨ᚞"): bstack1111l1_opy_ (u"ࠩࡅࡩࡦࡸࡥࡳࠢࠪ᚟") + os.getenv(bstack1111l1_opy_ (u"ࠥࡆࡘࡥࡁ࠲࠳࡜ࡣࡏ࡝ࡔࠣᚠ")),
      bstack1111l1_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪᚡ"): bstack1111l1_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨᚢ")
  }
  response = bstack111llll11_opy_(bstack1111l1_opy_ (u"࠭ࡐࡖࡖࠪᚣ"), bstack11ll11l111l_opy_ + bstack1111l1_opy_ (u"ࠧ࠰ࡶࡨࡷࡹࡥࡲࡶࡰࡶ࠳ࡸࡺ࡯ࡱࠩᚤ"), data, { bstack1111l1_opy_ (u"ࠨࡪࡨࡥࡩ࡫ࡲࡴࠩᚥ"): headers })
  try:
    if response.status_code == 200:
      logger.info(bstack1111l1_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲ࡚ࠥࡥࡴࡶࠣࡖࡺࡴࠠ࡮ࡣࡵ࡯ࡪࡪࠠࡢࡵࠣࡧࡴࡳࡰ࡭ࡧࡷࡩࡩࠦࡡࡵࠢࠥᚦ") + bstack1111ll1l1l_opy_().isoformat() + bstack1111l1_opy_ (u"ࠪ࡞ࠬᚧ"))
      return {bstack1111l1_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫᚨ"): bstack1111l1_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭ᚩ"), bstack1111l1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧᚪ"): bstack1111l1_opy_ (u"ࠧࠨᚫ")}
    else:
      response.raise_for_status()
  except requests.RequestException as error:
    logger.error(bstack1111l1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࡼ࡮ࡩ࡭ࡧࠣࡱࡦࡸ࡫ࡪࡰࡪࠤࡨࡵ࡭ࡱ࡮ࡨࡸ࡮ࡵ࡮ࠡࡱࡩࠤࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠣࡅࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠠࡕࡧࡶࡸࠥࡘࡵ࡯࠼ࠣࠦᚬ") + str(error))
    return {
        bstack1111l1_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩᚭ"): bstack1111l1_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩᚮ"),
        bstack1111l1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᚯ"): str(error)
    }
def bstack11ll1l1111l_opy_(bstack11ll1ll1ll1_opy_):
    return re.match(bstack1111l1_opy_ (u"ࡷ࠭࡞࡝ࡦ࠮ࠬࡡ࠴࡜ࡥ࠭ࠬࡃࠩ࠭ᚰ"), bstack11ll1ll1ll1_opy_.strip()) is not None
def bstack11l111111l_opy_(caps, options, desired_capabilities={}, config=None):
    try:
        if options:
          bstack11ll1l1l1ll_opy_ = options.to_capabilities()
        elif desired_capabilities:
          bstack11ll1l1l1ll_opy_ = desired_capabilities
        else:
          bstack11ll1l1l1ll_opy_ = {}
        bstack1ll1111ll1l_opy_ = (bstack11ll1l1l1ll_opy_.get(bstack1111l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡏࡣࡰࡩࠬᚱ"), bstack1111l1_opy_ (u"ࠧࠨᚲ")).lower() or caps.get(bstack1111l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡑࡥࡲ࡫ࠧᚳ"), bstack1111l1_opy_ (u"ࠩࠪᚴ")).lower())
        if bstack1ll1111ll1l_opy_ == bstack1111l1_opy_ (u"ࠪ࡭ࡴࡹࠧᚵ"):
            return True
        if bstack1ll1111ll1l_opy_ == bstack1111l1_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࠬᚶ"):
            bstack1ll11l1l1l1_opy_ = str(float(caps.get(bstack1111l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧᚷ")) or bstack11ll1l1l1ll_opy_.get(bstack1111l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᚸ"), {}).get(bstack1111l1_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪᚹ"),bstack1111l1_opy_ (u"ࠨࠩᚺ"))))
            if bstack1ll1111ll1l_opy_ == bstack1111l1_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࠪᚻ") and int(bstack1ll11l1l1l1_opy_.split(bstack1111l1_opy_ (u"ࠪ࠲ࠬᚼ"))[0]) < float(bstack11ll1ll1l1l_opy_):
                logger.warning(str(bstack11ll1l1l1l1_opy_))
                return False
            return True
        bstack1ll111111l1_opy_ = caps.get(bstack1111l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᚽ"), {}).get(bstack1111l1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠩᚾ"), caps.get(bstack1111l1_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭ᚿ"), bstack1111l1_opy_ (u"ࠧࠨᛀ")))
        if bstack1ll111111l1_opy_:
            logger.warning(bstack1111l1_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡶࡺࡴࠠࡰࡰ࡯ࡽࠥࡵ࡮ࠡࡆࡨࡷࡰࡺ࡯ࡱࠢࡥࡶࡴࡽࡳࡦࡴࡶ࠲ࠧᛁ"))
            return False
        browser = caps.get(bstack1111l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧᛂ"), bstack1111l1_opy_ (u"ࠪࠫᛃ")).lower() or bstack11ll1l1l1ll_opy_.get(bstack1111l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩᛄ"), bstack1111l1_opy_ (u"ࠬ࠭ᛅ")).lower()
        if browser != bstack1111l1_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ᛆ"):
            logger.warning(bstack1111l1_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡄࡪࡵࡳࡲ࡫ࠠࡣࡴࡲࡻࡸ࡫ࡲࡴ࠰ࠥᛇ"))
            return False
        browser_version = caps.get(bstack1111l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᛈ")) or caps.get(bstack1111l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫᛉ")) or bstack11ll1l1l1ll_opy_.get(bstack1111l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᛊ")) or bstack11ll1l1l1ll_opy_.get(bstack1111l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᛋ"), {}).get(bstack1111l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᛌ")) or bstack11ll1l1l1ll_opy_.get(bstack1111l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᛍ"), {}).get(bstack1111l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᛎ"))
        bstack1ll111ll11l_opy_ = bstack11ll1l1ll1l_opy_.bstack1ll11ll1111_opy_
        bstack11ll1l11ll1_opy_ = False
        if config is not None:
          bstack11ll1l11ll1_opy_ = bstack1111l1_opy_ (u"ࠨࡶࡸࡶࡧࡵࡓࡤࡣ࡯ࡩࠬᛏ") in config and str(config[bstack1111l1_opy_ (u"ࠩࡷࡹࡷࡨ࡯ࡔࡥࡤࡰࡪ࠭ᛐ")]).lower() != bstack1111l1_opy_ (u"ࠪࡪࡦࡲࡳࡦࠩᛑ")
        if os.environ.get(bstack1111l1_opy_ (u"ࠫࡎ࡙࡟ࡏࡑࡑࡣࡇ࡙ࡔࡂࡅࡎࡣࡎࡔࡆࡓࡃࡢࡅ࠶࠷࡙ࡠࡕࡈࡗࡘࡏࡏࡏࠩᛒ"), bstack1111l1_opy_ (u"ࠬ࠭ᛓ")).lower() == bstack1111l1_opy_ (u"࠭ࡴࡳࡷࡨࠫᛔ") or bstack11ll1l11ll1_opy_:
          bstack1ll111ll11l_opy_ = bstack11ll1l1ll1l_opy_.bstack1ll111l1l11_opy_
        if browser_version and browser_version != bstack1111l1_opy_ (u"ࠧ࡭ࡣࡷࡩࡸࡺࠧᛕ") and int(browser_version.split(bstack1111l1_opy_ (u"ࠨ࠰ࠪᛖ"))[0]) <= bstack1ll111ll11l_opy_:
          logger.warning(bstack11111l1ll1_opy_ (u"ࠩࡄࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠢࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡷࡻ࡮ࠡࡱࡱࡰࡾࠦ࡯࡯ࠢࡆ࡬ࡷࡵ࡭ࡦࠢࡥࡶࡴࡽࡳࡦࡴࠣࡺࡪࡸࡳࡪࡱࡱࠤ࡬ࡸࡥࡢࡶࡨࡶࠥࡺࡨࡢࡰࠣࡿࡲ࡯࡮ࡠࡣ࠴࠵ࡾࡥࡳࡶࡲࡳࡳࡷࡺࡥࡥࡡࡦ࡬ࡷࡵ࡭ࡦࡡࡹࡩࡷࡹࡩࡰࡰࢀ࠲ࠬᛗ"))
          return False
        if not options:
          bstack1l1llllll1l_opy_ = caps.get(bstack1111l1_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨᛘ")) or bstack11ll1l1l1ll_opy_.get(bstack1111l1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᛙ"), {})
          if bstack1111l1_opy_ (u"ࠬ࠳࠭ࡩࡧࡤࡨࡱ࡫ࡳࡴࠩᛚ") in bstack1l1llllll1l_opy_.get(bstack1111l1_opy_ (u"࠭ࡡࡳࡩࡶࠫᛛ"), []):
              logger.warning(bstack1111l1_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡱࡳࡹࠦࡲࡶࡰࠣࡳࡳࠦ࡬ࡦࡩࡤࡧࡾࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪ࠴ࠠࡔࡹ࡬ࡸࡨ࡮ࠠࡵࡱࠣࡲࡪࡽࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫ࠠࡰࡴࠣࡥࡻࡵࡩࡥࠢࡸࡷ࡮ࡴࡧࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥ࠯ࠤᛜ"))
              return False
        return True
    except Exception as error:
        logger.debug(bstack1111l1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡷࡣ࡯࡭ࡩࡧࡴࡦࠢࡤ࠵࠶ࡿࠠࡴࡷࡳࡴࡴࡸࡴࠡ࠼ࠥᛝ") + str(error))
        return False
def set_capabilities(caps, config):
  try:
    bstack1lll1l1111l_opy_ = config.get(bstack1111l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩᛞ"), {})
    bstack1lll1l1111l_opy_[bstack1111l1_opy_ (u"ࠪࡥࡺࡺࡨࡕࡱ࡮ࡩࡳ࠭ᛟ")] = os.getenv(bstack1111l1_opy_ (u"ࠫࡇ࡙࡟ࡂ࠳࠴࡝ࡤࡐࡗࡕࠩᛠ"))
    bstack11ll11ll1l1_opy_ = json.loads(os.getenv(bstack1111l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡙ࡋࡓࡕࡡࡄࡇࡈࡋࡓࡔࡋࡅࡍࡑࡏࡔ࡚ࡡࡆࡓࡓࡌࡉࡈࡗࡕࡅ࡙ࡏࡏࡏࡡ࡜ࡑࡑ࠭ᛡ"), bstack1111l1_opy_ (u"࠭ࡻࡾࠩᛢ"))).get(bstack1111l1_opy_ (u"ࠧࡴࡥࡤࡲࡳ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨᛣ"))
    if not config[bstack1111l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪᛤ")].get(bstack1111l1_opy_ (u"ࠤࡤࡴࡵࡥࡡࡶࡶࡲࡱࡦࡺࡥࠣᛥ")):
      if bstack1111l1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫᛦ") in caps:
        caps[bstack1111l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᛧ")][bstack1111l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡔࡶࡴࡪࡱࡱࡷࠬᛨ")] = bstack1lll1l1111l_opy_
        caps[bstack1111l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧᛩ")][bstack1111l1_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᛪ")][bstack1111l1_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩ᛫")] = bstack11ll11ll1l1_opy_
      else:
        caps[bstack1111l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨ᛬")] = bstack1lll1l1111l_opy_
        caps[bstack1111l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡑࡳࡸ࡮ࡵ࡮ࡴࠩ᛭")][bstack1111l1_opy_ (u"ࠫࡸࡩࡡ࡯ࡰࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬᛮ")] = bstack11ll11ll1l1_opy_
  except Exception as error:
    logger.debug(bstack1111l1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶ࠲ࠥࡋࡲࡳࡱࡵ࠾ࠥࠨᛯ") +  str(error))
def bstack111l11l1l_opy_(driver, bstack11ll11ll1ll_opy_):
  try:
    setattr(driver, bstack1111l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡇ࠱࠲ࡻࡖ࡬ࡴࡻ࡬ࡥࡕࡦࡥࡳ࠭ᛰ"), True)
    session = driver.session_id
    if session:
      bstack11ll1ll1111_opy_ = True
      current_url = driver.current_url
      try:
        url = urlparse(current_url)
      except Exception as e:
        bstack11ll1ll1111_opy_ = False
      bstack11ll1ll1111_opy_ = url.scheme in [bstack1111l1_opy_ (u"ࠢࡩࡶࡷࡴࠧᛱ"), bstack1111l1_opy_ (u"ࠣࡪࡷࡸࡵࡹࠢᛲ")]
      if bstack11ll1ll1111_opy_:
        if bstack11ll11ll1ll_opy_:
          logger.info(bstack1111l1_opy_ (u"ࠤࡖࡩࡹࡻࡰࠡࡨࡲࡶࠥࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡺࡥࡴࡶ࡬ࡲ࡬ࠦࡨࡢࡵࠣࡷࡹࡧࡲࡵࡧࡧ࠲ࠥࡇࡵࡵࡱࡰࡥࡹ࡫ࠠࡵࡧࡶࡸࠥࡩࡡࡴࡧࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡳࡳࠦࡷࡪ࡮࡯ࠤࡧ࡫ࡧࡪࡰࠣࡱࡴࡳࡥ࡯ࡶࡤࡶ࡮ࡲࡹ࠯ࠤᛳ"))
      return bstack11ll11ll1ll_opy_
  except Exception as e:
    logger.error(bstack1111l1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡶࡸࡦࡸࡴࡪࡰࡪࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡵࡦࡥࡳࠦࡦࡰࡴࠣࡸ࡭࡯ࡳࠡࡶࡨࡷࡹࠦࡣࡢࡵࡨ࠾ࠥࠨᛴ") + str(e))
    return False
def bstack1ll11llll1_opy_(driver, name, path):
  try:
    bstack1ll1111111l_opy_ = {
        bstack1111l1_opy_ (u"ࠫࡹ࡮ࡔࡦࡵࡷࡖࡺࡴࡕࡶ࡫ࡧࠫᛵ"): threading.current_thread().current_test_uuid,
        bstack1111l1_opy_ (u"ࠬࡺࡨࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪᛶ"): os.environ.get(bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᛷ"), bstack1111l1_opy_ (u"ࠧࠨᛸ")),
        bstack1111l1_opy_ (u"ࠨࡶ࡫ࡎࡼࡺࡔࡰ࡭ࡨࡲࠬ᛹"): os.environ.get(bstack1111l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡍ࡛࡙࠭᛺"), bstack1111l1_opy_ (u"ࠪࠫ᛻"))
    }
    bstack1ll11l111ll_opy_ = bstack1llll1llll_opy_.bstack1ll11ll11l1_opy_(EVENTS.bstack1ll111l11_opy_.value)
    logger.debug(bstack1111l1_opy_ (u"ࠫࡕ࡫ࡲࡧࡱࡵࡱ࡮ࡴࡧࠡࡵࡦࡥࡳࠦࡢࡦࡨࡲࡶࡪࠦࡳࡢࡸ࡬ࡲ࡬ࠦࡲࡦࡵࡸࡰࡹࡹࠧ᛼"))
    try:
      if (bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"ࠬ࡯ࡳࡂࡲࡳࡅ࠶࠷ࡹࡕࡧࡶࡸࠬ᛽"), None) and bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"࠭ࡡࡱࡲࡄ࠵࠶ࡿࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ᛾"), None)):
        scripts = {bstack1111l1_opy_ (u"ࠧࡴࡥࡤࡲࠬ᛿"): bstack1l1l11l11_opy_.perform_scan}
        bstack11ll1l1l111_opy_ = json.loads(scripts[bstack1111l1_opy_ (u"ࠣࡵࡦࡥࡳࠨᜀ")].replace(bstack1111l1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࠧᜁ"), bstack1111l1_opy_ (u"ࠥࠦᜂ")))
        bstack11ll1l1l111_opy_[bstack1111l1_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧᜃ")][bstack1111l1_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࠬᜄ")] = None
        scripts[bstack1111l1_opy_ (u"ࠨࡳࡤࡣࡱࠦᜅ")] = bstack1111l1_opy_ (u"ࠢࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࠥᜆ") + json.dumps(bstack11ll1l1l111_opy_)
        bstack1l1l11l11_opy_.bstack11l11l11l1_opy_(scripts)
        bstack1l1l11l11_opy_.store()
        logger.debug(driver.execute_script(bstack1l1l11l11_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack1l1l11l11_opy_.perform_scan, {bstack1111l1_opy_ (u"ࠣ࡯ࡨࡸ࡭ࡵࡤࠣᜇ"): name}))
      bstack1llll1llll_opy_.end(EVENTS.bstack1ll111l11_opy_.value, bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤᜈ"), bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣᜉ"), True, None)
    except Exception as error:
      bstack1llll1llll_opy_.end(EVENTS.bstack1ll111l11_opy_.value, bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᜊ"), bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᜋ"), False, str(error))
    bstack1ll11l111ll_opy_ = bstack1llll1llll_opy_.bstack11ll11l11l1_opy_(EVENTS.bstack1ll111l11ll_opy_.value)
    bstack1llll1llll_opy_.mark(bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠨ࠺ࡴࡶࡤࡶࡹࠨᜌ"))
    try:
      if (bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"ࠧࡪࡵࡄࡴࡵࡇ࠱࠲ࡻࡗࡩࡸࡺࠧᜍ"), None) and bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"ࠨࡣࡳࡴࡆ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪᜎ"), None)):
        scripts = {bstack1111l1_opy_ (u"ࠩࡶࡧࡦࡴࠧᜏ"): bstack1l1l11l11_opy_.perform_scan}
        bstack11ll1l1l111_opy_ = json.loads(scripts[bstack1111l1_opy_ (u"ࠥࡷࡨࡧ࡮ࠣᜐ")].replace(bstack1111l1_opy_ (u"ࠦࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࠢᜑ"), bstack1111l1_opy_ (u"ࠧࠨᜒ")))
        bstack11ll1l1l111_opy_[bstack1111l1_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩᜓ")][bstack1111l1_opy_ (u"ࠧ࡮ࡧࡷ࡬ࡴࡪ᜔ࠧ")] = None
        scripts[bstack1111l1_opy_ (u"ࠣࡵࡦࡥࡳࠨ᜕")] = bstack1111l1_opy_ (u"ࠤࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࠧ᜖") + json.dumps(bstack11ll1l1l111_opy_)
        bstack1l1l11l11_opy_.bstack11l11l11l1_opy_(scripts)
        bstack1l1l11l11_opy_.store()
        logger.debug(driver.execute_script(bstack1l1l11l11_opy_.perform_scan))
      else:
        logger.debug(driver.execute_async_script(bstack1l1l11l11_opy_.bstack11ll1l1ll11_opy_, bstack1ll1111111l_opy_))
      bstack1llll1llll_opy_.end(bstack1ll11l111ll_opy_, bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠥ࠾ࡸࡺࡡࡳࡶࠥ᜗"), bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠦ࠿࡫࡮ࡥࠤ᜘"),True, None)
    except Exception as error:
      bstack1llll1llll_opy_.end(bstack1ll11l111ll_opy_, bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧ᜙"), bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠨ࠺ࡦࡰࡧࠦ᜚"),False, str(error))
    logger.info(bstack1111l1_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡵࡧࡶࡸ࡮ࡴࡧࠡࡨࡲࡶࠥࡺࡨࡪࡵࠣࡸࡪࡹࡴࠡࡥࡤࡷࡪࠦࡨࡢࡵࠣࡩࡳࡪࡥࡥ࠰ࠥ᜛"))
  except Exception as bstack1ll11ll1ll1_opy_:
    logger.error(bstack1111l1_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡴࡨࡷࡺࡲࡴࡴࠢࡦࡳࡺࡲࡤࠡࡰࡲࡸࠥࡨࡥࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡧࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥ࠻ࠢࠥ᜜") + str(path) + bstack1111l1_opy_ (u"ࠤࠣࡉࡷࡸ࡯ࡳࠢ࠽ࠦ᜝") + str(bstack1ll11ll1ll1_opy_))
def bstack11ll1l1llll_opy_(driver):
    caps = driver.capabilities
    if caps.get(bstack1111l1_opy_ (u"ࠥࡴࡱࡧࡴࡧࡱࡵࡱࡓࡧ࡭ࡦࠤ᜞")) and str(caps.get(bstack1111l1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠥᜟ"))).lower() == bstack1111l1_opy_ (u"ࠧࡧ࡮ࡥࡴࡲ࡭ࡩࠨᜠ"):
        bstack1ll11l1l1l1_opy_ = caps.get(bstack1111l1_opy_ (u"ࠨࡡࡱࡲ࡬ࡹࡲࡀࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣᜡ")) or caps.get(bstack1111l1_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤᜢ"))
        if bstack1ll11l1l1l1_opy_ and int(str(bstack1ll11l1l1l1_opy_)) < bstack11ll1ll1l1l_opy_:
            return False
    return True
def bstack1ll11l1l1l_opy_(config):
  if bstack1111l1_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠨᜣ") in config:
        return config[bstack1111l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᜤ")]
  for platform in config.get(bstack1111l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ᜥ"), []):
      if bstack1111l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠫᜦ") in platform:
          return platform[bstack1111l1_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠬᜧ")]
  return None
def bstack1l11l1ll1l_opy_(bstack11l11l11l_opy_):
  try:
    browser_name = bstack11l11l11l_opy_[bstack1111l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟࡯ࡣࡰࡩࠬᜨ")]
    browser_version = bstack11l11l11l_opy_[bstack1111l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᜩ")]
    chrome_options = bstack11l11l11l_opy_[bstack1111l1_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡠࡱࡳࡸ࡮ࡵ࡮ࡴࠩᜪ")]
    try:
        bstack11ll11l1ll1_opy_ = int(browser_version.split(bstack1111l1_opy_ (u"ࠩ࠱ࠫᜫ"))[0])
    except ValueError as e:
        logger.error(bstack1111l1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡥࡲࡲࡻ࡫ࡲࡵ࡫ࡱ࡫ࠥࡨࡲࡰࡹࡶࡩࡷࠦࡶࡦࡴࡶ࡭ࡴࡴࠢᜬ") + str(e))
        return False
    if not (browser_name and browser_name.lower() == bstack1111l1_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࠫᜭ")):
        logger.warning(bstack1111l1_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡇࡵࡵࡱࡰࡥࡹ࡯࡯࡯ࠢࡺ࡭ࡱࡲࠠࡳࡷࡱࠤࡴࡴ࡬ࡺࠢࡲࡲࠥࡉࡨࡳࡱࡰࡩࠥࡨࡲࡰࡹࡶࡩࡷࡹ࠮ࠣᜮ"))
        return False
    if bstack11ll11l1ll1_opy_ < bstack11ll1l1ll1l_opy_.bstack1ll111l1l11_opy_:
        logger.warning(bstack11111l1ll1_opy_ (u"࠭ࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡶࡪࡷࡵࡪࡴࡨࡷࠥࡉࡨࡳࡱࡰࡩࠥࡼࡥࡳࡵ࡬ࡳࡳࠦࡻࡄࡑࡑࡗ࡙ࡇࡎࡕࡕ࠱ࡑࡎࡔࡉࡎࡗࡐࡣࡓࡕࡎࡠࡄࡖࡘࡆࡉࡋࡠࡋࡑࡊࡗࡇ࡟ࡂ࠳࠴࡝ࡤ࡙ࡕࡑࡒࡒࡖ࡙ࡋࡄࡠࡅࡋࡖࡔࡓࡅࡠࡘࡈࡖࡘࡏࡏࡏࡿࠣࡳࡷࠦࡨࡪࡩ࡫ࡩࡷ࠴ࠧᜯ"))
        return False
    if chrome_options and any(bstack1111l1_opy_ (u"ࠧ࠮࠯࡫ࡩࡦࡪ࡬ࡦࡵࡶࠫᜰ") in value for value in chrome_options.values() if isinstance(value, str)):
        logger.warning(bstack1111l1_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡲࡴࡺࠠࡳࡷࡱࠤࡴࡴࠠ࡭ࡧࡪࡥࡨࡿࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫࠮ࠡࡕࡺ࡭ࡹࡩࡨࠡࡶࡲࠤࡳ࡫ࡷࠡࡪࡨࡥࡩࡲࡥࡴࡵࠣࡱࡴࡪࡥࠡࡱࡵࠤࡦࡼ࡯ࡪࡦࠣࡹࡸ࡯࡮ࡨࠢ࡫ࡩࡦࡪ࡬ࡦࡵࡶࠤࡲࡵࡤࡦ࠰ࠥᜱ"))
        return False
    return True
  except Exception as e:
    logger.error(bstack1111l1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡨ࡮ࡥࡤ࡭࡬ࡲ࡬ࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠡࡵࡸࡴࡵࡵࡲࡵࠢࡩࡳࡷࠦ࡬ࡰࡥࡤࡰࠥࡉࡨࡳࡱࡰࡩ࠿ࠦࠢᜲ") + str(e))
    return False
def bstack1l11l1ll1_opy_(bstack1l11l1l11l_opy_, config):
    try:
      bstack1ll11ll1lll_opy_ = bstack1111l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠪᜳ") in config and config[bstack1111l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼ᜴ࠫ")] == True
      bstack11ll1l11ll1_opy_ = bstack1111l1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡗࡨࡧ࡬ࡦࠩ᜵") in config and str(config[bstack1111l1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡘࡩࡡ࡭ࡧࠪ᜶")]).lower() != bstack1111l1_opy_ (u"ࠧࡧࡣ࡯ࡷࡪ࠭᜷")
      if not (bstack1ll11ll1lll_opy_ and (not bstack1llllllll_opy_(config) or bstack11ll1l11ll1_opy_)):
        return bstack1l11l1l11l_opy_
      bstack11ll111lll1_opy_ = bstack1l1l11l11_opy_.bstack11ll11l11ll_opy_
      if bstack11ll111lll1_opy_ is None:
        logger.debug(bstack1111l1_opy_ (u"ࠣࡉࡲࡳ࡬ࡲࡥࠡࡥ࡫ࡶࡴࡳࡥࠡࡱࡳࡸ࡮ࡵ࡮ࡴࠢࡤࡶࡪࠦࡎࡰࡰࡨࠦ᜸"))
        return bstack1l11l1l11l_opy_
      bstack11ll1l11lll_opy_ = int(str(bstack11ll1ll1lll_opy_()).split(bstack1111l1_opy_ (u"ࠩ࠱ࠫ᜹"))[0])
      logger.debug(bstack1111l1_opy_ (u"ࠥࡗࡪࡲࡥ࡯࡫ࡸࡱࠥࡼࡥࡳࡵ࡬ࡳࡳࠦࡤࡦࡶࡨࡧࡹ࡫ࡤ࠻ࠢࠥ᜺") + str(bstack11ll1l11lll_opy_) + bstack1111l1_opy_ (u"ࠦࠧ᜻"))
      if bstack11ll1l11lll_opy_ == 3 and isinstance(bstack1l11l1l11l_opy_, dict) and bstack1111l1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬ᜼") in bstack1l11l1l11l_opy_ and bstack11ll111lll1_opy_ is not None:
        if bstack1111l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ᜽") not in bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ᜾")]:
          bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠨࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠨ᜿")][bstack1111l1_opy_ (u"ࠩࡪࡳࡴ࡭࠺ࡤࡪࡵࡳࡲ࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧᝀ")] = {}
        if bstack1111l1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨᝁ") in bstack11ll111lll1_opy_:
          if bstack1111l1_opy_ (u"ࠫࡦࡸࡧࡴࠩᝂ") not in bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᝃ")][bstack1111l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᝄ")]:
            bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᝅ")][bstack1111l1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᝆ")][bstack1111l1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧᝇ")] = []
          for arg in bstack11ll111lll1_opy_[bstack1111l1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨᝈ")]:
            if arg not in bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠫࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫᝉ")][bstack1111l1_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪᝊ")][bstack1111l1_opy_ (u"࠭ࡡࡳࡩࡶࠫᝋ")]:
              bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᝌ")][bstack1111l1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᝍ")][bstack1111l1_opy_ (u"ࠩࡤࡶ࡬ࡹࠧᝎ")].append(arg)
        if bstack1111l1_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧᝏ") in bstack11ll111lll1_opy_:
          if bstack1111l1_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨᝐ") not in bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᝑ")][bstack1111l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᝒ")]:
            bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᝓ")][bstack1111l1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭᝔")][bstack1111l1_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭᝕")] = []
          for ext in bstack11ll111lll1_opy_[bstack1111l1_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧ᝖")]:
            if ext not in bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠫࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫ᝗")][bstack1111l1_opy_ (u"ࠬ࡭࡯ࡰࡩ࠽ࡧ࡭ࡸ࡯࡮ࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ᝘")][bstack1111l1_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪ᝙")]:
              bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧ᝚")][bstack1111l1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭᝛")][bstack1111l1_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭᝜")].append(ext)
        if bstack1111l1_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩ᝝") in bstack11ll111lll1_opy_:
          if bstack1111l1_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪ᝞") not in bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠬࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬ᝟")][bstack1111l1_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫᝠ")]:
            bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᝡ")][bstack1111l1_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ᝢ")][bstack1111l1_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨᝣ")] = {}
          bstack11ll1ll11l1_opy_(bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠪࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠪᝤ")][bstack1111l1_opy_ (u"ࠫ࡬ࡵ࡯ࡨ࠼ࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩᝥ")][bstack1111l1_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫᝦ")],
                    bstack11ll111lll1_opy_[bstack1111l1_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬᝧ")])
        os.environ[bstack1111l1_opy_ (u"ࠧࡊࡕࡢࡒࡔࡔ࡟ࡃࡕࡗࡅࡈࡑ࡟ࡊࡐࡉࡖࡆࡥࡁ࠲࠳࡜ࡣࡘࡋࡓࡔࡋࡒࡒࠬᝨ")] = bstack1111l1_opy_ (u"ࠨࡶࡵࡹࡪ࠭ᝩ")
        return bstack1l11l1l11l_opy_
      else:
        chrome_options = None
        if isinstance(bstack1l11l1l11l_opy_, ChromeOptions):
          chrome_options = bstack1l11l1l11l_opy_
        elif isinstance(bstack1l11l1l11l_opy_, dict):
          for value in bstack1l11l1l11l_opy_.values():
            if isinstance(value, ChromeOptions):
              chrome_options = value
              break
        if chrome_options is None:
          chrome_options = ChromeOptions()
          if isinstance(bstack1l11l1l11l_opy_, dict):
            bstack1l11l1l11l_opy_[bstack1111l1_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࠪᝪ")] = chrome_options
          else:
            bstack1l11l1l11l_opy_ = chrome_options
        if bstack11ll111lll1_opy_ is not None:
          if bstack1111l1_opy_ (u"ࠪࡥࡷ࡭ࡳࠨᝫ") in bstack11ll111lll1_opy_:
                bstack11ll1ll11ll_opy_ = chrome_options.arguments or []
                new_args = bstack11ll111lll1_opy_[bstack1111l1_opy_ (u"ࠫࡦࡸࡧࡴࠩᝬ")]
                for arg in new_args:
                    if arg not in bstack11ll1ll11ll_opy_:
                        chrome_options.add_argument(arg)
          if bstack1111l1_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩ᝭") in bstack11ll111lll1_opy_:
                existing_extensions = chrome_options.experimental_options.get(bstack1111l1_opy_ (u"࠭ࡥࡹࡶࡨࡲࡸ࡯࡯࡯ࡵࠪᝮ"), [])
                bstack11ll1ll1l11_opy_ = bstack11ll111lll1_opy_[bstack1111l1_opy_ (u"ࠧࡦࡺࡷࡩࡳࡹࡩࡰࡰࡶࠫᝯ")]
                for extension in bstack11ll1ll1l11_opy_:
                    if extension not in existing_extensions:
                        chrome_options.add_encoded_extension(extension)
          if bstack1111l1_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧᝰ") in bstack11ll111lll1_opy_:
                bstack11ll1l11l1l_opy_ = chrome_options.experimental_options.get(bstack1111l1_opy_ (u"ࠩࡳࡶࡪ࡬ࡳࠨ᝱"), {})
                bstack11ll111ll1l_opy_ = bstack11ll111lll1_opy_[bstack1111l1_opy_ (u"ࠪࡴࡷ࡫ࡦࡴࠩᝲ")]
                bstack11ll1ll11l1_opy_(bstack11ll1l11l1l_opy_, bstack11ll111ll1l_opy_)
                chrome_options.add_experimental_option(bstack1111l1_opy_ (u"ࠫࡵࡸࡥࡧࡵࠪᝳ"), bstack11ll1l11l1l_opy_)
        os.environ[bstack1111l1_opy_ (u"ࠬࡏࡓࡠࡐࡒࡒࡤࡈࡓࡕࡃࡆࡏࡤࡏࡎࡇࡔࡄࡣࡆ࠷࠱࡚ࡡࡖࡉࡘ࡙ࡉࡐࡐࠪ᝴")] = bstack1111l1_opy_ (u"࠭ࡴࡳࡷࡨࠫ᝵")
        return bstack1l11l1l11l_opy_
    except Exception as e:
      logger.error(bstack1111l1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥࡧࡤࡥ࡫ࡱ࡫ࠥࡴ࡯࡯࠯ࡅࡗࠥ࡯࡮ࡧࡴࡤࠤࡦ࠷࠱ࡺࠢࡦ࡬ࡷࡵ࡭ࡦࠢࡲࡴࡹ࡯࡯࡯ࡵ࠽ࠤࠧ᝶") + str(e))
      return bstack1l11l1l11l_opy_