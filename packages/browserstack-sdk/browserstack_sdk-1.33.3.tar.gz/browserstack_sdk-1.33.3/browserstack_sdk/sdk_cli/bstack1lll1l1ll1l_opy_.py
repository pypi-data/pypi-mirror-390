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
from datetime import datetime, timezone
import os
import builtins
from pathlib import Path
from typing import Any, Tuple, Callable, List
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import bstack1llll1l11l1_opy_, bstack1llll1ll11l_opy_, bstack1lllll11111_opy_
from browserstack_sdk.sdk_cli.bstack1ll1l1l1111_opy_ import bstack1lll1111lll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1111ll1_opy_ import bstack1lll11ll1l1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1ll1111_opy_ import bstack1lll111l1l1_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1ll1lll1_opy_, bstack1ll1llll1l1_opy_, bstack1lll11l11ll_opy_, bstack1ll1l1l1lll_opy_
from json import dumps, JSONEncoder
import grpc
from browserstack_sdk import sdk_pb2 as structs
import sys
import traceback
import time
import json
from bstack_utils.helper import bstack1l1l1l1l1l1_opy_, bstack1l1ll1111l1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
bstack1l1l11lll1l_opy_ = [bstack1111l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤኀ"), bstack1111l1_opy_ (u"ࠧࡶࡡࡳࡧࡱࡸࠧኁ"), bstack1111l1_opy_ (u"ࠨࡣࡰࡰࡩ࡭࡬ࠨኂ"), bstack1111l1_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࠣኃ"), bstack1111l1_opy_ (u"ࠣࡲࡤࡸ࡭ࠨኄ")]
bstack1l1ll1lllll_opy_ = bstack1l1ll1111l1_opy_()
bstack1l1ll1l111l_opy_ = bstack1111l1_opy_ (u"ࠤࡘࡴࡱࡵࡡࡥࡧࡧࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳ࠮ࠤኅ")
bstack1l1l1l11l1l_opy_ = {
    bstack1111l1_opy_ (u"ࠥࡴࡾࡺࡥࡴࡶ࠱ࡴࡾࡺࡨࡰࡰ࠱ࡍࡹ࡫࡭ࠣኆ"): bstack1l1l11lll1l_opy_,
    bstack1111l1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡵࡿࡴࡩࡱࡱ࠲ࡕࡧࡣ࡬ࡣࡪࡩࠧኇ"): bstack1l1l11lll1l_opy_,
    bstack1111l1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡶࡹࡵࡪࡲࡲ࠳ࡓ࡯ࡥࡷ࡯ࡩࠧኈ"): bstack1l1l11lll1l_opy_,
    bstack1111l1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠴ࡰࡺࡶ࡫ࡳࡳ࠴ࡃ࡭ࡣࡶࡷࠧ኉"): bstack1l1l11lll1l_opy_,
    bstack1111l1_opy_ (u"ࠢࡱࡻࡷࡩࡸࡺ࠮ࡱࡻࡷ࡬ࡴࡴ࠮ࡇࡷࡱࡧࡹ࡯࡯࡯ࠤኊ"): bstack1l1l11lll1l_opy_
    + [
        bstack1111l1_opy_ (u"ࠣࡱࡵ࡭࡬࡯࡮ࡢ࡮ࡱࡥࡲ࡫ࠢኋ"),
        bstack1111l1_opy_ (u"ࠤ࡮ࡩࡾࡽ࡯ࡳࡦࡶࠦኌ"),
        bstack1111l1_opy_ (u"ࠥࡪ࡮ࡾࡴࡶࡴࡨ࡭ࡳ࡬࡯ࠣኍ"),
        bstack1111l1_opy_ (u"ࠦࡰ࡫ࡹࡸࡱࡵࡨࡸࠨ኎"),
        bstack1111l1_opy_ (u"ࠧࡩࡡ࡭࡮ࡶࡴࡪࡩࠢ኏"),
        bstack1111l1_opy_ (u"ࠨࡣࡢ࡮࡯ࡳࡧࡰࠢነ"),
        bstack1111l1_opy_ (u"ࠢࡴࡶࡤࡶࡹࠨኑ"),
        bstack1111l1_opy_ (u"ࠣࡵࡷࡳࡵࠨኒ"),
        bstack1111l1_opy_ (u"ࠤࡧࡹࡷࡧࡴࡪࡱࡱࠦና"),
        bstack1111l1_opy_ (u"ࠥࡻ࡭࡫࡮ࠣኔ"),
    ],
    bstack1111l1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷ࠲ࡲࡧࡩ࡯࠰ࡖࡩࡸࡹࡩࡰࡰࠥን"): [bstack1111l1_opy_ (u"ࠧࡹࡴࡢࡴࡷࡴࡦࡺࡨࠣኖ"), bstack1111l1_opy_ (u"ࠨࡴࡦࡵࡷࡷ࡫ࡧࡩ࡭ࡧࡧࠦኗ"), bstack1111l1_opy_ (u"ࠢࡵࡧࡶࡸࡸࡩ࡯࡭࡮ࡨࡧࡹ࡫ࡤࠣኘ"), bstack1111l1_opy_ (u"ࠣ࡫ࡷࡩࡲࡹࠢኙ")],
    bstack1111l1_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡦࡳࡳ࡬ࡩࡨ࠰ࡆࡳࡳ࡬ࡩࡨࠤኚ"): [bstack1111l1_opy_ (u"ࠥ࡭ࡳࡼ࡯ࡤࡣࡷ࡭ࡴࡴ࡟ࡱࡣࡵࡥࡲࡹࠢኛ"), bstack1111l1_opy_ (u"ࠦࡦࡸࡧࡴࠤኜ")],
    bstack1111l1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳࡬ࡩࡹࡶࡸࡶࡪࡹ࠮ࡇ࡫ࡻࡸࡺࡸࡥࡅࡧࡩࠦኝ"): [bstack1111l1_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧኞ"), bstack1111l1_opy_ (u"ࠢࡢࡴࡪࡲࡦࡳࡥࠣኟ"), bstack1111l1_opy_ (u"ࠣࡨࡸࡲࡨࠨአ"), bstack1111l1_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࡴࠤኡ"), bstack1111l1_opy_ (u"ࠥࡹࡳ࡯ࡴࡵࡧࡶࡸࠧኢ"), bstack1111l1_opy_ (u"ࠦ࡮ࡪࡳࠣኣ")],
    bstack1111l1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳࡬ࡩࡹࡶࡸࡶࡪࡹ࠮ࡔࡷࡥࡖࡪࡷࡵࡦࡵࡷࠦኤ"): [bstack1111l1_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࠦእ"), bstack1111l1_opy_ (u"ࠢࡱࡣࡵࡥࡲࠨኦ"), bstack1111l1_opy_ (u"ࠣࡲࡤࡶࡦࡳ࡟ࡪࡰࡧࡩࡽࠨኧ")],
    bstack1111l1_opy_ (u"ࠤࡳࡽࡹ࡫ࡳࡵ࠰ࡵࡹࡳࡴࡥࡳ࠰ࡆࡥࡱࡲࡉ࡯ࡨࡲࠦከ"): [bstack1111l1_opy_ (u"ࠥࡻ࡭࡫࡮ࠣኩ"), bstack1111l1_opy_ (u"ࠦࡷ࡫ࡳࡶ࡮ࡷࠦኪ")],
    bstack1111l1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠳ࡳࡡࡳ࡭࠱ࡷࡹࡸࡵࡤࡶࡸࡶࡪࡹ࠮ࡏࡱࡧࡩࡐ࡫ࡹࡸࡱࡵࡨࡸࠨካ"): [bstack1111l1_opy_ (u"ࠨ࡮ࡰࡦࡨࠦኬ"), bstack1111l1_opy_ (u"ࠢࡱࡣࡵࡩࡳࡺࠢክ")],
    bstack1111l1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠯࡯ࡤࡶࡰ࠴ࡳࡵࡴࡸࡧࡹࡻࡲࡦࡵ࠱ࡑࡦࡸ࡫ࠣኮ"): [bstack1111l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢኯ"), bstack1111l1_opy_ (u"ࠥࡥࡷ࡭ࡳࠣኰ"), bstack1111l1_opy_ (u"ࠦࡰࡽࡡࡳࡩࡶࠦ኱")],
}
_1l1ll11llll_opy_ = set()
class bstack1ll1llll11l_opy_(bstack1lll1111lll_opy_):
    bstack1l1l1llllll_opy_ = bstack1111l1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡨࡪ࡬ࡥࡳࡴࡨࡨࠧኲ")
    bstack1l1ll1ll1ll_opy_ = bstack1111l1_opy_ (u"ࠨࡉࡏࡈࡒࠦኳ")
    bstack1l1ll1l1lll_opy_ = bstack1111l1_opy_ (u"ࠢࡆࡔࡕࡓࡗࠨኴ")
    bstack1l1l1l11l11_opy_: Callable
    bstack1l1lll111ll_opy_: Callable
    def __init__(self, bstack1ll1l1ll1ll_opy_, bstack1lll1lllll1_opy_):
        super().__init__()
        self.bstack1ll11l11l11_opy_ = bstack1lll1lllll1_opy_
        if os.getenv(bstack1111l1_opy_ (u"ࠣࡕࡇࡏࡤࡉࡌࡊࡡࡉࡐࡆࡍ࡟ࡐ࠳࠴࡝ࠧኵ"), bstack1111l1_opy_ (u"ࠤ࠴ࠦ኶")) != bstack1111l1_opy_ (u"ࠥ࠵ࠧ኷") or not self.is_enabled():
            self.logger.warning(bstack1111l1_opy_ (u"ࠦࠧኸ") + str(self.__class__.__name__) + bstack1111l1_opy_ (u"ࠧࠦࡤࡪࡵࡤࡦࡱ࡫ࡤࠣኹ"))
            return
        TestFramework.bstack1ll111111ll_opy_((bstack1ll1ll1lll1_opy_.TEST, bstack1lll11l11ll_opy_.PRE), self.bstack1ll11ll111l_opy_)
        TestFramework.bstack1ll111111ll_opy_((bstack1ll1ll1lll1_opy_.TEST, bstack1lll11l11ll_opy_.POST), self.bstack1ll111ll1l1_opy_)
        for event in bstack1ll1ll1lll1_opy_:
            for state in bstack1lll11l11ll_opy_:
                TestFramework.bstack1ll111111ll_opy_((event, state), self.bstack1l1ll1l1ll1_opy_)
        bstack1ll1l1ll1ll_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.bstack1lllll111ll_opy_, bstack1lllll11111_opy_.POST), self.bstack1l1l1ll11l1_opy_)
        self.bstack1l1l1l11l11_opy_ = sys.stdout.write
        sys.stdout.write = self.bstack1l1l1l111ll_opy_(bstack1ll1llll11l_opy_.bstack1l1ll1ll1ll_opy_, self.bstack1l1l1l11l11_opy_)
        self.bstack1l1lll111ll_opy_ = sys.stderr.write
        sys.stderr.write = self.bstack1l1l1l111ll_opy_(bstack1ll1llll11l_opy_.bstack1l1ll1l1lll_opy_, self.bstack1l1lll111ll_opy_)
        self.bstack1l1l1ll1l1l_opy_ = builtins.print
        builtins.print = self.bstack1l1lll111l1_opy_()
    def is_enabled(self) -> bool:
        return True
    def bstack1l1ll1l1ll1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llll1l1_opy_,
        bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_],
        *args,
        **kwargs,
    ):
        if f.bstack1l1ll1l1111_opy_() and instance:
            bstack1l1ll1llll1_opy_ = datetime.now()
            test_framework_state, test_hook_state = bstack1llll1ll1l1_opy_
            if test_framework_state == bstack1ll1ll1lll1_opy_.SETUP_FIXTURE:
                return
            elif test_framework_state == bstack1ll1ll1lll1_opy_.LOG:
                bstack1lll11l11_opy_ = datetime.now()
                entries = f.bstack1l1l1ll11ll_opy_(instance, bstack1llll1ll1l1_opy_)
                if entries:
                    self.bstack1l1l1l111l1_opy_(instance, entries)
                    instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡸ࡫࡮ࡥࡡ࡯ࡳ࡬ࡥࡣࡳࡧࡤࡸࡪࡪ࡟ࡦࡸࡨࡲࡹࠨኺ"), datetime.now() - bstack1lll11l11_opy_)
                    f.bstack1l1ll111lll_opy_(instance, bstack1llll1ll1l1_opy_)
                instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠢࡰ࠳࠴ࡽ࠿ࡵ࡮ࡠࡣ࡯ࡰࡤࡺࡥࡴࡶࡢࡩࡻ࡫࡮ࡵࡵࠥኻ"), datetime.now() - bstack1l1ll1llll1_opy_)
                return # bstack1l1l1lllll1_opy_ not send this event with the bstack1l1l1l11ll1_opy_ bstack1l1l1l11lll_opy_
            elif (
                test_framework_state == bstack1ll1ll1lll1_opy_.TEST
                and test_hook_state == bstack1lll11l11ll_opy_.POST
                and not f.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1l1l1l1llll_opy_)
            ):
                self.logger.warning(bstack1111l1_opy_ (u"ࠣࡦࡵࡳࡵࡶࡩ࡯ࡩࠣࡨࡺ࡫ࠠࡵࡱࠣࡰࡦࡩ࡫ࠡࡱࡩࠤࡷ࡫ࡳࡶ࡮ࡷࡷࠥࠨኼ") + str(TestFramework.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1l1l1l1llll_opy_)) + bstack1111l1_opy_ (u"ࠤࠥኽ"))
                f.bstack1lllll1l1l1_opy_(instance, bstack1ll1llll11l_opy_.bstack1l1l1llllll_opy_, True)
                return # bstack1l1l1lllll1_opy_ not send this event bstack1l1l1l1l11l_opy_ bstack1l1ll1l11ll_opy_
            elif (
                f.bstack1lllll111l1_opy_(instance, bstack1ll1llll11l_opy_.bstack1l1l1llllll_opy_, False)
                and test_framework_state == bstack1ll1ll1lll1_opy_.LOG_REPORT
                and test_hook_state == bstack1lll11l11ll_opy_.POST
                and f.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1l1l1l1llll_opy_)
            ):
                self.logger.warning(bstack1111l1_opy_ (u"ࠥ࡭ࡳࡰࡥࡤࡶ࡬ࡲ࡬ࠦࡔࡦࡵࡷࡊࡷࡧ࡭ࡦࡹࡲࡶࡰ࡙ࡴࡢࡶࡨ࠲࡙ࡋࡓࡕ࠮ࠣࡘࡪࡹࡴࡉࡱࡲ࡯ࡘࡺࡡࡵࡧ࠱ࡔࡔ࡙ࡔࠡࠤኾ") + str(TestFramework.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1l1l1l1llll_opy_)) + bstack1111l1_opy_ (u"ࠦࠧ኿"))
                self.bstack1l1ll1l1ll1_opy_(f, instance, (bstack1ll1ll1lll1_opy_.TEST, bstack1lll11l11ll_opy_.POST), *args, **kwargs)
            bstack1lll11l11_opy_ = datetime.now()
            data = instance.data.copy()
            bstack1l1ll11ll1l_opy_ = sorted(
                filter(lambda x: x.get(bstack1111l1_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠣዀ"), None), data.pop(bstack1111l1_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࡸࠨ዁"), {}).values()),
                key=lambda x: x[bstack1111l1_opy_ (u"ࠢࡦࡸࡨࡲࡹࡥࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠥዂ")],
            )
            if bstack1lll11ll1l1_opy_.bstack1l1l1l1ll11_opy_ in data:
                data.pop(bstack1lll11ll1l1_opy_.bstack1l1l1l1ll11_opy_)
            data.update({bstack1111l1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡪࡺࡷࡹࡷ࡫ࡳࠣዃ"): bstack1l1ll11ll1l_opy_})
            instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠤ࡭ࡷࡴࡴ࠺ࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࡹࠢዄ"), datetime.now() - bstack1lll11l11_opy_)
            bstack1lll11l11_opy_ = datetime.now()
            event_json = dumps(data, cls=bstack1l1l1ll1111_opy_)
            instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠥ࡮ࡸࡵ࡮࠻ࡱࡱࡣࡦࡲ࡬ࡠࡶࡨࡷࡹࡥࡥࡷࡧࡱࡸࡸࠨዅ"), datetime.now() - bstack1lll11l11_opy_)
            self.bstack1l1l1l11lll_opy_(instance, bstack1llll1ll1l1_opy_, event_json=event_json)
            instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠦࡴ࠷࠱ࡺ࠼ࡲࡲࡤࡧ࡬࡭ࡡࡷࡩࡸࡺ࡟ࡦࡸࡨࡲࡹࡹࠢ዆"), datetime.now() - bstack1l1ll1llll1_opy_)
    def bstack1ll11ll111l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llll1l1_opy_,
        bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_],
        *args,
        **kwargs,
    ):
        from bstack_utils.bstack1llll1llll_opy_ import bstack1llll11l111_opy_
        bstack1ll11l111ll_opy_ = bstack1llll11l111_opy_.bstack1ll11ll11l1_opy_(EVENTS.bstack1lll11l1l_opy_.value)
        self.bstack1ll11l11l11_opy_.bstack1l1l1l1l111_opy_(instance, f, bstack1llll1ll1l1_opy_, *args, **kwargs)
        bstack1llll11l111_opy_.end(EVENTS.bstack1lll11l1l_opy_.value, bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧ዇"), bstack1ll11l111ll_opy_ + bstack1111l1_opy_ (u"ࠨ࠺ࡦࡰࡧࠦወ"), status=True, failure=None, test_name=None)
    def bstack1ll111ll1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llll1l1_opy_,
        bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_],
        *args,
        **kwargs,
    ):
        req = self.bstack1ll11l11l11_opy_.bstack1l1ll111l1l_opy_(instance, f, bstack1llll1ll1l1_opy_, *args, **kwargs)
        self.bstack1l1l1ll1lll_opy_(f, instance, req)
    @measure(event_name=EVENTS.bstack1l1ll11l111_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def bstack1l1l1ll1lll_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llll1l1_opy_,
        req: structs.TestSessionEventRequest
    ):
        if not req:
            self.logger.debug(bstack1111l1_opy_ (u"ࠢࡔ࡭࡬ࡴࡵ࡯࡮ࡨࠢࡗࡩࡸࡺࡓࡦࡵࡶ࡭ࡴࡴࡅࡷࡧࡱࡸࠥ࡭ࡒࡑࡅࠣࡧࡦࡲ࡬࠻ࠢࡑࡳࠥࡼࡡ࡭࡫ࡧࠤࡷ࡫ࡱࡶࡧࡶࡸࠥࡪࡡࡵࡣࠥዉ"))
            return
        bstack1lll11l11_opy_ = datetime.now()
        try:
            r = self.bstack1lll1l1lll1_opy_.TestSessionEvent(req)
            instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡹ࡫ࡳࡵࡡࡶࡩࡸࡹࡩࡰࡰࡢࡩࡻ࡫࡮ࡵࠤዊ"), datetime.now() - bstack1lll11l11_opy_)
            f.bstack1lllll1l1l1_opy_(instance, self.bstack1ll11l11l11_opy_.bstack1l1ll111111_opy_, r.success)
            if not r.success:
                self.logger.info(bstack1111l1_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦዋ") + str(r) + bstack1111l1_opy_ (u"ࠥࠦዌ"))
        except grpc.RpcError as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤው") + str(e) + bstack1111l1_opy_ (u"ࠧࠨዎ"))
            traceback.print_exc()
            raise e
    def bstack1l1l1ll11l1_opy_(
        self,
        f: bstack1lll111l1l1_opy_,
        _driver: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        _1l1l1l1ll1l_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if not bstack1lll111l1l1_opy_.bstack1ll11l1l111_opy_(method_name):
            return
        if f.bstack1ll11l1111l_opy_(*args) == bstack1lll111l1l1_opy_.bstack1l1ll111ll1_opy_:
            bstack1l1ll1llll1_opy_ = datetime.now()
            screenshot = result.get(bstack1111l1_opy_ (u"ࠨࡶࡢ࡮ࡸࡩࠧዏ"), None) if isinstance(result, dict) else None
            if not isinstance(screenshot, str) or len(screenshot) <= 0:
                self.logger.warning(bstack1111l1_opy_ (u"ࠢࡪࡰࡹࡥࡱ࡯ࡤࠡࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠥ࡯࡭ࡢࡩࡨࠤࡧࡧࡳࡦ࠸࠷ࠤࡸࡺࡲࠣዐ"))
                return
            bstack1l1ll1111ll_opy_ = self.bstack1l1lll11111_opy_(instance)
            if bstack1l1ll1111ll_opy_:
                entry = bstack1ll1l1l1lll_opy_(TestFramework.bstack1l1ll11ll11_opy_, screenshot)
                self.bstack1l1l1l111l1_opy_(bstack1l1ll1111ll_opy_, [entry])
                instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠣࡱ࠴࠵ࡾࡀ࡯࡯ࡡࡤࡪࡹ࡫ࡲࡠࡧࡻࡩࡨࡻࡴࡦࠤዑ"), datetime.now() - bstack1l1ll1llll1_opy_)
            else:
                self.logger.warning(bstack1111l1_opy_ (u"ࠤࡸࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡪࡥࡵࡧࡵࡱ࡮ࡴࡥࠡࡶࡨࡷࡹࠦࡦࡰࡴࠣࡻ࡭࡯ࡣࡩࠢࡷ࡬࡮ࡹࠠࡴࡥࡵࡩࡪࡴࡳࡩࡱࡷࠤࡼࡧࡳࠡࡶࡤ࡯ࡪࡴࠠࡣࡻࠣࡨࡷ࡯ࡶࡦࡴࡀࠤࢀࢃࠢዒ").format(instance.ref()))
        event = {}
        bstack1l1ll1111ll_opy_ = self.bstack1l1lll11111_opy_(instance)
        if bstack1l1ll1111ll_opy_:
            self.bstack1l1l1llll11_opy_(event, bstack1l1ll1111ll_opy_)
            if event.get(bstack1111l1_opy_ (u"ࠥࡰࡴ࡭ࡳࠣዓ")):
                self.bstack1l1l1l111l1_opy_(bstack1l1ll1111ll_opy_, event[bstack1111l1_opy_ (u"ࠦࡱࡵࡧࡴࠤዔ")])
            else:
                self.logger.debug(bstack1111l1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡦࡨࡸࡪࡸ࡭ࡪࡰࡨࠤࡱࡵࡧࡴࠢࡩࡳࡷࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࠣࡩࡻ࡫࡮ࡵࠤዕ"))
    @measure(event_name=EVENTS.bstack1l1ll11l11l_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def bstack1l1l1l111l1_opy_(
        self,
        bstack1l1ll1111ll_opy_: bstack1ll1llll1l1_opy_,
        entries: List[bstack1ll1l1l1lll_opy_],
    ):
        self.bstack1ll11111l1l_opy_()
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1lllll111l1_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1ll11l11ll1_opy_)
        req.execution_context.hash = str(bstack1l1ll1111ll_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1ll1111ll_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1ll1111ll_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1lllll111l1_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1ll1111llll_opy_)
            log_entry.test_framework_version = TestFramework.bstack1lllll111l1_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1l1l11llll1_opy_)
            log_entry.uuid = TestFramework.bstack1lllll111l1_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1ll11l111l1_opy_)
            log_entry.test_framework_state = bstack1l1ll1111ll_opy_.state.name
            log_entry.message = entry.message.encode(bstack1111l1_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧዖ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack1111l1_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤ዗"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1l1ll1ll1_opy_
                log_entry.file_path = entry.bstack1l1lll_opy_
        def bstack1l1l1ll1l11_opy_():
            bstack1lll11l11_opy_ = datetime.now()
            try:
                self.bstack1lll1l1lll1_opy_.LogCreatedEvent(req)
                if entry.kind == TestFramework.bstack1l1ll11ll11_opy_:
                    bstack1l1ll1111ll_opy_.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠧዘ"), datetime.now() - bstack1lll11l11_opy_)
                elif entry.kind == TestFramework.bstack1l1lll1111l_opy_:
                    bstack1l1ll1111ll_opy_.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡴࡧࡱࡨࡤࡲ࡯ࡨࡡࡦࡶࡪࡧࡴࡦࡦࡢࡩࡻ࡫࡮ࡵࡡࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠨዙ"), datetime.now() - bstack1lll11l11_opy_)
                else:
                    bstack1l1ll1111ll_opy_.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠥ࡫ࡷࡶࡣ࠻ࡵࡨࡲࡩࡥ࡬ࡰࡩࡢࡧࡷ࡫ࡡࡵࡧࡧࡣࡪࡼࡥ࡯ࡶࡢࡰࡴ࡭ࠢዚ"), datetime.now() - bstack1lll11l11_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1111l1_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤዛ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1lllllll1l1_opy_.enqueue(bstack1l1l1ll1l11_opy_)
    @measure(event_name=EVENTS.bstack1l1l1l1lll1_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def bstack1l1l1l11lll_opy_(
        self,
        instance: bstack1ll1llll1l1_opy_,
        bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_],
        event_json=None,
    ):
        self.bstack1ll11111l1l_opy_()
        req = structs.TestFrameworkEventRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1ll11l11ll1_opy_)
        req.test_framework_name = TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1ll1111llll_opy_)
        req.test_framework_version = TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l1l11llll1_opy_)
        req.test_framework_state = bstack1llll1ll1l1_opy_[0].name
        req.test_hook_state = bstack1llll1ll1l1_opy_[1].name
        started_at = TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l1ll1lll11_opy_, None)
        if started_at:
            req.started_at = started_at.isoformat()
        ended_at = TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l1l1lll1l1_opy_, None)
        if ended_at:
            req.ended_at = ended_at.isoformat()
        req.uuid = instance.ref()
        req.event_json = (event_json if event_json else dumps(instance.data, cls=bstack1l1l1ll1111_opy_)).encode(bstack1111l1_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦዜ"))
        req.execution_context.hash = str(instance.context.hash)
        req.execution_context.thread_id = str(instance.context.thread_id)
        req.execution_context.process_id = str(instance.context.process_id)
        def bstack1l1l1ll1l11_opy_():
            bstack1lll11l11_opy_ = datetime.now()
            try:
                self.bstack1lll1l1lll1_opy_.TestFrameworkEvent(req)
                instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠨࡧࡳࡲࡦ࠾ࡸ࡫࡮ࡥࡡࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡩࡻ࡫࡮ࡵࠤዝ"), datetime.now() - bstack1lll11l11_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1111l1_opy_ (u"ࠢࡳࡲࡦ࠱ࡪࡸࡲࡰࡴ࠽ࠤࠧዞ") + str(e))
                traceback.print_exc()
                raise e
        self.bstack1lllllll1l1_opy_.enqueue(bstack1l1l1ll1l11_opy_)
    def bstack1l1lll11111_opy_(self, instance: bstack1llll1l11l1_opy_):
        bstack1l1ll1lll1l_opy_ = TestFramework.bstack1llll11llll_opy_(instance.context)
        for t in bstack1l1ll1lll1l_opy_:
            bstack1l1ll1l1l1l_opy_ = TestFramework.bstack1lllll111l1_opy_(t, bstack1lll11ll1l1_opy_.bstack1l1l1l1ll11_opy_, [])
            if any(instance is d[1] for d in bstack1l1ll1l1l1l_opy_):
                return t
    def bstack1l1l1lll11l_opy_(self, message):
        self.bstack1l1l1l11l11_opy_(message + bstack1111l1_opy_ (u"ࠣ࡞ࡱࠦዟ"))
    def log_error(self, message):
        self.bstack1l1lll111ll_opy_(message + bstack1111l1_opy_ (u"ࠤ࡟ࡲࠧዠ"))
    def bstack1l1l1l111ll_opy_(self, level, original_func):
        def bstack1l1ll1l11l1_opy_(*args):
            return_value = original_func(*args)
            if not args or not isinstance(args[0], str) or not args[0].strip():
                return return_value
            message = args[0].strip()
            if bstack1111l1_opy_ (u"ࠥࡉࡻ࡫࡮ࡵࡆ࡬ࡷࡵࡧࡴࡤࡪࡨࡶࡒࡵࡤࡶ࡮ࡨࠦዡ") in message or bstack1111l1_opy_ (u"ࠦࡠ࡙ࡄࡌࡅࡏࡍࡢࠨዢ") in message or bstack1111l1_opy_ (u"ࠧࡡࡗࡦࡤࡇࡶ࡮ࡼࡥࡳࡏࡲࡨࡺࡲࡥ࡞ࠤዣ") in message:
                return return_value
            bstack1l1ll1lll1l_opy_ = TestFramework.bstack1l1ll1ll11l_opy_()
            if not bstack1l1ll1lll1l_opy_:
                return return_value
            bstack1l1ll1111ll_opy_ = next(
                (
                    instance
                    for instance in bstack1l1ll1lll1l_opy_
                    if TestFramework.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1ll11l111l1_opy_)
                ),
                None,
            )
            if not bstack1l1ll1111ll_opy_:
                return return_value
            entry = bstack1ll1l1l1lll_opy_(TestFramework.bstack1l1l1ll111l_opy_, message, level)
            self.bstack1l1l1l111l1_opy_(bstack1l1ll1111ll_opy_, [entry])
            return return_value
        return bstack1l1ll1l11l1_opy_
    def bstack1l1lll111l1_opy_(self):
        def bstack1l1ll11l1l1_opy_(*args, **kwargs):
            try:
                self.bstack1l1l1ll1l1l_opy_(*args, **kwargs)
                if not args:
                    return
                message = bstack1111l1_opy_ (u"࠭ࠠࠨዤ").join(str(arg) for arg in args)
                if not message.strip():
                    return
                if bstack1111l1_opy_ (u"ࠢࡆࡸࡨࡲࡹࡊࡩࡴࡲࡤࡸࡨ࡮ࡥࡳࡏࡲࡨࡺࡲࡥࠣዥ") in message:
                    return
                bstack1l1ll1lll1l_opy_ = TestFramework.bstack1l1ll1ll11l_opy_()
                if not bstack1l1ll1lll1l_opy_:
                    return
                bstack1l1ll1111ll_opy_ = next(
                    (
                        instance
                        for instance in bstack1l1ll1lll1l_opy_
                        if TestFramework.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1ll11l111l1_opy_)
                    ),
                    None,
                )
                if not bstack1l1ll1111ll_opy_:
                    return
                entry = bstack1ll1l1l1lll_opy_(TestFramework.bstack1l1l1ll111l_opy_, message, bstack1ll1llll11l_opy_.bstack1l1ll1ll1ll_opy_)
                self.bstack1l1l1l111l1_opy_(bstack1l1ll1111ll_opy_, [entry])
            except Exception as e:
                try:
                    self.bstack1l1l1ll1l1l_opy_(bstack11111l1ll1_opy_ (u"ࠣ࡝ࡈࡺࡪࡴࡴࡅ࡫ࡶࡴࡦࡺࡣࡩࡧࡵࡑࡴࡪࡵ࡭ࡧࡠࠤࡑࡵࡧࠡࡥࡤࡴࡹࡻࡲࡦࠢࡨࡶࡷࡵࡲ࠻ࠢࡾࡩࢂࠨዦ"))
                except:
                    pass
        return bstack1l1ll11l1l1_opy_
    def bstack1l1l1llll11_opy_(self, event: dict, instance=None) -> None:
        global _1l1ll11llll_opy_
        levels = [bstack1111l1_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧዧ"), bstack1111l1_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢየ")]
        bstack1l1l1lll1ll_opy_ = bstack1111l1_opy_ (u"ࠦࠧዩ")
        if instance is not None:
            try:
                bstack1l1l1lll1ll_opy_ = TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1ll11l111l1_opy_)
            except Exception as e:
                self.logger.warning(bstack1111l1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡻࡵࡪࡦࠣࡪࡷࡵ࡭ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧࠥዪ").format(e))
        bstack1l1ll11111l_opy_ = []
        try:
            for level in levels:
                platform_index = os.environ[bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ያ")]
                bstack1l1l1l1111l_opy_ = os.path.join(bstack1l1ll1lllll_opy_, (bstack1l1ll1l111l_opy_ + str(platform_index)), level)
                if not os.path.isdir(bstack1l1l1l1111l_opy_):
                    self.logger.debug(bstack1111l1_opy_ (u"ࠢࡅ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡲࡴࡺࠠࡱࡴࡨࡷࡪࡴࡴࠡࡨࡲࡶࠥࡶࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡗࡩࡸࡺࠠࡢࡰࡧࠤࡇࡻࡩ࡭ࡦࠣࡰࡪࡼࡥ࡭ࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠࡼࡿࠥዬ").format(bstack1l1l1l1111l_opy_))
                    continue
                file_names = os.listdir(bstack1l1l1l1111l_opy_)
                for file_name in file_names:
                    file_path = os.path.join(bstack1l1l1l1111l_opy_, file_name)
                    abs_path = os.path.abspath(file_path)
                    if abs_path in _1l1ll11llll_opy_:
                        self.logger.info(bstack1111l1_opy_ (u"ࠣࡒࡤࡸ࡭ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡿࢂࠨይ").format(abs_path))
                        continue
                    if os.path.isfile(file_path):
                        try:
                            bstack1l1l1l11111_opy_ = os.path.getmtime(file_path)
                            timestamp = datetime.fromtimestamp(bstack1l1l1l11111_opy_, tz=timezone.utc).isoformat()
                            file_size = os.path.getsize(file_path)
                            if level == bstack1111l1_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧዮ"):
                                entry = bstack1ll1l1l1lll_opy_(
                                    kind=bstack1111l1_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧዯ"),
                                    message=bstack1111l1_opy_ (u"ࠦࠧደ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1l1ll1ll1_opy_=file_size,
                                    bstack1l1ll111l11_opy_=bstack1111l1_opy_ (u"ࠧࡓࡁࡏࡗࡄࡐࡤ࡛ࡐࡍࡑࡄࡈࠧዱ"),
                                    bstack1l1lll_opy_=os.path.abspath(file_path),
                                    bstack1l1ll1ll_opy_=bstack1l1l1lll1ll_opy_
                                )
                            elif level == bstack1111l1_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࠥዲ"):
                                entry = bstack1ll1l1l1lll_opy_(
                                    kind=bstack1111l1_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤዳ"),
                                    message=bstack1111l1_opy_ (u"ࠣࠤዴ"),
                                    level=level,
                                    timestamp=timestamp,
                                    fileName=file_name,
                                    bstack1l1l1ll1ll1_opy_=file_size,
                                    bstack1l1ll111l11_opy_=bstack1111l1_opy_ (u"ࠤࡐࡅࡓ࡛ࡁࡍࡡࡘࡔࡑࡕࡁࡅࠤድ"),
                                    bstack1l1lll_opy_=os.path.abspath(file_path),
                                    bstack1l1l1lll111_opy_=bstack1l1l1lll1ll_opy_
                                )
                            bstack1l1ll11111l_opy_.append(entry)
                            _1l1ll11llll_opy_.add(abs_path)
                        except Exception as bstack1l1ll11l1ll_opy_:
                            self.logger.error(bstack1111l1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡲࡢ࡫ࡶࡩࡩࠦࡷࡩࡧࡱࠤࡵࡸ࡯ࡤࡧࡶࡷ࡮ࡴࡧࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡻࡾࠤዶ").format(bstack1l1ll11l1ll_opy_))
        except Exception as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠦࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡳࡣ࡬ࡷࡪࡪࠠࡸࡪࡨࡲࠥࡶࡲࡰࡥࡨࡷࡸ࡯࡮ࡨࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹࠠࡼࡿࠥዷ").format(e))
        event[bstack1111l1_opy_ (u"ࠧࡲ࡯ࡨࡵࠥዸ")] = bstack1l1ll11111l_opy_
class bstack1l1l1ll1111_opy_(JSONEncoder):
    def __init__(self, **kwargs):
        self.bstack1l1l11lllll_opy_ = set()
        kwargs[bstack1111l1_opy_ (u"ࠨࡳ࡬࡫ࡳ࡯ࡪࡿࡳࠣዹ")] = True
        super().__init__(**kwargs)
    def default(self, obj):
        return bstack1l1ll1ll111_opy_(obj, self.bstack1l1l11lllll_opy_)
def bstack1l1ll1ll1l1_opy_(obj):
    return isinstance(obj, (str, int, float, bool, type(None)))
def bstack1l1ll1ll111_opy_(obj, bstack1l1l11lllll_opy_=None, max_depth=3):
    if bstack1l1l11lllll_opy_ is None:
        bstack1l1l11lllll_opy_ = set()
    if id(obj) in bstack1l1l11lllll_opy_ or max_depth <= 0:
        return None
    max_depth -= 1
    bstack1l1l11lllll_opy_.add(id(obj))
    if isinstance(obj, datetime):
        return obj.isoformat()
    bstack1l1l1llll1l_opy_ = TestFramework.bstack1l1ll1l1l11_opy_(obj)
    bstack1l1ll11lll1_opy_ = next((k.lower() in bstack1l1l1llll1l_opy_.lower() for k in bstack1l1l1l11l1l_opy_.keys()), None)
    if bstack1l1ll11lll1_opy_:
        obj = TestFramework.bstack1l1l1l1l1ll_opy_(obj, bstack1l1l1l11l1l_opy_[bstack1l1ll11lll1_opy_])
    if not isinstance(obj, dict):
        keys = []
        if hasattr(obj, bstack1111l1_opy_ (u"ࠢࡠࡡࡶࡰࡴࡺࡳࡠࡡࠥዺ")):
            keys = getattr(obj, bstack1111l1_opy_ (u"ࠣࡡࡢࡷࡱࡵࡴࡴࡡࡢࠦዻ"), [])
        elif hasattr(obj, bstack1111l1_opy_ (u"ࠤࡢࡣࡩ࡯ࡣࡵࡡࡢࠦዼ")):
            keys = getattr(obj, bstack1111l1_opy_ (u"ࠥࡣࡤࡪࡩࡤࡶࡢࡣࠧዽ"), {}).keys()
        else:
            keys = dir(obj)
        obj = {k: getattr(obj, k, None) for k in keys if not str(k).startswith(bstack1111l1_opy_ (u"ࠦࡤࠨዾ"))}
        if not obj and bstack1l1l1llll1l_opy_ == bstack1111l1_opy_ (u"ࠧࡶࡡࡵࡪ࡯࡭ࡧ࠴ࡐࡰࡵ࡬ࡼࡕࡧࡴࡩࠤዿ"):
            obj = {bstack1111l1_opy_ (u"ࠨࡰࡢࡶ࡫ࠦጀ"): str(obj)}
    result = {}
    for key, value in obj.items():
        if not bstack1l1ll1ll1l1_opy_(key) or str(key).startswith(bstack1111l1_opy_ (u"ࠢࡠࠤጁ")):
            continue
        if value is not None and bstack1l1ll1ll1l1_opy_(value):
            result[key] = value
        elif isinstance(value, dict):
            r = bstack1l1ll1ll111_opy_(value, bstack1l1l11lllll_opy_, max_depth)
            if r is not None:
                result[key] = r
        elif isinstance(value, (list, tuple, set, frozenset)):
            result[key] = list(filter(None, [bstack1l1ll1ll111_opy_(o, bstack1l1l11lllll_opy_, max_depth) for o in value]))
    return result or None