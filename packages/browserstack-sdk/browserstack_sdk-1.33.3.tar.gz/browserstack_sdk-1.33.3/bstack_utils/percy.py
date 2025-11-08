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
import re
import sys
import json
import time
import shutil
import tempfile
import requests
import subprocess
from threading import Thread
from os.path import expanduser
from bstack_utils.constants import *
from requests.auth import HTTPBasicAuth
from bstack_utils.helper import bstack111llll11_opy_
from bstack_utils.measure import measure
from bstack_utils.bstack1l1lllll1_opy_ import bstack11ll111l1_opy_
class bstack111111ll_opy_:
  working_dir = os.getcwd()
  bstack11l11l11_opy_ = False
  config = {}
  bstack111ll11l1l1_opy_ = bstack1111l1_opy_ (u"ࠪࠫἅ")
  binary_path = bstack1111l1_opy_ (u"ࠫࠬἆ")
  bstack1111l1111ll_opy_ = bstack1111l1_opy_ (u"ࠬ࠭ἇ")
  bstack111l111ll_opy_ = False
  bstack111111ll1l1_opy_ = None
  bstack111111l1l11_opy_ = {}
  bstack11111l1ll11_opy_ = 300
  bstack11111llll1l_opy_ = False
  logger = None
  bstack111111llll1_opy_ = False
  bstack11l11111ll_opy_ = False
  percy_build_id = None
  bstack11111l111l1_opy_ = bstack1111l1_opy_ (u"࠭ࠧἈ")
  bstack11111lll11l_opy_ = {
    bstack1111l1_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࠧἉ") : 1,
    bstack1111l1_opy_ (u"ࠨࡨ࡬ࡶࡪ࡬࡯ࡹࠩἊ") : 2,
    bstack1111l1_opy_ (u"ࠩࡨࡨ࡬࡫ࠧἋ") : 3,
    bstack1111l1_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪἌ") : 4
  }
  def __init__(self) -> None: pass
  def bstack11111ll111l_opy_(self):
    bstack11111l1l111_opy_ = bstack1111l1_opy_ (u"ࠫࠬἍ")
    bstack1111l1111l1_opy_ = sys.platform
    bstack11111l11l11_opy_ = bstack1111l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࠫἎ")
    if re.match(bstack1111l1_opy_ (u"ࠨࡤࡢࡴࡺ࡭ࡳࢂ࡭ࡢࡥࠣࡳࡸࠨἏ"), bstack1111l1111l1_opy_) != None:
      bstack11111l1l111_opy_ = bstack11l1l11llll_opy_ + bstack1111l1_opy_ (u"ࠢ࠰ࡲࡨࡶࡨࡿ࠭ࡰࡵࡻ࠲ࡿ࡯ࡰࠣἐ")
      self.bstack11111l111l1_opy_ = bstack1111l1_opy_ (u"ࠨ࡯ࡤࡧࠬἑ")
    elif re.match(bstack1111l1_opy_ (u"ࠤࡰࡷࡼ࡯࡮ࡽ࡯ࡶࡽࡸࢂ࡭ࡪࡰࡪࡻࢁࡩࡹࡨࡹ࡬ࡲࢁࡨࡣࡤࡹ࡬ࡲࢁࡽࡩ࡯ࡥࡨࢀࡪࡳࡣࡽࡹ࡬ࡲ࠸࠸ࠢἒ"), bstack1111l1111l1_opy_) != None:
      bstack11111l1l111_opy_ = bstack11l1l11llll_opy_ + bstack1111l1_opy_ (u"ࠥ࠳ࡵ࡫ࡲࡤࡻ࠰ࡻ࡮ࡴ࠮ࡻ࡫ࡳࠦἓ")
      bstack11111l11l11_opy_ = bstack1111l1_opy_ (u"ࠦࡵ࡫ࡲࡤࡻ࠱ࡩࡽ࡫ࠢἔ")
      self.bstack11111l111l1_opy_ = bstack1111l1_opy_ (u"ࠬࡽࡩ࡯ࠩἕ")
    else:
      bstack11111l1l111_opy_ = bstack11l1l11llll_opy_ + bstack1111l1_opy_ (u"ࠨ࠯ࡱࡧࡵࡧࡾ࠳࡬ࡪࡰࡸࡼ࠳ࢀࡩࡱࠤ἖")
      self.bstack11111l111l1_opy_ = bstack1111l1_opy_ (u"ࠧ࡭࡫ࡱࡹࡽ࠭἗")
    return bstack11111l1l111_opy_, bstack11111l11l11_opy_
  def bstack11111lllll1_opy_(self):
    try:
      bstack11111l1l1ll_opy_ = [os.path.join(expanduser(bstack1111l1_opy_ (u"ࠣࢀࠥἘ")), bstack1111l1_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩἙ")), self.working_dir, tempfile.gettempdir()]
      for path in bstack11111l1l1ll_opy_:
        if(self.bstack11111llll11_opy_(path)):
          return path
      raise bstack1111l1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡤࡰࡹࡱࡰࡴࡧࡤࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠢἚ")
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠦࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡧ࡫ࡱࡨࠥࡧࡶࡢ࡫࡯ࡥࡧࡲࡥࠡࡲࡤࡸ࡭ࠦࡦࡰࡴࠣࡴࡪࡸࡣࡺࠢࡧࡳࡼࡴ࡬ࡰࡣࡧ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࠯ࠣࡿࢂࠨἛ").format(e))
  def bstack11111llll11_opy_(self, path):
    try:
      if not os.path.exists(path):
        os.makedirs(path)
      return True
    except:
      return False
  def bstack1111l11ll1l_opy_(self, bstack1111l11l1l1_opy_):
    return os.path.join(bstack1111l11l1l1_opy_, self.bstack111ll11l1l1_opy_ + bstack1111l1_opy_ (u"ࠧ࠴ࡥࡵࡣࡪࠦἜ"))
  def bstack111111l1ll1_opy_(self, bstack1111l11l1l1_opy_, bstack1111111l1ll_opy_):
    if not bstack1111111l1ll_opy_: return
    try:
      bstack1111l11ll11_opy_ = self.bstack1111l11ll1l_opy_(bstack1111l11l1l1_opy_)
      with open(bstack1111l11ll11_opy_, bstack1111l1_opy_ (u"ࠨࡷࠣἝ")) as f:
        f.write(bstack1111111l1ll_opy_)
        self.logger.debug(bstack1111l1_opy_ (u"ࠢࡔࡣࡹࡩࡩࠦ࡮ࡦࡹࠣࡉ࡙ࡧࡧࠡࡨࡲࡶࠥࡶࡥࡳࡥࡼࠦ἞"))
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤࡸࡧࡶࡦࠢࡷ࡬ࡪࠦࡥࡵࡣࡪ࠰ࠥ࡫ࡲࡳࡱࡵ࠾ࠥࢁࡽࠣ἟").format(e))
  def bstack11111l1111l_opy_(self, bstack1111l11l1l1_opy_):
    try:
      bstack1111l11ll11_opy_ = self.bstack1111l11ll1l_opy_(bstack1111l11l1l1_opy_)
      if os.path.exists(bstack1111l11ll11_opy_):
        with open(bstack1111l11ll11_opy_, bstack1111l1_opy_ (u"ࠤࡵࠦἠ")) as f:
          bstack1111111l1ll_opy_ = f.read().strip()
          return bstack1111111l1ll_opy_ if bstack1111111l1ll_opy_ else None
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠥࡊࡦ࡯࡬ࡦࡦࠣࡰࡴࡧࡤࡪࡰࡪࠤࡊ࡚ࡡࡨ࠮ࠣࡩࡷࡸ࡯ࡳ࠼ࠣࡿࢂࠨἡ").format(e))
  def bstack11111llllll_opy_(self, bstack1111l11l1l1_opy_, bstack11111l1l111_opy_):
    bstack1111l111lll_opy_ = self.bstack11111l1111l_opy_(bstack1111l11l1l1_opy_)
    if bstack1111l111lll_opy_:
      try:
        bstack11111ll1l11_opy_ = self.bstack1111l111ll1_opy_(bstack1111l111lll_opy_, bstack11111l1l111_opy_)
        if not bstack11111ll1l11_opy_:
          self.logger.debug(bstack1111l1_opy_ (u"ࠦࡕ࡫ࡲࡤࡻࠣࡦ࡮ࡴࡡࡳࡻࠣ࡭ࡸࠦࡵࡱࠢࡷࡳࠥࡪࡡࡵࡧࠣࠬࡊ࡚ࡡࡨࠢࡸࡲࡨ࡮ࡡ࡯ࡩࡨࡨ࠮ࠨἢ"))
          return True
        self.logger.debug(bstack1111l1_opy_ (u"ࠧࡔࡥࡸࠢࡓࡩࡷࡩࡹࠡࡤ࡬ࡲࡦࡸࡹࠡࡸࡨࡶࡸ࡯࡯࡯ࠢࡤࡺࡦ࡯࡬ࡢࡤ࡯ࡩ࠱ࠦࡤࡰࡹࡱࡰࡴࡧࡤࡪࡰࡪࠤࡺࡶࡤࡢࡶࡨࠦἣ"))
        return False
      except Exception as e:
        self.logger.warn(bstack1111l1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡦ࡬ࡪࡩ࡫ࠡࡨࡲࡶࠥࡨࡩ࡯ࡣࡵࡽࠥࡻࡰࡥࡣࡷࡩࡸ࠲ࠠࡶࡵ࡬ࡲ࡬ࠦࡥࡹ࡫ࡶࡸ࡮ࡴࡧࠡࡤ࡬ࡲࡦࡸࡹ࠻ࠢࡾࢁࠧἤ").format(e))
    return False
  def bstack1111l111ll1_opy_(self, bstack1111l111lll_opy_, bstack11111l1l111_opy_):
    try:
      headers = {
        bstack1111l1_opy_ (u"ࠢࡊࡨ࠰ࡒࡴࡴࡥ࠮ࡏࡤࡸࡨ࡮ࠢἥ"): bstack1111l111lll_opy_
      }
      response = bstack111llll11_opy_(bstack1111l1_opy_ (u"ࠨࡉࡈࡘࠬἦ"), bstack11111l1l111_opy_, {}, {bstack1111l1_opy_ (u"ࠤ࡫ࡩࡦࡪࡥࡳࡵࠥἧ"): headers})
      if response.status_code == 304:
        return False
      return True
    except Exception as e:
      raise(bstack1111l1_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢࡦ࡬ࡪࡩ࡫ࡪࡰࡪࠤ࡫ࡵࡲࠡࡒࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠠࡶࡲࡧࡥࡹ࡫ࡳ࠻ࠢࡾࢁࠧἨ").format(e))
  @measure(event_name=EVENTS.bstack11l1l11ll11_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
  def bstack1111l111111_opy_(self, bstack11111l1l111_opy_, bstack11111l11l11_opy_):
    try:
      bstack11111ll11l1_opy_ = self.bstack11111lllll1_opy_()
      bstack1111111ll11_opy_ = os.path.join(bstack11111ll11l1_opy_, bstack1111l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻ࠱ࡾ࡮ࡶࠧἩ"))
      bstack11111l11lll_opy_ = os.path.join(bstack11111ll11l1_opy_, bstack11111l11l11_opy_)
      if self.bstack11111llllll_opy_(bstack11111ll11l1_opy_, bstack11111l1l111_opy_): # if bstack1111111ll1l_opy_, bstack1l1l111lll1_opy_ bstack1111111l1ll_opy_ is bstack11111l111ll_opy_ to bstack111ll111ll1_opy_ version available (response 304)
        if os.path.exists(bstack11111l11lll_opy_):
          self.logger.info(bstack1111l1_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤ࡫ࡵࡵ࡯ࡦࠣ࡭ࡳࠦࡻࡾ࠮ࠣࡷࡰ࡯ࡰࡱ࡫ࡱ࡫ࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠢἪ").format(bstack11111l11lll_opy_))
          return bstack11111l11lll_opy_
        if os.path.exists(bstack1111111ll11_opy_):
          self.logger.info(bstack1111l1_opy_ (u"ࠨࡐࡦࡴࡦࡽࠥࢀࡩࡱࠢࡩࡳࡺࡴࡤࠡ࡫ࡱࠤࢀࢃࠬࠡࡷࡱࡾ࡮ࡶࡰࡪࡰࡪࠦἫ").format(bstack1111111ll11_opy_))
          return self.bstack111111lll1l_opy_(bstack1111111ll11_opy_, bstack11111l11l11_opy_)
      self.logger.info(bstack1111l1_opy_ (u"ࠢࡅࡱࡺࡲࡱࡵࡡࡥ࡫ࡱ࡫ࠥࡶࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼࠤ࡫ࡸ࡯࡮ࠢࡾࢁࠧἬ").format(bstack11111l1l111_opy_))
      response = bstack111llll11_opy_(bstack1111l1_opy_ (u"ࠨࡉࡈࡘࠬἭ"), bstack11111l1l111_opy_, {}, {})
      if response.status_code == 200:
        bstack11111lll111_opy_ = response.headers.get(bstack1111l1_opy_ (u"ࠤࡈࡘࡦ࡭ࠢἮ"), bstack1111l1_opy_ (u"ࠥࠦἯ"))
        if bstack11111lll111_opy_:
          self.bstack111111l1ll1_opy_(bstack11111ll11l1_opy_, bstack11111lll111_opy_)
        with open(bstack1111111ll11_opy_, bstack1111l1_opy_ (u"ࠫࡼࡨࠧἰ")) as file:
          file.write(response.content)
        self.logger.info(bstack1111l1_opy_ (u"ࠧࡊ࡯ࡸࡰ࡯ࡳࡦࡪࡥࡥࠢࡳࡩࡷࡩࡹࠡࡤ࡬ࡲࡦࡸࡹࠡࡣࡱࡨࠥࡹࡡࡷࡧࡧࠤࡦࡺࠠࡼࡿࠥἱ").format(bstack1111111ll11_opy_))
        return self.bstack111111lll1l_opy_(bstack1111111ll11_opy_, bstack11111l11l11_opy_)
      else:
        raise(bstack1111l1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡧࡳࡼࡴ࡬ࡰࡣࡧࠤࡹ࡮ࡥࠡࡨ࡬ࡰࡪ࠴ࠠࡔࡶࡤࡸࡺࡹࠠࡤࡱࡧࡩ࠿ࠦࡻࡾࠤἲ").format(response.status_code))
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡨࡴࡽ࡮࡭ࡱࡤࡨࠥࡶࡥࡳࡥࡼࠤࡧ࡯࡮ࡢࡴࡼ࠾ࠥࢁࡽࠣἳ").format(e))
  def bstack111111l1111_opy_(self, bstack11111l1l111_opy_, bstack11111l11l11_opy_):
    try:
      retry = 2
      bstack11111l11lll_opy_ = None
      bstack11111ll1ll1_opy_ = False
      while retry > 0:
        bstack11111l11lll_opy_ = self.bstack1111l111111_opy_(bstack11111l1l111_opy_, bstack11111l11l11_opy_)
        bstack11111ll1ll1_opy_ = self.bstack1111111llll_opy_(bstack11111l1l111_opy_, bstack11111l11l11_opy_, bstack11111l11lll_opy_)
        if bstack11111ll1ll1_opy_:
          break
        retry -= 1
      return bstack11111l11lll_opy_, bstack11111ll1ll1_opy_
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠣࡗࡱࡥࡧࡲࡥࠡࡶࡲࠤ࡬࡫ࡴࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠠࡱࡣࡷ࡬ࠧἴ").format(e))
    return bstack11111l11lll_opy_, False
  def bstack1111111llll_opy_(self, bstack11111l1l111_opy_, bstack11111l11l11_opy_, bstack11111l11lll_opy_, bstack11111ll11ll_opy_ = 0):
    if bstack11111ll11ll_opy_ > 1:
      return False
    if bstack11111l11lll_opy_ == None or os.path.exists(bstack11111l11lll_opy_) == False:
      self.logger.warn(bstack1111l1_opy_ (u"ࠤࡓࡩࡷࡩࡹࠡࡲࡤࡸ࡭ࠦ࡮ࡰࡶࠣࡪࡴࡻ࡮ࡥ࠮ࠣࡶࡪࡺࡲࡺ࡫ࡱ࡫ࠥࡪ࡯ࡸࡰ࡯ࡳࡦࡪࠢἵ"))
      return False
    bstack111111ll111_opy_ = bstack1111l1_opy_ (u"ࡵࠦࡣ࠴ࠪࡁࡲࡨࡶࡨࡿ࠯ࡤ࡮࡬ࠤࡡࡪࠫ࡝࠰࡟ࡨ࠰ࡢ࠮࡝ࡦ࠮ࠦἶ")
    command = bstack1111l1_opy_ (u"ࠫࢀࢃࠠ࠮࠯ࡹࡩࡷࡹࡩࡰࡰࠪἷ").format(bstack11111l11lll_opy_)
    bstack111111l1lll_opy_ = subprocess.check_output(command, shell=True, text=True)
    if re.match(bstack111111ll111_opy_, bstack111111l1lll_opy_) != None:
      return True
    else:
      self.logger.error(bstack1111l1_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡻ࡫ࡲࡴ࡫ࡲࡲࠥࡩࡨࡦࡥ࡮ࠤ࡫ࡧࡩ࡭ࡧࡧࠦἸ"))
      return False
  def bstack111111lll1l_opy_(self, bstack1111111ll11_opy_, bstack11111l11l11_opy_):
    try:
      working_dir = os.path.dirname(bstack1111111ll11_opy_)
      shutil.unpack_archive(bstack1111111ll11_opy_, working_dir)
      bstack11111l11lll_opy_ = os.path.join(working_dir, bstack11111l11l11_opy_)
      os.chmod(bstack11111l11lll_opy_, 0o755)
      return bstack11111l11lll_opy_
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡸࡲࡿ࡯ࡰࠡࡲࡨࡶࡨࡿࠠࡣ࡫ࡱࡥࡷࡿࠢἹ"))
  def bstack1111l11l11l_opy_(self):
    try:
      bstack111111ll11l_opy_ = self.config.get(bstack1111l1_opy_ (u"ࠧࡱࡧࡵࡧࡾ࠭Ἲ"))
      bstack1111l11l11l_opy_ = bstack111111ll11l_opy_ or (bstack111111ll11l_opy_ is None and self.bstack11l11l11_opy_)
      if not bstack1111l11l11l_opy_ or self.config.get(bstack1111l1_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫἻ"), None) not in bstack11l1ll1l1ll_opy_:
        return False
      self.bstack111l111ll_opy_ = True
      return True
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠤࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡪࡥࡵࡧࡦࡸࠥࡶࡥࡳࡥࡼ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡽࢀࠦἼ").format(e))
  def bstack111111ll1ll_opy_(self):
    try:
      bstack111111ll1ll_opy_ = self.percy_capture_mode
      return bstack111111ll1ll_opy_
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡤࡦࡶࡨࡧࡹࠦࡰࡦࡴࡦࡽࠥࡩࡡࡱࡶࡸࡶࡪࠦ࡭ࡰࡦࡨ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡽࢀࠦἽ").format(e))
  def init(self, bstack11l11l11_opy_, config, logger):
    self.bstack11l11l11_opy_ = bstack11l11l11_opy_
    self.config = config
    self.logger = logger
    if not self.bstack1111l11l11l_opy_():
      return
    self.bstack111111l1l11_opy_ = config.get(bstack1111l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࡒࡴࡹ࡯࡯࡯ࡵࠪἾ"), {})
    self.percy_capture_mode = config.get(bstack1111l1_opy_ (u"ࠬࡶࡥࡳࡥࡼࡇࡦࡶࡴࡶࡴࡨࡑࡴࡪࡥࠨἿ"))
    try:
      bstack11111l1l111_opy_, bstack11111l11l11_opy_ = self.bstack11111ll111l_opy_()
      self.bstack111ll11l1l1_opy_ = bstack11111l11l11_opy_
      bstack11111l11lll_opy_, bstack11111ll1ll1_opy_ = self.bstack111111l1111_opy_(bstack11111l1l111_opy_, bstack11111l11l11_opy_)
      if bstack11111ll1ll1_opy_:
        self.binary_path = bstack11111l11lll_opy_
        thread = Thread(target=self.bstack11111l1lll1_opy_)
        thread.start()
      else:
        self.bstack111111llll1_opy_ = True
        self.logger.error(bstack1111l1_opy_ (u"ࠨࡉ࡯ࡸࡤࡰ࡮ࡪࠠࡱࡧࡵࡧࡾࠦࡰࡢࡶ࡫ࠤ࡫ࡵࡵ࡯ࡦࠣ࠱ࠥࢁࡽ࠭ࠢࡘࡲࡦࡨ࡬ࡦࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡕ࡫ࡲࡤࡻࠥὀ").format(bstack11111l11lll_opy_))
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠢࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡷࡹࡧࡲࡵࠢࡳࡩࡷࡩࡹ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥࢁࡽࠣὁ").format(e))
  def bstack1111111lll1_opy_(self):
    try:
      logfile = os.path.join(self.working_dir, bstack1111l1_opy_ (u"ࠨ࡮ࡲ࡫ࠬὂ"), bstack1111l1_opy_ (u"ࠩࡳࡩࡷࡩࡹ࠯࡮ࡲ࡫ࠬὃ"))
      os.makedirs(os.path.dirname(logfile)) if not os.path.exists(os.path.dirname(logfile)) else None
      self.logger.debug(bstack1111l1_opy_ (u"ࠥࡔࡺࡹࡨࡪࡰࡪࠤࡵ࡫ࡲࡤࡻࠣࡰࡴ࡭ࡳࠡࡣࡷࠤࢀࢃࠢὄ").format(logfile))
      self.bstack1111l1111ll_opy_ = logfile
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"࡚ࠦࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡧࡷࠤࡵ࡫ࡲࡤࡻࠣࡰࡴ࡭ࠠࡱࡣࡷ࡬࠱ࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢࡾࢁࠧὅ").format(e))
  @measure(event_name=EVENTS.bstack11l1ll11111_opy_, stage=STAGE.bstack1l1ll1111l_opy_)
  def bstack11111l1lll1_opy_(self):
    bstack11111ll1111_opy_ = self.bstack11111l1llll_opy_()
    if bstack11111ll1111_opy_ == None:
      self.bstack111111llll1_opy_ = True
      self.logger.error(bstack1111l1_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡹࡵ࡫ࡦࡰࠣࡲࡴࡺࠠࡧࡱࡸࡲࡩ࠲ࠠࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡹࡧࡲࡵࠢࡳࡩࡷࡩࡹࠣ὆"))
      return False
    bstack11111ll1l1l_opy_ = [bstack1111l1_opy_ (u"ࠨࡡࡱࡲ࠽ࡩࡽ࡫ࡣ࠻ࡵࡷࡥࡷࡺࠢ὇") if self.bstack11l11l11_opy_ else bstack1111l1_opy_ (u"ࠧࡦࡺࡨࡧ࠿ࡹࡴࡢࡴࡷࠫὈ")]
    bstack111l1l1l11l_opy_ = self.bstack1111l111l1l_opy_()
    if bstack111l1l1l11l_opy_ != None:
      bstack11111ll1l1l_opy_.append(bstack1111l1_opy_ (u"ࠣ࠯ࡦࠤࢀࢃࠢὉ").format(bstack111l1l1l11l_opy_))
    env = os.environ.copy()
    env[bstack1111l1_opy_ (u"ࠤࡓࡉࡗࡉ࡙ࡠࡖࡒࡏࡊࡔࠢὊ")] = bstack11111ll1111_opy_
    env[bstack1111l1_opy_ (u"ࠥࡘࡍࡥࡂࡖࡋࡏࡈࡤ࡛ࡕࡊࡆࠥὋ")] = os.environ.get(bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩὌ"), bstack1111l1_opy_ (u"ࠬ࠭Ὅ"))
    bstack11111l11l1l_opy_ = [self.binary_path]
    self.bstack1111111lll1_opy_()
    self.bstack111111ll1l1_opy_ = self.bstack111111l111l_opy_(bstack11111l11l1l_opy_ + bstack11111ll1l1l_opy_, env)
    self.logger.debug(bstack1111l1_opy_ (u"ࠨࡓࡵࡣࡵࡸ࡮ࡴࡧࠡࡊࡨࡥࡱࡺࡨࠡࡅ࡫ࡩࡨࡱࠢ὎"))
    bstack11111ll11ll_opy_ = 0
    while self.bstack111111ll1l1_opy_.poll() == None:
      bstack11111l11ll1_opy_ = self.bstack11111ll1lll_opy_()
      if bstack11111l11ll1_opy_:
        self.logger.debug(bstack1111l1_opy_ (u"ࠢࡉࡧࡤࡰࡹ࡮ࠠࡄࡪࡨࡧࡰࠦࡳࡶࡥࡦࡩࡸࡹࡦࡶ࡮ࠥ὏"))
        self.bstack11111llll1l_opy_ = True
        return True
      bstack11111ll11ll_opy_ += 1
      self.logger.debug(bstack1111l1_opy_ (u"ࠣࡊࡨࡥࡱࡺࡨࠡࡅ࡫ࡩࡨࡱࠠࡓࡧࡷࡶࡾࠦ࠭ࠡࡽࢀࠦὐ").format(bstack11111ll11ll_opy_))
      time.sleep(2)
    self.logger.error(bstack1111l1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡴࡢࡴࡷࠤࡵ࡫ࡲࡤࡻ࠯ࠤࡍ࡫ࡡ࡭ࡶ࡫ࠤࡈ࡮ࡥࡤ࡭ࠣࡊࡦ࡯࡬ࡦࡦࠣࡥ࡫ࡺࡥࡳࠢࡾࢁࠥࡧࡴࡵࡧࡰࡴࡹࡹࠢὑ").format(bstack11111ll11ll_opy_))
    self.bstack111111llll1_opy_ = True
    return False
  def bstack11111ll1lll_opy_(self, bstack11111ll11ll_opy_ = 0):
    if bstack11111ll11ll_opy_ > 10:
      return False
    try:
      bstack11111l11111_opy_ = os.environ.get(bstack1111l1_opy_ (u"ࠪࡔࡊࡘࡃ࡚ࡡࡖࡉࡗ࡜ࡅࡓࡡࡄࡈࡉࡘࡅࡔࡕࠪὒ"), bstack1111l1_opy_ (u"ࠫ࡭ࡺࡴࡱ࠼࠲࠳ࡱࡵࡣࡢ࡮࡫ࡳࡸࡺ࠺࠶࠵࠶࠼ࠬὓ"))
      bstack111111l11l1_opy_ = bstack11111l11111_opy_ + bstack11l1ll1111l_opy_
      response = requests.get(bstack111111l11l1_opy_)
      data = response.json()
      self.percy_build_id = data.get(bstack1111l1_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࠫὔ"), {}).get(bstack1111l1_opy_ (u"࠭ࡩࡥࠩὕ"), None)
      return True
    except:
      self.logger.debug(bstack1111l1_opy_ (u"ࠢࡆࡴࡵࡳࡷࠦ࡯ࡤࡥࡸࡶࡷ࡫ࡤࠡࡹ࡫࡭ࡱ࡫ࠠࡱࡴࡲࡧࡪࡹࡳࡪࡰࡪࠤ࡭࡫ࡡ࡭ࡶ࡫ࠤࡨ࡮ࡥࡤ࡭ࠣࡶࡪࡹࡰࡰࡰࡶࡩࠧὖ"))
      return False
  def bstack11111l1llll_opy_(self):
    bstack111111lll11_opy_ = bstack1111l1_opy_ (u"ࠨࡣࡳࡴࠬὗ") if self.bstack11l11l11_opy_ else bstack1111l1_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶࡨࠫ὘")
    bstack11111l1ll1l_opy_ = bstack1111l1_opy_ (u"ࠥࡹࡳࡪࡥࡧ࡫ࡱࡩࡩࠨὙ") if self.config.get(bstack1111l1_opy_ (u"ࠫࡵ࡫ࡲࡤࡻࠪ὚")) is None else True
    bstack11ll1111ll1_opy_ = bstack1111l1_opy_ (u"ࠧࡧࡰࡪ࠱ࡤࡴࡵࡥࡰࡦࡴࡦࡽ࠴࡭ࡥࡵࡡࡳࡶࡴࡰࡥࡤࡶࡢࡸࡴࡱࡥ࡯ࡁࡱࡥࡲ࡫࠽ࡼࡿࠩࡸࡾࡶࡥ࠾ࡽࢀࠪࡵ࡫ࡲࡤࡻࡀࡿࢂࠨὛ").format(self.config[bstack1111l1_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫ὜")], bstack111111lll11_opy_, bstack11111l1ll1l_opy_)
    if self.percy_capture_mode:
      bstack11ll1111ll1_opy_ += bstack1111l1_opy_ (u"ࠢࠧࡲࡨࡶࡨࡿ࡟ࡤࡣࡳࡸࡺࡸࡥࡠ࡯ࡲࡨࡪࡃࡻࡾࠤὝ").format(self.percy_capture_mode)
    uri = bstack11ll111l1_opy_(bstack11ll1111ll1_opy_)
    try:
      response = bstack111llll11_opy_(bstack1111l1_opy_ (u"ࠨࡉࡈࡘࠬ὞"), uri, {}, {bstack1111l1_opy_ (u"ࠩࡤࡹࡹ࡮ࠧὟ"): (self.config[bstack1111l1_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬὠ")], self.config[bstack1111l1_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧὡ")])})
      if response.status_code == 200:
        data = response.json()
        self.bstack111l111ll_opy_ = data.get(bstack1111l1_opy_ (u"ࠬࡹࡵࡤࡥࡨࡷࡸ࠭ὢ"))
        self.percy_capture_mode = data.get(bstack1111l1_opy_ (u"࠭ࡰࡦࡴࡦࡽࡤࡩࡡࡱࡶࡸࡶࡪࡥ࡭ࡰࡦࡨࠫὣ"))
        os.environ[bstack1111l1_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡆࡔࡆ࡝ࠬὤ")] = str(self.bstack111l111ll_opy_)
        os.environ[bstack1111l1_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡑࡇࡕࡇ࡞ࡥࡃࡂࡒࡗ࡙ࡗࡋ࡟ࡎࡑࡇࡉࠬὥ")] = str(self.percy_capture_mode)
        if bstack11111l1ll1l_opy_ == bstack1111l1_opy_ (u"ࠤࡸࡲࡩ࡫ࡦࡪࡰࡨࡨࠧὦ") and str(self.bstack111l111ll_opy_).lower() == bstack1111l1_opy_ (u"ࠥࡸࡷࡻࡥࠣὧ"):
          self.bstack11l11111ll_opy_ = True
        if bstack1111l1_opy_ (u"ࠦࡹࡵ࡫ࡦࡰࠥὨ") in data:
          return data[bstack1111l1_opy_ (u"ࠧࡺ࡯࡬ࡧࡱࠦὩ")]
        else:
          raise bstack1111l1_opy_ (u"࠭ࡔࡰ࡭ࡨࡲࠥࡔ࡯ࡵࠢࡉࡳࡺࡴࡤࠡ࠯ࠣࡿࢂ࠭Ὢ").format(data)
      else:
        raise bstack1111l1_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡪࡪࡺࡣࡩࠢࡳࡩࡷࡩࡹࠡࡶࡲ࡯ࡪࡴࠬࠡࡔࡨࡷࡵࡵ࡮ࡴࡧࠣࡷࡹࡧࡴࡶࡵࠣ࠱ࠥࢁࡽ࠭ࠢࡕࡩࡸࡶ࡯࡯ࡵࡨࠤࡇࡵࡤࡺࠢ࠰ࠤࢀࢃࠢὫ").format(response.status_code, response.json())
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠣࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡤࡴࡨࡥࡹ࡯࡮ࡨࠢࡳࡩࡷࡩࡹࠡࡲࡵࡳ࡯࡫ࡣࡵࠤὬ").format(e))
  def bstack1111l111l1l_opy_(self):
    bstack111111lllll_opy_ = os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"ࠤࡳࡩࡷࡩࡹࡄࡱࡱࡪ࡮࡭࠮࡫ࡵࡲࡲࠧὭ"))
    try:
      if bstack1111l1_opy_ (u"ࠪࡺࡪࡸࡳࡪࡱࡱࠫὮ") not in self.bstack111111l1l11_opy_:
        self.bstack111111l1l11_opy_[bstack1111l1_opy_ (u"ࠫࡻ࡫ࡲࡴ࡫ࡲࡲࠬὯ")] = 2
      with open(bstack111111lllll_opy_, bstack1111l1_opy_ (u"ࠬࡽࠧὰ")) as fp:
        json.dump(self.bstack111111l1l11_opy_, fp)
      return bstack111111lllll_opy_
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡦࡶࡪࡧࡴࡦࠢࡳࡩࡷࡩࡹࠡࡥࡲࡲ࡫࠲ࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣࡿࢂࠨά").format(e))
  def bstack111111l111l_opy_(self, cmd, env = os.environ.copy()):
    try:
      if self.bstack11111l111l1_opy_ == bstack1111l1_opy_ (u"ࠧࡸ࡫ࡱࠫὲ"):
        bstack11111l1l11l_opy_ = [bstack1111l1_opy_ (u"ࠨࡥࡰࡨ࠳࡫ࡸࡦࠩέ"), bstack1111l1_opy_ (u"ࠩ࠲ࡧࠬὴ")]
        cmd = bstack11111l1l11l_opy_ + cmd
      cmd = bstack1111l1_opy_ (u"ࠪࠤࠬή").join(cmd)
      self.logger.debug(bstack1111l1_opy_ (u"ࠦࡗࡻ࡮࡯࡫ࡱ࡫ࠥࢁࡽࠣὶ").format(cmd))
      with open(self.bstack1111l1111ll_opy_, bstack1111l1_opy_ (u"ࠧࡧࠢί")) as bstack1111l111l11_opy_:
        process = subprocess.Popen(cmd, shell=True, stdout=bstack1111l111l11_opy_, text=True, stderr=bstack1111l111l11_opy_, env=env, universal_newlines=True)
      return process
    except Exception as e:
      self.bstack111111llll1_opy_ = True
      self.logger.error(bstack1111l1_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡸࡦࡸࡴࠡࡲࡨࡶࡨࡿࠠࡸ࡫ࡷ࡬ࠥࡩ࡭ࡥࠢ࠰ࠤࢀࢃࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱ࠾ࠥࢁࡽࠣὸ").format(cmd, e))
  def shutdown(self):
    try:
      if self.bstack11111llll1l_opy_:
        self.logger.info(bstack1111l1_opy_ (u"ࠢࡔࡶࡲࡴࡵ࡯࡮ࡨࠢࡓࡩࡷࡩࡹࠣό"))
        cmd = [self.binary_path, bstack1111l1_opy_ (u"ࠣࡧࡻࡩࡨࡀࡳࡵࡱࡳࠦὺ")]
        self.bstack111111l111l_opy_(cmd)
        self.bstack11111llll1l_opy_ = False
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠤࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥࡹࡴࡰࡲࠣࡷࡪࡹࡳࡪࡱࡱࠤࡼ࡯ࡴࡩࠢࡦࡳࡲࡳࡡ࡯ࡦࠣ࠱ࠥࢁࡽ࠭ࠢࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲ࠿ࠦࡻࡾࠤύ").format(cmd, e))
  def bstack1ll1ll1ll_opy_(self):
    if not self.bstack111l111ll_opy_:
      return
    try:
      bstack1111l11l111_opy_ = 0
      while not self.bstack11111llll1l_opy_ and bstack1111l11l111_opy_ < self.bstack11111l1ll11_opy_:
        if self.bstack111111llll1_opy_:
          self.logger.info(bstack1111l1_opy_ (u"ࠥࡔࡪࡸࡣࡺࠢࡶࡩࡹࡻࡰࠡࡨࡤ࡭ࡱ࡫ࡤࠣὼ"))
          return
        time.sleep(1)
        bstack1111l11l111_opy_ += 1
      os.environ[bstack1111l1_opy_ (u"ࠫࡕࡋࡒࡄ࡛ࡢࡆࡊ࡙ࡔࡠࡒࡏࡅ࡙ࡌࡏࡓࡏࠪώ")] = str(self.bstack1111l11l1ll_opy_())
      self.logger.info(bstack1111l1_opy_ (u"ࠧࡖࡥࡳࡥࡼࠤࡸ࡫ࡴࡶࡲࠣࡧࡴࡳࡰ࡭ࡧࡷࡩࡩࠨ὾"))
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"ࠨࡕ࡯ࡣࡥࡰࡪࠦࡴࡰࠢࡶࡩࡹࡻࡰࠡࡲࡨࡶࡨࡿࠬࠡࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤࢀࢃࠢ὿").format(e))
  def bstack1111l11l1ll_opy_(self):
    if self.bstack11l11l11_opy_:
      return
    try:
      bstack11111lll1l1_opy_ = [platform[bstack1111l1_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬᾀ")].lower() for platform in self.config.get(bstack1111l1_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫᾁ"), [])]
      bstack11111l1l1l1_opy_ = sys.maxsize
      bstack111111l1l1l_opy_ = bstack1111l1_opy_ (u"ࠩࠪᾂ")
      for browser in bstack11111lll1l1_opy_:
        if browser in self.bstack11111lll11l_opy_:
          bstack111111l11ll_opy_ = self.bstack11111lll11l_opy_[browser]
        if bstack111111l11ll_opy_ < bstack11111l1l1l1_opy_:
          bstack11111l1l1l1_opy_ = bstack111111l11ll_opy_
          bstack111111l1l1l_opy_ = browser
      return bstack111111l1l1l_opy_
    except Exception as e:
      self.logger.error(bstack1111l1_opy_ (u"࡙ࠥࡳࡧࡢ࡭ࡧࠣࡸࡴࠦࡦࡪࡰࡧࠤࡧ࡫ࡳࡵࠢࡳࡰࡦࡺࡦࡰࡴࡰ࠰ࠥࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡࡽࢀࠦᾃ").format(e))
  @classmethod
  def bstack1l11lll1l1_opy_(self):
    return os.getenv(bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡊࡘࡃ࡚ࠩᾄ"), bstack1111l1_opy_ (u"ࠬࡌࡡ࡭ࡵࡨࠫᾅ")).lower()
  @classmethod
  def bstack1l11ll1l1l_opy_(self):
    return os.getenv(bstack1111l1_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡖࡅࡓࡅ࡜ࡣࡈࡇࡐࡕࡗࡕࡉࡤࡓࡏࡅࡇࠪᾆ"), bstack1111l1_opy_ (u"ࠧࠨᾇ"))
  @classmethod
  def bstack1l1l11ll1l1_opy_(cls, value):
    cls.bstack11l11111ll_opy_ = value
  @classmethod
  def bstack1111l11111l_opy_(cls):
    return cls.bstack11l11111ll_opy_
  @classmethod
  def bstack1l1l11ll111_opy_(cls, value):
    cls.percy_build_id = value
  @classmethod
  def bstack11111lll1ll_opy_(cls):
    return cls.percy_build_id