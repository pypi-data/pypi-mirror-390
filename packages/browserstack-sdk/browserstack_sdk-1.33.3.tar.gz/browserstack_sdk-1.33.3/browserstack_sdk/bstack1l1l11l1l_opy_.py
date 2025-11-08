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
import json
import multiprocessing
import os
from bstack_utils.config import Config
class bstack1l1ll1lll_opy_():
  def __init__(self, args, logger, bstack1111111ll1_opy_, bstack111111l1ll_opy_, bstack1111111l11_opy_):
    self.args = args
    self.logger = logger
    self.bstack1111111ll1_opy_ = bstack1111111ll1_opy_
    self.bstack111111l1ll_opy_ = bstack111111l1ll_opy_
    self.bstack1111111l11_opy_ = bstack1111111l11_opy_
  def bstack1l1l11l111_opy_(self, bstack111111l111_opy_, bstack11l111ll11_opy_, bstack1111111l1l_opy_=False):
    bstack11l11ll1_opy_ = []
    manager = multiprocessing.Manager()
    bstack11111l1111_opy_ = manager.list()
    bstack11ll1l111l_opy_ = Config.bstack1l1l1l1111_opy_()
    if bstack1111111l1l_opy_:
      for index, platform in enumerate(self.bstack1111111ll1_opy_[bstack1111l1_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ႜ")]):
        if index == 0:
          bstack11l111ll11_opy_[bstack1111l1_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧႝ")] = self.args
        bstack11l11ll1_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack111111l111_opy_,
                                                    args=(bstack11l111ll11_opy_, bstack11111l1111_opy_)))
    else:
      for index, platform in enumerate(self.bstack1111111ll1_opy_[bstack1111l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ႞")]):
        bstack11l11ll1_opy_.append(multiprocessing.Process(name=str(index),
                                                    target=bstack111111l111_opy_,
                                                    args=(bstack11l111ll11_opy_, bstack11111l1111_opy_)))
    i = 0
    for t in bstack11l11ll1_opy_:
      try:
        if bstack11ll1l111l_opy_.get_property(bstack1111l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧ႟")):
          os.environ[bstack1111l1_opy_ (u"ࠧࡄࡗࡕࡖࡊࡔࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࡢࡈࡆ࡚ࡁࠨႠ")] = json.dumps(self.bstack1111111ll1_opy_[bstack1111l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫႡ")][i % self.bstack1111111l11_opy_])
      except Exception as e:
        self.logger.debug(bstack1111l1_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡࡹ࡫࡭ࡱ࡫ࠠࡴࡶࡲࡶ࡮ࡴࡧࠡࡥࡸࡶࡷ࡫࡮ࡵࠢࡳࡰࡦࡺࡦࡰࡴࡰࠤࡩ࡫ࡴࡢ࡫࡯ࡷ࠿ࠦࡻࡾࠤႢ").format(str(e)))
      i += 1
      t.start()
    for t in bstack11l11ll1_opy_:
      t.join()
    return list(bstack11111l1111_opy_)