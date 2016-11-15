import numpy as np


class BasicDistribution:
	def __init__(self, degree_resolution = 1):
		self.degree_resolution = degree_resolution
		self.cached_distribution = None


	def get_distribution(self, center = 0):
		if self.cached_distribution is None:
			self.cached_distribution = self.generate_base_distribution();

		return np.roll(self.cached_distribution, int(np.round(center)))


class Gaussian(BasicDistribution):
	def __init__(self, sigma = 100, amplitude = 1):
		super().__init__()
		self.sigma = sigma
		self.amplitude = amplitude
		self.cached_distribution = None


	def generate_base_distribution(self):
		
		arr = np.zeros(int(360 / self.degree_resolution))

		for degree in np.arange (-180, 540, self.degree_resolution):
			gaussian_value = self.amplitude * np.exp((-1 * ((degree) ** 2)) / (2 * (self.sigma ** 2)))

			if degree < 0:
				degree = degree + 360
			elif degree >= 360:
				degree = degree - 360
			if (arr[int(degree /  self.degree_resolution)] < gaussian_value):
				arr[int(degree /  self.degree_resolution)] = gaussian_value

		return arr;


class Rectangular(BasicDistribution):
	def __init__(self, width=40):
		self.width = width
		self.cached_distribution = None

	def generate_base_distribution(self):
		width = self.width;
		arr = np.zeros(360 / self.degree_resolution)
		halfwidth = int(width / 2)
		arr[:halfwidth] = 1
		arr[-halfwidth:] = 1
		return arr

