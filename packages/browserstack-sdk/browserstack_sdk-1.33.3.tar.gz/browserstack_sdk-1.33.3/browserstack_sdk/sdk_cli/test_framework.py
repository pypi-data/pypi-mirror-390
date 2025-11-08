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
from enum import Enum
import os
import threading
import traceback
from typing import Dict, List, Any, Callable, Tuple, Union
import abc
from datetime import datetime, timezone
from dataclasses import dataclass
from browserstack_sdk.sdk_cli.bstack1lllllll1l1_opy_ import bstack1lllllll1ll_opy_
from browserstack_sdk.sdk_cli.bstack1llll1lll11_opy_ import bstack1lllll11l1l_opy_, bstack1lllll1ll11_opy_
class bstack1lll11l11ll_opy_(Enum):
    PRE = 0
    POST = 1
    def __repr__(self) -> str:
        return bstack1111l1_opy_ (u"ࠥࡘࡪࡹࡴࡉࡱࡲ࡯ࡘࡺࡡࡵࡧ࠱ࡿࢂࠨᗜ").format(self.name)
class bstack1ll1ll1lll1_opy_(Enum):
    NONE = 0
    BEFORE_ALL = 1
    LOG = 2
    SETUP_FIXTURE = 3
    INIT_TEST = 4
    BEFORE_EACH = 5
    AFTER_EACH = 6
    TEST = 7
    STEP = 8
    LOG_REPORT = 9
    AFTER_ALL = 10
    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    def __repr__(self) -> str:
        return bstack1111l1_opy_ (u"࡙ࠦ࡫ࡳࡵࡈࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡗࡹࡧࡴࡦ࠰ࡾࢁࠧᗝ").format(self.name)
class bstack1ll1llll1l1_opy_(bstack1lllll11l1l_opy_):
    bstack1ll11lll11l_opy_: List[str]
    bstack11lllll1ll1_opy_: Dict[str, str]
    state: bstack1ll1ll1lll1_opy_
    bstack1lllll1l1ll_opy_: datetime
    bstack1llll1llll1_opy_: datetime
    def __init__(
        self,
        context: bstack1lllll1ll11_opy_,
        bstack1ll11lll11l_opy_: List[str],
        bstack11lllll1ll1_opy_: Dict[str, str],
        state=bstack1ll1ll1lll1_opy_.NONE,
    ):
        super().__init__(context)
        self.bstack1ll11lll11l_opy_ = bstack1ll11lll11l_opy_
        self.bstack11lllll1ll1_opy_ = bstack11lllll1ll1_opy_
        self.state = state
        self.bstack1lllll1l1ll_opy_ = datetime.now(tz=timezone.utc)
        self.bstack1llll1llll1_opy_ = datetime.now(tz=timezone.utc)
    def bstack1lllll1l1l1_opy_(self, bstack1llll1ll111_opy_: bstack1ll1ll1lll1_opy_):
        bstack1llllll1ll1_opy_ = bstack1ll1ll1lll1_opy_(bstack1llll1ll111_opy_).name
        if not bstack1llllll1ll1_opy_:
            return False
        if bstack1llll1ll111_opy_ == self.state:
            return False
        self.state = bstack1llll1ll111_opy_
        self.bstack1llll1llll1_opy_ = datetime.now(tz=timezone.utc)
        return True
@dataclass
class bstack11llll1l1ll_opy_:
    test_framework_name: str
    test_framework_version: str
    platform_index: int
@dataclass
class bstack1ll1l1l1lll_opy_:
    kind: str
    message: str
    level: Union[None, str] = None
    timestamp: Union[None, datetime] = datetime.now(tz=timezone.utc)
    fileName: str = None
    bstack1l1l1ll1ll1_opy_: int = None
    bstack1l1ll111l11_opy_: str = None
    bstack1l1lll_opy_: str = None
    bstack1l1ll1ll_opy_: str = None
    bstack1l1l1lll111_opy_: str = None
    bstack11lllll1l1l_opy_: str = None
