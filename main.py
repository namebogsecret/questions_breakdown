import sys
import logging
from os import getenv, path, makedirs
import json
from time import time
import argparse
from openai import OpenAI

from dotenv import load_dotenv
import chardet



model = "gpt-3.5-turbo"
max_depth = 1
max_gpt4_depth = 0
time_prefix = time()
query = "Как сделать лодку из дерева (немного плотничаю и слесарничаю)"
#"Разработай подробнейший план создания художественного произведения, которое будет вдохновлять людей. Я еще не писал книг. И не знаю как это делать."
#"Как разработать расписание для занятий Английским маме 3-х детей, один грудной. Денег на помощников нет, муж все время работает."
#"Как изучить Английский самостоятельно, с нуля для русской мамы троих детей без возможности покупать курсы и онлайн курсы."
temperature=0.9

# Настройка базового конфига логгера
logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.ERROR)

# Функция для логирования необработанных исключений
def log_exception(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception",
                  exc_info=(exc_type, exc_value, exc_traceback))

# Заменяем стандартный excepthook на нашу функцию
sys.excepthook = log_exception

load_dotenv()
# track all unique step descriptions to avoid duplicates
all_steps: set[str] = set()

# Validate and initialize OpenAI API key
api_key = getenv("gpt_api")
if not api_key:
    raise ValueError("Environment variable 'gpt_api' is not set. Please create a .env file with gpt_api=your-api-key")
client = OpenAI(api_key=api_key)

