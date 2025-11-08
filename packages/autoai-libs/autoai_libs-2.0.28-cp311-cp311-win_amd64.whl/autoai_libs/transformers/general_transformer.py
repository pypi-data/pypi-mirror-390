################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R, 5737-L65
# (c) Copyright IBM Corp. 2021-2025. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################
from abc import ABC, abstractmethod

import sklearn
import numpy as np

from autoai_libs.mixins.optimization import OptimizationParametersMixin


class AutoAITransformer(ABC, sklearn.base.TransformerMixin, OptimizationParametersMixin):
    """
    This makes explicit the methods that are implicit in the sklearn.base.TransformerMixin.  The fit() method tunes the
    transformer to match the data, and the transform method manipulates the data based on what it decided to do in fit().
    """

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray = None) -> "AutoAITransformer":
        pass

    @abstractmethod
    def transform(self, X: np.ndarray) -> np.ndarray:
        pass
