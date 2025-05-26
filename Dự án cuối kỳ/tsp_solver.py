import random
import math
import statistics
import numpy as np


class TSPSolver:
    def __init__(self):
        # Tên, tọa độ các campus
        self.campuses = [
    (5, 5, "A"),      
    (4, 7, "B"),      
    (6, 4, "C"),      
    (3, 8, "D"),      
    (8, 2, "E"),      
    (10, 1, "F"),     
    (9, 3, "G"),      
    (2, 6, "H"),      
    (7, 6, "I"),      
    (6, 8, "J"),          
    ]



        self.num_campuses = len(self.campuses)
        self.distance_matrix = self.calculate_distance_matrix()
        self.best_route = None
        self.best_distance = float("inf")
        self.history = []
        self.iteration = 0
        self.best_iteration = 0
        self.max_iteration = 1000

    def calculate_distance_matrix(self):
        matrix = []
        for i in range(self.num_campuses):
            row = []
            for j in range(self.num_campuses):
                if i == j:
                    row.append(0)
                else:
                    row.append(self.euclidean_distance(self.campuses[i], self.campuses[j]))
            matrix.append(row)
        return matrix

    def euclidean_distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def total_distance(self, route):
        dist = 0
        for i in range(len(route)):
            dist += self.distance_matrix[route[i]][route[(i + 1) % len(route)]]
        return dist

    def get_neighbors(self, route):
        neighbors = []
        for i in range(1, len(route)):
            for j in range(i + 1, len(route)):
                neighbor = route[:]
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                neighbors.append(neighbor)
        return neighbors

    def hill_climbing(self, initial_route):
        current_route = initial_route
        current_distance = self.total_distance(current_route)
        iteration =0 
        while True:
            neighbors = self.get_neighbors(current_route)
            next_route = min(neighbors, key=self.total_distance)
            next_distance = self.total_distance(next_route)

            if next_distance < current_distance:
                current_route = next_route
                current_distance = next_distance
                iteration +=1
            else:
                break
        return current_route, current_distance, iteration

    def random_restart(self, max_restarts=100):
        self.best_distance = float("inf")
        self.best_route = None
        self.history.clear()

        for _ in range(max_restarts):
            initial_route = list(range(self.num_campuses))
            random.shuffle(initial_route)
            route, distance, iterations = self.hill_climbing(initial_route)
            self.history.append((route, distance,iterations))

            if distance < self.best_distance:
                self.best_distance = distance
                self.best_route = route

    def get_statistics(self):
        lengths = [d for _, d in self.history]
        mean = statistics.mean(lengths)
        std = statistics.stdev(lengths) if len(lengths) > 1 else 0.0
        global_best = self.best_distance
        return global_best, mean, std


    

