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
import logging
from functools import wraps
from typing import Optional
from bstack_utils.constants import EVENTS, STAGE
from bstack_utils.bstack1lll1l11l_opy_ import get_logger
from bstack_utils.bstack1llll1llll_opy_ import bstack1llll11l111_opy_
bstack1llll1llll_opy_ = bstack1llll11l111_opy_()
logger = get_logger(__name__)
def measure(event_name: EVENTS, stage: STAGE, hook_type: Optional[str] = None, bstack11ll1l1l_opy_: Optional[str] = None):
    bstack1111l1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡄࡦࡥࡲࡶࡦࡺ࡯ࡳࠢࡷࡳࠥࡲ࡯ࡨࠢࡷ࡬ࡪࠦࡳࡵࡣࡵࡸࠥࡺࡩ࡮ࡧࠣࡳ࡫ࠦࡡࠡࡨࡸࡲࡨࡺࡩࡰࡰࠣࡩࡽ࡫ࡣࡶࡶ࡬ࡳࡳࠐࠠࠡࠢࠣࡥࡱࡵ࡮ࡨࠢࡺ࡭ࡹ࡮ࠠࡦࡸࡨࡲࡹࠦ࡮ࡢ࡯ࡨࠤࡦࡴࡤࠡࡵࡷࡥ࡬࡫࠮ࠋࠢࠣࠤࠥࠨࠢࠣḡ")
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            label: str = event_name.value
            bstack1ll11l111ll_opy_: str = bstack1llll1llll_opy_.bstack11ll11l11l1_opy_(label)
            start_mark: str = label + bstack1111l1_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢḢ")
            end_mark: str = label + bstack1111l1_opy_ (u"ࠣ࠼ࡨࡲࡩࠨḣ")
            result = None
            try:
                if stage.value == STAGE.bstack11ll11l1ll_opy_.value:
                    bstack1llll1llll_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                elif stage.value == STAGE.END.value:
                    result = func(*args, **kwargs)
                    bstack1llll1llll_opy_.end(label, start_mark, end_mark, status=True, failure=None,hook_type=hook_type,test_name=bstack11ll1l1l_opy_)
                elif stage.value == STAGE.bstack1l1ll1111l_opy_.value:
                    start_mark: str = bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤḤ")
                    end_mark: str = bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣḥ")
                    bstack1llll1llll_opy_.mark(start_mark)
                    result = func(*args, **kwargs)
                    bstack1llll1llll_opy_.end(label, start_mark, end_mark, status=True, failure=None, hook_type=hook_type,test_name=bstack11ll1l1l_opy_)
            except Exception as e:
                bstack1llll1llll_opy_.end(label, start_mark, end_mark, status=False, failure=str(e), hook_type=hook_type,
                                       test_name=bstack11ll1l1l_opy_)
            return result
        return wrapper
    return decorator