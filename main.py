import sys
import logging
#import codecs
from os import getenv, path, makedirs
import json
from time import time
import openai

#from collections import OrderedDict
from dotenv import load_dotenv
import chardet



model="gpt-3.5-turbo" # "gpt-4", #"gpt-3.5-turbo",
max_depth = 2
max_gpt4_depth = 0
time_prefix = time()
query = "Как сделать что бы лодка , сделанная самостоятельно, из дерева (немного плотничаю и слесарничаю)"
#"Как найти высокооплаиваемую работу в англии или канаде, если я сейчас работаю на себе в качестве репетитора по физике и математике, так же увлекаюсь программированием."
#"Разработай подробнейший план создания художественного произведения, которое будет вдохновлять людей. Я еще не писал книг. И не знаю как это делать."
#"Создай подробный план становления миллиардером. Сейчас я мужчина 40 лет, жена трое детей. Работаю на себя - репетитор по физике и математике. Остается после аренды не много. Но есть несколько вложений, которые стараюсь не трогать. Есть навыки программирования, столярного дела, работы в фотошопе, организации мероприятей с изначально горячей аудиторией, бегал марафон, ходил на тренинг по маркетингу (но ничего не получилось продать), пробовал продвигать себя сам - тоже без результата, написал бота, который ищет мне новых учеников. Нужен подробнейший план действий, чтобы стать миллиардером."
#"Как поднять свою самооценку маме 3-х детей."
#"Как реализоваться (и найти предназначение) мужчине 40 лет, который работает 20 лет репетиторо по физике и математике (но это не мое). У меня семья - жена, 3 маленьких детей, живем на съемной квартире."
#"Как разработать расписание для занятий Английским маме 3-х детей, один грудной. Денег на помощников нет, муж все время работает."
#"Как изучить Английский самостоятельно, с нуля для русской мамы троих детей без возможности покупать курсы и онлайн курсы."
temperature=0.9

# Настройка базового конфига логгера
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

# Функция для логирования необработанных исключений
def log_exception(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception",
                  exc_info=(exc_type, exc_value, exc_traceback))

# Заменяем стандартный excepthook на нашу функцию
sys.excepthook = log_exception

load_dotenv()
all_steps = []
openai.api_key = getenv("gpt_api")

