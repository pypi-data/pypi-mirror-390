#Using advanced optimisation techniques, such as evolutionary algorithms 
import numpy as np 
from sklearn.datasets import load_iris 
from sklearn.model_selection import train_test_split 
from sklearn.svm import SVC 
from sklearn.metrics import accuracy_score 
import pygad 
 
data = load_iris() 
X, y = data.data, data.target 
xtrain, xtest, ytrain, ytest = train_test_split(X, y, test_size=0.2, random_state=42) 
 
def fitness_func(ga_instance, solution, solution_idx): 
    C = solution[0] 
    gamma = solution[1] 
    kernel = ["linear", "poly", "rbf", "sigmoid"][int(solution[2])] 
    model = SVC(C=C, gamma=gamma, kernel=kernel) 
    model.fit(xtrain, ytrain) 
    predictions = model.predict(xtest) 
    accuracy = accuracy_score(ytest, predictions) 
    return accuracy 
 
ga_instance = pygad.GA( 
    num_generations=50, 
    num_parents_mating=5, 
    fitness_func=fitness_func, 
    sol_per_pop=10, 
    num_genes=3, 
    gene_space=[ 
        {'low': 0.1, 'high': 10.0}, 
        {'low': 0.0001, 'high': 1.0}, 
        {'low': 0, 'high': 3, 'step': 1}, 
    ], 
    parent_selection_type="rank", 
    keep_parents=2, 
    crossover_type="single_point", 
    mutation_type="random", 
    mutation_percent_genes=10 
) 
ga_instance.run() 
solution, solution_fitness, solution_idx = ga_instance.best_solution() 
8.07711465 0.42018293     
C_best, gamma_best, kernel_idx = solution 
kernel_best = ["linear", "poly", "rbf", "sigmoid"][int(kernel_idx)]
best_model = SVC(C=C_best, gamma=gamma_best, kernel=kernel_best, random_state=42) 
best_model.fit(xtrain, ytrain) 
final_accuracy = accuracy_score(ytest, best_model.predict(xtest)) 
print(f"Best Parameters → C: {C_best:.4f}, Gamma: {gamma_best:.4f}, Kernel: 
{kernel_best}") 
print(f"Final Accuracy → {final_accuracy:.4f}") 
