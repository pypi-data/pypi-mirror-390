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
import tempfile
import os
import time
from datetime import datetime
from bstack_utils.bstack11ll1111l11_opy_ import bstack11l1lllll1l_opy_
from bstack_utils.constants import bstack11l1l1l111l_opy_, bstack1l1l11l1ll_opy_
from bstack_utils.bstack11llll11l_opy_ import bstack11l111llll_opy_
from bstack_utils import bstack1lll1l11l_opy_
bstack11l11lll1ll_opy_ = 10
class bstack1ll1111l1l_opy_:
    def __init__(self, bstack1lll11l11l_opy_, config, bstack11l11ll1ll1_opy_=0):
        self.bstack11l11llll11_opy_ = set()
        self.lock = threading.Lock()
        self.bstack11l11ll1lll_opy_ = bstack1111l1_opy_ (u"ࠤࡾࢁ࠴ࡺࡥࡴࡶࡲࡶࡨ࡮ࡥࡴࡶࡵࡥࡹ࡯࡯࡯࠱ࡤࡴ࡮࠵ࡶ࠲࠱ࡩࡥ࡮ࡲࡥࡥ࠯ࡷࡩࡸࡺࡳࠣᬆ").format(bstack11l1l1l111l_opy_)
        self.bstack11l1l1111l1_opy_ = os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"ࠥࡥࡧࡵࡲࡵࡡࡥࡹ࡮ࡲࡤࡠࡽࢀࠦᬇ").format(os.environ.get(bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩᬈ"))))
        self.bstack11l1l111111_opy_ = os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࡤࡺࡥࡴࡶࡶࡣࢀࢃ࠮ࡵࡺࡷࠦᬉ").format(os.environ.get(bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡋ࡙ࡇࡥࡕࡖࡋࡇࠫᬊ"))))
        self.bstack11l1l11111l_opy_ = 2
        self.bstack1lll11l11l_opy_ = bstack1lll11l11l_opy_
        self.config = config
        self.logger = bstack1lll1l11l_opy_.get_logger(__name__, bstack1l1l11l1ll_opy_)
        self.bstack11l11ll1ll1_opy_ = bstack11l11ll1ll1_opy_
        self.bstack11l1l111lll_opy_ = False
        self.bstack11l1l11l111_opy_ = not (
                            os.environ.get(bstack1111l1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡖࡋࡏࡈࡤࡘࡕࡏࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗࠨᬋ")) and
                            os.environ.get(bstack1111l1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡏࡑࡇࡉࡤࡏࡎࡅࡇ࡛ࠦᬌ")) and
                            os.environ.get(bstack1111l1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡒࡘࡆࡒ࡟ࡏࡑࡇࡉࡤࡉࡏࡖࡐࡗࠦᬍ"))
                        )
        if bstack11l111llll_opy_.bstack11l1l1111ll_opy_(config):
            self.bstack11l1l11111l_opy_ = bstack11l111llll_opy_.bstack11l1l111l11_opy_(config, self.bstack11l11ll1ll1_opy_)
            self.bstack11l11lll1l1_opy_()
    def bstack11l11lll111_opy_(self):
        return bstack1111l1_opy_ (u"ࠥࡿࢂࡥࡻࡾࠤᬎ").format(self.config.get(bstack1111l1_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧᬏ")), os.environ.get(bstack1111l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇ࡛ࡉࡍࡆࡢࡖ࡚ࡔ࡟ࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕࠫᬐ")))
    def bstack11l1l111ll1_opy_(self):
        try:
            if self.bstack11l1l11l111_opy_:
                return
            with self.lock:
                try:
                    with open(self.bstack11l1l111111_opy_, bstack1111l1_opy_ (u"ࠨࡲࠣᬑ")) as f:
                        bstack11l1l11l1l1_opy_ = set(line.strip() for line in f if line.strip())
                except FileNotFoundError:
                    bstack11l1l11l1l1_opy_ = set()
                bstack11l1l11l1ll_opy_ = bstack11l1l11l1l1_opy_ - self.bstack11l11llll11_opy_
                if not bstack11l1l11l1ll_opy_:
                    return
                self.bstack11l11llll11_opy_.update(bstack11l1l11l1ll_opy_)
                data = {bstack1111l1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࡔࡦࡵࡷࡷࠧᬒ"): list(self.bstack11l11llll11_opy_), bstack1111l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠦᬓ"): self.config.get(bstack1111l1_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬᬔ")), bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡔࡸࡲࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠣᬕ"): os.environ.get(bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡆ࡚ࡏࡌࡅࡡࡕ࡙ࡓࡥࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠪᬖ")), bstack1111l1_opy_ (u"ࠧࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠥᬗ"): self.config.get(bstack1111l1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫᬘ"))}
            response = bstack11l1lllll1l_opy_.bstack11l11llll1l_opy_(self.bstack11l11ll1lll_opy_, data)
            if response.get(bstack1111l1_opy_ (u"ࠢࡴࡶࡤࡸࡺࡹࠢᬙ")) == 200:
                self.logger.debug(bstack1111l1_opy_ (u"ࠣࡕࡸࡧࡨ࡫ࡳࡴࡨࡸࡰࡱࡿࠠࡴࡧࡱࡸࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡺࡥࡴࡶࡶ࠾ࠥࢁࡽࠣᬚ").format(data))
            else:
                self.logger.debug(bstack1111l1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡥ࡯ࡦࠣࡪࡦ࡯࡬ࡦࡦࠣࡸࡪࡹࡴࡴ࠼ࠣࡿࢂࠨᬛ").format(response))
        except Exception as e:
            self.logger.debug(bstack1111l1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡤࡶࡴ࡬ࡲ࡬ࠦࡳࡦࡰࡧ࡭ࡳ࡭ࠠࡧࡣ࡬ࡰࡪࡪࠠࡵࡧࡶࡸࡸࡀࠠࡼࡿࠥᬜ").format(e))
    def bstack11l11lllll1_opy_(self):
        if self.bstack11l1l11l111_opy_:
            with self.lock:
                try:
                    with open(self.bstack11l1l111111_opy_, bstack1111l1_opy_ (u"ࠦࡷࠨᬝ")) as f:
                        bstack11l11llllll_opy_ = set(line.strip() for line in f if line.strip())
                    failed_count = len(bstack11l11llllll_opy_)
                except FileNotFoundError:
                    failed_count = 0
                self.logger.debug(bstack1111l1_opy_ (u"ࠧࡖ࡯࡭࡮ࡨࡨࠥ࡬ࡡࡪ࡮ࡨࡨࠥࡺࡥࡴࡶࡶࠤࡨࡵࡵ࡯ࡶࠣࠬࡱࡵࡣࡢ࡮ࠬ࠾ࠥࢁࡽࠣᬞ").format(failed_count))
                if failed_count >= self.bstack11l1l11111l_opy_:
                    self.logger.info(bstack1111l1_opy_ (u"ࠨࡔࡩࡴࡨࡷ࡭ࡵ࡬ࡥࠢࡦࡶࡴࡹࡳࡦࡦࠣࠬࡱࡵࡣࡢ࡮ࠬ࠾ࠥࢁࡽࠡࡀࡀࠤࢀࢃࠢᬟ").format(failed_count, self.bstack11l1l11111l_opy_))
                    self.bstack11l1l11l11l_opy_(failed_count)
                    self.bstack11l1l111lll_opy_ = True
            return
        try:
            response = bstack11l1lllll1l_opy_.bstack11l11lllll1_opy_(bstack1111l1_opy_ (u"ࠢࡼࡿࡂࡦࡺ࡯࡬ࡥࡐࡤࡱࡪࡃࡻࡾࠨࡥࡹ࡮ࡲࡤࡓࡷࡱࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸ࠽ࡼࡿࠩࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥ࠾ࡽࢀࠦᬠ").format(self.bstack11l11ll1lll_opy_, self.config.get(bstack1111l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫᬡ")), os.environ.get(bstack1111l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡓࡗࡑࡣࡎࡊࡅࡏࡖࡌࡊࡎࡋࡒࠨᬢ")), self.config.get(bstack1111l1_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨᬣ"))))
            if response.get(bstack1111l1_opy_ (u"ࠦࡸࡺࡡࡵࡷࡶࠦᬤ")) == 200:
                failed_count = response.get(bstack1111l1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨ࡙࡫ࡳࡵࡵࡆࡳࡺࡴࡴࠣᬥ"), 0)
                self.logger.debug(bstack1111l1_opy_ (u"ࠨࡐࡰ࡮࡯ࡩࡩࠦࡦࡢ࡫࡯ࡩࡩࠦࡴࡦࡵࡷࡷࠥࡩ࡯ࡶࡰࡷ࠾ࠥࢁࡽࠣᬦ").format(failed_count))
                if failed_count >= self.bstack11l1l11111l_opy_:
                    self.logger.info(bstack1111l1_opy_ (u"ࠢࡕࡪࡵࡩࡸ࡮࡯࡭ࡦࠣࡧࡷࡵࡳࡴࡧࡧ࠾ࠥࢁࡽࠡࡀࡀࠤࢀࢃࠢᬧ").format(failed_count, self.bstack11l1l11111l_opy_))
                    self.bstack11l1l11l11l_opy_(failed_count)
                    self.bstack11l1l111lll_opy_ = True
            else:
                self.logger.error(bstack1111l1_opy_ (u"ࠣࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡵࡵ࡬࡭ࠢࡩࡥ࡮ࡲࡥࡥࠢࡷࡩࡸࡺࡳ࠻ࠢࡾࢁࠧᬨ").format(response))
        except Exception as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡪࡵࡳ࡫ࡱ࡫ࠥࡶ࡯࡭࡮࡬ࡲ࡬ࡀࠠࡼࡿࠥᬩ").format(e))
    def bstack11l1l11l11l_opy_(self, failed_count):
        with open(self.bstack11l1l1111l1_opy_, bstack1111l1_opy_ (u"ࠥࡻࠧᬪ")) as f:
            f.write(bstack1111l1_opy_ (u"࡙ࠦ࡮ࡲࡦࡵ࡫ࡳࡱࡪࠠࡤࡴࡲࡷࡸ࡫ࡤࠡࡣࡷࠤࢀࢃ࡜࡯ࠤᬫ").format(datetime.now()))
            f.write(bstack1111l1_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺࡥࡴࡶࡶࠤࡨࡵࡵ࡯ࡶ࠽ࠤࢀࢃ࡜࡯ࠤᬬ").format(failed_count))
        self.logger.debug(bstack1111l1_opy_ (u"ࠨࡁࡣࡱࡵࡸࠥࡈࡵࡪ࡮ࡧࠤ࡫࡯࡬ࡦࠢࡦࡶࡪࡧࡴࡦࡦ࠽ࠤࢀࢃࠢᬭ").format(self.bstack11l1l1111l1_opy_))
    def bstack11l11lll1l1_opy_(self):
        def bstack11l11lll11l_opy_():
            while not self.bstack11l1l111lll_opy_:
                time.sleep(bstack11l11lll1ll_opy_)
                self.bstack11l1l111ll1_opy_()
                self.bstack11l11lllll1_opy_()
        bstack11l1l111l1l_opy_ = threading.Thread(target=bstack11l11lll11l_opy_, daemon=True)
        bstack11l1l111l1l_opy_.start()