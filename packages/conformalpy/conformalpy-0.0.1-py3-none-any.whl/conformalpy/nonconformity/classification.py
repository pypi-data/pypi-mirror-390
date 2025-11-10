import numpy as np

def prob_complement_nonconformity(y_true, y_prob):
        """
        Compute nonconformity scores using the complementary probability method.

        This nonconformity function is defined as:

            A(x, y) = 1 - P(y | x)

        Where:
            - y is the true label (integer: 0, 1, ..., n_classes - 1)
            - P(y | x) is the predicted probability of the true class

        For each observation i:
            A(x_i, y_i) = 1 - P(y_i | x_i)

        Parameters
        ----------
        y_true : array-like of shape (n_samples,)
            True class labels (integers from 0 to n_classes - 1).

        y_prob : array-like of shape (n_samples, n_classes)
            Predicted class probabilities from the classifier.

        Returns
        -------
        np.ndarray of shape (n_samples,)
            Nonconformity scores for each instance.

        Raises
        ------
        ValueError
            If inputs are not of compatible shapes or contain invalid values.
        """
        y_true = np.asarray(y_true)
        y_prob = np.asarray(y_prob)

        # Check that y_prob is a 2D array
        if y_prob.ndim != 2:
            raise ValueError(f"`y_prob` must be a 2D array of shape (n_samples, n_classes), got shape {y_prob.shape}.")

        # Check that y_true is 1D and matches y_prob in sample size
        if y_true.ndim != 1:
            raise ValueError(f"`y_true` must be a 1D array, got shape {y_true.shape}.")
        if len(y_true) != y_prob.shape[0]:
            raise ValueError(f"Number of samples in `y_true` and `y_prob` must match. "
                             f"Got {len(y_true)} and {y_prob.shape[0]}.")

        # Check that all y_true values are valid class indices
        n_classes = y_prob.shape[1]
        if not np.all((y_true >= 0) & (y_true < n_classes)):
            raise ValueError(f"Values in `y_true` must be integers between 0 and {n_classes - 1}.")

        # Compute the predicted probability for the true class
        true_class_probs = y_prob[np.arange(len(y_true)), y_true]

        # Return 1 - probability of the true class (nonconformity score)
        return 1.0 - true_class_probs
