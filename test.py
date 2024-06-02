import  numpy as np
import  pickle

with open(f"assets/connect 4/solution_4x5.pkl", "rb") as f:
    sigma = pickle.load(f)

print(sigma["00000-00000-00220-01110"])