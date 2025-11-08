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
from uuid import uuid4
from bstack_utils.helper import bstack11l1l1111l_opy_, bstack11l11l1l11l_opy_
from bstack_utils.bstack1l1l1l11_opy_ import bstack1lllll1lllll_opy_
class bstack1111llll1l_opy_:
    def __init__(self, name=None, code=None, uuid=None, file_path=None, started_at=None, framework=None, tags=[], scope=[], bstack1llll1ll1l11_opy_=None, bstack1llll1llllll_opy_=True, bstack1l1111ll1l1_opy_=None, bstack1ll1llll1l_opy_=None, result=None, duration=None, bstack111l11l1l1_opy_=None, meta={}):
        self.bstack111l11l1l1_opy_ = bstack111l11l1l1_opy_
        self.name = name
        self.code = code
        self.file_path = file_path
        self.uuid = uuid
        if not self.uuid and bstack1llll1llllll_opy_:
            self.uuid = uuid4().__str__()
        self.started_at = started_at
        self.framework = framework
        self.tags = tags
        self.scope = scope
        self.bstack1llll1ll1l11_opy_ = bstack1llll1ll1l11_opy_
        self.bstack1l1111ll1l1_opy_ = bstack1l1111ll1l1_opy_
        self.bstack1ll1llll1l_opy_ = bstack1ll1llll1l_opy_
        self.result = result
        self.duration = duration
        self.meta = meta
        self.hooks = []
    def bstack1111lll111_opy_(self):
        if self.uuid:
            return self.uuid
        self.uuid = uuid4().__str__()
        return self.uuid
    def bstack111l1ll111_opy_(self, meta):
        self.meta = meta
    def bstack111l1lll11_opy_(self, hooks):
        self.hooks = hooks
    def bstack1llll1lll11l_opy_(self):
        bstack1llll1ll11l1_opy_ = os.path.relpath(self.file_path, start=os.getcwd())
        return {
            bstack1111l1_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ₁"): bstack1llll1ll11l1_opy_,
            bstack1111l1_opy_ (u"࠭࡬ࡰࡥࡤࡸ࡮ࡵ࡮ࠨ₂"): bstack1llll1ll11l1_opy_,
            bstack1111l1_opy_ (u"ࠧࡷࡥࡢࡪ࡮ࡲࡥࡱࡣࡷ࡬ࠬ₃"): bstack1llll1ll11l1_opy_
        }
    def set(self, **kwargs):
        for key, val in kwargs.items():
            if not hasattr(self, key):
                raise TypeError(bstack1111l1_opy_ (u"ࠣࡗࡱࡩࡽࡶࡥࡤࡶࡨࡨࠥࡧࡲࡨࡷࡰࡩࡳࡺ࠺ࠡࠤ₄") + key)
            setattr(self, key, val)
    def bstack1llll1llll11_opy_(self):
        return {
            bstack1111l1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ₅"): self.name,
            bstack1111l1_opy_ (u"ࠪࡦࡴࡪࡹࠨ₆"): {
                bstack1111l1_opy_ (u"ࠫࡱࡧ࡮ࡨࠩ₇"): bstack1111l1_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ₈"),
                bstack1111l1_opy_ (u"࠭ࡣࡰࡦࡨࠫ₉"): self.code
            },
            bstack1111l1_opy_ (u"ࠧࡴࡥࡲࡴࡪࡹࠧ₊"): self.scope,
            bstack1111l1_opy_ (u"ࠨࡶࡤ࡫ࡸ࠭₋"): self.tags,
            bstack1111l1_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬ₌"): self.framework,
            bstack1111l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧ₍"): self.started_at
        }
    def bstack1llll1ll111l_opy_(self):
        return {
         bstack1111l1_opy_ (u"ࠫࡲ࡫ࡴࡢࠩ₎"): self.meta
        }
    def bstack1lllll11111l_opy_(self):
        return {
            bstack1111l1_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡗ࡫ࡲࡶࡰࡓࡥࡷࡧ࡭ࠨ₏"): {
                bstack1111l1_opy_ (u"࠭ࡲࡦࡴࡸࡲࡤࡴࡡ࡮ࡧࠪₐ"): self.bstack1llll1ll1l11_opy_
            }
        }
    def bstack1llll1lll1l1_opy_(self, bstack1llll1lll1ll_opy_, details):
        step = next(filter(lambda st: st[bstack1111l1_opy_ (u"ࠧࡪࡦࠪₑ")] == bstack1llll1lll1ll_opy_, self.meta[bstack1111l1_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧₒ")]), None)
        step.update(details)
    def bstack11l11l1ll1_opy_(self, bstack1llll1lll1ll_opy_):
        step = next(filter(lambda st: st[bstack1111l1_opy_ (u"ࠩ࡬ࡨࠬₓ")] == bstack1llll1lll1ll_opy_, self.meta[bstack1111l1_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩₔ")]), None)
        step.update({
            bstack1111l1_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨₕ"): bstack11l1l1111l_opy_()
        })
    def bstack111ll11l1l_opy_(self, bstack1llll1lll1ll_opy_, result, duration=None):
        bstack1l1111ll1l1_opy_ = bstack11l1l1111l_opy_()
        if bstack1llll1lll1ll_opy_ is not None and self.meta.get(bstack1111l1_opy_ (u"ࠬࡹࡴࡦࡲࡶࠫₖ")):
            step = next(filter(lambda st: st[bstack1111l1_opy_ (u"࠭ࡩࡥࠩₗ")] == bstack1llll1lll1ll_opy_, self.meta[bstack1111l1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭ₘ")]), None)
            step.update({
                bstack1111l1_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ₙ"): bstack1l1111ll1l1_opy_,
                bstack1111l1_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࠫₚ"): duration if duration else bstack11l11l1l11l_opy_(step[bstack1111l1_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧₛ")], bstack1l1111ll1l1_opy_),
                bstack1111l1_opy_ (u"ࠫࡷ࡫ࡳࡶ࡮ࡷࠫₜ"): result.result,
                bstack1111l1_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪ࠭₝"): str(result.exception) if result.exception else None
            })
    def add_step(self, bstack1llll1ll1ll1_opy_):
        if self.meta.get(bstack1111l1_opy_ (u"࠭ࡳࡵࡧࡳࡷࠬ₞")):
            self.meta[bstack1111l1_opy_ (u"ࠧࡴࡶࡨࡴࡸ࠭₟")].append(bstack1llll1ll1ll1_opy_)
        else:
            self.meta[bstack1111l1_opy_ (u"ࠨࡵࡷࡩࡵࡹࠧ₠")] = [ bstack1llll1ll1ll1_opy_ ]
    def bstack1llll1llll1l_opy_(self):
        return {
            bstack1111l1_opy_ (u"ࠩࡸࡹ࡮ࡪࠧ₡"): self.bstack1111lll111_opy_(),
            **self.bstack1llll1llll11_opy_(),
            **self.bstack1llll1lll11l_opy_(),
            **self.bstack1llll1ll111l_opy_()
        }
    def bstack1llll1lll111_opy_(self):
        if not self.result:
            return {}
        data = {
            bstack1111l1_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨ₢"): self.bstack1l1111ll1l1_opy_,
            bstack1111l1_opy_ (u"ࠫࡩࡻࡲࡢࡶ࡬ࡳࡳࡥࡩ࡯ࡡࡰࡷࠬ₣"): self.duration,
            bstack1111l1_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬ₤"): self.result.result
        }
        if data[bstack1111l1_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭₥")] == bstack1111l1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧ₦"):
            data[bstack1111l1_opy_ (u"ࠨࡨࡤ࡭ࡱࡻࡲࡦࡡࡷࡽࡵ࡫ࠧ₧")] = self.result.bstack11111111l1_opy_()
            data[bstack1111l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࠪ₨")] = [{bstack1111l1_opy_ (u"ࠪࡦࡦࡩ࡫ࡵࡴࡤࡧࡪ࠭₩"): self.result.bstack111lll1111l_opy_()}]
        return data
    def bstack1llll1ll1lll_opy_(self):
        return {
            bstack1111l1_opy_ (u"ࠫࡺࡻࡩࡥࠩ₪"): self.bstack1111lll111_opy_(),
            **self.bstack1llll1llll11_opy_(),
            **self.bstack1llll1lll11l_opy_(),
            **self.bstack1llll1lll111_opy_(),
            **self.bstack1llll1ll111l_opy_()
        }
    def bstack1111ll1lll_opy_(self, event, result=None):
        if result:
            self.result = result
        if bstack1111l1_opy_ (u"࡙ࠬࡴࡢࡴࡷࡩࡩ࠭₫") in event:
            return self.bstack1llll1llll1l_opy_()
        elif bstack1111l1_opy_ (u"࠭ࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨ€") in event:
            return self.bstack1llll1ll1lll_opy_()
    def bstack111l1111ll_opy_(self):
        pass
    def stop(self, time=None, duration=None, result=None):
        self.bstack1l1111ll1l1_opy_ = time if time else bstack11l1l1111l_opy_()
        self.duration = duration if duration else bstack11l11l1l11l_opy_(self.started_at, self.bstack1l1111ll1l1_opy_)
        if result:
            self.result = result
class bstack111ll1llll_opy_(bstack1111llll1l_opy_):
    def __init__(self, hooks=[], bstack111ll1l11l_opy_={}, *args, **kwargs):
        self.hooks = hooks
        self.bstack111ll1l11l_opy_ = bstack111ll1l11l_opy_
        super().__init__(*args, **kwargs, bstack1ll1llll1l_opy_=bstack1111l1_opy_ (u"ࠧࡵࡧࡶࡸࠬ₭"))
    @classmethod
    def bstack1lllll111111_opy_(cls, scenario, feature, test, **kwargs):
        steps = []
        for step in scenario.steps:
            steps.append({
                bstack1111l1_opy_ (u"ࠨ࡫ࡧࠫ₮"): id(step),
                bstack1111l1_opy_ (u"ࠩࡷࡩࡽࡺࠧ₯"): step.name,
                bstack1111l1_opy_ (u"ࠪ࡯ࡪࡿࡷࡰࡴࡧࠫ₰"): step.keyword,
            })
        return bstack111ll1llll_opy_(
            **kwargs,
            meta={
                bstack1111l1_opy_ (u"ࠫ࡫࡫ࡡࡵࡷࡵࡩࠬ₱"): {
                    bstack1111l1_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ₲"): feature.name,
                    bstack1111l1_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ₳"): feature.filename,
                    bstack1111l1_opy_ (u"ࠧࡥࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠬ₴"): feature.description
                },
                bstack1111l1_opy_ (u"ࠨࡵࡦࡩࡳࡧࡲࡪࡱࠪ₵"): {
                    bstack1111l1_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ₶"): scenario.name
                },
                bstack1111l1_opy_ (u"ࠪࡷࡹ࡫ࡰࡴࠩ₷"): steps,
                bstack1111l1_opy_ (u"ࠫࡪࡾࡡ࡮ࡲ࡯ࡩࡸ࠭₸"): bstack1lllll1lllll_opy_(test)
            }
        )
    def bstack1llll1lllll1_opy_(self):
        return {
            bstack1111l1_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫ₹"): self.hooks
        }
    def bstack1llll1ll11ll_opy_(self):
        if self.bstack111ll1l11l_opy_:
            return {
                bstack1111l1_opy_ (u"࠭ࡩ࡯ࡶࡨ࡫ࡷࡧࡴࡪࡱࡱࡷࠬ₺"): self.bstack111ll1l11l_opy_
            }
        return {}
    def bstack1llll1ll1lll_opy_(self):
        return {
            **super().bstack1llll1ll1lll_opy_(),
            **self.bstack1llll1lllll1_opy_()
        }
    def bstack1llll1llll1l_opy_(self):
        return {
            **super().bstack1llll1llll1l_opy_(),
            **self.bstack1llll1ll11ll_opy_()
        }
    def bstack111l1111ll_opy_(self):
        return bstack1111l1_opy_ (u"ࠧࡵࡧࡶࡸࡤࡸࡵ࡯ࠩ₻")
class bstack111ll1l111_opy_(bstack1111llll1l_opy_):
    def __init__(self, hook_type, *args,bstack111ll1l11l_opy_={}, **kwargs):
        self.hook_type = hook_type
        self.bstack1ll11111l11_opy_ = None
        self.bstack111ll1l11l_opy_ = bstack111ll1l11l_opy_
        super().__init__(*args, **kwargs, bstack1ll1llll1l_opy_=bstack1111l1_opy_ (u"ࠨࡪࡲࡳࡰ࠭₼"))
    def bstack111l1l1l11_opy_(self):
        return self.hook_type
    def bstack1llll1ll1l1l_opy_(self):
        return {
            bstack1111l1_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬ₽"): self.hook_type
        }
    def bstack1llll1ll1lll_opy_(self):
        return {
            **super().bstack1llll1ll1lll_opy_(),
            **self.bstack1llll1ll1l1l_opy_()
        }
    def bstack1llll1llll1l_opy_(self):
        return {
            **super().bstack1llll1llll1l_opy_(),
            bstack1111l1_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤ࡯ࡤࠨ₾"): self.bstack1ll11111l11_opy_,
            **self.bstack1llll1ll1l1l_opy_()
        }
    def bstack111l1111ll_opy_(self):
        return bstack1111l1_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡡࡵࡹࡳ࠭₿")
    def bstack111l1lllll_opy_(self, bstack1ll11111l11_opy_):
        self.bstack1ll11111l11_opy_ = bstack1ll11111l11_opy_