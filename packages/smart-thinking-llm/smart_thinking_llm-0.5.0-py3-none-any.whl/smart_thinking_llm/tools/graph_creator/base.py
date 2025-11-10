from abc import abstractmethod
import ast
import logging
from collections import defaultdict
import re
from tqdm import tqdm

import openai
from dotenv import load_dotenv
from pathlib import Path
from typing import Literal

from smart_thinking_llm.datasets.data_classes import (
    Entity,
    EntityID,
    Relation,
    RelationID,
)
from smart_thinking_llm.tools.graph import Graph
from smart_thinking_llm.utils import (
    init_basic_logger,
    make_openai_request,
)

load_dotenv()


class GraphCreatorBase:
    def __init__(
        self,
        entity_aliases_filepath: Path,
        relation_aliases_filepath: Path,
        dataset_filepath: Path,
        triplets_prompt_filepath: Path,
        openai_client: openai.OpenAI,
        triplets_model: Literal[
            "gpt-4.1-2025-04-14",
            "gpt-4.1-mini-2025-04-14",
            "gpt-4.1-nano-2025-04-14",
        ] = "gpt-4.1-nano-2025-04-14",
        norm_lev_threshold: float = 0.3,
        parse_graph_strategy: Literal[
            "no_info",  # без знаний о сущностях внутри одной тройки или каких-либо еще
            "root_entity",  # в коде используется информация о предсказанном root entity
            "pair_entities",  # в коде используется информация о предсказанных подряд entity
        ] = "pair_entities",
        logger_level: int = logging.WARNING,
    ):
        self.entity_aliases_filepath = entity_aliases_filepath
        self.relation_aliases_filepath = relation_aliases_filepath
        self.dataset_filepath = dataset_filepath
        self.triplets_prompt_filepath = triplets_prompt_filepath
        self.triplets_model = triplets_model
        self.openai_client = openai_client
        self.logger = init_basic_logger(self.__class__.__name__, logger_level)
        self.norm_lev_threshold = norm_lev_threshold

        if parse_graph_strategy not in ["no_info", "root_entity", "pair_entities"]:
            raise ValueError(f"Invalid parse graph strategy: {parse_graph_strategy}")
        self.parse_graph_strategy = parse_graph_strategy

        with open(self.triplets_prompt_filepath, mode="r", encoding="utf-8") as f:
            self.triplets_prompt = f.read()

        # Создаем индекс алиасов для быстрого поиска
        self.alias_to_entities = dict()
        self.entity_to_aliases = defaultdict(list)
        self.entity_aliases = []  # Список для rapidfuzz
        self.entity_aliases_prefix_index = defaultdict(list)  # Индекс по префиксам

        with open(self.entity_aliases_filepath, mode="r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in tqdm(
                lines, desc="Building entity alias index", total=len(lines)
            ):
                splitted_line = line.strip().split("\t")
                entity_id = splitted_line[0]
                aliases = splitted_line[1:]
                for alias in aliases:
                    normalized_alias = alias.lower().strip()
                    self.alias_to_entities[normalized_alias] = entity_id
                    self.entity_aliases.append(normalized_alias)
                    # Добавляем в префиксный индекс
                    prefix = (
                        normalized_alias[:3]
                        if len(normalized_alias) >= 3
                        else normalized_alias
                    )
                    self.entity_aliases_prefix_index[prefix].append(normalized_alias)
                self.entity_to_aliases[entity_id] = aliases

        self.alias_to_relation = {}
        self.relation_to_aliases = defaultdict(list)
        with open(self.relation_aliases_filepath, mode="r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in tqdm(
                lines, desc="Building relation alias index", total=len(lines)
            ):
                splitted_line = line.strip().split("\t")
                relation_id = splitted_line[0]
                aliases = splitted_line[1:]
                for alias in aliases:
                    normalized_alias = alias.lower().strip()
                    self.alias_to_relation[normalized_alias] = relation_id
                self.relation_to_aliases[relation_id] = aliases

        self.dataset_index = defaultdict(lambda: defaultdict(list))
        # matrix of entities to entities with relations lists [subject][answer] = list[relations]
        with open(self.dataset_filepath, mode="r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in tqdm(lines, desc="Building dataset index", total=len(lines)):
                splitted_line = line.strip().split("\t")
                subject = splitted_line[0]
                relation = splitted_line[1]
                answer = splitted_line[2]
                self.dataset_index[subject][answer].append(relation)

    @abstractmethod
    def find_entity_by_name(self, name: str, candidates: tuple[str]) -> Entity:
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def find_relation_by_name(
        self, relation_name: str, candidates: tuple[str]
    ) -> Relation:
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def parse_graph_structure(self, triplets_dict: defaultdict[str, dict[str, str]]) -> defaultdict[Entity, dict[Relation, Entity]]:
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def get_entity_candidates(self, entity_name: str) -> tuple[str]:
        raise NotImplementedError("Subclasses must implement this method")

    def get_relation_candidates(self, entity_start: Entity, entity_end: Entity) -> tuple[str]:
        if self.parse_graph_strategy == "no_info":
            return tuple(self.alias_to_relation.keys())
        elif self.parse_graph_strategy == "root_entity":
            candidates_relation_ids = []
            for relations in self.dataset_index[entity_start.id._id].values():
                candidates_relation_ids.extend(relations)

            candidates_aliases = []
            for relation_id in candidates_relation_ids:
                candidates_aliases.extend(self.relation_to_aliases[relation_id])

            return tuple(candidates_aliases)
        elif self.parse_graph_strategy == "pair_entities":
            candidates_relation_ids = self.dataset_index[entity_start.id._id][entity_end.id._id]

            candidates_aliases = []
            for relation_id in candidates_relation_ids:
                candidates_aliases.extend(self.relation_to_aliases[relation_id])

            return tuple(candidates_aliases)

    @staticmethod
    def parse_triplets(triplets: str) -> defaultdict[str, dict[str, str]]:
        # Check if triplets string matches the expected format using regex
        # Expected format: [("subject1", "relation1", "object1"), ("subject2", "relation2", "object2"), ...]
        triplet_pattern = r'^\s*\[\s*(?:\(\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*"[^"]*"\s*\)\s*(?:,\s*\(\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*"[^"]*"\s*\)\s*)*)?\s*\]\s*$'
        if not re.match(triplet_pattern, triplets.strip().replace("\n", "")):
            raise ValueError(
                f"Triplets string does not match expected format: {triplets}"
            )
        triplets = triplets.strip().replace("\n", "")
        triplets_list = ast.literal_eval(triplets)
        triplets_dict = defaultdict(dict)
        for triplet in triplets_list:
            subject, question, answer = triplet
            triplets_dict[subject][question] = answer
        return triplets_dict

    def get_graph_from_path(self, path: str) -> Graph:
        graph_structure = defaultdict(dict)
        triple_pattern = re.compile(r"(?=(Q\d+)-(P\d+)-(Q\d+))")

        for match in triple_pattern.finditer(path):
            subject_id, predicate_id, obj_id = match.groups()
            subject = Entity(EntityID(subject_id), self.entity_to_aliases[subject_id])
            predicate = Relation(
                RelationID(predicate_id), self._relation_to_aliases[predicate_id]
            )
            obj = Entity(EntityID(obj_id), self.entity_to_aliases[obj_id])
            graph_structure[subject][predicate] = obj

        return Graph(graph_structure)

    def __call__(self, model_answer: str) -> Graph:
        prompt = self.triplets_prompt % model_answer
        # [("Donatus Djagom", "religious affiliation", "Catholicism"), ("Catholicism", "headquarters located", "Vatican City")]
        triplets = make_openai_request(
            self.openai_client, self.triplets_model, prompt, self.logger
        )
        self.logger.debug("Triplets: %s", triplets)
        try:
            # {"Donatus Djagom": {"religious affiliation": "Catholicism"}, "Catholicism": {"headquarters located": "Vatican City"}}
            triplets_dict = self.parse_triplets(
                triplets
            )
        except ValueError as e:
            self.logger.warning(
                f"Error parsing triplets: {e}. Default triplets empty dict will be used."
            )
            triplets_dict = defaultdict(dict)
        self.logger.debug("Triplets dict: %s", triplets_dict)
        graph_structure = self.parse_graph_structure(triplets_dict)
        return Graph(graph_structure)