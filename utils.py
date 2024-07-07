import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler

from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from hdbscan import HDBSCAN
from sklearn.metrics import silhouette_score


def visualize_clusters(algorithm, data, **kwargs):
    if algorithm == 'hdbscan':
        clusterer = HDBSCAN(**kwargs)
    elif algorithm == 'gmm':
        clusterer = GaussianMixture(**kwargs)
    elif algorithm == 'kmeans':
        clusterer = KMeans(**kwargs)
    else:
        raise ValueError("Invalid clustering algorithm. Choose from 'hdbscan', 'gmm', or 'kmeans'.")

    labels = clusterer.fit_predict(data)

    plt.figure(figsize=(8, 8))
    scatter = plt.scatter(data[:, 0], data[:, 1], c=labels, cmap='viridis', s=10) 
    plt.xlabel('UMAP Component 1')
    plt.ylabel('UMAP Component 2')
    plt.title(f'{algorithm.capitalize()} Clustering')
    plt.colorbar(scatter, label='Cluster')
    plt.show()



def preprocess_data(data, features, target='Store'):
    """Preprocess data by grouping and aggregating features."""
    return data.groupby(target).agg(features).reset_index()

def standardize_features(data, target='Store'):
    """Standardize features excluding the target variable."""
    scaler = StandardScaler()
    return scaler.fit_transform(data.drop(columns=[target]))

def perform_clustering(X_scaled, algorithm='gmm', n_components=4, **kwargs):
    """Perform clustering on the preprocessed data."""
    if algorithm == 'gmm':
        clusterer = GaussianMixture(n_components=n_components, random_state=42, **kwargs)
    elif algorithm == 'kmeans':
        clusterer = KMeans(n_clusters=n_components, random_state=42, **kwargs)
    
    return clusterer.fit_predict(X_scaled)

def visualize(data, cluster_labels, features, target='Store', colors='viridis', style='fivethirtyeight', figsize=(12, 6), title=None):
    """Visualize clustering results."""
    plt.style.use(style)
    plt.figure(figsize=figsize)

    sns.boxplot(x=cluster_labels, y='Weekly_Sales', data=data, palette=colors)
    plt.title(title or f'Distribution of Weekly Sales by Cluster ({target.capitalize()})')
    plt.xlabel('Cluster')
    plt.ylabel('Weekly Sales')
    plt.show()

    cluster_summary = data.drop(target, axis=1).groupby('Cluster').mean().reset_index()
    visualize_cluster_summary(cluster_summary, features, colors)

def visualize_cluster_summary(cluster_summary, features, colors='viridis'):
    """Visualize cluster summary."""
    plt.figure(figsize=(15, 7))
    for i, feature, in enumerate(features.keys(), 1):
        plt.subplot(2, 3, i)
        sns.barplot(x='Cluster', y=feature, data=cluster_summary, hue='Cluster', palette=colors)
        plt.ylabel(feature)
        plt.xlabel('Cluster')
    plt.tight_layout()
    plt.show()

def compute_cluster_details(data, cluster_labels, target='Store'):
    """Compute cluster details."""
    cluster_details = {}
    for i in range(cluster_labels.max() + 1):
        cluster_data = data[cluster_labels == i]
        cluster_details[f'Cluster {i}'] = {
            f'{target.capitalize()}s': cluster_data[target].unique(),
            f'No. of {target}s': len(cluster_data)
        }
    cluster_details['Total'] = data[target].nunique()
    return cluster_details

def cluster_and_visualize(data, features, target='Store', algorithm='gmm', n_components=4, visualize_flag=True, 
                          colors='viridis', style='fivethirtyeight', figsize=(12, 6), title=None, **kwargs):
    """
    Perform clustering on the dataset and visualize the results.

    Parameters:
    data (DataFrame): The input dataset.
    features (dict): Dictionary specifying features to be aggregated.
    target (str): Name of the target variable (store or department).
    algorithm (str): Clustering algorithm to use ('gmm' or 'kmeans').
    n_components (int): Number of clusters.
    visualize (bool): Whether to visualize the results.
    colors (str or list): Color palette for visualizations.
    style (str): Matplotlib style.
    figsize (tuple): Figure size for visualizations.
    title (str): Title for the visualization.
    **kwargs: Additional keyword arguments for the clustering algorithm.

    Returns:
    dict: Details about the clusters.
    """
    if target not in data.columns:
        raise ValueError(f"Target '{target}' not found in the dataset columns.")
    if algorithm not in ['gmm', 'kmeans']:
        raise ValueError("Invalid clustering algorithm. Choose from 'gmm' or 'kmeans'.")

    df_clustering = preprocess_data(data, features, target)
    X_scaled = standardize_features(df_clustering, target)
    cluster_labels = perform_clustering(X_scaled, algorithm, n_components, **kwargs)
    df_clustering['Cluster'] = cluster_labels

    if visualize_flag:
        visualize(df_clustering, cluster_labels, features, target, colors, style, figsize, title)

    cluster_details = compute_cluster_details(df_clustering, cluster_labels, target)
    print(f"Cluster Details for {target.capitalize()}s:")
    return cluster_details



def plot_elbow_silhouette(data, groupby_col, features, clusters_range, method='elbow', figsize=(10, 6), random_state=42):
    df_clustering = data.groupby(groupby_col).agg(features).reset_index()
    metric_values = []

    if method == 'elbow':
        # Elbow Method
        for k in clusters_range:
            metric_values.append(KMeans(n_clusters=k, n_init=10, random_state=random_state).fit(df_clustering).inertia_)

        ylabel, title = 'Sum of Squared Distances', 'Elbow Method For Optimal k'

    if method == 'silhouette':
        # Silhouette Score
        for k in clusters_range:
            metric_values.append(silhouette_score(df_clustering, KMeans(n_clusters=k, random_state=random_state, n_init=10).fit_predict(df_clustering)))
        
        ylabel, title = 'Score', 'Silhouette Score vs. Number of Clusters'
      
    plt.figure(figsize=figsize)
    plt.plot(clusters_range, metric_values, 'bx-')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.show()