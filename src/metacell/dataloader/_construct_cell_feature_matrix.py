from __future__ import annotations
from typing import TYPE_CHECKING
from warnings import warn

# 类型检查时才会生效，运行时不会导入这些模块，避免不必要的依赖加载。
if TYPE_CHECKING:
    from anndata import AnnData



