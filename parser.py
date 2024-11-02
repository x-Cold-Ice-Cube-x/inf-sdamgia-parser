from bs4 import BeautifulSoup
from requests import Session
from enum import Enum
from pydantic import BaseModel


class Types(Enum):
    INF = "https://inf-ege.sdamgia.ru/test"
    MATH = "https://math-ege.sdamgia.ru/test"


class Application(BaseModel):
    __session = Session()

    ege_type: str
    output: str = None

    def parse(self, test_id: str):
        answers, solved_post_payload = self.__parse_answers_url(self.__parse_test_url(url=f"{self.ege_type}?id={test_id}"))
        if self.output is None:
            print("\n".join(answers))
            return
        self.__saving(answers)

    def __parse_test_url(self, url: str) -> dict:
        post_payload = {"is_cr": 0, "stat_id": 0, "timer": 1, "a": "check"}
        test_soup = BeautifulSoup(self.__session.get(url=url).content, "lxml")

        # hash
        post_payload["hash"] = test_soup.find("input", {"name": "hash"}).get("value")

        # test_id
        post_payload["test_id"] = int(test_soup.find("div", class_="new_header").find("b").text.split()[2])

        cases_soup = test_soup.find("div", class_="prob_list").find_all("div", class_="prob_view")
        for case_soup in cases_soup:
            # cases_id
            post_payload[case_soup.find("input", class_="test_inp").get("name")] = ""
        return post_payload

    def __parse_answers_url(self, post_payload: dict) -> (list, dict):
        answers_soup = BeautifulSoup(self.__session.post(url=self.ege_type, data=post_payload).content, "lxml")
        answers_column_soup = answers_soup.find("table", class_="res_table").find_all("tr", class_="res_row")
        answers = [answer_soup.find_all("td")[-1].text for answer_soup in answers_column_soup]
        solved_post_payload = {**post_payload, **{key: answers[list(post_payload.keys()).index(key) - 6] for key in post_payload.keys() if "answer" in key}}
        return answers, solved_post_payload

    def __saving(self, answers: list):
        with open(self.output, "w") as file:
            file.write("\n".join(answers))


if __name__ == "__main__":
    inf = Application(ege_type=Types.INF, output="17.txt")
    inf.parse(input())
