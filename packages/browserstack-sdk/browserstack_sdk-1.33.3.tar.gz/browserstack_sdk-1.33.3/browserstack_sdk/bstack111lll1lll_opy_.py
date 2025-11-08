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
import threading
import os
import logging
from uuid import uuid4
from bstack_utils.bstack111l1ll1l1_opy_ import bstack111ll1l111_opy_, bstack111ll1llll_opy_
from bstack_utils.bstack111ll1lll1_opy_ import bstack1ll1111ll1_opy_
from bstack_utils.helper import bstack1l1ll111l_opy_, bstack11l1l1111l_opy_, Result
from bstack_utils.bstack111ll11l11_opy_ import bstack1ll11111_opy_
from bstack_utils.capture import bstack111lll1111_opy_
from bstack_utils.constants import *
logger = logging.getLogger(__name__)
class bstack111lll1lll_opy_:
    def __init__(self):
        self.bstack111ll11ll1_opy_ = bstack111lll1111_opy_(self.bstack111ll11111_opy_)
        self.tests = {}
    @staticmethod
    def bstack111ll11111_opy_(log):
        if not (log[bstack1111l1_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ཀ")] and log[bstack1111l1_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧཁ")].strip()):
            return
        active = bstack1ll1111ll1_opy_.bstack111ll1l1l1_opy_()
        log = {
            bstack1111l1_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ག"): log[bstack1111l1_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧགྷ")],
            bstack1111l1_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬང"): bstack11l1l1111l_opy_(),
            bstack1111l1_opy_ (u"ࠪࡱࡪࡹࡳࡢࡩࡨࠫཅ"): log[bstack1111l1_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬཆ")],
        }
        if active:
            if active[bstack1111l1_opy_ (u"ࠬࡺࡹࡱࡧࠪཇ")] == bstack1111l1_opy_ (u"࠭ࡨࡰࡱ࡮ࠫ཈"):
                log[bstack1111l1_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡸࡵ࡯ࡡࡸࡹ࡮ࡪࠧཉ")] = active[bstack1111l1_opy_ (u"ࠨࡪࡲࡳࡰࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨཊ")]
            elif active[bstack1111l1_opy_ (u"ࠩࡷࡽࡵ࡫ࠧཋ")] == bstack1111l1_opy_ (u"ࠪࡸࡪࡹࡴࠨཌ"):
                log[bstack1111l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫཌྷ")] = active[bstack1111l1_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬཎ")]
        bstack1ll11111_opy_.bstack11ll111ll_opy_([log])
    def start_test(self, attrs):
        test_uuid = uuid4().__str__()
        self.tests[test_uuid] = {}
        self.bstack111ll11ll1_opy_.start()
        driver = bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰ࡙ࡥࡴࡵ࡬ࡳࡳࡊࡲࡪࡸࡨࡶࠬཏ"), None)
        bstack111l1ll1l1_opy_ = bstack111ll1llll_opy_(
            name=attrs.scenario.name,
            uuid=test_uuid,
            started_at=bstack11l1l1111l_opy_(),
            file_path=attrs.feature.filename,
            result=bstack1111l1_opy_ (u"ࠢࡱࡧࡱࡨ࡮ࡴࡧࠣཐ"),
            framework=bstack1111l1_opy_ (u"ࠨࡄࡨ࡬ࡦࡼࡥࠨད"),
            scope=[attrs.feature.name],
            bstack111ll1l11l_opy_=bstack1ll11111_opy_.bstack111l1llll1_opy_(driver) if driver and driver.session_id else {},
            meta={},
            tags=attrs.scenario.tags
        )
        self.tests[test_uuid][bstack1111l1_opy_ (u"ࠩࡷࡩࡸࡺ࡟ࡥࡣࡷࡥࠬདྷ")] = bstack111l1ll1l1_opy_
        threading.current_thread().current_test_uuid = test_uuid
        bstack1ll11111_opy_.bstack111ll1l1ll_opy_(bstack1111l1_opy_ (u"ࠪࡘࡪࡹࡴࡓࡷࡱࡗࡹࡧࡲࡵࡧࡧࠫན"), bstack111l1ll1l1_opy_)
    def end_test(self, attrs):
        bstack111ll1111l_opy_ = {
            bstack1111l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤཔ"): attrs.feature.name,
            bstack1111l1_opy_ (u"ࠧࡪࡥࡴࡥࡵ࡭ࡵࡺࡩࡰࡰࠥཕ"): attrs.feature.description
        }
        current_test_uuid = threading.current_thread().current_test_uuid
        bstack111l1ll1l1_opy_ = self.tests[current_test_uuid][bstack1111l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩབ")]
        meta = {
            bstack1111l1_opy_ (u"ࠢࡧࡧࡤࡸࡺࡸࡥࠣབྷ"): bstack111ll1111l_opy_,
            bstack1111l1_opy_ (u"ࠣࡵࡷࡩࡵࡹࠢམ"): bstack111l1ll1l1_opy_.meta.get(bstack1111l1_opy_ (u"ࠩࡶࡸࡪࡶࡳࠨཙ"), []),
            bstack1111l1_opy_ (u"ࠥࡷࡨ࡫࡮ࡢࡴ࡬ࡳࠧཚ"): {
                bstack1111l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤཛ"): attrs.feature.scenarios[0].name if len(attrs.feature.scenarios) else None
            }
        }
        bstack111l1ll1l1_opy_.bstack111l1ll111_opy_(meta)
        bstack111l1ll1l1_opy_.bstack111l1lll11_opy_(bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"ࠬࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡵࠪཛྷ"), []))
        bstack111l1lll1l_opy_, exception = self._111l1ll11l_opy_(attrs)
        bstack111ll1ll1l_opy_ = Result(result=attrs.status.name, exception=exception, bstack111ll111l1_opy_=[bstack111l1lll1l_opy_])
        self.tests[threading.current_thread().current_test_uuid][bstack1111l1_opy_ (u"࠭ࡴࡦࡵࡷࡣࡩࡧࡴࡢࠩཝ")].stop(time=bstack11l1l1111l_opy_(), duration=int(attrs.duration)*1000, result=bstack111ll1ll1l_opy_)
        bstack1ll11111_opy_.bstack111ll1l1ll_opy_(bstack1111l1_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩཞ"), self.tests[threading.current_thread().current_test_uuid][bstack1111l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫཟ")])
    def bstack11l11l1ll1_opy_(self, attrs):
        bstack111ll111ll_opy_ = {
            bstack1111l1_opy_ (u"ࠩ࡬ࡨࠬའ"): uuid4().__str__(),
            bstack1111l1_opy_ (u"ࠪ࡯ࡪࡿࡷࡰࡴࡧࠫཡ"): attrs.keyword,
            bstack1111l1_opy_ (u"ࠫࡸࡺࡥࡱࡡࡤࡶ࡬ࡻ࡭ࡦࡰࡷࠫར"): [],
            bstack1111l1_opy_ (u"ࠬࡺࡥࡹࡶࠪལ"): attrs.name,
            bstack1111l1_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪཤ"): bstack11l1l1111l_opy_(),
            bstack1111l1_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧཥ"): bstack1111l1_opy_ (u"ࠨࡲࡨࡲࡩ࡯࡮ࡨࠩས"),
            bstack1111l1_opy_ (u"ࠩࡧࡩࡸࡩࡲࡪࡲࡷ࡭ࡴࡴࠧཧ"): bstack1111l1_opy_ (u"ࠪࠫཨ")
        }
        self.tests[threading.current_thread().current_test_uuid][bstack1111l1_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠧཀྵ")].add_step(bstack111ll111ll_opy_)
        threading.current_thread().current_step_uuid = bstack111ll111ll_opy_[bstack1111l1_opy_ (u"ࠬ࡯ࡤࠨཪ")]
    def bstack1l1111l11_opy_(self, attrs):
        current_test_id = bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"࠭ࡣࡶࡴࡵࡩࡳࡺ࡟ࡵࡧࡶࡸࡤࡻࡵࡪࡦࠪཫ"), None)
        current_step_uuid = bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"ࠧࡤࡷࡵࡶࡪࡴࡴࡠࡵࡷࡩࡵࡥࡵࡶ࡫ࡧࠫཬ"), None)
        bstack111l1lll1l_opy_, exception = self._111l1ll11l_opy_(attrs)
        bstack111ll1ll1l_opy_ = Result(result=attrs.status.name, exception=exception, bstack111ll111l1_opy_=[bstack111l1lll1l_opy_])
        self.tests[current_test_id][bstack1111l1_opy_ (u"ࠨࡶࡨࡷࡹࡥࡤࡢࡶࡤࠫ཭")].bstack111ll11l1l_opy_(current_step_uuid, duration=int(attrs.duration)*1000, result=bstack111ll1ll1l_opy_)
        threading.current_thread().current_step_uuid = None
    def bstack11111l111_opy_(self, name, attrs):
        try:
            bstack111ll1ll11_opy_ = uuid4().__str__()
            self.tests[bstack111ll1ll11_opy_] = {}
            self.bstack111ll11ll1_opy_.start()
            scopes = []
            driver = bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨ཮"), None)
            current_thread = threading.current_thread()
            if not hasattr(current_thread, bstack1111l1_opy_ (u"ࠪࡧࡺࡸࡲࡦࡰࡷࡣࡹ࡫ࡳࡵࡡ࡫ࡳࡴࡱࡳࠨ཯")):
                current_thread.current_test_hooks = []
            current_thread.current_test_hooks.append(bstack111ll1ll11_opy_)
            if name in [bstack1111l1_opy_ (u"ࠦࡧ࡫ࡦࡰࡴࡨࡣࡦࡲ࡬ࠣ཰"), bstack1111l1_opy_ (u"ࠧࡧࡦࡵࡧࡵࡣࡦࡲ࡬ཱࠣ")]:
                file_path = os.path.join(attrs.config.base_dir, attrs.config.environment_file)
                scopes = [attrs.config.environment_file]
            elif name in [bstack1111l1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡦࡦࡣࡷࡹࡷ࡫ིࠢ"), bstack1111l1_opy_ (u"ࠢࡢࡨࡷࡩࡷࡥࡦࡦࡣࡷࡹࡷ࡫ཱིࠢ")]:
                file_path = attrs.filename
                scopes = [attrs.name]
            else:
                file_path = attrs.filename
                if hasattr(attrs, bstack1111l1_opy_ (u"ࠨࡨࡨࡥࡹࡻࡲࡦུࠩ")):
                    scopes =  [attrs.feature.name]
            hook_data = bstack111ll1l111_opy_(
                name=name,
                uuid=bstack111ll1ll11_opy_,
                started_at=bstack11l1l1111l_opy_(),
                file_path=file_path,
                framework=bstack1111l1_opy_ (u"ࠤࡅࡩ࡭ࡧࡶࡦࠤཱུ"),
                bstack111ll1l11l_opy_=bstack1ll11111_opy_.bstack111l1llll1_opy_(driver) if driver and driver.session_id else {},
                scope=scopes,
                result=bstack1111l1_opy_ (u"ࠥࡴࡪࡴࡤࡪࡰࡪࠦྲྀ"),
                hook_type=name
            )
            self.tests[bstack111ll1ll11_opy_][bstack1111l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡧࡥࡹࡧࠢཷ")] = hook_data
            current_test_id = bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"ࠧࡩࡵࡳࡴࡨࡲࡹࡥࡴࡦࡵࡷࡣࡺࡻࡩࡥࠤླྀ"), None)
            if current_test_id:
                hook_data.bstack111l1lllll_opy_(current_test_id)
            if name == bstack1111l1_opy_ (u"ࠨࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࠥཹ"):
                threading.current_thread().before_all_hook_uuid = bstack111ll1ll11_opy_
            threading.current_thread().current_hook_uuid = bstack111ll1ll11_opy_
            bstack1ll11111_opy_.bstack111ll1l1ll_opy_(bstack1111l1_opy_ (u"ࠢࡉࡱࡲ࡯ࡗࡻ࡮ࡔࡶࡤࡶࡹ࡫ࡤེࠣ"), hook_data)
        except Exception as e:
            logger.debug(bstack1111l1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡰࡥࡦࡹࡷࡸࡥࡥࠢ࡬ࡲࠥࡹࡴࡢࡴࡷࠤ࡭ࡵ࡯࡬ࠢࡨࡺࡪࡴࡴࡴ࠮ࠣ࡬ࡴࡵ࡫ࠡࡰࡤࡱࡪࡀࠠࠦࡵ࠯ࠤࡪࡸࡲࡰࡴ࠽ࠤࠪࡹཻࠢ"), name, e)
    def bstack1ll1l11lll_opy_(self, attrs):
        bstack111ll11lll_opy_ = bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"ࠩࡦࡹࡷࡸࡥ࡯ࡶࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩོ࠭"), None)
        hook_data = self.tests[bstack111ll11lll_opy_][bstack1111l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦཽ࠭")]
        status = bstack1111l1_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦཾ")
        exception = None
        bstack111l1lll1l_opy_ = None
        if hook_data.name == bstack1111l1_opy_ (u"ࠧࡧࡦࡵࡧࡵࡣࡦࡲ࡬ࠣཿ"):
            self.bstack111ll11ll1_opy_.reset()
            bstack111l1ll1ll_opy_ = self.tests[bstack1l1ll111l_opy_(threading.current_thread(), bstack1111l1_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪࡥࡡ࡭࡮ࡢ࡬ࡴࡵ࡫ࡠࡷࡸ࡭ࡩྀ࠭"), None)][bstack1111l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡪࡡࡵࡣཱྀࠪ")].result.result
            if bstack111l1ll1ll_opy_ == bstack1111l1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣྂ"):
                if attrs.hook_failures == 1:
                    status = bstack1111l1_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤྃ")
                elif attrs.hook_failures == 2:
                    status = bstack1111l1_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦ྄ࠥ")
            elif attrs.aborted:
                status = bstack1111l1_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦ྅")
            threading.current_thread().before_all_hook_uuid = None
        else:
            if hook_data.name == bstack1111l1_opy_ (u"ࠬࡨࡥࡧࡱࡵࡩࡤࡧ࡬࡭ࠩ྆") and attrs.hook_failures == 1:
                status = bstack1111l1_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ྇")
            elif hasattr(attrs, bstack1111l1_opy_ (u"ࠧࡦࡴࡵࡳࡷࡥ࡭ࡦࡵࡶࡥ࡬࡫ࠧྈ")) and attrs.error_message:
                status = bstack1111l1_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣྉ")
            bstack111l1lll1l_opy_, exception = self._111l1ll11l_opy_(attrs)
        bstack111ll1ll1l_opy_ = Result(result=status, exception=exception, bstack111ll111l1_opy_=[bstack111l1lll1l_opy_])
        hook_data.stop(time=bstack11l1l1111l_opy_(), duration=0, result=bstack111ll1ll1l_opy_)
        bstack1ll11111_opy_.bstack111ll1l1ll_opy_(bstack1111l1_opy_ (u"ࠩࡋࡳࡴࡱࡒࡶࡰࡉ࡭ࡳ࡯ࡳࡩࡧࡧࠫྊ"), self.tests[bstack111ll11lll_opy_][bstack1111l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡦࡤࡸࡦ࠭ྋ")])
        threading.current_thread().current_hook_uuid = None
    def _111l1ll11l_opy_(self, attrs):
        try:
            import traceback
            bstack11l1l1l1l_opy_ = traceback.format_tb(attrs.exc_traceback)
            bstack111l1lll1l_opy_ = bstack11l1l1l1l_opy_[-1] if bstack11l1l1l1l_opy_ else None
            exception = attrs.exception
        except Exception:
            logger.debug(bstack1111l1_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡳࡨࡩࡵࡳࡴࡨࡨࠥࡽࡨࡪ࡮ࡨࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡩࡵࡴࡶࡲࡱࠥࡺࡲࡢࡥࡨࡦࡦࡩ࡫ࠣྌ"))
            bstack111l1lll1l_opy_ = None
            exception = None
        return bstack111l1lll1l_opy_, exception