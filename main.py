from viewgradesAPI import ViewGrades
from viewgradesAPI.exceptions import ContentNotFoundError, CredentialsError
from getpass import getpass
from tabulate import tabulate
import sys


def showUserInfo(data: dict) -> None:
    print("")
    print(f"Roll no : {data['Roll No']}")
    print(f"Name    : {data['Name']}")
    print(f"CGPA    : {data['CGPA']}")
    print("")


def showSem(data: dict, n: int) -> None:
    semesters = data["Semesters"]
    try:
        sem = semesters[n - 1]
    except IndexError:
        print(f"[ ERROR ] : Semester {n} data not available")
        quit(1)
    else:
        print("")
        print(f"Semester : {n}")
        print(f" - GPA : {sem['GPA']}")
        print("")
        headers = ["Course", "Credits", "Grade", "Attendance"]
        table = [
            [
                course,
                sem["Courses"][course]["Credit"],
                sem["Courses"][course]["Grade"],
                sem["Courses"][course]["Attendance"]
            ] for course in sem["Courses"]
        ]

        print(tabulate(table, headers, tablefmt="grid"))
        
    """

def BalanceCredits(data: dict) -> None:
    eng_cred = int(data["Credit Summary"]["Engineering"])
    hum_cred = int(data["Credit Summary"]["Humanities"])
    pro_cred = int(data["Credit Summary"]["Professional"])
    sci_cred = int(data["Credit Summary"]["Science"])
    oth_cred = int(data["Credit Summary"]["Others"])
    
    eng_req = int(48)
    hum_req = int(27)
    pro_req = int(200)
    sci_req = int(86)
    oth_req = int(72)
  """
    
    


if __name__ == "__main__":

    if len(sys.argv) != 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("[ ERROR ] : Invalid argument, Semester number should be int")
            quit(1)
    else:
        n = 0

    ROLLNO = "na19b006"
    prompt = f"Password for {ROLLNO.upper()} : "
    pwd = getpass(prompt=prompt)

    remote = ViewGrades()

    try:
        remote.login(ROLLNO, pwd)
    except CredentialsError:
        print("\n[ ERROR ] : Invalid credentials\n")
        quit(1)
    except ConnectionError:
        print("\n[ ERROR ] : Could not connect to server\n")
        quit(1)

    try:
        data = remote.fetchInfo()
    except ContentNotFoundError:
        print("\n[ ERROR ] : Could not load data from view grades")
        quit(1)

    showUserInfo(data)
    if not n:
        for i in range(len(data["Semesters"])):
            showSem(data, i + 1)
    else:
        showSem(data, n)
