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
import copy
import asyncio
import threading
from browserstack_sdk import sdk_pb2 as structs
from packaging import version
import traceback
from browserstack_sdk.sdk_cli.bstack1ll1l1l1111_opy_ import bstack1lll1111lll_opy_
from browserstack_sdk.sdk_cli.bstack1llll11l1ll_opy_ import (
    bstack1llll1ll11l_opy_,
    bstack1lllll11111_opy_,
    bstack1llll1l11l1_opy_,
)
from bstack_utils.constants import *
from typing import Any, List, Union, Dict
from pathlib import Path
from browserstack_sdk.sdk_cli.bstack1lll1llll1l_opy_ import bstack1ll1ll1111l_opy_
from datetime import datetime
from typing import Tuple, Any
from bstack_utils.messages import bstack11l1l1ll11_opy_
from bstack_utils.helper import bstack1l1l1l1l1l1_opy_
import threading
import os
import urllib.parse
class bstack1lll111lll1_opy_(bstack1lll1111lll_opy_):
    def __init__(self, bstack1lll1lllll1_opy_):
        super().__init__()
        bstack1ll1ll1111l_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.bstack1llllll1l11_opy_, bstack1lllll11111_opy_.PRE), self.bstack1l1l111111l_opy_)
        bstack1ll1ll1111l_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.bstack1llllll1l11_opy_, bstack1lllll11111_opy_.PRE), self.bstack1l11llllll1_opy_)
        bstack1ll1ll1111l_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.bstack1lllll1llll_opy_, bstack1lllll11111_opy_.PRE), self.bstack1l1l111ll1l_opy_)
        bstack1ll1ll1111l_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.bstack1lllll111ll_opy_, bstack1lllll11111_opy_.PRE), self.bstack1l1l1111l11_opy_)
        bstack1ll1ll1111l_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.bstack1llllll1l11_opy_, bstack1lllll11111_opy_.PRE), self.bstack1l1l111l111_opy_)
        bstack1ll1ll1111l_opy_.bstack1ll111111ll_opy_((bstack1llll1ll11l_opy_.QUIT, bstack1lllll11111_opy_.PRE), self.on_close)
        self.bstack1lll1lllll1_opy_ = bstack1lll1lllll1_opy_
    def is_enabled(self) -> bool:
        return True
    def bstack1l1l111111l_opy_(
        self,
        f: bstack1ll1ll1111l_opy_,
        bstack1l1l1111ll1_opy_: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1111l1_opy_ (u"ࠥࡰࡦࡻ࡮ࡤࡪࠥጙ"):
            return
        if not bstack1l1l1l1l1l1_opy_():
            self.logger.debug(bstack1111l1_opy_ (u"ࠦࡗ࡫ࡴࡶࡴࡱ࡭ࡳ࡭ࠠࡪࡰࠣࡰࡦࡻ࡮ࡤࡪࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣጚ"))
            return
        def wrapped(bstack1l1l1111ll1_opy_, launch, *args, **kwargs):
            response = self.bstack1l11lllll1l_opy_(f.platform_index, instance.ref(), json.dumps({bstack1111l1_opy_ (u"ࠬ࡯ࡳࡑ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠫጛ"): True}).encode(bstack1111l1_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧጜ")))
            if response is not None and response.capabilities:
                if not bstack1l1l1l1l1l1_opy_():
                    browser = launch(bstack1l1l1111ll1_opy_)
                    return browser
                bstack1l1l111l1ll_opy_ = json.loads(response.capabilities.decode(bstack1111l1_opy_ (u"ࠢࡶࡶࡩ࠱࠽ࠨጝ")))
                if not bstack1l1l111l1ll_opy_: # empty caps bstack1l1l111lll1_opy_ bstack1l1l1111111_opy_ bstack1l1l111ll11_opy_ bstack1ll1lllll1l_opy_ or error in processing
                    return
                bstack1l11lllllll_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l1l111l1ll_opy_))
                f.bstack1lllll1l1l1_opy_(instance, bstack1ll1ll1111l_opy_.bstack1l1l1111l1l_opy_, bstack1l11lllllll_opy_)
                f.bstack1lllll1l1l1_opy_(instance, bstack1ll1ll1111l_opy_.bstack1l1l111l1l1_opy_, bstack1l1l111l1ll_opy_)
                browser = bstack1l1l1111ll1_opy_.connect(bstack1l11lllllll_opy_)
                return browser
        return wrapped
    def bstack1l1l111ll1l_opy_(
        self,
        f: bstack1ll1ll1111l_opy_,
        Connection: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1111l1_opy_ (u"ࠣࡦ࡬ࡷࡵࡧࡴࡤࡪࠥጞ"):
            self.logger.debug(bstack1111l1_opy_ (u"ࠤࡕࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥ࡯࡮ࠡࡦ࡬ࡷࡵࡧࡴࡤࡪࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣጟ"))
            return
        if not bstack1l1l1l1l1l1_opy_():
            return
        def wrapped(Connection, dispatch, *args, **kwargs):
            data = args[0]
            try:
                if args and args[0].get(bstack1111l1_opy_ (u"ࠪࡴࡦࡸࡡ࡮ࡵࠪጠ"), {}).get(bstack1111l1_opy_ (u"ࠫࡧࡹࡐࡢࡴࡤࡱࡸ࠭ጡ")):
                    bstack1l1l11111l1_opy_ = args[0][bstack1111l1_opy_ (u"ࠧࡶࡡࡳࡣࡰࡷࠧጢ")][bstack1111l1_opy_ (u"ࠨࡢࡴࡒࡤࡶࡦࡳࡳࠣጣ")]
                    session_id = bstack1l1l11111l1_opy_.get(bstack1111l1_opy_ (u"ࠢࡴࡧࡶࡷ࡮ࡵ࡮ࡊࡦࠥጤ"))
                    f.bstack1lllll1l1l1_opy_(instance, bstack1ll1ll1111l_opy_.bstack1l1l1111lll_opy_, session_id)
            except Exception as e:
                self.logger.debug(bstack1111l1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡥ࡫ࡶࡴࡦࡺࡣࡩࠢࡰࡩࡹ࡮࡯ࡥ࠼ࠣࠦጥ"), e)
            dispatch(Connection, *args)
        return wrapped
    def bstack1l1l111l111_opy_(
        self,
        f: bstack1ll1ll1111l_opy_,
        bstack1l1l1111ll1_opy_: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1111l1_opy_ (u"ࠤࡦࡳࡳࡴࡥࡤࡶࠥጦ"):
            return
        if not bstack1l1l1l1l1l1_opy_():
            self.logger.debug(bstack1111l1_opy_ (u"ࠥࡖࡪࡺࡵࡳࡰ࡬ࡲ࡬ࠦࡩ࡯ࠢࡦࡳࡳࡴࡥࡤࡶࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣጧ"))
            return
        def wrapped(bstack1l1l1111ll1_opy_, connect, *args, **kwargs):
            response = self.bstack1l11lllll1l_opy_(f.platform_index, instance.ref(), json.dumps({bstack1111l1_opy_ (u"ࠫ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠪጨ"): True}).encode(bstack1111l1_opy_ (u"ࠧࡻࡴࡧ࠯࠻ࠦጩ")))
            if response is not None and response.capabilities:
                bstack1l1l111l1ll_opy_ = json.loads(response.capabilities.decode(bstack1111l1_opy_ (u"ࠨࡵࡵࡨ࠰࠼ࠧጪ")))
                if not bstack1l1l111l1ll_opy_:
                    return
                bstack1l11lllllll_opy_ = PLAYWRIGHT_HUB_URL + urllib.parse.quote(json.dumps(bstack1l1l111l1ll_opy_))
                if bstack1l1l111l1ll_opy_.get(bstack1111l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ጫ")):
                    browser = bstack1l1l1111ll1_opy_.bstack1l1l111llll_opy_(bstack1l11lllllll_opy_)
                    return browser
                else:
                    args = list(args)
                    args[0] = bstack1l11lllllll_opy_
                    return connect(bstack1l1l1111ll1_opy_, *args, **kwargs)
        return wrapped
    def bstack1l11llllll1_opy_(
        self,
        f: bstack1ll1ll1111l_opy_,
        bstack1l1lll1lll1_opy_: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1111l1_opy_ (u"ࠣࡰࡨࡻࡤࡶࡡࡨࡧࠥጬ"):
            return
        if not bstack1l1l1l1l1l1_opy_():
            self.logger.debug(bstack1111l1_opy_ (u"ࠤࡕࡩࡹࡻࡲ࡯࡫ࡱ࡫ࠥ࡯࡮ࠡࡰࡨࡻࡤࡶࡡࡨࡧࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣጭ"))
            return
        def wrapped(bstack1l1lll1lll1_opy_, bstack1l1l111l11l_opy_, *args, **kwargs):
            contexts = bstack1l1lll1lll1_opy_.browser.contexts
            if contexts:
                for context in contexts:
                    if context.pages:
                        for page in context.pages:
                            if bstack1111l1_opy_ (u"ࠥࡥࡧࡵࡵࡵ࠼ࡥࡰࡦࡴ࡫ࠣጮ") in page.url:
                                return page
                            else:
                                return bstack1l1l111l11l_opy_(bstack1l1lll1lll1_opy_)
                    else:
                        return bstack1l1l111l11l_opy_(bstack1l1lll1lll1_opy_)
        return wrapped
    def bstack1l11lllll1l_opy_(self, platform_index: int, ref, user_input_params: bytes):
        req = structs.DriverInitRequest()
        req.bin_session_id = self.bin_session_id
        req.platform_index = platform_index
        req.user_input_params = user_input_params
        req.ref = ref
        self.logger.debug(bstack1111l1_opy_ (u"ࠦࡷ࡫ࡧࡪࡵࡷࡩࡷࡥࡷࡦࡤࡧࡶ࡮ࡼࡥࡳࡡ࡬ࡲ࡮ࡺ࠺ࠡࠤጯ") + str(req) + bstack1111l1_opy_ (u"ࠧࠨጰ"))
        try:
            r = self.bstack1lll1l1lll1_opy_.DriverInit(req)
            if not r.success:
                self.logger.debug(bstack1111l1_opy_ (u"ࠨࡲࡦࡥࡨ࡭ࡻ࡫ࡤࠡࡨࡵࡳࡲࠦࡳࡦࡴࡹࡩࡷࡀࠠࡴࡷࡦࡧࡪࡹࡳ࠾ࠤጱ") + str(r.success) + bstack1111l1_opy_ (u"ࠢࠣጲ"))
            return r
        except grpc.RpcError as e:
            self.logger.error(bstack1111l1_opy_ (u"ࠣࡴࡳࡧ࠲࡫ࡲࡳࡱࡵ࠾ࠥࠨጳ") + str(e) + bstack1111l1_opy_ (u"ࠤࠥጴ"))
            traceback.print_exc()
            raise e
    def bstack1l1l1111l11_opy_(
        self,
        f: bstack1ll1ll1111l_opy_,
        Connection: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1111l1_opy_ (u"ࠥࡣࡸ࡫࡮ࡥࡡࡰࡩࡸࡹࡡࡨࡧࡢࡸࡴࡥࡳࡦࡴࡹࡩࡷࠨጵ"):
            return
        if not bstack1l1l1l1l1l1_opy_():
            return
        def wrapped(Connection, bstack1l1l11111ll_opy_, *args, **kwargs):
            return bstack1l1l11111ll_opy_(Connection, *args, **kwargs)
        return wrapped
    def on_close(
        self,
        f: bstack1ll1ll1111l_opy_,
        bstack1l1l1111ll1_opy_: object,
        exec: Tuple[bstack1llll1l11l1_opy_, str],
        bstack1llll1ll1l1_opy_: Tuple[bstack1llll1ll11l_opy_, bstack1lllll11111_opy_],
        result: Any,
        *args,
        **kwargs,
    ):
        instance, method_name = exec
        if method_name != bstack1111l1_opy_ (u"ࠦࡨࡲ࡯ࡴࡧࠥጶ"):
            return
        if not bstack1l1l1l1l1l1_opy_():
            self.logger.debug(bstack1111l1_opy_ (u"ࠧࡘࡥࡵࡷࡵࡲ࡮ࡴࡧࠡ࡫ࡱࠤࡨࡲ࡯ࡴࡧࠣࡱࡪࡺࡨࡰࡦ࠯ࠤࡳࡵࡴࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠣጷ"))
            return
        def wrapped(Connection, close, *args, **kwargs):
            return close(Connection)
        return wrapped