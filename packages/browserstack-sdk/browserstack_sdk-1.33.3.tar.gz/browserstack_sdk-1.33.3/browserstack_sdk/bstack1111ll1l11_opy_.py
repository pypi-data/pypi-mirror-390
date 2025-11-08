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
class RobotHandler():
    def __init__(self, args, logger, bstack1111111ll1_opy_, bstack111111l1ll_opy_):
        self.args = args
        self.logger = logger
        self.bstack1111111ll1_opy_ = bstack1111111ll1_opy_
        self.bstack111111l1ll_opy_ = bstack111111l1ll_opy_
    @staticmethod
    def version():
        import robot
        return robot.__version__
    @staticmethod
    def bstack1111ll11ll_opy_(bstack1111111111_opy_):
        bstack111111111l_opy_ = []
        if bstack1111111111_opy_:
            tokens = str(os.path.basename(bstack1111111111_opy_)).split(bstack1111l1_opy_ (u"ࠥࡣࠧႣ"))
            camelcase_name = bstack1111l1_opy_ (u"ࠦࠥࠨႤ").join(t.title() for t in tokens)
            suite_name, bstack11111111ll_opy_ = os.path.splitext(camelcase_name)
            bstack111111111l_opy_.append(suite_name)
        return bstack111111111l_opy_
    @staticmethod
    def bstack11111111l1_opy_(typename):
        if bstack1111l1_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࠣႥ") in typename:
            return bstack1111l1_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࡇࡵࡶࡴࡸࠢႦ")
        return bstack1111l1_opy_ (u"ࠢࡖࡰ࡫ࡥࡳࡪ࡬ࡦࡦࡈࡶࡷࡵࡲࠣႧ")