# -*- coding: utf-8 -*-
"""
Module Name: storytelling.py
Description:
    This module is intended to provide functions for generating data storytelling.
    It contains functions to create a narrative story in Freytag pyramid structure and a narrative story in ABT (And, But, Therefore) format.

Author:
    Chao Lemen <chaolemen@ruc.edu.cn>

Maintainer:
    Chao Lemen <chaolemen@ruc.edu.cn>

Contributors:
    Chao Lemen <chaolemen@ruc.edu.cn>


Created on: 2025-1-3
Last Modified on: 2025-1-3
Version: [0.0.1]

License:
    This module is licensed under GPL-3.0 . See LICENSE file for details.

Usage Example:
    #from adore.storytelling import generate_freytag_story, generate_abt_story, select_top_k_feature_contributions
"""
import logging

import numpy as np
import pandas as pd

# Set up logger
logger = logging.getLogger(__name__)


def generate_freytag_story(feature_contributions, X_index, feature_names, top_k_contributions_df, model_name,
                           language='english'):
    """
    Create a Freytag pyramid structured narrative story based on the feature contribution analysis.

    Args:
    - feature_contributions: np.ndarray, The matrix containing feature contributions for each sample.
    - X_index: list, Indices of the samples in the dataset.
    - feature_names: list, Names of the features used in the model.
    - top_k_contributions_df: pd.DataFrame, DataFrame containing the top k contributions and their corresponding features.
    - model_name: str, Name of the model used for analysis.
    - language: str, Language of the story ('english' or 'chinese').

    Returns:
    - story: str, Narrative structured as a Freytag pyramid.
    """
    logger.info("Starting to generate Freytag story for model: %s", model_name)

    if language.lower() == 'chinese':
        # Chinese version here (removed for brevity)
        pass
    else:
        story = f"In this analysis, we used a {model_name}."
        logger.debug("Exposition part: Introducing dataset and model")
        exposition = "**Exposition:** Introduction of the dataset and the model."
        exposition += f"We analyzed a dataset with the following features: {', '.join(feature_names)}, and trained a {model_name}."

        logger.debug("Rising action part: Identifying important features")
        rising_action = "**Rising Action:** Description of important features. Through contribution analysis, we identified the following features as significantly contributing to the model's predictions:"

        for idx, row in top_k_contributions_df.iterrows():
            feature_name = row['Feature Name']
            contribution_value = row['Contribution']
            rising_action += f"\n- Feature '{feature_name}' has a contribution value of {contribution_value:.6f}"

        logger.debug("Climax part: Highlighting key findings")
        climax = "**Climax:** Emphasizing the main findings and their significance. The high contribution values of these features indicate that they play a crucial role in predicting the target variable."

        logger.debug("Falling action and Denouement: Discussing impact and proposing future improvements")
        falling_action = "**Falling Action:** Discussing the impact of these findings on the model. However, these contributions do not fully explain all prediction results, suggesting that the model may be influenced by other unanalyzed features."
        denouement = "**Denouement:** Proposing future improvement directions. Therefore, we plan to further optimize the model or incorporate additional relevant features to enhance prediction performance."

        story += exposition + rising_action + climax + falling_action + denouement

    logger.info("Completed generating Freytag story")
    return story


def select_top_k_feature_contributions(feature_contributions, feature_names, k=5):
    """
    Select the top k feature contributions from the contribution matrix.

    Args:
    - feature_contributions: np.ndarray, Feature contribution matrix.
    - feature_names: list, Feature names.
    - k: int, Number of top contributions to select.

    Returns:
    - top_k_contributions_df: pd.DataFrame, DataFrame containing the top k contributions and corresponding sample numbers.
    """
    logger.info("Starting to select top %d feature contributions", k)

    abs_feature_contributions = np.abs(feature_contributions)

    flat_contributions = abs_feature_contributions.flatten()
    top_k_indices = flat_contributions.argsort()[-k:][::-1]

    sample_indices, feature_indices = np.unravel_index(top_k_indices, feature_contributions.shape)

    top_k_contributions_df = pd.DataFrame({
        'Sample Number': sample_indices + 1,  # 1-based indexing for sample number
        'Feature Name': [feature_names[i] for i in feature_indices],
        'Contribution': feature_contributions[sample_indices, feature_indices]
    })

    logger.info("Completed selecting top %d feature contributions", k)
    return top_k_contributions_df
