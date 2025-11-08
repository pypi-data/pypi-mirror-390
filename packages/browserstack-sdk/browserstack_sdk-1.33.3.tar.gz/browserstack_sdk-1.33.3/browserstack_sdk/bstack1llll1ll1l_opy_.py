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
import multiprocessing
import os
import json
from time import sleep
import time
import bstack_utils.accessibility as bstack1ll1ll1l11_opy_
import subprocess
import re
from browserstack_sdk.bstack111ll1lll_opy_ import *
from bstack_utils.config import Config
from bstack_utils.messages import bstack1ll11l111l_opy_
from bstack_utils.bstack11llll11l_opy_ import bstack11l111llll_opy_
from bstack_utils.constants import bstack1111l11111_opy_
from bstack_utils.bstack1l1ll111ll_opy_ import bstack11l1111l_opy_
class bstack1l1l1111_opy_:
    bstack11111l11l1_opy_ = bstack1111l1_opy_ (u"ࡴࠪࡀࡒࡵࡤࡶ࡮ࡨࠤ࠭ࡡ࡞࠿࡟࠮࠭ࡃ࠭ၜ")  # bstack11111lll1l_opy_ lines bstack1llllll_opy_ <Module path/to/bstack1l1l11111l_opy_.py> in pytest --collect-bstack111111lll1_opy_ output
    def __init__(self, args, logger, bstack1111111ll1_opy_, bstack111111l1ll_opy_):
        self.args = args
        self.logger = logger
        self.bstack1111111ll1_opy_ = bstack1111111ll1_opy_
        self.bstack111111l1ll_opy_ = bstack111111l1ll_opy_
        self._prepareconfig = None
        self.Config = None
        self.runner = None
        self.bstack1111111l_opy_ = []
        self.bstack11111l1lll_opy_ = []
        self.bstack1l1lllll_opy_ = []
        self.bstack11111ll111_opy_ = self.bstack1l1l1l11l_opy_()
        self.bstack1l1lll11ll_opy_ = -1
    def bstack11l111ll11_opy_(self, bstack1111l11ll1_opy_):
        self.parse_args()
        self.bstack1111l111ll_opy_()
        self.bstack1111l1l111_opy_(bstack1111l11ll1_opy_)
        self.bstack11111llll1_opy_()
    def bstack11lll1111l_opy_(self):
        bstack1l1ll111ll_opy_ = bstack11l1111l_opy_.bstack1l1l1l1111_opy_(self.bstack1111111ll1_opy_, self.logger)
        if bstack1l1ll111ll_opy_ is None:
            self.logger.warn(bstack1111l1_opy_ (u"ࠥࡓࡷࡩࡨࡦࡵࡷࡶࡦࡺࡩࡰࡰࠣ࡬ࡦࡴࡤ࡭ࡧࡵࠤ࡮ࡹࠠ࡯ࡱࡷࠤ࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࢀࡥࡥ࠰ࠣࡗࡰ࡯ࡰࡱ࡫ࡱ࡫ࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲ࠳ࠨၝ"))
            return
        bstack11111ll11l_opy_ = False
        bstack1l1ll111ll_opy_.bstack11111ll1ll_opy_(bstack1111l1_opy_ (u"ࠦࡪࡴࡡࡣ࡮ࡨࡨࠧၞ"), bstack1l1ll111ll_opy_.bstack1lll1lll1l_opy_())
        start_time = time.time()
        if bstack1l1ll111ll_opy_.bstack1lll1lll1l_opy_():
            test_files = self.bstack11111l1l11_opy_()
            bstack11111ll11l_opy_ = True
            bstack111111ll1l_opy_ = bstack1l1ll111ll_opy_.bstack1111l1111l_opy_(test_files)
            if bstack111111ll1l_opy_:
                self.bstack1111111l_opy_ = [os.path.normpath(item).replace(bstack1111l1_opy_ (u"ࠬࡢ࡜ࠨၟ"), bstack1111l1_opy_ (u"࠭࠯ࠨၠ")) for item in bstack111111ll1l_opy_]
                self.__11111l111l_opy_()
                bstack1l1ll111ll_opy_.bstack111111llll_opy_(bstack11111ll11l_opy_)
                self.logger.info(bstack1111l1_opy_ (u"ࠢࡕࡧࡶࡸࡸࠦࡲࡦࡱࡵࡨࡪࡸࡥࡥࠢࡸࡷ࡮ࡴࡧࠡࡱࡵࡧ࡭࡫ࡳࡵࡴࡤࡸ࡮ࡵ࡮࠻ࠢࡾࢁࠧၡ").format(self.bstack1111111l_opy_))
            else:
                self.logger.info(bstack1111l1_opy_ (u"ࠣࡐࡲࠤࡹ࡫ࡳࡵࠢࡩ࡭ࡱ࡫ࡳࠡࡹࡨࡶࡪࠦࡲࡦࡱࡵࡨࡪࡸࡥࡥࠢࡥࡽࠥࡵࡲࡤࡪࡨࡷࡹࡸࡡࡵ࡫ࡲࡲ࠳ࠨၢ"))
        bstack1l1ll111ll_opy_.bstack11111ll1ll_opy_(bstack1111l1_opy_ (u"ࠤࡷ࡭ࡲ࡫ࡔࡢ࡭ࡨࡲ࡙ࡵࡁࡱࡲ࡯ࡽࠧၣ"), int((time.time() - start_time) * 1000)) # bstack1111l11l11_opy_ to bstack11111l1l1l_opy_
    def __11111l111l_opy_(self):
        bstack1111l1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡇࡱࡵࠤࡪࡧࡣࡩࠢࡷࡩࡸࡺࠠࡧ࡫࡯ࡩࠥ࡯࡮ࠡࡵࡨࡰ࡫࠴ࡳࡱࡧࡦࡣ࡫࡯࡬ࡦࡵ࠯ࠤࡨࡵ࡬࡭ࡧࡦࡸࠥࡧ࡬࡭ࠢࡱࡳࡩ࡫ࡩࡥࡵࠣࡹࡸ࡯࡮ࡨࠢࡳࡽࡹ࡫ࡳࡵࠢ࠰࠱ࡨࡵ࡬࡭ࡧࡦࡸ࠲ࡵ࡮࡭ࡻࠍࠤࠥࠦࠠࠡࠢࠣࠤࠧࠨࠢၤ")
        bstack1111l11l1l_opy_ = []
        for bstack1l1l11111l_opy_ in self.bstack1111111l_opy_:
            bstack1111l11lll_opy_ = [bstack1111l1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࠦၥ"), bstack1l1l11111l_opy_, bstack1111l1_opy_ (u"ࠧ࠳࠭ࡤࡱ࡯ࡰࡪࡩࡴ࠮ࡱࡱࡰࡾࠨၦ"), bstack1111l1_opy_ (u"ࠨ࠭ࡲࠤၧ")]
            result = subprocess.run(bstack1111l11lll_opy_, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                self.logger.error(bstack11111l1ll1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦࡣࡰ࡮࡯ࡩࡨࡺࡩ࡯ࡩࠣࡲࡴࡪࡥࡪࡦࡶࠤ࡫ࡵࡲࠡࡽࡷࡩࡸࡺ࡟ࡧ࡫࡯ࡩࢂࡀࠠࡼࡴࡨࡷࡺࡲࡴ࠯ࡵࡷࡨࡪࡸࡲࡾࠤၨ"))
                continue
            for line in result.stdout.splitlines():
                line = line.strip()
                if line and not line.startswith(bstack1111l1_opy_ (u"ࠣ࠾ࠥၩ")) and bstack1111l1_opy_ (u"ࠤ࠽࠾ࠧၪ") in line:
                    bstack1111l11l1l_opy_.append(line)
        os.environ[bstack1111l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡒࡖࡈࡎࡅࡔࡖࡕࡅ࡙ࡋࡄࡠࡕࡈࡐࡊࡉࡔࡐࡔࡖࠫၫ")] = json.dumps(bstack1111l11l1l_opy_)
    @staticmethod
    def version():
        import pytest
        return pytest.__version__
    @staticmethod
    def bstack111111ll11_opy_():
        import importlib
        if getattr(importlib, bstack1111l1_opy_ (u"ࠫ࡫࡯࡮ࡥࡡ࡯ࡳࡦࡪࡥࡳࠩၬ"), False):
            bstack1111l111l1_opy_ = importlib.find_loader(bstack1111l1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠧၭ"))
        else:
            bstack1111l111l1_opy_ = importlib.util.find_spec(bstack1111l1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࠨၮ"))
    def bstack111111l1l1_opy_(self, arg):
        if arg in self.args:
            i = self.args.index(arg)
            self.args.pop(i + 1)
            self.args.pop(i)
    def parse_args(self):
        self.bstack1l1lll11ll_opy_ = -1
        if self.bstack111111l1ll_opy_ and bstack1111l1_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧၯ") in self.bstack1111111ll1_opy_:
            self.bstack1l1lll11ll_opy_ = int(self.bstack1111111ll1_opy_[bstack1111l1_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨၰ")])
        try:
            bstack11111l11ll_opy_ = [bstack1111l1_opy_ (u"ࠩ࠰࠱ࡩࡸࡩࡷࡧࡵࠫၱ"), bstack1111l1_opy_ (u"ࠪ࠱࠲ࡶ࡬ࡶࡩ࡬ࡲࡸ࠭ၲ"), bstack1111l1_opy_ (u"ࠫ࠲ࡶࠧၳ")]
            if self.bstack1l1lll11ll_opy_ >= 0:
                bstack11111l11ll_opy_.extend([bstack1111l1_opy_ (u"ࠬ࠳࠭࡯ࡷࡰࡴࡷࡵࡣࡦࡵࡶࡩࡸ࠭ၴ"), bstack1111l1_opy_ (u"࠭࠭࡯ࠩၵ")])
            for arg in bstack11111l11ll_opy_:
                self.bstack111111l1l1_opy_(arg)
        except Exception as exc:
            self.logger.error(str(exc))
    def get_args(self):
        return self.args
    def bstack1111l111ll_opy_(self):
        bstack11111l1lll_opy_ = [os.path.normpath(item) for item in self.args]
        self.bstack11111l1lll_opy_ = bstack11111l1lll_opy_
        return self.bstack11111l1lll_opy_
    def bstack11l1111111_opy_(self):
        try:
            from _pytest.config import _prepareconfig
            from _pytest.config import Config
            from _pytest import runner
            self.bstack111111ll11_opy_()
            self._prepareconfig = _prepareconfig
            self.Config = Config
            self.runner = runner
        except Exception as e:
            self.logger.warn(e, bstack1ll11l111l_opy_)
    def bstack1111l1l111_opy_(self, bstack1111l11ll1_opy_):
        bstack11ll1l111l_opy_ = Config.bstack1l1l1l1111_opy_()
        if bstack1111l11ll1_opy_:
            self.bstack11111l1lll_opy_.append(bstack1111l1_opy_ (u"ࠧ࠮࠯ࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫၶ"))
            self.bstack11111l1lll_opy_.append(bstack1111l1_opy_ (u"ࠨࡖࡵࡹࡪ࠭ၷ"))
        if bstack11ll1l111l_opy_.bstack11111lllll_opy_():
            self.bstack11111l1lll_opy_.append(bstack1111l1_opy_ (u"ࠩ࠰࠱ࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠨၸ"))
            self.bstack11111l1lll_opy_.append(bstack1111l1_opy_ (u"ࠪࡘࡷࡻࡥࠨၹ"))
        self.bstack11111l1lll_opy_.append(bstack1111l1_opy_ (u"ࠫ࠲ࡶࠧၺ"))
        self.bstack11111l1lll_opy_.append(bstack1111l1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡴࡱࡻࡧࡪࡰࠪၻ"))
        self.bstack11111l1lll_opy_.append(bstack1111l1_opy_ (u"࠭࠭࠮ࡦࡵ࡭ࡻ࡫ࡲࠨၼ"))
        self.bstack11111l1lll_opy_.append(bstack1111l1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࠧၽ"))
        if self.bstack1l1lll11ll_opy_ > 1:
            self.bstack11111l1lll_opy_.append(bstack1111l1_opy_ (u"ࠨ࠯ࡱࠫၾ"))
            self.bstack11111l1lll_opy_.append(str(self.bstack1l1lll11ll_opy_))
    def bstack11111llll1_opy_(self):
        if bstack11l111llll_opy_.bstack111l1l11l_opy_(self.bstack1111111ll1_opy_):
             self.bstack11111l1lll_opy_ += [
                bstack1111l11111_opy_.get(bstack1111l1_opy_ (u"ࠩࡵࡩࡷࡻ࡮ࠨၿ")), str(bstack11l111llll_opy_.bstack1l111l1111_opy_(self.bstack1111111ll1_opy_)),
                bstack1111l11111_opy_.get(bstack1111l1_opy_ (u"ࠪࡨࡪࡲࡡࡺࠩႀ")), str(bstack1111l11111_opy_.get(bstack1111l1_opy_ (u"ࠫࡷ࡫ࡲࡶࡰ࠰ࡨࡪࡲࡡࡺࠩႁ")))
            ]
    def bstack1111111lll_opy_(self):
        bstack1l1lllll_opy_ = []
        for spec in self.bstack1111111l_opy_:
            bstack1ll11l1ll_opy_ = [spec]
            bstack1ll11l1ll_opy_ += self.bstack11111l1lll_opy_
            bstack1l1lllll_opy_.append(bstack1ll11l1ll_opy_)
        self.bstack1l1lllll_opy_ = bstack1l1lllll_opy_
        return bstack1l1lllll_opy_
    def bstack1l1l1l11l_opy_(self):
        try:
            from pytest_bdd import reporting
            self.bstack11111ll111_opy_ = True
            return True
        except Exception as e:
            self.bstack11111ll111_opy_ = False
        return self.bstack11111ll111_opy_
    def bstack1lll1l11l1_opy_(self):
        bstack1111l1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡇࡦࡶࠣࡸ࡭࡫ࠠࡤࡱࡸࡲࡹࠦ࡯ࡧࠢࡷࡩࡸࡺࡳࠡࡹ࡬ࡸ࡭ࡵࡵࡵࠢࡵࡹࡳࡴࡩ࡯ࡩࠣࡸ࡭࡫࡭ࠡࡷࡶ࡭ࡳ࡭ࠠࡱࡻࡷࡩࡸࡺࠧࡴࠢ࠰࠱ࡨࡵ࡬࡭ࡧࡦࡸ࠲ࡵ࡮࡭ࡻࠣࡪࡱࡧࡧ࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡓࡧࡷࡹࡷࡴࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࡮ࡴࡴ࠻ࠢࡗ࡬ࡪࠦࡴࡰࡶࡤࡰࠥࡴࡵ࡮ࡤࡨࡶࠥࡵࡦࠡࡶࡨࡷࡹࡹࠠࡤࡱ࡯ࡰࡪࡩࡴࡦࡦ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣႂ")
        try:
            self.logger.info(bstack1111l1_opy_ (u"ࠨࡃࡰ࡮࡯ࡩࡨࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࡴࠢࡸࡷ࡮ࡴࡧࠡࡲࡼࡸࡪࡹࡴࠡ࠯࠰ࡧࡴࡲ࡬ࡦࡥࡷ࠱ࡴࡴ࡬ࡺࠤႃ"))
            bstack1111l11lll_opy_ = [bstack1111l1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺࠢႄ"), *self.bstack11111l1lll_opy_, bstack1111l1_opy_ (u"ࠣ࠯࠰ࡧࡴࡲ࡬ࡦࡥࡷ࠱ࡴࡴ࡬ࡺࠤႅ")]
            result = subprocess.run(bstack1111l11lll_opy_, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                self.logger.error(bstack1111l1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡤࡱ࡯ࡰࡪࡩࡴࡪࡰࡪࠤࡹ࡫ࡳࡵࡵ࠽ࠤࢀࢃࠢႆ").format(result.stderr))
                return 0
            test_count = result.stdout.count(bstack1111l1_opy_ (u"ࠥࡀࡋࡻ࡮ࡤࡶ࡬ࡳࡳࠦࠢႇ"))
            self.logger.info(bstack1111l1_opy_ (u"࡙ࠦࡵࡴࡢ࡮ࠣࡸࡪࡹࡴࡴࠢࡦࡳࡱࡲࡥࡤࡶࡨࡨ࠿ࠦࡻࡾࠤႈ").format(test_count))
            return test_count
        except Exception as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠧࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡹ࡫࡭ࡱ࡫ࠠࡨࡧࡷࡸ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡣࡰࡷࡱࡸ࠿ࠦࡻࡾࠤႉ").format(e))
            return 0
    def bstack1l1l11l111_opy_(self, bstack111111l111_opy_, bstack11l111ll11_opy_):
        bstack11l111ll11_opy_[bstack1111l1_opy_ (u"࠭ࡃࡐࡐࡉࡍࡌ࠭ႊ")] = self.bstack1111111ll1_opy_
        multiprocessing.set_start_method(bstack1111l1_opy_ (u"ࠧࡴࡲࡤࡻࡳ࠭ႋ"))
        bstack11l11ll1_opy_ = []
        manager = multiprocessing.Manager()
        bstack11111l1111_opy_ = manager.list()
        if bstack1111l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫႌ") in self.bstack1111111ll1_opy_:
            for index, platform in enumerate(self.bstack1111111ll1_opy_[bstack1111l1_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷႍࠬ")]):
                bstack11l11ll1_opy_.append(multiprocessing.Process(name=str(index),
                                                            target=bstack111111l111_opy_,
                                                            args=(self.bstack11111l1lll_opy_, bstack11l111ll11_opy_, bstack11111l1111_opy_)))
            bstack11111ll1l1_opy_ = len(self.bstack1111111ll1_opy_[bstack1111l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ႎ")])
        else:
            bstack11l11ll1_opy_.append(multiprocessing.Process(name=str(0),
                                                        target=bstack111111l111_opy_,
                                                        args=(self.bstack11111l1lll_opy_, bstack11l111ll11_opy_, bstack11111l1111_opy_)))
            bstack11111ll1l1_opy_ = 1
        i = 0
        for t in bstack11l11ll1_opy_:
            os.environ[bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫႏ")] = str(i)
            if bstack1111l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ႐") in self.bstack1111111ll1_opy_:
                os.environ[bstack1111l1_opy_ (u"࠭ࡃࡖࡔࡕࡉࡓ࡚࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡇࡅ࡙ࡇࠧ႑")] = json.dumps(self.bstack1111111ll1_opy_[bstack1111l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ႒")][i % bstack11111ll1l1_opy_])
            i += 1
            t.start()
        for t in bstack11l11ll1_opy_:
            t.join()
        return list(bstack11111l1111_opy_)
    @staticmethod
    def bstack11lll11l1_opy_(driver, bstack11111lll11_opy_, logger, item=None, wait=False):
        item = item or getattr(threading.current_thread(), bstack1111l1_opy_ (u"ࠨࡥࡸࡶࡷ࡫࡮ࡵࡡࡷࡩࡸࡺ࡟ࡪࡶࡨࡱࠬ႓"), None)
        if item and getattr(item, bstack1111l1_opy_ (u"ࠩࡢࡥ࠶࠷ࡹࡠࡶࡨࡷࡹࡥࡣࡢࡵࡨࠫ႔"), None) and not getattr(item, bstack1111l1_opy_ (u"ࠪࡣࡦ࠷࠱ࡺࡡࡶࡸࡴࡶ࡟ࡥࡱࡱࡩࠬ႕"), False):
            logger.info(
                bstack1111l1_opy_ (u"ࠦࡆࡻࡴࡰ࡯ࡤࡸࡪࠦࡴࡦࡵࡷࠤࡨࡧࡳࡦࠢࡨࡼࡪࡩࡵࡵ࡫ࡲࡲࠥ࡮ࡡࡴࠢࡨࡲࡩ࡫ࡤ࠯ࠢࡓࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡦࡰࡴࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡸࡪࡹࡴࡪࡰࡪࠤ࡮ࡹࠠࡶࡰࡧࡩࡷࡽࡡࡺ࠰ࠥ႖"))
            bstack111111l11l_opy_ = item.cls.__name__ if not item.cls is None else None
            bstack1ll1ll1l11_opy_.bstack1ll11llll1_opy_(driver, item.name, item.path)
            item._a11y_stop_done = True
            if wait:
                sleep(2)
    def bstack11111l1l11_opy_(self):
        bstack1111l1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡕࡩࡹࡻࡲ࡯ࡵࠣࡸ࡭࡫ࠠ࡭࡫ࡶࡸࠥࡵࡦࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷࠥࡺ࡯ࠡࡤࡨࠤࡪࡾࡥࡤࡷࡷࡩࡩࠦࡢࡺࠢࡳࡥࡷࡹࡩ࡯ࡩࠣࡸ࡭࡫ࠠࡰࡷࡷࡴࡺࡺࠠࡰࡨࠣࡴࡾࡺࡥࡴࡶࠣ࠱࠲ࡩ࡯࡭࡮ࡨࡧࡹ࠳࡯࡯࡮ࡼ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡎࡰࡶࡨ࠾࡚ࠥࡨࡦࠢࡵࡩ࡬࡫ࡸࠡࡲࡤࡸࡹ࡫ࡲ࡯ࠢࡸࡷࡪࡪࠠࡩࡧࡵࡩࠥࡪࡥࡱࡧࡱࡨࡸࠦ࡯࡯ࠢࡳࡽࡹ࡫ࡳࡵࠩࡶࠤࡴࡻࡴࡱࡷࡷࠤ࡫ࡵࡲ࡮ࡣࡷࠤ࡫ࡵࡲࠡ࠾ࡐࡳࡩࡻ࡬ࡦࠢ࠱࠲࠳ࡄࠠ࡭࡫ࡱࡩࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦ႗")
        try:
            bstack1111l11lll_opy_ = [bstack1111l1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࠨ႘"), *self.bstack11111l1lll_opy_, bstack1111l1_opy_ (u"ࠢ࠮࠯ࡦࡳࡱࡲࡥࡤࡶ࠰ࡳࡳࡲࡹࠣ႙")]
            result = subprocess.run(bstack1111l11lll_opy_, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                self.logger.error(bstack1111l1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡣࡰ࡮࡯ࡩࡨࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࡴࠢࡩ࡭ࡱ࡫࠺ࠡࡽࢀࠦႚ").format(result.stderr))
                return []
            file_names = set(re.findall(self.bstack11111l11l1_opy_, result.stdout))
            file_names = sorted(file_names)
            return list(file_names)
        except Exception as e:
            self.logger.error(bstack11111l1ll1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࡽࡨࡪ࡮ࡨࠤࡨࡵ࡬࡭ࡧࡦࡸ࡮ࡴࡧࠡࡶࡨࡷࡹࠦࡦࡪ࡮ࡨࡷ࠿ࠦࡻࡦࡿࠥႛ"))
            return []