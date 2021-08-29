# K-means Clustering

k-means clustering is a method of vector quantization, originally from signal processing, that aims to partition n observations into k clusters in which each observation belongs to the cluster with the nearest mean, serving as a prototype of the cluster.
 The repo contains following code
- kmeans.ipynb: Implementation within time limit
- kmeans.py: Class based implementation

## Class Based K-means Documentation

- n_clusters: The number of clusters to form as well as the number of centroids to generate.
- max_iter: Number of time the k-means algorithm will be run with different centroid seeds. The final results will be the best output of max_iter consecutive runs.


## How to Run
Demo is shown at the bottom of kmeans.ipynb file
```sh
from kmeans import kmeans

# creating object
kmeans_test = kmeans(n_clusters = 3)

# get corresponding centroids
kmeans_test.centroids()

# plot the cluster
kmeans_test.plot_cluster()

# optimal number of clusters using elbow method
kmeans_test.elbow_method([1,2,3,4,5])
```

## References
1. https://heartbeat.fritz.ai/understanding-the-mathematics-behind-k-means-clustering-40e1d55e2f4c