def save_to_file(data, filename='results.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

#функция с несколькими аргументами
def task_brakedown(main_query, ancestors_of_queries, depth, steps_list):
    # Ваш код здесь
    for i, step in enumerate(steps_list):  # Добавьте enumerate()
        print(step["step"])
        if "need_futher_breakdown" in step and step["need_futher_breakdown"] and depth <= max_depth:
            steps_list[i]["SubSteps"] = Breakdown(f"{step['step']} (this is a step in brakedown of this task: ///{main_query}///. Do not include steps from this list ///{all_steps}///) This step is the brakedown of this previous steps: //{ancestors_of_queries}//", ancestors_of_queries=f"{ancestors_of_queries} -> {step['step']}", depth=depth, main_query=main_query, model=model if depth <= max_gpt4_depth else "gpt-3.5-turbo", temperature=temperature)
        else:
            steps_list[i]["SubSteps"] = {}
    return steps_list


def decode_string(encoded_str):
    # Проверка типа входных данных
    if isinstance(encoded_str, str):
        try:
            encoded_str = bytes(encoded_str, 'utf-8')
        except Exception as e:
            return str(e) #, None
    
    detected_info = chardet.detect(encoded_str)
    encoding_type = detected_info['encoding']
    confidence = detected_info['confidence']

    if confidence > 0.9:
        try:
            decoded_str = encoded_str.decode(encoding_type)
            return decoded_str #, encoding_type
        except Exception as e:
            return str(e) #, encoding_type
    else:
        return "Cannot confidently decode string" #, None

def Breakdown(query, main_query, ancestors_of_queries, model = "gpt-3.5-turbo", depth=0, temperature=0.9):
    global time_prefix
    global all_steps
    # Шаг 1: Определить функции, которые модель может вызвать

    functions = [
        {
        "name": "task_brakedown",
        "description": "Detailed steps by step brakedown of the task. Write each step so that it can be fully understood by a person who is not familiar with the task or other steps. No long answers, there will be futher breakdowns on subtasks. Write in russian.",
        "parameters": {
            "type": "object",
            "properties": {
            "steps": {
                "type": "array",
                "items": {
                "type": "object",
                "properties": {
                    "step": {
                    "type": "string",
                    "description": "step description"
                    },
                    "need_futher_breakdown": {
                    "type": "boolean",
                    "description": "if True - this subtask need futher breakdown to subtasks."
                    }
                },
                "required": ["step", "need_futher_breakdown"]
                }
            }
            },
            "required": ["steps"]
        }
    },
    ]
    
    
    # Шаг 2: Сформировать запрос к модели
    messages = [{"role": "user", "content": query}]
    if not path.exists( 'middle_results'):
        makedirs(       'middle_results')
    if not path.exists(f'middle_results/{main_query[:15]}_{time_prefix}_{model}'):
        makedirs(      f'middle_results/{main_query[:15]}_{time_prefix}_{model}')
    if not path.exists(f'middle_results/{main_query[:15]}_{time_prefix}_{model}/{str(depth)}/'):
        makedirs(      f'middle_results/{main_query[:15]}_{time_prefix}_{model}/{str(depth)}/')
    
    # Шаг 3: Вызвать модель
    try:
        response = openai.ChatCompletion.create(
            model=model, # "gpt-4", #"gpt-3.5-turbo",
            messages=messages,
            functions=functions,
            function_call={"name": "task_brakedown"},
            temperature=temperature
        )
    except Exception as e:
        print(f"Exception: {e}")
        save_to_file(f"Error: {e}", f'middle_results/{main_query[:15]}_{time_prefix}_{model}/{str(depth)}/{main_query[:15]}_{str(depth)}_{query[:15]}_{time()}.json')
    
        return {}
    # Шаг 4: Обработать ответ
    #print(f" response: {response}")
    response_content = response["choices"][0]["message"]
    #print(f" response_content: {response_content}")
    function_call_args = response_content.get("function_call", {}).get("arguments", None)
    #print(f" function_call_args: {function_call_args}")
    if function_call_args is not None:

        try:
            steps = json.loads(function_call_args)
            steps = steps["steps"]
        except json.JSONDecodeError:
            steps = {}

    else:
        steps = {}

    steps = [step for step in steps if step["step"] not in all_steps]



    steps_list = [step_data["step"] for step_data in steps if "step" in step_data]

    save_to_file(steps_list, f'middle_results/{main_query[:15]}_{time_prefix}_{model}/{str(depth)}/{main_query[:15]}_{str(depth)}_{query[:15]}_{time()}.json')
    all_steps.extend(steps_list)
    print(f" steps: {steps}")
    if steps and len(steps) > 1:
        kwargs = task_brakedown(main_query=main_query, ancestors_of_queries=ancestors_of_queries, depth = depth + 1, steps_list=steps)
        return kwargs
    return {}
    
def print_steps(json_data, indent=0, prefix='', file=None):
    if isinstance(json_data, list):  # Если json_data является списком
        for i, step_dict in enumerate(json_data):
            print_step_data(step_dict, indent, prefix, file)
    elif isinstance(json_data, dict):  # Если json_data является словарем
        print_step_data(json_data, indent, prefix, file)
    else:
        print("Неизвестный тип данных:", type(json_data))


def print_step_data(step_dict, indent, prefix, file):
    step = step_dict.get("step", "Неизвестный шаг")
    need_further_breakdown = step_dict.get("need_futher_breakdown", False)
    sub_steps = step_dict.get("SubSteps", {})
    
    print(f"{prefix}{step}", file=file)
    
    if need_further_breakdown and sub_steps:
        next_prefix = prefix + '    '
        print_steps(sub_steps, indent + 4, next_prefix, file)


# Пример использования
#query = "Как изучить Английский самостоятельно, с нуля для русской мамы троих детей без возможности покупать курсы и онлайн курсы."
#"Как переехать в Англию по рабочей визе, если пока нет работы. Работаю репетитором по физике и математике. Увлекаюсь программированием на питоне."
#"Как россиянину получить визу в Канаду, если у него нет официальной работы, живет он с семьей в Армении и у него есть ВНЖ на 5 лет?"#"Что нужно росиянину с ВНЖ Армении, и находящемуся там же, полуить визу в Канаду?"
result = Breakdown(query, query, query, model = model, temperature=temperature)
#print_steps(result)
"""with open(f'result_{query[:100]}_{time()}.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=4, ensure_ascii=False)"""
print(json.dumps(result, indent=4, ensure_ascii=False))
if not path.exists('results'):
    makedirs('results')
with open(f'results/{query[:40]}_{model}_t{temperature}_{time()}.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)
with open(f"results/{query[:40]}_{model}_t{temperature}_{time()}.txt", "w", encoding="utf-8") as f:
    original_stdout = sys.stdout  # сохраняем оригинальный stdout
    sys.stdout = f  # редиректим stdout в файл
    print_steps(result)
    sys.stdout = original_stdout  # возвращаем stdout обратно
