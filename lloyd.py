import random
import matplotlib.pyplot as plt
from dataclasses import dataclass

def euclidian_distance(p1: list, p2: list):
    dist = 0
    for i in range(len(p1)):
        dist += ((p1[i] - p2[i]) ** 2)
    return dist ** 0.5

def distance_for_bounding(p1: list, p_min:list, p_max: list):
    dist = 0
    for i in range(len(p1)):
        dist += (max(0, (p_min[i] - p1[i]), (p1[i] - p_max[i])) ** 2)
    return dist ** 0.5

def generate_random_dataset(items_count: int, dimensions: int, max_value):
    dataset = []
    for i in range(items_count):
        data = []
        for j in range(dimensions):
            data.append(random.randint(0, max_value))
        dataset.append(data)
    return dataset

def assign_points_to_clusters(dataset: list[list], centroids: dict):
    group = {}

    for k, v in centroids.items():
        group[k] = Cluster([])

    for i in range(len(dataset)):
        nearest_centroid = 0
        distance = euclidian_distance(dataset[i], centroids[nearest_centroid].center)
        for k, v in centroids.items():
            new_distance = euclidian_distance(dataset[i], v.center)
            if new_distance < distance:
                distance = new_distance
                nearest_centroid = k
        group[nearest_centroid].vectors.append(dataset[i])

    return group

def recalculate_centroids(centroids_group: dict, centroids: dict):
    new_centroids = {}
    for k, item in centroids_group.items():
        if len(item.vectors) == 0:
            new_centroids[k] = centroids[k]
            continue

        points = item.vectors
        centroid = []
        for i in range(len(points[0])):
            d_sum = 0
            for j in range(len(points)):
                d_sum += points[j][i]
            centroid.append(d_sum/len(points))
        new_centroids[k] = Centroid(centroid)
    return new_centroids

def create_kmeans_plus_plus_centroids(centroids_quantity: int, dataset: list[list]):
    centroids = {}

    # 1. Choose the first centroid randomly
    first_idx = random.randint(0, len(dataset) - 1)
    centroids[0] = Centroid(dataset[first_idx][:])

    # 2. The next centroids will be chosen by lucky using distances as weights
    for k in range(1, centroids_quantity):
        distances = []
        # Calculate the least distance between the points and the nearest centroid
        for point in dataset:
            min_dist = float('inf')
            for c_id in centroids:
                d = euclidian_distance(point, centroids[c_id].center)
                if d < min_dist:
                    min_dist = d
            # Storing the distance, but squaring the value to increase the chances of a far centroid be chosen
            distances.append(min_dist ** 2)

        # 3. Choose the next centroid
        total_distance = sum(distances)
        if total_distance == 0:  # Security for more centroids than points
            break

        probabilities = [d / total_distance for d in distances]

        # Choose index based on probabilities
        # random.choices return a list, and we get the 0 index
        chosen_idx = random.choices(range(len(dataset)), weights=probabilities, k=1)[0]

        centroids[k] = Centroid(dataset[chosen_idx][:])

    return centroids

def calculate_p_min_and_p_max(group: dict, centroids: dict):
    for k, cluster in group.items():
        p_min = []
        p_max = []
        for i in range(len(cluster.vectors[0])):
            i_min = None
            i_max = None
            for j in range(len(cluster.vectors)):
                if not i_min or cluster.vectors[j][i] < i_min:
                    i_min = cluster.vectors[j][i]
                if not i_max or cluster.vectors[j][i] > i_max:
                    i_max = cluster.vectors[j][i]
            p_min.append(i_min)
            p_max.append(i_max)
        centroids[k].p_max = p_max
        centroids[k].p_min = p_min
    return centroids

def run_kmeans(dataset: list[list], centroids_quantity: int, size_to_search_centroids: int, max_iterations = 30):
    centroids = create_kmeans_plus_plus_centroids(centroids_quantity, dataset[:size_to_search_centroids])

    iteration = 0
    while iteration <= max_iterations:
        group = assign_points_to_clusters(dataset, centroids)
        new_centroids = recalculate_centroids(group, centroids)
        total_distance_changes = sum(
            euclidian_distance(centroids[i].center, new_centroids[i].center)
            for i in range(len(centroids))
        )
        print(str(iteration) + ": " + str(total_distance_changes))
        if total_distance_changes < 250 or iteration == max_iterations:
            centroids = calculate_p_min_and_p_max(group, centroids)
            return group, centroids
        centroids = new_centroids

        iteration += 1

    return None

def try_insert_on_neighbor(nearest_vectors: list, vector_searched: list, vector_source: list):
    if len(nearest_vectors) < 5:
        nearest_vectors.append(Neighbor(euclidian_distance(vector_source, vector_searched), vector_source))
    else:
        new_neighbor = Neighbor(euclidian_distance(vector_source, vector_searched), vector_source)
        if new_neighbor.distance < nearest_vectors[4].distance:
            nearest_vectors.append(new_neighbor)

    nearest_vectors.sort()
    return nearest_vectors[:5]

def centroid_by_bounding_box(vector_searched: list, centroids: dict):

    centroids_by_bounding_distance = []

    for k,v in centroids.items():
        distance = distance_for_bounding(vector_searched, v.p_min, v.p_max)
        centroids_by_bounding_distance.append([distance, k])

    centroids_by_bounding_distance.sort()

    print(centroids_by_bounding_distance)

    return  centroids_by_bounding_distance

def search_nearest(vector_searched: list, centroids: dict, group: dict, max_centroids_visited = 10):
    if len(vector_searched) == 0 or len(vector_searched) != len(centroids[0].center):
        print("O vetor precisa ter a mesma dimensão que os dados de treinamento.")

    centroid_keys = centroid_by_bounding_box(vector_searched, centroids)

    nearest_vectors = []

    c_index = 0

    while True:
        print(nearest_vectors)
        for vector_source in group[centroid_keys[c_index][1]].vectors:
            nearest_vectors = try_insert_on_neighbor(nearest_vectors, vector_searched, vector_source)
        if (len(nearest_vectors) > 5 and nearest_vectors[-1].distance < centroid_keys[c_index + 1][0]) or c_index > (max_centroids_visited - 1):
            break
        else:
            c_index += 1

    print(nearest_vectors)
    return nearest_vectors

@dataclass(order=True)
class Neighbor:
    distance: float
    vector: list

@dataclass(order=True)
class Cluster:
    vectors: list[list]

@dataclass
class Centroid:
    center: list
    p_min: list = None
    p_max: list = None

def plot_clusters(clusters_dict, point: list):
    # Cria uma nova figura para desenhar
    plt.figure(figsize=(10, 8))

    # Vamos iterar sobre o seu dicionário de clusters
    for cluster_id, clusters in clusters_dict.items():
        if not clusters:  # Ignora se o cluster estiver vazio
            continue

        # O matplotlib precisa de uma lista de todos os X e uma de todos os Y
        # A função zip(*points) faz exatamente isso de forma elegante
        x_coords, y_coords = zip(*clusters.vectors)

        # Plota os pontos no gráfico (scatter = gráfico de dispersão)
        # O 'label' serve para criar a legenda depois
        plt.scatter(x_coords, y_coords,s=10 ,label=f'Cluster {cluster_id}')

    plt.plot([point[0]], [point[1]], 's')

    # Configurações visuais do gráfico
    plt.title('Visualização do K-Means')
    plt.xlabel('Eixo X')
    plt.ylabel('Eixo Y')

    # Abre a janela interativa com o gráfico
    plt.show()