import argparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert

# Add file path for scraped questions/anwers here
file_path = '' 

# Add quiz links here
quiz_links = []

parser = argparse.ArgumentParser()
optional = parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
required.add_argument('--n', help='number of times to scrape quiz data', required=True)
required.add_argument('--username', help='uni id, eg: a11111111', required=True)
required.add_argument('--password', help="uni password, eg: 'pa$$word'", required=True)
args = parser.parse_args()
    
def scrape_quiz_data(link) -> dict[str, list[str]]:
    browser = webdriver.Chrome()
    browser.get(link)
    wait = WebDriverWait(browser, 10)

    form = browser.find_element(by=By.ID,value='login_form')
    form.find_element(by=By.ID, value='pseudonym_session_unique_id').send_keys(args.username)
    form.find_element(by=By.ID, value='pseudonym_session_password').send_keys(args.password)
    form.find_element(by=By.CLASS_NAME, value='Button--login').click()

    take_quiz_button = wait.until(EC.element_to_be_clickable((By.ID, 'take_quiz_link')))
    take_quiz_button.click()

    submit_button = wait.until(EC.element_to_be_clickable((By.ID, 'submit_quiz_button')))
    submit_button.click()

    wait.until(EC.alert_is_present())
    alert = Alert(browser)
    alert.accept()

    time.sleep(3)

    question_element_container = wait.until(EC.presence_of_all_elements_located((By.ID, 'questions')))
    question_elements = question_element_container[0].find_elements(by=By.CLASS_NAME, value='display_question')

    question_texts = [question_element.find_element(by=By.CLASS_NAME, value='text') for question_element in question_elements]
    
    question_names = [question_text.find_element(by=By.TAG_NAME, value='p') for question_text in question_texts]
    question_answers = [question_text.find_element(by=By.CLASS_NAME, value='answers') for question_text in question_texts]
    correct_question_answers = [question_answer.find_elements(by=By.CLASS_NAME, value='correct_answer') for question_answer in question_answers]
    
    questions_dict = {}
    for question_name, correct_answer in zip(question_names, correct_question_answers):
        correct_answer_texts = []
        for answer in correct_answer:
            correct_answer_texts.append(answer.text.replace('Correct Answer\n', '').strip())
        questions_dict[question_name.text] = correct_answer_texts
        
    browser.close()
    return questions_dict

def main():
    all_quiz_questions = {}
    for _ in range(int(args.n)):
        for link in quiz_links:
            all_quiz_questions.update(scrape_quiz_data(link))
    with open(file_path, 'w') as f:
        for question, answers in all_quiz_questions.items():
            f.write(question + ':\n')
            for answer in answers:
                f.write('\t' + '- ' + answer + '\n')
            f.write('\n')
        f.write('\n\n\n')
            
if __name__ == '__main__':
    main()
