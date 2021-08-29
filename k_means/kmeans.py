import numpy as np
import matplotlib.pyplot as plt
import random
import math
import pandas as pd
import seaborn as sns

class kmeans:
    
    def __init__(self, n_clusters, max_iter=300):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
    
    def distance_tuples(self,x,y):
        """
        This function returns distance between two coordinates
        x,y: n dimentional Tuples
        """
        sum_sq = 0
        for i in range(len(x)):
            sum_sq += (x[i]-y[i])**2
        return math.sqrt(sum_sq)


    def find_closest(self, x, centroids):
        """
        This function returns index of the closest centroid 
        x: Tuple containing coordinates of a point
        centroids: List of tuples
        """
        for i in range(len(centroids)):
            if i == 0:
                min_dist = self.distance_tuples(x,centroids[i])
                cent = i
            else:
                dist = self.distance_tuples(x,centroids[i])
                if dist<min_dist:
                    cent = i
                    min_dist = dist
        return cent


    def find_center(self, data):
        """
        This function returns centroid for a list of data points
        data: list of tuples
        """
        x = [i[0] for i in data]
        y = [i[1] for i in data]
        return (x,y)


    def centroid_compare(self, centroids, new_centroids, limit=0.1):
        """
        This function checks the convergence of the centroid
        centroids: Old Centroid
        new_centroids: New centroid
        """
        for i in range(len(centroids)):
            dis = self.distance_tuples(centroids[i], new_centroids[i])
            if dis==dis:
                dis = self.distance_tuples(centroids[i], new_centroids[i])
                if dis>limit:
                    return 0
        return 1
    
    def fit(self, data, k=None, ret=False):
        """
        seperates data into different clusters
        data: list of tuples
        plot: True if you want to see the plot 
        """
        if not k:
            k = self.n_clusters
        iterations = self.max_iter
        
        self.data = data
        
        if len(data[0])>2:
            return "Dimensions of data set should not be more that 2"
        
        # Convert datapoints into a dataframe
        df = pd.DataFrame(data, columns =['x', 'y'])
        
        
        print(f"{k} means clustering")
        

        df['cluster_final'] = None
        for ite in range(iterations):

            # Get a sample of random centroids from data
            centroids = random.sample(data, k=k)

            while(True):
                # create clusters based on centroids
                df['new_cluster'] = df.apply(lambda row: self.find_closest((row['x'], row['y']), centroids), axis=1)

                # New centroids based on cluster
                new_centroids = []
                for i in range(len(centroids)):
                    x_mean = df[df['new_cluster']==i].x.mean()
                    y_mean = df[df['new_cluster']==i].y.mean()
                    new_centroids.append((x_mean, y_mean))
                df['new_dist'] = df.apply(lambda row: self.distance_tuples((row['x'], row['y']),
                                                                      centroids[int(row['new_cluster'])]), axis=1)
                if self.centroid_compare(centroids, new_centroids):
                    centroids = new_centroids
                    df['cluster'] = df['new_cluster']
                    df['dist'] = df['new_dist']
                    break  
                centroids = new_centroids
                df['cluster'] = df['new_cluster']
                df['dist'] = df['new_dist']

            dis_sum = df.groupby(['cluster']).sum()["dist"].mean()
            if ite==0:
                dis_sum_final = dis_sum
                df['cluster_final'] = df['cluster']
                df['dist_final'] = df['dist']
            elif dis_sum_final>dis_sum:
                dis_sum_final = dis_sum
                df['cluster_final'] = df['cluster']
                df['dist_final'] = df['dist']
                
        if ret == True:
            return df
        else:
            self.df = df
                
    def plot_cluster(self):
        
        if len(self.data[0])==2:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.scatterplot(data=self.df, x="x", y="y", hue="cluster_final", s=50, palette = "pastel", alpha=1)
            plt.title(f'{self.n_clusters}-means culstering',fontsize=15)
            plt.xlabel('x-coordinate',fontsize=15)
            plt.ylabel('y-coordinate',fontsize=15)
            plt.show()
        else:
            print("Dimensions of data set should not be more that 2")
            
    def elbow_method(self, k_values):
        """
        Get elbow plot for different values of k
        """
        print("Elbow method")
        sum_val = []
        for k in k_values:
            df = self.fit(self.data, k=k, ret=True)
            sum_val.append(df.groupby(['cluster_final']).sum()["dist_final"].mean())
        fig, ax = plt.subplots(figsize=(10, 4))
        plt.plot(k_values, sum_val, 'bx-')
        plt.xlabel('Values of K',fontsize=15)
        plt.ylabel('Distortion',fontsize=15)
        plt.title('The Elbow Method',fontsize=15)
        plt.show()
    
    def centroids(self):
        """
        Get centroids after training dataset
        """
        try:
            return self.df.groupby('cluster_final').mean()[["x", "y"]].values.tolist()
        except:
            print("Run clustering for a value of K")
            