import requests
from bs4 import BeautifulSoup
from .exceptions import ContentNotFoundError, CredentialsError


class URL:
    """ All URLs for sending requests """
    login = "https://www.iitm.ac.in/viewgrades/studentauth/login.php"
    index = "https://www.iitm.ac.in/viewgrades/index.html"
    grade = "https://www.iitm.ac.in/viewgrades/studentauth/btechdual.php"


class ViewGrades:
    def __init__(self) -> None:
        self.rawContent: bytes = None

        self.session = requests.Session()

    def login(self, username: str, password: str) -> None:
        """ Login to https://www.iitm.ac.in/viewgrades/index.html

        @params:
            username:
                type: str
                desc: LDAP username
            password:
                type: str
                desc: LDAP password

        @returns:
            None

        @raises:
            ConnectionError:
                error in connecting to server
            CredentialsError:
                invalid credentials
        """

        postData = {
            "rollno": username,
            "pwd": password,
            "submit": "Submit"
        }

        # try to login, will raise connection error
        loginResponse = self.session.post(url=URL.login, data=postData, verify=False)

        # check validity of credentials
        if not loginResponse.ok:
            raise ConnectionError

        # login page redirects to index page if credentials are wrong
        if loginResponse.url == URL.index:
            raise CredentialsError

        dataResponse = self.session.get(url=URL.grade, verify=False)

        if not dataResponse.ok:
            raise ConnectionError

        self.rawContent = dataResponse.content

    def fetchInfo(self) -> dict:
        """ Parse html from server and clean data 

        @params:
            None

        @returns:
            result:
                type: dict
                desc: cleaned data of user, in a json format

        @raises:
            ContentNotFoundError:
                raised when this method is called without logging in
        """

        if not self.rawContent:
            raise ContentNotFoundError

        result = dict()

        soup = BeautifulSoup(self.rawContent, "html.parser")

        rows = soup.find_all("tr")

        try:
            heading = rows[0].find_all("th")
        except IndexError:
            raise ContentNotFoundError

        result["Roll No"] = heading[0].text.strip().upper()
        result["Name"] = heading[2].text.strip()
        result["Programme"] = heading[4].text.strip()
        result["CGPA"] = ""
        result["Credit Summary"] = dict()

        # get earned credit summary
        summaryTable = soup.find_all("table", attrs={"border": "1"})[-1]
        cols = summaryTable.find_all("tr")[1].find_all("td")
        result["Credit Summary"]["Engineering"] = cols[7].text.strip()
        result["Credit Summary"]["Professional"] = cols[8].text.strip()
        result["Credit Summary"]["Science"] = cols[9].text.strip()
        result["Credit Summary"]["Humanities"] = cols[10].text.strip()
        result["Credit Summary"]["Others"] = cols[11].text.strip()

        # this table contains semester wise grade info
        masterTable = "".join(str(x) for x in rows[2:])

        result["Semesters"] = list()
        semData = masterTable.split("Semester")[1:]

        for sem in semData:
            semInfo = dict()
            semInfo["Courses"] = dict()
            soup = BeautifulSoup(sem, "html.parser")

            courseCount = 0
            rows = soup.find_all("tr")

            for row in rows:
                cols = row.find_all("td")
                if not cols[0].text.isnumeric():
                    break

                course = cols[1].text.strip()
                semInfo["Courses"][course] = dict()
                semInfo["Courses"][course]["Course Title"] = cols[2].text.strip()
                semInfo["Courses"][course]["Course Category"] = cols[3].text.strip()
                semInfo["Courses"][course]["Credit"] = cols[4].text.strip()
                semInfo["Courses"][course]["Grade"] = cols[5].text.strip()
                semInfo["Courses"][course]["Attendance"] = cols[6].text.strip()

                courseCount += 1

            cols = rows[courseCount].find_all("td")

            semInfo["Earned Credit"] = cols[0].text.strip().split(":")[1]

            gpaData = cols[1].text.strip().split(":")
            if gpaData[0] == "GPA":
                semInfo["GPA"] = gpaData[1]
            else:
                semInfo["GPA"] = "0"

            result["Semesters"].append(semInfo)

        self.__calculateCG(result)
        return result

    def __calculateCG(self, data: dict) -> None:
        """ Calculate CGPA """

        numerator = 0
        denominator = 0
        for sem in data["Semesters"]:
            numerator += int(sem["Earned Credit"]) * float(sem["GPA"])
            denominator += int(sem["Earned Credit"])

        data["CGPA"] = f"{numerator/denominator}"

    def __del__(self):
        self.session.close()
