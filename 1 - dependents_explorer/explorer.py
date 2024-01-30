# This script is not used anymore in favour of the GitHub project https://github.com/github-tooling/ghtopdep

import requests
import time
from random import randint
from bs4 import BeautifulSoup
from sys import argv


if __name__ == '__main__':
    if len(argv) < 3:
        print("Too few arguments, 1st argument: Name of the library, 2nd argument: URL with the library's dependents.")
    elif len(argv) == 3:
        library = argv[1]
        url = argv[2]
        
        folder = "/mansion/cavelazq/PhD/joint_tools/data/repositories"
        name_file = "{}/{}.txt".format(folder, library)

        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        number_repositories = int(soup.find("a", {"class": "btn-link selected"}).text.strip().split("\n")[0].strip().replace(",", ""))

        print("Number of repositories:", number_repositories)
        number_pages = number_repositories // 30 + 1

        print("Number of pages:", number_pages)

        with open(name_file, "w") as f:
            for i in range(number_pages):
                time.sleep(randint(1, 3))
                print("Page:", i + 1, "/", number_pages)

                r = requests.get(url)
                soup = BeautifulSoup(r.content, "html.parser")

                data = [
                    "{}/{}".format(
                        t.find('a', {"data-repository-hovercards-enabled":""}).text,
                        t.find('a', {"data-hovercard-type":"repository"}).text
                    )
                    for t in soup.findAll("div", {"class": "Box-row"})
                ]

                for repository in data:
                    f.write(repository + "\n")

                pagination_container = soup.find("div", {"class":"paginate-container"}).findAll('a')

                if len(pagination_container) == 1:
                    url = pagination_container[0]["href"]
                elif len(pagination_container) == 2:
                    url = pagination_container[1]["href"]
                else:
                    break
