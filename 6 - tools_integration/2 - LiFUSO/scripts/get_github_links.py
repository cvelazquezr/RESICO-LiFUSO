import time
import requests
import pandas as pd
from random import randint


if __name__ == '__main__':
	libraries = [
		("com.google.guava", "guava"),
		("org.apache.httpcomponents", "httpclient"),
		("org.apache.pdfbox", "pdfbox"),
		("org.apache.poi", "poi-ooxml"),
		("org.jfree", "jfreechart"),
		("org.jsoup", "jsoup"),
		("org.quartz-scheduler", "quartz")
	]

	for library in libraries:
		print(f"Processing library {library[1]} ...")

		limit_reached = False
		page = 1

		while not limit_reached:
			print(f"Page {page} ...")

			# Information to save
			host_types = list()
			languages = list()
			stars = list()
			names = list()
			descriptions = list()

			url = f"https://libraries.io/api/Maven/{library[0]}:{library[1]}/dependent_repositories?api_key=4f736e4d03fa9492d9835b9429144705&page={page}&per_page=100"
			response = requests.get(url)

			if response.status_code == 200:
				data = response.json()

				if len(data):
					for element in data:
						host_types.append(element["host_type"])
						languages.append(element["language"])
						stars.append(element["stargazers_count"])
						names.append(element["full_name"])
						descriptions.append(element["description"])
				else:
					limit_reached = True

			time.sleep(1)

			# Saving information
			print("Saving information ...")
			data_dict = {"full_name": names, "host_type": host_types, "language": languages, "stars": stars, "description": descriptions}
			df = pd.DataFrame(data=data_dict)
			
			if page == 1:
				df.to_csv(f"github_clients/{library[0]}_{library[1]}.csv", index = False)
			else:
				df.to_csv(f"github_clients/{library[0]}_{library[1]}.csv", index = False, mode = "a", header = False)

			page += 1

		print("Done!")
