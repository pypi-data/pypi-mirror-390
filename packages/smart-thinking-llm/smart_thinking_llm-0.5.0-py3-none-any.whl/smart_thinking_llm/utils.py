from functools import lru_cache
import logging
import multiprocessing
import sys

import openai
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer


def init_basic_logger(
    name: str, level: int, with_tqdm: bool = False, file_handler: bool = False
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if len(logger.handlers) == 0 and not with_tqdm:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(
            logging.Formatter(fmt="[%(asctime)s: %(levelname)s %(name)s] %(message)s")
        )
        logger.addHandler(handler)
    if file_handler:
        handler = logging.FileHandler(name + ".log")
        handler.setFormatter(
            logging.Formatter(fmt="[%(asctime)s: %(levelname)s %(name)s] %(message)s")
        )
        logger.addHandler(handler)
    return logger

def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class QuestionQualityMetric:
    def __init__(self, openai_client: openai.OpenAI, openai_model_name: str):
        self.openai_client = openai_client
        self.openai_model_name = openai_model_name
        self.name = "Question Quality Metric"
        self.description = "Measures the quality and naturalness of generated questions"

    def measure(self, question: str, answer: str) -> float:
        # Define evaluation prompt for the LLM to score the question
        eval_prompt = f"""
        Rate the following question (with providedd answer) on a scale from 0 to 1, where:
        - 0 means poor quality: unnatural, confusing, grammatically incorrect
        - 1 means excellent quality: natural, clear, grammatically correct
        
        Question: {question}
        Question answer: {answer}

        Provide only score in the range [0, 1].

        Example 1:
        Question: What is the capital of France?
        Question answer: Paris
        Responce: 1.00

        Example 2:
        Question: What type of institution is Indiana University?
        Question answer: State university system
        Responce: 0.15
        """

        # Call a model to evaluate
        response = self.openai_client.chat.completions.create(
            model=self.openai_model_name,
            messages=[{"role": "user", "content": eval_prompt}],
            max_tokens=16,
            temperature=0.0,
        )
        result = response.choices[0].message.content

        # Extract score
        try:
            score = float(result.strip()) if result else 0.0
        except (ValueError, TypeError) as e:
            print(f"Error occured while parsing score {e}")
            score = 0.0

        return score


# Автоматическое определение числа потоков на основе CPU
def get_optimal_threads():
    # Получаем количество логических ядер
    cpu_count = multiprocessing.cpu_count()

    # Консервативная оценка
    if cpu_count <= 2:
        return 4
    elif cpu_count <= 4:
        return 8
    else:
        return min(cpu_count * 2, 20)  # Не более 20 потоков

@lru_cache(maxsize=1000)
def make_openai_request(
    openai_client: openai.OpenAI,
    model_name: str,
    prompt: str,
    logger: logging.Logger = logging.getLogger(__name__),
    max_tokens: int = 16,
    temperature: float = 0.25,
) -> str:
    """Делает запрос к OpenAI API"""
    try:
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content
        return content.strip() if content else ""
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return ""

def last_token_pool(last_hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    sequence_lengths = attention_mask.sum(dim=1, dtype=torch.long) - 1
    batch_size = last_hidden_states.shape[0]

    sequence_lengths = sequence_lengths.view(batch_size, 1, 1).expand(
        -1, -1, last_hidden_states.shape[-1]
    )
    last_hidden = torch.gather(last_hidden_states, dim=1, index=sequence_lengths).squeeze(1)

    return last_hidden

def get_embedding_batch(
    batch_texts: list[str],
    tokenizer: AutoTokenizer,
    model: AutoModel,
    normalize: bool,
    max_length: int = 64,
) -> torch.Tensor:
    """Get embeddings for batch of texts"""
    with torch.no_grad():
        # Tokenize the input texts
        batch_dict = tokenizer(
            batch_texts,
            return_tensors="pt",
            max_length=max_length,
            truncation=True,
            padding=True,
        )
        batch_dict = {k: v.to(model.device) for k, v in batch_dict.items()}
        outputs = model(**batch_dict)
        embeddings = last_token_pool(outputs.last_hidden_state, batch_dict["attention_mask"])

        # normalize embeddings
        if normalize:
            embeddings = F.normalize(embeddings, p=2, dim=1)
        result = embeddings.cpu()

        del batch_dict, outputs, embeddings

        return result # [batch_size, embedding_dim]

def cosine_similarity_normalized_embeddings(embedding1: torch.Tensor, embedding2: torch.Tensor) -> float:
    scores = (embedding1 @ embedding2.T) # [embedding_dim, ] @ [batch_size, embedding_dim].T -> [batch_size, ]
    return scores.tolist() # [batch_size, ]