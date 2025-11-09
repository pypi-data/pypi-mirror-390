import numpy as np

I = [1,0]
w = np.random.randn(3,2)

def sigmoid(x):
    return 1/(1+np.exp(-x))

def orFunc():
    A = np.array([
        # A1, A2, Bias
        [1,1, 1],
        [0,1, 1],
        [1,0, 1],
        [0,0, 1]
    ]) #4,3

    t = np.array([1,1,1,0]).reshape(4,1) # 4,1
    eta = 0.5  # learning rate
    
    # 3,1
    w = np.random.randn(3,1)
    for epoch in range(10000):
        # 4,1
        z = A.dot(w)
        y = sigmoid(z)
        #y = (z > 0).astype(int)
        
        e = y - t
        
        # The error over all samples.
        total_error = np.mean((y-t)**2)
        
        grad = A.T.dot(e * y * (1 - y))
        
        w -= eta * grad / A.shape[0]
    
        if epoch % 1000 == 0:
            mse = np.mean((t - y)**2)
            print(f"Epoche {epoch}: MSE = {mse:.4f}")

    
    print(np.round(y))
    
orFunc()