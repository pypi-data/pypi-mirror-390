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
import re
from bstack_utils.bstack1lll1l1111_opy_ import bstack1llllll1l1ll_opy_
def bstack1llllll11l1l_opy_(fixture_name):
    if fixture_name.startswith(bstack1111l1_opy_ (u"ࠩࡢࡼࡺࡴࡩࡵࡡࡶࡩࡹࡻࡰࡠࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠫῈ")):
        return bstack1111l1_opy_ (u"ࠪࡷࡪࡺࡵࡱ࠯ࡩࡹࡳࡩࡴࡪࡱࡱࠫΈ")
    elif fixture_name.startswith(bstack1111l1_opy_ (u"ࠫࡤࡾࡵ࡯࡫ࡷࡣࡸ࡫ࡴࡶࡲࡢࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫῊ")):
        return bstack1111l1_opy_ (u"ࠬࡹࡥࡵࡷࡳ࠱ࡲࡵࡤࡶ࡮ࡨࠫΉ")
    elif fixture_name.startswith(bstack1111l1_opy_ (u"࠭࡟ࡹࡷࡱ࡭ࡹࡥࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡨࡸࡲࡨࡺࡩࡰࡰࡢࡪ࡮ࡾࡴࡶࡴࡨࠫῌ")):
        return bstack1111l1_opy_ (u"ࠧࡵࡧࡤࡶࡩࡵࡷ࡯࠯ࡩࡹࡳࡩࡴࡪࡱࡱࠫ῍")
    elif fixture_name.startswith(bstack1111l1_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭῎")):
        return bstack1111l1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱ࠱ࡲࡵࡤࡶ࡮ࡨࠫ῏")
def bstack1llllll1ll11_opy_(fixture_name):
    return bool(re.match(bstack1111l1_opy_ (u"ࠪࡢࡤࡾࡵ࡯࡫ࡷࡣ࠭ࡹࡥࡵࡷࡳࢀࡹ࡫ࡡࡳࡦࡲࡻࡳ࠯࡟ࠩࡨࡸࡲࡨࡺࡩࡰࡰࡿࡱࡴࡪࡵ࡭ࡧࠬࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࠴ࠪࠨῐ"), fixture_name))
def bstack1llllll11111_opy_(fixture_name):
    return bool(re.match(bstack1111l1_opy_ (u"ࠫࡣࡥࡸࡶࡰ࡬ࡸࡤ࠮ࡳࡦࡶࡸࡴࢁࡺࡥࡢࡴࡧࡳࡼࡴࠩࡠ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࡡ࠱࠮ࠬῑ"), fixture_name))
def bstack1llllll1l111_opy_(fixture_name):
    return bool(re.match(bstack1111l1_opy_ (u"ࠬࡤ࡟ࡹࡷࡱ࡭ࡹࡥࠨࡴࡧࡷࡹࡵࢂࡴࡦࡣࡵࡨࡴࡽ࡮ࠪࡡࡦࡰࡦࡹࡳࡠࡨ࡬ࡼࡹࡻࡲࡦࡡ࠱࠮ࠬῒ"), fixture_name))
def bstack1llllll1111l_opy_(fixture_name):
    if fixture_name.startswith(bstack1111l1_opy_ (u"࠭࡟ࡹࡷࡱ࡭ࡹࡥࡳࡦࡶࡸࡴࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨΐ")):
        return bstack1111l1_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠳ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠨ῔"), bstack1111l1_opy_ (u"ࠨࡄࡈࡊࡔࡘࡅࡠࡇࡄࡇࡍ࠭῕")
    elif fixture_name.startswith(bstack1111l1_opy_ (u"ࠩࡢࡼࡺࡴࡩࡵࡡࡶࡩࡹࡻࡰࡠ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࠩῖ")):
        return bstack1111l1_opy_ (u"ࠪࡷࡪࡺࡵࡱ࠯ࡰࡳࡩࡻ࡬ࡦࠩῗ"), bstack1111l1_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡆࡒࡌࠨῘ")
    elif fixture_name.startswith(bstack1111l1_opy_ (u"ࠬࡥࡸࡶࡰ࡬ࡸࡤࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪῙ")):
        return bstack1111l1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮࠮ࡨࡸࡲࡨࡺࡩࡰࡰࠪῚ"), bstack1111l1_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠫΊ")
    elif fixture_name.startswith(bstack1111l1_opy_ (u"ࠨࡡࡻࡹࡳ࡯ࡴࡠࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ῜")):
        return bstack1111l1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱ࠱ࡲࡵࡤࡶ࡮ࡨࠫ῝"), bstack1111l1_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡄࡐࡑ࠭῞")
    return None, None
