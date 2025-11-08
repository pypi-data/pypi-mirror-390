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
from _pytest import fixtures
from _pytest.python import _call_with_optional_argument
from pytest import Module, Class
from bstack_utils.helper import Result, bstack111ll111l1l_opy_
from browserstack_sdk.bstack1llll1ll1l_opy_ import bstack1l1l1111_opy_
def _111l1lll111_opy_(method, this, arg):
    arg_count = method.__code__.co_argcount
    if arg_count > 1:
        method(this, arg)
    else:
        method(this)
class bstack111l1ll1lll_opy_:
    def __init__(self, handler):
        self._111l1ll1ll1_opy_ = {}
        self._111ll1111ll_opy_ = {}
        self.handler = handler
        self.patch()
        pass
    def patch(self):
        pytest_version = bstack1l1l1111_opy_.version()
        if bstack111ll111l1l_opy_(pytest_version, bstack1111l1_opy_ (u"ࠣ࠺࠱࠵࠳࠷ࠢᶳ")) >= 0:
            self._111l1ll1ll1_opy_[bstack1111l1_opy_ (u"ࠩࡩࡹࡳࡩࡴࡪࡱࡱࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᶴ")] = Module._register_setup_function_fixture
            self._111l1ll1ll1_opy_[bstack1111l1_opy_ (u"ࠪࡱࡴࡪࡵ࡭ࡧࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᶵ")] = Module._register_setup_module_fixture
            self._111l1ll1ll1_opy_[bstack1111l1_opy_ (u"ࠫࡨࡲࡡࡴࡵࡢࡪ࡮ࡾࡴࡶࡴࡨࠫᶶ")] = Class._register_setup_class_fixture
            self._111l1ll1ll1_opy_[bstack1111l1_opy_ (u"ࠬࡳࡥࡵࡪࡲࡨࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᶷ")] = Class._register_setup_method_fixture
            Module._register_setup_function_fixture = self.bstack111l1llll11_opy_(bstack1111l1_opy_ (u"࠭ࡦࡶࡰࡦࡸ࡮ࡵ࡮ࡠࡨ࡬ࡼࡹࡻࡲࡦࠩᶸ"))
            Module._register_setup_module_fixture = self.bstack111l1llll11_opy_(bstack1111l1_opy_ (u"ࠧ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᶹ"))
            Class._register_setup_class_fixture = self.bstack111l1llll11_opy_(bstack1111l1_opy_ (u"ࠨࡥ࡯ࡥࡸࡹ࡟ࡧ࡫ࡻࡸࡺࡸࡥࠨᶺ"))
            Class._register_setup_method_fixture = self.bstack111l1llll11_opy_(bstack1111l1_opy_ (u"ࠩࡰࡩࡹ࡮࡯ࡥࡡࡩ࡭ࡽࡺࡵࡳࡧࠪᶻ"))
        else:
            self._111l1ll1ll1_opy_[bstack1111l1_opy_ (u"ࠪࡪࡺࡴࡣࡵ࡫ࡲࡲࡤ࡬ࡩࡹࡶࡸࡶࡪ࠭ᶼ")] = Module._inject_setup_function_fixture
            self._111l1ll1ll1_opy_[bstack1111l1_opy_ (u"ࠫࡲࡵࡤࡶ࡮ࡨࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᶽ")] = Module._inject_setup_module_fixture
            self._111l1ll1ll1_opy_[bstack1111l1_opy_ (u"ࠬࡩ࡬ࡢࡵࡶࡣ࡫࡯ࡸࡵࡷࡵࡩࠬᶾ")] = Class._inject_setup_class_fixture
            self._111l1ll1ll1_opy_[bstack1111l1_opy_ (u"࠭࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠧᶿ")] = Class._inject_setup_method_fixture
            Module._inject_setup_function_fixture = self.bstack111l1llll11_opy_(bstack1111l1_opy_ (u"ࠧࡧࡷࡱࡧࡹ࡯࡯࡯ࡡࡩ࡭ࡽࡺࡵࡳࡧࠪ᷀"))
            Module._inject_setup_module_fixture = self.bstack111l1llll11_opy_(bstack1111l1_opy_ (u"ࠨ࡯ࡲࡨࡺࡲࡥࡠࡨ࡬ࡼࡹࡻࡲࡦࠩ᷁"))
            Class._inject_setup_class_fixture = self.bstack111l1llll11_opy_(bstack1111l1_opy_ (u"ࠩࡦࡰࡦࡹࡳࡠࡨ࡬ࡼࡹࡻࡲࡦ᷂ࠩ"))
            Class._inject_setup_method_fixture = self.bstack111l1llll11_opy_(bstack1111l1_opy_ (u"ࠪࡱࡪࡺࡨࡰࡦࡢࡪ࡮ࡾࡴࡶࡴࡨࠫ᷃"))
    def bstack111l1llll1l_opy_(self, bstack111l1ll1l1l_opy_, hook_type):
        bstack111ll1111l1_opy_ = id(bstack111l1ll1l1l_opy_.__class__)
        if (bstack111ll1111l1_opy_, hook_type) in self._111ll1111ll_opy_:
            return
        meth = getattr(bstack111l1ll1l1l_opy_, hook_type, None)
        if meth is not None and fixtures.getfixturemarker(meth) is None:
            self._111ll1111ll_opy_[(bstack111ll1111l1_opy_, hook_type)] = meth
            setattr(bstack111l1ll1l1l_opy_, hook_type, self.bstack111l1lllll1_opy_(hook_type, bstack111ll1111l1_opy_))
    def bstack111l1lll1ll_opy_(self, instance, bstack111l1lll11l_opy_):
        if bstack111l1lll11l_opy_ == bstack1111l1_opy_ (u"ࠦ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࡥࡦࡪࡺࡷࡹࡷ࡫ࠢ᷄"):
            self.bstack111l1llll1l_opy_(instance.obj, bstack1111l1_opy_ (u"ࠧࡹࡥࡵࡷࡳࡣ࡫ࡻ࡮ࡤࡶ࡬ࡳࡳࠨ᷅"))
            self.bstack111l1llll1l_opy_(instance.obj, bstack1111l1_opy_ (u"ࠨࡴࡦࡣࡵࡨࡴࡽ࡮ࡠࡨࡸࡲࡨࡺࡩࡰࡰࠥ᷆"))
        if bstack111l1lll11l_opy_ == bstack1111l1_opy_ (u"ࠢ࡮ࡱࡧࡹࡱ࡫࡟ࡧ࡫ࡻࡸࡺࡸࡥࠣ᷇"):
            self.bstack111l1llll1l_opy_(instance.obj, bstack1111l1_opy_ (u"ࠣࡵࡨࡸࡺࡶ࡟࡮ࡱࡧࡹࡱ࡫ࠢ᷈"))
            self.bstack111l1llll1l_opy_(instance.obj, bstack1111l1_opy_ (u"ࠤࡷࡩࡦࡸࡤࡰࡹࡱࡣࡲࡵࡤࡶ࡮ࡨࠦ᷉"))
        if bstack111l1lll11l_opy_ == bstack1111l1_opy_ (u"ࠥࡧࡱࡧࡳࡴࡡࡩ࡭ࡽࡺࡵࡳࡧ᷊ࠥ"):
            self.bstack111l1llll1l_opy_(instance.obj, bstack1111l1_opy_ (u"ࠦࡸ࡫ࡴࡶࡲࡢࡧࡱࡧࡳࡴࠤ᷋"))
            self.bstack111l1llll1l_opy_(instance.obj, bstack1111l1_opy_ (u"ࠧࡺࡥࡢࡴࡧࡳࡼࡴ࡟ࡤ࡮ࡤࡷࡸࠨ᷌"))
        if bstack111l1lll11l_opy_ == bstack1111l1_opy_ (u"ࠨ࡭ࡦࡶ࡫ࡳࡩࡥࡦࡪࡺࡷࡹࡷ࡫ࠢ᷍"):
            self.bstack111l1llll1l_opy_(instance.obj, bstack1111l1_opy_ (u"ࠢࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩࠨ᷎"))
            self.bstack111l1llll1l_opy_(instance.obj, bstack1111l1_opy_ (u"ࠣࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦ᷏ࠥ"))
    @staticmethod
    def bstack111l1lll1l1_opy_(hook_type, func, args):
        if hook_type in [bstack1111l1_opy_ (u"ࠩࡶࡩࡹࡻࡰࡠ࡯ࡨࡸ࡭ࡵࡤࠨ᷐"), bstack1111l1_opy_ (u"ࠪࡸࡪࡧࡲࡥࡱࡺࡲࡤࡳࡥࡵࡪࡲࡨࠬ᷑")]:
            _111l1lll111_opy_(func, args[0], args[1])
            return
        _call_with_optional_argument(func, args[0])
    def bstack111l1lllll1_opy_(self, hook_type, bstack111ll1111l1_opy_):
        def bstack111l1llllll_opy_(arg=None):
            self.handler(hook_type, bstack1111l1_opy_ (u"ࠫࡧ࡫ࡦࡰࡴࡨࠫ᷒"))
            result = None
            try:
                bstack1llllll1l1l_opy_ = self._111ll1111ll_opy_[(bstack111ll1111l1_opy_, hook_type)]
                self.bstack111l1lll1l1_opy_(hook_type, bstack1llllll1l1l_opy_, (arg,))
                result = Result(result=bstack1111l1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᷓ"))
            except Exception as e:
                result = Result(result=bstack1111l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ᷔ"), exception=e)
                self.handler(hook_type, bstack1111l1_opy_ (u"ࠧࡢࡨࡷࡩࡷ࠭ᷕ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1111l1_opy_ (u"ࠨࡣࡩࡸࡪࡸࠧᷖ"), result)
        def bstack111ll11111l_opy_(this, arg=None):
            self.handler(hook_type, bstack1111l1_opy_ (u"ࠩࡥࡩ࡫ࡵࡲࡦࠩᷗ"))
            result = None
            exception = None
            try:
                self.bstack111l1lll1l1_opy_(hook_type, self._111ll1111ll_opy_[hook_type], (this, arg))
                result = Result(result=bstack1111l1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪᷘ"))
            except Exception as e:
                result = Result(result=bstack1111l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᷙ"), exception=e)
                self.handler(hook_type, bstack1111l1_opy_ (u"ࠬࡧࡦࡵࡧࡵࠫᷚ"), result)
                raise e.with_traceback(e.__traceback__)
            self.handler(hook_type, bstack1111l1_opy_ (u"࠭ࡡࡧࡶࡨࡶࠬᷛ"), result)
        if hook_type in [bstack1111l1_opy_ (u"ࠧࡴࡧࡷࡹࡵࡥ࡭ࡦࡶ࡫ࡳࡩ࠭ᷜ"), bstack1111l1_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࡢࡱࡪࡺࡨࡰࡦࠪᷝ")]:
            return bstack111ll11111l_opy_
        return bstack111l1llllll_opy_
    def bstack111l1llll11_opy_(self, bstack111l1lll11l_opy_):
        def bstack111l1ll1l11_opy_(this, *args, **kwargs):
            self.bstack111l1lll1ll_opy_(this, bstack111l1lll11l_opy_)
            self._111l1ll1ll1_opy_[bstack111l1lll11l_opy_](this, *args, **kwargs)
        return bstack111l1ll1l11_opy_