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
from browserstack_sdk.bstack1llll1ll1l_opy_ import bstack1l1l1111_opy_
from browserstack_sdk.bstack1111ll1l11_opy_ import RobotHandler
def bstack1ll11l1ll1_opy_(framework):
    if framework.lower() == bstack1111l1_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧᬮ"):
        return bstack1l1l1111_opy_.version()
    elif framework.lower() == bstack1111l1_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧᬯ"):
        return RobotHandler.version()
    elif framework.lower() == bstack1111l1_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩᬰ"):
        import behave
        return behave.__version__
    else:
        return bstack1111l1_opy_ (u"ࠪࡹࡳࡱ࡮ࡰࡹࡱࠫᬱ")
def bstack1ll1lll11_opy_():
    import importlib.metadata
    framework_name = []
    framework_version = []
    try:
        from selenium import webdriver
        framework_name.append(bstack1111l1_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠭ᬲ"))
        framework_version.append(importlib.metadata.version(bstack1111l1_opy_ (u"ࠧࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠢᬳ")))
    except:
        pass
    try:
        import playwright
        framework_name.append(bstack1111l1_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶ᬴ࠪ"))
        framework_version.append(importlib.metadata.version(bstack1111l1_opy_ (u"ࠢࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠦᬵ")))
    except:
        pass
    return {
        bstack1111l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᬶ"): bstack1111l1_opy_ (u"ࠩࡢࠫᬷ").join(framework_name),
        bstack1111l1_opy_ (u"ࠪࡺࡪࡸࡳࡪࡱࡱࠫᬸ"): bstack1111l1_opy_ (u"ࠫࡤ࠭ᬹ").join(framework_version)
    }