class TestFramework(abc.ABC):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    bstack1ll11l111l1_opy_ = bstack1111l1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡹࡺ࡯ࡤࠣᗞ")
    bstack1l11111l111_opy_ = bstack1111l1_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡮ࡪࠢᗟ")
    bstack1ll1111l111_opy_ = bstack1111l1_opy_ (u"ࠢࡵࡧࡶࡸࡤࡴࡡ࡮ࡧࠥᗠ")
    bstack1l11111l11l_opy_ = bstack1111l1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡪ࡮ࡨࡣࡵࡧࡴࡩࠤᗡ")
    bstack11llll11lll_opy_ = bstack1111l1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡵࡣࡪࡷࠧᗢ")
    bstack1l11lll1l1l_opy_ = bstack1111l1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡴࡨࡷࡺࡲࡴࠣᗣ")
    bstack1l1l1l1llll_opy_ = bstack1111l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡵࡩࡸࡻ࡬ࡵࡡࡤࡸࠧᗤ")
    bstack1l1ll1lll11_opy_ = bstack1111l1_opy_ (u"ࠧࡺࡥࡴࡶࡢࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠢᗥ")
    bstack1l1l1lll1l1_opy_ = bstack1111l1_opy_ (u"ࠨࡴࡦࡵࡷࡣࡪࡴࡤࡦࡦࡢࡥࡹࠨᗦ")
    bstack1l111111l11_opy_ = bstack1111l1_opy_ (u"ࠢࡵࡧࡶࡸࡤࡲ࡯ࡤࡣࡷ࡭ࡴࡴࠢᗧ")
    bstack1ll1111llll_opy_ = bstack1111l1_opy_ (u"ࠣࡶࡨࡷࡹࡥࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࡡࡱࡥࡲ࡫ࠢᗨ")
    bstack1l1l11llll1_opy_ = bstack1111l1_opy_ (u"ࠤࡷࡩࡸࡺ࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠦᗩ")
    bstack11llll1ll1l_opy_ = bstack1111l1_opy_ (u"ࠥࡸࡪࡹࡴࡠࡥࡲࡨࡪࠨᗪ")
    bstack1l1l11ll11l_opy_ = bstack1111l1_opy_ (u"ࠦࡹ࡫ࡳࡵࡡࡵࡩࡷࡻ࡮ࡠࡰࡤࡱࡪࠨᗫ")
    bstack1ll11l11ll1_opy_ = bstack1111l1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳ࡟ࡪࡰࡧࡩࡽࠨᗬ")
    bstack1l11lll1l11_opy_ = bstack1111l1_opy_ (u"ࠨࡴࡦࡵࡷࡣ࡫ࡧࡩ࡭ࡷࡵࡩࠧᗭ")
    bstack1l111l1l11l_opy_ = bstack1111l1_opy_ (u"ࠢࡵࡧࡶࡸࡤ࡬ࡡࡪ࡮ࡸࡶࡪࡥࡴࡺࡲࡨࠦᗮ")
    bstack1l111l111ll_opy_ = bstack1111l1_opy_ (u"ࠣࡶࡨࡷࡹࡥ࡬ࡰࡩࡶࠦᗯ")
    bstack1l111111ll1_opy_ = bstack1111l1_opy_ (u"ࠤࡷࡩࡸࡺ࡟࡮ࡧࡷࡥࠧᗰ")
    bstack11llll111l1_opy_ = bstack1111l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡵࡦࡳࡵ࡫ࡳࠨᗱ")
    bstack1l11l11l1ll_opy_ = bstack1111l1_opy_ (u"ࠦࡦࡻࡴࡰ࡯ࡤࡸࡪࡥࡳࡦࡵࡶ࡭ࡴࡴ࡟࡯ࡣࡰࡩࠧᗲ")
    bstack11lllll11l1_opy_ = bstack1111l1_opy_ (u"ࠧ࡫ࡶࡦࡰࡷࡣࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠣᗳ")
    bstack1l1111llll1_opy_ = bstack1111l1_opy_ (u"ࠨࡥࡷࡧࡱࡸࡤ࡫࡮ࡥࡧࡧࡣࡦࡺࠢᗴ")
    bstack1l1111lll11_opy_ = bstack1111l1_opy_ (u"ࠢࡩࡱࡲ࡯ࡤ࡯ࡤࠣᗵ")
    bstack1l1111l111l_opy_ = bstack1111l1_opy_ (u"ࠣࡪࡲࡳࡰࡥࡲࡦࡵࡸࡰࡹࠨᗶ")
    bstack1l11111llll_opy_ = bstack1111l1_opy_ (u"ࠤ࡫ࡳࡴࡱ࡟࡭ࡱࡪࡷࠧᗷ")
    bstack1l11111111l_opy_ = bstack1111l1_opy_ (u"ࠥ࡬ࡴࡵ࡫ࡠࡰࡤࡱࡪࠨᗸ")
    bstack1l111l11lll_opy_ = bstack1111l1_opy_ (u"ࠦࡱࡵࡧࡴࠤᗹ")
    bstack1l111l1llll_opy_ = bstack1111l1_opy_ (u"ࠧࡩࡵࡴࡶࡲࡱࡤࡳࡥࡵࡣࡧࡥࡹࡧࠢᗺ")
    bstack1l11111ll11_opy_ = bstack1111l1_opy_ (u"ࠨࡰࡦࡰࡧ࡭ࡳ࡭ࠢᗻ")
    bstack1l1111l1l1l_opy_ = bstack1111l1_opy_ (u"ࠢࡱࡧࡱࡨ࡮ࡴࡧࠣᗼ")
    bstack1l1ll11ll11_opy_ = bstack1111l1_opy_ (u"ࠣࡖࡈࡗ࡙ࡥࡓࡄࡔࡈࡉࡓ࡙ࡈࡐࡖࠥᗽ")
    bstack1l1l1ll111l_opy_ = bstack1111l1_opy_ (u"ࠤࡗࡉࡘ࡚࡟ࡍࡑࡊࠦᗾ")
    bstack1l1lll1111l_opy_ = bstack1111l1_opy_ (u"ࠥࡘࡊ࡙ࡔࡠࡃࡗࡘࡆࡉࡈࡎࡇࡑࡘࠧᗿ")
    bstack1lllll1111l_opy_: Dict[str, bstack1ll1llll1l1_opy_] = dict()
    bstack11lll1lll1l_opy_: Dict[str, List[Callable]] = dict()
    bstack1ll11lll11l_opy_: List[str]
    bstack11lllll1ll1_opy_: Dict[str, str]
    def __init__(
        self,
        bstack1ll11lll11l_opy_: List[str],
        bstack11lllll1ll1_opy_: Dict[str, str],
        bstack1lllllll1l1_opy_: bstack1lllllll1ll_opy_
    ):
        self.bstack1ll11lll11l_opy_ = bstack1ll11lll11l_opy_
        self.bstack11lllll1ll1_opy_ = bstack11lllll1ll1_opy_
        self.bstack1lllllll1l1_opy_ = bstack1lllllll1l1_opy_
    def track_event(
        self,
        context: bstack11llll1l1ll_opy_,
        test_framework_state: bstack1ll1ll1lll1_opy_,
        test_hook_state: bstack1lll11l11ll_opy_,
        *args,
        **kwargs,
    ):
        self.logger.debug(bstack1111l1_opy_ (u"ࠦࡹࡸࡡࡤ࡭ࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡸࡪࡹࡴࡠࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࡣࡸࡺࡡࡵࡧࡀࡿࢂࠦࡴࡦࡵࡷࡣ࡭ࡵ࡯࡬ࡡࡶࡸࡦࡺࡥ࠾ࡽࢀࠤࡦࡸࡧࡴ࠿ࡾࢁࠥࡱࡷࡢࡴࡪࡷࡂࢁࡽࠣᘀ").format(test_framework_state,test_hook_state,args,kwargs))
    def bstack11llllll1ll_opy_(
        self,
        instance: bstack1ll1llll1l1_opy_,
        bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_],
        *args,
        **kwargs,
    ):
        bstack1l111lll1l1_opy_ = TestFramework.bstack1l111lll111_opy_(bstack1llll1ll1l1_opy_)
        if not bstack1l111lll1l1_opy_ in TestFramework.bstack11lll1lll1l_opy_:
            return
        self.logger.debug(bstack1111l1_opy_ (u"ࠧ࡯࡮ࡷࡱ࡮࡭ࡳ࡭ࠠࡼࡿࠣࡧࡦࡲ࡬ࡣࡣࡦ࡯ࡸࠨᘁ").format(len(TestFramework.bstack11lll1lll1l_opy_[bstack1l111lll1l1_opy_])))
        for callback in TestFramework.bstack11lll1lll1l_opy_[bstack1l111lll1l1_opy_]:
            try:
                callback(self, instance, bstack1llll1ll1l1_opy_, *args, **kwargs)
            except Exception as e:
                self.logger.error(bstack1111l1_opy_ (u"ࠨࡥࡳࡴࡲࡶࠥ࡯࡮ࡷࡱ࡮࡭ࡳ࡭ࠠࡤࡣ࡯ࡰࡧࡧࡣ࡬࠼ࠣࡿࢂࠨᘂ").format(e))
                traceback.print_exc()
    @abc.abstractmethod
    def bstack1l1ll1l1111_opy_(self):
        return
    @abc.abstractmethod
    def bstack1l1l1ll11ll_opy_(self, instance, bstack1llll1ll1l1_opy_):
        return
    @abc.abstractmethod
    def bstack1l1ll111lll_opy_(self, instance, bstack1llll1ll1l1_opy_):
        return
    @staticmethod
    def bstack1llll1l1lll_opy_(target: object, strict=True):
        if target is None:
            return None
        ctx = bstack1lllll11l1l_opy_.create_context(target)
        instance = TestFramework.bstack1lllll1111l_opy_.get(ctx.id, None)
        if instance and instance.bstack1llll1lll1l_opy_(target):
            return instance
        return instance if instance and not strict else None
    @staticmethod
    def bstack1l1ll1ll11l_opy_(reverse=True) -> List[bstack1ll1llll1l1_opy_]:
        thread_id = threading.get_ident()
        process_id = os.getpid()
        return sorted(
            filter(
                lambda t: t.context.thread_id == thread_id
                and t.context.process_id == process_id,
                TestFramework.bstack1lllll1111l_opy_.values(),
            ),
            key=lambda t: t.bstack1lllll1l1ll_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1llll11llll_opy_(ctx: bstack1lllll1ll11_opy_, reverse=True) -> List[bstack1ll1llll1l1_opy_]:
        return sorted(
            filter(
                lambda t: t.context.thread_id == ctx.thread_id
                and t.context.process_id == ctx.process_id,
                TestFramework.bstack1lllll1111l_opy_.values(),
            ),
            key=lambda t: t.bstack1lllll1l1ll_opy_,
            reverse=reverse,
        )
    @staticmethod
    def bstack1llll1l1ll1_opy_(instance: bstack1ll1llll1l1_opy_, key: str):
        return instance and key in instance.data
    @staticmethod
    def bstack1lllll111l1_opy_(instance: bstack1ll1llll1l1_opy_, key: str, default_value=None):
        return instance.data.get(key, default_value) if instance else default_value
    @staticmethod
    def bstack1lllll1l1l1_opy_(instance: bstack1ll1llll1l1_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack1111l1_opy_ (u"ࠢࡴࡧࡷࡣࡸࡺࡡࡵࡧ࠽ࠤ࡮ࡴࡳࡵࡣࡱࡧࡪࡃࡻࡾࠢ࡮ࡩࡾࡃࡻࡾࠢࡹࡥࡱࡻࡥ࠾ࡽࢀࠦᘃ").format(instance.ref(),key,value))
        instance.data[key] = value
        return True
    @staticmethod
    def bstack11llll1l111_opy_(instance: bstack1ll1llll1l1_opy_, entries: Dict[str, Any]):
        TestFramework.logger.debug(bstack1111l1_opy_ (u"ࠣࡵࡨࡸࡤࡹࡴࡢࡶࡨࡣࡪࡴࡴࡳ࡫ࡨࡷ࠿ࠦࡩ࡯ࡵࡷࡥࡳࡩࡥ࠾ࡽࢀࠤࡪࡴࡴࡳ࡫ࡨࡷࡂࢁࡽࠣᘄ").format(instance.ref(),entries,))
        instance.data.update(entries)
        return True
    @staticmethod
    def bstack11lll1l1l1l_opy_(instance: bstack1ll1ll1lll1_opy_, key: str, value: Any):
        TestFramework.logger.debug(bstack1111l1_opy_ (u"ࠤࡸࡴࡩࡧࡴࡦࡡࡶࡸࡦࡺࡥ࠻ࠢ࡬ࡲࡸࡺࡡ࡯ࡥࡨࡁࢀࢃࠠ࡬ࡧࡼࡁࢀࢃࠠࡷࡣ࡯ࡹࡪࡃࡻࡾࠤᘅ").format(instance.ref(),key,value))
        instance.data.update(key, value)
        return True
    @staticmethod
    def get_data(key: str, target: object, strict=True, default_value=None):
        instance = TestFramework.bstack1llll1l1lll_opy_(target, strict)
        return TestFramework.bstack1lllll111l1_opy_(instance, key, default_value)
    @staticmethod
    def set_data(key: str, value: Any, target: object, strict=True):
        instance = TestFramework.bstack1llll1l1lll_opy_(target, strict)
        if not instance:
            return False
        instance.data[key] = value
        return True
    @staticmethod
    def bstack1l111l11ll1_opy_(instance: bstack1ll1llll1l1_opy_, key: str, value: object):
        if instance == None:
            return
        instance.data[key] = value
    @staticmethod
    def bstack1l1111l11l1_opy_(instance: bstack1ll1llll1l1_opy_, key: str):
        return instance.data[key]
    @staticmethod
    def bstack1l111lll111_opy_(bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_]):
        return bstack1111l1_opy_ (u"ࠥ࠾ࠧᘆ").join((bstack1ll1ll1lll1_opy_(bstack1llll1ll1l1_opy_[0]).name, bstack1lll11l11ll_opy_(bstack1llll1ll1l1_opy_[1]).name))
    @staticmethod
    def bstack1ll111111ll_opy_(bstack1llll1ll1l1_opy_: Tuple[bstack1ll1ll1lll1_opy_, bstack1lll11l11ll_opy_], callback: Callable):
        bstack1l111lll1l1_opy_ = TestFramework.bstack1l111lll111_opy_(bstack1llll1ll1l1_opy_)
        TestFramework.logger.debug(bstack1111l1_opy_ (u"ࠦࡸ࡫ࡴࡠࡪࡲࡳࡰࡥࡣࡢ࡮࡯ࡦࡦࡩ࡫࠻ࠢ࡫ࡳࡴࡱ࡟ࡳࡧࡪ࡭ࡸࡺࡲࡺࡡ࡮ࡩࡾࡃࡻࡾࠤᘇ").format(bstack1l111lll1l1_opy_))
        if not bstack1l111lll1l1_opy_ in TestFramework.bstack11lll1lll1l_opy_:
            TestFramework.bstack11lll1lll1l_opy_[bstack1l111lll1l1_opy_] = []
        TestFramework.bstack11lll1lll1l_opy_[bstack1l111lll1l1_opy_].append(callback)
    @staticmethod
    def bstack1l1ll1l1l11_opy_(o):
        klass = o.__class__
        module = klass.__module__
        if module == bstack1111l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡷ࡭ࡳࡹࠢᘈ"):
            return klass.__qualname__
        return module + bstack1111l1_opy_ (u"ࠨ࠮ࠣᘉ") + klass.__qualname__
    @staticmethod
    def bstack1l1l1l1l1ll_opy_(obj, keys, default_value=None):
        return {k: getattr(obj, k, default_value) for k in keys}