def save_to_file(data, filename='results.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

#функция с несколькими аргументами
def task_breakdown(main_query, ancestors_of_queries, depth, **kwargs):

    for key in kwargs:
        print(kwargs[key]["step"])
        if "need_further_breakdown" in kwargs[key] and kwargs[key]["need_further_breakdown"] and depth <= max_depth:
            kwargs[key]["SubSteps"] = Breakdown(f"{kwargs[key]['step']} (this is a step in breakdown of this task: ///{main_query}///. Do not include steps from this list ///{all_steps}///) This step is the breakdown of this previous steps: //{ancestors_of_queries}//", ancestors_of_queries=f"{ancestors_of_queries} -> {kwargs[key]['step']}", depth=depth, main_query=main_query, model=model if depth <= max_gpt4_depth else "gpt-3.5-turbo", temperature=temperature)
        else:
            kwargs[key]["SubSteps"] = {}
    return kwargs

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
            "name": "task_breakdown",
            "description": "Detailed steps by step breakdown of the task (some steps could be None, if you do not need all 10 steps). Write each step so that it can be fully understood by a person who is not familiar with the task or other steps. No long answers, there will be further breakdowns on subtasks. Write in russian.",
            "parameters": {
            "type": "object",
            "properties": {
                "step1": {
                    "type": "object",
                    "description": "first step",
                    "properties": {
                        "step": {
                            "type": "string",
                            "description": "step description",
                        },
                        "need_further_breakdown": {
                            "type": "boolean",
                            "description": "if True - this subtask need further breakdown to subtasks.",
                        },
                    },
                    "required": ["step", "need_further_breakdown"],
                },
                "step2": {
                    "type": "object",
                    "description": "second step",
                    "properties": {
                        "step": {
                            "type": "string",
                            "description": "step description",
                        },
                        "need_further_breakdown": {
                            "type": "boolean",
                            "description": "if True - this subtask need further breakdown to subtasks.",
                        },
                    },
                    "required": ["step", "need_further_breakdown"],
                },
                "step3": {
                    "type": "object",
                    "description": "third step",
                    "properties": {
                        "step": {
                            "type": "string",
                            "description": "step description",
                        },
                        "need_further_breakdown": {
                            "type": "boolean",
                            "description": "if True - this subtask need further breakdown to subtasks.",
                        },
                    },
                    "required": ["step", "need_further_breakdown"],
                },
                "step4": {
                    "type": "object",
                    "description": "fourth step",
                    "properties": {
                        "step": {
                            "type": "string",
                            "description": "step description",
                        },
                        "need_further_breakdown": {
                            "type": "boolean",
                            "description": "if True - this subtask need further breakdown to subtasks.",
                        },
                    },
                    "required": ["step", "need_further_breakdown"],
                },
                "step5": {
                    "type": "object",
                    "description": "fifth step",
                    "properties": {
                        "step": {
                            "type": "string",
                            "description": "step description",
                        },
                        "need_further_breakdown": {
                            "type": "boolean",
                            "description": "if True - this subtask need further breakdown to subtasks.",
                        },
                    },
                    "required": ["step", "need_further_breakdown"],
                },
                "step6": {
                    "type": "object",
                    "description": "sixth step",
                    "properties": {
                        "step": {
                            "type": "string",
                            "description": "step description",
                        },
                        "need_further_breakdown": {
                            "type": "boolean",
                            "description": "if True - this subtask need further breakdown to subtasks.",
                        },
                    },
                    "required": ["step", "need_further_breakdown"],
                },
                "step7": {
                    "type": "object",
                    "description": "seventh step",
                    "properties": {
                        "step": {
                            "type": "string",
                            "description": "step description",
                        },
                        "need_further_breakdown": {
                            "type": "boolean",
                            "description": "if True - this subtask need further breakdown to subtasks.",
                        },
                    },
                    "required": ["step", "need_further_breakdown"],
                },
                "step8": {
                    "type": "object",
                    "description": "eighth step",
                    "properties": {
                        "step": {
                            "type": "string",
                            "description": "step description",
                        },
                        "need_further_breakdown": {
                            "type": "boolean",
                            "description": "if True - this subtask need further breakdown to subtasks.",
                        },
                    },
                    "required": ["step", "need_further_breakdown"],
                },
                "step9": {
                    "type": "object",
                    "description": "ninth step",
                    "properties": {
                        "step": {
                            "type": "string",
                            "description": "step description",
                        },
                        "need_further_breakdown": {
                            "type": "boolean",
                            "description": "if True - this subtask need further breakdown to subtasks.",
                        },
                    },
                    "required": ["step", "need_further_breakdown"],
                },
                "step10": {
                    "type": "object",
                    "description": "tenth step",
                    "properties": {
                        "step": {
                            "type": "string",
                            "description": "step description",
                        },
                        "need_further_breakdown": {
                            "type": "boolean",
                            "description": "if True - this subtask need further breakdown to subtasks.",
                        },
                    },
                    "required": ["step", "need_further_breakdown"],
                },
                }
            },
            "required": ["step1", "step2", "step3", "step4", "step5", "step6", "step7", "step8", "step9", "step10"],
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
        response = client.chat.completions.create(
            model=model, # "gpt-4", #"gpt-3.5-turbo",
            messages=messages,
            tools=[{
                "type": "function",
                "function": functions[0]
            }],
            tool_choice={"type": "function", "function": {"name": "task_breakdown"}},
            temperature=temperature
        )
    except Exception as e:
        print(f"Exception: {e}")
        save_to_file(f"Error: {e}", f'middle_results/{main_query[:15]}_{time_prefix}_{model}/{str(depth)}/{main_query[:15]}_{str(depth)}_{query[:15]}_{time()}.json')

        return {}
    # Шаг 4: Обработать ответ
    #print(f" response: {response}")
    response_content = response.choices[0].message
    #print(f" response_content: {response_content}")
    # Get tool calls from the response (new API format)
    tool_calls = response_content.tool_calls
    function_call_args = tool_calls[0].function.arguments if tool_calls else None
    #print(f" function_call_args: {function_call_args}")
    if function_call_args is not None:
        try:
            steps = json.loads(function_call_args)
            for step in steps:
                steps[step]["step"] = decode_string(steps[step]["step"])
            #.encode('utf-8').decode('unicode_escape')
            #print(f" steps: {steps}")
        except json.JSONDecodeError:
            steps = {}

    else:
        steps = {}

    unique_steps = {}
    seen_steps = set()
    for k, v in steps.items():
        step_desc = v.get("step")
        if step_desc and step_desc not in all_steps and step_desc not in seen_steps:
            unique_steps[k] = v
            seen_steps.add(step_desc)
    steps = unique_steps



    steps_list = [step_data["step"] for step_data in steps.values() if "step" in step_data]
    """steps_list = [step_data["step"] for step_data in steps if "step" in step_data]"""

    save_to_file(steps_list, f'middle_results/{main_query[:15]}_{time_prefix}_{model}/{str(depth)}/{main_query[:15]}_{str(depth)}_{query[:15]}_{time()}.json')
    all_steps.update(steps_list)
    print(f" steps: {steps}")
    if steps and len(steps) > 1:
        kwargs = task_breakdown(main_query=main_query, ancestors_of_queries=ancestors_of_queries, depth = depth + 1, **steps)
        return kwargs
    return {}
    
def print_steps(json_data, indent=0, prefix='', file=None):
    """Рекурсивно печатает шаги из вложенного JSON-объекта.

    Аргументы:
    json_data -- словарь с шагами и подшагами
    indent -- текущий уровень отступа
    prefix -- текущий префикс для вертикальных линий
    file -- файловый объект для записи вывода
    """
    keys = list(json_data.keys())
    for i, key in enumerate(keys):
        value = json_data[key]
        is_last = i == len(keys) - 1

        new_prefix = prefix + ('└── ' if is_last else '├── ')

        print(prefix + new_prefix + value["step"], file=file)

        if value.get("need_further_breakdown"):
            next_prefix = prefix + ('    ' if is_last else '│   ')
            print_steps(value["SubSteps"], indent=indent + 4, prefix=next_prefix, file=file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a task breakdown")
    parser.add_argument("query", nargs="?", default=query, help="Main task description")
    parser.add_argument("--model", default=model, help="OpenAI model to use")
    parser.add_argument("--max-depth", type=int, default=max_depth, help="Max recursion depth")
    parser.add_argument("--gpt4-depth", type=int, default=max_gpt4_depth, help="Depth to use GPT-4")
    parser.add_argument("--temperature", type=float, default=temperature, help="Sampling temperature")
    args = parser.parse_args()

    model = args.model
    max_depth = args.max_depth
    max_gpt4_depth = args.gpt4_depth
    temperature = args.temperature
    query = args.query

    result = Breakdown(query, query, query, model=model, temperature=temperature)
    print(json.dumps(result, indent=4, ensure_ascii=False))
    if not path.exists('results'):
        makedirs('results')
    filename_prefix = f"results/{query[:40]}_{model}_t{temperature}_{time()}"
    with open(f"{filename_prefix}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    with open(f"{filename_prefix}.txt", "w", encoding="utf-8") as f:
        print_steps(result, file=f)
