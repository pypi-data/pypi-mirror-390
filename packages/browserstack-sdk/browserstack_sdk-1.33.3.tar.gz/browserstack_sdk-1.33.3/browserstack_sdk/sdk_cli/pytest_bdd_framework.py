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
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Any, Tuple
from browserstack_sdk.sdk_cli.bstack1llll1lll11_opy_ import bstack1lllll11l1l_opy_
from browserstack_sdk.sdk_cli.utils.bstack11l11lll1l_opy_ import bstack1l111111111_opy_
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1ll1ll1lll1_opy_,
    bstack1ll1llll1l1_opy_,
    bstack1lll11l11ll_opy_,
    bstack11llll1l1ll_opy_,
    bstack1ll1l1l1lll_opy_,
)
import traceback
from bstack_utils.helper import bstack1l1ll1111l1_opy_
from bstack_utils.bstack1llll1llll_opy_ import bstack1llll11l111_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.utils.bstack1lll1ll111l_opy_ import bstack1lll1lll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1lllllll1l1_opy_ import bstack1lllllll1ll_opy_
bstack1l1ll1lllll_opy_ = bstack1l1ll1111l1_opy_()
bstack1l1ll1l111l_opy_ = bstack1111l1_opy_ (u"࡚ࠦࡶ࡬ࡰࡣࡧࡩࡩࡇࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵ࠰ࠦᑕ")
bstack1l111l111l1_opy_ = bstack1111l1_opy_ (u"ࠧࡎ࡯ࡰ࡭ࡏࡩࡻ࡫࡬ࠣᑖ")
bstack1l11111l1l1_opy_ = bstack1111l1_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠧᑗ")
bstack11lllllll11_opy_ = 1.0
_1l1ll11llll_opy_ = set()
class PytestBDDFramework(TestFramework):
    bstack1l1111111ll_opy_ = bstack1111l1_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡩࡹࡶࡸࡶࡪࡹࠢᑘ")
    bstack1l1111lllll_opy_ = bstack1111l1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࠨᑙ")
    bstack1l1111l1l11_opy_ = bstack1111l1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡸࡥࡦࡪࡰ࡬ࡷ࡭࡫ࡤࠣᑚ")
    bstack1l1111l1111_opy_ = bstack1111l1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥ࡬ࡢࡵࡷࡣࡸࡺࡡࡳࡶࡨࡨࠧᑛ")
    bstack1l111l1ll11_opy_ = bstack1111l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟࡭ࡣࡶࡸࡤ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪࠢᑜ")
    bstack1l1111ll1ll_opy_: bool
    bstack1lllllll1l1_opy_: bstack1lllllll1ll_opy_  = None
    bstack1l1111ll111_opy_ = [
        bstack1ll1ll1lll1_opy_.BEFORE_ALL,
        bstack1ll1ll1lll1_opy_.AFTER_ALL,
        bstack1ll1ll1lll1_opy_.BEFORE_EACH,
        bstack1ll1ll1lll1_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack11lllll1ll1_opy_: Dict[str, str],
        bstack1ll11lll11l_opy_: List[str]=[bstack1111l1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠤᑝ")],
        bstack1lllllll1l1_opy_: bstack1lllllll1ll_opy_ = None,
        bstack1lll1l1lll1_opy_=None
    ):
        super().__init__(bstack1ll11lll11l_opy_, bstack11lllll1ll1_opy_, bstack1lllllll1l1_opy_)
        self.bstack1l1111ll1ll_opy_ = any(bstack1111l1_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠥᑞ") in item.lower() for item in bstack1ll11lll11l_opy_)
        self.bstack1lll1l1lll1_opy_ = bstack1lll1l1lll1_opy_
    def track_event(
        self,
        context: bstack11llll1l1ll_opy_,
        test_framework_state: bstack1ll1ll1lll1_opy_,
        test_hook_state: bstack1lll11l11ll_opy_,
        *args,
        **kwargs,
    ):
        super().track_event(self, context, test_framework_state, test_hook_state, *args, **kwargs)
        if test_framework_state == bstack1ll1ll1lll1_opy_.TEST or test_framework_state in PytestBDDFramework.bstack1l1111ll111_opy_:
            bstack1l111111111_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1ll1ll1lll1_opy_.NONE:
            self.logger.warning(bstack1111l1_opy_ (u"ࠢࡪࡩࡱࡳࡷ࡫ࡤࠡࡥࡤࡰࡱࡨࡡࡤ࡭ࠣࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࡹ࡫ࡳࡵࡡࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡹࡴࡢࡶࡨࢁࠥࡺࡥࡴࡶࡢ࡬ࡴࡵ࡫ࡠࡵࡷࡥࡹ࡫࠽ࠣᑟ") + str(test_hook_state) + bstack1111l1_opy_ (u"ࠣࠤᑠ"))
            return
        if not self.bstack1l1111ll1ll_opy_:
            self.logger.warning(bstack1111l1_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡷࡱࡷࡺࡶࡰࡰࡴࡷࡩࡩࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬࠿ࠥᑡ") + str(str(self.bstack1ll11lll11l_opy_)) + bstack1111l1_opy_ (u"ࠥࠦᑢ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack1111l1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡫ࡸࡱࡧࡦࡸࡪࡪࠠࡢࡴࡪࡷࡂࢁࡡࡳࡩࡶࢁࠥࡱࡷࡢࡴࡪࡷࡂࠨᑣ") + str(kwargs) + bstack1111l1_opy_ (u"ࠧࠨᑤ"))
            return
        instance = self.__1l11111ll1l_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack1111l1_opy_ (u"ࠨࡴࡳࡣࡦ࡯ࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡡࡳࡩࡶࡁࠧᑥ") + str(args) + bstack1111l1_opy_ (u"ࠢࠣᑦ"))
            return
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l1111ll111_opy_ and test_hook_state == bstack1lll11l11ll_opy_.PRE:
                bstack1ll11l111ll_opy_ = bstack1llll11l111_opy_.bstack1ll11ll11l1_opy_(EVENTS.bstack1ll1l1111_opy_.value)
                name = str(EVENTS.bstack1ll1l1111_opy_.name)+bstack1111l1_opy_ (u"ࠣ࠼ࠥᑧ")+str(test_framework_state.name)
                TestFramework.bstack1l111l11ll1_opy_(instance, name, bstack1ll11l111ll_opy_)
        except Exception as e:
            self.logger.debug(bstack1111l1_opy_ (u"ࠤࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡪࡲࡳࡰࠦࡥࡳࡴࡲࡶࠥࡶࡲࡦ࠼ࠣࡿࢂࠨᑨ").format(e))
        try:
            if test_framework_state == bstack1ll1ll1lll1_opy_.TEST:
                if not TestFramework.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1l11111l111_opy_) and test_hook_state == bstack1lll11l11ll_opy_.PRE:
                    if not (len(args) >= 3):
                        return
                    test = PytestBDDFramework.__11llllll1l1_opy_(args)
                    if test:
                        instance.data.update(test)
                        self.logger.debug(bstack1111l1_opy_ (u"ࠥࡰࡴࡧࡤࡦࡦࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᑩ") + str(test_hook_state) + bstack1111l1_opy_ (u"ࠦࠧᑪ"))
                if test_hook_state == bstack1lll11l11ll_opy_.PRE and not TestFramework.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1l1ll1lll11_opy_):
                    TestFramework.bstack1lllll1l1l1_opy_(instance, TestFramework.bstack1l1ll1lll11_opy_, datetime.now(tz=timezone.utc))
                    PytestBDDFramework.__1l1111l1lll_opy_(instance, args)
                    self.logger.debug(bstack1111l1_opy_ (u"ࠧࡹࡥࡵࠢࡷࡩࡸࡺ࠭ࡴࡶࡤࡶࡹࠦࡦࡰࡴࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᑫ") + str(test_hook_state) + bstack1111l1_opy_ (u"ࠨࠢᑬ"))
                elif test_hook_state == bstack1lll11l11ll_opy_.POST and not TestFramework.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1l1l1lll1l1_opy_):
                    TestFramework.bstack1lllll1l1l1_opy_(instance, TestFramework.bstack1l1l1lll1l1_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack1111l1_opy_ (u"ࠢࡴࡧࡷࠤࡹ࡫ࡳࡵ࠯ࡨࡲࡩࠦࡦࡰࡴࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࡂࢁࡩ࡯ࡵࡷࡥࡳࡩࡥ࠯ࡴࡨࡪ࠭࠯ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᑭ") + str(test_hook_state) + bstack1111l1_opy_ (u"ࠣࠤᑮ"))
            elif test_framework_state == bstack1ll1ll1lll1_opy_.STEP:
                if test_hook_state == bstack1lll11l11ll_opy_.PRE:
                    PytestBDDFramework.__1l111l1l111_opy_(instance, args)
                elif test_hook_state == bstack1lll11l11ll_opy_.POST:
                    PytestBDDFramework.__1l111l1lll1_opy_(instance, args)
            elif test_framework_state == bstack1ll1ll1lll1_opy_.LOG and test_hook_state == bstack1lll11l11ll_opy_.POST:
                PytestBDDFramework.__1l111ll1ll1_opy_(instance, *args)
            elif test_framework_state == bstack1ll1ll1lll1_opy_.LOG_REPORT and test_hook_state == bstack1lll11l11ll_opy_.POST:
                self.__11llllll111_opy_(instance, *args)
                self.__1l111l11111_opy_(instance)
            elif test_framework_state in PytestBDDFramework.bstack1l1111ll111_opy_:
                self.__1l1111111l1_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack1111l1_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡪࡤࡲࡩࡲࡥࡥࠢࡨࡺࡪࡴࡴ࠾ࡽࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦࡿ࠱ࡿࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡪࡰࡶࡸࡦࡴࡣࡦ࠿ࠥᑯ") + str(instance.ref()) + bstack1111l1_opy_ (u"ࠥࠦᑰ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack11llllll1ll_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in PytestBDDFramework.bstack1l1111ll111_opy_ and test_hook_state == bstack1lll11l11ll_opy_.POST:
                name = str(EVENTS.bstack1ll1l1111_opy_.name)+bstack1111l1_opy_ (u"ࠦ࠿ࠨᑱ")+str(test_framework_state.name)
                bstack1ll11l111ll_opy_ = TestFramework.bstack1l1111l11l1_opy_(instance, name)
                bstack1llll11l111_opy_.end(EVENTS.bstack1ll1l1111_opy_.value, bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠧࡀࡳࡵࡣࡵࡸࠧᑲ"), bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠨ࠺ࡦࡰࡧࠦᑳ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack1111l1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡨࡰࡱ࡮ࠤࡪࡸࡲࡰࡴ࠽ࠤࢀࢃࠢᑴ").format(e))
    def bstack1l1ll1l1111_opy_(self):
        return self.bstack1l1111ll1ll_opy_
    def __1l111111l1l_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack1111l1_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡴࡷ࡯ࡸࠧᑵ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1l1l1l1ll_opy_(rep, [bstack1111l1_opy_ (u"ࠤࡺ࡬ࡪࡴࠢᑶ"), bstack1111l1_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᑷ"), bstack1111l1_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦᑸ"), bstack1111l1_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧᑹ"), bstack1111l1_opy_ (u"ࠨࡳ࡬࡫ࡳࡴࡪࡪࠢᑺ"), bstack1111l1_opy_ (u"ࠢ࡭ࡱࡱ࡫ࡷ࡫ࡰࡳࡶࡨࡼࡹࠨᑻ")])
        return None
    def __11llllll111_opy_(self, instance: bstack1ll1llll1l1_opy_, *args):
        result = self.__1l111111l1l_opy_(*args)
        if not result:
            return
        failure = None
        bstack11111111l1_opy_ = None
        if result.get(bstack1111l1_opy_ (u"ࠣࡱࡸࡸࡨࡵ࡭ࡦࠤᑼ"), None) == bstack1111l1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤᑽ") and len(args) > 1 and getattr(args[1], bstack1111l1_opy_ (u"ࠥࡩࡽࡩࡩ࡯ࡨࡲࠦᑾ"), None) is not None:
            failure = [{bstack1111l1_opy_ (u"ࠫࡧࡧࡣ࡬ࡶࡵࡥࡨ࡫ࠧᑿ"): [args[1].excinfo.exconly(), result.get(bstack1111l1_opy_ (u"ࠧࡲ࡯࡯ࡩࡵࡩࡵࡸࡴࡦࡺࡷࠦᒀ"), None)]}]
            bstack11111111l1_opy_ = bstack1111l1_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࡇࡵࡶࡴࡸࠢᒁ") if bstack1111l1_opy_ (u"ࠢࡂࡵࡶࡩࡷࡺࡩࡰࡰࠥᒂ") in getattr(args[1].excinfo, bstack1111l1_opy_ (u"ࠣࡶࡼࡴࡪࡴࡡ࡮ࡧࠥᒃ"), bstack1111l1_opy_ (u"ࠤࠥᒄ")) else bstack1111l1_opy_ (u"࡙ࠥࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࡋࡲࡳࡱࡵࠦᒅ")
        bstack11llll1llll_opy_ = result.get(bstack1111l1_opy_ (u"ࠦࡴࡻࡴࡤࡱࡰࡩࠧᒆ"), TestFramework.bstack1l11111ll11_opy_)
        if bstack11llll1llll_opy_ != TestFramework.bstack1l11111ll11_opy_:
            TestFramework.bstack1lllll1l1l1_opy_(instance, TestFramework.bstack1l1l1l1llll_opy_, datetime.now(tz=timezone.utc))
        TestFramework.bstack11llll1l111_opy_(instance, {
            TestFramework.bstack1l11lll1l11_opy_: failure,
            TestFramework.bstack1l111l1l11l_opy_: bstack11111111l1_opy_,
            TestFramework.bstack1l11lll1l1l_opy_: bstack11llll1llll_opy_,
        })
    def __1l11111ll1l_opy_(
        self,
        context: bstack11llll1l1ll_opy_,
        test_framework_state: bstack1ll1ll1lll1_opy_,
        test_hook_state: bstack1lll11l11ll_opy_,
        *args,
        **kwargs,
    ):
        instance = None
        if test_framework_state == bstack1ll1ll1lll1_opy_.SETUP_FIXTURE:
            instance = self.__1l1111ll11l_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        else:
            target = None # bstack1l111ll1111_opy_ bstack11llll1l11l_opy_ this to be bstack1111l1_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᒇ")
            if test_framework_state == bstack1ll1ll1lll1_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__1l1111l1ll1_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1ll1ll1lll1_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack1111l1_opy_ (u"ࠨ࡮ࡰࡦࡨࠦᒈ"), None), bstack1111l1_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᒉ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack1111l1_opy_ (u"ࠣࡰࡲࡨࡪࠨᒊ"), None):
                target = args[0].node.nodeid
            elif getattr(args[0], bstack1111l1_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᒋ"), None):
                target = args[0].nodeid
            instance = TestFramework.bstack1llll1l1lll_opy_(target) if target else None
        return instance
    def __1l1111111l1_opy_(
        self,
        instance: bstack1ll1llll1l1_opy_,
        test_framework_state: bstack1ll1ll1lll1_opy_,
        test_hook_state: bstack1lll11l11ll_opy_,
        *args,
    ):
        key = test_framework_state.name
        bstack11llll1ll11_opy_ = TestFramework.bstack1lllll111l1_opy_(instance, PytestBDDFramework.bstack1l1111lllll_opy_, {})
        if not key in bstack11llll1ll11_opy_:
            bstack11llll1ll11_opy_[key] = []
        bstack11lllllll1l_opy_ = TestFramework.bstack1lllll111l1_opy_(instance, PytestBDDFramework.bstack1l1111l1l11_opy_, {})
        if not key in bstack11lllllll1l_opy_:
            bstack11lllllll1l_opy_[key] = []
        bstack1l111ll11ll_opy_ = {
            PytestBDDFramework.bstack1l1111lllll_opy_: bstack11llll1ll11_opy_,
            PytestBDDFramework.bstack1l1111l1l11_opy_: bstack11lllllll1l_opy_,
        }
        if test_hook_state == bstack1lll11l11ll_opy_.PRE:
            hook_name = args[1] if len(args) > 1 else None
            hook = {
                bstack1111l1_opy_ (u"ࠥ࡯ࡪࡿࠢᒌ"): key,
                TestFramework.bstack1l1111lll11_opy_: uuid4().__str__(),
                TestFramework.bstack1l1111l111l_opy_: TestFramework.bstack1l1111l1l1l_opy_,
                TestFramework.bstack11lllll11l1_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack1l11111llll_opy_: [],
                TestFramework.bstack1l11111111l_opy_: hook_name,
                TestFramework.bstack1l111l1llll_opy_: bstack1lll1lll1ll_opy_.bstack1l111ll1l1l_opy_()
            }
            bstack11llll1ll11_opy_[key].append(hook)
            bstack1l111ll11ll_opy_[PytestBDDFramework.bstack1l1111l1111_opy_] = key
        elif test_hook_state == bstack1lll11l11ll_opy_.POST:
            bstack1l111l1ll1l_opy_ = bstack11llll1ll11_opy_.get(key, [])
            hook = bstack1l111l1ll1l_opy_.pop() if bstack1l111l1ll1l_opy_ else None
            if hook:
                result = self.__1l111111l1l_opy_(*args)
                if result:
                    bstack1l111ll11l1_opy_ = result.get(bstack1111l1_opy_ (u"ࠦࡴࡻࡴࡤࡱࡰࡩࠧᒍ"), TestFramework.bstack1l1111l1l1l_opy_)
                    if bstack1l111ll11l1_opy_ != TestFramework.bstack1l1111l1l1l_opy_:
                        hook[TestFramework.bstack1l1111l111l_opy_] = bstack1l111ll11l1_opy_
                hook[TestFramework.bstack1l1111llll1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack1l111l1llll_opy_] = bstack1lll1lll1ll_opy_.bstack1l111ll1l1l_opy_()
                self.bstack1l111l11l11_opy_(hook)
                logs = hook.get(TestFramework.bstack1l111l11lll_opy_, [])
                self.bstack1l1l1l111l1_opy_(instance, logs)
                bstack11lllllll1l_opy_[key].append(hook)
                bstack1l111ll11ll_opy_[PytestBDDFramework.bstack1l111l1ll11_opy_] = key
        TestFramework.bstack11llll1l111_opy_(instance, bstack1l111ll11ll_opy_)
        self.logger.debug(bstack1111l1_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣ࡭ࡵ࡯࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࡁࢀࡱࡥࡺࡿ࠱ࡿࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࢃࠠࡩࡱࡲ࡯ࡸࡥࡳࡵࡣࡵࡸࡪࡪ࠽ࡼࡪࡲࡳࡰࡹ࡟ࡴࡶࡤࡶࡹ࡫ࡤࡾࠢ࡫ࡳࡴࡱࡳࡠࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡀࠦᒎ") + str(bstack11lllllll1l_opy_) + bstack1111l1_opy_ (u"ࠨࠢᒏ"))
    def __1l1111ll11l_opy_(
        self,
        context: bstack11llll1l1ll_opy_,
        test_framework_state: bstack1ll1ll1lll1_opy_,
        test_hook_state: bstack1lll11l11ll_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1l1l1l1ll_opy_(args[0], [bstack1111l1_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᒐ"), bstack1111l1_opy_ (u"ࠣࡣࡵ࡫ࡳࡧ࡭ࡦࠤᒑ"), bstack1111l1_opy_ (u"ࠤࡳࡥࡷࡧ࡭ࡴࠤᒒ"), bstack1111l1_opy_ (u"ࠥ࡭ࡩࡹࠢᒓ"), bstack1111l1_opy_ (u"ࠦࡺࡴࡩࡵࡶࡨࡷࡹࠨᒔ"), bstack1111l1_opy_ (u"ࠧࡨࡡࡴࡧ࡬ࡨࠧᒕ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scenario = args[2] if len(args) == 3 else None
        scope = request.scope if hasattr(request, bstack1111l1_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᒖ")) else fixturedef.get(bstack1111l1_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᒗ"), None)
        fixturename = request.fixturename if hasattr(request, bstack1111l1_opy_ (u"ࠣࡨ࡬ࡼࡹࡻࡲࡦࡰࡤࡱࡪࠨᒘ")) else None
        node = request.node if hasattr(request, bstack1111l1_opy_ (u"ࠤࡱࡳࡩ࡫ࠢᒙ")) else None
        target = request.node.nodeid if hasattr(node, bstack1111l1_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᒚ")) else None
        baseid = fixturedef.get(bstack1111l1_opy_ (u"ࠦࡧࡧࡳࡦ࡫ࡧࠦᒛ"), None) or bstack1111l1_opy_ (u"ࠧࠨᒜ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack1111l1_opy_ (u"ࠨ࡟ࡱࡻࡩࡹࡳࡩࡩࡵࡧࡰࠦᒝ")):
            target = PytestBDDFramework.__11lllll1lll_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack1111l1_opy_ (u"ࠢ࡭ࡱࡦࡥࡹ࡯࡯࡯ࠤᒞ")) else None
            if target and not TestFramework.bstack1llll1l1lll_opy_(target):
                self.__1l1111l1ll1_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack1111l1_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠࡧࡹࡩࡳࡺ࠺ࠡࡨࡤࡰࡱࡨࡡࡤ࡭ࠣࡸࡦࡸࡧࡦࡶࡀࡿࡹࡧࡲࡨࡧࡷࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡲࡴࡪࡥ࠾ࡽࡱࡳࡩ࡫ࡽࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࠥᒟ") + str(test_hook_state) + bstack1111l1_opy_ (u"ࠤࠥᒠ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack1111l1_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡩ࡭ࡽࡺࡵࡳࡧࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡹࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࠦࡥࡷࡧࡱࡸࡂࢁࡴࡦࡵࡷࡣ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡶࡤࡸࡪࢃ࠮ࡼࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡩ࡫ࡦ࠾ࡽࡩ࡭ࡽࡺࡵࡳࡧࡧࡩ࡫ࢃࠠࡴࡥࡲࡴࡪࡃࡻࡴࡥࡲࡴࡪࢃࠠࡵࡣࡵ࡫ࡪࡺ࠽ࠣᒡ") + str(target) + bstack1111l1_opy_ (u"ࠦࠧᒢ"))
            return None
        instance = TestFramework.bstack1llll1l1lll_opy_(target)
        if not instance:
            self.logger.warning(bstack1111l1_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣ࡫࡯ࡸࡵࡷࡵࡩࡤ࡫ࡶࡦࡰࡷ࠾ࠥࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤࡧࡧࡳࡦ࡫ࡧࡁࢀࡨࡡࡴࡧ࡬ࡨࢂࠦࡴࡢࡴࡪࡩࡹࡃࠢᒣ") + str(target) + bstack1111l1_opy_ (u"ࠨࠢᒤ"))
            return None
        bstack11lllll1111_opy_ = TestFramework.bstack1lllll111l1_opy_(instance, PytestBDDFramework.bstack1l1111111ll_opy_, {})
        if os.getenv(bstack1111l1_opy_ (u"ࠢࡔࡆࡎࡣࡈࡒࡉࡠࡈࡏࡅࡌࡥࡆࡊ࡚ࡗ࡙ࡗࡋࡓࠣᒥ"), bstack1111l1_opy_ (u"ࠣ࠳ࠥᒦ")) == bstack1111l1_opy_ (u"ࠤ࠴ࠦᒧ"):
            bstack1l111ll1lll_opy_ = bstack1111l1_opy_ (u"ࠥ࠾ࠧᒨ").join((scope, fixturename))
            bstack11llll1l1l1_opy_ = datetime.now(tz=timezone.utc)
            bstack11lllllllll_opy_ = {
                bstack1111l1_opy_ (u"ࠦࡰ࡫ࡹࠣᒩ"): bstack1l111ll1lll_opy_,
                bstack1111l1_opy_ (u"ࠧࡺࡡࡨࡵࠥᒪ"): PytestBDDFramework.__1l1111lll1l_opy_(request.node, scenario),
                bstack1111l1_opy_ (u"ࠨࡦࡪࡺࡷࡹࡷ࡫ࠢᒫ"): fixturedef,
                bstack1111l1_opy_ (u"ࠢࡴࡥࡲࡴࡪࠨᒬ"): scope,
                bstack1111l1_opy_ (u"ࠣࡶࡼࡴࡪࠨᒭ"): None,
            }
            try:
                if test_hook_state == bstack1lll11l11ll_opy_.POST and callable(getattr(args[-1], bstack1111l1_opy_ (u"ࠤࡪࡩࡹࡥࡲࡦࡵࡸࡰࡹࠨᒮ"), None)):
                    bstack11lllllllll_opy_[bstack1111l1_opy_ (u"ࠥࡸࡾࡶࡥࠣᒯ")] = TestFramework.bstack1l1ll1l1l11_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll11l11ll_opy_.PRE:
                bstack11lllllllll_opy_[bstack1111l1_opy_ (u"ࠦࡺࡻࡩࡥࠤᒰ")] = uuid4().__str__()
                bstack11lllllllll_opy_[PytestBDDFramework.bstack11lllll11l1_opy_] = bstack11llll1l1l1_opy_
            elif test_hook_state == bstack1lll11l11ll_opy_.POST:
                bstack11lllllllll_opy_[PytestBDDFramework.bstack1l1111llll1_opy_] = bstack11llll1l1l1_opy_
            if bstack1l111ll1lll_opy_ in bstack11lllll1111_opy_:
                bstack11lllll1111_opy_[bstack1l111ll1lll_opy_].update(bstack11lllllllll_opy_)
                self.logger.debug(bstack1111l1_opy_ (u"ࠧࡻࡰࡥࡣࡷࡩࡩࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡂࠨᒱ") + str(bstack11lllll1111_opy_[bstack1l111ll1lll_opy_]) + bstack1111l1_opy_ (u"ࠨࠢᒲ"))
            else:
                bstack11lllll1111_opy_[bstack1l111ll1lll_opy_] = bstack11lllllllll_opy_
                self.logger.debug(bstack1111l1_opy_ (u"ࠢࡴࡣࡹࡩࡩࠦࡦࡪࡺࡷࡹࡷ࡫࡮ࡢ࡯ࡨࡁࢀ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࢀࠤࡸࡩ࡯ࡱࡧࡀࡿࡸࡩ࡯ࡱࡧࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡂࢁࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࢂࠦࡴࡳࡣࡦ࡯ࡪࡪ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡴ࠿ࠥᒳ") + str(len(bstack11lllll1111_opy_)) + bstack1111l1_opy_ (u"ࠣࠤᒴ"))
        TestFramework.bstack1lllll1l1l1_opy_(instance, PytestBDDFramework.bstack1l1111111ll_opy_, bstack11lllll1111_opy_)
        self.logger.debug(bstack1111l1_opy_ (u"ࠤࡶࡥࡻ࡫ࡤࠡࡨ࡬ࡼࡹࡻࡲࡦࡵࡀࡿࡱ࡫࡮ࠩࡶࡵࡥࡨࡱࡥࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࡶ࠭ࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤᒵ") + str(instance.ref()) + bstack1111l1_opy_ (u"ࠥࠦᒶ"))
        return instance
    def __1l1111l1ll1_opy_(
        self,
        context: bstack11llll1l1ll_opy_,
        test_framework_state: bstack1ll1ll1lll1_opy_,
        target: Any,
        *args,
    ):
        ctx = bstack1lllll11l1l_opy_.create_context(target)
        ob = bstack1ll1llll1l1_opy_(ctx, self.bstack1ll11lll11l_opy_, self.bstack11lllll1ll1_opy_, test_framework_state)
        TestFramework.bstack11llll1l111_opy_(ob, {
            TestFramework.bstack1ll1111llll_opy_: context.test_framework_name,
            TestFramework.bstack1l1l11llll1_opy_: context.test_framework_version,
            TestFramework.bstack1l111l111ll_opy_: [],
            PytestBDDFramework.bstack1l1111111ll_opy_: {},
            PytestBDDFramework.bstack1l1111l1l11_opy_: {},
            PytestBDDFramework.bstack1l1111lllll_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1lllll1l1l1_opy_(ob, TestFramework.bstack1l111111l11_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1lllll1l1l1_opy_(ob, TestFramework.bstack1ll11l11ll1_opy_, context.platform_index)
        TestFramework.bstack1lllll1111l_opy_[ctx.id] = ob
        self.logger.debug(bstack1111l1_opy_ (u"ࠦࡸࡧࡶࡦࡦࠣ࡭ࡳࡹࡴࡢࡰࡦࡩࠥࡩࡴࡹ࠰࡬ࡨࡂࢁࡣࡵࡺ࠱࡭ࡩࢃࠠࡵࡣࡵ࡫ࡪࡺ࠽ࡼࡶࡤࡶ࡬࡫ࡴࡾࠢࡤࡶ࡬ࡹ࠽ࡼࡣࡵ࡫ࡸࢃࠠࡪࡰࡶࡸࡦࡴࡣࡦࡵࡀࠦᒷ") + str(TestFramework.bstack1lllll1111l_opy_.keys()) + bstack1111l1_opy_ (u"ࠧࠨᒸ"))
        return ob
    @staticmethod
    def __1l1111l1lll_opy_(instance, args):
        request, feature, scenario = args
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1111l1_opy_ (u"࠭ࡩࡥࠩᒹ"): id(step),
                bstack1111l1_opy_ (u"ࠧࡵࡧࡻࡸࠬᒺ"): step.name,
                bstack1111l1_opy_ (u"ࠨ࡭ࡨࡽࡼࡵࡲࡥࠩᒻ"): step.keyword,
            })
        meta = {
            bstack1111l1_opy_ (u"ࠩࡩࡩࡦࡺࡵࡳࡧࠪᒼ"): {
                bstack1111l1_opy_ (u"ࠪࡲࡦࡳࡥࠨᒽ"): feature.name,
                bstack1111l1_opy_ (u"ࠫࡵࡧࡴࡩࠩᒾ"): feature.filename,
                bstack1111l1_opy_ (u"ࠬࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠪᒿ"): feature.description
            },
            bstack1111l1_opy_ (u"࠭ࡳࡤࡧࡱࡥࡷ࡯࡯ࠨᓀ"): {
                bstack1111l1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᓁ"): scenario.name
            },
            bstack1111l1_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧᓂ"): steps,
            bstack1111l1_opy_ (u"ࠩࡨࡼࡦࡳࡰ࡭ࡧࡶࠫᓃ"): PytestBDDFramework.__11llll11ll1_opy_(request.node)
        }
        instance.data.update(
            {
                TestFramework.bstack1l111111ll1_opy_: meta
            }
        )
    def bstack1l111l11l11_opy_(self, hook: Dict[str, Any]) -> None:
        bstack1111l1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡑࡴࡲࡧࡪࡹࡳࡦࡵࠣࡸ࡭࡫ࠠࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮ࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡵ࡬ࡱ࡮ࡲࡡࡳࠢࡷࡳࠥࡺࡨࡦࠢࡍࡥࡻࡧࠠࡪ࡯ࡳࡰࡪࡳࡥ࡯ࡶࡤࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡘ࡭࡯ࡳࠡ࡯ࡨࡸ࡭ࡵࡤ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࠳ࠠࡄࡪࡨࡧࡰࡹࠠࡵࡪࡨࠤࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠠࡥ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣ࡭ࡳࡹࡩࡥࡧࠣࢂ࠴࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠴࡛ࡰ࡭ࡱࡤࡨࡪࡪࡁࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡊࡴࡸࠠࡦࡣࡦ࡬ࠥ࡬ࡩ࡭ࡧࠣ࡭ࡳࠦࡨࡰࡱ࡮ࡣࡱ࡫ࡶࡦ࡮ࡢࡪ࡮ࡲࡥࡴ࠮ࠣࡶࡪࡶ࡬ࡢࡥࡨࡷࠥࠨࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠤࠣࡻ࡮ࡺࡨࠡࠤࡋࡳࡴࡱࡌࡦࡸࡨࡰࠧࠦࡩ࡯ࠢ࡬ࡸࡸࠦࡰࡢࡶ࡫࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡ࠯ࠣࡍ࡫ࠦࡡࠡࡨ࡬ࡰࡪࠦࡩ࡯ࠢࡷ࡬ࡪࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢࡰࡥࡹࡩࡨࡦࡵࠣࡥࠥࡳ࡯ࡥ࡫ࡩ࡭ࡪࡪࠠࡩࡱࡲ࡯࠲ࡲࡥࡷࡧ࡯ࠤ࡫࡯࡬ࡦ࠮ࠣ࡭ࡹࠦࡣࡳࡧࡤࡸࡪࡹࠠࡢࠢࡏࡳ࡬ࡋ࡮ࡵࡴࡼࠤࡴࡨࡪࡦࡥࡷࠤࡼ࡯ࡴࡩࠢࡤࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࠦࡤࡦࡶࡤ࡭ࡱࡹ࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡓࡪ࡯࡬ࡰࡦࡸ࡬ࡺ࠮ࠣ࡭ࡹࠦࡰࡳࡱࡦࡩࡸࡹࡥࡴࠢࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤࡱࡵࡣࡢࡶࡨࡨࠥ࡯࡮ࠡࡊࡲࡳࡰࡒࡥࡷࡧ࡯࠳ࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠣࡦࡾࠦࡲࡦࡲ࡯ࡥࡨ࡯࡮ࡨࠢࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢࠡࡹ࡬ࡸ࡭ࠦࠢࡉࡱࡲ࡯ࡑ࡫ࡶࡦ࡮࠲ࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࡈࡰࡱ࡮ࡉࡻ࡫࡮ࡵࠤ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡗ࡬ࡪࠦࡣࡳࡧࡤࡸࡪࡪࠠࡍࡱࡪࡉࡳࡺࡲࡺࠢࡲࡦ࡯࡫ࡣࡵࡵࠣࡥࡷ࡫ࠠࡢࡦࡧࡩࡩࠦࡴࡰࠢࡷ࡬ࡪࠦࡨࡰࡱ࡮ࠫࡸࠦࠢ࡭ࡱࡪࡷࠧࠦ࡬ࡪࡵࡷ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࡁࡳࡩࡶ࠾ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࡬ࡴࡵ࡫࠻ࠢࡗ࡬ࡪࠦࡥࡷࡧࡱࡸࠥࡪࡩࡤࡶ࡬ࡳࡳࡧࡲࡺࠢࡦࡳࡳࡺࡡࡪࡰ࡬ࡲ࡬ࠦࡥࡹ࡫ࡶࡸ࡮ࡴࡧࠡ࡮ࡲ࡫ࡸࠦࡡ࡯ࡦࠣ࡬ࡴࡵ࡫ࠡ࡫ࡱࡪࡴࡸ࡭ࡢࡶ࡬ࡳࡳ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡮࡯ࡰ࡭ࡢࡰࡪࡼࡥ࡭ࡡࡩ࡭ࡱ࡫ࡳ࠻ࠢࡏ࡭ࡸࡺࠠࡰࡨࠣࡔࡦࡺࡨࠡࡱࡥ࡮ࡪࡩࡴࡴࠢࡩࡶࡴࡳࠠࡵࡪࡨࠤ࡙࡫ࡳࡵࡎࡨࡺࡪࡲࠠ࡮ࡱࡱ࡭ࡹࡵࡲࡪࡰࡪ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࡦࡺ࡯࡬ࡥࡡ࡯ࡩࡻ࡫࡬ࡠࡨ࡬ࡰࡪࡹ࠺ࠡࡎ࡬ࡷࡹࠦ࡯ࡧࠢࡓࡥࡹ࡮ࠠࡰࡤ࡭ࡩࡨࡺࡳࠡࡨࡵࡳࡲࠦࡴࡩࡧࠣࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠠ࡮ࡱࡱ࡭ࡹࡵࡲࡪࡰࡪ࠲ࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤᓄ")
        global _1l1ll11llll_opy_
        platform_index = os.environ[bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡑࡇࡔࡇࡑࡕࡑࡤࡏࡎࡅࡇ࡛ࠫᓅ")]
        bstack1l1l1l1111l_opy_ = os.path.join(bstack1l1ll1lllll_opy_, (bstack1l1ll1l111l_opy_ + str(platform_index)), bstack1l111l111l1_opy_)
        if not os.path.exists(bstack1l1l1l1111l_opy_) or not os.path.isdir(bstack1l1l1l1111l_opy_):
            return
        logs = hook.get(bstack1111l1_opy_ (u"ࠧࡲ࡯ࡨࡵࠥᓆ"), [])
        with os.scandir(bstack1l1l1l1111l_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1ll11llll_opy_:
                    self.logger.info(bstack1111l1_opy_ (u"ࠨࡐࡢࡶ࡫ࠤࡦࡲࡲࡦࡣࡧࡽࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡤࠡࡽࢀࠦᓇ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack1111l1_opy_ (u"ࠢࠣᓈ")
                    log_entry = bstack1ll1l1l1lll_opy_(
                        kind=bstack1111l1_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡁࡕࡖࡄࡇࡍࡓࡅࡏࡖࠥᓉ"),
                        message=bstack1111l1_opy_ (u"ࠤࠥᓊ"),
                        level=bstack1111l1_opy_ (u"ࠥࠦᓋ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1l1ll1ll1_opy_=entry.stat().st_size,
                        bstack1l1ll111l11_opy_=bstack1111l1_opy_ (u"ࠦࡒࡇࡎࡖࡃࡏࡣ࡚ࡖࡌࡐࡃࡇࠦᓌ"),
                        bstack1l1lll_opy_=os.path.abspath(entry.path),
                        bstack11lllll1l1l_opy_=hook.get(TestFramework.bstack1l1111lll11_opy_)
                    )
                    logs.append(log_entry)
                    _1l1ll11llll_opy_.add(abs_path)
        platform_index = os.environ[bstack1111l1_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡕࡒࡁࡕࡈࡒࡖࡒࡥࡉࡏࡆࡈ࡜ࠬᓍ")]
        bstack1l11111lll1_opy_ = os.path.join(bstack1l1ll1lllll_opy_, (bstack1l1ll1l111l_opy_ + str(platform_index)), bstack1l111l111l1_opy_, bstack1l11111l1l1_opy_)
        if not os.path.exists(bstack1l11111lll1_opy_) or not os.path.isdir(bstack1l11111lll1_opy_):
            self.logger.info(bstack1111l1_opy_ (u"ࠨࡎࡰࠢࡅࡹ࡮ࡲࡤࡍࡧࡹࡩࡱࡎ࡯ࡰ࡭ࡈࡺࡪࡴࡴࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢࡩࡳࡺࡴࡤࠡࡣࡷ࠾ࠥࢁࡽࠣᓎ").format(bstack1l11111lll1_opy_))
        else:
            self.logger.info(bstack1111l1_opy_ (u"ࠢࡑࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࡉࡱࡲ࡯ࡊࡼࡥ࡯ࡶࠣࡥࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠡࡨࡵࡳࡲࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺ࠼ࠣࡿࢂࠨᓏ").format(bstack1l11111lll1_opy_))
            with os.scandir(bstack1l11111lll1_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1ll11llll_opy_:
                        self.logger.info(bstack1111l1_opy_ (u"ࠣࡒࡤࡸ࡭ࠦࡡ࡭ࡴࡨࡥࡩࡿࠠࡱࡴࡲࡧࡪࡹࡳࡦࡦࠣࡿࢂࠨᓐ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack1111l1_opy_ (u"ࠤࠥᓑ")
                        log_entry = bstack1ll1l1l1lll_opy_(
                            kind=bstack1111l1_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᓒ"),
                            message=bstack1111l1_opy_ (u"ࠦࠧᓓ"),
                            level=bstack1111l1_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤᓔ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1l1ll1ll1_opy_=entry.stat().st_size,
                            bstack1l1ll111l11_opy_=bstack1111l1_opy_ (u"ࠨࡍࡂࡐࡘࡅࡑࡥࡕࡑࡎࡒࡅࡉࠨᓕ"),
                            bstack1l1lll_opy_=os.path.abspath(entry.path),
                            bstack1l1l1lll111_opy_=hook.get(TestFramework.bstack1l1111lll11_opy_)
                        )
                        logs.append(log_entry)
                        _1l1ll11llll_opy_.add(abs_path)
        hook[bstack1111l1_opy_ (u"ࠢ࡭ࡱࡪࡷࠧᓖ")] = logs
    def bstack1l1l1l111l1_opy_(
        self,
        bstack1l1ll1111ll_opy_: bstack1ll1llll1l1_opy_,
        entries: List[bstack1ll1l1l1lll_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack1111l1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡎࡌࡣࡇࡏࡎࡠࡕࡈࡗࡘࡏࡏࡏࡡࡌࡈࠧᓗ"))
        req.platform_index = TestFramework.bstack1lllll111l1_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1ll11l11ll1_opy_)
        req.execution_context.hash = str(bstack1l1ll1111ll_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1ll1111ll_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1ll1111ll_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1lllll111l1_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1ll1111llll_opy_)
            log_entry.test_framework_version = TestFramework.bstack1lllll111l1_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1l1l11llll1_opy_)
            log_entry.uuid = entry.bstack11lllll1l1l_opy_ if entry.bstack11lllll1l1l_opy_ else TestFramework.bstack1lllll111l1_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1ll11l111l1_opy_)
            log_entry.test_framework_state = bstack1l1ll1111ll_opy_.state.name
            log_entry.message = entry.message.encode(bstack1111l1_opy_ (u"ࠤࡸࡸ࡫࠳࠸ࠣᓘ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            if isinstance(entry.level, str) and len(entry.level.strip()) > 0:
                log_entry.level = entry.level.strip()
            if entry.kind == bstack1111l1_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᓙ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1l1ll1ll1_opy_
                log_entry.file_path = entry.bstack1l1lll_opy_
        def bstack1l1l1ll1l11_opy_():
            bstack1lll11l11_opy_ = datetime.now()
            try:
                self.bstack1lll1l1lll1_opy_.LogCreatedEvent(req)
                bstack1l1ll1111ll_opy_.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠦ࡬ࡸࡰࡤ࠼ࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠣᓚ"), datetime.now() - bstack1lll11l11_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1111l1_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࡶࡩࡳࡪ࡟࡭ࡱࡪࡣࡨࡸࡥࡢࡶࡨࡨࡤ࡫ࡶࡦࡰࡷࡣࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠡࡽࢀࠦᓛ").format(str(e)))
                traceback.print_exc()
        self.bstack1lllllll1l1_opy_.enqueue(bstack1l1l1ll1l11_opy_)
    def __1l111l11111_opy_(self, instance) -> None:
        bstack1111l1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࠠࠡࠢࠣࡐࡴࡧࡤࡴࠢࡦࡹࡸࡺ࡯࡮ࠢࡷࡥ࡬ࡹࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡩ࡬ࡺࡪࡴࠠࡵࡧࡶࡸࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠡ࡫ࡱࡷࡹࡧ࡮ࡤࡧ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࡉࡲࡦࡣࡷࡩࡸࠦࡡࠡࡦ࡬ࡧࡹࠦࡣࡰࡰࡷࡥ࡮ࡴࡩ࡯ࡩࠣࡸࡪࡹࡴࠡ࡮ࡨࡺࡪࡲࠠࡤࡷࡶࡸࡴࡳࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡵࡩࡹࡸࡩࡦࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡈࡻࡳࡵࡱࡰࡘࡦ࡭ࡍࡢࡰࡤ࡫ࡪࡸࠠࡢࡰࡧࠤࡺࡶࡤࡢࡶࡨࡷࠥࡺࡨࡦࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠤࡸࡺࡡࡵࡧࠣࡹࡸ࡯࡮ࡨࠢࡶࡩࡹࡥࡳࡵࡣࡷࡩࡤ࡫࡮ࡵࡴ࡬ࡩࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᓜ")
        bstack1l111ll11ll_opy_ = {bstack1111l1_opy_ (u"ࠢࡤࡷࡶࡸࡴࡳ࡟࡮ࡧࡷࡥࡩࡧࡴࡢࠤᓝ"): bstack1lll1lll1ll_opy_.bstack1l111ll1l1l_opy_()}
        TestFramework.bstack11llll1l111_opy_(instance, bstack1l111ll11ll_opy_)
    @staticmethod
    def __1l111l1l111_opy_(instance, args):
        request, bstack1l111ll111l_opy_ = args
        bstack11lllll111l_opy_ = id(bstack1l111ll111l_opy_)
        bstack1l111111lll_opy_ = instance.data[TestFramework.bstack1l111111ll1_opy_]
        step = next(filter(lambda st: st[bstack1111l1_opy_ (u"ࠨ࡫ࡧࠫᓞ")] == bstack11lllll111l_opy_, bstack1l111111lll_opy_[bstack1111l1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᓟ")]), None)
        step.update({
            bstack1111l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧᓠ"): datetime.now(tz=timezone.utc)
        })
        index = next((i for i, st in enumerate(bstack1l111111lll_opy_[bstack1111l1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᓡ")]) if st[bstack1111l1_opy_ (u"ࠬ࡯ࡤࠨᓢ")] == step[bstack1111l1_opy_ (u"࠭ࡩࡥࠩᓣ")]), None)
        if index is not None:
            bstack1l111111lll_opy_[bstack1111l1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᓤ")][index] = step
        instance.data[TestFramework.bstack1l111111ll1_opy_] = bstack1l111111lll_opy_
    @staticmethod
    def __1l111l1lll1_opy_(instance, args):
        bstack1111l1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࠢࠣࠤࠥࡽࡨࡦࡰࠣࡰࡪࡴࠠࡢࡴࡪࡷࠥ࡯ࡳࠡ࠴࠯ࠤ࡮ࡺࠠࡴ࡫ࡪࡲ࡮࡬ࡩࡦࡵࠣࡸ࡭࡫ࡲࡦࠢ࡬ࡷࠥࡴ࡯ࠡࡧࡻࡧࡪࡶࡴࡪࡱࡱࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡤࡶ࡬ࡹࠠࡢࡴࡨࠤ࠲࡛ࠦࡳࡧࡴࡹࡪࡹࡴ࠭ࠢࡶࡸࡪࡶ࡝ࠋࠢࠣࠤࠥࠦࠠࠡࠢ࡬ࡪࠥࡧࡲࡨࡵࠣࡥࡷ࡫ࠠ࠴ࠢࡷ࡬ࡪࡴࠠࡵࡪࡨࠤࡱࡧࡳࡵࠢࡹࡥࡱࡻࡥࠡ࡫ࡶࠤࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᓥ")
        bstack1l1111ll1l1_opy_ = datetime.now(tz=timezone.utc)
        request = args[0]
        bstack1l111ll111l_opy_ = args[1]
        bstack11lllll111l_opy_ = id(bstack1l111ll111l_opy_)
        bstack1l111111lll_opy_ = instance.data[TestFramework.bstack1l111111ll1_opy_]
        step = None
        if bstack11lllll111l_opy_ is not None and bstack1l111111lll_opy_.get(bstack1111l1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨᓦ")):
            step = next(filter(lambda st: st[bstack1111l1_opy_ (u"ࠪ࡭ࡩ࠭ᓧ")] == bstack11lllll111l_opy_, bstack1l111111lll_opy_[bstack1111l1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᓨ")]), None)
            step.update({
                bstack1111l1_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪᓩ"): bstack1l1111ll1l1_opy_,
            })
        if len(args) > 2:
            exception = args[2]
            step.update({
                bstack1111l1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭ᓪ"): bstack1111l1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᓫ"),
                bstack1111l1_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࠩᓬ"): str(exception)
            })
        else:
            if step is not None:
                step.update({
                    bstack1111l1_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩᓭ"): bstack1111l1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᓮ"),
                })
        index = next((i for i, st in enumerate(bstack1l111111lll_opy_[bstack1111l1_opy_ (u"ࠫࡸࡺࡥࡱࡵࠪᓯ")]) if st[bstack1111l1_opy_ (u"ࠬ࡯ࡤࠨᓰ")] == step[bstack1111l1_opy_ (u"࠭ࡩࡥࠩᓱ")]), None)
        if index is not None:
            bstack1l111111lll_opy_[bstack1111l1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ᓲ")][index] = step
        instance.data[TestFramework.bstack1l111111ll1_opy_] = bstack1l111111lll_opy_
    @staticmethod
    def __11llll11ll1_opy_(node):
        try:
            examples = []
            if hasattr(node, bstack1111l1_opy_ (u"ࠨࡥࡤࡰࡱࡹࡰࡦࡥࠪᓳ")):
                examples = list(node.callspec.params[bstack1111l1_opy_ (u"ࠩࡢࡴࡾࡺࡥࡴࡶࡢࡦࡩࡪ࡟ࡦࡺࡤࡱࡵࡲࡥࠨᓴ")].values())
            return examples
        except:
            return []
    def bstack1l1l1ll11ll_opy_(self, instance: bstack1ll1llll1l1_opy_, bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_]):
        bstack11lllll1l11_opy_ = (
            PytestBDDFramework.bstack1l1111l1111_opy_
            if bstack1llll1ll1l1_opy_[1] == bstack1lll11l11ll_opy_.PRE
            else PytestBDDFramework.bstack1l111l1ll11_opy_
        )
        hook = PytestBDDFramework.bstack1l111l1l1l1_opy_(instance, bstack11lllll1l11_opy_)
        entries = hook.get(TestFramework.bstack1l11111llll_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l111l111ll_opy_, []))
        return entries
    def bstack1l1ll111lll_opy_(self, instance: bstack1ll1llll1l1_opy_, bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_]):
        bstack11lllll1l11_opy_ = (
            PytestBDDFramework.bstack1l1111l1111_opy_
            if bstack1llll1ll1l1_opy_[1] == bstack1lll11l11ll_opy_.PRE
            else PytestBDDFramework.bstack1l111l1ll11_opy_
        )
        PytestBDDFramework.bstack1l111ll1l11_opy_(instance, bstack11lllll1l11_opy_)
        TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l111l111ll_opy_, []).clear()
    @staticmethod
    def bstack1l111l1l1l1_opy_(instance: bstack1ll1llll1l1_opy_, bstack11lllll1l11_opy_: str):
        bstack1l111l1l1ll_opy_ = (
            PytestBDDFramework.bstack1l1111l1l11_opy_
            if bstack11lllll1l11_opy_ == PytestBDDFramework.bstack1l111l1ll11_opy_
            else PytestBDDFramework.bstack1l1111lllll_opy_
        )
        bstack11llllllll1_opy_ = TestFramework.bstack1lllll111l1_opy_(instance, bstack11lllll1l11_opy_, None)
        bstack1l111l11l1l_opy_ = TestFramework.bstack1lllll111l1_opy_(instance, bstack1l111l1l1ll_opy_, None) if bstack11llllllll1_opy_ else None
        return (
            bstack1l111l11l1l_opy_[bstack11llllllll1_opy_][-1]
            if isinstance(bstack1l111l11l1l_opy_, dict) and len(bstack1l111l11l1l_opy_.get(bstack11llllllll1_opy_, [])) > 0
            else None
        )
    @staticmethod
    def bstack1l111ll1l11_opy_(instance: bstack1ll1llll1l1_opy_, bstack11lllll1l11_opy_: str):
        hook = PytestBDDFramework.bstack1l111l1l1l1_opy_(instance, bstack11lllll1l11_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack1l11111llll_opy_, []).clear()
    @staticmethod
    def __1l111ll1ll1_opy_(instance: bstack1ll1llll1l1_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack1111l1_opy_ (u"ࠥ࡫ࡪࡺ࡟ࡳࡧࡦࡳࡷࡪࡳࠣᓵ"), None)):
            return
        if os.getenv(bstack1111l1_opy_ (u"ࠦࡘࡊࡋࡠࡅࡏࡍࡤࡌࡌࡂࡉࡢࡐࡔࡍࡓࠣᓶ"), bstack1111l1_opy_ (u"ࠧ࠷ࠢᓷ")) != bstack1111l1_opy_ (u"ࠨ࠱ࠣᓸ"):
            PytestBDDFramework.logger.warning(bstack1111l1_opy_ (u"ࠢࡪࡩࡱࡳࡷ࡯࡮ࡨࠢࡦࡥࡵࡲ࡯ࡨࠤᓹ"))
            return
        bstack11lllll11ll_opy_ = {
            bstack1111l1_opy_ (u"ࠣࡵࡨࡸࡺࡶࠢᓺ"): (PytestBDDFramework.bstack1l1111l1111_opy_, PytestBDDFramework.bstack1l1111lllll_opy_),
            bstack1111l1_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࠦᓻ"): (PytestBDDFramework.bstack1l111l1ll11_opy_, PytestBDDFramework.bstack1l1111l1l11_opy_),
        }
        for when in (bstack1111l1_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤᓼ"), bstack1111l1_opy_ (u"ࠦࡨࡧ࡬࡭ࠤᓽ"), bstack1111l1_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴࠢᓾ")):
            bstack11llll1lll1_opy_ = args[1].get_records(when)
            if not bstack11llll1lll1_opy_:
                continue
            records = [
                bstack1ll1l1l1lll_opy_(
                    kind=TestFramework.bstack1l1l1ll111l_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack1111l1_opy_ (u"ࠨ࡬ࡦࡸࡨࡰࡳࡧ࡭ࡦࠤᓿ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack1111l1_opy_ (u"ࠢࡤࡴࡨࡥࡹ࡫ࡤࠣᔀ")) and r.created
                        else None
                    ),
                )
                for r in bstack11llll1lll1_opy_
                if isinstance(getattr(r, bstack1111l1_opy_ (u"ࠣ࡯ࡨࡷࡸࡧࡧࡦࠤᔁ"), None), str) and r.message.strip()
            ]
            if not records:
                continue
            bstack11llllll11l_opy_, bstack1l111l1l1ll_opy_ = bstack11lllll11ll_opy_.get(when, (None, None))
            bstack1l11111l1ll_opy_ = TestFramework.bstack1lllll111l1_opy_(instance, bstack11llllll11l_opy_, None) if bstack11llllll11l_opy_ else None
            bstack1l111l11l1l_opy_ = TestFramework.bstack1lllll111l1_opy_(instance, bstack1l111l1l1ll_opy_, None) if bstack1l11111l1ll_opy_ else None
            if isinstance(bstack1l111l11l1l_opy_, dict) and len(bstack1l111l11l1l_opy_.get(bstack1l11111l1ll_opy_, [])) > 0:
                hook = bstack1l111l11l1l_opy_[bstack1l11111l1ll_opy_][-1]
                if isinstance(hook, dict) and TestFramework.bstack1l11111llll_opy_ in hook:
                    hook[TestFramework.bstack1l11111llll_opy_].extend(records)
                    continue
            logs = TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l111l111ll_opy_, [])
            logs.extend(records)
    @staticmethod
    def __11llllll1l1_opy_(args) -> Dict[str, Any]:
        request, feature, scenario = args
        bstack1l1l1l1lll_opy_ = request.node.nodeid
        test_name = PytestBDDFramework.__1l1111l11ll_opy_(request.node, scenario)
        bstack1l111l1111l_opy_ = feature.filename
        if not bstack1l1l1l1lll_opy_ or not test_name or not bstack1l111l1111l_opy_:
            return None
        code = None
        return {
            TestFramework.bstack1ll11l111l1_opy_: uuid4().__str__(),
            TestFramework.bstack1l11111l111_opy_: bstack1l1l1l1lll_opy_,
            TestFramework.bstack1ll1111l111_opy_: test_name,
            TestFramework.bstack1l1l11ll11l_opy_: bstack1l1l1l1lll_opy_,
            TestFramework.bstack1l11111l11l_opy_: bstack1l111l1111l_opy_,
            TestFramework.bstack11llll11lll_opy_: PytestBDDFramework.__1l1111lll1l_opy_(feature, scenario),
            TestFramework.bstack11llll1ll1l_opy_: code,
            TestFramework.bstack1l11lll1l1l_opy_: TestFramework.bstack1l11111ll11_opy_,
            TestFramework.bstack1l11l11l1ll_opy_: test_name
        }
    @staticmethod
    def __1l1111l11ll_opy_(node, scenario):
        if hasattr(node, bstack1111l1_opy_ (u"ࠩࡦࡥࡱࡲࡳࡱࡧࡦࠫᔂ")):
            parts = node.nodeid.rsplit(bstack1111l1_opy_ (u"ࠥ࡟ࠧᔃ"))
            params = parts[-1]
            return bstack1111l1_opy_ (u"ࠦࢀࢃࠠ࡜ࡽࢀࠦᔄ").format(scenario.name, params)
        return scenario.name
    @staticmethod
    def __1l1111lll1l_opy_(feature, scenario) -> List[str]:
        return (list(feature.tags) if hasattr(feature, bstack1111l1_opy_ (u"ࠬࡺࡡࡨࡵࠪᔅ")) else []) + (list(scenario.tags) if hasattr(scenario, bstack1111l1_opy_ (u"࠭ࡴࡢࡩࡶࠫᔆ")) else [])
    @staticmethod
    def __11lllll1lll_opy_(location):
        return bstack1111l1_opy_ (u"ࠢ࠻࠼ࠥᔇ").join(filter(lambda x: isinstance(x, str), location))