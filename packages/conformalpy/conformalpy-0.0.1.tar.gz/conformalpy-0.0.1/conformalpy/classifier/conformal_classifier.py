from typing import Callable, List
import numpy as np
from sklearn.utils.validation import check_is_fitted
from sklearn.exceptions import NotFittedError

class ConformalClassifier:
    def __init__(self, model, alpha: float=0.1, nonconformity_function: Callable=None, mondrian: bool=False):
        """
        Initialize the conformal classifier.

        Parameters
        ----------
        model : Any
            The classification model to use for predictions.
        alpha : float, optional
            Significance level for the conformal prediction, by default 0.1.
        nonconformity_function : Callable, optional
            Function to compute nonconformity scores, by default None.
        mondrian : bool, optional
            Whether to use Mondrian conformal prediction, by default False (use ICP).
        """
        self.model = model
        self._alpha = alpha
        self._nonconformity_function = nonconformity_function
        self._calibration_scores = None
        self._qhat = None
        self.mondrian = mondrian

        # Verify that the model has predict_proba method
        if not hasattr(self.model, 'predict_proba'):
            raise ValueError("The model must implement a 'predict_proba' method.")

        # Check if the model is fitted
        try:
            check_is_fitted(self.model)
        except NotFittedError:
            raise NotFittedError("The model must be fitted before using ConformalClassifier.")


    @property
    def alpha(self):
        """
        Get the significance level for the conformal prediction.

        Returns
        -------
        float
            The significance level.
        """
        return self._alpha

    @alpha.setter
    def alpha(self, value: float):
        """
        Set the significance level for the conformal prediction.

        Parameters
        ----------
        value : float
            The new significance level.
        """
        if not (0 < value < 1):
            raise ValueError("Alpha must be in the range (0, 1).")
        self._alpha = value

    @property
    def nonconformity_function(self):
        """
        Get the nonconformity function used for scoring.

        Returns
        -------
        Callable
            The nonconformity function.
        """
        return self._nonconformity_function

    @nonconformity_function.setter
    def nonconformity_function(self, func: Callable):
        """
        Set the nonconformity function used for scoring.

        Parameters
        ----------
        func : Callable
            The new nonconformity function.
        """
        if not callable(func):
            raise ValueError("Nonconformity function must be callable.")
        self._nonconformity_function = func

    def calibrate(self, X_calib: np.ndarray, y_calib: np.array) -> np.ndarray:
        """
        Calibrate the conformal classifier using a calibration set.

        Parameters
        ----------
        X_calib : np.ndarray
            Calibration features.
        y_calib : np.ndarray
            Calibration labels.

        Returns
        -------
        np.ndarray
            Nonconformity scores for the calibration set.
        """
        if self._nonconformity_function is None:
            raise ValueError("Nonconformity function must be set before calibration.")

        # Get predictions and compute nonconformity scores
        probs = self.model.predict_proba(X_calib)
        self._calibration_scores = self._nonconformity_function(y_calib, probs)
        if self._calibration_scores is None:
            raise ValueError("Nonconformity function must return nonconformity scores.")
        if len(y_calib) != len(self._calibration_scores):
            raise ValueError("Calibration scores must match the number of calibration labels.")
        # Compute the quantile for the significance level
        if self.mondrian:
            # For Mondrian conformal prediction, we need to compute the quantile
            # for each class separately
            classes = np.unique(y_calib)
            self._qhat = {
                y: np.quantile(self._calibration_scores[y_calib == y], 1 - self.alpha)
                for y in classes
            }

        else:
            self._qhat = np.quantile(self._calibration_scores, 1 - self._alpha)

        return self._calibration_scores

    def get_qhat(self):
        """
        Get the quantile threshold for the nonconformity scores.

        Returns
        -------
        float
            The quantile threshold.
        """
        if self._qhat is None:
            raise ValueError("Calibration must be performed before getting qhat.")
        return self._qhat

    def predict(self, X: np.ndarray) -> List[List[int]]:
        """
        Predict conformal prediction sets for the given input data.

        Parameters
        ----------
        X : np.ndarray
            Input features of shape (n_samples, n_features)

        Returns
        -------
        List[List[int]]
            List of prediction sets, one per input instance.
            Each prediction set contains class labels that conform to the threshold.
        """
        if self._qhat is None:
            raise ValueError("Model must be calibrated before calling predict().")

        # Get predicted probabilities (shape: [n_samples, n_classes])
        probas = self.model.predict_proba(X)
        n_samples, n_classes = probas.shape

        prediction_sets = []

        for i in range(n_samples):
            current_set = []
            for y in range(n_classes):
                nonconformity = 1.0 - probas[i, y]  # Nonconformity score for label y

                if self.mondrian:
                    qhat_y = self._qhat.get(y, 1.0)  # fallback if class was not seen in calibration
                else:
                    qhat_y = self._qhat

                if nonconformity <= qhat_y:
                    current_set.append(y)

            prediction_sets.append(current_set)

        return prediction_sets
