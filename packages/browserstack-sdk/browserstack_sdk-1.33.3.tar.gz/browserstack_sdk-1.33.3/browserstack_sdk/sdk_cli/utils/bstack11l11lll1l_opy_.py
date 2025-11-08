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
import shutil
import tempfile
import threading
import urllib.request
import uuid
from pathlib import Path
import logging
import re
from bstack_utils.helper import bstack1l1ll1111l1_opy_
bstack11lll111l11_opy_ = 100 * 1024 * 1024 # 100 bstack11lll1111l1_opy_
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
bstack1l1ll1lllll_opy_ = bstack1l1ll1111l1_opy_()
bstack1l1ll1l111l_opy_ = bstack1111l1_opy_ (u"ࠣࡗࡳࡰࡴࡧࡤࡦࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹ࠭ࠣᘙ")
bstack11llll111ll_opy_ = bstack1111l1_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧᘚ")
bstack11llll11l11_opy_ = bstack1111l1_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢᘛ")
bstack11llll11l1l_opy_ = bstack1111l1_opy_ (u"ࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢᘜ")
bstack11lll111l1l_opy_ = bstack1111l1_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦᘝ")
_11ll1lll11l_opy_ = threading.local()
def bstack1l111111111_opy_(test_framework_state, test_hook_state):
    bstack1111l1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡓࡦࡶࠣࡸ࡭࡫ࠠࡤࡷࡵࡶࡪࡴࡴࠡࡶࡨࡷࡹࠦࡥࡷࡧࡱࡸࠥࡹࡴࡢࡶࡨࠤ࡮ࡴࠠࡵࡪࡵࡩࡦࡪ࠭࡭ࡱࡦࡥࡱࠦࡳࡵࡱࡵࡥ࡬࡫࠮ࠋࠢࠣࠤ࡚ࠥࡨࡪࡵࠣࡪࡺࡴࡣࡵ࡫ࡲࡲࠥࡹࡨࡰࡷ࡯ࡨࠥࡨࡥࠡࡥࡤࡰࡱ࡫ࡤࠡࡤࡼࠤࡹ࡮ࡥࠡࡧࡹࡩࡳࡺࠠࡩࡣࡱࡨࡱ࡫ࡲࠡࠪࡶࡹࡨ࡮ࠠࡢࡵࠣࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴࠪࠌࠣࠤࠥࠦࡢࡦࡨࡲࡶࡪࠦࡡ࡯ࡻࠣࡪ࡮ࡲࡥࠡࡷࡳࡰࡴࡧࡤࡴࠢࡲࡧࡨࡻࡲ࠯ࠌࠣࠤࠥࠦࠢࠣࠤᘞ")
    _11ll1lll11l_opy_.test_framework_state = test_framework_state
    _11ll1lll11l_opy_.test_hook_state = test_hook_state