def bstack1llllll11l11_opy_(hook_name):
    if hook_name in [bstack1111l1_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪ῟"), bstack1111l1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴࠧῠ")]:
        return hook_name.capitalize()
    return hook_name
def bstack1llllll11lll_opy_(hook_name):
    if hook_name in [bstack1111l1_opy_ (u"࠭ࡳࡦࡶࡸࡴࡤ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠧῡ"), bstack1111l1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩ࠭ῢ")]:
        return bstack1111l1_opy_ (u"ࠨࡄࡈࡊࡔࡘࡅࡠࡇࡄࡇࡍ࠭ΰ")
    elif hook_name in [bstack1111l1_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡲࡨࡺࡲࡥࠨῤ"), bstack1111l1_opy_ (u"ࠪࡷࡪࡺࡵࡱࡡࡦࡰࡦࡹࡳࠨῥ")]:
        return bstack1111l1_opy_ (u"ࠫࡇࡋࡆࡐࡔࡈࡣࡆࡒࡌࠨῦ")
    elif hook_name in [bstack1111l1_opy_ (u"ࠬࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡧࡷࡱࡧࡹ࡯࡯࡯ࠩῧ"), bstack1111l1_opy_ (u"࠭ࡴࡦࡣࡵࡨࡴࡽ࡮ࡠ࡯ࡨࡸ࡭ࡵࡤࠨῨ")]:
        return bstack1111l1_opy_ (u"ࠧࡂࡈࡗࡉࡗࡥࡅࡂࡅࡋࠫῩ")
    elif hook_name in [bstack1111l1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡴࡪࡵ࡭ࡧࠪῪ"), bstack1111l1_opy_ (u"ࠩࡷࡩࡦࡸࡤࡰࡹࡱࡣࡨࡲࡡࡴࡵࠪΎ")]:
        return bstack1111l1_opy_ (u"ࠪࡅࡋ࡚ࡅࡓࡡࡄࡐࡑ࠭Ῥ")
    return hook_name
def bstack1llllll1l11l_opy_(node, scenario):
    if hasattr(node, bstack1111l1_opy_ (u"ࠫࡨࡧ࡬࡭ࡵࡳࡩࡨ࠭῭")):
        parts = node.nodeid.rsplit(bstack1111l1_opy_ (u"ࠧࡡࠢ΅"))
        params = parts[-1]
        return bstack1111l1_opy_ (u"ࠨࡻࡾࠢ࡞ࡿࢂࠨ`").format(scenario.name, params)
    return scenario.name
def bstack1lllll1lllll_opy_(node):
    try:
        examples = []
        if hasattr(node, bstack1111l1_opy_ (u"ࠧࡤࡣ࡯ࡰࡸࡶࡥࡤࠩ῰")):
            examples = list(node.callspec.params[bstack1111l1_opy_ (u"ࠨࡡࡳࡽࡹ࡫ࡳࡵࡡࡥࡨࡩࡥࡥࡹࡣࡰࡴࡱ࡫ࠧ῱")].values())
        return examples
    except:
        return []
def bstack1llllll11ll1_opy_(feature, scenario):
    return list(feature.tags) + list(scenario.tags)
def bstack1llllll111l1_opy_(report):
    try:
        status = bstack1111l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩῲ")
        if report.passed or (report.failed and hasattr(report, bstack1111l1_opy_ (u"ࠥࡻࡦࡹࡸࡧࡣ࡬ࡰࠧῳ"))):
            status = bstack1111l1_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫῴ")
        elif report.skipped:
            status = bstack1111l1_opy_ (u"ࠬࡹ࡫ࡪࡲࡳࡩࡩ࠭῵")
        bstack1llllll1l1ll_opy_(status)
    except:
        pass
def bstack11ll1111l1_opy_(status):
    try:
        bstack1llllll111ll_opy_ = bstack1111l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ῶ")
        if status == bstack1111l1_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧῷ"):
            bstack1llllll111ll_opy_ = bstack1111l1_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨῸ")
        elif status == bstack1111l1_opy_ (u"ࠩࡶ࡯࡮ࡶࡰࡦࡦࠪΌ"):
            bstack1llllll111ll_opy_ = bstack1111l1_opy_ (u"ࠪࡷࡰ࡯ࡰࡱࡧࡧࠫῺ")
        bstack1llllll1l1ll_opy_(bstack1llllll111ll_opy_)
    except:
        pass
def bstack1llllll1l1l1_opy_(item=None, report=None, summary=None, extra=None):
    return