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
import os
import grpc
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1ll1l1l1111_opy_ import bstack1lll1111lll_opy_
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll1ll11l_opy_,
    bstack1lllll11111_opy_,
    bstack1llll1l11l1_opy_,
)
from browserstack_sdk.sdk_cli.bstack1lll1ll1111_opy_ import bstack1lll111l1l1_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack11l1l1ll11_opy_
from bstack_utils.measure import measure
from bstack_utils.constants import *
import threading
import os
from bstack_utils.bstack1llll1llll_opy_ import bstack1llll11l111_opy_
class bstack1lll111l11l_opy_(bstack1lll1111lll_opy_):
    bstack1l11ll1111l_opy_ = bstack1111l1_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡩ࡯࡫ࡷࠦ᎑")
    bstack1l11ll11l1l_opy_ = bstack1111l1_opy_ (u"ࠧࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡤࡶࡹࠨ᎒")
    bstack1l11ll111ll_opy_ = bstack1111l1_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࠨ᎓")
    def __init__(self, bstack1ll1l11ll11_opy_):
        super().__init__()
        bstack1lll111l1l1_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.bstack1llllll1l11_opy_, bstack1lllll11111_opy_.PRE), self.bstack1l11ll11l11_opy_)
        bstack1lll111l1l1_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.bstack1lllll111ll_opy_, bstack1lllll11111_opy_.PRE), self.bstack1l1llll11ll_opy_)
        bstack1lll111l1l1_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.bstack1lllll111ll_opy_, bstack1lllll11111_opy_.POST), self.bstack1l11ll11lll_opy_)
        bstack1lll111l1l1_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.bstack1lllll111ll_opy_, bstack1lllll11111_opy_.POST), self.bstack1l11l1l11ll_opy_)
        bstack1lll111l1l1_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.QUIT, bstack1lllll11111_opy_.POST), self.bstack1l11ll11111_opy_)
    def is_enabled(self) -> bool:
        return True
    def bstack1l11ll11l11_opy_(
        self,
        f: bstack1lll111l1l1_opy_,
        driver: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1111l1_opy_ (u"ࠢࡠࡡ࡬ࡲ࡮ࡺ࡟ࡠࠤ᎔"):
            return
        def wrapped(driver, init, *args, **kwargs):
            url = None
            try:
                if isinstance(kwargs.get(bstack1111l1_opy_ (u"ࠣࡥࡲࡱࡲࡧ࡮ࡥࡡࡨࡼࡪࡩࡵࡵࡱࡵࠦ᎕")), str):
                    url = kwargs.get(bstack1111l1_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࡢࡩࡽ࡫ࡣࡶࡶࡲࡶࠧ᎖"))
                elif hasattr(kwargs.get(bstack1111l1_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡣࡪࡾࡥࡤࡷࡷࡳࡷࠨ᎗")), bstack1111l1_opy_ (u"ࠫࡤࡩ࡬ࡪࡧࡱࡸࡤࡩ࡯࡯ࡨ࡬࡫ࠬ᎘")):
                    url = kwargs.get(bstack1111l1_opy_ (u"ࠧࡩ࡯࡮࡯ࡤࡲࡩࡥࡥࡹࡧࡦࡹࡹࡵࡲࠣ᎙"))._client_config.remote_server_addr
                else:
                    url = kwargs.get(bstack1111l1_opy_ (u"ࠨࡣࡰ࡯ࡰࡥࡳࡪ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳࠤ᎚"))._url
            except Exception as e:
                url = bstack1111l1_opy_ (u"ࠧࠨ᎛")
                self.logger.error(bstack1111l1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡧࡦࡶࡷ࡭ࡳ࡭ࠠࡶࡴ࡯ࠤ࡫ࡸ࡯࡮ࠢࡧࡶ࡮ࡼࡥࡳ࠼ࠣࡿࢂࠨ᎜").format(e))
            self.logger.info(bstack1111l1_opy_ (u"ࠤࡕࡩࡲࡵࡴࡦࠢࡖࡩࡷࡼࡥࡳࠢࡄࡨࡩࡸࡥࡴࡵࠣࡦࡪ࡯࡮ࡨࠢࡳࡥࡸࡹࡥࡥࠢࡤࡷࠥࡀࠠࡼࡿࠥ᎝").format(str(url)))
            self.bstack1l11l1lll1l_opy_(instance, url, f, kwargs)
            self.logger.info(bstack1111l1_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴ࠱ࡿࡲ࡫ࡴࡩࡱࡧࡣࡳࡧ࡭ࡦࡿࠣࡴࡱࡧࡴࡧࡱࡵࡱࡤ࡯࡮ࡥࡧࡻࡁࢀࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࢃ࠺ࠡࡣࡵ࡫ࡸࡃࡻࡢࡴࡪࡷࢂࠦ࡫ࡸࡣࡵ࡫ࡸࡃࡻ࡬ࡹࡤࡶ࡬ࡹࡽࠣ᎞").format(method_name=method_name, platform_index=f.platform_index, args=args, kwargs=kwargs))
            threading.current_thread().bstackSessionDriver = driver
            return init(driver, *args, **kwargs)
        return wrapped
    def bstack1l1llll11ll_opy_(
        self,
        f: bstack1lll111l1l1_opy_,
        driver: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if f.bstack1lllll111l1_opy_(instance, bstack1lll111l11l_opy_.bstack1l11ll1111l_opy_, False):
            return
        if not f.bstack1llll1l1ll1_opy_(instance, bstack1lll111l1l1_opy_.bstack1ll11l11ll1_opy_):
            return
        platform_index = f.bstack1lllll111l1_opy_(instance, bstack1lll111l1l1_opy_.bstack1ll11l11ll1_opy_)
        if f.bstack1ll11l1ll11_opy_(method_name, *args) and len(args) > 1:
            bstack1lll11l11_opy_ = datetime.now()
            hub_url = bstack1lll111l1l1_opy_.hub_url(driver)
            self.logger.warning(bstack1111l1_opy_ (u"ࠦ࡭ࡻࡢࡠࡷࡵࡰࡂࠨ᎟") + str(hub_url) + bstack1111l1_opy_ (u"ࠧࠨᎠ"))
            bstack1l11l1l11l1_opy_ = args[1][bstack1111l1_opy_ (u"ࠨࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᎡ")] if isinstance(args[1], dict) and bstack1111l1_opy_ (u"ࠢࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᎢ") in args[1] else None
            bstack1l11l1l1ll1_opy_ = bstack1111l1_opy_ (u"ࠣࡣ࡯ࡻࡦࡿࡳࡎࡣࡷࡧ࡭ࠨᎣ")
            if isinstance(bstack1l11l1l11l1_opy_, dict):
                bstack1lll11l11_opy_ = datetime.now()
                r = self.bstack1l11l1lllll_opy_(
                    instance.ref(),
                    platform_index,
                    f.framework_name,
                    f.framework_version,
                    hub_url
                )
                instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠤࡪࡶࡵࡩ࠺ࡳࡧࡪ࡭ࡸࡺࡥࡳࡡ࡬ࡲ࡮ࡺࠢᎤ"), datetime.now() - bstack1lll11l11_opy_)
                try:
                    if not r.success:
                        self.logger.info(bstack1111l1_opy_ (u"ࠥࡷࡴࡳࡥࡵࡪ࡬ࡲ࡬ࠦࡷࡦࡰࡷࠤࡼࡸ࡯࡯ࡩ࠽ࠤࠧᎥ") + str(r) + bstack1111l1_opy_ (u"ࠦࠧᎦ"))
                        return
                    if r.hub_url:
                        f.bstack1l11ll1l1l1_opy_(instance, driver, r.hub_url)
                        f.bstack1lllll1l1l1_opy_(instance, bstack1lll111l11l_opy_.bstack1l11ll1111l_opy_, True)
                except Exception as e:
                    self.logger.error(bstack1111l1_opy_ (u"ࠧ࡫ࡲࡳࡱࡵࠦᎧ"), e)
    def bstack1l11ll11lll_opy_(
        self,
        f: bstack1lll111l1l1_opy_,
        driver: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
            session_id = bstack1lll111l1l1_opy_.session_id(driver)
            if session_id:
                bstack1l11ll11ll1_opy_ = bstack1111l1_opy_ (u"ࠨࡻࡾ࠼ࡶࡸࡦࡸࡴࠣᎨ").format(session_id)
                bstack1llll11l111_opy_.mark(bstack1l11ll11ll1_opy_)
    def bstack1l11l1l11ll_opy_(
        self,
        f: bstack1lll111l1l1_opy_,
        driver: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if f.bstack1lllll111l1_opy_(instance, bstack1lll111l11l_opy_.bstack1l11ll11l1l_opy_, False):
            return
        ref = instance.ref()
        hub_url = bstack1lll111l1l1_opy_.hub_url(driver)
        if not hub_url:
            self.logger.warning(bstack1111l1_opy_ (u"ࠢࡧࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡴࡦࡸࡳࡦࠢ࡫ࡹࡧࡥࡵࡳ࡮ࡀࠦᎩ") + str(hub_url) + bstack1111l1_opy_ (u"ࠣࠤᎪ"))
            return
        framework_session_id = bstack1lll111l1l1_opy_.session_id(driver)
        if not framework_session_id:
            self.logger.warning(bstack1111l1_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡶࡡࡳࡵࡨࠤ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡴࡧࡶࡷ࡮ࡵ࡮ࡠ࡫ࡧࡁࠧᎫ") + str(framework_session_id) + bstack1111l1_opy_ (u"ࠥࠦᎬ"))
            return
        if bstack1lll111l1l1_opy_.bstack1l11l1l1l1l_opy_(*args) == bstack1lll111l1l1_opy_.bstack1l11l11llll_opy_:
            bstack1l11ll1l11l_opy_ = bstack1111l1_opy_ (u"ࠦࢀࢃ࠺ࡦࡰࡧࠦᎭ").format(framework_session_id)
            bstack1l11ll11ll1_opy_ = bstack1111l1_opy_ (u"ࠧࢁࡽ࠻ࡵࡷࡥࡷࡺࠢᎮ").format(framework_session_id)
            bstack1llll11l111_opy_.end(
                label=bstack1111l1_opy_ (u"ࠨࡳࡥ࡭࠽ࡨࡷ࡯ࡶࡦࡴ࠽ࡴࡴࡹࡴ࠮࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡥࡹ࡯࡯࡯ࠤᎯ"),
                start=bstack1l11ll11ll1_opy_,
                end=bstack1l11ll1l11l_opy_,
                status=True,
                failure=None
            )
            bstack1lll11l11_opy_ = datetime.now()
            r = self.bstack1l11l1ll11l_opy_(
                ref,
                f.bstack1lllll111l1_opy_(instance, bstack1lll111l1l1_opy_.bstack1ll11l11ll1_opy_, 0),
                f.framework_name,
                f.framework_version,
                framework_session_id,
                hub_url,
            )
            instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠢࡨࡴࡳࡧ࠿ࡸࡥࡨ࡫ࡶࡸࡪࡸ࡟ࡴࡶࡤࡶࡹࠨᎰ"), datetime.now() - bstack1lll11l11_opy_)
            f.bstack1lllll1l1l1_opy_(instance, bstack1lll111l11l_opy_.bstack1l11ll11l1l_opy_, r.success)
    def bstack1l11ll11111_opy_(
        self,
        f: bstack1lll111l1l1_opy_,
        driver: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance = exec[0]
        if f.bstack1lllll111l1_opy_(instance, bstack1lll111l11l_opy_.bstack1l11ll111ll_opy_, False):
            return
        ref = instance.ref()
        framework_session_id = bstack1lll111l1l1_opy_.session_id(driver)
        hub_url = bstack1lll111l1l1_opy_.hub_url(driver)
        bstack1lll11l11_opy_ = datetime.now()
        r = self.bstack1l11l1l1l11_opy_(
            ref,
            f.bstack1lllll111l1_opy_(instance, bstack1lll111l1l1_opy_.bstack1ll11l11ll1_opy_, 0),
            f.framework_name,
            f.framework_version,
            framework_session_id,
            hub_url,
        )
        instance.bstack1l11ll1l11_opy_(bstack1111l1_opy_ (u"ࠣࡩࡵࡴࡨࡀࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࠨᎱ"), datetime.now() - bstack1lll11l11_opy_)
        f.bstack1lllll1l1l1_opy_(instance, bstack1lll111l11l_opy_.bstack1l11ll111ll_opy_, r.success)
    @measure(event_name=EVENTS.bstack1lll1ll1l_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def bstack1l11lllll1l_opy_(self, platform_index: int, url: str, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        req.hub_url = url
        self.logger.debug(bstack1111l1_opy_ (u"ࠤࡵࡩ࡬࡯ࡳࡵࡧࡵࡣࡼ࡫ࡢࡥࡴ࡬ࡺࡪࡸ࡟ࡪࡰ࡬ࡸ࠿ࠦࠢᎲ") + str(req) + bstack1111l1_opy_ (u"ࠥࠦᎳ"))
        try:
            r = self.bstack1lll1l1lll1_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack1111l1_opy_ (u"ࠦࡷ࡫ࡣࡦ࡫ࡹࡩࡩࠦࡦࡳࡱࡰࠤࡸ࡫ࡲࡷࡧࡵ࠾ࠥࡹࡵࡤࡥࡨࡷࡸࡃࠢᎴ") + str(r.success) + bstack1111l1_opy_ (u"ࠧࠨᎵ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠨࡲࡱࡥ࠰ࡩࡷࡸ࡯ࡳ࠼ࠣࠦᎶ") + str(e) + bstack1111l1_opy_ (u"ࠢࠣᎷ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11ll1l111_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def bstack1l11l1lllll_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        hub_url: str
    ):
        self.bstack1ll11111l1l_opy_()
        req = structs.AutomationFrameworkInitRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.hub_url = hub_url
        self.logger.debug(bstack1111l1_opy_ (u"ࠣࡴࡨ࡫࡮ࡹࡴࡦࡴࡢ࡭ࡳ࡯ࡴ࠻ࠢࠥᎸ") + str(req) + bstack1111l1_opy_ (u"ࠤࠥᎹ"))
        try:
            r = self.bstack1lll1l1lll1_opy_.AutomationFrameworkInit(req)
            if not r.success:
                self.logger.debug(bstack1111l1_opy_ (u"ࠥࡶࡪࡩࡥࡪࡸࡨࡨࠥ࡬ࡲࡰ࡯ࠣࡷࡪࡸࡶࡦࡴ࠽ࠤࡸࡻࡣࡤࡧࡶࡷࡂࠨᎺ") + str(r.success) + bstack1111l1_opy_ (u"ࠦࠧᎻ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠧࡸࡰࡤ࠯ࡨࡶࡷࡵࡲ࠻ࠢࠥᎼ") + str(e) + bstack1111l1_opy_ (u"ࠨࠢᎽ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l1ll1ll_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def bstack1l11l1ll11l_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll11111l1l_opy_()
        req = structs.AutomationFrameworkStartRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack1111l1_opy_ (u"ࠢࡳࡧࡪ࡭ࡸࡺࡥࡳࡡࡶࡸࡦࡸࡴ࠻ࠢࠥᎾ") + str(req) + bstack1111l1_opy_ (u"ࠣࠤᎿ"))
        try:
            r = self.bstack1lll1l1lll1_opy_.AutomationFrameworkStart(req)
            if not r.success:
                self.logger.debug(bstack1111l1_opy_ (u"ࠤࡵࡩࡨ࡫ࡩࡷࡧࡧࠤ࡫ࡸ࡯࡮ࠢࡶࡩࡷࡼࡥࡳ࠼ࠣࠦᏀ") + str(r) + bstack1111l1_opy_ (u"ࠥࠦᏁ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠦࡷࡶࡣ࠮ࡧࡵࡶࡴࡸ࠺ࠡࠤᏂ") + str(e) + bstack1111l1_opy_ (u"ࠧࠨᏃ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack1l11l1ll111_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def bstack1l11l1l1l11_opy_(
        self,
        ref: str,
        platform_index: int,
        framework_name: str,
        framework_version: str,
        framework_session_id: str,
        hub_url: str,
    ):
        self.bstack1ll11111l1l_opy_()
        req = structs.AutomationFrameworkStopRequest()
        req.ref = ref
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.framework_name = framework_name
        req.framework_version = framework_version
        req.framework_session_id = framework_session_id
        req.hub_url = hub_url
        self.logger.debug(bstack1111l1_opy_ (u"ࠨࡲࡦࡩ࡬ࡷࡹ࡫ࡲࡠࡵࡷࡳࡵࡀࠠࠣᏄ") + str(req) + bstack1111l1_opy_ (u"ࠢࠣᏅ"))
        try:
            r = self.bstack1lll1l1lll1_opy_.AutomationFrameworkStop(req)
            if not r.success:
                self.logger.debug(bstack1111l1_opy_ (u"ࠣࡴࡨࡧࡪ࡯ࡶࡦࡦࠣࡪࡷࡵ࡭ࠡࡵࡨࡶࡻ࡫ࡲ࠻ࠢࠥᏆ") + str(r) + bstack1111l1_opy_ (u"ࠤࠥᏇ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠥࡶࡵࡩ࠭ࡦࡴࡵࡳࡷࡀࠠࠣᏈ") + str(e) + bstack1111l1_opy_ (u"ࠦࠧᏉ"))
            traceback.print_exc()
            raise e
    @measure(event_name=EVENTS.bstack11llll111_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
    def bstack1l11l1lll1l_opy_(self, instance: bstack1llll1l11l1_opy_, url: str, f: bstack1lll111l1l1_opy_, kwargs):
        bstack1l11l1ll1l1_opy_ = version.parse(f.framework_version)
        bstack1l11l1l1lll_opy_ = kwargs.get(bstack1111l1_opy_ (u"ࠧࡵࡰࡵ࡫ࡲࡲࡸࠨᏊ"))
        bstack1l11l1lll11_opy_ = kwargs.get(bstack1111l1_opy_ (u"ࠨࡤࡦࡵ࡬ࡶࡪࡪ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶ࡬ࡩࡸࠨᏋ"))
        bstack1l1l111l1ll_opy_ = {}
        bstack1l11ll111l1_opy_ = {}
        bstack1l11l1l111l_opy_ = None
        bstack1l11l1llll1_opy_ = {}
        if bstack1l11l1lll11_opy_ is not None or bstack1l11l1l1lll_opy_ is not None: # check top level caps
            if bstack1l11l1lll11_opy_ is not None:
                bstack1l11l1llll1_opy_[bstack1111l1_opy_ (u"ࠧࡥࡧࡶ࡭ࡷ࡫ࡤࡠࡥࡤࡴࡦࡨࡩ࡭࡫ࡷ࡭ࡪࡹࠧᏌ")] = bstack1l11l1lll11_opy_
            if bstack1l11l1l1lll_opy_ is not None and callable(getattr(bstack1l11l1l1lll_opy_, bstack1111l1_opy_ (u"ࠣࡶࡲࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᏍ"))):
                bstack1l11l1llll1_opy_[bstack1111l1_opy_ (u"ࠩࡲࡴࡹ࡯࡯࡯ࡵࡢࡥࡸࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠬᏎ")] = bstack1l11l1l1lll_opy_.to_capabilities()
        response = self.bstack1l11lllll1l_opy_(f.platform_index, url, instance.ref(), json.dumps(bstack1l11l1llll1_opy_).encode(bstack1111l1_opy_ (u"ࠥࡹࡹ࡬࠭࠹ࠤᏏ")))
        if response is not None and response.capabilities:
            bstack1l1l111l1ll_opy_ = json.loads(response.capabilities.decode(bstack1111l1_opy_ (u"ࠦࡺࡺࡦ࠮࠺ࠥᏐ")))
            if not bstack1l1l111l1ll_opy_: # empty caps bstack1l1l111lll1_opy_ bstack1l1l1111111_opy_ bstack1l1l111ll11_opy_ bstack1ll1lllll1l_opy_ or error in processing
                return
            bstack1l11l1l111l_opy_ = f.bstack1lll1111111_opy_[bstack1111l1_opy_ (u"ࠧࡩࡲࡦࡣࡷࡩࡤࡵࡰࡵ࡫ࡲࡲࡸࡥࡦࡳࡱࡰࡣࡨࡧࡰࡴࠤᏑ")](bstack1l1l111l1ll_opy_)
        if bstack1l11l1l1lll_opy_ is not None and bstack1l11l1ll1l1_opy_ >= version.parse(bstack1111l1_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬᏒ")):
            bstack1l11ll111l1_opy_ = None
        if (
                not bstack1l11l1l1lll_opy_ and not bstack1l11l1lll11_opy_
        ) or (
                bstack1l11l1ll1l1_opy_ < version.parse(bstack1111l1_opy_ (u"ࠧ࠴࠰࠻࠲࠵࠭Ꮣ"))
        ):
            bstack1l11ll111l1_opy_ = {}
            bstack1l11ll111l1_opy_.update(bstack1l1l111l1ll_opy_)
        self.logger.info(bstack11l1l1ll11_opy_)
        if os.environ.get(bstack1111l1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠦᏔ")).lower().__eq__(bstack1111l1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᏕ")):
            kwargs.update(
                {
                    bstack1111l1_opy_ (u"ࠥࡧࡴࡳ࡭ࡢࡰࡧࡣࡪࡾࡥࡤࡷࡷࡳࡷࠨᏖ"): f.bstack1l11l1l1111_opy_,
                }
            )
        if bstack1l11l1ll1l1_opy_ >= version.parse(bstack1111l1_opy_ (u"ࠫ࠹࠴࠱࠱࠰࠳ࠫᏗ")):
            if bstack1l11l1lll11_opy_ is not None:
                del kwargs[bstack1111l1_opy_ (u"ࠧࡪࡥࡴ࡫ࡵࡩࡩࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵ࡫ࡨࡷࠧᏘ")]
            kwargs.update(
                {
                    bstack1111l1_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡳࡳࡹࠢᏙ"): bstack1l11l1l111l_opy_,
                    bstack1111l1_opy_ (u"ࠢ࡬ࡧࡨࡴࡤࡧ࡬ࡪࡸࡨࠦᏚ"): True,
                    bstack1111l1_opy_ (u"ࠣࡨ࡬ࡰࡪࡥࡤࡦࡶࡨࡧࡹࡵࡲࠣᏛ"): None,
                }
            )
        elif bstack1l11l1ll1l1_opy_ >= version.parse(bstack1111l1_opy_ (u"ࠩ࠶࠲࠽࠴࠰ࠨᏜ")):
            kwargs.update(
                {
                    bstack1111l1_opy_ (u"ࠥࡨࡪࡹࡩࡳࡧࡧࡣࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡩࡦࡵࠥᏝ"): bstack1l11ll111l1_opy_,
                    bstack1111l1_opy_ (u"ࠦࡴࡶࡴࡪࡱࡱࡷࠧᏞ"): bstack1l11l1l111l_opy_,
                    bstack1111l1_opy_ (u"ࠧࡱࡥࡦࡲࡢࡥࡱ࡯ࡶࡦࠤᏟ"): True,
                    bstack1111l1_opy_ (u"ࠨࡦࡪ࡮ࡨࡣࡩ࡫ࡴࡦࡥࡷࡳࡷࠨᏠ"): None,
                }
            )
        elif bstack1l11l1ll1l1_opy_ >= version.parse(bstack1111l1_opy_ (u"ࠧ࠳࠰࠸࠷࠳࠶ࠧᏡ")):
            kwargs.update(
                {
                    bstack1111l1_opy_ (u"ࠣࡦࡨࡷ࡮ࡸࡥࡥࡡࡦࡥࡵࡧࡢࡪ࡮࡬ࡸ࡮࡫ࡳࠣᏢ"): bstack1l11ll111l1_opy_,
                    bstack1111l1_opy_ (u"ࠤ࡮ࡩࡪࡶ࡟ࡢ࡮࡬ࡺࡪࠨᏣ"): True,
                    bstack1111l1_opy_ (u"ࠥࡪ࡮ࡲࡥࡠࡦࡨࡸࡪࡩࡴࡰࡴࠥᏤ"): None,
                }
            )
        else:
            kwargs.update(
                {
                    bstack1111l1_opy_ (u"ࠦࡩ࡫ࡳࡪࡴࡨࡨࡤࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠦᏥ"): bstack1l11ll111l1_opy_,
                    bstack1111l1_opy_ (u"ࠧࡱࡥࡦࡲࡢࡥࡱ࡯ࡶࡦࠤᏦ"): True,
                    bstack1111l1_opy_ (u"ࠨࡦࡪ࡮ࡨࡣࡩ࡫ࡴࡦࡥࡷࡳࡷࠨᏧ"): None,
                }
            )