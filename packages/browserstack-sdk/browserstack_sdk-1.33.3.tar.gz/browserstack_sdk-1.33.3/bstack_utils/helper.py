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
import collections
import datetime
import json
import os
import platform
import re
import subprocess
import traceback
import tempfile
import multiprocessing
import threading
import sys
import logging
from math import ceil
from unittest import result
import urllib
from urllib.parse import urlparse
import copy
import zipfile
import git
import requests
from packaging import version
from bstack_utils.config import Config
from bstack_utils.constants import (bstack1lllll11l1_opy_, bstack1l1111ll1l_opy_, bstack1l1l1llll1_opy_,
                                    bstack11l1lll1111_opy_, bstack11l1ll111ll_opy_, bstack11l1ll1l1l1_opy_, bstack11l1l11lll1_opy_)
from bstack_utils.measure import measure
from bstack_utils.messages import bstack111l1l1l1_opy_, bstack1l111llll_opy_
from bstack_utils.proxy import bstack11ll1l1l1l_opy_, bstack11lllll1ll_opy_
from bstack_utils.constants import *
from bstack_utils import bstack1lll1l11l_opy_
from bstack_utils.bstack1l1lllll1_opy_ import bstack11ll111l1_opy_
from browserstack_sdk._version import __version__
bstack11ll1l111l_opy_ = Config.bstack1l1l1l1111_opy_()
logger = bstack1lll1l11l_opy_.get_logger(__name__, bstack1lll1l11l_opy_.bstack1lll1111l1l_opy_())
def bstack11ll11lllll_opy_(config):
    return config[bstack1111l1_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧᬺ")]
def bstack11ll1ll111l_opy_(config):
    return config[bstack1111l1_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩᬻ")]
def bstack11111l11_opy_():
    try:
        import playwright
        return True
    except ImportError:
        return False
def bstack111llll11ll_opy_(obj):
    values = []
    bstack111lll11ll1_opy_ = re.compile(bstack1111l1_opy_ (u"ࡲࠣࡠࡆ࡙ࡘ࡚ࡏࡎࡡࡗࡅࡌࡥ࡜ࡥ࠭ࠧࠦᬼ"), re.I)
    for key in obj.keys():
        if bstack111lll11ll1_opy_.match(key):
            values.append(obj[key])
    return values
def bstack11l11l11lll_opy_(config):
    tags = []
    tags.extend(bstack111llll11ll_opy_(os.environ))
    tags.extend(bstack111llll11ll_opy_(config))
    return tags
def bstack111llllll1l_opy_(markers):
    tags = []
    for marker in markers:
        tags.append(marker.name)
    return tags
def bstack111llll1lll_opy_(bstack111ll1l11ll_opy_):
    if not bstack111ll1l11ll_opy_:
        return bstack1111l1_opy_ (u"ࠨࠩᬽ")
    return bstack1111l1_opy_ (u"ࠤࡾࢁࠥ࠮ࡻࡾࠫࠥᬾ").format(bstack111ll1l11ll_opy_.name, bstack111ll1l11ll_opy_.email)
def bstack11ll11lll11_opy_():
    try:
        repo = git.Repo(search_parent_directories=True)
        bstack11l111lllll_opy_ = repo.common_dir
        info = {
            bstack1111l1_opy_ (u"ࠥࡷ࡭ࡧࠢᬿ"): repo.head.commit.hexsha,
            bstack1111l1_opy_ (u"ࠦࡸ࡮࡯ࡳࡶࡢࡷ࡭ࡧࠢᭀ"): repo.git.rev_parse(repo.head.commit, short=True),
            bstack1111l1_opy_ (u"ࠧࡨࡲࡢࡰࡦ࡬ࠧᭁ"): repo.active_branch.name,
            bstack1111l1_opy_ (u"ࠨࡴࡢࡩࠥᭂ"): repo.git.describe(all=True, tags=True, exact_match=True),
            bstack1111l1_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡴࡦࡴࠥᭃ"): bstack111llll1lll_opy_(repo.head.commit.committer),
            bstack1111l1_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡵࡧࡵࡣࡩࡧࡴࡦࠤ᭄"): repo.head.commit.committed_datetime.isoformat(),
            bstack1111l1_opy_ (u"ࠤࡤࡹࡹ࡮࡯ࡳࠤᭅ"): bstack111llll1lll_opy_(repo.head.commit.author),
            bstack1111l1_opy_ (u"ࠥࡥࡺࡺࡨࡰࡴࡢࡨࡦࡺࡥࠣᭆ"): repo.head.commit.authored_datetime.isoformat(),
            bstack1111l1_opy_ (u"ࠦࡨࡵ࡭࡮࡫ࡷࡣࡲ࡫ࡳࡴࡣࡪࡩࠧᭇ"): repo.head.commit.message,
            bstack1111l1_opy_ (u"ࠧࡸ࡯ࡰࡶࠥᭈ"): repo.git.rev_parse(bstack1111l1_opy_ (u"ࠨ࠭࠮ࡵ࡫ࡳࡼ࠳ࡴࡰࡲ࡯ࡩࡻ࡫࡬ࠣᭉ")),
            bstack1111l1_opy_ (u"ࠢࡤࡱࡰࡱࡴࡴ࡟ࡨ࡫ࡷࡣࡩ࡯ࡲࠣᭊ"): bstack11l111lllll_opy_,
            bstack1111l1_opy_ (u"ࠣࡹࡲࡶࡰࡺࡲࡦࡧࡢ࡫࡮ࡺ࡟ࡥ࡫ࡵࠦᭋ"): subprocess.check_output([bstack1111l1_opy_ (u"ࠤࡪ࡭ࡹࠨᭌ"), bstack1111l1_opy_ (u"ࠥࡶࡪࡼ࠭ࡱࡣࡵࡷࡪࠨ᭍"), bstack1111l1_opy_ (u"ࠦ࠲࠳ࡧࡪࡶ࠰ࡧࡴࡳ࡭ࡰࡰ࠰ࡨ࡮ࡸࠢ᭎")]).strip().decode(
                bstack1111l1_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫ᭏")),
            bstack1111l1_opy_ (u"ࠨ࡬ࡢࡵࡷࡣࡹࡧࡧࠣ᭐"): repo.git.describe(tags=True, abbrev=0, always=True),
            bstack1111l1_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡳࡠࡵ࡬ࡲࡨ࡫࡟࡭ࡣࡶࡸࡤࡺࡡࡨࠤ᭑"): repo.git.rev_list(
                bstack1111l1_opy_ (u"ࠣࡽࢀ࠲࠳ࢁࡽࠣ᭒").format(repo.head.commit, repo.git.describe(tags=True, abbrev=0, always=True)), count=True)
        }
        remotes = repo.remotes
        bstack111ll1lllll_opy_ = []
        for remote in remotes:
            bstack11l11111ll1_opy_ = {
                bstack1111l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ᭓"): remote.name,
                bstack1111l1_opy_ (u"ࠥࡹࡷࡲࠢ᭔"): remote.url,
            }
            bstack111ll1lllll_opy_.append(bstack11l11111ll1_opy_)
        bstack111lllll111_opy_ = {
            bstack1111l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤ᭕"): bstack1111l1_opy_ (u"ࠧ࡭ࡩࡵࠤ᭖"),
            **info,
            bstack1111l1_opy_ (u"ࠨࡲࡦ࡯ࡲࡸࡪࡹࠢ᭗"): bstack111ll1lllll_opy_
        }
        bstack111lllll111_opy_ = bstack11l111ll111_opy_(bstack111lllll111_opy_)
        return bstack111lllll111_opy_
    except git.InvalidGitRepositoryError:
        return {}
    except Exception as err:
        print(bstack1111l1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡰࡲࡸࡰࡦࡺࡩ࡯ࡩࠣࡋ࡮ࡺࠠ࡮ࡧࡷࡥࡩࡧࡴࡢࠢࡺ࡭ࡹ࡮ࠠࡦࡴࡵࡳࡷࡀࠠࡼࡿࠥ᭘").format(err))
        return {}
def bstack11l11l1lll1_opy_(bstack111ll1ll111_opy_=None):
    bstack1111l1_opy_ (u"ࠣࠤࠥࠎࠥࠦࠠࠡࡉࡨࡸࠥ࡭ࡩࡵࠢࡰࡩࡹࡧࡤࡢࡶࡤࠤࡸࡶࡥࡤ࡫ࡩ࡭ࡨࡧ࡬࡭ࡻࠣࡪࡴࡸ࡭ࡢࡶࡷࡩࡩࠦࡦࡰࡴࠣࡅࡎࠦࡳࡦ࡮ࡨࡧࡹ࡯࡯࡯ࠢࡸࡷࡪࠦࡣࡢࡵࡨࡷࠥ࡬࡯ࡳࠢࡨࡥࡨ࡮ࠠࡧࡱ࡯ࡨࡪࡸࠠࡪࡰࠣࡸ࡭࡫ࠠ࡭࡫ࡶࡸ࠳ࠐࠠࠡࠢࠣࡅࡷ࡭ࡳ࠻ࠌࠣࠤࠥࠦࠠࠡࠢࠣࡪࡴࡲࡤࡦࡴࡶࠤ࠭ࡲࡩࡴࡶ࠯ࠤࡴࡶࡴࡪࡱࡱࡥࡱ࠯࠺ࠡࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡑࡳࡳ࡫࠺ࠡࡏࡲࡲࡴ࠳ࡲࡦࡲࡲࠤࡦࡶࡰࡳࡱࡤࡧ࡭࠲ࠠࡶࡵࡨࡷࠥࡩࡵࡳࡴࡨࡲࡹࠦࡤࡪࡴࡨࡧࡹࡵࡲࡺࠢ࡞ࡳࡸ࠴ࡧࡦࡶࡦࡻࡩ࠮ࠩ࡞ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠ࠮ࠢࡈࡱࡵࡺࡹࠡ࡮࡬ࡷࡹ࡛ࠦ࡞࠼ࠣࡑࡺࡲࡴࡪ࠯ࡵࡩࡵࡵࠠࡢࡲࡳࡶࡴࡧࡣࡩࠢࡺ࡭ࡹ࡮ࠠ࡯ࡱࠣࡷࡴࡻࡲࡤࡧࡶࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷ࡫ࡤ࠭ࠢࡵࡩࡹࡻࡲ࡯ࡵࠣ࡟ࡢࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤ࠲ࠦࡌࡪࡵࡷࠤࡴ࡬ࠠࡱࡣࡷ࡬ࡸࡀࠠࡎࡷ࡯ࡸ࡮࠳ࡲࡦࡲࡲࠤࡦࡶࡰࡳࡱࡤࡧ࡭ࠦࡷࡪࡶ࡫ࠤࡸࡶࡥࡤ࡫ࡩ࡭ࡨࠦࡦࡰ࡮ࡧࡩࡷࡹࠠࡵࡱࠣࡥࡳࡧ࡬ࡺࡼࡨࠎࠥࠦࠠࠡࡔࡨࡸࡺࡸ࡮ࡴ࠼ࠍࠤࠥࠦࠠࠡࠢࠣࠤࡱ࡯ࡳࡵ࠼ࠣࡐ࡮ࡹࡴࠡࡱࡩࠤࡩ࡯ࡣࡵࡵ࠯ࠤࡪࡧࡣࡩࠢࡦࡳࡳࡺࡡࡪࡰ࡬ࡲ࡬ࠦࡧࡪࡶࠣࡱࡪࡺࡡࡥࡣࡷࡥࠥ࡬࡯ࡳࠢࡤࠤ࡫ࡵ࡬ࡥࡧࡵ࠲ࠏࠦࠠࠡࠢࠥࠦࠧ᭙")
    if bstack111ll1ll111_opy_ is None:
        bstack111ll1ll111_opy_ = [os.getcwd()]
    elif isinstance(bstack111ll1ll111_opy_, list) and len(bstack111ll1ll111_opy_) == 0:
        return []
    results = []
    for folder in bstack111ll1ll111_opy_:
        try:
            if not os.path.exists(folder):
                raise Exception(bstack1111l1_opy_ (u"ࠤࡉࡳࡱࡪࡥࡳࠢࡧࡳࡪࡹࠠ࡯ࡱࡷࠤࡪࡾࡩࡴࡶ࠽ࠤࢀࢃࠢ᭚").format(folder))
            repo = git.Repo(folder, search_parent_directories=True)
            result = {
                bstack1111l1_opy_ (u"ࠥࡴࡷࡏࡤࠣ᭛"): bstack1111l1_opy_ (u"ࠦࠧ᭜"),
                bstack1111l1_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡶࡇ࡭ࡧ࡮ࡨࡧࡧࠦ᭝"): [],
                bstack1111l1_opy_ (u"ࠨࡡࡶࡶ࡫ࡳࡷࡹࠢ᭞"): [],
                bstack1111l1_opy_ (u"ࠢࡱࡴࡇࡥࡹ࡫ࠢ᭟"): bstack1111l1_opy_ (u"ࠣࠤ᭠"),
                bstack1111l1_opy_ (u"ࠤࡦࡳࡲࡳࡩࡵࡏࡨࡷࡸࡧࡧࡦࡵࠥ᭡"): [],
                bstack1111l1_opy_ (u"ࠥࡴࡷ࡚ࡩࡵ࡮ࡨࠦ᭢"): bstack1111l1_opy_ (u"ࠦࠧ᭣"),
                bstack1111l1_opy_ (u"ࠧࡶࡲࡅࡧࡶࡧࡷ࡯ࡰࡵ࡫ࡲࡲࠧ᭤"): bstack1111l1_opy_ (u"ࠨࠢ᭥"),
                bstack1111l1_opy_ (u"ࠢࡱࡴࡕࡥࡼࡊࡩࡧࡨࠥ᭦"): bstack1111l1_opy_ (u"ࠣࠤ᭧")
            }
            bstack111ll11l1ll_opy_ = repo.active_branch.name
            bstack11l11ll1l1l_opy_ = repo.head.commit
            result[bstack1111l1_opy_ (u"ࠤࡳࡶࡎࡪࠢ᭨")] = bstack11l11ll1l1l_opy_.hexsha
            bstack111lll11111_opy_ = _11l111111l1_opy_(repo)
            logger.debug(bstack1111l1_opy_ (u"ࠥࡆࡦࡹࡥࠡࡤࡵࡥࡳࡩࡨࠡࡨࡲࡶࠥࡩ࡯࡮ࡲࡤࡶ࡮ࡹ࡯࡯࠼ࠣࠦ᭩") + str(bstack111lll11111_opy_) + bstack1111l1_opy_ (u"ࠦࠧ᭪"))
            if bstack111lll11111_opy_:
                try:
                    bstack111lll111l1_opy_ = repo.git.diff(bstack1111l1_opy_ (u"ࠧ࠳࠭࡯ࡣࡰࡩ࠲ࡵ࡮࡭ࡻࠥ᭫"), bstack11111l1ll1_opy_ (u"ࠨࡻࡣࡣࡶࡩࡤࡨࡲࡢࡰࡦ࡬ࢂ࠴࠮࠯ࡽࡦࡹࡷࡸࡥ࡯ࡶࡢࡦࡷࡧ࡮ࡤࡪࢀ᭬ࠦ")).split(bstack1111l1_opy_ (u"ࠧ࡝ࡰࠪ᭭"))
                    logger.debug(bstack1111l1_opy_ (u"ࠣࡅ࡫ࡥࡳ࡭ࡥࡥࠢࡩ࡭ࡱ࡫ࡳࠡࡤࡨࡸࡼ࡫ࡥ࡯ࠢࡾࡦࡦࡹࡥࡠࡤࡵࡥࡳࡩࡨࡾࠢࡤࡲࡩࠦࡻࡤࡷࡵࡶࡪࡴࡴࡠࡤࡵࡥࡳࡩࡨࡾ࠼ࠣࠦ᭮") + str(bstack111lll111l1_opy_) + bstack1111l1_opy_ (u"ࠤࠥ᭯"))
                    result[bstack1111l1_opy_ (u"ࠥࡪ࡮ࡲࡥࡴࡅ࡫ࡥࡳ࡭ࡥࡥࠤ᭰")] = [f.strip() for f in bstack111lll111l1_opy_ if f.strip()]
                    commits = list(repo.iter_commits(bstack11111l1ll1_opy_ (u"ࠦࢀࡨࡡࡴࡧࡢࡦࡷࡧ࡮ࡤࡪࢀ࠲࠳ࢁࡣࡶࡴࡵࡩࡳࡺ࡟ࡣࡴࡤࡲࡨ࡮ࡽࠣ᭱")))
                except Exception:
                    logger.debug(bstack1111l1_opy_ (u"ࠧࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡩࡨࡸࠥࡩࡨࡢࡰࡪࡩࡩࠦࡦࡪ࡮ࡨࡷࠥ࡬ࡲࡰ࡯ࠣࡦࡷࡧ࡮ࡤࡪࠣࡧࡴࡳࡰࡢࡴ࡬ࡷࡴࡴ࠮ࠡࡈࡤࡰࡱ࡯࡮ࡨࠢࡥࡥࡨࡱࠠࡵࡱࠣࡶࡪࡩࡥ࡯ࡶࠣࡧࡴࡳ࡭ࡪࡶࡶ࠲ࠧ᭲"))
                    commits = list(repo.iter_commits(max_count=10))
                    if commits:
                        result[bstack1111l1_opy_ (u"ࠨࡦࡪ࡮ࡨࡷࡈ࡮ࡡ࡯ࡩࡨࡨࠧ᭳")] = _111llll1l11_opy_(commits[:5])
            else:
                commits = list(repo.iter_commits(max_count=10))
                if commits:
                    result[bstack1111l1_opy_ (u"ࠢࡧ࡫࡯ࡩࡸࡉࡨࡢࡰࡪࡩࡩࠨ᭴")] = _111llll1l11_opy_(commits[:5])
            bstack111lll1l111_opy_ = set()
            bstack11l111l1111_opy_ = []
            for commit in commits:
                logger.debug(bstack1111l1_opy_ (u"ࠣࡒࡵࡳࡨ࡫ࡳࡴ࡫ࡱ࡫ࠥࡩ࡯࡮࡯࡬ࡸ࠿ࠦࠢ᭵") + str(commit.message) + bstack1111l1_opy_ (u"ࠤࠥ᭶"))
                bstack11l11ll1l11_opy_ = commit.author.name if commit.author else bstack1111l1_opy_ (u"࡙ࠥࡳࡱ࡮ࡰࡹࡱࠦ᭷")
                bstack111lll1l111_opy_.add(bstack11l11ll1l11_opy_)
                bstack11l111l1111_opy_.append({
                    bstack1111l1_opy_ (u"ࠦࡲ࡫ࡳࡴࡣࡪࡩࠧ᭸"): commit.message.strip(),
                    bstack1111l1_opy_ (u"ࠧࡻࡳࡦࡴࠥ᭹"): bstack11l11ll1l11_opy_
                })
            result[bstack1111l1_opy_ (u"ࠨࡡࡶࡶ࡫ࡳࡷࡹࠢ᭺")] = list(bstack111lll1l111_opy_)
            result[bstack1111l1_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺࡍࡦࡵࡶࡥ࡬࡫ࡳࠣ᭻")] = bstack11l111l1111_opy_
            result[bstack1111l1_opy_ (u"ࠣࡲࡵࡈࡦࡺࡥࠣ᭼")] = bstack11l11ll1l1l_opy_.committed_datetime.strftime(bstack1111l1_opy_ (u"ࠤࠨ࡝࠲ࠫ࡭࠮ࠧࡧࠦ᭽"))
            if (not result[bstack1111l1_opy_ (u"ࠥࡴࡷ࡚ࡩࡵ࡮ࡨࠦ᭾")] or result[bstack1111l1_opy_ (u"ࠦࡵࡸࡔࡪࡶ࡯ࡩࠧ᭿")].strip() == bstack1111l1_opy_ (u"ࠧࠨᮀ")) and bstack11l11ll1l1l_opy_.message:
                bstack111ll1lll1l_opy_ = bstack11l11ll1l1l_opy_.message.strip().splitlines()
                result[bstack1111l1_opy_ (u"ࠨࡰࡳࡖ࡬ࡸࡱ࡫ࠢᮁ")] = bstack111ll1lll1l_opy_[0] if bstack111ll1lll1l_opy_ else bstack1111l1_opy_ (u"ࠢࠣᮂ")
                if len(bstack111ll1lll1l_opy_) > 2:
                    result[bstack1111l1_opy_ (u"ࠣࡲࡵࡈࡪࡹࡣࡳ࡫ࡳࡸ࡮ࡵ࡮ࠣᮃ")] = bstack1111l1_opy_ (u"ࠩ࡟ࡲࠬᮄ").join(bstack111ll1lll1l_opy_[2:]).strip()
            results.append(result)
        except Exception as err:
            logger.error(bstack1111l1_opy_ (u"ࠥࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡳࡵࡻ࡬ࡢࡶ࡬ࡲ࡬ࠦࡇࡪࡶࠣࡱࡪࡺࡡࡥࡣࡷࡥࠥ࡬࡯ࡳࠢࡄࡍࠥࡹࡥ࡭ࡧࡦࡸ࡮ࡵ࡮ࠡࠪࡩࡳࡱࡪࡥࡳ࠼ࠣࡿࢂ࠯࠺ࠡࡽࢀࠤ࠲ࠦࡻࡾࠤᮅ").format(
                folder,
                type(err).__name__,
                str(err)
            ))
    filtered_results = [
        result
        for result in results
        if _11l11l1111l_opy_(result)
    ]
    return filtered_results
def _11l11l1111l_opy_(result):
    bstack1111l1_opy_ (u"ࠦࠧࠨࠊࠡࠢࠣࠤࡍ࡫࡬ࡱࡧࡵࠤࡹࡵࠠࡤࡪࡨࡧࡰࠦࡩࡧࠢࡤࠤ࡬࡯ࡴࠡ࡯ࡨࡸࡦࡪࡡࡵࡣࠣࡶࡪࡹࡵ࡭ࡶࠣ࡭ࡸࠦࡶࡢ࡮࡬ࡨࠥ࠮࡮ࡰࡰ࠰ࡩࡲࡶࡴࡺࠢࡩ࡭ࡱ࡫ࡳࡄࡪࡤࡲ࡬࡫ࡤࠡࡣࡱࡨࠥࡧࡵࡵࡪࡲࡶࡸ࠯࠮ࠋࠢࠣࠤࠥࠨࠢࠣᮆ")
    return (
        isinstance(result.get(bstack1111l1_opy_ (u"ࠧ࡬ࡩ࡭ࡧࡶࡇ࡭ࡧ࡮ࡨࡧࡧࠦᮇ"), None), list)
        and len(result[bstack1111l1_opy_ (u"ࠨࡦࡪ࡮ࡨࡷࡈ࡮ࡡ࡯ࡩࡨࡨࠧᮈ")]) > 0
        and isinstance(result.get(bstack1111l1_opy_ (u"ࠢࡢࡷࡷ࡬ࡴࡸࡳࠣᮉ"), None), list)
        and len(result[bstack1111l1_opy_ (u"ࠣࡣࡸࡸ࡭ࡵࡲࡴࠤᮊ")]) > 0
    )
def _11l111111l1_opy_(repo):
    bstack1111l1_opy_ (u"ࠤࠥࠦࠏࠦࠠࠡࠢࡗࡶࡾࠦࡴࡰࠢࡧࡩࡹ࡫ࡲ࡮࡫ࡱࡩࠥࡺࡨࡦࠢࡥࡥࡸ࡫ࠠࡣࡴࡤࡲࡨ࡮ࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡩ࡬ࡺࡪࡴࠠࡳࡧࡳࡳࠥࡽࡩࡵࡪࡲࡹࡹࠦࡨࡢࡴࡧࡧࡴࡪࡥࡥࠢࡱࡥࡲ࡫ࡳࠡࡣࡱࡨࠥࡽ࡯ࡳ࡭ࠣࡻ࡮ࡺࡨࠡࡣ࡯ࡰࠥ࡜ࡃࡔࠢࡳࡶࡴࡼࡩࡥࡧࡵࡷ࠳ࠐࠠࠡࠢࠣࡖࡪࡺࡵࡳࡰࡶࠤࡹ࡮ࡥࠡࡦࡨࡪࡦࡻ࡬ࡵࠢࡥࡶࡦࡴࡣࡩࠢ࡬ࡪࠥࡶ࡯ࡴࡵ࡬ࡦࡱ࡫ࠬࠡࡧ࡯ࡷࡪࠦࡎࡰࡰࡨ࠲ࠏࠦࠠࠡࠢࠥࠦࠧᮋ")
    try:
        try:
            origin = repo.remotes.origin
            bstack11l11ll111l_opy_ = origin.refs[bstack1111l1_opy_ (u"ࠪࡌࡊࡇࡄࠨᮌ")]
            target = bstack11l11ll111l_opy_.reference.name
            if target.startswith(bstack1111l1_opy_ (u"ࠫࡴࡸࡩࡨ࡫ࡱ࠳ࠬᮍ")):
                return target
        except Exception:
            pass
        if repo.remotes and repo.remotes.origin.refs:
            for ref in repo.remotes.origin.refs:
                if ref.name.startswith(bstack1111l1_opy_ (u"ࠬࡵࡲࡪࡩ࡬ࡲ࠴࠭ᮎ")):
                    return ref.name
        if repo.heads:
            return repo.heads[0].name
    except Exception:
        pass
    return None
def _111llll1l11_opy_(commits):
    bstack1111l1_opy_ (u"ࠨࠢࠣࠌࠣࠤࠥࠦࡇࡦࡶࠣࡰ࡮ࡹࡴࠡࡱࡩࠤࡨ࡮ࡡ࡯ࡩࡨࡨࠥ࡬ࡩ࡭ࡧࡶࠤ࡫ࡸ࡯࡮ࠢࡤࠤࡱ࡯ࡳࡵࠢࡲࡪࠥࡩ࡯࡮࡯࡬ࡸࡸ࠴ࠊࠡࠢࠣࠤࠧࠨࠢᮏ")
    bstack111lll111l1_opy_ = set()
    try:
        for commit in commits:
            if commit.parents:
                for parent in commit.parents:
                    diff = commit.diff(parent)
                    for bstack11l11ll1111_opy_ in diff:
                        if bstack11l11ll1111_opy_.a_path:
                            bstack111lll111l1_opy_.add(bstack11l11ll1111_opy_.a_path)
                        if bstack11l11ll1111_opy_.b_path:
                            bstack111lll111l1_opy_.add(bstack11l11ll1111_opy_.b_path)
    except Exception:
        pass
    return list(bstack111lll111l1_opy_)
def bstack11l111ll111_opy_(bstack111lllll111_opy_):
    bstack111llll1ll1_opy_ = bstack111ll1llll1_opy_(bstack111lllll111_opy_)
    if bstack111llll1ll1_opy_ and bstack111llll1ll1_opy_ > bstack11l1lll1111_opy_:
        bstack11l11111111_opy_ = bstack111llll1ll1_opy_ - bstack11l1lll1111_opy_
        bstack111lll11l11_opy_ = bstack111lllll11l_opy_(bstack111lllll111_opy_[bstack1111l1_opy_ (u"ࠢࡤࡱࡰࡱ࡮ࡺ࡟࡮ࡧࡶࡷࡦ࡭ࡥࠣᮐ")], bstack11l11111111_opy_)
        bstack111lllll111_opy_[bstack1111l1_opy_ (u"ࠣࡥࡲࡱࡲ࡯ࡴࡠ࡯ࡨࡷࡸࡧࡧࡦࠤᮑ")] = bstack111lll11l11_opy_
        logger.info(bstack1111l1_opy_ (u"ࠤࡗ࡬ࡪࠦࡣࡰ࡯ࡰ࡭ࡹࠦࡨࡢࡵࠣࡦࡪ࡫࡮ࠡࡶࡵࡹࡳࡩࡡࡵࡧࡧ࠲࡙ࠥࡩࡻࡧࠣࡳ࡫ࠦࡣࡰ࡯ࡰ࡭ࡹࠦࡡࡧࡶࡨࡶࠥࡺࡲࡶࡰࡦࡥࡹ࡯࡯࡯ࠢ࡬ࡷࠥࢁࡽࠡࡍࡅࠦᮒ")
                    .format(bstack111ll1llll1_opy_(bstack111lllll111_opy_) / 1024))
    return bstack111lllll111_opy_
def bstack111ll1llll1_opy_(bstack1l1l1111l_opy_):
    try:
        if bstack1l1l1111l_opy_:
            bstack11l11l1llll_opy_ = json.dumps(bstack1l1l1111l_opy_)
            bstack111ll1l1111_opy_ = sys.getsizeof(bstack11l11l1llll_opy_)
            return bstack111ll1l1111_opy_
    except Exception as e:
        logger.debug(bstack1111l1_opy_ (u"ࠥࡗࡴࡳࡥࡵࡪ࡬ࡲ࡬ࠦࡷࡦࡰࡷࠤࡼࡸ࡯࡯ࡩࠣࡻ࡭࡯࡬ࡦࠢࡦࡥࡱࡩࡵ࡭ࡣࡷ࡭ࡳ࡭ࠠࡴ࡫ࡽࡩࠥࡵࡦࠡࡌࡖࡓࡓࠦ࡯ࡣ࡬ࡨࡧࡹࡀࠠࡼࡿࠥᮓ").format(e))
    return -1
def bstack111lllll11l_opy_(field, bstack111lll1lll1_opy_):
    try:
        bstack11l11l1ll1l_opy_ = len(bytes(bstack11l1ll111ll_opy_, bstack1111l1_opy_ (u"ࠫࡺࡺࡦ࠮࠺ࠪᮔ")))
        bstack11l111l1ll1_opy_ = bytes(field, bstack1111l1_opy_ (u"ࠬࡻࡴࡧ࠯࠻ࠫᮕ"))
        bstack111ll111l11_opy_ = len(bstack11l111l1ll1_opy_)
        bstack11l111l1l1l_opy_ = ceil(bstack111ll111l11_opy_ - bstack111lll1lll1_opy_ - bstack11l11l1ll1l_opy_)
        if bstack11l111l1l1l_opy_ > 0:
            bstack111ll11l11l_opy_ = bstack11l111l1ll1_opy_[:bstack11l111l1l1l_opy_].decode(bstack1111l1_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᮖ"), errors=bstack1111l1_opy_ (u"ࠧࡪࡩࡱࡳࡷ࡫ࠧᮗ")) + bstack11l1ll111ll_opy_
            return bstack111ll11l11l_opy_
    except Exception as e:
        logger.debug(bstack1111l1_opy_ (u"ࠣࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡴࡳࡷࡱࡧࡦࡺࡩ࡯ࡩࠣࡪ࡮࡫࡬ࡥ࠮ࠣࡲࡴࡺࡨࡪࡰࡪࠤࡼࡧࡳࠡࡶࡵࡹࡳࡩࡡࡵࡧࡧࠤ࡭࡫ࡲࡦ࠼ࠣࡿࢂࠨᮘ").format(e))
    return field
def bstack1l1l1l111_opy_():
    env = os.environ
    if (bstack1111l1_opy_ (u"ࠤࡍࡉࡓࡑࡉࡏࡕࡢ࡙ࡗࡒࠢᮙ") in env and len(env[bstack1111l1_opy_ (u"ࠥࡎࡊࡔࡋࡊࡐࡖࡣ࡚ࡘࡌࠣᮚ")]) > 0) or (
            bstack1111l1_opy_ (u"ࠦࡏࡋࡎࡌࡋࡑࡗࡤࡎࡏࡎࡇࠥᮛ") in env and len(env[bstack1111l1_opy_ (u"ࠧࡐࡅࡏࡍࡌࡒࡘࡥࡈࡐࡏࡈࠦᮜ")]) > 0):
        return {
            bstack1111l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦᮝ"): bstack1111l1_opy_ (u"ࠢࡋࡧࡱ࡯࡮ࡴࡳࠣᮞ"),
            bstack1111l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦᮟ"): env.get(bstack1111l1_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡗࡕࡐࠧᮠ")),
            bstack1111l1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᮡ"): env.get(bstack1111l1_opy_ (u"ࠦࡏࡕࡂࡠࡐࡄࡑࡊࠨᮢ")),
            bstack1111l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᮣ"): env.get(bstack1111l1_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧᮤ"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠢࡄࡋࠥᮥ")) == bstack1111l1_opy_ (u"ࠣࡶࡵࡹࡪࠨᮦ") and bstack11ll11ll1l_opy_(env.get(bstack1111l1_opy_ (u"ࠤࡆࡍࡗࡉࡌࡆࡅࡌࠦᮧ"))):
        return {
            bstack1111l1_opy_ (u"ࠥࡲࡦࡳࡥࠣᮨ"): bstack1111l1_opy_ (u"ࠦࡈ࡯ࡲࡤ࡮ࡨࡇࡎࠨᮩ"),
            bstack1111l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬᮪ࠣ"): env.get(bstack1111l1_opy_ (u"ࠨࡃࡊࡔࡆࡐࡊࡥࡂࡖࡋࡏࡈࡤ࡛ࡒࡍࠤ᮫")),
            bstack1111l1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᮬ"): env.get(bstack1111l1_opy_ (u"ࠣࡅࡌࡖࡈࡒࡅࡠࡌࡒࡆࠧᮭ")),
            bstack1111l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᮮ"): env.get(bstack1111l1_opy_ (u"ࠥࡇࡎࡘࡃࡍࡇࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࠨᮯ"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠦࡈࡏࠢ᮰")) == bstack1111l1_opy_ (u"ࠧࡺࡲࡶࡧࠥ᮱") and bstack11ll11ll1l_opy_(env.get(bstack1111l1_opy_ (u"ࠨࡔࡓࡃ࡙ࡍࡘࠨ᮲"))):
        return {
            bstack1111l1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ᮳"): bstack1111l1_opy_ (u"ࠣࡖࡵࡥࡻ࡯ࡳࠡࡅࡌࠦ᮴"),
            bstack1111l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧ᮵"): env.get(bstack1111l1_opy_ (u"ࠥࡘࡗࡇࡖࡊࡕࡢࡆ࡚ࡏࡌࡅࡡ࡚ࡉࡇࡥࡕࡓࡎࠥ᮶")),
            bstack1111l1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ᮷"): env.get(bstack1111l1_opy_ (u"࡚ࠧࡒࡂࡘࡌࡗࡤࡐࡏࡃࡡࡑࡅࡒࡋࠢ᮸")),
            bstack1111l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᮹"): env.get(bstack1111l1_opy_ (u"ࠢࡕࡔࡄ࡚ࡎ࡙࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᮺ"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠣࡅࡌࠦᮻ")) == bstack1111l1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᮼ") and env.get(bstack1111l1_opy_ (u"ࠥࡇࡎࡥࡎࡂࡏࡈࠦᮽ")) == bstack1111l1_opy_ (u"ࠦࡨࡵࡤࡦࡵ࡫࡭ࡵࠨᮾ"):
        return {
            bstack1111l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᮿ"): bstack1111l1_opy_ (u"ࠨࡃࡰࡦࡨࡷ࡭࡯ࡰࠣᯀ"),
            bstack1111l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᯁ"): None,
            bstack1111l1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᯂ"): None,
            bstack1111l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᯃ"): None
        }
    if env.get(bstack1111l1_opy_ (u"ࠥࡆࡎ࡚ࡂࡖࡅࡎࡉ࡙ࡥࡂࡓࡃࡑࡇࡍࠨᯄ")) and env.get(bstack1111l1_opy_ (u"ࠦࡇࡏࡔࡃࡗࡆࡏࡊ࡚࡟ࡄࡑࡐࡑࡎ࡚ࠢᯅ")):
        return {
            bstack1111l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᯆ"): bstack1111l1_opy_ (u"ࠨࡂࡪࡶࡥࡹࡨࡱࡥࡵࠤᯇ"),
            bstack1111l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᯈ"): env.get(bstack1111l1_opy_ (u"ࠣࡄࡌࡘࡇ࡛ࡃࡌࡇࡗࡣࡌࡏࡔࡠࡊࡗࡘࡕࡥࡏࡓࡋࡊࡍࡓࠨᯉ")),
            bstack1111l1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᯊ"): None,
            bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᯋ"): env.get(bstack1111l1_opy_ (u"ࠦࡇࡏࡔࡃࡗࡆࡏࡊ࡚࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨᯌ"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠧࡉࡉࠣᯍ")) == bstack1111l1_opy_ (u"ࠨࡴࡳࡷࡨࠦᯎ") and bstack11ll11ll1l_opy_(env.get(bstack1111l1_opy_ (u"ࠢࡅࡔࡒࡒࡊࠨᯏ"))):
        return {
            bstack1111l1_opy_ (u"ࠣࡰࡤࡱࡪࠨᯐ"): bstack1111l1_opy_ (u"ࠤࡇࡶࡴࡴࡥࠣᯑ"),
            bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᯒ"): env.get(bstack1111l1_opy_ (u"ࠦࡉࡘࡏࡏࡇࡢࡆ࡚ࡏࡌࡅࡡࡏࡍࡓࡑࠢᯓ")),
            bstack1111l1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᯔ"): None,
            bstack1111l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᯕ"): env.get(bstack1111l1_opy_ (u"ࠢࡅࡔࡒࡒࡊࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠧᯖ"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠣࡅࡌࠦᯗ")) == bstack1111l1_opy_ (u"ࠤࡷࡶࡺ࡫ࠢᯘ") and bstack11ll11ll1l_opy_(env.get(bstack1111l1_opy_ (u"ࠥࡗࡊࡓࡁࡑࡊࡒࡖࡊࠨᯙ"))):
        return {
            bstack1111l1_opy_ (u"ࠦࡳࡧ࡭ࡦࠤᯚ"): bstack1111l1_opy_ (u"࡙ࠧࡥ࡮ࡣࡳ࡬ࡴࡸࡥࠣᯛ"),
            bstack1111l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡻࡲ࡭ࠤᯜ"): env.get(bstack1111l1_opy_ (u"ࠢࡔࡇࡐࡅࡕࡎࡏࡓࡇࡢࡓࡗࡍࡁࡏࡋ࡝ࡅ࡙ࡏࡏࡏࡡࡘࡖࡑࠨᯝ")),
            bstack1111l1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᯞ"): env.get(bstack1111l1_opy_ (u"ࠤࡖࡉࡒࡇࡐࡉࡑࡕࡉࡤࡐࡏࡃࡡࡑࡅࡒࡋࠢᯟ")),
            bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᯠ"): env.get(bstack1111l1_opy_ (u"ࠦࡘࡋࡍࡂࡒࡋࡓࡗࡋ࡟ࡋࡑࡅࡣࡎࡊࠢᯡ"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠧࡉࡉࠣᯢ")) == bstack1111l1_opy_ (u"ࠨࡴࡳࡷࡨࠦᯣ") and bstack11ll11ll1l_opy_(env.get(bstack1111l1_opy_ (u"ࠢࡈࡋࡗࡐࡆࡈ࡟ࡄࡋࠥᯤ"))):
        return {
            bstack1111l1_opy_ (u"ࠣࡰࡤࡱࡪࠨᯥ"): bstack1111l1_opy_ (u"ࠤࡊ࡭ࡹࡒࡡࡣࠤ᯦"),
            bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᯧ"): env.get(bstack1111l1_opy_ (u"ࠦࡈࡏ࡟ࡋࡑࡅࡣ࡚ࡘࡌࠣᯨ")),
            bstack1111l1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᯩ"): env.get(bstack1111l1_opy_ (u"ࠨࡃࡊࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦᯪ")),
            bstack1111l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᯫ"): env.get(bstack1111l1_opy_ (u"ࠣࡅࡌࡣࡏࡕࡂࡠࡋࡇࠦᯬ"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠤࡆࡍࠧᯭ")) == bstack1111l1_opy_ (u"ࠥࡸࡷࡻࡥࠣᯮ") and bstack11ll11ll1l_opy_(env.get(bstack1111l1_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡎࡍ࡙ࡋࠢᯯ"))):
        return {
            bstack1111l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᯰ"): bstack1111l1_opy_ (u"ࠨࡂࡶ࡫࡯ࡨࡰ࡯ࡴࡦࠤᯱ"),
            bstack1111l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮᯲ࠥ"): env.get(bstack1111l1_opy_ (u"ࠣࡄࡘࡍࡑࡊࡋࡊࡖࡈࡣࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒ᯳ࠢ")),
            bstack1111l1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦ᯴"): env.get(bstack1111l1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡍࡌࡘࡊࡥࡌࡂࡄࡈࡐࠧ᯵")) or env.get(bstack1111l1_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡎࡍ࡙ࡋ࡟ࡑࡋࡓࡉࡑࡏࡎࡆࡡࡑࡅࡒࡋࠢ᯶")),
            bstack1111l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦ᯷"): env.get(bstack1111l1_opy_ (u"ࠨࡂࡖࡋࡏࡈࡐࡏࡔࡆࡡࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣ᯸"))
        }
    if bstack11ll11ll1l_opy_(env.get(bstack1111l1_opy_ (u"ࠢࡕࡈࡢࡆ࡚ࡏࡌࡅࠤ᯹"))):
        return {
            bstack1111l1_opy_ (u"ࠣࡰࡤࡱࡪࠨ᯺"): bstack1111l1_opy_ (u"ࠤ࡙࡭ࡸࡻࡡ࡭ࠢࡖࡸࡺࡪࡩࡰࠢࡗࡩࡦࡳࠠࡔࡧࡵࡺ࡮ࡩࡥࡴࠤ᯻"),
            bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨ᯼"): bstack1111l1_opy_ (u"ࠦࢀࢃࡻࡾࠤ᯽").format(env.get(bstack1111l1_opy_ (u"࡙࡙ࠬࡔࡖࡈࡑࡤ࡚ࡅࡂࡏࡉࡓ࡚ࡔࡄࡂࡖࡌࡓࡓ࡙ࡅࡓࡘࡈࡖ࡚ࡘࡉࠨ᯾")), env.get(bstack1111l1_opy_ (u"࠭ࡓ࡚ࡕࡗࡉࡒࡥࡔࡆࡃࡐࡔࡗࡕࡊࡆࡅࡗࡍࡉ࠭᯿"))),
            bstack1111l1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᰀ"): env.get(bstack1111l1_opy_ (u"ࠣࡕ࡜ࡗ࡙ࡋࡍࡠࡆࡈࡊࡎࡔࡉࡕࡋࡒࡒࡎࡊࠢᰁ")),
            bstack1111l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡰࡸࡱࡧ࡫ࡲࠣᰂ"): env.get(bstack1111l1_opy_ (u"ࠥࡆ࡚ࡏࡌࡅࡡࡅ࡙ࡎࡒࡄࡊࡆࠥᰃ"))
        }
    if bstack11ll11ll1l_opy_(env.get(bstack1111l1_opy_ (u"ࠦࡆࡖࡐࡗࡇ࡜ࡓࡗࠨᰄ"))):
        return {
            bstack1111l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᰅ"): bstack1111l1_opy_ (u"ࠨࡁࡱࡲࡹࡩࡾࡵࡲࠣᰆ"),
            bstack1111l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᰇ"): bstack1111l1_opy_ (u"ࠣࡽࢀ࠳ࡵࡸ࡯࡫ࡧࡦࡸ࠴ࢁࡽ࠰ࡽࢀ࠳ࡧࡻࡩ࡭ࡦࡶ࠳ࢀࢃࠢᰈ").format(env.get(bstack1111l1_opy_ (u"ࠩࡄࡔࡕ࡜ࡅ࡚ࡑࡕࡣ࡚ࡘࡌࠨᰉ")), env.get(bstack1111l1_opy_ (u"ࠪࡅࡕࡖࡖࡆ࡛ࡒࡖࡤࡇࡃࡄࡑࡘࡒ࡙ࡥࡎࡂࡏࡈࠫᰊ")), env.get(bstack1111l1_opy_ (u"ࠫࡆࡖࡐࡗࡇ࡜ࡓࡗࡥࡐࡓࡑࡍࡉࡈ࡚࡟ࡔࡎࡘࡋࠬᰋ")), env.get(bstack1111l1_opy_ (u"ࠬࡇࡐࡑࡘࡈ࡝ࡔࡘ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠩᰌ"))),
            bstack1111l1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᰍ"): env.get(bstack1111l1_opy_ (u"ࠢࡂࡒࡓ࡚ࡊ࡟ࡏࡓࡡࡍࡓࡇࡥࡎࡂࡏࡈࠦᰎ")),
            bstack1111l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᰏ"): env.get(bstack1111l1_opy_ (u"ࠤࡄࡔࡕ࡜ࡅ࡚ࡑࡕࡣࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࠥᰐ"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠥࡅ࡟࡛ࡒࡆࡡࡋࡘ࡙ࡖ࡟ࡖࡕࡈࡖࡤࡇࡇࡆࡐࡗࠦᰑ")) and env.get(bstack1111l1_opy_ (u"࡙ࠦࡌ࡟ࡃࡗࡌࡐࡉࠨᰒ")):
        return {
            bstack1111l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᰓ"): bstack1111l1_opy_ (u"ࠨࡁࡻࡷࡵࡩࠥࡉࡉࠣᰔ"),
            bstack1111l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᰕ"): bstack1111l1_opy_ (u"ࠣࡽࢀࡿࢂ࠵࡟ࡣࡷ࡬ࡰࡩ࠵ࡲࡦࡵࡸࡰࡹࡹ࠿ࡣࡷ࡬ࡰࡩࡏࡤ࠾ࡽࢀࠦᰖ").format(env.get(bstack1111l1_opy_ (u"ࠩࡖ࡝ࡘ࡚ࡅࡎࡡࡗࡉࡆࡓࡆࡐࡗࡑࡈࡆ࡚ࡉࡐࡐࡖࡉࡗ࡜ࡅࡓࡗࡕࡍࠬᰗ")), env.get(bstack1111l1_opy_ (u"ࠪࡗ࡞࡙ࡔࡆࡏࡢࡘࡊࡇࡍࡑࡔࡒࡎࡊࡉࡔࠨᰘ")), env.get(bstack1111l1_opy_ (u"ࠫࡇ࡛ࡉࡍࡆࡢࡆ࡚ࡏࡌࡅࡋࡇࠫᰙ"))),
            bstack1111l1_opy_ (u"ࠧࡰ࡯ࡣࡡࡱࡥࡲ࡫ࠢᰚ"): env.get(bstack1111l1_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡈࡕࡊࡎࡇࡍࡉࠨᰛ")),
            bstack1111l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥ࡮ࡶ࡯ࡥࡩࡷࠨᰜ"): env.get(bstack1111l1_opy_ (u"ࠣࡄࡘࡍࡑࡊ࡟ࡃࡗࡌࡐࡉࡏࡄࠣᰝ"))
        }
    if any([env.get(bstack1111l1_opy_ (u"ࠤࡆࡓࡉࡋࡂࡖࡋࡏࡈࡤࡈࡕࡊࡎࡇࡣࡎࡊࠢᰞ")), env.get(bstack1111l1_opy_ (u"ࠥࡇࡔࡊࡅࡃࡗࡌࡐࡉࡥࡒࡆࡕࡒࡐ࡛ࡋࡄࡠࡕࡒ࡙ࡗࡉࡅࡠࡘࡈࡖࡘࡏࡏࡏࠤᰟ")), env.get(bstack1111l1_opy_ (u"ࠦࡈࡕࡄࡆࡄࡘࡍࡑࡊ࡟ࡔࡑࡘࡖࡈࡋ࡟ࡗࡇࡕࡗࡎࡕࡎࠣᰠ"))]):
        return {
            bstack1111l1_opy_ (u"ࠧࡴࡡ࡮ࡧࠥᰡ"): bstack1111l1_opy_ (u"ࠨࡁࡘࡕࠣࡇࡴࡪࡥࡃࡷ࡬ࡰࡩࠨᰢ"),
            bstack1111l1_opy_ (u"ࠢࡣࡷ࡬ࡰࡩࡥࡵࡳ࡮ࠥᰣ"): env.get(bstack1111l1_opy_ (u"ࠣࡅࡒࡈࡊࡈࡕࡊࡎࡇࡣࡕ࡛ࡂࡍࡋࡆࡣࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠢᰤ")),
            bstack1111l1_opy_ (u"ࠤ࡭ࡳࡧࡥ࡮ࡢ࡯ࡨࠦᰥ"): env.get(bstack1111l1_opy_ (u"ࠥࡇࡔࡊࡅࡃࡗࡌࡐࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠣᰦ")),
            bstack1111l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡲࡺࡳࡢࡦࡴࠥᰧ"): env.get(bstack1111l1_opy_ (u"ࠧࡉࡏࡅࡇࡅ࡙ࡎࡒࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠥᰨ"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠨࡢࡢ࡯ࡥࡳࡴࡥࡢࡶ࡫࡯ࡨࡓࡻ࡭ࡣࡧࡵࠦᰩ")):
        return {
            bstack1111l1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧᰪ"): bstack1111l1_opy_ (u"ࠣࡄࡤࡱࡧࡵ࡯ࠣᰫ"),
            bstack1111l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᰬ"): env.get(bstack1111l1_opy_ (u"ࠥࡦࡦࡳࡢࡰࡱࡢࡦࡺ࡯࡬ࡥࡔࡨࡷࡺࡲࡴࡴࡗࡵࡰࠧᰭ")),
            bstack1111l1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᰮ"): env.get(bstack1111l1_opy_ (u"ࠧࡨࡡ࡮ࡤࡲࡳࡤࡹࡨࡰࡴࡷࡎࡴࡨࡎࡢ࡯ࡨࠦᰯ")),
            bstack1111l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧᰰ"): env.get(bstack1111l1_opy_ (u"ࠢࡣࡣࡰࡦࡴࡵ࡟ࡣࡷ࡬ࡰࡩࡔࡵ࡮ࡤࡨࡶࠧᰱ"))
        }
    if env.get(bstack1111l1_opy_ (u"࡙ࠣࡈࡖࡈࡑࡅࡓࠤᰲ")) or env.get(bstack1111l1_opy_ (u"ࠤ࡚ࡉࡗࡉࡋࡆࡔࡢࡑࡆࡏࡎࡠࡒࡌࡔࡊࡒࡉࡏࡇࡢࡗ࡙ࡇࡒࡕࡇࡇࠦᰳ")):
        return {
            bstack1111l1_opy_ (u"ࠥࡲࡦࡳࡥࠣᰴ"): bstack1111l1_opy_ (u"ࠦ࡜࡫ࡲࡤ࡭ࡨࡶࠧᰵ"),
            bstack1111l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᰶ"): env.get(bstack1111l1_opy_ (u"ࠨࡗࡆࡔࡆࡏࡊࡘ࡟ࡃࡗࡌࡐࡉࡥࡕࡓࡎ᰷ࠥ")),
            bstack1111l1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤ᰸"): bstack1111l1_opy_ (u"ࠣࡏࡤ࡭ࡳࠦࡐࡪࡲࡨࡰ࡮ࡴࡥࠣ᰹") if env.get(bstack1111l1_opy_ (u"ࠤ࡚ࡉࡗࡉࡋࡆࡔࡢࡑࡆࡏࡎࡠࡒࡌࡔࡊࡒࡉࡏࡇࡢࡗ࡙ࡇࡒࡕࡇࡇࠦ᰺")) else None,
            bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤ᰻"): env.get(bstack1111l1_opy_ (u"ࠦ࡜ࡋࡒࡄࡍࡈࡖࡤࡍࡉࡕࡡࡆࡓࡒࡓࡉࡕࠤ᰼"))
        }
    if any([env.get(bstack1111l1_opy_ (u"ࠧࡍࡃࡑࡡࡓࡖࡔࡐࡅࡄࡖࠥ᰽")), env.get(bstack1111l1_opy_ (u"ࠨࡇࡄࡎࡒ࡙ࡉࡥࡐࡓࡑࡍࡉࡈ࡚ࠢ᰾")), env.get(bstack1111l1_opy_ (u"ࠢࡈࡑࡒࡋࡑࡋ࡟ࡄࡎࡒ࡙ࡉࡥࡐࡓࡑࡍࡉࡈ࡚ࠢ᰿"))]):
        return {
            bstack1111l1_opy_ (u"ࠣࡰࡤࡱࡪࠨ᱀"): bstack1111l1_opy_ (u"ࠤࡊࡳࡴ࡭࡬ࡦࠢࡆࡰࡴࡻࡤࠣ᱁"),
            bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨ᱂"): None,
            bstack1111l1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨ᱃"): env.get(bstack1111l1_opy_ (u"ࠧࡖࡒࡐࡌࡈࡇ࡙ࡥࡉࡅࠤ᱄")),
            bstack1111l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᱅"): env.get(bstack1111l1_opy_ (u"ࠢࡃࡗࡌࡐࡉࡥࡉࡅࠤ᱆"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠣࡕࡋࡍࡕࡖࡁࡃࡎࡈࠦ᱇")):
        return {
            bstack1111l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ᱈"): bstack1111l1_opy_ (u"ࠥࡗ࡭࡯ࡰࡱࡣࡥࡰࡪࠨ᱉"),
            bstack1111l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢ᱊"): env.get(bstack1111l1_opy_ (u"࡙ࠧࡈࡊࡒࡓࡅࡇࡒࡅࡠࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦ᱋")),
            bstack1111l1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣ᱌"): bstack1111l1_opy_ (u"ࠢࡋࡱࡥࠤࠨࢁࡽࠣᱍ").format(env.get(bstack1111l1_opy_ (u"ࠨࡕࡋࡍࡕࡖࡁࡃࡎࡈࡣࡏࡕࡂࡠࡋࡇࠫᱎ"))) if env.get(bstack1111l1_opy_ (u"ࠤࡖࡌࡎࡖࡐࡂࡄࡏࡉࡤࡐࡏࡃࡡࡌࡈࠧᱏ")) else None,
            bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤ᱐"): env.get(bstack1111l1_opy_ (u"ࠦࡘࡎࡉࡑࡒࡄࡆࡑࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗࠨ᱑"))
        }
    if bstack11ll11ll1l_opy_(env.get(bstack1111l1_opy_ (u"ࠧࡔࡅࡕࡎࡌࡊ࡞ࠨ᱒"))):
        return {
            bstack1111l1_opy_ (u"ࠨ࡮ࡢ࡯ࡨࠦ᱓"): bstack1111l1_opy_ (u"ࠢࡏࡧࡷࡰ࡮࡬ࡹࠣ᱔"),
            bstack1111l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟ࡶࡴ࡯ࠦ᱕"): env.get(bstack1111l1_opy_ (u"ࠤࡇࡉࡕࡒࡏ࡚ࡡࡘࡖࡑࠨ᱖")),
            bstack1111l1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧ᱗"): env.get(bstack1111l1_opy_ (u"ࠦࡘࡏࡔࡆࡡࡑࡅࡒࡋࠢ᱘")),
            bstack1111l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦ᱙"): env.get(bstack1111l1_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡏࡄࠣᱚ"))
        }
    if bstack11ll11ll1l_opy_(env.get(bstack1111l1_opy_ (u"ࠢࡈࡋࡗࡌ࡚ࡈ࡟ࡂࡅࡗࡍࡔࡔࡓࠣᱛ"))):
        return {
            bstack1111l1_opy_ (u"ࠣࡰࡤࡱࡪࠨᱜ"): bstack1111l1_opy_ (u"ࠤࡊ࡭ࡹࡎࡵࡣࠢࡄࡧࡹ࡯࡯࡯ࡵࠥᱝ"),
            bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᱞ"): bstack1111l1_opy_ (u"ࠦࢀࢃ࠯ࡼࡿ࠲ࡥࡨࡺࡩࡰࡰࡶ࠳ࡷࡻ࡮ࡴ࠱ࡾࢁࠧᱟ").format(env.get(bstack1111l1_opy_ (u"ࠬࡍࡉࡕࡊࡘࡆࡤ࡙ࡅࡓࡘࡈࡖࡤ࡛ࡒࡍࠩᱠ")), env.get(bstack1111l1_opy_ (u"࠭ࡇࡊࡖࡋ࡙ࡇࡥࡒࡆࡒࡒࡗࡎ࡚ࡏࡓ࡛ࠪᱡ")), env.get(bstack1111l1_opy_ (u"ࠧࡈࡋࡗࡌ࡚ࡈ࡟ࡓࡗࡑࡣࡎࡊࠧᱢ"))),
            bstack1111l1_opy_ (u"ࠣ࡬ࡲࡦࡤࡴࡡ࡮ࡧࠥᱣ"): env.get(bstack1111l1_opy_ (u"ࠤࡊࡍ࡙ࡎࡕࡃࡡ࡚ࡓࡗࡑࡆࡍࡑ࡚ࠦᱤ")),
            bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᱥ"): env.get(bstack1111l1_opy_ (u"ࠦࡌࡏࡔࡉࡗࡅࡣࡗ࡛ࡎࡠࡋࡇࠦᱦ"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠧࡉࡉࠣᱧ")) == bstack1111l1_opy_ (u"ࠨࡴࡳࡷࡨࠦᱨ") and env.get(bstack1111l1_opy_ (u"ࠢࡗࡇࡕࡇࡊࡒࠢᱩ")) == bstack1111l1_opy_ (u"ࠣ࠳ࠥᱪ"):
        return {
            bstack1111l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢᱫ"): bstack1111l1_opy_ (u"࡚ࠥࡪࡸࡣࡦ࡮ࠥᱬ"),
            bstack1111l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᱭ"): bstack1111l1_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࢁࡽࠣᱮ").format(env.get(bstack1111l1_opy_ (u"࠭ࡖࡆࡔࡆࡉࡑࡥࡕࡓࡎࠪᱯ"))),
            bstack1111l1_opy_ (u"ࠢ࡫ࡱࡥࡣࡳࡧ࡭ࡦࠤᱰ"): None,
            bstack1111l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᱱ"): None,
        }
    if env.get(bstack1111l1_opy_ (u"ࠤࡗࡉࡆࡓࡃࡊࡖ࡜ࡣ࡛ࡋࡒࡔࡋࡒࡒࠧᱲ")):
        return {
            bstack1111l1_opy_ (u"ࠥࡲࡦࡳࡥࠣᱳ"): bstack1111l1_opy_ (u"࡙ࠦ࡫ࡡ࡮ࡥ࡬ࡸࡾࠨᱴ"),
            bstack1111l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡺࡸ࡬ࠣᱵ"): None,
            bstack1111l1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᱶ"): env.get(bstack1111l1_opy_ (u"ࠢࡕࡇࡄࡑࡈࡏࡔ࡚ࡡࡓࡖࡔࡐࡅࡄࡖࡢࡒࡆࡓࡅࠣᱷ")),
            bstack1111l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᱸ"): env.get(bstack1111l1_opy_ (u"ࠤࡅ࡙ࡎࡒࡄࡠࡐࡘࡑࡇࡋࡒࠣᱹ"))
        }
    if any([env.get(bstack1111l1_opy_ (u"ࠥࡇࡔࡔࡃࡐࡗࡕࡗࡊࠨᱺ")), env.get(bstack1111l1_opy_ (u"ࠦࡈࡕࡎࡄࡑࡘࡖࡘࡋ࡟ࡖࡔࡏࠦᱻ")), env.get(bstack1111l1_opy_ (u"ࠧࡉࡏࡏࡅࡒ࡙ࡗ࡙ࡅࡠࡗࡖࡉࡗࡔࡁࡎࡇࠥᱼ")), env.get(bstack1111l1_opy_ (u"ࠨࡃࡐࡐࡆࡓ࡚ࡘࡓࡆࡡࡗࡉࡆࡓࠢᱽ"))]):
        return {
            bstack1111l1_opy_ (u"ࠢ࡯ࡣࡰࡩࠧ᱾"): bstack1111l1_opy_ (u"ࠣࡅࡲࡲࡨࡵࡵࡳࡵࡨࠦ᱿"),
            bstack1111l1_opy_ (u"ࠤࡥࡹ࡮ࡲࡤࡠࡷࡵࡰࠧᲀ"): None,
            bstack1111l1_opy_ (u"ࠥ࡮ࡴࡨ࡟࡯ࡣࡰࡩࠧᲁ"): env.get(bstack1111l1_opy_ (u"ࠦࡇ࡛ࡉࡍࡆࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᲂ")) or None,
            bstack1111l1_opy_ (u"ࠧࡨࡵࡪ࡮ࡧࡣࡳࡻ࡭ࡣࡧࡵࠦᲃ"): env.get(bstack1111l1_opy_ (u"ࠨࡂࡖࡋࡏࡈࡤࡏࡄࠣᲄ"), 0)
        }
    if env.get(bstack1111l1_opy_ (u"ࠢࡈࡑࡢࡎࡔࡈ࡟ࡏࡃࡐࡉࠧᲅ")):
        return {
            bstack1111l1_opy_ (u"ࠣࡰࡤࡱࡪࠨᲆ"): bstack1111l1_opy_ (u"ࠤࡊࡳࡈࡊࠢᲇ"),
            bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡸࡶࡱࠨᲈ"): None,
            bstack1111l1_opy_ (u"ࠦ࡯ࡵࡢࡠࡰࡤࡱࡪࠨᲉ"): env.get(bstack1111l1_opy_ (u"ࠧࡍࡏࡠࡌࡒࡆࡤࡔࡁࡎࡇࠥᲊ")),
            bstack1111l1_opy_ (u"ࠨࡢࡶ࡫࡯ࡨࡤࡴࡵ࡮ࡤࡨࡶࠧ᲋"): env.get(bstack1111l1_opy_ (u"ࠢࡈࡑࡢࡔࡎࡖࡅࡍࡋࡑࡉࡤࡉࡏࡖࡐࡗࡉࡗࠨ᲌"))
        }
    if env.get(bstack1111l1_opy_ (u"ࠣࡅࡉࡣࡇ࡛ࡉࡍࡆࡢࡍࡉࠨ᲍")):
        return {
            bstack1111l1_opy_ (u"ࠤࡱࡥࡲ࡫ࠢ᲎"): bstack1111l1_opy_ (u"ࠥࡇࡴࡪࡥࡇࡴࡨࡷ࡭ࠨ᲏"),
            bstack1111l1_opy_ (u"ࠦࡧࡻࡩ࡭ࡦࡢࡹࡷࡲࠢᲐ"): env.get(bstack1111l1_opy_ (u"ࠧࡉࡆࡠࡄࡘࡍࡑࡊ࡟ࡖࡔࡏࠦᲑ")),
            bstack1111l1_opy_ (u"ࠨࡪࡰࡤࡢࡲࡦࡳࡥࠣᲒ"): env.get(bstack1111l1_opy_ (u"ࠢࡄࡈࡢࡔࡎࡖࡅࡍࡋࡑࡉࡤࡔࡁࡎࡇࠥᲓ")),
            bstack1111l1_opy_ (u"ࠣࡤࡸ࡭ࡱࡪ࡟࡯ࡷࡰࡦࡪࡸࠢᲔ"): env.get(bstack1111l1_opy_ (u"ࠤࡆࡊࡤࡈࡕࡊࡎࡇࡣࡎࡊࠢᲕ"))
        }
    return {bstack1111l1_opy_ (u"ࠥࡦࡺ࡯࡬ࡥࡡࡱࡹࡲࡨࡥࡳࠤᲖ"): None}
