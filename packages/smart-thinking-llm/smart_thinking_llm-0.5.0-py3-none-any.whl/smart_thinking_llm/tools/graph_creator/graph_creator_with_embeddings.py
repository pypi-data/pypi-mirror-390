import logging
from collections import defaultdict
from functools import lru_cache
from tqdm import tqdm

import openai
import torch
from transformers import AutoModel, AutoTokenizer
from dotenv import load_dotenv
from pathlib import Path
from typing import Literal
from rapidfuzz import process, fuzz

from smart_thinking_llm.datasets.data_classes import (
    Entity,
    EntityID,
    Relation,
)
from smart_thinking_llm.tools.graph_creator.graph_creator import GraphCreator
from smart_thinking_llm.utils import (
    cosine_similarity_normalized_embeddings,
    get_embedding_batch,
)

load_dotenv()


class GraphCreatorWithEmbeddings(GraphCreator):
    def __init__(
        self,
        entity_aliases_filepath: Path,
        relation_aliases_filepath: Path,
        dataset_filepath: Path,
        triplets_prompt_filepath: Path,
        openai_client: openai.OpenAI,
        entity_description_filepath: Path,
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
        ] = "no_info",
        embeddings_model: Literal[
            "Qwen/Qwen3-Embedding-4B"
        ] = "Qwen/Qwen3-Embedding-4B",
        device: torch.device | str = torch.device("cuda:1"),
        logger_level: int = logging.WARNING,
    ):
        super().__init__(
            entity_aliases_filepath,
            relation_aliases_filepath,
            dataset_filepath,
            triplets_prompt_filepath,
            openai_client,
            triplets_model,
            norm_lev_threshold,
            parse_graph_strategy,
            logger_level,
        )

        if isinstance(device, str):
            device = torch.device(device)
        self.embeddings_tokenizer = AutoTokenizer.from_pretrained(
            embeddings_model,
            padding_side="left",
            use_fast=True,
        )
        self.embeddings_model = AutoModel.from_pretrained(
            embeddings_model,
            dtype=torch.bfloat16,
        )
        self.embeddings_model.to(device)
        self.embeddings_model.eval()
        self.device = device

        self._entity_descriptions = {}
        with open(entity_description_filepath, mode="r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in tqdm(
                lines, desc="Reading entity descriptions", total=len(lines)
            ):
                splitted_line = line.strip().split("\t")
                entity_id = splitted_line[0]
                description = splitted_line[1]
                self._entity_descriptions[entity_id] = description

    @staticmethod
    def get_query_by_entity_relations(
        entity_name: str, relations: dict[str, str]
    ) -> str:
        query = ""
        for relation, answer in relations.items():
            query += f"{entity_name} {relation} {answer}. "
        return query.strip()

    @lru_cache(maxsize=512)
    def find_entity_by_name(self, name: str, candidates: list[str], query: str) -> Entity:
        """
        Find entity by name using embeddings
        """
        normalized_name = name.lower().strip()
        normalized_query = query.lower().strip()
        self.logger.debug("Query: %s", normalized_query)

        if not candidates:
            raise ValueError(f"Entity {normalized_name} not found")

        result = process.extract(
            normalized_name,
            candidates,
            scorer=fuzz.token_ratio,
            score_cutoff=(1 - self.norm_lev_threshold) * 100,
            limit=20,
        )

        if result is None:
            self.logger.debug("No aliases after fuzzy search found.")
            raise ValueError(f"Entity {normalized_name} not found")
        self.logger.debug("Found %d aliases for entity %s", len(result), normalized_name)

        matched_descriptions = []
        matched_description_indx_to_entity_id = []
        for alias, _, _ in result:
            entity_id = self.alias_to_entities[alias]
            if entity_id in self._entity_descriptions:
                description = self._entity_descriptions[entity_id].strip()
                if len(description) > 100:
                    description = description[:100].strip()
                if description not in matched_descriptions:
                    matched_descriptions.append(description)
                    matched_description_indx_to_entity_id.append(entity_id)

        if len(matched_descriptions) == 0:
            self.logger.warning("No descriptions found for entity %s.", normalized_name)
            raise ValueError(f"Entity {normalized_name} not found")

        self.logger.debug("Matched descriptions for entity %s: %s", normalized_name, matched_descriptions)
        self.logger.debug("Generating embeddings for matched aliases...")
        embeddings = get_embedding_batch(
            [query.lower().strip()] + matched_descriptions,
            self.embeddings_tokenizer,
            self.embeddings_model,
            normalize=True,
            max_length=16,
        )  # [len(matched_descriptions) + 1, embedding_dim]
        if embeddings is None:
            raise ValueError(f"Failed to generate embeddings for entity {normalized_name}")
        query_embedding = embeddings[0]
        embeddings = embeddings[1:]
        distances = cosine_similarity_normalized_embeddings(
            query_embedding, embeddings
        )  # [len(matched_descriptions), ]
        self.logger.debug("Distances: %s", distances)
        index_of_closest_embedding = distances.index(max(distances))  # int
        closest_entity = matched_description_indx_to_entity_id[
            index_of_closest_embedding
        ]

        del query_embedding, embeddings, distances

        return Entity(EntityID(closest_entity), self.entity_to_aliases[closest_entity])

    def get_entity_candidates(self, entity_name: str) -> tuple[str]:
        normalized_name = entity_name.lower().strip()
        # Используем префиксный индекс для ускорения поиска
        prefix = normalized_name[:3] if len(normalized_name) >= 3 else normalized_name
        candidates = self.entity_aliases_prefix_index.get(prefix, [])

        # Если кандидатов слишком мало, расширяем поиск на соседние префиксы
        if len(candidates) < 100 and len(prefix) >= 2:
            # Добавляем кандидатов с похожими префиксами (первые 2 символа)
            prefix_2 = prefix[:2]
            for key in self.entity_aliases_prefix_index.keys():
                if key.startswith(prefix_2) and key != prefix:
                    candidates.extend(self.entity_aliases_prefix_index[key])

        return tuple(candidates)

    def parse_graph_structure(
        self, triplets_dict: defaultdict[str, dict[str, str]]
    ) -> defaultdict[Entity, dict[Relation, Entity]]:
        graph_structure = defaultdict(dict)
        for subject, relations in triplets_dict.items():
            try:
                entity_candidates = self.get_entity_candidates(subject)
                query = GraphCreatorWithEmbeddings.get_query_by_entity_relations(
                    subject, relations
                )
                subject_entity = self.find_entity_by_name(subject, entity_candidates, query)
            except ValueError as _:
                self.logger.warning(
                    "Skip triplet (%s, %s) because subject is not found in wikidataset", subject, relations
                )
                continue
            for relation, answer in relations.items():
                try:
                    entity_candidates = self.get_entity_candidates(answer)
                    query = GraphCreatorWithEmbeddings.get_query_by_entity_relations(
                        answer, {relation: answer}
                    )
                    answer_entity = self.find_entity_by_name(answer, entity_candidates, query)
                except ValueError as _:
                    self.logger.warning(
                        "Skip triplet (%s, %s, %s) because answer is not found in wikidataset", subject, relation, answer
                    )
                    continue
                try:
                    relation_candidates = self.get_relation_candidates(subject_entity, answer_entity)
                    relation_entity = self.find_relation_by_name(
                        relation, relation_candidates
                    )
                except ValueError as _:
                    self.logger.warning(
                        "Skip triplet (%s, %s, %s) because relation is not found", subject, relation, answer
                    )
                    continue
                graph_structure[subject_entity][relation_entity] = answer_entity
        return graph_structure
