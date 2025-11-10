import logging
from collections import defaultdict
from functools import lru_cache
from tqdm import tqdm

import openai
from dotenv import load_dotenv
from pathlib import Path
from typing import Literal
from rapidfuzz import process, fuzz

from smart_thinking_llm.datasets.data_classes import (
    Entity,
    EntityID,
    Relation,
)
from smart_thinking_llm.tools.graph_creator.graph_creator_with_embeddings import GraphCreatorWithEmbeddings
from smart_thinking_llm.utils import (
    make_openai_request,
)
from smart_thinking_llm.tools.graph_creator.graph_creator import GraphCreator

load_dotenv()


class GraphCreatorWithLLMSelector(GraphCreator):
    def __init__(
        self,
        entity_aliases_filepath: Path,
        relation_aliases_filepath: Path,
        dataset_filepath: Path,
        triplets_prompt_filepath: Path,
        openai_client: openai.OpenAI,
        entity_description_filepath: Path,
        llm_selector_prompt_filepath: Path,
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
        llm_selector_model: Literal[
            "gpt-4.1-2025-04-14",
            "gpt-4.1-mini-2025-04-14",
            "gpt-4.1-nano-2025-04-14",
        ] = "gpt-4.1-nano-2025-04-14",
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
        self.llm_selector_model = llm_selector_model
        with open(llm_selector_prompt_filepath, mode="r", encoding="utf-8") as f:
            self.llm_selector_prompt = f.read()

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

    @lru_cache(maxsize=512)
    def find_entity_by_name(self, name: str, candidates: list[str], query: str) -> Entity:
        """
        Find entity by name using llm selector
        """
        normalized_name = name.lower().strip()
        normalized_query = query.lower().strip()
        self.logger.debug("Searching for entity %s in aliases", normalized_name)
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
            raise ValueError(f"Entity {normalized_name} not found")
        self.logger.debug("Found %d aliases for entity %s", len(result), normalized_name)

        matched_descriptions = set()
        for alias, _, _ in result:
            entity_id = self.alias_to_entities[alias]
            if entity_id in self._entity_descriptions:
                matched_descriptions.add(self._entity_descriptions[entity_id])
        matched_descriptions = list(matched_descriptions)

        self.logger.debug(
            "Matched descriptions for entity %s: %s", normalized_name, matched_descriptions
        )
        self.logger.debug("Selecting entity by name using llm selector...")
        model_select = make_openai_request(
            self.openai_client,
            self.llm_selector_model,
            self.llm_selector_prompt % (normalized_query, matched_descriptions),
            self.logger,
        )
        model_select = model_select.strip().lower()
        self.logger.debug("Model select: %s", model_select)

        closest_alias = result[int(model_select)][0]
        self.logger.debug("Closest alias: %s", closest_alias)
        closest_entity = self.alias_to_entities[closest_alias]
        self.logger.debug("Closest entity: %s", closest_entity)

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
        self.logger.debug("Found %d candidates for entity %s", len(candidates), normalized_name)
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