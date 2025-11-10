import pandas as pd

def plot_coverage_vs_confidence(summary_df: pd.DataFrame, title: str = "Coverage and Prediction Set Composition"):
    """
    Plot empirical coverage and prediction set type proportions against confidence level.

    Parameters
    ----------
    summary_df : pd.DataFrame
        Must contain columns: ['Confidence', 'Coverage', 'One_Class_Correct', 'One_Class_Incorrect', 'Two_Class_Sets', 'No_Sets']
    title : str
        Title of the plot.
    """
    # Convert to long format for area chart
    melted = summary_df.melt(
        id_vars=["Confidence", "Coverage"],
        value_vars=["One_Class_Correct", "One_Class_Incorrect", "Two_Class_Sets", "No_Sets"],
        var_name="Set_Type",
        value_name="Percentage"
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    # Area plot of uncertainty composition
    for key, grp in melted.groupby("Set_Type"):
        ax.fill_between(grp["Confidence"], grp["Percentage"], label=key, alpha=0.4)

    # Overlay coverage line
    ax.plot(summary_df["Confidence"], summary_df["Coverage"], color="blue", linewidth=2, label="Empirical Coverage")
    ax.plot(summary_df["Confidence"], summary_df["Confidence"], linestyle="--", color="red", label="Ideal Coverage")

    ax.set_xlabel("Confidence (1 - α)")
    ax.set_ylabel("Proportion / Coverage")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.show()

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_prediction_set_size_distribution(prediction_sets: list, title: str = "Prediction Set Size Distribution"):
    """
    Plot the distribution of prediction set sizes.

    Parameters
    ----------
    prediction_sets : list of lists
        Each inner list is the prediction set for one sample.
    title : str
        Title of the plot.
    """
    sizes = [len(s) for s in prediction_sets]
    size_series = pd.Series(sizes)

    plt.figure(figsize=(8, 5))
    sns.countplot(x=size_series)
    plt.xlabel("Prediction Set Size")
    plt.ylabel("Count")
    plt.title(title)
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.show()

def plot_set_size_vs_true_label(prediction_sets: list, y_true: list, title: str = "Set Size vs True Label"):
    """
    Plot a stacked bar chart showing the distribution of true labels for each prediction set size.

    Parameters
    ----------
    prediction_sets : list of lists
        Each inner list is the prediction set for one sample.
    y_true : list or np.array
        True labels for each instance.
    title : str
        Title of the plot.
    """
    sizes = [len(s) for s in prediction_sets]
    df = pd.DataFrame({"Set_Size": sizes, "True_Label": y_true})

    size_label_counts = df.groupby(["Set_Size", "True_Label"]).size().unstack(fill_value=0)
    size_label_props = size_label_counts.div(size_label_counts.sum(axis=1), axis=0)

    size_label_props.plot(kind="bar", stacked=True, figsize=(8, 5))
    plt.xlabel("Prediction Set Size")
    plt.ylabel("Proportion of True Labels")
    plt.title(title)
    plt.legend(title="True Label")
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.show()

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def plot_nonconformity_scores(
    y_calib,
    scores_calib,
    y_test,
    scores_test,
    qhat,
    title="Nonconformity Scores",
    palette={0: "red", 1: "cyan"}
):
    """
    Plot nonconformity scores for calibration and test sets, highlighting class and q̂ threshold.

    Parameters
    ----------
    y_calib : array-like
        True labels of the calibration set.

    scores_calib : array-like
        Nonconformity scores of the calibration set.

    y_test : array-like
        True labels of the test set.

    scores_test : array-like
        Nonconformity scores of the test set.

    qhat : float
        Quantile threshold (1 - alpha).

    title : str
        Title of the plot.

    palette : dict
        Color mapping for class labels.
    """
    df_calib = pd.DataFrame({
        "Instance": np.arange(len(y_calib)),
        "Score": scores_calib,
        "Default": y_calib,
        "Set": "Calibration"
    })

    df_test = pd.DataFrame({
        "Instance": np.arange(len(y_test)),
        "Score": scores_test,
        "Default": y_test,
        "Set": "Test"
    })

    df_plot = pd.concat([df_calib, df_test], ignore_index=True)

    plt.figure(figsize=(12, 5))
    sns.scatterplot(
        data=df_plot,
        x="Instance",
        y="Score",
        hue="Default",
        style="Set",
        alpha=0.3,
        palette=palette
    )
    plt.axhline(y=qhat, color="cyan", linestyle="dashed", label="Umbral q̂")
    plt.ylim(0, 1)
    plt.title(title)
    plt.ylabel("Nonconformity Score")
    plt.xlabel("Instance")
    plt.legend(title="Class / Set")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot_conformal_coverage_vs_confidence(calibration_scores, probs_test, y_test, alphas=np.arange(0.01, 0.61, 0.01)):
    """
    Plot coverage and uncertainty metrics for conformal prediction using a stacked area chart.

    Parameters
    ----------
    calibration_scores : array-like of shape (n_samples,)
        Nonconformity scores from the calibration set.

    probs_test : array-like of shape (n_samples, n_classes)
        Predicted probabilities for the test set.

    y_test : array-like of shape (n_samples,)
        True labels for the test set.

    alphas : array-like
        List of alpha values to evaluate (default is np.arange(0.01, 0.61, 0.01)).

    Returns
    -------
    None
        Displays the plot.
    """
    calibration_scores = np.asarray(calibration_scores)
    probs_test = np.asarray(probs_test)
    y_test = np.asarray(y_test)

    metrics = []

    for alpha in alphas:
        qhat = np.quantile(calibration_scores, 1 - alpha)

        prediction_sets = [np.where(1 - prob <= qhat)[0].tolist() for prob in probs_test]

        covered = [y in pset for y, pset in zip(y_test, prediction_sets)]
        one_class_correct = [len(pset) == 1 and y == pset[0] for y, pset in zip(y_test, prediction_sets)]
        one_class_incorrect = [len(pset) == 1 and y != pset[0] for y, pset in zip(y_test, prediction_sets)]
        two_class_sets = [len(pset) == 2 for pset in prediction_sets]
        no_sets = [len(pset) == 0 for pset in prediction_sets]

        metrics.append({
            "Confidence": 1 - alpha,
            "Coverage": np.mean(covered),
            "One_Class_Correct": np.mean(one_class_correct),
            "One_Class_Incorrect": np.mean(one_class_incorrect),
            "Two_Class_Sets": np.mean(two_class_sets),
            "No_Sets": np.mean(no_sets)
        })

    df = pd.DataFrame(metrics)
    df = df.sort_values("Confidence")

    # Prepare stacked area values
    x = df["Confidence"]
    y_values = [
        df["One_Class_Correct"],
        df["One_Class_Incorrect"],
        df["Two_Class_Sets"],
        df["No_Sets"]
    ]
    labels = ["One_Class_Correct", "One_Class_Incorrect", "Two_Class_Sets", "No_Sets"]
    colors = ["#2ca02c", "#d62728", "#1f77b4", "#7f7f7f"]

    # Plot
    plt.figure(figsize=(12, 6))
    plt.stackplot(x, *y_values, labels=labels, colors=colors, alpha=0.5)

    # Overlay coverage line
    plt.plot(x, df["Coverage"], color="blue", linewidth=2, label="Coverage")
    plt.plot(x, x, linestyle="--", color="red", label="Ideal")

    plt.title("Coverage and Prediction Set Uncertainty")
    plt.xlabel("Confidence Level (1 - α)")
    plt.ylabel("Empirical Coverage / Percentage")
    plt.ylim(0, 1.05)
    plt.legend(loc="upper left", title="Set Type")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()
