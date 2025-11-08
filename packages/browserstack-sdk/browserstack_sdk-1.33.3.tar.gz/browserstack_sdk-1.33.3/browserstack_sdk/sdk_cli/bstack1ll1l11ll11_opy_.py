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
from datetime import datetime
import os
import threading
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll1ll11l_opy_,
    bstack1lllll11111_opy_,
    bstack1lllll11l11_opy_,
    bstack1llll1l11l1_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1ll1111_opy_ import bstack1lll111l1l1_opy_
from browserstack_sdk.sdk_cli.test_framework import TestFramework, bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_, bstack1ll1llll1l1_opy_
from typing import Tuple, Dict, Any, List, Union
from browserstack_sdk import sdk_pb2 as structs
from browserstack_sdk.sdk_cli.bstack1ll1l1l1111_opy_ import bstack1lll1111lll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1111ll1_opy_ import bstack1lll11ll1l1_opy_
from browserstack_sdk.sdk_cli.bstack1lll1lll111_opy_ import bstack1ll1ll1llll_opy_
from browserstack_sdk.sdk_cli.bstack1lll1llll1l_opy_ import bstack1ll1ll1111l_opy_
from bstack_utils.helper import bstack1ll111llll1_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
from bstack_utils.bstack1llll1llll_opy_ import bstack1llll11l111_opy_
import grpc
import traceback
import json
class bstack1lll111l111_opy_(bstack1lll1111lll_opy_):
    bstack1ll1111lll1_opy_ = False
    bstack1ll1l11111l_opy_ = bstack1111l1_opy_ (u"ࠨࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࠯ࡹࡨࡦࡩࡸࡩࡷࡧࡵࠦᆛ")
    bstack1ll1l111111_opy_ = bstack1111l1_opy_ (u"ࠢࡳࡧࡰࡳࡹ࡫࠮ࡸࡧࡥࡨࡷ࡯ࡶࡦࡴࠥᆜ")
    bstack1ll111l1111_opy_ = bstack1111l1_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠ࡫ࡱ࡭ࡹࠨᆝ")
    bstack1ll1111l1l1_opy_ = bstack1111l1_opy_ (u"ࠤࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡡ࡬ࡷࡤࡹࡣࡢࡰࡱ࡭ࡳ࡭ࠢᆞ")
    bstack1ll111lll1l_opy_ = bstack1111l1_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴࡢ࡬ࡦࡹ࡟ࡶࡴ࡯ࠦᆟ")
    scripts: Dict[str, Dict[str, str]]
    commands: Dict[str, Dict[str, Dict[str, List[str]]]]
    def __init__(self, bstack1ll1l1ll1ll_opy_, bstack1lll1lllll1_opy_):
        super().__init__()
        self.scripts = dict()
        self.commands = dict()
        self.accessibility = False
        self.bstack1ll111l11l1_opy_ = False
        self.bstack1ll11llll11_opy_ = dict()
        self.bstack1ll11ll1l1l_opy_ = False
        self.bstack1ll111lllll_opy_ = dict()
        if not self.is_enabled():
            return
        self.bstack1ll11l11l11_opy_ = bstack1lll1lllll1_opy_
        bstack1ll1l1ll1ll_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.bstack1lllll111ll_opy_, bstack1lllll11111_opy_.PRE), self.bstack1ll1111l1ll_opy_)
        TestFramework.bstack1ll111111ll_opy_((bstack1ll1ll1lll1_opy_.TEST, bstack1lll11l11ll_opy_.PRE), self.bstack1ll11ll111l_opy_)
        TestFramework.bstack1ll111111ll_opy_((bstack1ll1ll1lll1_opy_.TEST, bstack1lll11l11ll_opy_.POST), self.bstack1ll111ll1l1_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1ll11ll111l_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llll1l1_opy_,
        bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1ll11ll11ll_opy_(instance, args)
        test_framework = f.bstack1lllll111l1_opy_(instance, TestFramework.bstack1ll1111llll_opy_)
        if self.bstack1ll111l11l1_opy_:
            self.bstack1ll11llll11_opy_[bstack1111l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠦᆠ")] = f.bstack1lllll111l1_opy_(instance, TestFramework.bstack1ll11l111l1_opy_)
        if bstack1111l1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠩᆡ") in instance.bstack1ll11lll11l_opy_:
            platform_index = f.bstack1lllll111l1_opy_(instance, TestFramework.bstack1ll11l11ll1_opy_)
            self.accessibility = self.bstack1ll11ll1lll_opy_(tags, self.config[bstack1111l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩᆢ")][platform_index])
        else:
            capabilities = self.bstack1ll11l11l11_opy_.bstack1ll11l1llll_opy_(f, instance, bstack1llll1ll1l1_opy_, *args, **kwargs)
            if not capabilities:
                self.logger.debug(bstack1111l1_opy_ (u"ࠢࡰࡰࡢࡦࡪ࡬࡯ࡳࡧࡢࡸࡪࡹࡴ࠻ࠢࡱࡳࠥࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠤ࡫ࡵࡵ࡯ࡦࠣࡪࡴࡸࠠࡩࡱࡲ࡯ࡤ࡯࡮ࡧࡱࡀࡿ࡭ࡵ࡯࡬ࡡ࡬ࡲ࡫ࡵࡽࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࠢᆣ") + str(kwargs) + bstack1111l1_opy_ (u"ࠣࠤᆤ"))
                return
            self.accessibility = self.bstack1ll11ll1lll_opy_(tags, capabilities)
        if self.bstack1ll11l11l11_opy_.pages and self.bstack1ll11l11l11_opy_.pages.values():
            bstack1ll11l1l11l_opy_ = list(self.bstack1ll11l11l11_opy_.pages.values())
            if bstack1ll11l1l11l_opy_ and isinstance(bstack1ll11l1l11l_opy_[0], (list, tuple)) and bstack1ll11l1l11l_opy_[0]:
                bstack1ll111l111l_opy_ = bstack1ll11l1l11l_opy_[0][0]
                if callable(bstack1ll111l111l_opy_):
                    page = bstack1ll111l111l_opy_()
                    def bstack11lll1l1_opy_():
                        self.get_accessibility_results(page, bstack1111l1_opy_ (u"ࠤࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠨᆥ"))
                    def bstack1ll111l1lll_opy_():
                        self.get_accessibility_results_summary(page, bstack1111l1_opy_ (u"ࠥࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠢᆦ"))
                    setattr(page, bstack1111l1_opy_ (u"ࠦ࡬࡫ࡴࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡒࡦࡵࡸࡰࡹࡹࠢᆧ"), bstack11lll1l1_opy_)
                    setattr(page, bstack1111l1_opy_ (u"ࠧ࡭ࡥࡵࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡓࡧࡶࡹࡱࡺࡓࡶ࡯ࡰࡥࡷࡿࠢᆨ"), bstack1ll111l1lll_opy_)
        self.logger.debug(bstack1111l1_opy_ (u"ࠨࡳࡩࡱࡸࡰࡩࠦࡲࡶࡰࠣࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠣࡺࡦࡲࡵࡦ࠿ࠥᆩ") + str(self.accessibility) + bstack1111l1_opy_ (u"ࠢࠣᆪ"))
    def bstack1ll1111l1ll_opy_(
        self,
        f: bstack1lll111l1l1_opy_,
        driver: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        try:
            bstack1lll11l11_opy_ = datetime.now()
            self.bstack1ll11l11111_opy_(f, exec, *args, **kwargs)
            instance, method_name = exec
            instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠣࡣ࠴࠵ࡾࡀࡩ࡯࡫ࡷࡣࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡣࡨࡵ࡮ࡧ࡫ࡪࠦᆫ"), datetime.now() - bstack1lll11l11_opy_)
            if (
                not f.bstack1ll11l1l111_opy_(method_name)
                or f.bstack1l1lllllll1_opy_(method_name, *args)
                or f.bstack1ll111ll111_opy_(method_name, *args)
            ):
                return
            if not f.bstack1lllll111l1_opy_(instance, bstack1lll111l111_opy_.bstack1ll111l1111_opy_, False):
                if not bstack1lll111l111_opy_.bstack1ll1111lll1_opy_:
                    self.logger.warning(bstack1111l1_opy_ (u"ࠤ࡞ࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࠧᆬ") + str(f.platform_index) + bstack1111l1_opy_ (u"ࠥࡡࠥࡧ࠱࠲ࡻࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴࠢ࡫ࡥࡻ࡫ࠠ࡯ࡱࡷࠤࡧ࡫ࡥ࡯ࠢࡶࡩࡹࠦࡦࡰࡴࠣࡸ࡭࡯ࡳࠡࡵࡨࡷࡸ࡯࡯࡯ࠤᆭ"))
                    bstack1lll111l111_opy_.bstack1ll1111lll1_opy_ = True
                return
            bstack1l1llllllll_opy_ = self.scripts.get(f.framework_name, {})
            if not bstack1l1llllllll_opy_:
                platform_index = f.bstack1lllll111l1_opy_(instance, bstack1lll111l1l1_opy_.bstack1ll11l11ll1_opy_, 0)
                self.logger.debug(bstack1111l1_opy_ (u"ࠦࡳࡵࠠࡢ࠳࠴ࡽࠥࡹࡣࡳ࡫ࡳࡸࡸࠦࡦࡰࡴࠣࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࢀࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࢃࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥ࠾ࠤᆮ") + str(f.framework_name) + bstack1111l1_opy_ (u"ࠧࠨᆯ"))
                return
            command_name = f.bstack1ll11l1111l_opy_(*args)
            if not command_name:
                self.logger.debug(bstack1111l1_opy_ (u"ࠨ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࡤࡱࡰࡱࡦࡴࡤࡠࡰࡤࡱࡪࠦࡦࡰࡴࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࡁࢀ࡬࠮ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥࡾࠢࡰࡩࡹ࡮࡯ࡥࡡࡱࡥࡲ࡫࠽ࠣᆰ") + str(method_name) + bstack1111l1_opy_ (u"ࠢࠣᆱ"))
                return
            bstack1ll11111111_opy_ = f.bstack1lllll111l1_opy_(instance, bstack1lll111l111_opy_.bstack1ll111lll1l_opy_, False)
            if command_name == bstack1111l1_opy_ (u"ࠣࡩࡨࡸࠧᆲ") and not bstack1ll11111111_opy_:
                f.bstack1lllll1l1l1_opy_(instance, bstack1lll111l111_opy_.bstack1ll111lll1l_opy_, True)
                bstack1ll11111111_opy_ = True
            if not bstack1ll11111111_opy_ and not self.bstack1ll111l11l1_opy_:
                self.logger.debug(bstack1111l1_opy_ (u"ࠤࡱࡳ࡛ࠥࡒࡍࠢ࡯ࡳࡦࡪࡥࡥࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡࡥࡲࡱࡲࡧ࡮ࡥࡡࡱࡥࡲ࡫࠽ࠣᆳ") + str(command_name) + bstack1111l1_opy_ (u"ࠥࠦᆴ"))
                return
            scripts_to_run = self.commands.get(f.framework_name, {}).get(method_name, {}).get(command_name, [])
            if not scripts_to_run:
                self.logger.debug(bstack1111l1_opy_ (u"ࠦࡳࡵࠠࡢ࠳࠴ࡽࠥࡹࡣࡳ࡫ࡳࡸࡸࠦࡦࡰࡴࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰࡥ࡮ࡢ࡯ࡨࡁࢀ࡬࠮ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡲࡦࡳࡥࡾࠢࡦࡳࡲࡳࡡ࡯ࡦࡢࡲࡦࡳࡥ࠾ࠤᆵ") + str(command_name) + bstack1111l1_opy_ (u"ࠧࠨᆶ"))
                return
            self.logger.info(bstack1111l1_opy_ (u"ࠨࡲࡶࡰࡱ࡭ࡳ࡭ࠠࡼ࡮ࡨࡲ࠭ࡹࡣࡳ࡫ࡳࡸࡸࡥࡴࡰࡡࡵࡹࡳ࠯ࡽࠡࡵࡦࡶ࡮ࡶࡴࡴࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫࠴ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡࡥࡲࡱࡲࡧ࡮ࡥࡡࡱࡥࡲ࡫࠽ࠣᆷ") + str(command_name) + bstack1111l1_opy_ (u"ࠢࠣᆸ"))
            scripts = [(s, bstack1l1llllllll_opy_[s]) for s in scripts_to_run if s in bstack1l1llllllll_opy_]
            for script_name, bstack1ll11ll1l11_opy_ in scripts:
                try:
                    bstack1lll11l11_opy_ = datetime.now()
                    if script_name == bstack1111l1_opy_ (u"ࠣࡵࡦࡥࡳࠨᆹ"):
                        result = self.perform_scan(driver, method=command_name, framework_name=f.framework_name)
                    instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠤࡤ࠵࠶ࡿ࠺ࠣᆺ") + script_name, datetime.now() - bstack1lll11l11_opy_)
                    if isinstance(result, dict) and not result.get(bstack1111l1_opy_ (u"ࠥࡷࡺࡩࡣࡦࡵࡶࠦᆻ"), True):
                        self.logger.warning(bstack1111l1_opy_ (u"ࠦࡸࡱࡩࡱࠢࡨࡼࡪࡩࡵࡵ࡫ࡱ࡫ࠥࡸࡥ࡮ࡣ࡬ࡲ࡮ࡴࡧࠡࡵࡦࡶ࡮ࡶࡴࡴ࠼ࠣࠦᆼ") + str(result) + bstack1111l1_opy_ (u"ࠧࠨᆽ"))
                        break
                except Exception as e:
                    self.logger.error(bstack1111l1_opy_ (u"ࠨࡥࡳࡴࡲࡶࠥ࡫ࡸࡦࡥࡸࡸ࡮ࡴࡧࠡࡵࡦࡶ࡮ࡶࡴ࠾ࡽࡶࡧࡷ࡯ࡰࡵࡡࡱࡥࡲ࡫ࡽࠡࡧࡵࡶࡴࡸ࠽ࠣᆾ") + str(e) + bstack1111l1_opy_ (u"ࠢࠣᆿ"))
        except Exception as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠣࡱࡱࡣࡧ࡫ࡦࡰࡴࡨࡣࡪࡾࡥࡤࡷࡷࡩࠥ࡫ࡲࡳࡱࡵࡁࠧᇀ") + str(e) + bstack1111l1_opy_ (u"ࠤࠥᇁ"))
    def bstack1ll111ll1l1_opy_(
        self,
        f: TestFramework,
        instance: bstack1ll1llll1l1_opy_,
        bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_],
        *args,
        **kwargs,
    ):
        tags = self._1ll11ll11ll_opy_(instance, args)
        capabilities = self.bstack1ll11l11l11_opy_.bstack1ll11l1llll_opy_(f, instance, bstack1llll1ll1l1_opy_, *args, **kwargs)
        self.accessibility = self.bstack1ll11ll1lll_opy_(tags, capabilities)
        if not self.accessibility:
            self.logger.debug(bstack1111l1_opy_ (u"ࠥࡳࡳࡥࡡࡧࡶࡨࡶࡤࡺࡥࡴࡶ࠽ࠤࡦ࠷࠱ࡺࠢࡱࡳࡹࠦࡥ࡯ࡣࡥࡰࡪࡪࠢᇂ"))
            return
        driver = self.bstack1ll11l11l11_opy_.bstack1ll1111ll11_opy_(f, instance, bstack1llll1ll1l1_opy_, *args, **kwargs)
        test_name = f.bstack1lllll111l1_opy_(instance, TestFramework.bstack1ll1111l111_opy_)
        if not test_name:
            self.logger.debug(bstack1111l1_opy_ (u"ࠦࡴࡴ࡟ࡢࡨࡷࡩࡷࡥࡴࡦࡵࡷ࠾ࠥࡳࡩࡴࡵ࡬ࡲ࡬ࠦࡴࡦࡵࡷࠤࡳࡧ࡭ࡦࠤᇃ"))
            return
        test_uuid = f.bstack1lllll111l1_opy_(instance, TestFramework.bstack1ll11l111l1_opy_)
        if not test_uuid:
            self.logger.debug(bstack1111l1_opy_ (u"ࠧࡵ࡮ࡠࡣࡩࡸࡪࡸ࡟ࡵࡧࡶࡸ࠿ࠦ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࡵࡧࡶࡸࠥࡻࡵࡪࡦࠥᇄ"))
            return
        if isinstance(self.bstack1ll11l11l11_opy_, bstack1ll1ll1llll_opy_):
            framework_name = bstack1111l1_opy_ (u"࠭ࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪᇅ")
        else:
            framework_name = bstack1111l1_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠩᇆ")
        self.bstack1ll11llll1_opy_(driver, test_name, framework_name, test_uuid)
    def perform_scan(self, driver: object, method: Union[None, str], framework_name: str):
        bstack1ll11l111ll_opy_ = bstack1llll11l111_opy_.bstack1ll11ll11l1_opy_(EVENTS.bstack1ll111l11_opy_.value)
        if not self.accessibility:
            self.logger.debug(bstack1111l1_opy_ (u"ࠣࡲࡨࡶ࡫ࡵࡲ࡮ࡡࡶࡧࡦࡴ࠺ࠡࡣ࠴࠵ࡾࠦ࡮ࡰࡶࠣࡩࡳࡧࡢ࡭ࡧࡧࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࢁࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࡽࠡࠤᇇ"))
            return
        bstack1lll11l11_opy_ = datetime.now()
        bstack1ll11ll1l11_opy_ = self.scripts.get(framework_name, {}).get(bstack1111l1_opy_ (u"ࠤࡶࡧࡦࡴࠢᇈ"), None)
        if not bstack1ll11ll1l11_opy_:
            self.logger.debug(bstack1111l1_opy_ (u"ࠥࡴࡪࡸࡦࡰࡴࡰࡣࡸࡩࡡ࡯࠼ࠣࡱ࡮ࡹࡳࡪࡰࡪࠤࠬࡹࡣࡢࡰࠪࠤࡸࡩࡲࡪࡲࡷࠤ࡫ࡵࡲࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦ࠿ࠥᇉ") + str(framework_name) + bstack1111l1_opy_ (u"ࠦࠥࠨᇊ"))
            return
        if self.bstack1ll111l11l1_opy_:
            arg = dict()
            arg[bstack1111l1_opy_ (u"ࠧࡳࡥࡵࡪࡲࡨࠧᇋ")] = method if method else bstack1111l1_opy_ (u"ࠨࠢᇌ")
            arg[bstack1111l1_opy_ (u"ࠢࡵࡪࡗࡩࡸࡺࡒࡶࡰࡘࡹ࡮ࡪࠢᇍ")] = self.bstack1ll11llll11_opy_[bstack1111l1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠣᇎ")]
            arg[bstack1111l1_opy_ (u"ࠤࡷ࡬ࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠢᇏ")] = self.bstack1ll11llll11_opy_[bstack1111l1_opy_ (u"ࠥࡸࡪࡹࡴࡩࡷࡥࡣࡧࡻࡩ࡭ࡦࡢࡹࡺ࡯ࡤࠣᇐ")]
            arg[bstack1111l1_opy_ (u"ࠦࡦࡻࡴࡩࡊࡨࡥࡩ࡫ࡲࠣᇑ")] = self.bstack1ll11llll11_opy_[bstack1111l1_opy_ (u"ࠧࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽ࡙ࡵ࡫ࡦࡰࠥᇒ")]
            arg[bstack1111l1_opy_ (u"ࠨࡴࡩࡌࡺࡸ࡙ࡵ࡫ࡦࡰࠥᇓ")] = self.bstack1ll11llll11_opy_[bstack1111l1_opy_ (u"ࠢࡵࡪࡢ࡮ࡼࡺ࡟ࡵࡱ࡮ࡩࡳࠨᇔ")]
            arg[bstack1111l1_opy_ (u"ࠣࡵࡦࡥࡳ࡚ࡩ࡮ࡧࡶࡸࡦࡳࡰࠣᇕ")] = str(int(datetime.now().timestamp() * 1000))
            bstack1ll11l1l1ll_opy_ = self.bstack1ll111ll1ll_opy_(bstack1111l1_opy_ (u"ࠤࡶࡧࡦࡴࠢᇖ"), self.bstack1ll11llll11_opy_[bstack1111l1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠥᇗ")])
            if bstack1111l1_opy_ (u"ࠦࡨ࡫࡮ࡵࡴࡤࡰࡆࡻࡴࡩࡖࡲ࡯ࡪࡴࠢᇘ") in bstack1ll11l1l1ll_opy_:
                bstack1ll11l1l1ll_opy_ = bstack1ll11l1l1ll_opy_.copy()
                bstack1ll11l1l1ll_opy_[bstack1111l1_opy_ (u"ࠧࡩࡥ࡯ࡶࡵࡥࡱࡇࡵࡵࡪࡋࡩࡦࡪࡥࡳࠤᇙ")] = bstack1ll11l1l1ll_opy_.pop(bstack1111l1_opy_ (u"ࠨࡣࡦࡰࡷࡶࡦࡲࡁࡶࡶ࡫ࡘࡴࡱࡥ࡯ࠤᇚ"))
            arg = bstack1ll111llll1_opy_(arg, bstack1ll11l1l1ll_opy_)
            bstack1ll111lll11_opy_ = bstack1ll11ll1l11_opy_ % json.dumps(arg)
            driver.execute_script(bstack1ll111lll11_opy_)
            return
        instance = bstack1lllll11l11_opy_.bstack1llll1l1lll_opy_(driver)
        if instance:
            if not bstack1lllll11l11_opy_.bstack1lllll111l1_opy_(instance, bstack1lll111l111_opy_.bstack1ll1111l1l1_opy_, False):
                bstack1lllll11l11_opy_.bstack1lllll1l1l1_opy_(instance, bstack1lll111l111_opy_.bstack1ll1111l1l1_opy_, True)
            else:
                self.logger.info(bstack1111l1_opy_ (u"ࠢࡱࡧࡵࡪࡴࡸ࡭ࡠࡵࡦࡥࡳࡀࠠࡢ࡮ࡵࡩࡦࡪࡹࠡ࡫ࡱࠤࡵࡸ࡯ࡨࡴࡨࡷࡸࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࡼࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡳࡧ࡭ࡦࡿࠣࡱࡪࡺࡨࡰࡦࡀࠦᇛ") + str(method) + bstack1111l1_opy_ (u"ࠣࠤᇜ"))
                return
        self.logger.info(bstack1111l1_opy_ (u"ࠤࡳࡩࡷ࡬࡯ࡳ࡯ࡢࡷࡨࡧ࡮࠻ࠢࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࡀࡿ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࢂࠦ࡭ࡦࡶ࡫ࡳࡩࡃࠢᇝ") + str(method) + bstack1111l1_opy_ (u"ࠥࠦᇞ"))
        if framework_name == bstack1111l1_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨᇟ"):
            result = self.bstack1ll11l11l11_opy_.bstack1ll1111l11l_opy_(driver, bstack1ll11ll1l11_opy_)
        else:
            result = driver.execute_async_script(bstack1ll11ll1l11_opy_, {bstack1111l1_opy_ (u"ࠧࡳࡥࡵࡪࡲࡨࠧᇠ"): method if method else bstack1111l1_opy_ (u"ࠨࠢᇡ")})
        bstack1llll11l111_opy_.end(EVENTS.bstack1ll111l11_opy_.value, bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠢ࠻ࡵࡷࡥࡷࡺࠢᇢ"), bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠣ࠼ࡨࡲࡩࠨᇣ"), True, None, command=method)
        if instance:
            bstack1lllll11l11_opy_.bstack1lllll1l1l1_opy_(instance, bstack1lll111l111_opy_.bstack1ll1111l1l1_opy_, False)
            instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠤࡤ࠵࠶ࡿ࠺ࡱࡧࡵࡪࡴࡸ࡭ࡠࡵࡦࡥࡳࠨᇤ"), datetime.now() - bstack1lll11l11_opy_)
        return result
        def bstack1ll11lll1ll_opy_(self, driver: object, framework_name, bstack111lll1ll1_opy_: str):
            self.bstack1ll11111l1l_opy_()
            req = structs.AccessibilityResultRequest()
            req.bin_session_id = self.bin_session_id
            req.bstack1ll11111l11_opy_ = self.bstack1ll11llll11_opy_[bstack1111l1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡸࡲࡤࡻࡵࡪࡦࠥᇥ")]
            req.bstack111lll1ll1_opy_ = bstack111lll1ll1_opy_
            req.session_id = self.bin_session_id
            try:
                r = self.bstack1lll1l1lll1_opy_.AccessibilityResult(req)
                if not r.success:
                    self.logger.debug(bstack1111l1_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࠨᇦ") + str(r) + bstack1111l1_opy_ (u"ࠧࠨᇧ"))
                else:
                    bstack1ll11llll1l_opy_ = json.loads(r.bstack1ll111l1l1l_opy_.decode(bstack1111l1_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᇨ")))
                    if bstack111lll1ll1_opy_ == bstack1111l1_opy_ (u"ࠧࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࠫᇩ"):
                        return bstack1ll11llll1l_opy_.get(bstack1111l1_opy_ (u"ࠣࡦࡤࡸࡦࠨᇪ"), [])
                    else:
                        return bstack1ll11llll1l_opy_.get(bstack1111l1_opy_ (u"ࠤࡧࡥࡹࡧࠢᇫ"), {})
            except grpc.RpcError as e:
                self.logger.error(bstack1111l1_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࠦࡷࡩ࡫࡯ࡩࠥ࡬ࡥࡵࡥ࡫࡭ࡳ࡭ࠠࡨࡧࡷࡣࡦࡶࡰࡠࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡠࡴࡨࡷࡺࡲࡴࠡࡨࡵࡳࡲࠦࡣ࡭࡫࠽ࠤࠧᇬ") + str(e) + bstack1111l1_opy_ (u"ࠦࠧᇭ"))
    @measure(event_name=EVENTS.bstack11l111l11_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def get_accessibility_results(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack1111l1_opy_ (u"ࠧ࡭ࡥࡵࡡࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࡡࡵࡩࡸࡻ࡬ࡵࡵ࠽ࠤࡦ࠷࠱ࡺࠢࡱࡳࡹࠦࡥ࡯ࡣࡥࡰࡪࡪࠢᇮ"))
            return
        if self.bstack1ll111l11l1_opy_:
            self.logger.debug(bstack1111l1_opy_ (u"࠭ࡐࡦࡴࡩࡳࡷࡳࡩ࡯ࡩࠣࡷࡨࡧ࡮ࠡࡨࡲࡶࠥࡧࡰࡱࠢࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᇯ"))
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1ll11lll1ll_opy_(driver, framework_name, bstack1111l1_opy_ (u"ࠢࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࠦᇰ"))
        bstack1ll11ll1l11_opy_ = self.scripts.get(framework_name, {}).get(bstack1111l1_opy_ (u"ࠣࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࠧᇱ"), None)
        if not bstack1ll11ll1l11_opy_:
            self.logger.debug(bstack1111l1_opy_ (u"ࠤࡰ࡭ࡸࡹࡩ࡯ࡩࠣࠫ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࠨࠢࡶࡧࡷ࡯ࡰࡵࠢࡩࡳࡷࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࠣᇲ") + str(framework_name) + bstack1111l1_opy_ (u"ࠥࠦᇳ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack1lll11l11_opy_ = datetime.now()
        if framework_name == bstack1111l1_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨᇴ"):
            result = self.bstack1ll11l11l11_opy_.bstack1ll1111l11l_opy_(driver, bstack1ll11ll1l11_opy_)
        else:
            result = driver.execute_async_script(bstack1ll11ll1l11_opy_)
        instance = bstack1lllll11l11_opy_.bstack1llll1l1lll_opy_(driver)
        if instance:
            instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠧࡧ࠱࠲ࡻ࠽࡫ࡪࡺ࡟ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࡟ࡳࡧࡶࡹࡱࡺࡳࠣᇵ"), datetime.now() - bstack1lll11l11_opy_)
        return result
    @measure(event_name=EVENTS.bstack1l1l1l1l_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def get_accessibility_results_summary(self, driver: object, framework_name):
        if not self.accessibility:
            self.logger.debug(bstack1111l1_opy_ (u"ࠨࡧࡦࡶࡢࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡢࡶࡪࡹࡵ࡭ࡶࡶࡣࡸࡻ࡭࡮ࡣࡵࡽ࠿ࠦࡡ࠲࠳ࡼࠤࡳࡵࡴࠡࡧࡱࡥࡧࡲࡥࡥࠤᇶ"))
            return
        if self.bstack1ll111l11l1_opy_:
            self.perform_scan(driver, method=None, framework_name=framework_name)
            return self.bstack1ll11lll1ll_opy_(driver, framework_name, bstack1111l1_opy_ (u"ࠧࡨࡧࡷࡖࡪࡹࡵ࡭ࡶࡶࡗࡺࡳ࡭ࡢࡴࡼࠫᇷ"))
        bstack1ll11ll1l11_opy_ = self.scripts.get(framework_name, {}).get(bstack1111l1_opy_ (u"ࠣࡩࡨࡸࡗ࡫ࡳࡶ࡮ࡷࡷࡘࡻ࡭࡮ࡣࡵࡽࠧᇸ"), None)
        if not bstack1ll11ll1l11_opy_:
            self.logger.debug(bstack1111l1_opy_ (u"ࠤࡰ࡭ࡸࡹࡩ࡯ࡩࠣࠫ࡬࡫ࡴࡓࡧࡶࡹࡱࡺࡳࡔࡷࡰࡱࡦࡸࡹࠨࠢࡶࡧࡷ࡯ࡰࡵࠢࡩࡳࡷࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫࠽ࠣᇹ") + str(framework_name) + bstack1111l1_opy_ (u"ࠥࠦᇺ"))
            return
        self.perform_scan(driver, method=None, framework_name=framework_name)
        bstack1lll11l11_opy_ = datetime.now()
        if framework_name == bstack1111l1_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨᇻ"):
            result = self.bstack1ll11l11l11_opy_.bstack1ll1111l11l_opy_(driver, bstack1ll11ll1l11_opy_)
        else:
            result = driver.execute_async_script(bstack1ll11ll1l11_opy_)
        instance = bstack1lllll11l11_opy_.bstack1llll1l1lll_opy_(driver)
        if instance:
            instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠧࡧ࠱࠲ࡻ࠽࡫ࡪࡺ࡟ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿ࡟ࡳࡧࡶࡹࡱࡺࡳࡠࡵࡸࡱࡲࡧࡲࡺࠤᇼ"), datetime.now() - bstack1lll11l11_opy_)
        return result
    @measure(event_name=EVENTS.bstack1ll11lll111_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def bstack1ll11111lll_opy_(
        self,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str,
    ):
        self.bstack1ll11111l1l_opy_()
        req = structs.AccessibilityConfigRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        try:
            r = self.bstack1lll1l1lll1_opy_.AccessibilityConfig(req)
            if not r.success:
                self.logger.debug(bstack1111l1_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࠣᇽ") + str(r) + bstack1111l1_opy_ (u"ࠢࠣᇾ"))
            else:
                self.bstack1ll11l11l1l_opy_(framework_name, r)
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨᇿ") + str(e) + bstack1111l1_opy_ (u"ࠤࠥሀ"))
            traceback.print_exc()
            raise e
    def bstack1ll11l11l1l_opy_(self, framework_name: str, result: structs.AccessibilityConfigResponse) -> bool:
        if not result.success or not result.accessibility.success:
            self.logger.debug(bstack1111l1_opy_ (u"ࠥࡰࡴࡧࡤࡠࡥࡲࡲ࡫࡯ࡧ࠻ࠢࡤ࠵࠶ࡿࠠ࡯ࡱࡷࠤ࡫ࡵࡵ࡯ࡦࠥሁ"))
            return False
        if result.accessibility.is_app_accessibility:
            self.bstack1ll111l11l1_opy_ = result.accessibility.is_app_accessibility
        if result.testhub.build_hashed_id:
            self.bstack1ll11llll11_opy_[bstack1111l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡪࡸࡦࡤࡨࡵࡪ࡮ࡧࡣࡺࡻࡩࡥࠤሂ")] = result.testhub.build_hashed_id
        if result.testhub.jwt:
            self.bstack1ll11llll11_opy_[bstack1111l1_opy_ (u"ࠧࡺࡨࡠ࡬ࡺࡸࡤࡺ࡯࡬ࡧࡱࠦሃ")] = result.testhub.jwt
        if result.accessibility.options:
            options = result.accessibility.options
            if options.capabilities:
                for caps in options.capabilities:
                    self.bstack1ll11llll11_opy_[caps.name] = caps.value
            if options.scripts:
                self.scripts[framework_name] = {row.name: row.command for row in options.scripts}
            if options.commands_to_wrap and options.commands_to_wrap.commands:
                scripts_to_run = [s for s in options.commands_to_wrap.scripts_to_run]
                if not scripts_to_run:
                    return False
                bstack1ll11111ll1_opy_ = dict()
                for command in options.commands_to_wrap.commands:
                    if command.library == self.bstack1ll1l11111l_opy_ and command.module == self.bstack1ll1l111111_opy_:
                        if command.method and not command.method in bstack1ll11111ll1_opy_:
                            bstack1ll11111ll1_opy_[command.method] = dict()
                        if command.name and not command.name in bstack1ll11111ll1_opy_[command.method]:
                            bstack1ll11111ll1_opy_[command.method][command.name] = list()
                        bstack1ll11111ll1_opy_[command.method][command.name].extend(scripts_to_run)
                self.commands[framework_name] = bstack1ll11111ll1_opy_
        return bool(self.commands.get(framework_name, None))
    def bstack1ll11l11111_opy_(
        self,
        f: bstack1lll111l1l1_opy_,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if isinstance(self.bstack1ll11l11l11_opy_, bstack1ll1ll1llll_opy_) and method_name != bstack1111l1_opy_ (u"࠭ࡣࡰࡰࡱࡩࡨࡺࠧሄ"):
            return
        if bstack1lllll11l11_opy_.bstack1llll1l1ll1_opy_(instance, bstack1lll111l111_opy_.bstack1ll111l1111_opy_):
            return
        if f.bstack1ll11l1ll11_opy_(method_name, *args):
            bstack1ll11l11lll_opy_ = False
            desired_capabilities = f.bstack1ll11l1ll1l_opy_(instance)
            if isinstance(desired_capabilities, dict):
                hub_url = f.bstack1ll11lll1l1_opy_(instance)
                platform_index = f.bstack1lllll111l1_opy_(instance, bstack1lll111l1l1_opy_.bstack1ll11l11ll1_opy_, 0)
                bstack1ll111l1ll1_opy_ = datetime.now()
                r = self.bstack1ll11111lll_opy_(platform_index, f.framework_name, f.framework_version, hub_url)
                instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࡤࡩ࡯࡯ࡨ࡬࡫ࠧህ"), datetime.now() - bstack1ll111l1ll1_opy_)
                bstack1ll11l11lll_opy_ = r.success
            else:
                self.logger.error(bstack1111l1_opy_ (u"ࠣ࡯࡬ࡷࡸ࡯࡮ࡨࠢࡧࡩࡸ࡯ࡲࡦࡦࠣࡧࡦࡶࡡࡣ࡫࡯࡭ࡹ࡯ࡥࡴ࠿ࠥሆ") + str(desired_capabilities) + bstack1111l1_opy_ (u"ࠤࠥሇ"))
            f.bstack1lllll1l1l1_opy_(instance, bstack1lll111l111_opy_.bstack1ll111l1111_opy_, bstack1ll11l11lll_opy_)
    def bstack11l1ll111l_opy_(self, test_tags):
        bstack1ll11111lll_opy_ = self.config.get(bstack1111l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪለ"))
        if not bstack1ll11111lll_opy_:
            return True
        try:
            include_tags = bstack1ll11111lll_opy_[bstack1111l1_opy_ (u"ࠫ࡮ࡴࡣ࡭ࡷࡧࡩ࡙ࡧࡧࡴࡋࡱࡘࡪࡹࡴࡪࡰࡪࡗࡨࡵࡰࡦࠩሉ")] if bstack1111l1_opy_ (u"ࠬ࡯࡮ࡤ࡮ࡸࡨࡪ࡚ࡡࡨࡵࡌࡲ࡙࡫ࡳࡵ࡫ࡱ࡫ࡘࡩ࡯ࡱࡧࠪሊ") in bstack1ll11111lll_opy_ and isinstance(bstack1ll11111lll_opy_[bstack1111l1_opy_ (u"࠭ࡩ࡯ࡥ࡯ࡹࡩ࡫ࡔࡢࡩࡶࡍࡳ࡚ࡥࡴࡶ࡬ࡲ࡬࡙ࡣࡰࡲࡨࠫላ")], list) else []
            exclude_tags = bstack1ll11111lll_opy_[bstack1111l1_opy_ (u"ࠧࡦࡺࡦࡰࡺࡪࡥࡕࡣࡪࡷࡎࡴࡔࡦࡵࡷ࡭ࡳ࡭ࡓࡤࡱࡳࡩࠬሌ")] if bstack1111l1_opy_ (u"ࠨࡧࡻࡧࡱࡻࡤࡦࡖࡤ࡫ࡸࡏ࡮ࡕࡧࡶࡸ࡮ࡴࡧࡔࡥࡲࡴࡪ࠭ል") in bstack1ll11111lll_opy_ and isinstance(bstack1ll11111lll_opy_[bstack1111l1_opy_ (u"ࠩࡨࡼࡨࡲࡵࡥࡧࡗࡥ࡬ࡹࡉ࡯ࡖࡨࡷࡹ࡯࡮ࡨࡕࡦࡳࡵ࡫ࠧሎ")], list) else []
            excluded = any(tag in exclude_tags for tag in test_tags)
            included = len(include_tags) == 0 or any(tag in include_tags for tag in test_tags)
            return not excluded and included
        except Exception as error:
            self.logger.debug(bstack1111l1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡸࡤࡰ࡮ࡪࡡࡵ࡫ࡱ࡫ࠥࡺࡥࡴࡶࠣࡧࡦࡹࡥࠡࡨࡲࡶࠥࡧࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡨࡥࡧࡱࡵࡩࠥࡹࡣࡢࡰࡱ࡭ࡳ࡭࠮ࠡࡇࡵࡶࡴࡸࠠ࠻ࠢࠥሏ") + str(error))
        return False
    def bstack11l111111l_opy_(self, caps):
        try:
            if self.bstack1ll111l11l1_opy_:
                bstack1ll1111ll1l_opy_ = caps.get(bstack1111l1_opy_ (u"ࠦࡵࡲࡡࡵࡨࡲࡶࡲࡔࡡ࡮ࡧࠥሐ"))
                if bstack1ll1111ll1l_opy_ is not None and str(bstack1ll1111ll1l_opy_).lower() == bstack1111l1_opy_ (u"ࠧࡧ࡮ࡥࡴࡲ࡭ࡩࠨሑ"):
                    bstack1ll11l1l1l1_opy_ = caps.get(bstack1111l1_opy_ (u"ࠨࡡࡱࡲ࡬ࡹࡲࡀࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠣሒ")) or caps.get(bstack1111l1_opy_ (u"ࠢࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠤሓ"))
                    if bstack1ll11l1l1l1_opy_ is not None and int(bstack1ll11l1l1l1_opy_) < 11:
                        self.logger.warning(bstack1111l1_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠥࡽࡩ࡭࡮ࠣࡶࡺࡴࠠࡰࡰ࡯ࡽࠥࡵ࡮ࠡࡃࡱࡨࡷࡵࡩࡥࠢ࠴࠵ࠥࡧ࡮ࡥࠢࡤࡦࡴࡼࡥ࠯ࠢࡆࡹࡷࡸࡥ࡯ࡶࠣࡴࡱࡧࡴࡧࡱࡵࡱࠥࡼࡥࡳࡵ࡬ࡳࡳࠦ࠽ࠣሔ") + str(bstack1ll11l1l1l1_opy_) + bstack1111l1_opy_ (u"ࠤࠥሕ"))
                        return False
                return True
            bstack1ll111111l1_opy_ = caps.get(bstack1111l1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠽ࡳࡵࡺࡩࡰࡰࡶࠫሖ"), {}).get(bstack1111l1_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨሗ"), caps.get(bstack1111l1_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬመ"), bstack1111l1_opy_ (u"࠭ࠧሙ")))
            if bstack1ll111111l1_opy_:
                self.logger.warning(bstack1111l1_opy_ (u"ࠢࡂࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࠠࡂࡷࡷࡳࡲࡧࡴࡪࡱࡱࠤࡼ࡯࡬࡭ࠢࡵࡹࡳࠦ࡯࡯࡮ࡼࠤࡴࡴࠠࡅࡧࡶ࡯ࡹࡵࡰࠡࡤࡵࡳࡼࡹࡥࡳࡵ࠱ࠦሚ"))
                return False
            browser = caps.get(bstack1111l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ማ"), bstack1111l1_opy_ (u"ࠩࠪሜ")).lower()
            if browser != bstack1111l1_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪም"):
                self.logger.warning(bstack1111l1_opy_ (u"ࠦࡆࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠡࡹ࡬ࡰࡱࠦࡲࡶࡰࠣࡳࡳࡲࡹࠡࡱࡱࠤࡈ࡮ࡲࡰ࡯ࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࡸ࠴ࠢሞ"))
                return False
            bstack1ll111ll11l_opy_ = bstack1ll11ll1111_opy_
            if not self.config.get(bstack1111l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧሟ")) or self.config.get(bstack1111l1_opy_ (u"࠭ࡴࡶࡴࡥࡳࡸࡩࡡ࡭ࡧࠪሠ")):
                bstack1ll111ll11l_opy_ = bstack1ll111l1l11_opy_
            browser_version = caps.get(bstack1111l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨሡ"))
            if not browser_version:
                browser_version = caps.get(bstack1111l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩሢ"), {}).get(bstack1111l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪሣ"), bstack1111l1_opy_ (u"ࠪࠫሤ"))
            if browser_version and browser_version != bstack1111l1_opy_ (u"ࠫࡱࡧࡴࡦࡵࡷࠫሥ") and int(browser_version.split(bstack1111l1_opy_ (u"ࠬ࠴ࠧሦ"))[0]) <= bstack1ll111ll11l_opy_:
                self.logger.warning(bstack1111l1_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡴࡸࡲࠥࡵ࡮࡭ࡻࠣࡳࡳࠦࡃࡩࡴࡲࡱࡪࠦࡢࡳࡱࡺࡷࡪࡸࠠࡷࡧࡵࡷ࡮ࡵ࡮ࠡࡩࡵࡩࡦࡺࡥࡳࠢࡷ࡬ࡦࡴࠠࠣሧ") + str(bstack1ll111ll11l_opy_) + bstack1111l1_opy_ (u"ࠢ࠯ࠤረ"))
                return False
            bstack1l1llllll1l_opy_ = caps.get(bstack1111l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩሩ"), {}).get(bstack1111l1_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩሪ"))
            if not bstack1l1llllll1l_opy_:
                bstack1l1llllll1l_opy_ = caps.get(bstack1111l1_opy_ (u"ࠪ࡫ࡴࡵࡧ࠻ࡥ࡫ࡶࡴࡳࡥࡐࡲࡷ࡭ࡴࡴࡳࠨራ"), {})
            if bstack1l1llllll1l_opy_ and bstack1111l1_opy_ (u"ࠫ࠲࠳ࡨࡦࡣࡧࡰࡪࡹࡳࠨሬ") in bstack1l1llllll1l_opy_.get(bstack1111l1_opy_ (u"ࠬࡧࡲࡨࡵࠪር"), []):
                self.logger.warning(bstack1111l1_opy_ (u"ࠨࡁࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾࠦࡁࡶࡶࡲࡱࡦࡺࡩࡰࡰࠣࡻ࡮ࡲ࡬ࠡࡰࡲࡸࠥࡸࡵ࡯ࠢࡲࡲࠥࡲࡥࡨࡣࡦࡽࠥ࡮ࡥࡢࡦ࡯ࡩࡸࡹࠠ࡮ࡱࡧࡩ࠳ࠦࡓࡸ࡫ࡷࡧ࡭ࠦࡴࡰࠢࡱࡩࡼࠦࡨࡦࡣࡧࡰࡪࡹࡳࠡ࡯ࡲࡨࡪࠦ࡯ࡳࠢࡤࡺࡴ࡯ࡤࠡࡷࡶ࡭ࡳ࡭ࠠࡩࡧࡤࡨࡱ࡫ࡳࡴࠢࡰࡳࡩ࡫࠮ࠣሮ"))
                return False
            return True
        except Exception as error:
            self.logger.debug(bstack1111l1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡶࡢ࡮࡬ࡨࡦࡺࡥࠡࡣ࠴࠵ࡾࠦࡳࡶࡲࡳࡳࡷࡺࠠ࠻ࠤሯ") + str(error))
            return False
    def bstack1ll11llllll_opy_(self, test_uuid: str, result: structs.FetchDriverExecuteParamsEventResponse):
        bstack1ll1111111l_opy_ = {
            bstack1111l1_opy_ (u"ࠨࡶ࡫ࡘࡪࡹࡴࡓࡷࡱ࡙ࡺ࡯ࡤࠨሰ"): test_uuid,
        }
        bstack1ll11lllll1_opy_ = {}
        if result.success:
            bstack1ll11lllll1_opy_ = json.loads(result.accessibility_execute_params)
        return bstack1ll111llll1_opy_(bstack1ll1111111l_opy_, bstack1ll11lllll1_opy_)
    def bstack1ll111ll1ll_opy_(self, script_name: str, test_uuid: str) -> dict:
        bstack1111l1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࠣࠤࠥࠦࡆࡦࡶࡦ࡬ࠥࡩࡥ࡯ࡶࡵࡥࡱࠦࡡࡶࡶ࡫ࠤࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࡫ࡵࡲࠡࡶ࡫ࡩࠥ࡭ࡩࡷࡧࡱࠤࡸࡩࡲࡪࡲࡷࠤࡳࡧ࡭ࡦ࠰ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡗ࡫ࡴࡶࡴࡱࡷࠥࡩࡡࡤࡪࡨࡨࠥࡩ࡯࡯ࡨ࡬࡫ࠥ࡯ࡦࠡࡣ࡯ࡶࡪࡧࡤࡺࠢࡩࡩࡹࡩࡨࡦࡦ࠯ࠤࡴࡺࡨࡦࡴࡺ࡭ࡸ࡫ࠠ࡭ࡱࡤࡨࡸࠦࡡ࡯ࡦࠣࡧࡦࡩࡨࡦࡵࠣ࡭ࡹ࠴ࠊࠡࠢࠣࠤࠥࠦࠠࠡࡃࡵ࡫ࡸࡀࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࡹࡣࡳ࡫ࡳࡸࡤࡴࡡ࡮ࡧ࠽ࠤࡓࡧ࡭ࡦࠢࡲࡪࠥࡺࡨࡦࠢࡶࡧࡷ࡯ࡰࡵࠢࡷࡳࠥ࡬ࡥࡵࡥ࡫ࠤࡨࡵ࡮ࡧ࡫ࡪࠤ࡫ࡵࡲࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡴࡦࡵࡷࡣࡺࡻࡩࡥ࠼࡙࡚ࠣࡏࡄࠡࡱࡩࠤࡹ࡮ࡥࠡࡶࡨࡷࡹࠦࡲࡶࡰࠣࡪࡴࡸࠠࡸࡪ࡬ࡧ࡭ࠦࡴࡰࠢࡩࡩࡹࡩࡨࠡࡥࡲࡲ࡫࡯ࡧࠋࠢࠣࠤࠥࠦࠠࠡࠢࡕࡩࡹࡻࡲ࡯ࡵ࠽ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࡧ࡭ࡨࡺ࠺ࠡࡅࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠡࡦ࡬ࡧࡹ࡯࡯࡯ࡣࡵࡽ࠱ࠦࡥ࡮ࡲࡷࡽࠥࡪࡩࡤࡶࠣ࡭࡫ࠦࡥࡳࡴࡲࡶࠥࡵࡣࡤࡷࡵࡷࠏࠦࠠࠡࠢࠣࠤࠥࠦࠢࠣࠤሱ")
        try:
            if self.bstack1ll11ll1l1l_opy_:
                return self.bstack1ll111lllll_opy_
            self.bstack1ll11111l1l_opy_()
            req = structs.FetchDriverExecuteParamsEventRequest()
            req.bin_session_id = self.bin_session_id
            req.product = bstack1111l1_opy_ (u"ࠥࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࠥሲ")
            req.script_name = script_name
            r = self.bstack1lll1l1lll1_opy_.FetchDriverExecuteParamsEvent(req)
            if r.success:
                self.bstack1ll111lllll_opy_ = self.bstack1ll11llllll_opy_(test_uuid, r)
                self.bstack1ll11ll1l1l_opy_ = True
            else:
                self.logger.error(bstack1111l1_opy_ (u"ࠦ࡫࡫ࡴࡤࡪࡆࡩࡳࡺࡲࡢ࡮ࡄࡹࡹ࡮ࡁ࠲࠳ࡼࡇࡴࡴࡦࡪࡩ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡧࡧࡷࡧ࡭ࠦࡤࡳ࡫ࡹࡩࡷࠦࡥࡹࡧࡦࡹࡹ࡫ࠠࡱࡣࡵࡥࡲࡹࠠࡧࡱࡵࠤࢀࡹࡣࡳ࡫ࡳࡸࡤࡴࡡ࡮ࡧࢀ࠾ࠥࠨሳ") + str(r.error) + bstack1111l1_opy_ (u"ࠧࠨሴ"))
                self.bstack1ll111lllll_opy_ = dict()
            return self.bstack1ll111lllll_opy_
        except Exception as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠨࡦࡦࡶࡦ࡬ࡈ࡫࡮ࡵࡴࡤࡰࡆࡻࡴࡩࡃ࠴࠵ࡾࡉ࡯࡯ࡨ࡬࡫࠿ࠦࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡩࡩࡹࡩࡨࠡࡦࡵ࡭ࡻ࡫ࡲࠡࡧࡻࡩࡨࡻࡴࡦࠢࡳࡥࡷࡧ࡭ࡴࠢࡩࡳࡷࠦࡻࡴࡥࡵ࡭ࡵࡺ࡟࡯ࡣࡰࡩࢂࡀࠠࠣስ") + str(traceback.format_exc()) + bstack1111l1_opy_ (u"ࠢࠣሶ"))
            return dict()
    def bstack1ll11llll1_opy_(self, driver: object, name: str, framework_name: str, test_uuid: str):
        bstack1ll11l111ll_opy_ = None
        try:
            self.bstack1ll11111l1l_opy_()
            req = structs.FetchDriverExecuteParamsEventRequest()
            req.bin_session_id = self.bin_session_id
            req.product = bstack1111l1_opy_ (u"ࠣࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠣሷ")
            req.script_name = bstack1111l1_opy_ (u"ࠤࡶࡥࡻ࡫ࡒࡦࡵࡸࡰࡹࡹࠢሸ")
            r = self.bstack1lll1l1lll1_opy_.FetchDriverExecuteParamsEvent(req)
            if not r.success:
                self.logger.debug(bstack1111l1_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥࡪࡲࡪࡸࡨࡶࠥ࡫ࡸࡦࡥࡸࡸࡪࠦࡰࡢࡴࡤࡱࡸࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࠨሹ") + str(r.error) + bstack1111l1_opy_ (u"ࠦࠧሺ"))
            else:
                bstack1ll1111111l_opy_ = self.bstack1ll11llllll_opy_(test_uuid, r)
                bstack1ll11ll1l11_opy_ = r.script
            self.logger.debug(bstack1111l1_opy_ (u"ࠬࡖࡥࡳࡨࡲࡶࡲ࡯࡮ࡨࠢࡶࡧࡦࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡴࡣࡹ࡭ࡳ࡭ࠠࡳࡧࡶࡹࡱࡺࡳࠨሻ") + str(bstack1ll1111111l_opy_))
            self.perform_scan(driver, name, framework_name=framework_name)
            if not bstack1ll11ll1l11_opy_:
                self.logger.debug(bstack1111l1_opy_ (u"ࠨࡰࡦࡴࡩࡳࡷࡳ࡟ࡴࡥࡤࡲ࠿ࠦ࡭ࡪࡵࡶ࡭ࡳ࡭ࠠࠨࡵࡤࡺࡪࡘࡥࡴࡷ࡯ࡸࡸ࠭ࠠࡴࡥࡵ࡭ࡵࡺࠠࡧࡱࡵࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟࡯ࡣࡰࡩࡂࠨሼ") + str(framework_name) + bstack1111l1_opy_ (u"ࠢࠡࠤሽ"))
                return
            bstack1ll11l111ll_opy_ = bstack1llll11l111_opy_.bstack1ll11ll11l1_opy_(EVENTS.bstack1ll111l11ll_opy_.value)
            self.bstack1ll11l1lll1_opy_(driver, bstack1ll11ll1l11_opy_, bstack1ll1111111l_opy_, framework_name)
            self.logger.info(bstack1111l1_opy_ (u"ࠣࡃࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࠡࡶࡨࡷࡹ࡯࡮ࡨࠢࡩࡳࡷࠦࡴࡩ࡫ࡶࠤࡹ࡫ࡳࡵࠢࡦࡥࡸ࡫ࠠࡩࡣࡶࠤࡪࡴࡤࡦࡦ࠱ࠦሾ"))
            bstack1llll11l111_opy_.end(EVENTS.bstack1ll111l11ll_opy_.value, bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠤ࠽ࡷࡹࡧࡲࡵࠤሿ"), bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠥ࠾ࡪࡴࡤࠣቀ"), True, None, command=bstack1111l1_opy_ (u"ࠫࡸࡧࡶࡦࡔࡨࡷࡺࡲࡴࡴࠩቁ"),test_name=name)
        except Exception as bstack1ll11ll1ll1_opy_:
            self.logger.error(bstack1111l1_opy_ (u"ࠧࡇࡣࡤࡧࡶࡷ࡮ࡨࡩ࡭࡫ࡷࡽࠥࡸࡥࡴࡷ࡯ࡸࡸࠦࡣࡰࡷ࡯ࡨࠥࡴ࡯ࡵࠢࡥࡩࠥࡶࡲࡰࡥࡨࡷࡸ࡫ࡤࠡࡨࡲࡶࠥࡺࡨࡦࠢࡷࡩࡸࡺࠠࡤࡣࡶࡩ࠿ࠦࠢቂ") + bstack1111l1_opy_ (u"ࠨࡳࡵࡴࠫࡴࡦࡺࡨࠪࠤቃ") + bstack1111l1_opy_ (u"ࠢࠡࡇࡵࡶࡴࡸࠠ࠻ࠤቄ") + str(bstack1ll11ll1ll1_opy_))
            bstack1llll11l111_opy_.end(EVENTS.bstack1ll111l11ll_opy_.value, bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠣ࠼ࡶࡸࡦࡸࡴࠣቅ"), bstack1ll11l111ll_opy_+bstack1111l1_opy_ (u"ࠤ࠽ࡩࡳࡪࠢቆ"), False, bstack1ll11ll1ll1_opy_, command=bstack1111l1_opy_ (u"ࠪࡷࡦࡼࡥࡓࡧࡶࡹࡱࡺࡳࠨቇ"),test_name=name)
    def bstack1ll11l1lll1_opy_(self, driver, bstack1ll11ll1l11_opy_, bstack1ll1111111l_opy_, framework_name):
        if framework_name == bstack1111l1_opy_ (u"ࠫࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠨቈ"):
            self.bstack1ll11l11l11_opy_.bstack1ll1111l11l_opy_(driver, bstack1ll11ll1l11_opy_, bstack1ll1111111l_opy_)
        else:
            self.logger.debug(driver.execute_async_script(bstack1ll11ll1l11_opy_, bstack1ll1111111l_opy_))
    def _1ll11ll11ll_opy_(self, instance: bstack1ll1llll1l1_opy_, args: Tuple) -> list:
        bstack1111l1_opy_ (u"ࠧࠨࠢࡆࡺࡷࡶࡦࡩࡴࠡࡶࡤ࡫ࡸࠦࡢࡢࡵࡨࡨࠥࡵ࡮ࠡࡶ࡫ࡩࠥࡺࡥࡴࡶࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠴ࠢࠣࠤ቉")
        if bstack1111l1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠪቊ") in instance.bstack1ll11lll11l_opy_:
            return args[2].tags if hasattr(args[2], bstack1111l1_opy_ (u"ࠧࡵࡣࡪࡷࠬቋ")) else []
        if hasattr(args[0], bstack1111l1_opy_ (u"ࠨࡱࡺࡲࡤࡳࡡࡳ࡭ࡨࡶࡸ࠭ቌ")):
            return [marker.name for marker in args[0].own_markers]
        return []
    def bstack1ll11ll1lll_opy_(self, tags, capabilities):
        return self.bstack11l1ll111l_opy_(tags) and self.bstack11l111111l_opy_(capabilities)