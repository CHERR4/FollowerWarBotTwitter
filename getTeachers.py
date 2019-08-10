from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import pickle

BEGINING_WEB = "https://www.uma.es/etsi-informatica/info/72378/grado-ing-del-software-guia-docente/"
SUBJECT_PATTERN = "https://www.uma.es/centers/subject/etsi-informatica/5103/"
TEACHER_PATTERN = "https://www.uma.es/departments/teachers/"

def containsPattern(url, pattern):
        result = re.search(pattern, url)
        return result is not None

def getSubjectsUma(driver):
        driver.get(BEGINING_WEB)
        assert "Universidad de Málaga" in driver.title
        elems = driver.find_elements_by_tag_name('a')
        subjects = []
        for link in elems:
                if(type(link.get_attribute("href")) != type(None)):
                        if(containsPattern(link.get_attribute("href"), SUBJECT_PATTERN)):
                                print ("URL: " + link.get_attribute("href"))
                                subjects.append(link.get_attribute("href"))
        return set(subjects)

def getTeachersLinksUma(driver, subjects):
        teachers = []
        for subject in subjects:
                driver.get(subject)
                elems = driver.find_elements_by_tag_name('a')
                for link in elems:
                        if(type(link.get_attribute("href")) != type(None)):
                                if(containsPattern(link.get_attribute("href"), TEACHER_PATTERN)):
                                        print ("URL: " + link.get_attribute("href"))
                                        teachers.append(link.get_attribute("href"))
        return set(teachers)

def getTeachersUma(driver, teachersLinks):
        teachers = []
        for teacherLink in teachersLinks:
                driver.get(teacherLink)
                elem = driver.find_element_by_tag_name("h1")
                print(elem.get_attribute("title"))
                teachers.append(elem.get_attribute("title"))
        return set(teachers)


def main():
        driver = webdriver.Chrome()
        subjects = getSubjectsUma(driver)
        teachersLinks = getTeachersLinksUma(driver, subjects)
        teachers = getTeachersUma(driver, teachersLinks)
        with open('teachers.txt', 'w') as fp:
                pickle.dump(teachers, fp)


if __name__== "__main__":
    main()




