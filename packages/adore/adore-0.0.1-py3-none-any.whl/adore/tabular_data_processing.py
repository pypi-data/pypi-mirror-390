# -*- coding: utf-8 -*-
"""
Module Name: tabular_data_processing.py
Description:
    This module is designed to provide functions for efficiently calculating derivative matrices for tabular data.
    It contains functions for constructing the feature matrices of tabular data, perturbation functions, and functions for calculating first- and second-order derivatives.

Author:
    Fang Anran <fanganran97@126.com>

Maintainer:
    Fang Anran <fanganran97@126.com>

Contributors:
    Chao Lemen <chaolemen@ruc.edu.cn>
    Lei Ming <leimingnick@ruc.edu.cn>
    Fang Anran <fanganran97@126.com>

Created on: 2024-12-25
Last Modified on: 2024-12-25
Version: [0.0.1]

License:
    This module is licensed under GPL-3.0 . See LICENSE file for details.

Usage Example:
    # >>> from adore.tabular_data_processing import construct_table_feature_matrix, compute_tabel_derivative_matrix
"""

import logging
from typing import Union

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from adore.utils import extract_prediction_scalar

# Set up logger
logger = logging.getLogger(__name__)


def construct_table_feature_matrix(data: Union[np.ndarray, list, tuple, pd.DataFrame]) -> np.ndarray:
    """
    Convert input data into a NumPy array. Supports input types: numpy.ndarray, list, tuple, pandas.DataFrame.

    Args:
        data: Input data to be converted

    Returns:
        np.ndarray: Converted NumPy array

    Raises:
        TypeError: If input data type is not supported
        ValueError: If input data is empty or contains invalid values
    """
    logger.info("Starting to construct table feature matrix")

    if data is None or len(data) == 0:
        raise ValueError("Input data cannot be empty")

    try:
        if isinstance(data, np.ndarray):
            return data
        elif isinstance(data, (list, tuple)):
            return np.array(data)
        elif isinstance(data, pd.DataFrame):
            return data.values
        else:
            raise TypeError("Input data must be of type np.ndarray, list, tuple, or pd.DataFrame")
    except Exception as e:
        logger.error(f"Data conversion failed: {str(e)}")
        raise ValueError(f"Data conversion failed: {str(e)}")


def _compute_dense_delta(X: np.ndarray,
                         delta_method: str,
                         epsilon: float) -> np.ndarray:
    """
    Generate adaptive perturbation values for input data.

    Args:
        X: Input feature matrix
        delta_method: Method for computing perturbations, options: 'std', 'range', or 'single'
        epsilon: Perturbation scaling factor

    Returns:
        np.ndarray: Perturbation values matrix with shape (m,n)

    Raises:
        ValueError: If delta_method is invalid or epsilon is illegal
    """
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    if delta_method not in ['std', 'range', 'single']:
        raise ValueError("delta_method must be one of 'std', 'range', or 'single'")

    logger.info("### Start computing delta matrix")
    n_samples, n_features = X.shape
    delta = np.zeros((n_samples, n_features))

    try:
        for j in range(n_features):
            if delta_method == 'std':
                sigma_j = np.std(X[:, j])
                delta[:, j] = epsilon if sigma_j == 0 else epsilon * sigma_j
            elif delta_method == 'range':
                range_j = np.max(X[:, j]) - np.min(X[:, j])
                delta[:, j] = epsilon if range_j == 0 else epsilon * range_j
            elif delta_method == 'single':
                delta[:, j] = epsilon
    except Exception as e:
        logger.error(f"Error occurred while computing delta matrix: {str(e)}")
        raise RuntimeError(f"Error occurred while computing delta matrix: {str(e)}")

    logger.info("### Finished computing delta matrix")
    return delta

def compute_table_derivative_matrix(model: object,
                                    X: np.ndarray,
                                    epsilon: float,
                                    delta_method: str,
                                    tau_threshold: float,
                                    n_jobs: int) -> np.ndarray:
    """
    Compute derivative matrix d_matrix for tabular data.

    Args:
        model: Trained model with predict method
        X: Dataset for computing derivatives
        epsilon: Scaling factor for determining delta values
        delta_method: Method for computing perturbations
        tau_threshold: Threshold for deciding between first and second order derivatives
        n_jobs: Number of parallel jobs for computation

    Returns:
        np.ndarray: Derivative matrix with dimensions (n_samples, n_features)

    Raises:
        ValueError: If input parameters are invalid
        RuntimeError: If error occurs during computation
    """
    if not hasattr(model, 'predict'):
        raise ValueError("Model must have a predict method")
    if tau_threshold <= 0:
        raise ValueError("tau_threshold must be in range (0,inf)")

    logger.info("### Start computing d_matrix matrix for tabular data")
    try:
        n_samples, n_features = X.shape
        J_D = np.zeros((n_samples, n_features))
        H_D = np.zeros((n_samples, n_features))

        delta = _compute_dense_delta(X, delta_method, epsilon)

        # Use parallel computation to collect all results
        logger.info("Starting parallel computation for derivatives")
        results = Parallel(n_jobs=n_jobs)(
            delayed(_compute_derivatives)(model, X, delta, i, j)
            for i in range(n_samples)
            for j in range(n_features)
        )

        # Update J_D and H_D with computed results
        for i, j, J_val, H_val in results:
            J_D[i, j] = J_val
            H_D[i, j] = H_val

        # Compute norm of H_D and J_D to decide which to use
        norm_H_D = np.linalg.norm(H_D, 'fro')
        norm_J_D = np.linalg.norm(J_D, 'fro')
        tau = norm_H_D / (1 + norm_J_D)
        logger.info(f"Calculated tau: {tau}")

        D = J_D if tau < tau_threshold else H_D
        logger.info(f"Using {'first' if tau < tau_threshold else 'second'} order derivatives")

    except Exception as e:
        logger.error(f"Error occurred while computing d_matrix matrix: {str(e)}")
        raise RuntimeError(f"Error occurred while computing d_matrix matrix: {str(e)}")

    logger.info("### Finished computing d_matrix matrix for tabular data")
    return D


def _compute_derivatives(model: object, X: np.ndarray, delta: np.ndarray, i: int, j: int):
    """
    Compute first-order and second-order derivatives for a single feature.

    Args:
        model: Trained model with predict method
        X: Dataset for computing derivatives
        delta: Perturbation matrix
        i: Index of the sample
        j: Index of the feature

    Returns:
        Tuple[int, int, float, float]: Sample index, feature index, first-order derivative, second-order derivative
    """
    try:
        x_i = X[i].copy()
        x_perturbed_pos = x_i.copy()
        x_perturbed_neg = x_i.copy()

        x_perturbed_pos[j] += delta[i, j]
        x_perturbed_neg[j] -= delta[i, j]

        prediction = model.predict(x_i.reshape(1, -1))
        prediction_pos = model.predict(x_perturbed_pos.reshape(1, -1))
        prediction_neg = model.predict(x_perturbed_neg.reshape(1, -1))

        y_i, y_pos, y_neg = extract_prediction_scalar(
            prediction, prediction_pos, prediction_neg)

        J_val = (y_pos - y_neg) / (2 * delta[i, j])
        H_val = (y_pos - 2 * y_i + y_neg) / (delta[i, j] ** 2)
        return i, j, J_val, H_val

    except Exception as e:
        logger.error(f"Error occurred while computing derivatives for sample {i}, feature {j}: {str(e)}")
        raise RuntimeError(f"Error occurred while computing derivatives: {str(e)}")
