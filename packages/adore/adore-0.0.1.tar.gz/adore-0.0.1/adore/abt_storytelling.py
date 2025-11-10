import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_abt_story(feature_contributions, X_index, feature_names, top_k_contributions_df, model_name,
                       language='english'):
    """
    Create an ABT (And, But, Therefore) format narrative story based on feature contribution analysis.

    Args:
    - feature_contributions: np.ndarray, The matrix containing feature contributions for each sample.
    - X_index: list, Indices of the samples in the dataset.
    - feature_names: list, Names of the features used in the model.
    - top_k_contributions_df: pd.DataFrame, DataFrame containing the top k contributions and their corresponding features.
    - model_name: str, Name of the model used for analysis.
    - language: str, Language of the story ('english' or 'chinese').

    Returns:
    - and_part: str, The "AND" section of the story.
    - but_part: str, The "BUT" section of the story.
    - therefore_part: str, The "THEREFORE" section of the story.
    """
    logger.info("Starting to generate ABT story for model: %s", model_name)

    # Sorting top and low contributions
    top_k_contributions_df['Absolute Contribution'] = top_k_contributions_df['Contribution'].abs()
    top_k_contributions_sorted = top_k_contributions_df.sort_values(by='Absolute Contribution', ascending=False)
    top_contributions = top_k_contributions_sorted.head(5)
    low_contributions = top_k_contributions_sorted.tail(5)

    if language.lower() == 'english':
        logger.debug("ABT Story - Generating AND, BUT, and THEREFORE parts")

        # **AND**: Setting context and establishing the purpose
        and_part = f"We used the {model_name} to analyze the key factors influencing the target outcome.\n\n"
        and_part += "The primary goal of this analysis is to understand which features significantly impact the target variable and how we can optimize decision-making based on these insights.\n\n"
        and_part += "Our model evaluated the following features:\n"
        for feature in feature_names:
            and_part += f"- **{feature}**: Represents data related to this specific feature.\n"
        and_part += "\nThrough this analysis, we identified the top contributing features and samples:\n"
        for idx, row in top_contributions.iterrows():
            sample_index = row['Sample Number']
            feature_name = row['Feature Name']
            contribution_value = row['Contribution']
            and_part += (f"- Sample {sample_index} with feature '{feature_name}' contributed {contribution_value:.6f}, "
                         f"representing {row['Absolute Contribution']:.2f}% of the total impact.\n")

        # **BUT**: Highlighting challenges or unexpected findings
        but_part = "\nHowever, our analysis also revealed several challenges and limitations:\n\n"
        for idx, row in low_contributions.iterrows():
            sample_index = row['Sample Number']
            feature_name = row['Feature Name']
            contribution_value = row['Contribution']
            if contribution_value < 0:
                but_part += (
                    f"- The feature '{feature_name}' for Sample {sample_index} showed a negative contribution (-{abs(contribution_value):.6f}), "
                    f"suggesting that this feature may have had an adverse or counterintuitive effect in this specific scenario.\n")
            else:
                but_part += (
                    f"- The feature '{feature_name}' for Sample {sample_index} contributed only {contribution_value:.6f}, "
                    f"indicating a minimal impact on the target outcome in this case.\n")

        but_part += "\nThese issues may arise due to:\n"
        but_part += "- Variations in data or conditions, such as regional differences, seasonal trends, or market anomalies.\n"
        but_part += "- Missing contextual features that could provide additional insights into the outcomes.\n"
        but_part += "- Limitations of the model in capturing certain patterns or external factors.\n"

        # **THEREFORE**: Offering actionable recommendations
        therefore_part = "\nTherefore, based on our findings, we recommend the following actions:\n\n"
        therefore_part += ("- **Focus on high-impact features**: Prioritize features such as "
                           f"{', '.join(top_contributions['Feature Name'].unique())} that have the most significant contributions.\n")
        therefore_part += ("- **Investigate low or negative contributions**: Examine features like "
                           f"{', '.join(low_contributions['Feature Name'].unique())} in specific samples to identify potential issues or areas for improvement.\n")
        therefore_part += "- **Enhance data quality and feature richness**: Incorporate additional contextual features, such as demographic or time-based data, to improve the model's accuracy and robustness.\n"
        therefore_part += "- **Regularly monitor and refine the model**: Ensure that the model adapts to new data and conditions to maintain its predictive effectiveness.\n"

    logger.info("Completed generating ABT story")
    return and_part, but_part, therefore_part


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

    # Compute absolute contributions
    abs_feature_contributions = np.abs(feature_contributions)

    # Flatten the matrix and get the top-k indices
    flat_contributions = abs_feature_contributions.flatten()
    top_k_indices = flat_contributions.argsort()[-k:][::-1]

    # Convert flat indices to matrix indices
    sample_indices, feature_indices = np.unravel_index(top_k_indices, feature_contributions.shape)

    # Create a DataFrame with top-k contributions
    top_k_contributions_df = pd.DataFrame({
        'Sample Number': sample_indices + 1,  # 1-based indexing for sample numbers
        'Feature Name': [feature_names[i] for i in feature_indices],
        'Contribution': feature_contributions[sample_indices, feature_indices]
    })

    logger.info("Completed selecting top %d feature contributions", k)
    return top_k_contributions_df


def plot_feature_contributions(contributions_df, title="Feature Contributions"):
    """
    Plot a bar chart for feature contributions.

    Args:
    - contributions_df: pd.DataFrame, DataFrame containing feature contributions.
    - title: str, Title of the plot.
    """
    logger.info("Generating bar chart for feature contributions")
    plt.figure(figsize=(8, 6))
    contributions_df.sort_values(by="Contribution", ascending=False, inplace=True)
    plt.barh(contributions_df["Feature Name"], contributions_df["Contribution"], color='blue')
    plt.xlabel("Contribution Value")
    plt.title(title)
    plt.tight_layout()
    plt.show()

# # Example usage
# if __name__ == "__main__":
#     # Simulated example data
#     feature_contributions = np.array([[0.8, -0.2, 0.1], [0.6, -0.3, 0.05], [0.7, -0.1, -0.4]])
#     feature_names = ['TV', 'Radio', 'Newspaper']
#     X_index = [0, 1, 2]  # Sample indices
#
#     # Select top contributions
#     top_k_contributions_df = select_top_k_feature_contributions(feature_contributions, feature_names, k=5)
#
#     # Generate ABT story
#     story = generate_abt_story(feature_contributions, X_index, feature_names, top_k_contributions_df,
#                                model_name="CustomModel")
#     print(story)
#
#     # Plot feature contributions
#     # plot_feature_contributions(top_k_contributions_df, title="Top Feature Contributions")