def get_host_info():
    return {
        bstack1111l1_opy_ (u"ࠦ࡭ࡵࡳࡵࡰࡤࡱࡪࠨᲗ"): platform.node(),
        bstack1111l1_opy_ (u"ࠧࡶ࡬ࡢࡶࡩࡳࡷࡳࠢᲘ"): platform.system(),
        bstack1111l1_opy_ (u"ࠨࡴࡺࡲࡨࠦᲙ"): platform.machine(),
        bstack1111l1_opy_ (u"ࠢࡷࡧࡵࡷ࡮ࡵ࡮ࠣᲚ"): platform.version(),
        bstack1111l1_opy_ (u"ࠣࡣࡵࡧ࡭ࠨᲛ"): platform.architecture()[0]
    }
def bstack111l11ll_opy_():
    try:
        import selenium
        return True
    except ImportError:
        return False
def bstack111llllll11_opy_():
    if bstack11ll1l111l_opy_.get_property(bstack1111l1_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡡࡶࡩࡸࡹࡩࡰࡰࠪᲜ")):
        return bstack1111l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩᲝ")
    return bstack1111l1_opy_ (u"ࠫࡺࡴ࡫࡯ࡱࡺࡲࡤ࡭ࡲࡪࡦࠪᲞ")
def bstack111ll1l11l1_opy_(driver):
    info = {
        bstack1111l1_opy_ (u"ࠬࡩࡡࡱࡣࡥ࡭ࡱ࡯ࡴࡪࡧࡶࠫᲟ"): driver.capabilities,
        bstack1111l1_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴ࡟ࡪࡦࠪᲠ"): driver.session_id,
        bstack1111l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨᲡ"): driver.capabilities.get(bstack1111l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭Ტ"), None),
        bstack1111l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫᲣ"): driver.capabilities.get(bstack1111l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᲤ"), None),
        bstack1111l1_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࠭Ქ"): driver.capabilities.get(bstack1111l1_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡎࡢ࡯ࡨࠫᲦ"), None),
        bstack1111l1_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᲧ"):driver.capabilities.get(bstack1111l1_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩᲨ"), None),
    }
    if bstack111llllll11_opy_() == bstack1111l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧᲩ"):
        if bstack11l11l11_opy_():
            info[bstack1111l1_opy_ (u"ࠩࡳࡶࡴࡪࡵࡤࡶࠪᲪ")] = bstack1111l1_opy_ (u"ࠪࡥࡵࡶ࠭ࡢࡷࡷࡳࡲࡧࡴࡦࠩᲫ")
        elif driver.capabilities.get(bstack1111l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬᲬ"), {}).get(bstack1111l1_opy_ (u"ࠬࡺࡵࡳࡤࡲࡷࡨࡧ࡬ࡦࠩᲭ"), False):
            info[bstack1111l1_opy_ (u"࠭ࡰࡳࡱࡧࡹࡨࡺࠧᲮ")] = bstack1111l1_opy_ (u"ࠧࡵࡷࡵࡦࡴࡹࡣࡢ࡮ࡨࠫᲯ")
        else:
            info[bstack1111l1_opy_ (u"ࠨࡲࡵࡳࡩࡻࡣࡵࠩᲰ")] = bstack1111l1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶࡨࠫᲱ")
    return info
def bstack11l11l11_opy_():
    if bstack11ll1l111l_opy_.get_property(bstack1111l1_opy_ (u"ࠪࡥࡵࡶ࡟ࡢࡷࡷࡳࡲࡧࡴࡦࠩᲲ")):
        return True
    if bstack11ll11ll1l_opy_(os.environ.get(bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬᲳ"), None)):
        return True
    return False
def bstack111llll11_opy_(bstack111lllll1ll_opy_, url, data, config):
    headers = config.get(bstack1111l1_opy_ (u"ࠬ࡮ࡥࡢࡦࡨࡶࡸ࠭Ჴ"), None)
    proxies = bstack11ll1l1l1l_opy_(config, url)
    auth = config.get(bstack1111l1_opy_ (u"࠭ࡡࡶࡶ࡫ࠫᲵ"), None)
    response = requests.request(
            bstack111lllll1ll_opy_,
            url=url,
            headers=headers,
            auth=auth,
            json=data,
            proxies=proxies
        )
    return response
def bstack11111lll1_opy_(bstack1111l11l_opy_, size):
    bstack1l1111l11l_opy_ = []
    while len(bstack1111l11l_opy_) > size:
        bstack1111111l1_opy_ = bstack1111l11l_opy_[:size]
        bstack1l1111l11l_opy_.append(bstack1111111l1_opy_)
        bstack1111l11l_opy_ = bstack1111l11l_opy_[size:]
    bstack1l1111l11l_opy_.append(bstack1111l11l_opy_)
    return bstack1l1111l11l_opy_
def bstack11l11111l11_opy_(message, bstack11l1111l1l1_opy_=False):
    os.write(1, bytes(message, bstack1111l1_opy_ (u"ࠧࡶࡶࡩ࠱࠽࠭Ჶ")))
    os.write(1, bytes(bstack1111l1_opy_ (u"ࠨ࡞ࡱࠫᲷ"), bstack1111l1_opy_ (u"ࠩࡸࡸ࡫࠳࠸ࠨᲸ")))
    if bstack11l1111l1l1_opy_:
        with open(bstack1111l1_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭࠰ࡳ࠶࠷ࡹ࠮ࠩᲹ") + os.environ[bstack1111l1_opy_ (u"ࠫࡇ࡙࡟ࡕࡇࡖࡘࡔࡖࡓࡠࡄࡘࡍࡑࡊ࡟ࡉࡃࡖࡌࡊࡊ࡟ࡊࡆࠪᲺ")] + bstack1111l1_opy_ (u"ࠬ࠴࡬ࡰࡩࠪ᲻"), bstack1111l1_opy_ (u"࠭ࡡࠨ᲼")) as f:
            f.write(message + bstack1111l1_opy_ (u"ࠧ࡝ࡰࠪᲽ"))
def bstack1l1l1l1l1l1_opy_():
    return os.environ[bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫᲾ")].lower() == bstack1111l1_opy_ (u"ࠩࡷࡶࡺ࡫ࠧᲿ")
def bstack11l1l1111l_opy_():
    return bstack1111ll1l1l_opy_().replace(tzinfo=None).isoformat() + bstack1111l1_opy_ (u"ࠪ࡞ࠬ᳀")
def bstack11l11l1l11l_opy_(start, finish):
    return (datetime.datetime.fromisoformat(finish.rstrip(bstack1111l1_opy_ (u"ࠫ࡟࠭᳁"))) - datetime.datetime.fromisoformat(start.rstrip(bstack1111l1_opy_ (u"ࠬࡠࠧ᳂")))).total_seconds() * 1000
def bstack11l11l111ll_opy_(timestamp):
    return bstack11l11l11l11_opy_(timestamp).isoformat() + bstack1111l1_opy_ (u"࡚࠭ࠨ᳃")
def bstack11l111ll1ll_opy_(bstack111ll1ll11l_opy_):
    date_format = bstack1111l1_opy_ (u"࡛ࠧࠦࠨࡱࠪࡪࠠࠦࡊ࠽ࠩࡒࡀࠥࡔ࠰ࠨࡪࠬ᳄")
    bstack11l1111ll1l_opy_ = datetime.datetime.strptime(bstack111ll1ll11l_opy_, date_format)
    return bstack11l1111ll1l_opy_.isoformat() + bstack1111l1_opy_ (u"ࠨ࡜ࠪ᳅")
def bstack111llll111l_opy_(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    if exception:
        return bstack1111l1_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ᳆")
    else:
        return bstack1111l1_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ᳇")
def bstack11ll11ll1l_opy_(val):
    if val is None:
        return False
    return val.__str__().lower() == bstack1111l1_opy_ (u"ࠫࡹࡸࡵࡦࠩ᳈")
def bstack11l1111l111_opy_(val):
    return val.__str__().lower() == bstack1111l1_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫ᳉")
def error_handler(bstack11l11l11l1l_opy_=Exception, class_method=False, default_value=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except bstack11l11l11l1l_opy_ as e:
                print(bstack1111l1_opy_ (u"ࠨࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠠࡼࡿࠣ࠱ࡃࠦࡻࡾ࠼ࠣࡿࢂࠨ᳊").format(func.__name__, bstack11l11l11l1l_opy_.__name__, str(e)))
                return default_value
        return wrapper
    def bstack111llll1l1l_opy_(bstack111ll1l1ll1_opy_):
        def wrapped(cls, *args, **kwargs):
            try:
                return bstack111ll1l1ll1_opy_(cls, *args, **kwargs)
            except bstack11l11l11l1l_opy_ as e:
                print(bstack1111l1_opy_ (u"ࠢࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡦࡶࡰࡦࡸ࡮ࡵ࡮ࠡࡽࢀࠤ࠲ࡄࠠࡼࡿ࠽ࠤࢀࢃࠢ᳋").format(bstack111ll1l1ll1_opy_.__name__, bstack11l11l11l1l_opy_.__name__, str(e)))
                return default_value
        return wrapped
    if class_method:
        return bstack111llll1l1l_opy_
    else:
        return decorator
def bstack1llllllll_opy_(bstack1111111ll1_opy_):
    if os.getenv(bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫ᳌")) is not None:
        return bstack11ll11ll1l_opy_(os.getenv(bstack1111l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡃࡘࡘࡔࡓࡁࡕࡋࡒࡒࠬ᳍")))
    if bstack1111l1_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧ᳎") in bstack1111111ll1_opy_ and bstack11l1111l111_opy_(bstack1111111ll1_opy_[bstack1111l1_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ᳏")]):
        return False
    if bstack1111l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡅࡺࡺ࡯࡮ࡣࡷ࡭ࡴࡴࠧ᳐") in bstack1111111ll1_opy_ and bstack11l1111l111_opy_(bstack1111111ll1_opy_[bstack1111l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨ᳑")]):
        return False
    return True
def bstack1llllll1ll_opy_():
    try:
        from pytest_bdd import reporting
        bstack11l111l111l_opy_ = os.environ.get(bstack1111l1_opy_ (u"ࠢࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡕࡔࡇࡕࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠢ᳒"), None)
        return bstack11l111l111l_opy_ is None or bstack11l111l111l_opy_ == bstack1111l1_opy_ (u"ࠣࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠧ᳓")
    except Exception as e:
        return False
def bstack11l1ll11l_opy_(hub_url, CONFIG):
    if bstack11111l1l1_opy_() <= version.parse(bstack1111l1_opy_ (u"ࠩ࠶࠲࠶࠹࠮࠱᳔ࠩ")):
        if hub_url:
            return bstack1111l1_opy_ (u"ࠥ࡬ࡹࡺࡰ࠻࠱࠲᳕ࠦ") + hub_url + bstack1111l1_opy_ (u"ࠦ࠿࠾࠰࠰ࡹࡧ࠳࡭ࡻࡢ᳖ࠣ")
        return bstack1l1111ll1l_opy_
    if hub_url:
        return bstack1111l1_opy_ (u"ࠧ࡮ࡴࡵࡲࡶ࠾࠴࠵᳗ࠢ") + hub_url + bstack1111l1_opy_ (u"ࠨ࠯ࡸࡦ࠲࡬ࡺࡨ᳘ࠢ")
    return bstack1l1l1llll1_opy_
def bstack111ll1l1l1l_opy_():
    return isinstance(os.getenv(bstack1111l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐ࡚ࡖࡈࡗ࡙ࡥࡐࡍࡗࡊࡍࡓ᳙࠭")), str)
def bstack11lll1lll1_opy_(url):
    return urlparse(url).hostname
def bstack1l11ll1l_opy_(hostname):
    for bstack11ll1l1l1_opy_ in bstack1lllll11l1_opy_:
        regex = re.compile(bstack11ll1l1l1_opy_)
        if regex.match(hostname):
            return True
    return False
def bstack11l111lll11_opy_(bstack11l1111l1ll_opy_, file_name, logger):
    bstack111l1l1ll_opy_ = os.path.join(os.path.expanduser(bstack1111l1_opy_ (u"ࠨࢀࠪ᳚")), bstack11l1111l1ll_opy_)
    try:
        if not os.path.exists(bstack111l1l1ll_opy_):
            os.makedirs(bstack111l1l1ll_opy_)
        file_path = os.path.join(os.path.expanduser(bstack1111l1_opy_ (u"ࠩࢁࠫ᳛")), bstack11l1111l1ll_opy_, file_name)
        if not os.path.isfile(file_path):
            with open(file_path, bstack1111l1_opy_ (u"ࠪࡻ᳜ࠬ")):
                pass
            with open(file_path, bstack1111l1_opy_ (u"ࠦࡼ࠱᳝ࠢ")) as outfile:
                json.dump({}, outfile)
        return file_path
    except Exception as e:
        logger.debug(bstack111l1l1l1_opy_.format(str(e)))
def bstack11l11ll11l1_opy_(file_name, key, value, logger):
    file_path = bstack11l111lll11_opy_(bstack1111l1_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯᳞ࠬ"), file_name, logger)
    if file_path != None:
        if os.path.exists(file_path):
            bstack1l1ll1llll_opy_ = json.load(open(file_path, bstack1111l1_opy_ (u"࠭ࡲࡣ᳟ࠩ")))
        else:
            bstack1l1ll1llll_opy_ = {}
        bstack1l1ll1llll_opy_[key] = value
        with open(file_path, bstack1111l1_opy_ (u"ࠢࡸ࠭ࠥ᳠")) as outfile:
            json.dump(bstack1l1ll1llll_opy_, outfile)
def bstack11l11l1l_opy_(file_name, logger):
    file_path = bstack11l111lll11_opy_(bstack1111l1_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨ᳡"), file_name, logger)
    bstack1l1ll1llll_opy_ = {}
    if file_path != None and os.path.exists(file_path):
        with open(file_path, bstack1111l1_opy_ (u"ࠩࡵ᳢ࠫ")) as bstack11ll11l1l_opy_:
            bstack1l1ll1llll_opy_ = json.load(bstack11ll11l1l_opy_)
    return bstack1l1ll1llll_opy_
def bstack1l11l1l1ll_opy_(file_path, logger):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.debug(bstack1111l1_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡪࡥ࡭ࡧࡷ࡭ࡳ࡭ࠠࡧ࡫࡯ࡩ࠿᳣ࠦࠧ") + file_path + bstack1111l1_opy_ (u"᳤ࠫࠥ࠭") + str(e))
def bstack11111l1l1_opy_():
    from selenium import webdriver
    return version.parse(webdriver.__version__)
class Notset:
    def __repr__(self):
        return bstack1111l1_opy_ (u"ࠧࡂࡎࡐࡖࡖࡉ࡙ࡄ᳥ࠢ")
def bstack1111lll1_opy_(config):
    if bstack1111l1_opy_ (u"࠭ࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸ᳦ࠬ") in config:
        del (config[bstack1111l1_opy_ (u"ࠧࡪࡵࡓࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ᳧࠭")])
        return False
    if bstack11111l1l1_opy_() < version.parse(bstack1111l1_opy_ (u"ࠨ࠵࠱࠸࠳࠶᳨ࠧ")):
        return False
    if bstack11111l1l1_opy_() >= version.parse(bstack1111l1_opy_ (u"ࠩ࠷࠲࠶࠴࠵ࠨᳩ")):
        return True
    if bstack1111l1_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪᳪ") in config and config[bstack1111l1_opy_ (u"ࠫࡺࡹࡥࡘ࠵ࡆࠫᳫ")] is False:
        return False
    else:
        return True
def bstack111lll11_opy_(args_list, bstack11l11111lll_opy_):
    index = -1
    for value in bstack11l11111lll_opy_:
        try:
            index = args_list.index(value)
            return index
        except Exception as e:
            return index
    return index
def bstack11ll1ll11l1_opy_(a, b):
  for k, v in b.items():
    if isinstance(v, dict) and k in a and isinstance(a[k], dict):
        bstack11ll1ll11l1_opy_(a[k], v)
    else:
        a[k] = v
class Result:
    def __init__(self, result=None, duration=None, exception=None, bstack111ll111l1_opy_=None):
        self.result = result
        self.duration = duration
        self.exception = exception
        self.exception_type = type(self.exception).__name__ if exception else None
        self.bstack111ll111l1_opy_ = bstack111ll111l1_opy_
    @classmethod
    def passed(cls):
        return Result(result=bstack1111l1_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬᳬ"))
    @classmethod
    def failed(cls, exception=None):
        return Result(result=bstack1111l1_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ᳭࠭"), exception=exception)
    def bstack11111111l1_opy_(self):
        if self.result != bstack1111l1_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧᳮ"):
            return None
        if isinstance(self.exception_type, str) and bstack1111l1_opy_ (u"ࠣࡃࡶࡷࡪࡸࡴࡪࡱࡱࠦᳯ") in self.exception_type:
            return bstack1111l1_opy_ (u"ࠤࡄࡷࡸ࡫ࡲࡵ࡫ࡲࡲࡊࡸࡲࡰࡴࠥᳰ")
        return bstack1111l1_opy_ (u"࡙ࠥࡳ࡮ࡡ࡯ࡦ࡯ࡩࡩࡋࡲࡳࡱࡵࠦᳱ")
    def bstack111lll1111l_opy_(self):
        if self.result != bstack1111l1_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᳲ"):
            return None
        if self.bstack111ll111l1_opy_:
            return self.bstack111ll111l1_opy_
        return bstack111ll11ll1l_opy_(self.exception)
def bstack111ll11ll1l_opy_(exc):
    return [traceback.format_exception(exc)]
def bstack111llll1111_opy_(message):
    if isinstance(message, str):
        return not bool(message and message.strip())
    return True
def bstack1l1ll111l_opy_(object, key, default_value):
    if not object or not object.__dict__:
        return default_value
    if key in object.__dict__.keys():
        return object.__dict__.get(key)
    return default_value
def bstack111llll1ll_opy_(config, logger):
    try:
        import playwright
        bstack111lllllll1_opy_ = playwright.__file__
        bstack111llll11l1_opy_ = os.path.split(bstack111lllllll1_opy_)
        bstack111ll111lll_opy_ = bstack111llll11l1_opy_[0] + bstack1111l1_opy_ (u"ࠬ࠵ࡤࡳ࡫ࡹࡩࡷ࠵ࡰࡢࡥ࡮ࡥ࡬࡫࠯࡭࡫ࡥ࠳ࡨࡲࡩ࠰ࡥ࡯࡭࠳ࡰࡳࠨᳳ")
        os.environ[bstack1111l1_opy_ (u"࠭ࡇࡍࡑࡅࡅࡑࡥࡁࡈࡇࡑࡘࡤࡎࡔࡕࡒࡢࡔࡗࡕࡘ࡚ࠩ᳴")] = bstack11lllll1ll_opy_(config)
        with open(bstack111ll111lll_opy_, bstack1111l1_opy_ (u"ࠧࡳࠩᳵ")) as f:
            bstack1ll1ll11ll_opy_ = f.read()
            bstack111lllll1l1_opy_ = bstack1111l1_opy_ (u"ࠨࡩ࡯ࡳࡧࡧ࡬࠮ࡣࡪࡩࡳࡺࠧᳶ")
            bstack111lll1ll11_opy_ = bstack1ll1ll11ll_opy_.find(bstack111lllll1l1_opy_)
            if bstack111lll1ll11_opy_ == -1:
              process = subprocess.Popen(bstack1111l1_opy_ (u"ࠤࡱࡴࡲࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡨ࡮ࡲࡦࡦࡲ࠭ࡢࡩࡨࡲࡹࠨ᳷"), shell=True, cwd=bstack111llll11l1_opy_[0])
              process.wait()
              bstack11l11l1ll11_opy_ = bstack1111l1_opy_ (u"ࠪࠦࡺࡹࡥࠡࡵࡷࡶ࡮ࡩࡴࠣ࠽ࠪ᳸")
              bstack111lll1l11l_opy_ = bstack1111l1_opy_ (u"ࠦࠧࠨࠠ࡝ࠤࡸࡷࡪࠦࡳࡵࡴ࡬ࡧࡹࡢࠢ࠼ࠢࡦࡳࡳࡹࡴࠡࡽࠣࡦࡴࡵࡴࡴࡶࡵࡥࡵࠦࡽࠡ࠿ࠣࡶࡪࡷࡵࡪࡴࡨࠬࠬ࡭࡬ࡰࡤࡤࡰ࠲ࡧࡧࡦࡰࡷࠫ࠮ࡁࠠࡪࡨࠣࠬࡵࡸ࡯ࡤࡧࡶࡷ࠳࡫࡮ࡷ࠰ࡊࡐࡔࡈࡁࡍࡡࡄࡋࡊࡔࡔࡠࡊࡗࡘࡕࡥࡐࡓࡑ࡛࡝࠮ࠦࡢࡰࡱࡷࡷࡹࡸࡡࡱࠪࠬ࠿ࠥࠨࠢࠣ᳹")
              bstack111lll1ll1l_opy_ = bstack1ll1ll11ll_opy_.replace(bstack11l11l1ll11_opy_, bstack111lll1l11l_opy_)
              with open(bstack111ll111lll_opy_, bstack1111l1_opy_ (u"ࠬࡽࠧᳺ")) as f:
                f.write(bstack111lll1ll1l_opy_)
    except Exception as e:
        logger.error(bstack1l111llll_opy_.format(str(e)))
def bstack1l1l11111_opy_():
  try:
    bstack111ll11ll11_opy_ = os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"࠭࡯ࡱࡶ࡬ࡱࡦࡲ࡟ࡩࡷࡥࡣࡺࡸ࡬࠯࡬ࡶࡳࡳ࠭᳻"))
    bstack11l1111lll1_opy_ = []
    if os.path.exists(bstack111ll11ll11_opy_):
      with open(bstack111ll11ll11_opy_) as f:
        bstack11l1111lll1_opy_ = json.load(f)
      os.remove(bstack111ll11ll11_opy_)
    return bstack11l1111lll1_opy_
  except:
    pass
  return []
def bstack1l1llllll1_opy_(bstack1ll111lll_opy_):
  try:
    bstack11l1111lll1_opy_ = []
    bstack111ll11ll11_opy_ = os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"ࠧࡰࡲࡷ࡭ࡲࡧ࡬ࡠࡪࡸࡦࡤࡻࡲ࡭࠰࡭ࡷࡴࡴࠧ᳼"))
    if os.path.exists(bstack111ll11ll11_opy_):
      with open(bstack111ll11ll11_opy_) as f:
        bstack11l1111lll1_opy_ = json.load(f)
    bstack11l1111lll1_opy_.append(bstack1ll111lll_opy_)
    with open(bstack111ll11ll11_opy_, bstack1111l1_opy_ (u"ࠨࡹࠪ᳽")) as f:
        json.dump(bstack11l1111lll1_opy_, f)
  except:
    pass
def bstack1l1ll1l1l1_opy_(logger, bstack11l11111l1l_opy_ = False):
  try:
    test_name = os.environ.get(bstack1111l1_opy_ (u"ࠩࡓ࡝࡙ࡋࡓࡕࡡࡗࡉࡘ࡚࡟ࡏࡃࡐࡉࠬ᳾"), bstack1111l1_opy_ (u"ࠪࠫ᳿"))
    if test_name == bstack1111l1_opy_ (u"ࠫࠬᴀ"):
        test_name = threading.current_thread().__dict__.get(bstack1111l1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡇࡪࡤࡠࡶࡨࡷࡹࡥ࡮ࡢ࡯ࡨࠫᴁ"), bstack1111l1_opy_ (u"࠭ࠧᴂ"))
    bstack11l11l11ll1_opy_ = bstack1111l1_opy_ (u"ࠧ࠭ࠢࠪᴃ").join(threading.current_thread().bstackTestErrorMessages)
    if bstack11l11111l1l_opy_:
        bstack1l1ll1ll1l_opy_ = os.environ.get(bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡎࡄࡘࡋࡕࡒࡎࡡࡌࡒࡉࡋࡘࠨᴄ"), bstack1111l1_opy_ (u"ࠩ࠳ࠫᴅ"))
        bstack1l1ll11l1_opy_ = {bstack1111l1_opy_ (u"ࠪࡲࡦࡳࡥࠨᴆ"): test_name, bstack1111l1_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪᴇ"): bstack11l11l11ll1_opy_, bstack1111l1_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫᴈ"): bstack1l1ll1ll1l_opy_}
        bstack111ll1l111l_opy_ = []
        bstack11l111l11ll_opy_ = os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹࡥࡰࡱࡲࡢࡩࡷࡸ࡯ࡳࡡ࡯࡭ࡸࡺ࠮࡫ࡵࡲࡲࠬᴉ"))
        if os.path.exists(bstack11l111l11ll_opy_):
            with open(bstack11l111l11ll_opy_) as f:
                bstack111ll1l111l_opy_ = json.load(f)
        bstack111ll1l111l_opy_.append(bstack1l1ll11l1_opy_)
        with open(bstack11l111l11ll_opy_, bstack1111l1_opy_ (u"ࠧࡸࠩᴊ")) as f:
            json.dump(bstack111ll1l111l_opy_, f)
    else:
        bstack1l1ll11l1_opy_ = {bstack1111l1_opy_ (u"ࠨࡰࡤࡱࡪ࠭ᴋ"): test_name, bstack1111l1_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨᴌ"): bstack11l11l11ll1_opy_, bstack1111l1_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩᴍ"): str(multiprocessing.current_process().name)}
        if bstack1111l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡣࡪࡸࡲࡰࡴࡢࡰ࡮ࡹࡴࠨᴎ") not in multiprocessing.current_process().__dict__.keys():
            multiprocessing.current_process().bstack_error_list = []
        multiprocessing.current_process().bstack_error_list.append(bstack1l1ll11l1_opy_)
  except Exception as e:
      logger.warn(bstack1111l1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡳࡷ࡫ࠠࡱࡻࡷࡩࡸࡺࠠࡧࡷࡱࡲࡪࡲࠠࡥࡣࡷࡥ࠿ࠦࡻࡾࠤᴏ").format(e))
def bstack11l111ll_opy_(error_message, test_name, index, logger):
  try:
    from filelock import FileLock
  except ImportError:
    logger.debug(bstack1111l1_opy_ (u"࠭ࡦࡪ࡮ࡨࡰࡴࡩ࡫ࠡࡰࡲࡸࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥ࠭ࠢࡸࡷ࡮ࡴࡧࠡࡤࡤࡷ࡮ࡩࠠࡧ࡫࡯ࡩࠥࡵࡰࡦࡴࡤࡸ࡮ࡵ࡮ࡴࠩᴐ"))
    try:
      bstack11l11ll11ll_opy_ = []
      bstack1l1ll11l1_opy_ = {bstack1111l1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᴑ"): test_name, bstack1111l1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧᴒ"): error_message, bstack1111l1_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨᴓ"): index}
      bstack111ll1l1lll_opy_ = os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࡡࡨࡶࡷࡵࡲࡠ࡮࡬ࡷࡹ࠴ࡪࡴࡱࡱࠫᴔ"))
      if os.path.exists(bstack111ll1l1lll_opy_):
          with open(bstack111ll1l1lll_opy_) as f:
              bstack11l11ll11ll_opy_ = json.load(f)
      bstack11l11ll11ll_opy_.append(bstack1l1ll11l1_opy_)
      with open(bstack111ll1l1lll_opy_, bstack1111l1_opy_ (u"ࠫࡼ࠭ᴕ")) as f:
          json.dump(bstack11l11ll11ll_opy_, f)
    except Exception as e:
      logger.warn(bstack1111l1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡵࡷࡳࡷ࡫ࠠࡳࡱࡥࡳࡹࠦࡦࡶࡰࡱࡩࡱࠦࡤࡢࡶࡤ࠾ࠥࢁࡽࠣᴖ").format(e))
    return
  bstack11l11ll11ll_opy_ = []
  bstack1l1ll11l1_opy_ = {bstack1111l1_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᴗ"): test_name, bstack1111l1_opy_ (u"ࠧࡦࡴࡵࡳࡷ࠭ᴘ"): error_message, bstack1111l1_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧᴙ"): index}
  bstack111ll1l1lll_opy_ = os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"ࠩࡵࡳࡧࡵࡴࡠࡧࡵࡶࡴࡸ࡟࡭࡫ࡶࡸ࠳ࡰࡳࡰࡰࠪᴚ"))
  lock_file = bstack111ll1l1lll_opy_ + bstack1111l1_opy_ (u"ࠪ࠲ࡱࡵࡣ࡬ࠩᴛ")
  try:
    with FileLock(lock_file, timeout=10):
      if os.path.exists(bstack111ll1l1lll_opy_):
          with open(bstack111ll1l1lll_opy_, bstack1111l1_opy_ (u"ࠫࡷ࠭ᴜ")) as f:
              content = f.read().strip()
              if content:
                  bstack11l11ll11ll_opy_ = json.load(open(bstack111ll1l1lll_opy_))
      bstack11l11ll11ll_opy_.append(bstack1l1ll11l1_opy_)
      with open(bstack111ll1l1lll_opy_, bstack1111l1_opy_ (u"ࠬࡽࠧᴝ")) as f:
          json.dump(bstack11l11ll11ll_opy_, f)
  except Exception as e:
    logger.warn(bstack1111l1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡶࡸࡴࡸࡥࠡࡴࡲࡦࡴࡺࠠࡧࡷࡱࡲࡪࡲࠠࡥࡣࡷࡥࠥࡽࡩࡵࡪࠣࡪ࡮ࡲࡥࠡ࡮ࡲࡧࡰ࡯࡮ࡨ࠼ࠣࡿࢂࠨᴞ").format(e))
def bstack1l11l1l1l_opy_(bstack11ll1111l_opy_, name, logger):
  try:
    bstack1l1ll11l1_opy_ = {bstack1111l1_opy_ (u"ࠧ࡯ࡣࡰࡩࠬᴟ"): name, bstack1111l1_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧᴠ"): bstack11ll1111l_opy_, bstack1111l1_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨᴡ"): str(threading.current_thread()._name)}
    return bstack1l1ll11l1_opy_
  except Exception as e:
    logger.warn(bstack1111l1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡳࡵࡱࡵࡩࠥࡨࡥࡩࡣࡹࡩࠥ࡬ࡵ࡯ࡰࡨࡰࠥࡪࡡࡵࡣ࠽ࠤࢀࢃࠢᴢ").format(e))
  return
def bstack111lll1llll_opy_():
    return platform.system() == bstack1111l1_opy_ (u"ࠫ࡜࡯࡮ࡥࡱࡺࡷࠬᴣ")
def bstack11ll1l11l_opy_(bstack111ll1ll1ll_opy_, config, logger):
    bstack111ll11lll1_opy_ = {}
    try:
        return {key: config[key] for key in config if bstack111ll1ll1ll_opy_.match(key)}
    except Exception as e:
        logger.debug(bstack1111l1_opy_ (u"࡛ࠧ࡮ࡢࡤ࡯ࡩࠥࡺ࡯ࠡࡨ࡬ࡰࡹ࡫ࡲࠡࡥࡲࡲ࡫࡯ࡧࠡ࡭ࡨࡽࡸࠦࡢࡺࠢࡵࡩ࡬࡫ࡸࠡ࡯ࡤࡸࡨ࡮࠺ࠡࡽࢀࠦᴤ").format(e))
    return bstack111ll11lll1_opy_
def bstack111ll111l1l_opy_(bstack11l111lll1l_opy_, bstack111ll1ll1l1_opy_):
    bstack11l111ll11l_opy_ = version.parse(bstack11l111lll1l_opy_)
    bstack111lll111ll_opy_ = version.parse(bstack111ll1ll1l1_opy_)
    if bstack11l111ll11l_opy_ > bstack111lll111ll_opy_:
        return 1
    elif bstack11l111ll11l_opy_ < bstack111lll111ll_opy_:
        return -1
    else:
        return 0
def bstack1111ll1l1l_opy_():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
def bstack11l11l11l11_opy_(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).replace(tzinfo=None)
def bstack11l11l1l111_opy_(framework):
    from browserstack_sdk._version import __version__
    return str(framework) + str(__version__)
def bstack1lll11ll11_opy_(options, framework, config, bstack1l1lll1lll_opy_={}):
    if options is None:
        return
    if getattr(options, bstack1111l1_opy_ (u"࠭ࡧࡦࡶࠪᴥ"), None):
        caps = options
    else:
        caps = options.to_capabilities()
    bstack1llll11l11_opy_ = caps.get(bstack1111l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᴦ"))
    bstack111lll1l1ll_opy_ = True
    bstack1lllllll1l_opy_ = os.environ[bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡕࡇࡖࡘࡍ࡛ࡂࡠࡗࡘࡍࡉ࠭ᴧ")]
    bstack1ll11ll1lll_opy_ = config.get(bstack1111l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᴨ"), False)
    if bstack1ll11ll1lll_opy_:
        bstack1lll1l1111l_opy_ = config.get(bstack1111l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᴩ"), {})
        bstack1lll1l1111l_opy_[bstack1111l1_opy_ (u"ࠫࡦࡻࡴࡩࡖࡲ࡯ࡪࡴࠧᴪ")] = os.getenv(bstack1111l1_opy_ (u"ࠬࡈࡓࡠࡃ࠴࠵࡞ࡥࡊࡘࡖࠪᴫ"))
        bstack11ll11ll1l1_opy_ = json.loads(os.getenv(bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤ࡚ࡅࡔࡖࡢࡅࡈࡉࡅࡔࡕࡌࡆࡎࡒࡉࡕ࡛ࡢࡇࡔࡔࡆࡊࡉࡘࡖࡆ࡚ࡉࡐࡐࡢ࡝ࡒࡒࠧᴬ"), bstack1111l1_opy_ (u"ࠧࡼࡿࠪᴭ"))).get(bstack1111l1_opy_ (u"ࠨࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᴮ"))
    if bstack11l1111l111_opy_(caps.get(bstack1111l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡷࡶࡩ࡜࠹ࡃࠨᴯ"))) or bstack11l1111l111_opy_(caps.get(bstack1111l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡸࡷࡪࡥࡷ࠴ࡥࠪᴰ"))):
        bstack111lll1l1ll_opy_ = False
    if bstack1111lll1_opy_({bstack1111l1_opy_ (u"ࠦࡺࡹࡥࡘ࠵ࡆࠦᴱ"): bstack111lll1l1ll_opy_}):
        bstack1llll11l11_opy_ = bstack1llll11l11_opy_ or {}
        bstack1llll11l11_opy_[bstack1111l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧᴲ")] = bstack11l11l1l111_opy_(framework)
        bstack1llll11l11_opy_[bstack1111l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡆࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨᴳ")] = bstack1l1l1l1l1l1_opy_()
        bstack1llll11l11_opy_[bstack1111l1_opy_ (u"ࠧࡵࡧࡶࡸ࡭ࡻࡢࡃࡷ࡬ࡰࡩ࡛ࡵࡪࡦࠪᴴ")] = bstack1lllllll1l_opy_
        bstack1llll11l11_opy_[bstack1111l1_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡐࡳࡱࡧࡹࡨࡺࡍࡢࡲࠪᴵ")] = bstack1l1lll1lll_opy_
        if bstack1ll11ll1lll_opy_:
            bstack1llll11l11_opy_[bstack1111l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴ࡫ࡥ࡭ࡱ࡯ࡴࡺࠩᴶ")] = bstack1ll11ll1lll_opy_
            bstack1llll11l11_opy_[bstack1111l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵ࡬ࡦ࡮ࡲࡩࡵࡻࡒࡴࡹ࡯࡯࡯ࡵࠪᴷ")] = bstack1lll1l1111l_opy_
            bstack1llll11l11_opy_[bstack1111l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶ࡭ࡧ࡯࡬ࡪࡶࡼࡓࡵࡺࡩࡰࡰࡶࠫᴸ")][bstack1111l1_opy_ (u"ࠬࡹࡣࡢࡰࡱࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ᴹ")] = bstack11ll11ll1l1_opy_
        if getattr(options, bstack1111l1_opy_ (u"࠭ࡳࡦࡶࡢࡧࡦࡶࡡࡣ࡫࡯࡭ࡹࡿࠧᴺ"), None):
            options.set_capability(bstack1111l1_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨᴻ"), bstack1llll11l11_opy_)
        else:
            options[bstack1111l1_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩᴼ")] = bstack1llll11l11_opy_
    else:
        if getattr(options, bstack1111l1_opy_ (u"ࠩࡶࡩࡹࡥࡣࡢࡲࡤࡦ࡮ࡲࡩࡵࡻࠪᴽ"), None):
            options.set_capability(bstack1111l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫᴾ"), bstack11l11l1l111_opy_(framework))
            options.set_capability(bstack1111l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᴿ"), bstack1l1l1l1l1l1_opy_())
            options.set_capability(bstack1111l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡹ࡫ࡳࡵࡪࡸࡦࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧᵀ"), bstack1lllllll1l_opy_)
            options.set_capability(bstack1111l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧᵁ"), bstack1l1lll1lll_opy_)
            if bstack1ll11ll1lll_opy_:
                options.set_capability(bstack1111l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᵂ"), bstack1ll11ll1lll_opy_)
                options.set_capability(bstack1111l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᵃ"), bstack1lll1l1111l_opy_)
                options.set_capability(bstack1111l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳ࠯ࡵࡦࡥࡳࡴࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩᵄ"), bstack11ll11ll1l1_opy_)
        else:
            options[bstack1111l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫᵅ")] = bstack11l11l1l111_opy_(framework)
            options[bstack1111l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᵆ")] = bstack1l1l1l1l1l1_opy_()
            options[bstack1111l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡹ࡫ࡳࡵࡪࡸࡦࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧᵇ")] = bstack1lllllll1l_opy_
            options[bstack1111l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧᵈ")] = bstack1l1lll1lll_opy_
            if bstack1ll11ll1lll_opy_:
                options[bstack1111l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸ࡯ࡢࡪ࡮࡬ࡸࡾ࠭ᵉ")] = bstack1ll11ll1lll_opy_
                options[bstack1111l1_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡥࡦࡩࡸࡹࡩࡣ࡫࡯࡭ࡹࡿࡏࡱࡶ࡬ࡳࡳࡹࠧᵊ")] = bstack1lll1l1111l_opy_
                options[bstack1111l1_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡦࡧࡪࡹࡳࡪࡤ࡬ࡰ࡮ࡺࡹࡐࡲࡷ࡭ࡴࡴࡳࠨᵋ")][bstack1111l1_opy_ (u"ࠪࡷࡨࡧ࡮࡯ࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫᵌ")] = bstack11ll11ll1l1_opy_
    return options
def bstack111ll1lll11_opy_(bstack111lll1l1l1_opy_, framework):
    bstack1l1lll1lll_opy_ = bstack11ll1l111l_opy_.get_property(bstack1111l1_opy_ (u"ࠦࡕࡒࡁ࡚࡙ࡕࡍࡌࡎࡔࡠࡒࡕࡓࡉ࡛ࡃࡕࡡࡐࡅࡕࠨᵍ"))
    if bstack111lll1l1l1_opy_ and len(bstack111lll1l1l1_opy_.split(bstack1111l1_opy_ (u"ࠬࡩࡡࡱࡵࡀࠫᵎ"))) > 1:
        ws_url = bstack111lll1l1l1_opy_.split(bstack1111l1_opy_ (u"࠭ࡣࡢࡲࡶࡁࠬᵏ"))[0]
        if bstack1111l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯ࠪᵐ") in ws_url:
            from browserstack_sdk._version import __version__
            bstack111ll11llll_opy_ = json.loads(urllib.parse.unquote(bstack111lll1l1l1_opy_.split(bstack1111l1_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧᵑ"))[1]))
            bstack111ll11llll_opy_ = bstack111ll11llll_opy_ or {}
            bstack1lllllll1l_opy_ = os.environ[bstack1111l1_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡖࡈࡗ࡙ࡎࡕࡃࡡࡘ࡙ࡎࡊࠧᵒ")]
            bstack111ll11llll_opy_[bstack1111l1_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫᵓ")] = str(framework) + str(__version__)
            bstack111ll11llll_opy_[bstack1111l1_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡃࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬᵔ")] = bstack1l1l1l1l1l1_opy_()
            bstack111ll11llll_opy_[bstack1111l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡹ࡫ࡳࡵࡪࡸࡦࡇࡻࡩ࡭ࡦࡘࡹ࡮ࡪࠧᵕ")] = bstack1lllllll1l_opy_
            bstack111ll11llll_opy_[bstack1111l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡔࡷࡵࡤࡶࡥࡷࡑࡦࡶࠧᵖ")] = bstack1l1lll1lll_opy_
            bstack111lll1l1l1_opy_ = bstack111lll1l1l1_opy_.split(bstack1111l1_opy_ (u"ࠧࡤࡣࡳࡷࡂ࠭ᵗ"))[0] + bstack1111l1_opy_ (u"ࠨࡥࡤࡴࡸࡃࠧᵘ") + urllib.parse.quote(json.dumps(bstack111ll11llll_opy_))
    return bstack111lll1l1l1_opy_
def bstack111l1l1l_opy_():
    global bstack1ll11l1l11_opy_
    from playwright._impl._browser_type import BrowserType
    bstack1ll11l1l11_opy_ = BrowserType.connect
    return bstack1ll11l1l11_opy_
def bstack11lllllll_opy_(framework_name):
    global bstack11ll1l11l1_opy_
    bstack11ll1l11l1_opy_ = framework_name
    return framework_name
def bstack1l1lll1l1_opy_(self, *args, **kwargs):
    global bstack1ll11l1l11_opy_
    try:
        global bstack11ll1l11l1_opy_
        if bstack1111l1_opy_ (u"ࠩࡺࡷࡊࡴࡤࡱࡱ࡬ࡲࡹ࠭ᵙ") in kwargs:
            kwargs[bstack1111l1_opy_ (u"ࠪࡻࡸࡋ࡮ࡥࡲࡲ࡭ࡳࡺࠧᵚ")] = bstack111ll1lll11_opy_(
                kwargs.get(bstack1111l1_opy_ (u"ࠫࡼࡹࡅ࡯ࡦࡳࡳ࡮ࡴࡴࠨᵛ"), None),
                bstack11ll1l11l1_opy_
            )
    except Exception as e:
        logger.error(bstack1111l1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡥ࡯ࠢࡳࡶࡴࡩࡥࡴࡵ࡬ࡲ࡬ࠦࡓࡅࡍࠣࡧࡦࡶࡳ࠻ࠢࡾࢁࠧᵜ").format(str(e)))
    return bstack1ll11l1l11_opy_(self, *args, **kwargs)
def bstack11l111l11l1_opy_(bstack11l1111ll11_opy_, proxies):
    proxy_settings = {}
    try:
        if not proxies:
            proxies = bstack11ll1l1l1l_opy_(bstack11l1111ll11_opy_, bstack1111l1_opy_ (u"ࠨࠢᵝ"))
        if proxies and proxies.get(bstack1111l1_opy_ (u"ࠢࡩࡶࡷࡴࡸࠨᵞ")):
            parsed_url = urlparse(proxies.get(bstack1111l1_opy_ (u"ࠣࡪࡷࡸࡵࡹࠢᵟ")))
            if parsed_url and parsed_url.hostname: proxy_settings[bstack1111l1_opy_ (u"ࠩࡳࡶࡴࡾࡹࡉࡱࡶࡸࠬᵠ")] = str(parsed_url.hostname)
            if parsed_url and parsed_url.port: proxy_settings[bstack1111l1_opy_ (u"ࠪࡴࡷࡵࡸࡺࡒࡲࡶࡹ࠭ᵡ")] = str(parsed_url.port)
            if parsed_url and parsed_url.username: proxy_settings[bstack1111l1_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡘࡷࡪࡸࠧᵢ")] = str(parsed_url.username)
            if parsed_url and parsed_url.password: proxy_settings[bstack1111l1_opy_ (u"ࠬࡶࡲࡰࡺࡼࡔࡦࡹࡳࠨᵣ")] = str(parsed_url.password)
        return proxy_settings
    except:
        return proxy_settings
def bstack11ll1llll_opy_(bstack11l1111ll11_opy_):
    bstack11l1111111l_opy_ = {
        bstack11l1l11lll1_opy_[bstack111lll11lll_opy_]: bstack11l1111ll11_opy_[bstack111lll11lll_opy_]
        for bstack111lll11lll_opy_ in bstack11l1111ll11_opy_
        if bstack111lll11lll_opy_ in bstack11l1l11lll1_opy_
    }
    bstack11l1111111l_opy_[bstack1111l1_opy_ (u"ࠨࡰࡳࡱࡻࡽࡘ࡫ࡴࡵ࡫ࡱ࡫ࡸࠨᵤ")] = bstack11l111l11l1_opy_(bstack11l1111ll11_opy_, bstack11ll1l111l_opy_.get_property(bstack1111l1_opy_ (u"ࠢࡱࡴࡲࡼࡾ࡙ࡥࡵࡶ࡬ࡲ࡬ࡹࠢᵥ")))
    bstack11l111llll1_opy_ = [element.lower() for element in bstack11l1ll1l1l1_opy_]
    bstack11l111ll1l1_opy_(bstack11l1111111l_opy_, bstack11l111llll1_opy_)
    return bstack11l1111111l_opy_
def bstack11l111ll1l1_opy_(d, keys):
    for key in list(d.keys()):
        if key.lower() in keys:
            d[key] = bstack1111l1_opy_ (u"ࠣࠬ࠭࠮࠯ࠨᵦ")
    for value in d.values():
        if isinstance(value, dict):
            bstack11l111ll1l1_opy_(value, keys)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    bstack11l111ll1l1_opy_(item, keys)
def bstack1l1ll1111l1_opy_():
    bstack111lll11l1l_opy_ = [os.environ.get(bstack1111l1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡈࡌࡐࡊ࡙࡟ࡅࡋࡕࠦᵧ")), os.path.join(os.path.expanduser(bstack1111l1_opy_ (u"ࠥࢂࠧᵨ")), bstack1111l1_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫᵩ")), os.path.join(bstack1111l1_opy_ (u"ࠬ࠵ࡴ࡮ࡲࠪᵪ"), bstack1111l1_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ᵫ"))]
    for path in bstack111lll11l1l_opy_:
        if path is None:
            continue
        try:
            if os.path.exists(path):
                logger.debug(bstack1111l1_opy_ (u"ࠢࡇ࡫࡯ࡩࠥ࠭ࠢᵬ") + str(path) + bstack1111l1_opy_ (u"ࠣࠩࠣࡩࡽ࡯ࡳࡵࡵ࠱ࠦᵭ"))
                if not os.access(path, os.W_OK):
                    logger.debug(bstack1111l1_opy_ (u"ࠤࡊ࡭ࡻ࡯࡮ࡨࠢࡳࡩࡷࡳࡩࡴࡵ࡬ࡳࡳࡹࠠࡧࡱࡵࠤࠬࠨᵮ") + str(path) + bstack1111l1_opy_ (u"ࠥࠫࠧᵯ"))
                    os.chmod(path, 0o777)
                else:
                    logger.debug(bstack1111l1_opy_ (u"ࠦࡋ࡯࡬ࡦࠢࠪࠦᵰ") + str(path) + bstack1111l1_opy_ (u"ࠧ࠭ࠠࡢ࡮ࡵࡩࡦࡪࡹࠡࡪࡤࡷࠥࡺࡨࡦࠢࡵࡩࡶࡻࡩࡳࡧࡧࠤࡵ࡫ࡲ࡮࡫ࡶࡷ࡮ࡵ࡮ࡴ࠰ࠥᵱ"))
            else:
                logger.debug(bstack1111l1_opy_ (u"ࠨࡃࡳࡧࡤࡸ࡮ࡴࡧࠡࡨ࡬ࡰࡪࠦࠧࠣᵲ") + str(path) + bstack1111l1_opy_ (u"ࠢࠨࠢࡺ࡭ࡹ࡮ࠠࡸࡴ࡬ࡸࡪࠦࡰࡦࡴࡰ࡭ࡸࡹࡩࡰࡰ࠱ࠦᵳ"))
                os.makedirs(path, exist_ok=True)
                os.chmod(path, 0o777)
            logger.debug(bstack1111l1_opy_ (u"ࠣࡑࡳࡩࡷࡧࡴࡪࡱࡱࠤࡸࡻࡣࡤࡧࡨࡨࡪࡪࠠࡧࡱࡵࠤࠬࠨᵴ") + str(path) + bstack1111l1_opy_ (u"ࠤࠪ࠲ࠧᵵ"))
            return path
        except Exception as e:
            logger.debug(bstack1111l1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡳࡦࡶࠣࡹࡵࠦࡦࡪ࡮ࡨࠤࠬࢁࡰࡢࡶ࡫ࢁࠬࡀࠠࠣᵶ") + str(e) + bstack1111l1_opy_ (u"ࠦࠧᵷ"))
    logger.debug(bstack1111l1_opy_ (u"ࠧࡇ࡬࡭ࠢࡳࡥࡹ࡮ࡳࠡࡨࡤ࡭ࡱ࡫ࡤ࠯ࠤᵸ"))
    return None
@measure(event_name=EVENTS.bstack11l1ll1l11l_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
def bstack1lll1l11ll1_opy_(binary_path, bstack1llll111ll1_opy_, bs_config):
    logger.debug(bstack1111l1_opy_ (u"ࠨࡃࡶࡴࡵࡩࡳࡺࠠࡄࡎࡌࠤࡕࡧࡴࡩࠢࡩࡳࡺࡴࡤ࠻ࠢࡾࢁࠧᵹ").format(binary_path))
    bstack11l111l1l11_opy_ = bstack1111l1_opy_ (u"ࠧࠨᵺ")
    bstack11l11l1l1l1_opy_ = {
        bstack1111l1_opy_ (u"ࠨࡵࡧ࡯ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ᵻ"): __version__,
        bstack1111l1_opy_ (u"ࠤࡲࡷࠧᵼ"): platform.system(),
        bstack1111l1_opy_ (u"ࠥࡳࡸࡥࡡࡳࡥ࡫ࠦᵽ"): platform.machine(),
        bstack1111l1_opy_ (u"ࠦࡨࡲࡩࡠࡸࡨࡶࡸ࡯࡯࡯ࠤᵾ"): bstack1111l1_opy_ (u"ࠬ࠶ࠧᵿ"),
        bstack1111l1_opy_ (u"ࠨࡳࡥ࡭ࡢࡰࡦࡴࡧࡶࡣࡪࡩࠧᶀ"): bstack1111l1_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧᶁ")
    }
    bstack11l111l1lll_opy_(bstack11l11l1l1l1_opy_)
    try:
        if binary_path:
            if bstack111lll1llll_opy_():
                bstack11l11l1l1l1_opy_[bstack1111l1_opy_ (u"ࠨࡥ࡯࡭ࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ᶂ")] = subprocess.check_output([binary_path, bstack1111l1_opy_ (u"ࠤࡹࡩࡷࡹࡩࡰࡰࠥᶃ")]).strip().decode(bstack1111l1_opy_ (u"ࠪࡹࡹ࡬࠭࠹ࠩᶄ"))
            else:
                bstack11l11l1l1l1_opy_[bstack1111l1_opy_ (u"ࠫࡨࡲࡩࡠࡸࡨࡶࡸ࡯࡯࡯ࠩᶅ")] = subprocess.check_output([binary_path, bstack1111l1_opy_ (u"ࠧࡼࡥࡳࡵ࡬ࡳࡳࠨᶆ")], stderr=subprocess.DEVNULL).strip().decode(bstack1111l1_opy_ (u"࠭ࡵࡵࡨ࠰࠼ࠬᶇ"))
        response = requests.request(
            bstack1111l1_opy_ (u"ࠧࡈࡇࡗࠫᶈ"),
            url=bstack11ll111l1_opy_(bstack11l1lll11ll_opy_),
            headers=None,
            auth=(bs_config[bstack1111l1_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪᶉ")], bs_config[bstack1111l1_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬᶊ")]),
            json=None,
            params=bstack11l11l1l1l1_opy_
        )
        data = response.json()
        if response.status_code == 200 and bstack1111l1_opy_ (u"ࠪࡹࡷࡲࠧᶋ") in data.keys() and bstack1111l1_opy_ (u"ࠫࡺࡶࡤࡢࡶࡨࡨࡤࡩ࡬ࡪࡡࡹࡩࡷࡹࡩࡰࡰࠪᶌ") in data.keys():
            logger.debug(bstack1111l1_opy_ (u"ࠧࡔࡥࡦࡦࠣࡸࡴࠦࡵࡱࡦࡤࡸࡪࠦࡢࡪࡰࡤࡶࡾ࠲ࠠࡤࡷࡵࡶࡪࡴࡴࠡࡤ࡬ࡲࡦࡸࡹࠡࡸࡨࡶࡸ࡯࡯࡯࠼ࠣࡿࢂࠨᶍ").format(bstack11l11l1l1l1_opy_[bstack1111l1_opy_ (u"࠭ࡣ࡭࡫ࡢࡺࡪࡸࡳࡪࡱࡱࠫᶎ")]))
            if bstack1111l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡂࡊࡐࡄࡖ࡞ࡥࡕࡓࡎࠪᶏ") in os.environ:
                logger.debug(bstack1111l1_opy_ (u"ࠣࡕ࡮࡭ࡵࡶࡩ࡯ࡩࠣࡦ࡮ࡴࡡࡳࡻࠣࡨࡴࡽ࡮࡭ࡱࡤࡨࠥࡧࡳࠡࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡋࡑࡅࡗ࡟࡟ࡖࡔࡏࠤ࡮ࡹࠠࡴࡧࡷࠦᶐ"))
                data[bstack1111l1_opy_ (u"ࠩࡸࡶࡱ࠭ᶑ")] = os.environ[bstack1111l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡅࡍࡓࡇࡒ࡚ࡡࡘࡖࡑ࠭ᶒ")]
            bstack111ll11l1l1_opy_ = bstack11l11l11111_opy_(data[bstack1111l1_opy_ (u"ࠫࡺࡸ࡬ࠨᶓ")], bstack1llll111ll1_opy_)
            bstack11l111l1l11_opy_ = os.path.join(bstack1llll111ll1_opy_, bstack111ll11l1l1_opy_)
            os.chmod(bstack11l111l1l11_opy_, 0o777) # bstack111ll11l111_opy_ permission
            return bstack11l111l1l11_opy_
    except Exception as e:
        logger.debug(bstack1111l1_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤࡼ࡮ࡩ࡭ࡧࠣࡨࡴࡽ࡮࡭ࡱࡤࡨ࡮ࡴࡧࠡࡰࡨࡻ࡙ࠥࡄࡌࠢࡾࢁࠧᶔ").format(e))
    return binary_path
def bstack11l111l1lll_opy_(bstack11l11l1l1l1_opy_):
    try:
        if bstack1111l1_opy_ (u"࠭࡬ࡪࡰࡸࡼࠬᶕ") not in bstack11l11l1l1l1_opy_[bstack1111l1_opy_ (u"ࠧࡰࡵࠪᶖ")].lower():
            return
        if os.path.exists(bstack1111l1_opy_ (u"ࠣ࠱ࡨࡸࡨ࠵࡯ࡴ࠯ࡵࡩࡱ࡫ࡡࡴࡧࠥᶗ")):
            with open(bstack1111l1_opy_ (u"ࠤ࠲ࡩࡹࡩ࠯ࡰࡵ࠰ࡶࡪࡲࡥࡢࡵࡨࠦᶘ"), bstack1111l1_opy_ (u"ࠥࡶࠧᶙ")) as f:
                bstack111llllllll_opy_ = {}
                for line in f:
                    if bstack1111l1_opy_ (u"ࠦࡂࠨᶚ") in line:
                        key, value = line.rstrip().split(bstack1111l1_opy_ (u"ࠧࡃࠢᶛ"), 1)
                        bstack111llllllll_opy_[key] = value.strip(bstack1111l1_opy_ (u"࠭ࠢ࡝ࠩࠪᶜ"))
                bstack11l11l1l1l1_opy_[bstack1111l1_opy_ (u"ࠧࡥ࡫ࡶࡸࡷࡵࠧᶝ")] = bstack111llllllll_opy_.get(bstack1111l1_opy_ (u"ࠣࡋࡇࠦᶞ"), bstack1111l1_opy_ (u"ࠤࠥᶟ"))
        elif os.path.exists(bstack1111l1_opy_ (u"ࠥ࠳ࡪࡺࡣ࠰ࡣ࡯ࡴ࡮ࡴࡥ࠮ࡴࡨࡰࡪࡧࡳࡦࠤᶠ")):
            bstack11l11l1l1l1_opy_[bstack1111l1_opy_ (u"ࠫࡩ࡯ࡳࡵࡴࡲࠫᶡ")] = bstack1111l1_opy_ (u"ࠬࡧ࡬ࡱ࡫ࡱࡩࠬᶢ")
    except Exception as e:
        logger.debug(bstack1111l1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡪࡩࡹࠦࡤࡪࡵࡷࡶࡴࠦ࡯ࡧࠢ࡯࡭ࡳࡻࡸࠣᶣ") + e)
@measure(event_name=EVENTS.bstack11l1l1l1111_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
def bstack11l11l11111_opy_(bstack11l11l1l1ll_opy_, bstack111ll1l1l11_opy_):
    logger.debug(bstack1111l1_opy_ (u"ࠢࡅࡱࡺࡲࡱࡵࡡࡥ࡫ࡱ࡫࡙ࠥࡄࡌࠢࡥ࡭ࡳࡧࡲࡺࠢࡩࡶࡴࡳ࠺ࠡࠤᶤ") + str(bstack11l11l1l1ll_opy_) + bstack1111l1_opy_ (u"ࠣࠤᶥ"))
    zip_path = os.path.join(bstack111ll1l1l11_opy_, bstack1111l1_opy_ (u"ࠤࡧࡳࡼࡴ࡬ࡰࡣࡧࡩࡩࡥࡦࡪ࡮ࡨ࠲ࡿ࡯ࡰࠣᶦ"))
    bstack111ll11l1l1_opy_ = bstack1111l1_opy_ (u"ࠪࠫᶧ")
    with requests.get(bstack11l11l1l1ll_opy_, stream=True) as response:
        response.raise_for_status()
        with open(zip_path, bstack1111l1_opy_ (u"ࠦࡼࡨࠢᶨ")) as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        logger.debug(bstack1111l1_opy_ (u"ࠧࡌࡩ࡭ࡧࠣࡨࡴࡽ࡮࡭ࡱࡤࡨࡪࡪࠠࡴࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࡰࡾ࠴ࠢᶩ"))
    with zipfile.ZipFile(zip_path, bstack1111l1_opy_ (u"࠭ࡲࠨᶪ")) as zip_ref:
        bstack11l1111l11l_opy_ = zip_ref.namelist()
        if len(bstack11l1111l11l_opy_) > 0:
            bstack111ll11l1l1_opy_ = bstack11l1111l11l_opy_[0] # bstack11l111111ll_opy_ bstack11l1ll11lll_opy_ will be bstack111111lll1_opy_ 1 file i.e. the binary in the zip
        zip_ref.extractall(bstack111ll1l1l11_opy_)
        logger.debug(bstack1111l1_opy_ (u"ࠢࡇ࡫࡯ࡩࡸࠦࡳࡶࡥࡦࡩࡸࡹࡦࡶ࡮࡯ࡽࠥ࡫ࡸࡵࡴࡤࡧࡹ࡫ࡤࠡࡶࡲࠤࠬࠨᶫ") + str(bstack111ll1l1l11_opy_) + bstack1111l1_opy_ (u"ࠣࠩࠥᶬ"))
    os.remove(zip_path)
    return bstack111ll11l1l1_opy_
def get_cli_dir():
    bstack11l11l111l1_opy_ = bstack1l1ll1111l1_opy_()
    if bstack11l11l111l1_opy_:
        bstack1llll111ll1_opy_ = os.path.join(bstack11l11l111l1_opy_, bstack1111l1_opy_ (u"ࠤࡦࡰ࡮ࠨᶭ"))
        if not os.path.exists(bstack1llll111ll1_opy_):
            os.makedirs(bstack1llll111ll1_opy_, mode=0o777, exist_ok=True)
        return bstack1llll111ll1_opy_
    else:
        raise FileNotFoundError(bstack1111l1_opy_ (u"ࠥࡒࡴࠦࡷࡳ࡫ࡷࡥࡧࡲࡥࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡦࡼࡡࡪ࡮ࡤࡦࡱ࡫ࠠࡧࡱࡵࠤࡹ࡮ࡥࠡࡕࡇࡏࠥࡨࡩ࡯ࡣࡵࡽ࠳ࠨᶮ"))
def bstack1lll11lll1l_opy_(bstack1llll111ll1_opy_):
    bstack1111l1_opy_ (u"ࠦࠧࠨࡇࡦࡶࠣࡸ࡭࡫ࠠࡱࡣࡷ࡬ࠥ࡬࡯ࡳࠢࡷ࡬ࡪࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯࡙ࠥࡄࡌࠢࡥ࡭ࡳࡧࡲࡺࠢ࡬ࡲࠥࡧࠠࡸࡴ࡬ࡸࡦࡨ࡬ࡦࠢࡧ࡭ࡷ࡫ࡣࡵࡱࡵࡽ࠳ࠨࠢࠣᶯ")
    bstack11l1111llll_opy_ = [
        os.path.join(bstack1llll111ll1_opy_, f)
        for f in os.listdir(bstack1llll111ll1_opy_)
        if os.path.isfile(os.path.join(bstack1llll111ll1_opy_, f)) and f.startswith(bstack1111l1_opy_ (u"ࠧࡨࡩ࡯ࡣࡵࡽ࠲ࠨᶰ"))
    ]
    if len(bstack11l1111llll_opy_) > 0:
        return max(bstack11l1111llll_opy_, key=os.path.getmtime) # get bstack111ll111ll1_opy_ binary
    return bstack1111l1_opy_ (u"ࠨࠢᶱ")
def bstack11ll1ll1lll_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1ll111llll1_opy_(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = bstack1ll111llll1_opy_(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack11lll1ll_opy_(data, keys, default=None):
    bstack1111l1_opy_ (u"ࠢࠣࠤࠍࠤࠥࠦࠠࡔࡣࡩࡩࡱࡿࠠࡨࡧࡷࠤࡦࠦ࡮ࡦࡵࡷࡩࡩࠦࡶࡢ࡮ࡸࡩࠥ࡬ࡲࡰ࡯ࠣࡥࠥࡪࡩࡤࡶ࡬ࡳࡳࡧࡲࡺࠢࡲࡶࠥࡲࡩࡴࡶ࠱ࠎࠥࠦࠠࠡ࠼ࡳࡥࡷࡧ࡭ࠡࡦࡤࡸࡦࡀࠠࡕࡪࡨࠤࡩ࡯ࡣࡵ࡫ࡲࡲࡦࡸࡹࠡࡱࡵࠤࡱ࡯ࡳࡵࠢࡷࡳࠥࡺࡲࡢࡸࡨࡶࡸ࡫࠮ࠋࠢࠣࠤࠥࡀࡰࡢࡴࡤࡱࠥࡱࡥࡺࡵ࠽ࠤࡆࠦ࡬ࡪࡵࡷࠤࡴ࡬ࠠ࡬ࡧࡼࡷ࠴࡯࡮ࡥ࡫ࡦࡩࡸࠦࡲࡦࡲࡵࡩࡸ࡫࡮ࡵ࡫ࡱ࡫ࠥࡺࡨࡦࠢࡳࡥࡹ࡮࠮ࠋࠢࠣࠤࠥࡀࡰࡢࡴࡤࡱࠥࡪࡥࡧࡣࡸࡰࡹࡀࠠࡗࡣ࡯ࡹࡪࠦࡴࡰࠢࡵࡩࡹࡻࡲ࡯ࠢ࡬ࡪࠥࡺࡨࡦࠢࡳࡥࡹ࡮ࠠࡥࡱࡨࡷࠥࡴ࡯ࡵࠢࡨࡼ࡮ࡹࡴ࠯ࠌࠣࠤࠥࠦ࠺ࡳࡧࡷࡹࡷࡴ࠺ࠡࡖ࡫ࡩࠥࡼࡡ࡭ࡷࡨࠤࡦࡺࠠࡵࡪࡨࠤࡳ࡫ࡳࡵࡧࡧࠤࡵࡧࡴࡩ࠮ࠣࡳࡷࠦࡤࡦࡨࡤࡹࡱࡺࠠࡪࡨࠣࡲࡴࡺࠠࡧࡱࡸࡲࡩ࠴ࠊࠡࠢࠣࠤࠧࠨࠢᶲ")
    if not data:
        return default
    current = data
    try:
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int):
                current = current[key]
            else:
                return default
        return current
    except (KeyError, IndexError, TypeError):
        return default