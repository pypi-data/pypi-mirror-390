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
import threading
import logging
import bstack_utils.accessibility as bstack1ll1ll1l11_opy_
from bstack_utils.helper import bstack1l1ll111l_opy_
logger = logging.getLogger(__name__)
def bstack11ll1lll1l_opy_(bstack11l1l1111_opy_):
  return True if bstack11l1l1111_opy_ in threading.current_thread().__dict__.keys() else False
def bstack11l1lllll_opy_(context, *args):
    tags = getattr(args[0], bstack1111l1_opy_ (u"ࠩࡷࡥ࡬ࡹࠧអ"), [])
    bstack111l1l111_opy_ = bstack1ll1ll1l11_opy_.bstack11l1ll111l_opy_(tags)
    threading.current_thread().isA11yTest = bstack111l1l111_opy_
    try:
      bstack1lll11l1ll_opy_ = threading.current_thread().bstackSessionDriver if bstack11ll1lll1l_opy_(bstack1111l1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩឣ")) else context.browser
      if bstack1lll11l1ll_opy_ and bstack1lll11l1ll_opy_.session_id and bstack111l1l111_opy_ and bstack1l1ll111l_opy_(
              threading.current_thread(), bstack1111l1_opy_ (u"ࠫࡦ࠷࠱ࡺࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪឤ"), None):
          threading.current_thread().isA11yTest = bstack1ll1ll1l11_opy_.bstack111l11l1l_opy_(bstack1lll11l1ll_opy_, bstack111l1l111_opy_)
    except Exception as e:
       logger.debug(bstack1111l1_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡷࡥࡷࡺࠠࡢ࠳࠴ࡽࠥ࡯࡮ࠡࡤࡨ࡬ࡦࡼࡥ࠻ࠢࡾࢁࠬឥ").format(str(e)))
def bstack111ll1l1_opy_(bstack1lll11l1ll_opy_):
    if bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"࠭ࡩࡴࡃ࠴࠵ࡾ࡚ࡥࡴࡶࠪឦ"), None) and bstack1l1ll111l_opy_(
      threading.current_thread(), bstack1111l1_opy_ (u"ࠧࡢ࠳࠴ࡽࡕࡲࡡࡵࡨࡲࡶࡲ࠭ឧ"), None) and not bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"ࠨࡣ࠴࠵ࡾࡥࡳࡵࡱࡳࠫឨ"), False):
      threading.current_thread().a11y_stop = True
      bstack1ll1ll1l11_opy_.bstack1ll11llll1_opy_(bstack1lll11l1ll_opy_, name=bstack1111l1_opy_ (u"ࠤࠥឩ"), path=bstack1111l1_opy_ (u"ࠥࠦឪ"))