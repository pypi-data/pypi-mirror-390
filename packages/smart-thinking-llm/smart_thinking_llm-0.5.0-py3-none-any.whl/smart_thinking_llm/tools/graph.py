from collections import defaultdict

import networkx as nx
from dotenv import load_dotenv

from smart_thinking_llm.datasets.data_classes import (
    Entity,
    Relation,
)

load_dotenv()


class Graph:
    def __init__(
        self, entity_to_entity_struct: defaultdict[Entity, dict[Relation, Entity]]
    ):
        self.entity_to_entity_struct = entity_to_entity_struct
        self.graph = nx.DiGraph()
        for entity_1, relations in entity_to_entity_struct.items():
            self.graph.add_node(entity_1, label=entity_1.id._id)
            for relation, entity_2 in relations.items():
                if entity_2 not in self.graph:
                    self.graph.add_node(entity_2, label=entity_2.id._id)
                self.graph.add_edge(entity_1, entity_2, label=relation.id._id)

    @staticmethod
    def node_match(n1, n2):
        return n1["label"] == n2["label"]

    @staticmethod
    def edge_match(e1, e2):
        return e1["label"] == e2["label"]

    def compare_to(
        self,
        other: "Graph",
        node_del_cost: float = 1.0,
        node_ins_cost: float = 1.0,
        edge_del_cost: float = 1.0,
        edge_ins_cost: float = 1.0,
    ) -> float:
        # TODO: add edge_subst_cost and node_subst_cost
        node_del = lambda _: node_del_cost
        node_ins = lambda _: node_ins_cost
        edge_del = lambda _: edge_del_cost
        edge_ins = lambda _: edge_ins_cost
        return nx.graph_edit_distance(
            self.graph,
            other.graph,
            node_match=self.node_match,
            edge_match=self.edge_match,
            node_del_cost=node_del,
            node_ins_cost=node_ins,
            edge_del_cost=edge_del,
            edge_ins_cost=edge_ins,
        )

    def __str__(self) -> str:
        if not self.entity_to_entity_struct:
            return "Graph is empty."

        def get_repr(item: object) -> str:
            """Helper для читаемого представления Entity/Relation"""
            aliases = getattr(item, "aliases", [])
            item_id = getattr(item, "id", "")
            name = aliases[0] if aliases else "N/A"
            return f"{name} ({item_id})"

        output_lines = []

        # Находим корневые узлы (те, что не являются объектами ни одной связи)
        all_subjects = set(self.entity_to_entity_struct.keys())
        all_objects = {
            obj
            for relations_dict in self.entity_to_entity_struct.values()
            for obj in relations_dict.values()
        }
        root_nodes = sorted(
            [s for s in all_subjects if s not in all_objects],
            key=lambda x: str(x.id),
        )

        # Узлы которые и субъекты и объекты (могут быть часть циклов)
        other_nodes = sorted(
            [s for s in all_subjects if s in all_objects],
            key=lambda x: str(x.id),
        )

        visited_globally = set()

        def build_tree(
            node: Entity, prefix: str, is_root: bool, visited_in_path: set[Entity]
        ):
            """Рекурсивное построение дерева с отслеживанием пути для циклов"""

            if is_root:
                output_lines.append(f"[{get_repr(node)}]")

            # Проверяем цикл: если узел уже в текущем пути обхода
            if node in visited_in_path:
                return

            visited_globally.add(node)
            visited_in_path.add(node)

            # Получаем дочерние связи
            if node not in self.entity_to_entity_struct:
                return

            relations = self.entity_to_entity_struct[node]
            children = sorted(list(relations.items()), key=lambda x: str(x[0].id))

            for i, (relation, obj) in enumerate(children):
                is_last = i == len(children) - 1
                connector = "└──" if is_last else "├──"

                # Проверяем, создаст ли этот объект цикл
                if obj in visited_in_path:
                    output_lines.append(
                        f"{prefix}{connector} {get_repr(relation)}: [{get_repr(obj)}] ⟲ (cycle)"
                    )
                else:
                    output_lines.append(
                        f"{prefix}{connector} {get_repr(relation)}: [{get_repr(obj)}]"
                    )

                    # Рекурсивно обрабатываем только Entity
                    if isinstance(obj, Entity):
                        new_prefix = prefix + ("    " if is_last else "│   ")
                        build_tree(obj, new_prefix, False, visited_in_path.copy())

            visited_in_path.remove(node)

        # Обрабатываем все компоненты графа
        for node in root_nodes + other_nodes:
            if node not in visited_globally:
                build_tree(node, "", True, set())
                output_lines.append("")

        return "\n".join(output_lines).rstrip()
