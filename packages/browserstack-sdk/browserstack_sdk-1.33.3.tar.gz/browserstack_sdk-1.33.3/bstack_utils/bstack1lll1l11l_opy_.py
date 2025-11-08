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
import sys
import logging
import tarfile
import io
import os
import time
import requests
import re
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bstack_utils.constants import bstack11l1ll1ll11_opy_, bstack11l1ll1llll_opy_, bstack11l1ll1l1l1_opy_
import tempfile
import json
bstack111l1l1lll1_opy_ = os.getenv(bstack1111l1_opy_ (u"ࠤࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡎࡒࡋࡤࡌࡉࡍࡇࠥᷞ"), None) or os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"ࠥࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡧࡩࡧࡻࡧ࠯࡮ࡲ࡫ࠧᷟ"))
bstack111l1l111ll_opy_ = os.path.join(bstack1111l1_opy_ (u"ࠦࡱࡵࡧࠣᷠ"), bstack1111l1_opy_ (u"ࠬࡹࡤ࡬࠯ࡦࡰ࡮࠳ࡤࡦࡤࡸ࡫࠳ࡲ࡯ࡨࠩᷡ"))
logging.Formatter.converter = time.gmtime
def get_logger(name=__name__, level=None):
  logger = logging.getLogger(name)
  if level:
    logging.basicConfig(
      level=level,
      format=bstack1111l1_opy_ (u"࠭ࠥࠩࡣࡶࡧࡹ࡯࡭ࡦࠫࡶࠤࡠࠫࠨ࡯ࡣࡰࡩ࠮ࡹ࡝࡜ࠧࠫࡰࡪࡼࡥ࡭ࡰࡤࡱࡪ࠯ࡳ࡞ࠢ࠰ࠤࠪ࠮࡭ࡦࡵࡶࡥ࡬࡫ࠩࡴࠩᷢ"),
      datefmt=bstack1111l1_opy_ (u"࡛ࠧࠦ࠰ࠩࡲ࠳ࠥࡥࡖࠨࡌ࠿ࠫࡍ࠻ࠧࡖ࡞ࠬᷣ"),
      stream=sys.stdout
    )
  return logger
def bstack1lll1111l1l_opy_():
  bstack111l1ll11ll_opy_ = os.environ.get(bstack1111l1_opy_ (u"ࠣࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡃࡋࡑࡅࡗ࡟࡟ࡅࡇࡅ࡙ࡌࠨᷤ"), bstack1111l1_opy_ (u"ࠤࡩࡥࡱࡹࡥࠣᷥ"))
  return logging.DEBUG if bstack111l1ll11ll_opy_.lower() == bstack1111l1_opy_ (u"ࠥࡸࡷࡻࡥࠣᷦ") else logging.INFO
def bstack1l1ll111lll_opy_():
  global bstack111l1l1lll1_opy_
  if os.path.exists(bstack111l1l1lll1_opy_):
    os.remove(bstack111l1l1lll1_opy_)
  if os.path.exists(bstack111l1l111ll_opy_):
    os.remove(bstack111l1l111ll_opy_)
def bstack11l1l1lll1_opy_():
  for handler in logging.getLogger().handlers:
    logging.getLogger().removeHandler(handler)
