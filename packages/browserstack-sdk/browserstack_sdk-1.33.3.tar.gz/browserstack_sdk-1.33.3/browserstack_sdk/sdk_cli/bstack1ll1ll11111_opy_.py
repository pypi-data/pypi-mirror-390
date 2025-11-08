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
from browserstack_sdk.sdk_cli.test_framework import (
    TestFramework,
    bstack1ll1ll1lll1_opy_,
    bstack1ll1llll1l1_opy_,
    bstack1lll11l11ll_opy_,
    bstack11llll1l1ll_opy_,
    bstack1ll1l1l1lll_opy_,
)
from pathlib import Path
import grpc
from browserstack_sdk import sdk_pb2 as structs
from datetime import datetime, timezone
from typing import List, Dict, Any
import traceback
from bstack_utils.helper import bstack1l1ll1111l1_opy_
from bstack_utils.bstack1llll1llll_opy_ import bstack1llll11l111_opy_
from bstack_utils.constants import EVENTS
from browserstack_sdk.sdk_cli.bstack1lllllll1l1_opy_ import bstack1lllllll1ll_opy_
from browserstack_sdk.sdk_cli.utils.bstack1lll1ll111l_opy_ import bstack1lll1lll1ll_opy_
from bstack_utils.bstack111ll1lll1_opy_ import bstack1ll1111ll1_opy_
bstack1l1ll1lllll_opy_ = bstack1l1ll1111l1_opy_()
bstack11lllllll11_opy_ = 1.0
bstack1l1ll1l111l_opy_ = bstack1111l1_opy_ (u"ࠣࡗࡳࡰࡴࡧࡤࡦࡦࡄࡸࡹࡧࡣࡩ࡯ࡨࡲࡹࡹ࠭ࠣᔈ")
bstack11llll111ll_opy_ = bstack1111l1_opy_ (u"ࠤࡗࡩࡸࡺࡌࡦࡸࡨࡰࠧᔉ")
bstack11llll11l11_opy_ = bstack1111l1_opy_ (u"ࠥࡆࡺ࡯࡬ࡥࡎࡨࡺࡪࡲࠢᔊ")
bstack11llll11l1l_opy_ = bstack1111l1_opy_ (u"ࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢᔋ")
bstack11llll1111l_opy_ = bstack1111l1_opy_ (u"ࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦᔌ")
_1l1ll11llll_opy_ = set()
class bstack1lll111ll11_opy_(TestFramework):
    bstack1l1111111ll_opy_ = bstack1111l1_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫࡯ࡸࡵࡷࡵࡩࡸࠨᔍ")
    bstack1l1111lllll_opy_ = bstack1111l1_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡶࡣࡸࡺࡡࡳࡶࡨࡨࠧᔎ")
    bstack1l1111l1l11_opy_ = bstack1111l1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡷࡤ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪࠢᔏ")
    bstack1l1111l1111_opy_ = bstack1111l1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡲࡡࡴࡶࡢࡷࡹࡧࡲࡵࡧࡧࠦᔐ")
    bstack1l111l1ll11_opy_ = bstack1111l1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥ࡬ࡢࡵࡷࡣ࡫࡯࡮ࡪࡵ࡫ࡩࡩࠨᔑ")
    bstack1l1111ll1ll_opy_: bool
    bstack1lllllll1l1_opy_: bstack1lllllll1ll_opy_  = None
    bstack1lll1l1lll1_opy_ = None
    bstack1l1111ll111_opy_ = [
        bstack1ll1ll1lll1_opy_.BEFORE_ALL,
        bstack1ll1ll1lll1_opy_.AFTER_ALL,
        bstack1ll1ll1lll1_opy_.BEFORE_EACH,
        bstack1ll1ll1lll1_opy_.AFTER_EACH,
    ]
    def __init__(
        self,
        bstack11lllll1ll1_opy_: Dict[str, str],
        bstack1ll11lll11l_opy_: List[str]=[bstack1111l1_opy_ (u"ࠦࡵࡿࡴࡦࡵࡷࠦᔒ")],
        bstack1lllllll1l1_opy_: bstack1lllllll1ll_opy_=None,
        bstack1lll1l1lll1_opy_=None
    ):
        super().__init__(bstack1ll11lll11l_opy_, bstack11lllll1ll1_opy_, bstack1lllllll1l1_opy_)
        self.bstack1l1111ll1ll_opy_ = any(bstack1111l1_opy_ (u"ࠧࡶࡹࡵࡧࡶࡸࠧᔓ") in item.lower() for item in bstack1ll11lll11l_opy_)
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
        if test_framework_state == bstack1ll1ll1lll1_opy_.TEST or test_framework_state in bstack1lll111ll11_opy_.bstack1l1111ll111_opy_:
            bstack1l111111111_opy_(test_framework_state, test_hook_state)
        if test_framework_state == bstack1ll1ll1lll1_opy_.NONE:
            self.logger.warning(bstack1111l1_opy_ (u"ࠨࡩࡨࡰࡲࡶࡪࡪࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡷࡹࡧࡴࡦ࠿ࡾࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࢀࠤࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱ࡟ࡴࡶࡤࡸࡪࡃࠢᔔ") + str(test_hook_state) + bstack1111l1_opy_ (u"ࠢࠣᔕ"))
            return
        if not self.bstack1l1111ll1ll_opy_:
            self.logger.warning(bstack1111l1_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡶࡰࡶࡹࡵࡶ࡯ࡳࡶࡨࡨࠥ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠾ࠤᔖ") + str(str(self.bstack1ll11lll11l_opy_)) + bstack1111l1_opy_ (u"ࠤࠥᔗ"))
            return
        if not isinstance(args, tuple) or len(args) == 0:
            self.logger.warning(bstack1111l1_opy_ (u"ࠥࡸࡷࡧࡣ࡬ࡡࡨࡺࡪࡴࡴ࠻ࠢࡸࡲࡪࡾࡰࡦࡥࡷࡩࡩࠦࡡࡳࡩࡶࡁࢀࡧࡲࡨࡵࢀࠤࡰࡽࡡࡳࡩࡶࡁࠧᔘ") + str(kwargs) + bstack1111l1_opy_ (u"ࠦࠧᔙ"))
            return
        instance = self.__1l11111ll1l_opy_(context, test_framework_state, test_hook_state, *args, **kwargs)
        if not instance:
            self.logger.debug(bstack1111l1_opy_ (u"ࠧࡺࡲࡢࡥ࡮ࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥࡧࡲࡨࡵࡀࠦᔚ") + str(args) + bstack1111l1_opy_ (u"ࠨࠢᔛ"))
            return
        try:
            if instance!= None and test_framework_state in bstack1lll111ll11_opy_.bstack1l1111ll111_opy_ and test_hook_state == bstack1lll11l11ll_opy_.PRE:
                bstack1ll11l111ll_opy_ = bstack1llll11l111_opy_.bstack1ll11ll11l1_opy_(EVENTS.bstack1ll1l1111_opy_.value)
                name = str(EVENTS.bstack1ll1l1111_opy_.name)+bstack1111l1_opy_ (u"ࠢ࠻ࠤᔜ")+str(test_framework_state.name)
                TestFramework.bstack1l111l11ll1_opy_(instance, name, bstack1ll11l111ll_opy_)
        except Exception as e:
            self.logger.debug(bstack1111l1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡩࡱࡲ࡯ࠥ࡫ࡲࡳࡱࡵࠤࡵࡸࡥ࠻ࠢࡾࢁࠧᔝ").format(e))
        try:
            if not TestFramework.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1l11111l111_opy_) and test_hook_state == bstack1lll11l11ll_opy_.PRE:
                test = bstack1lll111ll11_opy_.__11llllll1l1_opy_(args[0])
                if test:
                    instance.data.update(test)
                    self.logger.debug(bstack1111l1_opy_ (u"ࠤ࡯ࡳࡦࡪࡥࡥࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᔞ") + str(test_hook_state) + bstack1111l1_opy_ (u"ࠥࠦᔟ"))
            if test_framework_state == bstack1ll1ll1lll1_opy_.TEST:
                if test_hook_state == bstack1lll11l11ll_opy_.PRE and not TestFramework.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1l1ll1lll11_opy_):
                    TestFramework.bstack1lllll1l1l1_opy_(instance, TestFramework.bstack1l1ll1lll11_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack1111l1_opy_ (u"ࠦࡸ࡫ࡴࠡࡶࡨࡷࡹ࠳ࡳࡵࡣࡵࡸࠥ࡬࡯ࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᔠ") + str(test_hook_state) + bstack1111l1_opy_ (u"ࠧࠨᔡ"))
                elif test_hook_state == bstack1lll11l11ll_opy_.POST and not TestFramework.bstack1llll1l1ll1_opy_(instance, TestFramework.bstack1l1l1lll1l1_opy_):
                    TestFramework.bstack1lllll1l1l1_opy_(instance, TestFramework.bstack1l1l1lll1l1_opy_, datetime.now(tz=timezone.utc))
                    self.logger.debug(bstack1111l1_opy_ (u"ࠨࡳࡦࡶࠣࡸࡪࡹࡴ࠮ࡧࡱࡨࠥ࡬࡯ࡳࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࡳࡧࡩࠬ࠮ࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᔢ") + str(test_hook_state) + bstack1111l1_opy_ (u"ࠢࠣᔣ"))
            elif test_framework_state == bstack1ll1ll1lll1_opy_.LOG and test_hook_state == bstack1lll11l11ll_opy_.POST:
                bstack1lll111ll11_opy_.__1l111ll1ll1_opy_(instance, *args)
            elif test_framework_state == bstack1ll1ll1lll1_opy_.LOG_REPORT and test_hook_state == bstack1lll11l11ll_opy_.POST:
                self.__11llllll111_opy_(instance, *args)
                self.__1l111l11111_opy_(instance)
            elif test_framework_state in bstack1lll111ll11_opy_.bstack1l1111ll111_opy_:
                self.__1l1111111l1_opy_(instance, test_framework_state, test_hook_state, *args)
            self.logger.debug(bstack1111l1_opy_ (u"ࠣࡶࡵࡥࡨࡱ࡟ࡦࡸࡨࡲࡹࡀࠠࡩࡣࡱࡨࡱ࡫ࡤࠡࡧࡹࡩࡳࡺ࠽ࡼࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡶࡸࡦࡺࡥࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࠤᔤ") + str(instance.ref()) + bstack1111l1_opy_ (u"ࠤࠥᔥ"))
        except Exception as e:
            self.logger.error(e)
            traceback.print_exc()
        self.bstack11llllll1ll_opy_(instance, (test_framework_state, test_hook_state), *args, **kwargs)
        try:
            if instance!= None and test_framework_state in bstack1lll111ll11_opy_.bstack1l1111ll111_opy_ and test_hook_state == bstack1lll11l11ll_opy_.POST:
                name = str(EVENTS.bstack1ll1l1111_opy_.name)+bstack1111l1_opy_ (u"ࠥ࠾ࠧᔦ")+str(test_framework_state.name)
                bstack1ll11l111ll_opy_ = TestFramework.bstack1l1111l11l1_opy_(instance, name)
                bstack1llll11l111_opy_.end(EVENTS.bstack1ll1l1111_opy_.value, bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠦ࠿ࡹࡴࡢࡴࡷࠦᔧ"), bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠧࡀࡥ࡯ࡦࠥᔨ"), True, None, test_framework_state.name)
        except Exception as e:
            self.logger.debug(bstack1111l1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡮࡯ࡰ࡭ࠣࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨᔩ").format(e))
    def bstack1l1ll1l1111_opy_(self):
        return self.bstack1l1111ll1ll_opy_
    def __1l111111l1l_opy_(self, *args):
        if len(args) > 2 and callable(getattr(args[2], bstack1111l1_opy_ (u"ࠢࡨࡧࡷࡣࡷ࡫ࡳࡶ࡮ࡷࠦᔪ"), None)):
            rep = args[2].get_result()
            if rep:
                return TestFramework.bstack1l1l1l1l1ll_opy_(rep, [bstack1111l1_opy_ (u"ࠣࡹ࡫ࡩࡳࠨᔫ"), bstack1111l1_opy_ (u"ࠤࡲࡹࡹࡩ࡯࡮ࡧࠥᔬ"), bstack1111l1_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥᔭ"), bstack1111l1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦᔮ"), bstack1111l1_opy_ (u"ࠧࡹ࡫ࡪࡲࡳࡩࡩࠨᔯ"), bstack1111l1_opy_ (u"ࠨ࡬ࡰࡰࡪࡶࡪࡶࡲࡵࡧࡻࡸࠧᔰ")])
        return None
    def __11llllll111_opy_(self, instance: bstack1ll1llll1l1_opy_, *args):
        result = self.__1l111111l1l_opy_(*args)
        if not result:
            return
        failure = None
        bstack11111111l1_opy_ = None
        if result.get(bstack1111l1_opy_ (u"ࠢࡰࡷࡷࡧࡴࡳࡥࠣᔱ"), None) == bstack1111l1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣᔲ") and len(args) > 1 and getattr(args[1], bstack1111l1_opy_ (u"ࠤࡨࡼࡨ࡯࡮ࡧࡱࠥᔳ"), None) is not None:
            failure = [{bstack1111l1_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭ᔴ"): [args[1].excinfo.exconly(), result.get(bstack1111l1_opy_ (u"ࠦࡱࡵ࡮ࡨࡴࡨࡴࡷࡺࡥࡹࡶࠥᔵ"), None)]}]
            bstack11111111l1_opy_ = bstack1111l1_opy_ (u"ࠧࡇࡳࡴࡧࡵࡸ࡮ࡵ࡮ࡆࡴࡵࡳࡷࠨᔶ") if bstack1111l1_opy_ (u"ࠨࡁࡴࡵࡨࡶࡹ࡯࡯࡯ࠤᔷ") in getattr(args[1].excinfo, bstack1111l1_opy_ (u"ࠢࡵࡻࡳࡩࡳࡧ࡭ࡦࠤᔸ"), bstack1111l1_opy_ (u"ࠣࠤᔹ")) else bstack1111l1_opy_ (u"ࠤࡘࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࡊࡸࡲࡰࡴࠥᔺ")
        bstack11llll1llll_opy_ = result.get(bstack1111l1_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᔻ"), TestFramework.bstack1l11111ll11_opy_)
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
            target = None # bstack1l111ll1111_opy_ bstack11llll1l11l_opy_ this to be bstack1111l1_opy_ (u"ࠦࡳࡵࡤࡦ࡫ࡧࠦᔼ")
            if test_framework_state == bstack1ll1ll1lll1_opy_.INIT_TEST:
                target = args[0] if isinstance(args[0], str) else None
                if target:
                    self.__1l1111l1ll1_opy_(context, test_framework_state, target, *args)
            elif test_framework_state == bstack1ll1ll1lll1_opy_.LOG:
                nodeid = getattr(getattr(args[0], bstack1111l1_opy_ (u"ࠧࡴ࡯ࡥࡧࠥᔽ"), None), bstack1111l1_opy_ (u"ࠨ࡮ࡰࡦࡨ࡭ࡩࠨᔾ"), None) if args else None
                if isinstance(nodeid, str):
                    target = nodeid
            elif getattr(args[0], bstack1111l1_opy_ (u"ࠢ࡯ࡱࡧࡩ࡮ࡪࠢᔿ"), None):
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
        bstack11llll1ll11_opy_ = TestFramework.bstack1lllll111l1_opy_(instance, bstack1lll111ll11_opy_.bstack1l1111lllll_opy_, {})
        if not key in bstack11llll1ll11_opy_:
            bstack11llll1ll11_opy_[key] = []
        bstack11lllllll1l_opy_ = TestFramework.bstack1lllll111l1_opy_(instance, bstack1lll111ll11_opy_.bstack1l1111l1l11_opy_, {})
        if not key in bstack11lllllll1l_opy_:
            bstack11lllllll1l_opy_[key] = []
        bstack1l111ll11ll_opy_ = {
            bstack1lll111ll11_opy_.bstack1l1111lllll_opy_: bstack11llll1ll11_opy_,
            bstack1lll111ll11_opy_.bstack1l1111l1l11_opy_: bstack11lllllll1l_opy_,
        }
        if test_hook_state == bstack1lll11l11ll_opy_.PRE:
            hook = {
                bstack1111l1_opy_ (u"ࠣ࡭ࡨࡽࠧᕀ"): key,
                TestFramework.bstack1l1111lll11_opy_: uuid4().__str__(),
                TestFramework.bstack1l1111l111l_opy_: TestFramework.bstack1l1111l1l1l_opy_,
                TestFramework.bstack11lllll11l1_opy_: datetime.now(tz=timezone.utc),
                TestFramework.bstack1l11111llll_opy_: [],
                TestFramework.bstack1l11111111l_opy_: args[1] if len(args) > 1 else bstack1111l1_opy_ (u"ࠩࠪᕁ"),
                TestFramework.bstack1l111l1llll_opy_: bstack1lll1lll1ll_opy_.bstack1l111ll1l1l_opy_()
            }
            bstack11llll1ll11_opy_[key].append(hook)
            bstack1l111ll11ll_opy_[bstack1lll111ll11_opy_.bstack1l1111l1111_opy_] = key
        elif test_hook_state == bstack1lll11l11ll_opy_.POST:
            bstack1l111l1ll1l_opy_ = bstack11llll1ll11_opy_.get(key, [])
            hook = bstack1l111l1ll1l_opy_.pop() if bstack1l111l1ll1l_opy_ else None
            if hook:
                result = self.__1l111111l1l_opy_(*args)
                if result:
                    bstack1l111ll11l1_opy_ = result.get(bstack1111l1_opy_ (u"ࠥࡳࡺࡺࡣࡰ࡯ࡨࠦᕂ"), TestFramework.bstack1l1111l1l1l_opy_)
                    if bstack1l111ll11l1_opy_ != TestFramework.bstack1l1111l1l1l_opy_:
                        hook[TestFramework.bstack1l1111l111l_opy_] = bstack1l111ll11l1_opy_
                hook[TestFramework.bstack1l1111llll1_opy_] = datetime.now(tz=timezone.utc)
                hook[TestFramework.bstack1l111l1llll_opy_]= bstack1lll1lll1ll_opy_.bstack1l111ll1l1l_opy_()
                self.bstack1l111l11l11_opy_(hook)
                logs = hook.get(TestFramework.bstack1l111l11lll_opy_, [])
                if logs: self.bstack1l1l1l111l1_opy_(instance, logs)
                bstack11lllllll1l_opy_[key].append(hook)
                bstack1l111ll11ll_opy_[bstack1lll111ll11_opy_.bstack1l111l1ll11_opy_] = key
        TestFramework.bstack11llll1l111_opy_(instance, bstack1l111ll11ll_opy_)
        self.logger.debug(bstack1111l1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢ࡬ࡴࡵ࡫ࡠࡧࡹࡩࡳࡺ࠺ࠡࡶࡨࡷࡹࡥࡨࡰࡱ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࡰ࡫ࡹࡾ࠰ࡾࡸࡪࡹࡴࡠࡪࡲࡳࡰࡥࡳࡵࡣࡷࡩࢂࠦࡨࡰࡱ࡮ࡷࡤࡹࡴࡢࡴࡷࡩࡩࡃࡻࡩࡱࡲ࡯ࡸࡥࡳࡵࡣࡵࡸࡪࡪࡽࠡࡪࡲࡳࡰࡹ࡟ࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥ࠿ࠥᕃ") + str(bstack11lllllll1l_opy_) + bstack1111l1_opy_ (u"ࠧࠨᕄ"))
    def __1l1111ll11l_opy_(
        self,
        context: bstack11llll1l1ll_opy_,
        test_framework_state: bstack1ll1ll1lll1_opy_,
        test_hook_state: bstack1lll11l11ll_opy_,
        *args,
        **kwargs,
    ):
        fixturedef = TestFramework.bstack1l1l1l1l1ll_opy_(args[0], [bstack1111l1_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᕅ"), bstack1111l1_opy_ (u"ࠢࡢࡴࡪࡲࡦࡳࡥࠣᕆ"), bstack1111l1_opy_ (u"ࠣࡲࡤࡶࡦࡳࡳࠣᕇ"), bstack1111l1_opy_ (u"ࠤ࡬ࡨࡸࠨᕈ"), bstack1111l1_opy_ (u"ࠥࡹࡳ࡯ࡴࡵࡧࡶࡸࠧᕉ"), bstack1111l1_opy_ (u"ࠦࡧࡧࡳࡦ࡫ࡧࠦᕊ")]) if len(args) > 0 else {}
        request = args[1] if len(args) > 1 else None
        scope = request.scope if hasattr(request, bstack1111l1_opy_ (u"ࠧࡹࡣࡰࡲࡨࠦᕋ")) else fixturedef.get(bstack1111l1_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᕌ"), None)
        fixturename = request.fixturename if hasattr(request, bstack1111l1_opy_ (u"ࠢࡧ࡫ࡻࡸࡺࡸࡥ࡯ࡣࡰࡩࠧᕍ")) else None
        node = request.node if hasattr(request, bstack1111l1_opy_ (u"ࠣࡰࡲࡨࡪࠨᕎ")) else None
        target = request.node.nodeid if hasattr(node, bstack1111l1_opy_ (u"ࠤࡱࡳࡩ࡫ࡩࡥࠤᕏ")) else None
        baseid = fixturedef.get(bstack1111l1_opy_ (u"ࠥࡦࡦࡹࡥࡪࡦࠥᕐ"), None) or bstack1111l1_opy_ (u"ࠦࠧᕑ")
        if (not target or len(baseid) > 0) and hasattr(request, bstack1111l1_opy_ (u"ࠧࡥࡰࡺࡨࡸࡲࡨ࡯ࡴࡦ࡯ࠥᕒ")):
            target = bstack1lll111ll11_opy_.__11lllll1lll_opy_(request._pyfuncitem.location) if hasattr(request._pyfuncitem, bstack1111l1_opy_ (u"ࠨ࡬ࡰࡥࡤࡸ࡮ࡵ࡮ࠣᕓ")) else None
            if target and not TestFramework.bstack1llll1l1lll_opy_(target):
                self.__1l1111l1ll1_opy_(context, test_framework_state, target, (target, request._pyfuncitem.location))
                node = request._pyfuncitem
                self.logger.debug(bstack1111l1_opy_ (u"ࠢࡵࡴࡤࡧࡰࡥࡦࡪࡺࡷࡹࡷ࡫࡟ࡦࡸࡨࡲࡹࡀࠠࡧࡣ࡯ࡰࡧࡧࡣ࡬ࠢࡷࡥࡷ࡭ࡥࡵ࠿ࡾࡸࡦࡸࡧࡦࡶࢀࠤ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦ࠿ࡾࡪ࡮ࡾࡴࡶࡴࡨࡲࡦࡳࡥࡾࠢࡱࡳࡩ࡫࠽ࡼࡰࡲࡨࡪࢃࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࠤᕔ") + str(test_hook_state) + bstack1111l1_opy_ (u"ࠣࠤᕕ"))
        if not fixturedef or not scope or not target:
            self.logger.warning(bstack1111l1_opy_ (u"ࠤࡷࡶࡦࡩ࡫ࡠࡨ࡬ࡼࡹࡻࡲࡦࡡࡨࡺࡪࡴࡴ࠻ࠢࡸࡲ࡭ࡧ࡮ࡥ࡮ࡨࡨࠥ࡫ࡶࡦࡰࡷࡁࢀࡺࡥࡴࡶࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥࡳࡵࡣࡷࡩࢂ࠴ࡻࡵࡧࡶࡸࡤ࡮࡯ࡰ࡭ࡢࡷࡹࡧࡴࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡨࡪ࡬࠽ࡼࡨ࡬ࡼࡹࡻࡲࡦࡦࡨࡪࢂࠦࡳࡤࡱࡳࡩࡂࢁࡳࡤࡱࡳࡩࢂࠦࡴࡢࡴࡪࡩࡹࡃࠢᕖ") + str(target) + bstack1111l1_opy_ (u"ࠥࠦᕗ"))
            return None
        instance = TestFramework.bstack1llll1l1lll_opy_(target)
        if not instance:
            self.logger.warning(bstack1111l1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡪ࡮ࡾࡴࡶࡴࡨࡣࡪࡼࡥ࡯ࡶ࠽ࠤࡺࡴࡨࡢࡰࡧࡰࡪࡪࠠࡦࡸࡨࡲࡹࡃࡻࡵࡧࡶࡸࡤ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࡠࡵࡷࡥࡹ࡫ࡽ࠯ࡽࡷࡩࡸࡺ࡟ࡩࡱࡲ࡯ࡤࡹࡴࡢࡶࡨࢁࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡦࡦࡹࡥࡪࡦࡀࡿࡧࡧࡳࡦ࡫ࡧࢁࠥࡺࡡࡳࡩࡨࡸࡂࠨᕘ") + str(target) + bstack1111l1_opy_ (u"ࠧࠨᕙ"))
            return None
        bstack11lllll1111_opy_ = TestFramework.bstack1lllll111l1_opy_(instance, bstack1lll111ll11_opy_.bstack1l1111111ll_opy_, {})
        if os.getenv(bstack1111l1_opy_ (u"ࠨࡓࡅࡍࡢࡇࡑࡏ࡟ࡇࡎࡄࡋࡤࡌࡉ࡙ࡖࡘࡖࡊ࡙ࠢᕚ"), bstack1111l1_opy_ (u"ࠢ࠲ࠤᕛ")) == bstack1111l1_opy_ (u"ࠣ࠳ࠥᕜ"):
            bstack1l111ll1lll_opy_ = bstack1111l1_opy_ (u"ࠤ࠽ࠦᕝ").join((scope, fixturename))
            bstack11llll1l1l1_opy_ = datetime.now(tz=timezone.utc)
            bstack11lllllllll_opy_ = {
                bstack1111l1_opy_ (u"ࠥ࡯ࡪࡿࠢᕞ"): bstack1l111ll1lll_opy_,
                bstack1111l1_opy_ (u"ࠦࡹࡧࡧࡴࠤᕟ"): bstack1lll111ll11_opy_.__1l1111lll1l_opy_(request.node),
                bstack1111l1_opy_ (u"ࠧ࡬ࡩࡹࡶࡸࡶࡪࠨᕠ"): fixturedef,
                bstack1111l1_opy_ (u"ࠨࡳࡤࡱࡳࡩࠧᕡ"): scope,
                bstack1111l1_opy_ (u"ࠢࡵࡻࡳࡩࠧᕢ"): None,
            }
            try:
                if test_hook_state == bstack1lll11l11ll_opy_.POST and callable(getattr(args[-1], bstack1111l1_opy_ (u"ࠣࡩࡨࡸࡤࡸࡥࡴࡷ࡯ࡸࠧᕣ"), None)):
                    bstack11lllllllll_opy_[bstack1111l1_opy_ (u"ࠤࡷࡽࡵ࡫ࠢᕤ")] = TestFramework.bstack1l1ll1l1l11_opy_(args[-1].get_result())
            except Exception as e:
                pass
            if test_hook_state == bstack1lll11l11ll_opy_.PRE:
                bstack11lllllllll_opy_[bstack1111l1_opy_ (u"ࠥࡹࡺ࡯ࡤࠣᕥ")] = uuid4().__str__()
                bstack11lllllllll_opy_[bstack1lll111ll11_opy_.bstack11lllll11l1_opy_] = bstack11llll1l1l1_opy_
            elif test_hook_state == bstack1lll11l11ll_opy_.POST:
                bstack11lllllllll_opy_[bstack1lll111ll11_opy_.bstack1l1111llll1_opy_] = bstack11llll1l1l1_opy_
            if bstack1l111ll1lll_opy_ in bstack11lllll1111_opy_:
                bstack11lllll1111_opy_[bstack1l111ll1lll_opy_].update(bstack11lllllllll_opy_)
                self.logger.debug(bstack1111l1_opy_ (u"ࠦࡺࡶࡤࡢࡶࡨࡨࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡁࠧᕦ") + str(bstack11lllll1111_opy_[bstack1l111ll1lll_opy_]) + bstack1111l1_opy_ (u"ࠧࠨᕧ"))
            else:
                bstack11lllll1111_opy_[bstack1l111ll1lll_opy_] = bstack11lllllllll_opy_
                self.logger.debug(bstack1111l1_opy_ (u"ࠨࡳࡢࡸࡨࡨࠥ࡬ࡩࡹࡶࡸࡶࡪࡴࡡ࡮ࡧࡀࡿ࡫࡯ࡸࡵࡷࡵࡩࡳࡧ࡭ࡦࡿࠣࡷࡨࡵࡰࡦ࠿ࡾࡷࡨࡵࡰࡦࡿࠣࡪ࡮ࡾࡴࡶࡴࡨࡁࢀࡺࡥࡴࡶࡢࡪ࡮ࡾࡴࡶࡴࡨࢁࠥࡺࡲࡢࡥ࡮ࡩࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࡳ࠾ࠤᕨ") + str(len(bstack11lllll1111_opy_)) + bstack1111l1_opy_ (u"ࠢࠣᕩ"))
        TestFramework.bstack1lllll1l1l1_opy_(instance, bstack1lll111ll11_opy_.bstack1l1111111ll_opy_, bstack11lllll1111_opy_)
        self.logger.debug(bstack1111l1_opy_ (u"ࠣࡵࡤࡺࡪࡪࠠࡧ࡫ࡻࡸࡺࡸࡥࡴ࠿ࡾࡰࡪࡴࠨࡵࡴࡤࡧࡰ࡫ࡤࡠࡨ࡬ࡼࡹࡻࡲࡦࡵࠬࢁࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠽ࠣᕪ") + str(instance.ref()) + bstack1111l1_opy_ (u"ࠤࠥᕫ"))
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
            bstack1lll111ll11_opy_.bstack1l1111111ll_opy_: {},
            bstack1lll111ll11_opy_.bstack1l1111l1l11_opy_: {},
            bstack1lll111ll11_opy_.bstack1l1111lllll_opy_: {},
        })
        if len(args) > 1 and isinstance(args[1], tuple):
            TestFramework.bstack1lllll1l1l1_opy_(ob, TestFramework.bstack1l111111l11_opy_, str(args[1][0]))
        if context.platform_index >= 0:
            TestFramework.bstack1lllll1l1l1_opy_(ob, TestFramework.bstack1ll11l11ll1_opy_, context.platform_index)
        TestFramework.bstack1lllll1111l_opy_[ctx.id] = ob
        self.logger.debug(bstack1111l1_opy_ (u"ࠥࡷࡦࡼࡥࡥࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࠤࡨࡺࡸ࠯࡫ࡧࡁࢀࡩࡴࡹ࠰࡬ࡨࢂࠦࡴࡢࡴࡪࡩࡹࡃࡻࡵࡣࡵ࡫ࡪࡺࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࡴ࠿ࠥᕬ") + str(TestFramework.bstack1lllll1111l_opy_.keys()) + bstack1111l1_opy_ (u"ࠦࠧᕭ"))
        return ob
    def bstack1l1l1ll11ll_opy_(self, instance: bstack1ll1llll1l1_opy_, bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_]):
        bstack11lllll1l11_opy_ = (
            bstack1lll111ll11_opy_.bstack1l1111l1111_opy_
            if bstack1llll1ll1l1_opy_[1] == bstack1lll11l11ll_opy_.PRE
            else bstack1lll111ll11_opy_.bstack1l111l1ll11_opy_
        )
        hook = bstack1lll111ll11_opy_.bstack1l111l1l1l1_opy_(instance, bstack11lllll1l11_opy_)
        entries = hook.get(TestFramework.bstack1l11111llll_opy_, []) if isinstance(hook, dict) else []
        entries.extend(TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l111l111ll_opy_, []))
        return entries
    def bstack1l1ll111lll_opy_(self, instance: bstack1ll1llll1l1_opy_, bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_]):
        bstack11lllll1l11_opy_ = (
            bstack1lll111ll11_opy_.bstack1l1111l1111_opy_
            if bstack1llll1ll1l1_opy_[1] == bstack1lll11l11ll_opy_.PRE
            else bstack1lll111ll11_opy_.bstack1l111l1ll11_opy_
        )
        bstack1lll111ll11_opy_.bstack1l111ll1l11_opy_(instance, bstack11lllll1l11_opy_)
        TestFramework.bstack1lllll111l1_opy_(instance, TestFramework.bstack1l111l111ll_opy_, []).clear()
    def bstack1l111l11l11_opy_(self, hook: Dict[str, Any]) -> None:
        bstack1111l1_opy_ (u"ࠧࠨࠢࠋࠢࠣࠤࠥࠦࠠࠡࠢࡓࡶࡴࡩࡥࡴࡵࡨࡷࠥࡺࡨࡦࠢࡋࡳࡴࡱࡌࡦࡸࡨࡰࠥࡧࡴࡵࡣࡦ࡬ࡲ࡫࡮ࡵࡵࠣࡷ࡮ࡳࡩ࡭ࡣࡵࠤࡹࡵࠠࡵࡪࡨࠤࡏࡧࡶࡢࠢ࡬ࡱࡵࡲࡥ࡮ࡧࡱࡸࡦࡺࡩࡰࡰ࠱ࠎࠥࠦࠠࠡࠢࠣࠤ࡚ࠥࡨࡪࡵࠣࡱࡪࡺࡨࡰࡦ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡆ࡬ࡪࡩ࡫ࡴࠢࡷ࡬ࡪࠦࡈࡰࡱ࡮ࡐࡪࡼࡥ࡭ࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥ࡯࡮ࡴ࡫ࡧࡩࠥࢄ࠯࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠯ࡖࡲ࡯ࡳࡦࡪࡥࡥࡃࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡌ࡯ࡳࠢࡨࡥࡨ࡮ࠠࡧ࡫࡯ࡩࠥ࡯࡮ࠡࡪࡲࡳࡰࡥ࡬ࡦࡸࡨࡰࡤ࡬ࡩ࡭ࡧࡶ࠰ࠥࡸࡥࡱ࡮ࡤࡧࡪࡹࠠࠣࡖࡨࡷࡹࡒࡥࡷࡧ࡯ࠦࠥࡽࡩࡵࡪࠣࠦࡍࡵ࡯࡬ࡎࡨࡺࡪࡲࠢࠡ࡫ࡱࠤ࡮ࡺࡳࠡࡲࡤࡸ࡭࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣ࠱ࠥࡏࡦࠡࡣࠣࡪ࡮ࡲࡥࠡ࡫ࡱࠤࡹ࡮ࡥࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡲࡧࡴࡤࡪࡨࡷࠥࡧࠠ࡮ࡱࡧ࡭࡫࡯ࡥࡥࠢ࡫ࡳࡴࡱ࠭࡭ࡧࡹࡩࡱࠦࡦࡪ࡮ࡨ࠰ࠥ࡯ࡴࠡࡥࡵࡩࡦࡺࡥࡴࠢࡤࠤࡑࡵࡧࡆࡰࡷࡶࡾࠦ࡯ࡣ࡬ࡨࡧࡹࠦࡷࡪࡶ࡫ࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࠡࡦࡨࡸࡦ࡯࡬ࡴ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦ࠭ࠡࡕ࡬ࡱ࡮ࡲࡡࡳ࡮ࡼ࠰ࠥ࡯ࡴࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡶࠤࡇࡻࡩ࡭ࡦࡏࡩࡻ࡫࡬ࠡࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࡸࠦ࡬ࡰࡥࡤࡸࡪࡪࠠࡪࡰࠣࡌࡴࡵ࡫ࡍࡧࡹࡩࡱ࠵ࡂࡶ࡫࡯ࡨࡑ࡫ࡶࡦ࡮ࡋࡳࡴࡱࡅࡷࡧࡱࡸࠥࡨࡹࠡࡴࡨࡴࡱࡧࡣࡪࡰࡪࠤࠧࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠤࠣࡻ࡮ࡺࡨࠡࠤࡋࡳࡴࡱࡌࡦࡸࡨࡰ࠴ࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠦ࠳ࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢ࠰ࠤ࡙࡮ࡥࠡࡥࡵࡩࡦࡺࡥࡥࠢࡏࡳ࡬ࡋ࡮ࡵࡴࡼࠤࡴࡨࡪࡦࡥࡷࡷࠥࡧࡲࡦࠢࡤࡨࡩ࡫ࡤࠡࡶࡲࠤࡹ࡮ࡥࠡࡪࡲࡳࡰ࠭ࡳࠡࠤ࡯ࡳ࡬ࡹࠢࠡ࡮࡬ࡷࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥ࡮࡯ࡰ࡭࠽ࠤ࡙࡮ࡥࠡࡧࡹࡩࡳࡺࠠࡥ࡫ࡦࡸ࡮ࡵ࡮ࡢࡴࡼࠤࡨࡵ࡮ࡵࡣ࡬ࡲ࡮ࡴࡧࠡࡧࡻ࡭ࡸࡺࡩ࡯ࡩࠣࡰࡴ࡭ࡳࠡࡣࡱࡨࠥ࡮࡯ࡰ࡭ࠣ࡭ࡳ࡬࡯ࡳ࡯ࡤࡸ࡮ࡵ࡮࠯ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࡩࡱࡲ࡯ࡤࡲࡥࡷࡧ࡯ࡣ࡫࡯࡬ࡦࡵ࠽ࠤࡑ࡯ࡳࡵࠢࡲࡪࠥࡖࡡࡵࡪࠣࡳࡧࡰࡥࡤࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡷ࡬ࡪࠦࡔࡦࡵࡷࡐࡪࡼࡥ࡭ࠢࡰࡳࡳ࡯ࡴࡰࡴ࡬ࡲ࡬࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡨࡵࡪ࡮ࡧࡣࡱ࡫ࡶࡦ࡮ࡢࡪ࡮ࡲࡥࡴ࠼ࠣࡐ࡮ࡹࡴࠡࡱࡩࠤࡕࡧࡴࡩࠢࡲࡦ࡯࡫ࡣࡵࡵࠣࡪࡷࡵ࡭ࠡࡶ࡫ࡩࠥࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࠢࡰࡳࡳ࡯ࡴࡰࡴ࡬ࡲ࡬࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࠤࠥࠦᕮ")
        global _1l1ll11llll_opy_
        platform_index = os.environ[bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡌࡂࡖࡉࡓࡗࡓ࡟ࡊࡐࡇࡉ࡝࠭ᕯ")]
        bstack1l1l1l1111l_opy_ = os.path.join(bstack1l1ll1lllll_opy_, (bstack1l1ll1l111l_opy_ + str(platform_index)), bstack11llll11l1l_opy_)
        if not os.path.exists(bstack1l1l1l1111l_opy_) or not os.path.isdir(bstack1l1l1l1111l_opy_):
            self.logger.debug(bstack1111l1_opy_ (u"ࠢࡅ࡫ࡵࡩࡨࡺ࡯ࡳࡻࠣࡨࡴ࡫ࡳࠡࡰࡲࡸࠥ࡫ࡸࡪࡵࡷࡷࠥࡺ࡯ࠡࡲࡵࡳࡨ࡫ࡳࡴࠢࡾࢁࠧᕰ").format(bstack1l1l1l1111l_opy_))
            return
        logs = hook.get(bstack1111l1_opy_ (u"ࠣ࡮ࡲ࡫ࡸࠨᕱ"), [])
        with os.scandir(bstack1l1l1l1111l_opy_) as entries:
            for entry in entries:
                abs_path = os.path.abspath(entry.path)
                if abs_path in _1l1ll11llll_opy_:
                    self.logger.info(bstack1111l1_opy_ (u"ࠤࡓࡥࡹ࡮ࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡲࡵࡳࡨ࡫ࡳࡴࡧࡧࠤࢀࢃࠢᕲ").format(abs_path))
                    continue
                if entry.is_file():
                    try:
                        timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                    except Exception:
                        timestamp = bstack1111l1_opy_ (u"ࠥࠦᕳ")
                    log_entry = bstack1ll1l1l1lll_opy_(
                        kind=bstack1111l1_opy_ (u"࡙ࠦࡋࡓࡕࡡࡄࡘ࡙ࡇࡃࡉࡏࡈࡒ࡙ࠨᕴ"),
                        message=bstack1111l1_opy_ (u"ࠧࠨᕵ"),
                        level=bstack1111l1_opy_ (u"ࠨࠢᕶ"),
                        timestamp=timestamp,
                        fileName=entry.name,
                        bstack1l1l1ll1ll1_opy_=entry.stat().st_size,
                        bstack1l1ll111l11_opy_=bstack1111l1_opy_ (u"ࠢࡎࡃࡑ࡙ࡆࡒ࡟ࡖࡒࡏࡓࡆࡊࠢᕷ"),
                        bstack1l1lll_opy_=os.path.abspath(entry.path),
                        bstack11lllll1l1l_opy_=hook.get(TestFramework.bstack1l1111lll11_opy_)
                    )
                    logs.append(log_entry)
                    _1l1ll11llll_opy_.add(abs_path)
        platform_index = os.environ[bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨᕸ")]
        bstack1l11111lll1_opy_ = os.path.join(bstack1l1ll1lllll_opy_, (bstack1l1ll1l111l_opy_ + str(platform_index)), bstack11llll11l1l_opy_, bstack11llll1111l_opy_)
        if not os.path.exists(bstack1l11111lll1_opy_) or not os.path.isdir(bstack1l11111lll1_opy_):
            self.logger.info(bstack1111l1_opy_ (u"ࠤࡑࡳࠥࡈࡵࡪ࡮ࡧࡐࡪࡼࡥ࡭ࡊࡲࡳࡰࡋࡶࡦࡰࡷࠤࡦࡺࡴࡢࡥ࡫ࡱࡪࡴࡴࡴࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽࠥ࡬࡯ࡶࡰࡧࠤࡦࡺ࠺ࠡࡽࢀࠦᕹ").format(bstack1l11111lll1_opy_))
        else:
            self.logger.info(bstack1111l1_opy_ (u"ࠥࡔࡷࡵࡣࡦࡵࡶ࡭ࡳ࡭ࠠࡃࡷ࡬ࡰࡩࡒࡥࡷࡧ࡯ࡌࡴࡵ࡫ࡆࡸࡨࡲࡹࠦࡡࡵࡶࡤࡧ࡭ࡳࡥ࡯ࡶࡶࠤ࡫ࡸ࡯࡮ࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽ࠿ࠦࡻࡾࠤᕺ").format(bstack1l11111lll1_opy_))
            with os.scandir(bstack1l11111lll1_opy_) as entries:
                for entry in entries:
                    abs_path = os.path.abspath(entry.path)
                    if abs_path in _1l1ll11llll_opy_:
                        self.logger.info(bstack1111l1_opy_ (u"ࠦࡕࡧࡴࡩࠢࡤࡰࡷ࡫ࡡࡥࡻࠣࡴࡷࡵࡣࡦࡵࡶࡩࡩࠦࡻࡾࠤᕻ").format(abs_path))
                        continue
                    if entry.is_file():
                        try:
                            timestamp = datetime.fromtimestamp(entry.stat().st_mtime, tz=timezone.utc).isoformat()
                        except Exception:
                            timestamp = bstack1111l1_opy_ (u"ࠧࠨᕼ")
                        log_entry = bstack1ll1l1l1lll_opy_(
                            kind=bstack1111l1_opy_ (u"ࠨࡔࡆࡕࡗࡣࡆ࡚ࡔࡂࡅࡋࡑࡊࡔࡔࠣᕽ"),
                            message=bstack1111l1_opy_ (u"ࠢࠣᕾ"),
                            level=bstack1111l1_opy_ (u"ࠣࡄࡸ࡭ࡱࡪࡌࡦࡸࡨࡰࠧᕿ"),
                            timestamp=timestamp,
                            fileName=entry.name,
                            bstack1l1l1ll1ll1_opy_=entry.stat().st_size,
                            bstack1l1ll111l11_opy_=bstack1111l1_opy_ (u"ࠤࡐࡅࡓ࡛ࡁࡍࡡࡘࡔࡑࡕࡁࡅࠤᖀ"),
                            bstack1l1lll_opy_=os.path.abspath(entry.path),
                            bstack1l1l1lll111_opy_=hook.get(TestFramework.bstack1l1111lll11_opy_)
                        )
                        logs.append(log_entry)
                        _1l1ll11llll_opy_.add(abs_path)
        hook[bstack1111l1_opy_ (u"ࠥࡰࡴ࡭ࡳࠣᖁ")] = logs
    def bstack1l1l1l111l1_opy_(
        self,
        bstack1l1ll1111ll_opy_: bstack1ll1llll1l1_opy_,
        entries: List[bstack1ll1l1l1lll_opy_],
    ):
        req = structs.LogCreatedEventRequest()
        req.bin_session_id = os.environ.get(bstack1111l1_opy_ (u"ࠦࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡇࡑࡏ࡟ࡃࡋࡑࡣࡘࡋࡓࡔࡋࡒࡒࡤࡏࡄࠣᖂ"))
        req.platform_index = TestFramework.bstack1lllll111l1_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1ll11l11ll1_opy_)
        req.execution_context.hash = str(bstack1l1ll1111ll_opy_.context.hash)
        req.execution_context.thread_id = str(bstack1l1ll1111ll_opy_.context.thread_id)
        req.execution_context.process_id = str(bstack1l1ll1111ll_opy_.context.process_id)
        for entry in entries:
            log_entry = req.logs.add()
            log_entry.test_framework_name = TestFramework.bstack1lllll111l1_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1ll1111llll_opy_)
            log_entry.test_framework_version = TestFramework.bstack1lllll111l1_opy_(bstack1l1ll1111ll_opy_, TestFramework.bstack1l1l11llll1_opy_)
            log_entry.uuid = entry.bstack11lllll1l1l_opy_
            log_entry.test_framework_state = bstack1l1ll1111ll_opy_.state.name
            log_entry.message = entry.message.encode(bstack1111l1_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦᖃ"))
            log_entry.kind = entry.kind
            log_entry.timestamp = (
                entry.timestamp.isoformat()
                if isinstance(entry.timestamp, datetime)
                else datetime.now(tz=timezone.utc).isoformat()
            )
            log_entry.level = bstack1111l1_opy_ (u"ࠨࠢᖄ")
            if entry.kind == bstack1111l1_opy_ (u"ࠢࡕࡇࡖࡘࡤࡇࡔࡕࡃࡆࡌࡒࡋࡎࡕࠤᖅ"):
                log_entry.file_name = entry.fileName
                log_entry.file_size = entry.bstack1l1l1ll1ll1_opy_
                log_entry.file_path = entry.bstack1l1lll_opy_
        def bstack1l1l1ll1l11_opy_():
            bstack1lll11l11_opy_ = datetime.now()
            try:
                self.bstack1lll1l1lll1_opy_.LogCreatedEvent(req)
                bstack1l1ll1111ll_opy_.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠧᖆ"), datetime.now() - bstack1lll11l11_opy_)
            except grpc.RpcError as e:
                self.log_error(bstack1111l1_opy_ (u"ࠤࡵࡴࡨ࠳ࡥࡳࡴࡲࡶ࠿ࠦࡳࡦࡰࡧࡣࡱࡵࡧࡠࡥࡵࡩࡦࡺࡥࡥࡡࡨࡺࡪࡴࡴࡠࡣࡷࡸࡦࡩࡨ࡮ࡧࡱࡸࠥࢁࡽࠣᖇ").format(str(e)))
                traceback.print_exc()
        self.bstack1lllllll1l1_opy_.enqueue(bstack1l1l1ll1l11_opy_)
    def __1l111l11111_opy_(self, instance) -> None:
        bstack1111l1_opy_ (u"ࠥࠦࠧࠐࠠࠡࠢࠣࠤࠥࠦࠠࡍࡱࡤࡨࡸࠦࡣࡶࡵࡷࡳࡲࠦࡴࡢࡩࡶࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥ࡭ࡩࡷࡧࡱࠤࡹ࡫ࡳࡵࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠥ࡯࡮ࡴࡶࡤࡲࡨ࡫࠮ࠋࠢࠣࠤࠥࠦࠠࠡࠢࡆࡶࡪࡧࡴࡦࡵࠣࡥࠥࡪࡩࡤࡶࠣࡧࡴࡴࡴࡢ࡫ࡱ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡲࡥࡷࡧ࡯ࠤࡨࡻࡳࡵࡱࡰࠤࡲ࡫ࡴࡢࡦࡤࡸࡦࠦࡲࡦࡶࡵ࡭ࡪࡼࡥࡥࠢࡩࡶࡴࡳࠊࠡࠢࠣࠤࠥࠦࠠࠡࡅࡸࡷࡹࡵ࡭ࡕࡣࡪࡑࡦࡴࡡࡨࡧࡵࠤࡦࡴࡤࠡࡷࡳࡨࡦࡺࡥࡴࠢࡷ࡬ࡪࠦࡩ࡯ࡵࡷࡥࡳࡩࡥࠡࡵࡷࡥࡹ࡫ࠠࡶࡵ࡬ࡲ࡬ࠦࡳࡦࡶࡢࡷࡹࡧࡴࡦࡡࡨࡲࡹࡸࡩࡦࡵ࠱ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠨࠢࠣᖈ")
        bstack1l111ll11ll_opy_ = {bstack1111l1_opy_ (u"ࠦࡨࡻࡳࡵࡱࡰࡣࡲ࡫ࡴࡢࡦࡤࡸࡦࠨᖉ"): bstack1lll1lll1ll_opy_.bstack1l111ll1l1l_opy_()}
        from browserstack_sdk.sdk_cli.test_framework import TestFramework
        TestFramework.bstack11llll1l111_opy_(instance, bstack1l111ll11ll_opy_)
    @staticmethod
    def bstack1l111l1l1l1_opy_(instance: bstack1ll1llll1l1_opy_, bstack11lllll1l11_opy_: str):
        bstack1l111l1l1ll_opy_ = (
            bstack1lll111ll11_opy_.bstack1l1111l1l11_opy_
            if bstack11lllll1l11_opy_ == bstack1lll111ll11_opy_.bstack1l111l1ll11_opy_
            else bstack1lll111ll11_opy_.bstack1l1111lllll_opy_
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
        hook = bstack1lll111ll11_opy_.bstack1l111l1l1l1_opy_(instance, bstack11lllll1l11_opy_)
        if isinstance(hook, dict):
            hook.get(TestFramework.bstack1l11111llll_opy_, []).clear()
    @staticmethod
    def __1l111ll1ll1_opy_(instance: bstack1ll1llll1l1_opy_, *args):
        if len(args) < 2 or not callable(getattr(args[1], bstack1111l1_opy_ (u"ࠧ࡭ࡥࡵࡡࡵࡩࡨࡵࡲࡥࡵࠥᖊ"), None)):
            return
        if os.getenv(bstack1111l1_opy_ (u"ࠨࡓࡅࡍࡢࡇࡑࡏ࡟ࡇࡎࡄࡋࡤࡒࡏࡈࡕࠥᖋ"), bstack1111l1_opy_ (u"ࠢ࠲ࠤᖌ")) != bstack1111l1_opy_ (u"ࠣ࠳ࠥᖍ"):
            bstack1lll111ll11_opy_.logger.warning(bstack1111l1_opy_ (u"ࠤ࡬࡫ࡳࡵࡲࡪࡰࡪࠤࡨࡧࡰ࡭ࡱࡪࠦᖎ"))
            return
        bstack11lllll11ll_opy_ = {
            bstack1111l1_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤᖏ"): (bstack1lll111ll11_opy_.bstack1l1111l1111_opy_, bstack1lll111ll11_opy_.bstack1l1111lllll_opy_),
            bstack1111l1_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࠨᖐ"): (bstack1lll111ll11_opy_.bstack1l111l1ll11_opy_, bstack1lll111ll11_opy_.bstack1l1111l1l11_opy_),
        }
        for when in (bstack1111l1_opy_ (u"ࠧࡹࡥࡵࡷࡳࠦᖑ"), bstack1111l1_opy_ (u"ࠨࡣࡢ࡮࡯ࠦᖒ"), bstack1111l1_opy_ (u"ࠢࡵࡧࡤࡶࡩࡵࡷ࡯ࠤᖓ")):
            bstack11llll1lll1_opy_ = args[1].get_records(when)
            if not bstack11llll1lll1_opy_:
                continue
            records = [
                bstack1ll1l1l1lll_opy_(
                    kind=TestFramework.bstack1l1l1ll111l_opy_,
                    message=r.message,
                    level=r.levelname if hasattr(r, bstack1111l1_opy_ (u"ࠣ࡮ࡨࡺࡪࡲ࡮ࡢ࡯ࡨࠦᖔ")) and r.levelname else None,
                    timestamp=(
                        datetime.fromtimestamp(r.created, tz=timezone.utc)
                        if hasattr(r, bstack1111l1_opy_ (u"ࠤࡦࡶࡪࡧࡴࡦࡦࠥᖕ")) and r.created
                        else None
                    ),
                )
                for r in bstack11llll1lll1_opy_
                if isinstance(getattr(r, bstack1111l1_opy_ (u"ࠥࡱࡪࡹࡳࡢࡩࡨࠦᖖ"), None), str) and r.message.strip()
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
    def __11llllll1l1_opy_(test) -> Dict[str, Any]:
        bstack1l1l1l1lll_opy_ = bstack1lll111ll11_opy_.__11lllll1lll_opy_(test.location) if hasattr(test, bstack1111l1_opy_ (u"ࠦࡱࡵࡣࡢࡶ࡬ࡳࡳࠨᖗ")) else getattr(test, bstack1111l1_opy_ (u"ࠧࡴ࡯ࡥࡧ࡬ࡨࠧᖘ"), None)
        test_name = test.name if hasattr(test, bstack1111l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᖙ")) else None
        bstack1l111l1111l_opy_ = test.fspath.strpath if hasattr(test, bstack1111l1_opy_ (u"ࠢࡧࡵࡳࡥࡹ࡮ࠢᖚ")) and test.fspath else None
        if not bstack1l1l1l1lll_opy_ or not test_name or not bstack1l111l1111l_opy_:
            return None
        code = None
        if hasattr(test, bstack1111l1_opy_ (u"ࠣࡱࡥ࡮ࠧᖛ")):
            try:
                import inspect
                code = inspect.getsource(test.obj)
            except:
                pass
        bstack11llll11111_opy_ = []
        try:
            bstack11llll11111_opy_ = bstack1ll1111ll1_opy_.bstack1111ll11ll_opy_(test)
        except:
            bstack1lll111ll11_opy_.logger.warning(bstack1111l1_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡬ࡩ࡯ࡦࠣࡸࡪࡹࡴࠡࡵࡦࡳࡵ࡫ࡳ࠭ࠢࡷࡩࡸࡺࠠࡴࡥࡲࡴࡪࡹࠠࡸ࡫࡯ࡰࠥࡨࡥࠡࡴࡨࡷࡴࡲࡶࡦࡦࠣ࡭ࡳࠦࡃࡍࡋࠥᖜ"))
        return {
            TestFramework.bstack1ll11l111l1_opy_: uuid4().__str__(),
            TestFramework.bstack1l11111l111_opy_: bstack1l1l1l1lll_opy_,
            TestFramework.bstack1ll1111l111_opy_: test_name,
            TestFramework.bstack1l1l11ll11l_opy_: getattr(test, bstack1111l1_opy_ (u"ࠥࡲࡴࡪࡥࡪࡦࠥᖝ"), None),
            TestFramework.bstack1l11111l11l_opy_: bstack1l111l1111l_opy_,
            TestFramework.bstack11llll11lll_opy_: bstack1lll111ll11_opy_.__1l1111lll1l_opy_(test),
            TestFramework.bstack11llll1ll1l_opy_: code,
            TestFramework.bstack1l11lll1l1l_opy_: TestFramework.bstack1l11111ll11_opy_,
            TestFramework.bstack1l11l11l1ll_opy_: bstack1l1l1l1lll_opy_,
            TestFramework.bstack11llll111l1_opy_: bstack11llll11111_opy_
        }
    @staticmethod
    def __1l1111lll1l_opy_(test) -> List[str]:
        markers = []
        current = test
        while current:
            own_markers = getattr(current, bstack1111l1_opy_ (u"ࠦࡴࡽ࡮ࡠ࡯ࡤࡶࡰ࡫ࡲࡴࠤᖞ"), [])
            markers.extend([getattr(m, bstack1111l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᖟ"), None) for m in own_markers if getattr(m, bstack1111l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᖠ"), None)])
            current = getattr(current, bstack1111l1_opy_ (u"ࠢࡱࡣࡵࡩࡳࡺࠢᖡ"), None)
        return markers
    @staticmethod
    def __11lllll1lll_opy_(location):
        return bstack1111l1_opy_ (u"ࠣ࠼࠽ࠦᖢ").join(filter(lambda x: isinstance(x, str), location))