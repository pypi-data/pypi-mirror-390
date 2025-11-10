import argparse
from .gbm_simulator.gbm_simulator import GBMSimulator #it is a file called gbm_simulator.py within the folder gbm.simulator

def main():
    parser = argparse.ArgumentParser(description="pygbm CLI Tool")
    parser.add_argument("--y0",type = float,required = True, help = "initial value of y(t), i.e. at t=0")
    parser.add_argument("--mu",type = float, required = True, help = "expected value of Y given t" )
    parser.add_argument("--sigma", type = float, required = True, help = "standard deviation of Y given t")
    parser.add_argument("--T", type = float, required = True, help = "end time")
    parser.add_argument("--N", type = int, required = True, help = "number of increments")
    parser.add_argument("--output", type = str, help = "Output file of plot")

    args = parser.parse_args()
    
    simulator = GBMSimulator(args.y0,args.mu,args.sigma)
    t_values, y_values = simulator.simulate_path(args.T, args.N)
    simulator.plot_simulate_path(t_values, y_values, output=args.output)



if __name__ == "__main__":
    main()



#can now test CLI in terminal with below:
 #pygbm --y0 1.0 --mu 0.05 --sigma 0.2 --T 1.0 --N 100 --output gbm_plot.png
