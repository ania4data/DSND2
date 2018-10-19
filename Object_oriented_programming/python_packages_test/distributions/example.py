from Gaussiandistribution import Gaussian

gaussian_one = Gaussian(20,3)
gaussian_two = Gaussian(10,4)

gaussian_three = gaussian_one + gaussian_two

print(gaussian_one.mean,gaussian_one.stdev)
print(gaussian_two.mean,gaussian_two.stdev)

print(gaussian_three.mean,gaussian_three.stdev)

print(gaussian_three)

#gaussian_three   need print command

gaussian_four = Gaussian()
gaussian_four.read_data_file('numbers.txt')
gaussian_four.calculate_mean()
gaussian_four.calculate_stdev()

gaussian_four.plot_histogram_pdf()


gaussian_four.plot_histogram()


gaussian_five = Gaussian(10, 5)
gaussian_five.plot_histogram()

print(gaussian_five)


gaussian_six = Gaussian()
gaussian_six.read_data_file('numbers2.txt')
gaussian_six.calculate_mean()
gaussian_six.calculate_stdev()
gaussian_six.plot_histogram_pdf()
gaussian_six.plot_histogram()