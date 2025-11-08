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
from bstack_utils.constants import bstack11ll1111lll_opy_
def bstack11ll111l1_opy_(bstack11ll1111ll1_opy_):
    from browserstack_sdk.sdk_cli.cli import cli
    from bstack_utils.helper import bstack11lll1ll_opy_
    host = bstack11lll1ll_opy_(cli.config, [bstack1111l1_opy_ (u"ࠤࡤࡴ࡮ࡹࠢប"), bstack1111l1_opy_ (u"ࠥࡥࡺࡺ࡯࡮ࡣࡷࡩࠧផ"), bstack1111l1_opy_ (u"ࠦࡦࡶࡩࠣព")], bstack11ll1111lll_opy_)
    return bstack1111l1_opy_ (u"ࠬࢁࡽ࠰ࡽࢀࠫភ").format(host, bstack11ll1111ll1_opy_)