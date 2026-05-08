import lloyd
import random

dimensions = 20

dataset = lloyd.generate_random_dataset(50000, dimensions, 1000)
group, centroids_idx = lloyd.run_kmeans(dataset, 100, 3000, 50)

p = []
for i in range (dimensions):
    p.append(random.randint(0, 1000))

lloyd.search_nearest(p, centroids_idx, group, 10)

#lloyd.plot_clusters(group, p)