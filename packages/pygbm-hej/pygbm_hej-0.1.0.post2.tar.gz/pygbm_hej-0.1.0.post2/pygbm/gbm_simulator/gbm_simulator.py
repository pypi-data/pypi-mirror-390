import numpy as np
import matplotlib.pyplot as plt
from ..base_pygbm import BaseGBM


class GBMSimulator(BaseGBM):
    def __init__(self,y0,mu,sigma):
        super().__init__(y0,mu,sigma)

    def simulate_path(self,T,N):
        """
        This is simlating GBM using the following solution of it:
        Y_(t+1) = Y_t * exp((mu-0.5*sigma**2)*dt + sigma * dB(t))

        Parameters:
        -T(float): final time, i.e. end of time interval
        -N(int): number of time steps, increments dividing time increment

        """
        #not sure what to do so copied Boris' code for this method
        dt = T / N
        t_values = np.linspace(0, T, N + 1) #time interval
        y_values = [self.y0] #initilisation with y value at time 0
        
        for _ in range(N):
            y_prev = y_values[-1]
            dB = np.random.normal(0, np.sqrt(dt)) #can refer to mf1 notes - this is one of the properties that Brownian motion needs to satisfy; 
                                                  #the others are: 1) B_0 = 0; 2)for t4>t3>=t2>t1, (W4-W3) and (W2-W1) are INDEPENDENT increments
            y_next = y_prev * np.exp((self.mu - 0.5 * self.sigma ** 2) * dt + self.sigma * dB)
            y_values.append(y_next)
        
        return t_values, y_values
    
    def plot_simulate_path(self,t_values, y_values,output = None): #originally i didn't have output parameter, added when saw Boris has this
        #this 'output' parameter is also needed becuase seeing the requirements from CLI, it is included as a parameter
        """
        This plots the simulated path over the specified time interval
        With this method, users could just call this function to get the graph

        Parameters:
        - t_values(float): time interval
        - y_values(float): Y(t) values over the time interval
        - output(str): optional path. If provided will save to this location; if omitted will display on screen
        """
        self.t_values = t_values
        self.y_values = y_values
        plt.plot(t_values, y_values, label="GBM Path")
        plt.xlabel("Time")
        plt.ylabel("Y(t)")
        plt.title("Simulated Geometric Brownian Motion Path")
        plt.legend()
        plt.show()

        #what is lacking previously and Boris has:
        if output:
            plt.savefig(output)
        else:
            plt.show()






