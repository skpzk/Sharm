import Sharm

if __name__ == "__main__":

	sharm = Sharm.Sharm()
	print("Init done.")

	try:
		while True:
			sharm.mainLoop()
	except KeyboardInterrupt:
		print("Main loop stopped.")

	sharm.close()
	print("Closed.")