def bstack11lll11l111_opy_():
    bstack1111l1_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࡓࡧࡷࡶ࡮࡫ࡶࡦࠢࡷ࡬ࡪࠦࡣࡶࡴࡵࡩࡳࡺࠠࡵࡧࡶࡸࠥ࡫ࡶࡦࡰࡷࠤࡸࡺࡡࡵࡧࠣࡪࡷࡵ࡭ࠡࡶ࡫ࡶࡪࡧࡤ࠮࡮ࡲࡧࡦࡲࠠࡴࡶࡲࡶࡦ࡭ࡥ࠯ࠌࠣࠤࠥࠦࡒࡦࡶࡸࡶࡳࡹࠠࡢࠢࡷࡹࡵࡲࡥࠡࠪࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦ࠮ࠣࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩ࠮ࠦ࡯ࡳࠢࠫࡒࡴࡴࡥ࠭ࠢࡑࡳࡳ࡫ࠩࠡ࡫ࡩࠤࡳࡵࡴࠡࡵࡨࡸ࠳ࠐࠠࠡࠢࠣࠦࠧࠨᘟ")
    return (
        getattr(_11ll1lll11l_opy_, bstack1111l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࠨᘠ"), None),
        getattr(_11ll1lll11l_opy_, bstack1111l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࠫᘡ"), None)
    )
class bstack1l11111l_opy_:
    bstack1111l1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࡊ࡮ࡲࡥࡖࡲ࡯ࡳࡦࡪࡥࡳࠢࡳࡶࡴࡼࡩࡥࡧࡶࠤ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡧ࡬ࡪࡶࡼࠤࡹࡵࠠࡶࡲ࡯ࡳࡦࡪࠠࡢࡰࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࠠࡣࡣࡶࡩࡩࠦ࡯࡯ࠢࡷ࡬ࡪࠦࡧࡪࡸࡨࡲࠥ࡬ࡩ࡭ࡧࠣࡴࡦࡺࡨ࠯ࠌࠣࠤࠥࠦࡉࡵࠢࡶࡹࡵࡶ࡯ࡳࡶࡶࠤࡧࡵࡴࡩࠢ࡯ࡳࡨࡧ࡬ࠡࡨ࡬ࡰࡪࠦࡰࡢࡶ࡫ࡷࠥࡧ࡮ࡥࠢࡋࡘ࡙ࡖ࠯ࡉࡖࡗࡔࡘࠦࡕࡓࡎࡶ࠰ࠥࡧ࡮ࡥࠢࡦࡳࡵ࡯ࡥࡴࠢࡷ࡬ࡪࠦࡦࡪ࡮ࡨࠤ࡮ࡴࡴࡰࠢࡤࠤࡩ࡫ࡳࡪࡩࡱࡥࡹ࡫ࡤࠋࠢࠣࠤࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹࠡࡹ࡬ࡸ࡭࡯࡮ࠡࡶ࡫ࡩࠥࡻࡳࡦࡴࠪࡷࠥ࡮࡯࡮ࡧࠣࡪࡴࡲࡤࡦࡴࠣࡹࡳࡪࡥࡳࠢࢁ࠳࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠳࡚ࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠱ࠎࠥࠦࠠࠡࡋࡩࠤࡦࡴࠠࡰࡲࡷ࡭ࡴࡴࡡ࡭ࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠦࡰࡢࡴࡤࡱࡪࡺࡥࡳࠢࠫ࡭ࡳࠦࡊࡔࡑࡑࠤ࡫ࡵࡲ࡮ࡣࡷ࠭ࠥ࡯ࡳࠡࡲࡵࡳࡻ࡯ࡤࡦࡦࠣࡥࡳࡪࠠࡤࡱࡱࡸࡦ࡯࡮ࡴࠢࡤࠤࡹࡸࡵࡵࡪࡼࠤࡻࡧ࡬ࡶࡧࠍࠤࠥࠦࠠࡧࡱࡵࠤࡹ࡮ࡥࠡ࡭ࡨࡽࠥࠨࡢࡶ࡫࡯ࡨࡆࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠣ࠮ࠣࡸ࡭࡫ࠠࡧ࡫࡯ࡩࠥࡽࡩ࡭࡮ࠣࡦࡪࠦࡰ࡭ࡣࡦࡩࡩࠦࡩ࡯ࠢࡷ࡬ࡪࠦࠢࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࠦࠥ࡬࡯࡭ࡦࡨࡶࡀࠦ࡯ࡵࡪࡨࡶࡼ࡯ࡳࡦ࠮ࠍࠤࠥࠦࠠࡪࡶࠣࡨࡪ࡬ࡡࡶ࡮ࡷࡷࠥࡺ࡯ࠡࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧ࠴ࠊࠡࠢࠣࠤ࡙࡮ࡩࡴࠢࡹࡩࡷࡹࡩࡰࡰࠣࡳ࡫ࠦࡡࡥࡦࡢࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࠠࡪࡵࠣࡥࠥࡼ࡯ࡪࡦࠣࡱࡪࡺࡨࡰࡦ⠗࡭ࡹࠦࡨࡢࡰࡧࡰࡪࡹࠠࡢ࡮࡯ࠤࡪࡸࡲࡰࡴࡶࠤ࡬ࡸࡡࡤࡧࡩࡹࡱࡲࡹࠡࡤࡼࠤࡱࡵࡧࡨ࡫ࡱ࡫ࠏࠦࠠࠡࠢࡷ࡬ࡪࡳࠠࡢࡰࡧࠤࡸ࡯࡭ࡱ࡮ࡼࠤࡷ࡫ࡴࡶࡴࡱ࡭ࡳ࡭ࠠࡸ࡫ࡷ࡬ࡴࡻࡴࠡࡶ࡫ࡶࡴࡽࡩ࡯ࡩࠣࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࡹ࠮ࠋࠢࠣࠤࠥࠨࠢࠣᘢ")
    @staticmethod
    def upload_attachment(bstack11ll1lll1l1_opy_: str, *bstack11ll1lllll1_opy_) -> None:
        if not bstack11ll1lll1l1_opy_ or not bstack11ll1lll1l1_opy_.strip():
            logger.error(bstack1111l1_opy_ (u"ࠦࡦࡪࡤࡠࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠥ࡬ࡡࡪ࡮ࡨࡨ࠿ࠦࡐࡳࡱࡹ࡭ࡩ࡫ࡤࠡࡨ࡬ࡰࡪࠦࡰࡢࡶ࡫ࠤ࡮ࡹࠠࡦ࡯ࡳࡸࡾࠦ࡯ࡳࠢࡑࡳࡳ࡫࠮ࠣᘣ"))
            return
        bstack11lll11l11l_opy_ = bstack11ll1lllll1_opy_[0] if bstack11ll1lllll1_opy_ and len(bstack11ll1lllll1_opy_) > 0 else None
        bstack11ll1llll11_opy_ = None
        test_framework_state, test_hook_state = bstack11lll11l111_opy_()
        try:
            if bstack11ll1lll1l1_opy_.startswith(bstack1111l1_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨᘤ")) or bstack11ll1lll1l1_opy_.startswith(bstack1111l1_opy_ (u"ࠨࡨࡵࡶࡳࡷ࠿࠵࠯ࠣᘥ")):
                logger.debug(bstack1111l1_opy_ (u"ࠢࡑࡣࡷ࡬ࠥ࡯ࡳࠡ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡨࠥࡧࡳࠡࡗࡕࡐࡀࠦࡤࡰࡹࡱࡰࡴࡧࡤࡪࡰࡪࠤࡹ࡮ࡥࠡࡨ࡬ࡰࡪ࠴ࠢᘦ"))
                url = bstack11ll1lll1l1_opy_
                bstack11lll1111ll_opy_ = str(uuid.uuid4())
                bstack11lll11111l_opy_ = os.path.basename(urllib.request.urlparse(url).path)
                if not bstack11lll11111l_opy_ or not bstack11lll11111l_opy_.strip():
                    bstack11lll11111l_opy_ = bstack11lll1111ll_opy_
                temp_file = tempfile.NamedTemporaryFile(delete=False,
                                                        prefix=bstack1111l1_opy_ (u"ࠣࡷࡳࡰࡴࡧࡤࡠࠤᘧ") + bstack11lll1111ll_opy_ + bstack1111l1_opy_ (u"ࠤࡢࠦᘨ"),
                                                        suffix=bstack1111l1_opy_ (u"ࠥࡣࠧᘩ") + bstack11lll11111l_opy_)
                with urllib.request.urlopen(url) as response, open(temp_file.name, bstack1111l1_opy_ (u"ࠫࡼࡨࠧᘪ")) as out_file:
                    shutil.copyfileobj(response, out_file)
                bstack11ll1llll11_opy_ = Path(temp_file.name)
                logger.debug(bstack1111l1_opy_ (u"ࠧࡊ࡯ࡸࡰ࡯ࡳࡦࡪࡥࡥࠢࡩ࡭ࡱ࡫ࠠࡵࡱࠣࡸࡪࡳࡰࡰࡴࡤࡶࡾࠦ࡬ࡰࡥࡤࡸ࡮ࡵ࡮࠻ࠢࡾࢁࠧᘫ").format(bstack11ll1llll11_opy_))
            else:
                bstack11ll1llll11_opy_ = Path(bstack11ll1lll1l1_opy_)
                logger.debug(bstack1111l1_opy_ (u"ࠨࡐࡢࡶ࡫ࠤ࡮ࡹࠠࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡧࠤࡦࡹࠠ࡭ࡱࡦࡥࡱࠦࡦࡪ࡮ࡨ࠾ࠥࢁࡽࠣᘬ").format(bstack11ll1llll11_opy_))
        except Exception as e:
            logger.error(bstack1111l1_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡳࡧࡺࡡࡪࡰࠣࡪ࡮ࡲࡥࠡࡨࡵࡳࡲࠦࡰࡢࡶ࡫࠳࡚ࡘࡌ࠻ࠢࡾࢁࠧᘭ").format(e))
            return
        if bstack11ll1llll11_opy_ is None or not bstack11ll1llll11_opy_.exists():
            logger.error(bstack1111l1_opy_ (u"ࠣࡕࡲࡹࡷࡩࡥࠡࡨ࡬ࡰࡪࠦࡤࡰࡧࡶࠤࡳࡵࡴࠡࡧࡻ࡭ࡸࡺ࠺ࠡࡽࢀࠦᘮ").format(bstack11ll1llll11_opy_))
            return
        if bstack11ll1llll11_opy_.stat().st_size > bstack11lll111l11_opy_:
            logger.error(bstack1111l1_opy_ (u"ࠤࡉ࡭ࡱ࡫ࠠࡴ࡫ࡽࡩࠥ࡫ࡸࡤࡧࡨࡨࡸࠦ࡭ࡢࡺ࡬ࡱࡺࡳࠠࡢ࡮࡯ࡳࡼ࡫ࡤࠡࡵ࡬ࡾࡪࠦ࡯ࡧࠢࡾࢁࠧᘯ").format(bstack11lll111l11_opy_))
            return
        bstack11ll1lll1ll_opy_ = bstack1111l1_opy_ (u"ࠥࡘࡪࡹࡴࡍࡧࡹࡩࡱࠨᘰ")
        if bstack11lll11l11l_opy_:
            try:
                params = json.loads(bstack11lll11l11l_opy_)
                if bstack1111l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠨᘱ") in params and params.get(bstack1111l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࠢᘲ")) is True:
                    bstack11ll1lll1ll_opy_ = bstack1111l1_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠥᘳ")
            except Exception as bstack11ll1llllll_opy_:
                logger.error(bstack1111l1_opy_ (u"ࠢࡋࡕࡒࡒࠥࡶࡡࡳࡵ࡬ࡲ࡬ࠦࡥࡳࡴࡲࡶࠥ࡯࡮ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡕࡧࡲࡢ࡯ࡶ࠾ࠥࢁࡽࠣᘴ").format(bstack11ll1llllll_opy_))
        bstack11lll111ll1_opy_ = False
        from browserstack_sdk.sdk_cli.bstack1ll1ll11111_opy_ import bstack1lll111ll11_opy_
        if test_framework_state in bstack1lll111ll11_opy_.bstack1l1111ll111_opy_:
            if bstack11ll1lll1ll_opy_ == bstack11llll11l11_opy_:
                bstack11lll111ll1_opy_ = True
            bstack11ll1lll1ll_opy_ = bstack11llll11l1l_opy_
        try:
            platform_index = os.environ[bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨᘵ")]
            target_dir = os.path.join(bstack1l1ll1lllll_opy_, bstack1l1ll1l111l_opy_ + str(platform_index),
                                      bstack11ll1lll1ll_opy_)
            if bstack11lll111ll1_opy_:
                target_dir = os.path.join(target_dir, bstack11lll111l1l_opy_)
            os.makedirs(target_dir, exist_ok=True)
            logger.debug(bstack1111l1_opy_ (u"ࠤࡆࡶࡪࡧࡴࡦࡦ࠲ࡺࡪࡸࡩࡧ࡫ࡨࡨࠥࡺࡡࡳࡩࡨࡸࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹ࠻ࠢࡾࢁࠧᘶ").format(target_dir))
            file_name = os.path.basename(bstack11ll1llll11_opy_)
            bstack11ll1lll111_opy_ = os.path.join(target_dir, file_name)
            if os.path.exists(bstack11ll1lll111_opy_):
                base_name, extension = os.path.splitext(file_name)
                bstack11lll111111_opy_ = 1
                while os.path.exists(os.path.join(target_dir, base_name + str(bstack11lll111111_opy_) + extension)):
                    bstack11lll111111_opy_ += 1
                bstack11ll1lll111_opy_ = os.path.join(target_dir, base_name + str(bstack11lll111111_opy_) + extension)
            shutil.copy(bstack11ll1llll11_opy_, bstack11ll1lll111_opy_)
            logger.info(bstack1111l1_opy_ (u"ࠥࡊ࡮ࡲࡥࠡࡵࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿࠠࡤࡱࡳ࡭ࡪࡪࠠࡵࡱ࠽ࠤࢀࢃࠢᘷ").format(bstack11ll1lll111_opy_))
        except Exception as e:
            logger.error(bstack1111l1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡱࡴࡼࡩ࡯ࡩࠣࡪ࡮ࡲࡥࠡࡶࡲࠤࡹࡧࡲࡨࡧࡷࠤࡩ࡯ࡲࡦࡥࡷࡳࡷࡿ࠺ࠡࡽࢀࠦᘸ").format(e))
            return
        finally:
            if bstack11ll1lll1l1_opy_.startswith(bstack1111l1_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨᘹ")) or bstack11ll1lll1l1_opy_.startswith(bstack1111l1_opy_ (u"ࠨࡨࡵࡶࡳࡷ࠿࠵࠯ࠣᘺ")):
                try:
                    if bstack11ll1llll11_opy_ is not None and bstack11ll1llll11_opy_.exists():
                        bstack11ll1llll11_opy_.unlink()
                        logger.debug(bstack1111l1_opy_ (u"ࠢࡕࡧࡰࡴࡴࡸࡡࡳࡻࠣࡪ࡮ࡲࡥࠡࡦࡨࡰࡪࡺࡥࡥ࠼ࠣࡿࢂࠨᘻ").format(bstack11ll1llll11_opy_))
                except Exception as ex:
                    logger.error(bstack1111l1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡥࡧ࡯ࡩࡹ࡯࡮ࡨࠢࡷࡩࡲࡶ࡯ࡳࡣࡵࡽࠥ࡬ࡩ࡭ࡧ࠽ࠤࢀࢃࠢᘼ").format(ex))
    @staticmethod
    def bstack11ll11l1l1_opy_() -> None:
        bstack1111l1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡄࡦ࡮ࡨࡸࡪࡹࠠࡢ࡮࡯ࠤ࡫ࡵ࡬ࡥࡧࡵࡷࠥࡽࡨࡰࡵࡨࠤࡳࡧ࡭ࡦࡵࠣࡷࡹࡧࡲࡵࠢࡺ࡭ࡹ࡮ࠠࠣࡗࡳࡰࡴࡧࡤࡦࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹ࠭ࠣࠢࡩࡳࡱࡲ࡯ࡸࡧࡧࠤࡧࡿࠠࡢࠢࡱࡹࡲࡨࡥࡳࠢ࡬ࡲࠏࠦࠠࠡࠢࠣࠤࠥࠦࡴࡩࡧࠣࡹࡸ࡫ࡲࠨࡵࠣࢂ࠴࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠦࠧࠨᘽ")
        bstack11ll1llll1l_opy_ = bstack1l1ll1111l1_opy_()
        pattern = re.compile(bstack1111l1_opy_ (u"ࡵ࡚ࠦࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠰ࡠࡩ࠱ࠢᘾ"))
        if os.path.exists(bstack11ll1llll1l_opy_):
            for item in os.listdir(bstack11ll1llll1l_opy_):
                bstack11lll111lll_opy_ = os.path.join(bstack11ll1llll1l_opy_, item)
                if os.path.isdir(bstack11lll111lll_opy_) and pattern.fullmatch(item):
                    try:
                        shutil.rmtree(bstack11lll111lll_opy_)
                    except Exception as e:
                        logger.error(bstack1111l1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡨࡪࡲࡥࡵ࡫ࡱ࡫ࠥࡪࡩࡳࡧࡦࡸࡴࡸࡹ࠻ࠢࡾࢁࠧᘿ").format(e))
        else:
            logger.info(bstack1111l1_opy_ (u"࡚ࠧࡨࡦࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥࡪ࡯ࡦࡵࠣࡲࡴࡺࠠࡦࡺ࡬ࡷࡹࡀࠠࡼࡿࠥᙀ").format(bstack11ll1llll1l_opy_))