#!/usr/bin/python3

class Shape:
	def __init__(self):
		pass; # Placeholder -- This is an abstract class

	def __str__(self):
		return self.__repr__();

	def __repr__(self):
		return "Shape";


