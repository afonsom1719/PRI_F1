from typing import Any, Sequence, Tuple, Dict, Union, Callable
import json
from openai import OpenAI
import os
import math
import inspect
from collections import deque
from azure.search.documents.models import QueryType
from approaches.approach import Approach
from text import nonewlines
import logging

# Create a logger
logger = logging.getLogger("globalLogger")


FUNCTION_CALL_LABEL = "function_call"
NEGATIVE_LABEL = "Negative"
SELF_LABEL = "self"
PROMPT_LABEL = "prompt"
NONE_INFO_LABEL = "NoneInfo"
SENTIMENTAL_ON_EACH = 1
LANGUAGE_DICT = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
}
FUNCTIONS_DESCRIPTIONS = [
    {
        "name": "create_images",
        "description": "Use this function to create images from a description. This function should be only used if the description includes explicitly the intent of creating or drawing an image. The user must explicitly say he wants to create an image.",
        "parameters": {
            "type": "object",
            "properties": {
                "dallE_prompt": {
                    "description": "The user description of the image he wants to build.",
                    "type": "string",
                },
            },
            "required": ["dallE_prompt"],
        },
    },
    {
        "name": "calculator",
        "description": "A simple calculator used to perform basic arithmetic operations",
        "parameters": {
            "type": "object",
            "properties": {
                "num1": {"type": "number"},
                "num2": {"type": "number"},
                "operator": {
                    "type": "string",
                    "enum": ["+", "-", "*", "/", "**", "sqrt"],
                },
            },
            "required": ["num1", "num2", "operator"],
        },
    },
]

openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# Simple retrieve-then-read implementation, using the Cognitive Search and OpenAI APIs directly. It first retrieves
# top documents from search, then constructs a prompt with them, and then uses OpenAI to generate an completion
# (answer) with that prompt.
class ChatReadRetrieveReadApproach(Approach):
    prompt_prefix = """<|im_start|>system
        Assistant helps the company employees extracting information from uploaded invoices and providing answers related to the extracted data, performing basic calculations, creating images according to the user input, and also answering their questions about everything.
        If the user asks if the assistant can extract data from invoices, tell him you can but he needs to upload them in case they have not already. In this case do not include any citation.
        Be brief in your answers. Make a citation whenever possible.
        Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below. If asking a clarifying question to the user would help, ask the question.
        For tabular information return it as an html table. Do not return markdown format.
        Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brakets to reference the source, e.g. [info1.txt]. Don't combine sources, list each source separately, e.g. [info1.txt][info2.pdf].
        {follow_up_questions_prompt}
        {injected_prompt}
        Sources:
        {sources}
        <|im_end|>
        {chat_history}
        """

    prompt_prefix_no_content = """<|im_start|>system
        Assistant helps the company employees extracting information from uploaded invoices and providing answers related to the extracted data, performing basic calculations, creating images according to the user input, and also answering their questions about everything.
        If the user asks if the assistant can extract data from invoices, tell him you can but he needs to upload them in case they have not already. In this case do not include any citation.
        Be brief in your answers.
        If there isn't enough information below, say you don't know. If asking a clarifying question to the user would help, ask the question.
        For tabular information return it as an html table. Do not return markdown format. 
        {injected_prompt}
        <|im_end|>
        {chat_history}
        """

    follow_up_questions_prompt_content = """Generate three very brief follow-up questions that the user would likely ask next about their healthcare plan and employee handbook. 
        Use double angle brackets to reference the questions, e.g. <<Are there exclusions for prescriptions?>>.
        Try not to repeat questions that have already been asked.
        Only generate questions and do not generate any text before or after the questions, such as 'Next Questions'"""

    query_prompt_template = """Below is a history of the conversation so far, and a new question asked by the user that needs to be answered. The answer should be based on your knowledge base or in a given function execution.
        Generate a search query based on the conversation and the new question. Beware that the question may not be in English.
        Do not include cited source filenames and document names e.g info.txt or doc.pdf in the search query terms.
        Do not include any text inside [] or <<>> in the search query terms.
        If the question is not in English, translate the question to English before generating the search query.

        Chat History:
        {chat_history}

        Question:
        {question}

        Search query:
        """

    sentimental_analysis_base_prompt = """Based on the following conversation, analyze the user statements and perform a sentimental analysis on them. Classify the user conversation from 1 to 10 where 1 is very negative, 5 is neutral and 10 is very positive.
    You should take into account the user sentence to classify.
        Return the response in a JSON format like so: {"sentiment": "6"}
        """

    messages = deque(maxlen=20)  # type: ignore
    m_history: list[dict[str, str]] = []
    m_overrides: dict[str, str] = {}
    m_language: str = "en"

    def __init__(
        self,
        chatgpt_deployment: str,
        gpt_deployment: str,
        gpt_functions_deployment: str,
        sourcepage_field: str,
        content_field: str,
    ):
        self.chatgpt_deployment = chatgpt_deployment
        self.gpt_deployment = gpt_deployment
        self.gpt_functions_deployment = gpt_functions_deployment
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field

    def create_images(self, dallE_prompt: str) -> str:
        """Uses OpenAI Image to create images from text prompts.

        This function takes a text prompt as input and uses the OpenAI Image API to create images from it.
        The function uses DALL-E, a generative model that can create images from natural language descriptions. The function returns the URL of the generated image.

        Args:
            dallE_prompt (str): A text prompt that describes the image to be created.

        Returns:
            str: The URL of the generated image.

        Raises:
            ValueError: If the dallE_prompt is empty or invalid.
            OpenAIError: If there is an error while calling the OpenAI API.
        """
        logger.info(f"Creating images for {dallE_prompt}")
        # dallE = openai.Image.create(
        #     prompt=dallE_prompt,
        #     size=os.environ.get("DALLE_IMAGE_SIZE"),
        #     n=1,
        #     temperature=0.7,
        # )

        return True, {
            "data_points": [],
            "answer": dallE["data"][0]["url"],
            "thoughts": f"I need to call DallE API for this with the prompt: {dallE_prompt}",
            "dallE": True,
        }

    def calculator(
        self, num1: Union[int, float], num2: Union[int, float], operator: str
    ) -> str:
        """Performs a basic arithmetic operation on two numbers.

        Args:
            num1 (Union[int, float]): The first operand.
            num2 (Union[int, float]): The second operand.
            operator (str): The operator to apply. Can be one of "+", "-", "*", or "/".

        Returns:
            str: The result of the operation if it identifies the operator, otherwhise returns "Invalid opertator".

        """
        logger.info(f"Calculating {num1} {operator} {num2}")
        plus_sign = "+"
        minus_sign = "-"
        multiply_sign = "*"
        divide_sign = "/"
        power_sign = "**"
        sqrt_operator = "sqrt"

        if operator == plus_sign:
            result = str(num1 + num2)
        elif operator == minus_sign:
            result = str(num1 - num2)
        elif operator == multiply_sign:
            result = str(num1 * num2)
        elif operator == divide_sign:
            result = str(num1 / num2)
        elif operator == power_sign:
            result = str(num1**num2)
        elif operator == sqrt_operator:
            result = str(math.sqrt(num1))
        else:
            result = "Invalid operator"

        return True, {
            "data_points": [],
            "answer": result,
            "thoughts": f"I need to call calculator for this with the arguments: {num1}, {num2}, {operator}",
            "dallE": False,
        }

    # invoice_data = self.process_invoice(invoice_prompt)
    def sentimental_analysis(self, history: Sequence[dict[str, str]]) -> str:
        """Uses OpenAI Completion to perform sentiment analysis on user messages.

        This function takes a sequence of user messages as input and uses the OpenAI Completion API to perform sentiment analysis on them.
        The function uses a predefined base prompt that contains the logic and criteria for the sentiment analysis.
        The function returns a string that indicates the overall sentiment of the user messages, such as "Positive", "Negative", or "Neutral".

        Args:
            history (Sequence[dict[str, str]]): A sequence of user messages as dictionaries with keys "user" and "assistant".

        Returns:
            str: A string that indicates the overall sentiment of the user messages.

        Raises:
            ValueError: If the history is empty or invalid.
            OpenAIError: If there is an error while calling the OpenAI API.
        """
        sentimental_analysis = f"{self.sentimental_analysis_base_prompt} {history}"
        logger.info(self.chatgpt_deployment)
        logger.info(self.gpt_deployment)
        logger.info(self.gpt_functions_deployment)

        sentimental_analysis_completion = ompletion.create(
            engine=self.gpt_deployment,
            prompt=sentimental_analysis,
            temperature=0.2,
            max_tokens=32,
            n=1,
        )
        sentimental_analysis_response = sentimental_analysis_completion.choices[0].text
        sentimental_json = json.loads(sentimental_analysis_response)

        logger.info(sentimental_json["sentiment"])

        return sentimental_json["sentiment"]

    def check_args(self, function: Callable, args: Dict[str, Any]) -> bool:
        """Checks if the args are valid for the function.

        Args:
            function (Callable): The callable object to check the args for.
            args (Dict[str, Any]): The dictionary of argument names and values.

        Returns:
            bool: True if the args are valid, False otherwise.
        """
        logger.info("Checking if args are valid")
        sig = inspect.signature(function)
        params = sig.parameters

        logger.info("params")
        logger.info(params)
        logger.info("args")
        logger.info(args)
        # Check if there are extra arguments
        for name in args:
            if name not in params:
                logger.error(f"Invalid argument: {name}")
                return False
        # Check if the required arguments are provided
        for name, param in params.items():
            if param.default is param.empty and name not in args and name != SELF_LABEL:
                logger.error(f"Missing argument: {name}")
                return False

        return True

    def check_function(self, response_message: Dict[str, Union[str, Dict]]):
        """Check the function call in the chat completion response and process it.

        Args:
            response_message (Dict[str, Union[str, Dict]]): The chat completion response message containing function call details.
            available_functions (Dict[str, Callable]): A dictionary of function names and callable objects.

        Returns:
            Any: The result of the function call.

        Raises:
            ValueError: If the function name does not exist in the available functions or if there is an invalid number of arguments for the function.
        """
        logger.info("Checking if function call is valid")
        function_name: str = response_message[FUNCTION_CALL_LABEL]["name"]
        if function_name not in self.AVAILABLE_FUNCTIONS:
            logger.error(f"Function {function_name} does not exist")
            return True, {
                "data_points": [],
                "answer": "I am confused can you be more specific?",
                "thoughts": "",
                "dallE": False,
            }

        function_to_call: Callable = self.AVAILABLE_FUNCTIONS[function_name]
        function_args = json.loads(response_message[FUNCTION_CALL_LABEL]["arguments"])

        if self.check_args(function_to_call, function_args) is False:
            logger.error(f"Invalid number of arguments for function: {function_name}")
            return True, {
                "data_points": [],
                "answer": "I do not have enough information to answer this question.",
                "thoughts": "",
                "dallE": False,
            }

        sig = inspect.signature(function_to_call)
        func_params = sig.parameters
        logger.info("func_params")
        logger.info(func_params)
        logger.info("function_args")
        logger.info(function_args)
        if SELF_LABEL in func_params:
            function_args[SELF_LABEL] = self

        stop_bool, function_response = function_to_call(**function_args)
        return stop_bool, function_response

    def gpt_functions(
        self, history: Sequence[dict[str, str]]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Uses OpenAI ChatCompletion to check if we should create images from text prompts.

        This function takes a sequence of user messages as input and uses the OpenAI ChatCompletion API to check if we need to use a function to generate images from text prompts.
        The function uses a predefined list of functions that can be called by the user, such as create_images. The function returns a tuple of a boolean flag and a dictionary of data points, answer, thoughts, and dallE.

        Args:
            history (Sequence[dict[str, str]]): A sequence of user messages as dictionaries with keys "user" and "assistant".

        Returns:
            Tuple[bool, Dict[str, Any]]: A tuple of a boolean flag indicating whether the function call was successful or not, and a dictionary containing the following keys:
                - data_points (List[Any]): A list of data points related to the answer.
                - answer (str): The answer to the user's question or prompt.
                - thoughts (str): The thoughts or reasoning behind the answer.
                - dallE (bool): A flag indicating whether the answer is an image generated by DALL-E or not.

        Raises:
            ValueError: If the user's question or prompt is invalid or not supported by the function.
            OpenAIError: If there is an error while calling the OpenAI API.
        """
        # Checking firstly for DallE execution
        logger.debug("Checking if we need to call a function using GPT functions...")
        user_question = history[-1]["user"]
        logger.info(f"User question: {user_question}")

        functions = openai.chat.completions.create(
            model=self.gpt_functions_deployment,
            messages=[{"role": "user", "content": user_question}],
            functions=FUNCTIONS_DESCRIPTIONS,
            function_call="auto",
            max_tokens=250,
        )

        functions_response = functions.choices[0]
        if functions_response.finish_reason == FUNCTION_CALL_LABEL:
            reply_content = functions_response.message

            reply_function = functions_response.message.function_call.name
            func = reply_content.to_dict()[FUNCTION_CALL_LABEL]["arguments"]
            func = json.loads(func)
            logger.info("func")
            logger.info(func)
            if PROMPT_LABEL in func:
                functions_prompt = func[PROMPT_LABEL]
                logger.info("functions_prompt")
                logger.info(functions_prompt)
                logger.info(f"I must call: {reply_function}")
                logger.info(
                    f"I need to call {reply_function} for this with the prompt: {functions_prompt}"
                )

            function_should_return, function_answer = self.check_function(reply_content)

            return function_should_return, function_answer

        return False, {}

    def prepare_messages(self):
        """Prepares the messages to be used by the OpenAI API.

        This function prepares the messages to be used by the OpenAI API by appending the user and assistant messages to the messages list.

        """
        for message in self.m_history:
            if message.get("user"):
                self.messages.append({"role": "user", "content": message["user"]})
            if message.get("bot"):
                self.messages.append({"role": "assistant", "content": message["bot"]})

    AVAILABLE_FUNCTIONS: Dict[str, Callable] = {
        "create_images": create_images,
        "calculator": calculator,
    }

    def generate_optimized_query(self) -> str:
        """
        Generates an optimized keyword search query based on the chat history and the last question.

        Returns:
            str: The generated optimized query.

        Raises:
            None
        """
        # STEP 1: Generate an optimized keyword search query based on the chat history and the last question
        logger.debug(
            "Generating an optimized keyword search query based on the chat history and the last question..."
        )

        # translated_question = (
        #     translate_text(self.m_history[-1]["user"]) or self.m_history[-1]["user"]
        # )

        prompt = self.query_prompt_template.format(
            chat_history=self.get_chat_history_as_text(
                self.m_history, include_last_turn=False
            ),
            question=self.m_history[-1]["user"],
        )
        logger.debug(f"prompt: {prompt}")

        completion = openai.completions.create(
            model=self.gpt_deployment,
            prompt=prompt,
            max_tokens=32,
            n=1,
        )

        q = completion.choices[0].text

        # translated_query = translate_text(q)
        logger.debug(f"translated_query: {q}")
        logger.debug("q")
        logger.debug(q)

        return q

    def retrieve_relevant_documents(
        self, optimized_query: str
    ) -> Tuple[str, str, list]:
        """
        Retrieves relevant documents from the search index with the GPT optimized query.

        Args:
            optimized_query (str): The GPT optimized query.

        Returns:
            list[dict[str, str]]: A list of relevant documents, each represented as a dictionary with 'sourcepage' and 'content' fields.

        Raises:
            None

        """
        # STEP 2: Retrieve relevant documents from the search index with the GPT optimized query
        logger.debug(
            "Retrieving relevant documents from the search index with the GPT optimized query..."
        )

        use_semantic_captions = (
            True  # if self.m_overrides.get("semantic_captions") else False
        )
        top = self.m_overrides.get("top") or 3

        exclude_category = self.m_overrides.get("exclude_category") or None
        filter = (
            "category ne '{}'".format(exclude_category.replace("'", "''"))
            if exclude_category
            else None
        )

        if self.m_overrides.get("semantic_ranker"):
            r = self.search_client.search(
                optimized_query,
                filter=filter,
                query_type=QueryType.SEMANTIC,
                query_language="en-us",
                query_speller="lexicon",
                semantic_configuration_name="default",
                top=top,
                query_caption="extractive|highlight-false"
                if use_semantic_captions
                else None,
            )
        else:
            r = self.search_client.search(optimized_query, filter=filter, top=top)

        results = [
            doc[self.sourcepage_field] + ": " + nonewlines(doc[self.content_field])
            for doc in r
        ]

        # if use_semantic_captions:
        #     results = [
        #         doc[self.sourcepage_field]
        #         + ": "
        #         + nonewlines(" . ".join([c.text for c in doc["@search.captions"]]))
        #         for doc in r
        #     ]
        # else:
        #     results = [
        #         doc[self.sourcepage_field] + ": " + nonewlines(doc[self.content_field])
        #         for doc in r
        #     ]
        content = "\n".join(results)
        logger.debug("content")
        logger.debug(content)
        follow_up_questions_prompt = (
            self.follow_up_questions_prompt_content
            if self.m_overrides.get("suggest_followup_questions")
            else ""
        )

        return content, follow_up_questions_prompt, results

    def prompt_injection(self, content: str, follow_up_questions_prompt: str) -> str:
        """
        Generate a prompt by injecting content into the existing prompt or replacing the entire prompt.

        Args:
            prompt (str): The original prompt.
            content (str): The content to inject into the prompt.
            follow_up_questions_prompt (str): The prompt for follow-up questions.

        Returns:
            str: The generated prompt.
        """
        # Allow client to replace the entire prompt, or to inject into the exiting prompt using >>>
        logger.debug(
            "Allowing client to replace the entire prompt, or to inject into the exiting prompt using >>>..."
        )

        prompt_override = self.m_overrides.get("prompt_template")
        no_content = "No sources found."
        if content == no_content:
            prefix = self.prompt_prefix_no_content
        else:
            prefix = self.prompt_prefix

        logger.debug(f"prefix: {prefix}")

        if prompt_override is None:
            prompt = prefix.format(
                injected_prompt="",
                sources=content,
                chat_history=self.get_chat_history_as_text(self.m_history),
                follow_up_questions_prompt=follow_up_questions_prompt,
            )
        elif prompt_override.startswith(">>>"):
            prompt = prefix.format(
                injected_prompt=prompt_override[3:] + "\n",
                sources=content,
                chat_history=self.get_chat_history_as_text(self.m_history),
                follow_up_questions_prompt=follow_up_questions_prompt,
            )
        else:
            prompt = prompt_override.format(
                sources=content,
                chat_history=self.get_chat_history_as_text(self.m_history),
                follow_up_questions_prompt=follow_up_questions_prompt,
            )

        return prompt

    def generate_contextual_answer(self, prompt: str) -> str:
        """
        Generate a contextual and content-specific answer using the search results and chat history.

        Args:
            prompt (str): The prompt to generate the answer from.
            sentimental_str (str): The sentiment string indicating the sentiment of the user.

        Returns:
            Any: The generated answer.

        Raises:
            None
        """
        # STEP 3: Generate a contextual and content specific answer using the search results and chat history
        logger.debug(
            "Generating a contextual and content specific answer using the search results and chat history..."
        )

        completion = openai.completions.create(
            model=self.gpt_deployment,
            prompt=prompt,
            max_tokens=1024,
            n=1,
        )

        answer = completion.choices[0].text

        return answer

    def run(
        self,
        history: Sequence[dict[str, str]],
        overrides: dict[str, Any],
        language: str,
    ) -> Dict[str, str]:
        logger.debug(f"Running {__file__} approach")
        self.m_history = history
        self.m_overrides = overrides
        self.prepare_messages()
        m_language = LANGUAGE_DICT[language]
        logger.debug(f"m_language: {m_language}")
        sentimental_str = ""

        logger.info("history")
        logger.info(history)

        if len(history) % SENTIMENTAL_ON_EACH == 0:
            logger.debug("Performing sentimental analysis...")
            # sentimental_str = self.sentimental_analysis(history=history)

            logger.info("sentimental_str")
            logger.info(sentimental_str)
            if sentimental_str and sentimental_str == NEGATIVE_LABEL:
                logger.info("we should register the negative sentiment from the user")

        should_return, data = self.gpt_functions(history=history)

        logger.debug("should_return")
        logger.debug(should_return)
        logger.debug(data)

        if should_return:
            return data

        optimized_query = self.generate_optimized_query()

        # if optimized_query != "":
        #     logger.debug("optimized_query is not empty: " + optimized_query)
        #     (
        #         content,
        #         follow_up_questions_prompt,
        #         results,
        #     ) = self.retrieve_relevant_documents(optimized_query=optimized_query)
        # else:
        #     logger.debug("optimized_query is empty")
        #     content = "No sources found."
        #     follow_up_questions_prompt = ""
        #     results = []

        prompt = self.prompt_injection(
            content="No sources found.", follow_up_questions_prompt=""
        )

        answer = self.generate_contextual_answer(prompt=prompt)

        logger.debug("answer")
        logger.debug(answer)
        logger.debug("results")
        # logger.debug(results)
        logger.debug(PROMPT_LABEL)
        logger.debug(prompt)
        logger.debug("content")
        # logger.debug(content)

        return {
            "data_points": "results",
            "answer": answer,
            "sentiment": sentimental_str,
            "thoughts": f"Searched for:<br>{optimized_query}<br><br>Prompt:<br>"
            + prompt.replace("\n", "<br>"),
        }

    def get_chat_history_as_text(
        self,
        history: Sequence[dict[str, str]],
        include_last_turn: bool = True,
        approx_max_tokens: int = 1000,
    ) -> str:
        history_text = ""
        for h in reversed(history if include_last_turn else history[:-1]):
            history_text = (
                """<|im_start|>user"""
                + "\n"
                + h["user"]
                + "\n"
                + """<|im_end|>"""
                + "\n"
                + """<|im_start|>assistant"""
                + "\n"
                + (h.get("bot", "") + """<|im_end|>""" if h.get("bot") else "")
                + "\n"
                + history_text
            )
            if len(history_text) > approx_max_tokens * 4:
                break
        return history_text
