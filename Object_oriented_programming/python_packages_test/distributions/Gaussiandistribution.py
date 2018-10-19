import math
import numpy as np
import matplotlib.pyplot as plt
from Generaldistribution import Distribution

class Gaussian(Distribution):
    """ Gaussian distribution class for calculating and 
    visualizing a Gaussian distribution.
    
    Args:
        mean (float) representing the mean value of the distribution
        stdev (float) representing the standard deviation of the distribution           
    
    Attributes:
        mean (float) representing the mean value of the distribution
        stdev (float) representing the standard deviation of the distribution
        data_list (list of floats) a list of floats extracted from the data file
            
    """
    def __init__(self, mu=0, sigma=1):
        #super(Gaussian,self).__init__()
        Distribution.__init__(self, mu , sigma) #no need to defaut again
        
        # self.mean = mu
        # self.stdev = sigma
        # self.data = []


    
    def calculate_mean(self):
    
        """Function to calculate the mean of the data set.
        
        Args: 
            None
        
        Returns: 
            float: mean of the data set
    
        """
                    
        avg = 1.0 * sum(self.data) / len(self.data)
        
        self.mean = avg
        
        return self.mean

                


    def calculate_stdev(self, sample=True):

        """Method to calculate the standard deviation of the data set.
        
        Args: 
            sample (bool): whether the data represents a sample or population
        
        Returns: 
            float: standard deviation of the data set
    
        """
            
        sum_ = 0
        for i in range(len(self.data)):

            sum_ += math.pow((self.data[i]-self.mean),2)
        
        if (sample==True):
            
            self.stdev = math.sqrt(sum_/(len(self.data)-1))
            
            return self.stdev
        
        if (sample==False):
            
            self.stdev = math.sqrt(sum_/(len(self.data)))
            
            return self.stdev            
                 
        

        
    def plot_histogram(self):
        """Method to output a histogram of the instance variable data using 
        matplotlib pyplot library.
        
        Args:
            None
            
        Returns:
            None
        """
        
        if(len(self.data)!= 0):
            bin_num=50 #len(self.data)
            data_generate = self.data
            Text = "Gaussian distribution from input data file"

            plt.figure(figsize=(12,6))
            plt.hist(data_generate, density = True) #,bins=bin_num
            plt.xlabel('input')
            plt.ylabel('Histogram')
            plt.title(str(Text))
            plt.show() 



        else:    # no input file done at this stage, create graphs based on mu and sigma

            min_range = -4.0 * self.stdev + self.mean
            max_range =  4.0 * self.stdev + self.mean
            

            bin_num = 50
            delta = (max_range - min_range)/bin_num

            #x_data1 = np.linspace(min_range, max_range, num=bin_num)   # this is uniform prob only enforcing pdf on top

            x_data2 = np.random.normal(self.mean, self.stdev, bin_num)  # this ensure random normal generation in x_data

            pdf_vec = np.vectorize(self.pdf)   # no lambda

            data_generate1 = pdf_vec(x_data2)  #x_data1

            
            print(x_data2)

            Text = "Gaussian distribution with mu = {} and sigma = {}".format(self.mean,self.stdev)

            plt.figure(figsize=(12,6))
            plt.hist(x_data2,  density=True) # if false actual count, for True density (divide bytotal numbers) bins=bin_num,
            plt.xlabel('input')
            plt.ylabel('Count')
            plt.title(str(Text)+' with normal xdata sampling')



            plt.figure(figsize=(12,6))
            #plt.plot(x_data2, data_generate1)
            plt.scatter(x_data2, data_generate1)
            plt.xlabel('input')
            plt.ylabel('Pdf, Histogram')
            plt.title(str(Text))
            plt.show()
       
              
        
    def pdf(self, x):
        """Probability density function calculator for the gaussian distribution.
        
        Args:
            x (float): point for calculating the probability density function
            
        
        Returns:
            float: probability density function output
        """
        
        return (1.0/(math.sqrt(2.0*math.pi*(self.stdev)**2.0)))*(math.exp(-math.pow((x-self.mean),2)/(2.0*self.stdev**2.0)))
        
        # TODO: Calculate the probability density function of the Gaussian distribution
        #       at the value x. You'll need to use self.stdev and self.mean to do the calculation
     
    
    

    def plot_histogram_pdf(self, n_spaces = 50):

        """Method to plot the normalized histogram of the data and a plot of the 
        probability density function along the same range
        
        Args:
            n_spaces (int): number of data points 
        
        Returns:
            list: x values for the pdf plot
            list: y values for the pdf plot
            
        """
        
        #TODO: Nothing to do for this method. Try it out and see how it works.
        
        mu = self.mean
        sigma = self.stdev



        min_range = min(self.data)
        max_range = max(self.data)
        
         # calculates the interval between x values
        interval = 1.0 * (max_range - min_range) / n_spaces

        x = []
        y = []
        
        # calculate the x values to visualize
        for i in range(n_spaces):
            tmp = min_range + interval*i
            x.append(tmp)
            y.append(self.pdf(tmp))

        # make the plots
        fig, axes = plt.subplots(2,sharex=True)
        fig.subplots_adjust(hspace=.5)
        axes[0].hist(self.data, density=True)  # if false actual count, for True density (divide bytotal numbers)
        axes[0].set_title('Normed Histogram of Data')
        axes[0].set_ylabel('Density')

        axes[1].plot(x, y)
        axes[1].set_title('Normal Distribution for \n Sample Mean and Sample Standard Deviation')
        axes[0].set_ylabel('Density')
        plt.show()

        return x, y


    def __add__(self, other):
        
        """Function to add together two Gaussian distributions
        
        Args:
            other (Gaussian): Gaussian instance
            
        Returns:
            Gaussian: Gaussian distribution
            
        """
        
        result = Gaussian()
        result.mean = self.mean + other.mean
        result.stdev = math.sqrt(self.stdev ** 2 + other.stdev ** 2)
        
        return result
        
        
    def __repr__(self):
    
        """Function to output the characteristics of the Gaussian instance
        
        Args:
            None
        
        Returns:
            string: characteristics of the Gaussian
        
        """
        
        return "mean {}, standard deviation {}".format(self.mean, self.stdev)        