def configure_logger(config, log_level):
  bstack111l1l1l1l1_opy_ = log_level
  if bstack1111l1_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭ᷧ") in config and config[bstack1111l1_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧᷨ")] in bstack11l1ll1llll_opy_:
    bstack111l1l1l1l1_opy_ = bstack11l1ll1llll_opy_[config[bstack1111l1_opy_ (u"࠭࡬ࡰࡩࡏࡩࡻ࡫࡬ࠨᷩ")]]
  if config.get(bstack1111l1_opy_ (u"ࠧࡥ࡫ࡶࡥࡧࡲࡥࡂࡷࡷࡳࡈࡧࡰࡵࡷࡵࡩࡑࡵࡧࡴࠩᷪ"), False):
    logging.getLogger().setLevel(bstack111l1l1l1l1_opy_)
    return bstack111l1l1l1l1_opy_
  global bstack111l1l1lll1_opy_
  bstack11l1l1lll1_opy_()
  bstack111l1l111l1_opy_ = logging.Formatter(
    fmt=bstack1111l1_opy_ (u"ࠨࠧࠫࡥࡸࡩࡴࡪ࡯ࡨ࠭ࡸ࡛ࠦࠦࠪࡱࡥࡲ࡫ࠩࡴ࡟࡞ࠩ࠭ࡲࡥࡷࡧ࡯ࡲࡦࡳࡥࠪࡵࡠࠤ࠲ࠦࠥࠩ࡯ࡨࡷࡸࡧࡧࡦࠫࡶࠫᷫ"),
    datefmt=bstack1111l1_opy_ (u"ࠩࠨ࡝࠲ࠫ࡭࠮ࠧࡧࡘࠪࡎ࠺ࠦࡏ࠽ࠩࡘࡠࠧᷬ"),
  )
  bstack111l11llll1_opy_ = logging.StreamHandler(sys.stdout)
  file_handler = logging.FileHandler(bstack111l1l1lll1_opy_)
  file_handler.setFormatter(bstack111l1l111l1_opy_)
  bstack111l11llll1_opy_.setFormatter(bstack111l1l111l1_opy_)
  file_handler.setLevel(logging.DEBUG)
  bstack111l11llll1_opy_.setLevel(log_level)
  file_handler.addFilter(lambda r: r.name != bstack1111l1_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱ࠳ࡽࡥࡣࡦࡵ࡭ࡻ࡫ࡲ࠯ࡴࡨࡱࡴࡺࡥ࠯ࡴࡨࡱࡴࡺࡥࡠࡥࡲࡲࡳ࡫ࡣࡵ࡫ࡲࡲࠬᷭ"))
  logging.getLogger().setLevel(logging.DEBUG)
  bstack111l11llll1_opy_.setLevel(bstack111l1l1l1l1_opy_)
  logging.getLogger().addHandler(bstack111l11llll1_opy_)
  logging.getLogger().addHandler(file_handler)
  return bstack111l1l1l1l1_opy_
def bstack111l1l11lll_opy_(config):
  try:
    bstack111l1ll11l1_opy_ = set(bstack11l1ll1l1l1_opy_)
    bstack111l11lll1l_opy_ = bstack1111l1_opy_ (u"ࠫࠬᷮ")
    with open(bstack1111l1_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠨᷯ")) as bstack111l1l11l1l_opy_:
      bstack111l1ll1111_opy_ = bstack111l1l11l1l_opy_.read()
      bstack111l11lll1l_opy_ = re.sub(bstack1111l1_opy_ (u"ࡸࠧ࡟ࠪ࡟ࡷ࠰࠯࠿ࠤ࠰࠭ࠨࡡࡴࠧᷰ"), bstack1111l1_opy_ (u"ࠧࠨᷱ"), bstack111l1ll1111_opy_, flags=re.M)
      bstack111l11lll1l_opy_ = re.sub(
        bstack1111l1_opy_ (u"ࡳࠩࡡࠬࡡࡹࠫࠪࡁࠫࠫᷲ") + bstack1111l1_opy_ (u"ࠩࡿࠫᷳ").join(bstack111l1ll11l1_opy_) + bstack1111l1_opy_ (u"ࠪ࠭࠳࠰ࠤࠨᷴ"),
        bstack1111l1_opy_ (u"ࡶࠬࡢ࠲࠻ࠢ࡞ࡖࡊࡊࡁࡄࡖࡈࡈࡢ࠭᷵"),
        bstack111l11lll1l_opy_, flags=re.M | re.I
      )
    def bstack111l1ll111l_opy_(dic):
      bstack111l1l1111l_opy_ = {}
      for key, value in dic.items():
        if key in bstack111l1ll11l1_opy_:
          bstack111l1l1111l_opy_[key] = bstack1111l1_opy_ (u"ࠬࡡࡒࡆࡆࡄࡇ࡙ࡋࡄ࡞ࠩ᷶")
        else:
          if isinstance(value, dict):
            bstack111l1l1111l_opy_[key] = bstack111l1ll111l_opy_(value)
          else:
            bstack111l1l1111l_opy_[key] = value
      return bstack111l1l1111l_opy_
    bstack111l1l1111l_opy_ = bstack111l1ll111l_opy_(config)
    return {
      bstack1111l1_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭᷷ࠩ"): bstack111l11lll1l_opy_,
      bstack1111l1_opy_ (u"ࠧࡧ࡫ࡱࡥࡱࡩ࡯࡯ࡨ࡬࡫࠳ࡰࡳࡰࡰ᷸ࠪ"): json.dumps(bstack111l1l1111l_opy_)
    }
  except Exception as e:
    return {}
def bstack111l1l11l11_opy_(inipath, rootpath):
  log_dir = os.path.join(os.getcwd(), bstack1111l1_opy_ (u"ࠨ࡮ࡲ࡫᷹ࠬ"))
  if not os.path.exists(log_dir):
    os.makedirs(log_dir)
  bstack111l1l1l11l_opy_ = os.path.join(log_dir, bstack1111l1_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࡡࡦࡳࡳ࡬ࡩࡨࡵ᷺ࠪ"))
  if not os.path.exists(bstack111l1l1l11l_opy_):
    bstack111l1l1ll11_opy_ = {
      bstack1111l1_opy_ (u"ࠥ࡭ࡳ࡯ࡰࡢࡶ࡫ࠦ᷻"): str(inipath),
      bstack1111l1_opy_ (u"ࠦࡷࡵ࡯ࡵࡲࡤࡸ࡭ࠨ᷼"): str(rootpath)
    }
    with open(os.path.join(log_dir, bstack1111l1_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࡤࡩ࡯࡯ࡨ࡬࡫ࡸ࠴ࡪࡴࡱࡱ᷽ࠫ")), bstack1111l1_opy_ (u"࠭ࡷࠨ᷾")) as bstack111l1l11ll1_opy_:
      bstack111l1l11ll1_opy_.write(json.dumps(bstack111l1l1ll11_opy_))
def bstack111l11lll11_opy_():
  try:
    bstack111l1l1l11l_opy_ = os.path.join(os.getcwd(), bstack1111l1_opy_ (u"ࠧ࡭ࡱࡪ᷿ࠫ"), bstack1111l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧḀ"))
    if os.path.exists(bstack111l1l1l11l_opy_):
      with open(bstack111l1l1l11l_opy_, bstack1111l1_opy_ (u"ࠩࡵࠫḁ")) as bstack111l1l11ll1_opy_:
        bstack111l1l1llll_opy_ = json.load(bstack111l1l11ll1_opy_)
      return bstack111l1l1llll_opy_.get(bstack1111l1_opy_ (u"ࠪ࡭ࡳ࡯ࡰࡢࡶ࡫ࠫḂ"), bstack1111l1_opy_ (u"ࠫࠬḃ")), bstack111l1l1llll_opy_.get(bstack1111l1_opy_ (u"ࠬࡸ࡯ࡰࡶࡳࡥࡹ࡮ࠧḄ"), bstack1111l1_opy_ (u"࠭ࠧḅ"))
  except:
    pass
  return None, None
def bstack111l1l1l1ll_opy_():
  try:
    bstack111l1l1l11l_opy_ = os.path.join(os.getcwd(), bstack1111l1_opy_ (u"ࠧ࡭ࡱࡪࠫḆ"), bstack1111l1_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࡠࡥࡲࡲ࡫࡯ࡧࡴ࠰࡭ࡷࡴࡴࠧḇ"))
    if os.path.exists(bstack111l1l1l11l_opy_):
      os.remove(bstack111l1l1l11l_opy_)
  except:
    pass
def bstack11ll111ll_opy_(config):
  try:
    from bstack_utils.helper import bstack11ll1l111l_opy_, bstack11lll1ll_opy_
    from browserstack_sdk.sdk_cli.cli import cli
    global bstack111l1l1lll1_opy_
    if config.get(bstack1111l1_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡹࡹࡵࡃࡢࡲࡷࡹࡷ࡫ࡌࡰࡩࡶࠫḈ"), False):
      return
    uuid = os.getenv(bstack1111l1_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡗࡉࡘ࡚ࡈࡖࡄࡢ࡙࡚ࡏࡄࠨḉ")) if os.getenv(bstack1111l1_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡘࡊ࡙ࡔࡉࡗࡅࡣ࡚࡛ࡉࡅࠩḊ")) else bstack11ll1l111l_opy_.get_property(bstack1111l1_opy_ (u"ࠧࡹࡤ࡬ࡔࡸࡲࡎࡪࠢḋ"))
    if not uuid or uuid == bstack1111l1_opy_ (u"࠭࡮ࡶ࡮࡯ࠫḌ"):
      return
    bstack111l1l1ll1l_opy_ = [bstack1111l1_opy_ (u"ࠧࡳࡧࡴࡹ࡮ࡸࡥ࡮ࡧࡱࡸࡸ࠴ࡴࡹࡶࠪḍ"), bstack1111l1_opy_ (u"ࠨࡒ࡬ࡴ࡫࡯࡬ࡦࠩḎ"), bstack1111l1_opy_ (u"ࠩࡳࡽࡵࡸ࡯࡫ࡧࡦࡸ࠳ࡺ࡯࡮࡮ࠪḏ"), bstack111l1l1lll1_opy_, bstack111l1l111ll_opy_]
    bstack111l1l11111_opy_, root_path = bstack111l11lll11_opy_()
    if bstack111l1l11111_opy_ != None:
      bstack111l1l1ll1l_opy_.append(bstack111l1l11111_opy_)
    if root_path != None:
      bstack111l1l1ll1l_opy_.append(os.path.join(root_path, bstack1111l1_opy_ (u"ࠪࡧࡴࡴࡦࡵࡧࡶࡸ࠳ࡶࡹࠨḐ")))
    bstack11l1l1lll1_opy_()
    logging.shutdown()
    output_file = os.path.join(tempfile.gettempdir(), bstack1111l1_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠱ࡱࡵࡧࡴ࠯ࠪḑ") + uuid + bstack1111l1_opy_ (u"ࠬ࠴ࡴࡢࡴ࠱࡫ࡿ࠭Ḓ"))
    with tarfile.open(output_file, bstack1111l1_opy_ (u"ࠨࡷ࠻ࡩࡽࠦḓ")) as archive:
      for file in filter(lambda f: os.path.exists(f), bstack111l1l1ll1l_opy_):
        try:
          archive.add(file,  arcname=os.path.basename(file))
        except:
          pass
      for name, data in bstack111l1l11lll_opy_(config).items():
        tarinfo = tarfile.TarInfo(name)
        bstack111l1l1l111_opy_ = data.encode()
        tarinfo.size = len(bstack111l1l1l111_opy_)
        archive.addfile(tarinfo, io.BytesIO(bstack111l1l1l111_opy_))
    bstack11l1l1l1l1_opy_ = MultipartEncoder(
      fields= {
        bstack1111l1_opy_ (u"ࠧࡥࡣࡷࡥࠬḔ"): (os.path.basename(output_file), open(os.path.abspath(output_file), bstack1111l1_opy_ (u"ࠨࡴࡥࠫḕ")), bstack1111l1_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯ࡹ࠯ࡪࡾ࡮ࡶࠧḖ")),
        bstack1111l1_opy_ (u"ࠪࡧࡱ࡯ࡥ࡯ࡶࡅࡹ࡮ࡲࡤࡖࡷ࡬ࡨࠬḗ"): uuid
      }
    )
    bstack111l11lllll_opy_ = bstack11lll1ll_opy_(cli.config, [bstack1111l1_opy_ (u"ࠦࡦࡶࡩࡴࠤḘ"), bstack1111l1_opy_ (u"ࠧࡵࡢࡴࡧࡵࡺࡦࡨࡩ࡭࡫ࡷࡽࠧḙ"), bstack1111l1_opy_ (u"ࠨࡵࡱ࡮ࡲࡥࡩࠨḚ")], bstack11l1ll1ll11_opy_)
    response = requests.post(
      bstack1111l1_opy_ (u"ࠢࡼࡿ࠲ࡧࡱ࡯ࡥ࡯ࡶ࠰ࡰࡴ࡭ࡳ࠰ࡷࡳࡰࡴࡧࡤࠣḛ").format(bstack111l11lllll_opy_),
      data=bstack11l1l1l1l1_opy_,
      headers={bstack1111l1_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡗࡽࡵ࡫ࠧḜ"): bstack11l1l1l1l1_opy_.content_type},
      auth=(config[bstack1111l1_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫḝ")], config[bstack1111l1_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭Ḟ")])
    )
    os.remove(output_file)
    if response.status_code != 200:
      get_logger().debug(bstack1111l1_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣࡹࡵࡲ࡯ࡢࡦࠣࡰࡴ࡭ࡳ࠻ࠢࠪḟ") + response.status_code)
  except Exception as e:
    get_logger().debug(bstack1111l1_opy_ (u"ࠬࡋࡸࡤࡧࡳࡸ࡮ࡵ࡮ࠡ࡫ࡱࠤࡸ࡫࡮ࡥ࡫ࡱ࡫ࠥࡲ࡯ࡨࡵ࠽ࠫḠ") + str(e))
  finally:
    try:
      bstack1l1ll111lll_opy_()
      bstack111l1l1l1ll_opy_()
    except:
      pass