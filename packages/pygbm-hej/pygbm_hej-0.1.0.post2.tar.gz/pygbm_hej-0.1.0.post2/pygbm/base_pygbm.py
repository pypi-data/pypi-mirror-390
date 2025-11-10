class BaseGBM:
    def __init__(self,y0, mu, sigma):
        """
        Initialize a base geometric Brownian motion (GBM) model.
        
        Parameters:
        - y0 (float): initial value at t = 0
        - mu (float): drift
        - sigma(float): diffusion coefficient
        """
        self.y0 = y0
        self.mu = mu
        self.sigma = sigma
