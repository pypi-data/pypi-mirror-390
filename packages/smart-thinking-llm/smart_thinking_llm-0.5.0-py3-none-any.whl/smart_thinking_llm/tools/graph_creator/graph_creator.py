import logging
from collections import defaultdict
from functools import lru_cache

import openai
from dotenv import load_dotenv
from pathlib import Path
from rapidfuzz import process, fuzz
from typing import Literal

from smart_thinking_llm.datasets.data_classes import (
    Entity,
    EntityID,
    Relation,
    RelationID,
)
from smart_thinking_llm.tools.graph_creator.base import GraphCreatorBase

load_dotenv()


class GraphCreator(GraphCreatorBase):
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

    @lru_cache(maxsize=512)
    def find_entity_by_name(self, name: str, candidates: tuple[str]) -> Entity:
        normalized_name = name.lower().strip()

        result = process.extractOne(
            normalized_name,
            candidates,
            scorer=fuzz.token_ratio,
            score_cutoff=(1 - self.norm_lev_threshold) * 100,
        )

        if result is None:
            raise ValueError(f"Entity {name} not found")

        matched_alias, _, _ = result

        entity_id = self.alias_to_entities[matched_alias]
        entity = Entity(EntityID(entity_id), self.entity_to_aliases[entity_id])
        return entity

    @lru_cache(maxsize=64)
    def find_relation_by_name(self, name: str, candidates: tuple[str]) -> Relation:
        self.logger.debug("Searching for relation %s in %d candidates", name, len(candidates))
        normalized_name = name.lower().strip()

        result = process.extractOne(
            normalized_name,
            candidates,
            scorer=fuzz.token_ratio,
        )
        if result is None:
            raise ValueError(f"Relation {name} not found")

        matched_alias, _, _ = result

        relation_id = self.alias_to_relation[matched_alias]
        relation = Relation(
            RelationID(relation_id), self.relation_to_aliases[relation_id]
        )
        return relation

    def get_entity_candidates(self,) -> tuple[str]:
        return tuple(self.entity_aliases)

    def parse_graph_structure(
        self, triplets_dict: defaultdict[str, dict[str, str]]
    ) -> defaultdict[Entity, dict[Relation, Entity]]:
        graph_structure = defaultdict(dict)
        for subject, relations in triplets_dict.items():
            try:
                entity_candidates = self.get_entity_candidates(subject)
                subject_entity = self.find_entity_by_name(subject, entity_candidates)
            except ValueError as _:
                self.logger.warning(
                    "Skip triplet (%s, %s) because subject is not found in wikidataset", subject, relations
                )
                continue
            for relation, answer in relations.items():
                try:
                    entity_candidates = self.get_entity_candidates(answer)
                    answer_entity = self.find_entity_by_name(answer, entity_candidates)
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
