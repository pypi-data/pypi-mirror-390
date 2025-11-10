import logging
from .AGEGraph import AGEGraph
from mem0.graphs.utils import EXTRACT_RELATIONS_PROMPT, get_delete_messages
from mem0.utils.factory import EmbedderFactory, LlmFactory
from mem0.memory.utils import format_entities

logger = logging.getLogger(__name__)

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    raise ImportError("rank_bm25 is not installed. Please install it using pip install rank-bm25")

from mem0.graphs.tools import (
    DELETE_MEMORY_STRUCT_TOOL_GRAPH,
    DELETE_MEMORY_TOOL_GRAPH,
    EXTRACT_ENTITIES_STRUCT_TOOL,
    EXTRACT_ENTITIES_TOOL,
    RELATIONS_STRUCT_TOOL,
    RELATIONS_TOOL,
)

class MemoryGraph:
    def __init__(self, config):
        self.config = config

        self.graph = None
        dbconf = {
                "database": self.config.graph_store.config.database,
                "user":self.config.graph_store.config.username,
                "host":self.config.graph_store.config.url,
                "port":self.config.graph_store.config.port,
                "password":self.config.graph_store.config.password,
                }
        self.graphname = self.config.graph_store.config.graphname
        self.graph = AGEGraph(graph_name = self.config.graph_store.config.graphname, conf = dbconf)

        if not self.graph:
            raise ValueError("Unable to create a  client: missing 'endpoint' in config")

        self.node_label = ":__Entity__"
        self.node_table = '__Entity__'

        self.graph._check_label_vertex(self.node_table, self.graphname)
        
        self.embedding_model = EmbedderFactory.create(
            self.config.embedder.provider, self.config.embedder.config, self.config.vector_store.config
        )

        self.llm_provider = "bailian_structured"
        if self.config.llm.provider:
            self.llm_provider = self.config.llm.provider
        if self.config.graph_store.llm:
            self.llm_provider = self.config.graph_store.llm.provider

        self.llm = LlmFactory.create(self.llm_provider, self.config.llm.config)
        self.user_id = None
        self.threshold = 0.7
        self.embedding_col = "embedding"
        
    def add(self, data, filters):
        """
        Adds data to the graph.

        Args:
            data (str): The data to add to the graph.
            filters (dict): A dictionary containing filters to be applied during the addition.
        """
        entity_type_map = self._retrieve_nodes_from_data(data, filters)
        to_be_added = self._establish_nodes_relations_from_data(data, filters, entity_type_map)
        search_output = self._search_graph_db(node_list=list(entity_type_map.keys()), filters=filters)
        to_be_deleted = self._get_delete_entities_from_search_output(search_output, data, filters)

        deleted_entities = self._delete_entities(to_be_deleted, filters)
        added_entities = self._add_entities(to_be_added, filters, entity_type_map)

        return {"deleted_entities": deleted_entities, "added_entities": added_entities}

    def search(self, query, filters, limit=100):
        """
        Search for memories and related graph data.

        Args:
            query (str): Query to search for.
            filters (dict): A dictionary containing filters to be applied during the search.
            limit (int): The maximum number of nodes and relationships to retrieve. Defaults to 100.

        Returns:
            dict: A dictionary containing:
                - "contexts": List of search results from the base data store.
                - "entities": List of related graph data based on the query.
        """
        entity_type_map = self._retrieve_nodes_from_data(query, filters)
        search_output = self._search_graph_db(node_list=list(entity_type_map.keys()), filters=filters)

        if not search_output:
            return []

        search_outputs_sequence = [
            [item["source"], item["relationship"], item["destination"]] for item in search_output
        ]
        bm25 = BM25Okapi(search_outputs_sequence)

        tokenized_query = query.split(" ")
        reranked_results = bm25.get_top_n(tokenized_query, search_outputs_sequence, n=5)

        search_results = []
        for item in reranked_results:
            search_results.append({"source": item[0], "relationship": item[1], "destination": item[2]})

        logger.info(f"Returned {len(search_results)} search results")

        return search_results

    def delete_all(self, filters):
        if filters.get("agent_id"):
            cypher = f"""
            MATCH (n {self.node_label})
            WHERE n.agent_id = '{{agent_id}}' AND n.user_id = '{{user_id}}'
            DETACH DELETE n
            """
            params = {"user_id": filters["user_id"], "agent_id": filters["agent_id"]}
        else:
            cypher = f"""
            MATCH (n {self.node_label})
            WHERE n.user_id = '{{user_id}}'
            DETACH DELETE n
            """
            params = {"user_id": filters["user_id"]}
        self.graph.query(cypher, params=params)

    def get_all(self, filters, limit=100):
        """
        Retrieves all nodes and relationships from the graph database based on optional filtering criteria.
         Args:
            filters (dict): A dictionary containing filters to be applied during the retrieval.
            limit (int): The maximum number of nodes and relationships to retrieve. Defaults to 100.
        Returns:
            list: A list of dictionaries, each containing:
                - 'contexts': The base data store response for each memory.
                - 'entities': A list of strings representing the nodes and relationships
        """
        agent_filter = ""
        params = {"user_id": filters["user_id"], "limit": limit}
        if filters.get("agent_id"):
            agent_filter = "AND n.agent_id = '{{agent_id}}' AND m.agent_id = '{{agent_id}}' "
            params["agent_id"] = filters["agent_id"]

        query = f"""
        MATCH (n {self.node_label})-[r]->(m {self.node_label})
        WHERE n.user_id = '{{user_id}}' AND m.user_id = '{{user_id}}' {agent_filter}
        RETURN n.name AS source, type(r) AS relationship, m.name AS target
        LIMIT {{limit}}
        """
        results = self.graph.query(query, params=params)

        final_results = []
        for result in results:
            final_results.append(
                {
                    "source": result["source"],
                    "relationship": result["relationship"],
                    "target": result["target"],
                }
            )

        logger.info(f"Retrieved {len(final_results)} relationships")

        return final_results

    def _retrieve_nodes_from_data(self, data, filters):
        """Extracts all the entities mentioned in the query."""
        _tools = [EXTRACT_ENTITIES_TOOL]
        if self.llm_provider in ["azure_openai_structured", "openai_structured", "bailian_structured"]:
            _tools = [EXTRACT_ENTITIES_STRUCT_TOOL]
        search_results = self.llm.generate_response(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a smart assistant who understands entities and their types in a given text. If user message contains self reference such as 'I', 'me', 'my' etc. then use {filters['user_id']} as the source entity. Extract all the entities from the text. ***DO NOT*** answer the question itself if the given text is a question.",
                },
                {"role": "user", "content": data},
            ],
            tools=_tools,
        )

        entity_type_map = {}

        try:
            for tool_call in search_results["tool_calls"]:
                if tool_call["name"] != "extract_entities":
                    continue
                for item in tool_call["arguments"]["entities"]:
                    entity_type_map[item["entity"]] = item["entity_type"]
        except Exception as e:
            logger.exception(
                f"Error in search tool: {e}, llm_provider={self.llm_provider}, search_results={search_results}"
            )

        entity_type_map = {k.lower().replace(" ", "_"): v.lower().replace(" ", "_") for k, v in entity_type_map.items()}
        logger.debug(f"Entity type map: {entity_type_map}\n search_results={search_results}")
        return entity_type_map

    def _establish_nodes_relations_from_data(self, data, filters, entity_type_map):
        """Establish relations among the extracted nodes."""

        # Compose user identification string for prompt
        user_identity = f"user_id: {filters['user_id']}"
        if filters.get("agent_id"):
            user_identity += f", agent_id: {filters['agent_id']}"

        if self.config.graph_store.custom_prompt:
            system_content = EXTRACT_RELATIONS_PROMPT.replace("USER_ID", user_identity)
            # Add the custom prompt line if configured
            system_content = system_content.replace("CUSTOM_PROMPT", f"4. {self.config.graph_store.custom_prompt}")
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": data},
            ]
        else:
            system_content = EXTRACT_RELATIONS_PROMPT.replace("USER_ID", user_identity)
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"List of entities: {list(entity_type_map.keys())}. \n\nText: {data}"},
            ]

        _tools = [RELATIONS_TOOL]
        if self.llm_provider in ["azure_openai_structured", "openai_structured", "bailian_structured"]:
            _tools = [RELATIONS_STRUCT_TOOL]

        extracted_entities = self.llm.generate_response(
            messages=messages,
            tools=_tools,
        )

        entities = []
        if extracted_entities.get("tool_calls"):
            entities = extracted_entities["tool_calls"][0].get("arguments", {}).get("entities", [])

        entities = self._remove_spaces_from_entities(entities)
        logger.debug(f"Extracted entities: {entities}")
        return entities

    def _search_graph_db(self, node_list, filters, limit=100):
        """Search similar nodes among and their respective incoming and outgoing relations."""
        result_relations = []
        agent_filter = ""
        if filters.get("agent_id"):
            agent_filter = f"""
                AND ag_catalog.agtype_access_operator(properties, '"agent_id"'::agtype) = '"{{agent_id}}"'::agtype 
                """
        for node in node_list:
            n_embedding = self.embedding_model.embed(node)

            cypher_query = f"""
                with t as (
                SELECT id,(1 - ({self.embedding_col} <=> '{{n_embedding}}')) as similarity
                FROM {self.graphname}."{self.node_table}"
                WHERE {self.embedding_col} IS NOT NULL AND ag_catalog.agtype_access_operator(properties, '"user_id"'::agtype) = '"{{user_id}}"'::agtype {agent_filter}
                ORDER BY similarity DESC
                LIMIT {{limit}}
                ), 
                tmp as (
                SELECT id, similarity
                FROM t
                WHERE similarity > {{threshold}}
                ),
                tmp2 as (
                SELECT ag_catalog.agtype_access_operator(vertex.properties, '"name"'::agtype) as source, 
                    edge.start_id as source_id,
                    ag_catalog._label_name({self.graph.graphid}::oid,edge.id) as relationship,
                    edge.id as relation_id,
                    ag_catalog.agtype_access_operator(vertex2.properties, '"name"'::agtype) as destination, 
                    edge.end_id as destination_id,
                    tmp.similarity
                FROM {self.graphname}._ag_label_edge edge,
                     {self.graphname}._ag_label_vertex vertex,
                     {self.graphname}._ag_label_vertex vertex2,
                     tmp
                WHERE edge.start_id = tmp.id
                      AND edge.start_id = vertex.id
                      AND edge.end_id = vertex2.id
                UNION ALL
                SELECT ag_catalog.agtype_access_operator(vertex.properties, '"name"'::agtype) as source, 
                    edge.start_id as source_id,
                    ag_catalog._label_name({self.graph.graphid}::oid,edge.id) as relationship,
                    edge.id as relation_id,
                    ag_catalog.agtype_access_operator(vertex2.properties, '"name"'::agtype) as destination, 
                    edge.end_id as destination_id,
                    tmp.similarity
                FROM {self.graphname}._ag_label_edge edge,
                     {self.graphname}._ag_label_vertex vertex,
                     {self.graphname}._ag_label_vertex vertex2,
                     tmp
                WHERE edge.end_id = tmp.id
                      AND edge.start_id = vertex.id
                      AND edge.end_id = vertex2.id
                )
                SELECT * FROM tmp2
                ORDER BY similarity DESC
                LIMIT {{limit}}
            """
            
            params = {
                "n_embedding": n_embedding,
                "threshold": self.threshold,
                "user_id": filters["user_id"],
                "limit": limit,
            }
            if filters.get("agent_id"):
                params["agent_id"] = filters["agent_id"]
                
            ans = self.graph._query(cypher_query, params=params)            
            result_relations.extend(ans)

        return result_relations

    def _get_delete_entities_from_search_output(self, search_output, data, filters):
        """Get the entities to be deleted from the search output."""
        search_output_string = format_entities(search_output)

        # Compose user identification string for prompt
        user_identity = f"user_id: {filters['user_id']}"
        if filters.get("agent_id"):
            user_identity += f", agent_id: {filters['agent_id']}"

        system_prompt, user_prompt = get_delete_messages(search_output_string, data, user_identity)

        _tools = [DELETE_MEMORY_TOOL_GRAPH]
        if self.llm_provider in ["azure_openai_structured", "openai_structured", "bailian_structured"]:
            _tools = [
                DELETE_MEMORY_STRUCT_TOOL_GRAPH,
            ]

        memory_updates = self.llm.generate_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            tools=_tools,
        )

        to_be_deleted = []
        for item in memory_updates.get("tool_calls", []):
            if item.get("name") == "delete_graph_memory":
                to_be_deleted.append(item.get("arguments"))
        # Clean entities formatting
        to_be_deleted = self._remove_spaces_from_entities(to_be_deleted)
        logger.debug(f"Deleted relationships: {to_be_deleted}")
        return to_be_deleted

    def _delete_entities(self, to_be_deleted, filters):
        """Delete the entities from the graph."""
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id", None)
        results = []

        for item in to_be_deleted:
            source = item["source"]
            destination = item["destination"]
            relationship = item["relationship"]

            # Build the agent filter for the query
            agent_filter = ""
            params = {
                "source_name": source,
                "dest_name": destination,
                "user_id": user_id,
            }

            if agent_id:
                agent_filter = f"""
                    AND n.agent_id = '{{agent_id}}' AND m.agent_id = '{{agent_id}}'
                """
                params["agent_id"] = agent_id

            # Delete the specific relationship between nodes
            cypher = f"""
            MATCH (n {self.node_label})-[r:{relationship}]->(m {self.node_label})
            WHERE n.name = '{{source_name}}' AND n.user_id = '{{user_id}}' 
                  AND m.name = '{{dest_name}}' AND m.user_id = '{{user_id}}' {agent_filter}
            DELETE r
            RETURN 
                n.name AS source,
                m.name AS target,
                type(r) AS relationship
            """

            result = self.graph.query(cypher, params=params)
            results.append(result)

        return results

    def _add_entities(self, to_be_added, filters, entity_type_map):
        """Add the new entities to the graph. Merge the nodes if they already exist."""
        user_id = filters["user_id"]
        agent_id = filters.get("agent_id", None)
        results = []
        for item in to_be_added:
            # entities
            source = item["source"]
            destination = item["destination"]
            relationship = item["relationship"]

            # types
            source_type = entity_type_map.get(source, "__User__")
            source_label = self.node_label if self.node_label else f": {source_type}"
            source_table = source_label.replace(":", "")
            source_extra_set = f""", source: "{source_type}" """ if self.node_label else ""
            destination_type = entity_type_map.get(destination, "__User__")
            destination_label = self.node_label if self.node_label else f": {destination_type}"
            destination_table = destination_label.replace(":", "")
            destination_extra_set = f""", destination: "{destination_type}" """ if self.node_label else ""

            # embeddings
            source_embedding = self.embedding_model.embed(source)
            dest_embedding = self.embedding_model.embed(destination)

            # search for the nodes with the closest embeddings
            source_node_search_result = self._search_source_node(source_embedding, filters, threshold=0.9)
            destination_node_search_result = self._search_destination_node(dest_embedding, filters, threshold=0.9)

            self.graph._check_label_edge(relationship, self.graphname)
            self.graph._check_label_vertex(source_table, self.graphname)
            self.graph._check_label_vertex(destination_table, self.graphname)
            
            # TODO: Create a cypher query and common params for all the cases
            if not destination_node_search_result and source_node_search_result:
                # Build destination MERGE properties
                merge_props = ['name: "{destination_name}"', 'user_id: "{user_id}"']
                if agent_id:
                    merge_props.append('agent_id: "{agent_id}"')

                merge_props_str = ", ".join(merge_props)
                params = {
                    "source_id": source_node_search_result[0]["id"],
                    "destination_name": destination,
                    "destination_embedding": dest_embedding,
                    "user_id": user_id,
                }
                if agent_id:
                    params["agent_id"] = agent_id
                    
                cypher = f"""
                  MATCH (source {source_label} )
                  WHERE Id(source) = '{{source_id}}'
                  SET source.mentions = coalesce(source.mentions, 0) + 1
                  MERGE (destination {destination_label} {{{{ {merge_props_str} {destination_extra_set} }}}})
                  MERGE (source)-[r:{relationship}]->(destination)
                  RETURN source.name AS source, type(r) AS relationship, destination.name AS target,  id(source) as source_id, id(destination) as destination_id, id(r) as relationship_id 
                """

                result = self.graph.query(cypher, params=params)
                
                sql = f"""
                    UPDATE {self.graphname}."{destination_table}"
                    SET properties = age_set_int8_prop(agtype_increase(properties, agtype_build_map('mentions', 1)), 'created', age_timestamp()::bigint),
                        {self.embedding_col} = '{{destination_embedding}}'
                    WHERE id = '{result[0]["destination_id"]}'::graphid;
                    UPDATE {self.graphname}."{relationship}"
                    SET properties = age_set_int8_prop(agtype_increase(properties, agtype_build_map('mentions', 1)), 'created', age_timestamp()::bigint)
                    WHERE id = '{result[0]["relationship_id"]}'::graphid;
                """
                self.graph._query(sql, params=params)

            elif destination_node_search_result and not source_node_search_result:
                # Build source MERGE properties
                merge_props = ['name: "{source_name}"', 'user_id: "{user_id}"']
                if agent_id:
                    merge_props.append('agent_id: "{agent_id}"')
                merge_props_str = ", ".join(merge_props)

                params = {
                    "destination_id": destination_node_search_result[0]["id"],
                    "source_name": source,
                    "source_embedding": source_embedding,
                    "user_id": user_id,
                }
                if agent_id:
                    params["agent_id"] = agent_id
                    
                cypher = f"""
                  MATCH (destination {destination_label})
                  WHERE Id(destination) = '{{destination_id}}'
                  SET destination.mentions = coalesce(destination.mentions, 0) + 1
                  WITH destination
                  MERGE (source {source_label} {{{{ {merge_props_str} {source_extra_set}}}}})
                  WITH source, destination
                  MERGE (source)-[r:{relationship}]->(destination)
                  RETURN source.name AS source, type(r) AS relationship, destination.name AS target, id(source) as source_id, id(destination) as destination_id, id(r) as relationship_id
                """

                result = self.graph.query(cypher, params=params)
                               
                sql = f"""
                    UPDATE {self.graphname}."{source_table}"
                    SET properties = age_set_int8_prop(agtype_increase(properties, agtype_build_map('mentions', 1)), 'created', age_timestamp()::bigint),
                        {self.embedding_col} = '{{source_embedding}}'
                    WHERE id = '{result[0]["source_id"]}'::graphid;
                    UPDATE {self.graphname}."{relationship}"
                    SET properties = age_set_int8_prop(agtype_increase(properties, agtype_build_map('mentions', 1)), 'created', age_timestamp()::bigint)
                    WHERE id = '{result[0]["relationship_id"]}'::graphid;
                """
                self.graph._query(sql, params=params)

            elif source_node_search_result and destination_node_search_result:
                params = {
                    "source_id": source_node_search_result[0]["id"],
                    "destination_id": destination_node_search_result[0]["id"],
                    "user_id": user_id,
                }
                if agent_id:
                    params["agent_id"] = agent_id
                
                cypher = f"""
                    MATCH (source {source_label})
                    WHERE id(source) = '{{source_id}}'
                    SET source.mentions = coalesce(source.mentions, 0) + 1
                    WITH source
                    MATCH (destination {destination_label})
                    WHERE id(destination) = '{{destination_id}}'
                    SET destination.mentions = coalesce(destination.mentions, 0) + 1                    
                    RETURN source.name AS source, '{relationship}' AS relationship, destination.name AS target
                """
                result = self.graph.query(cypher, params=params)                
                
                sql = f"""
                    INSERT INTO {self.graphname}."{relationship}" as e(id, start_id, end_id, properties) 
                    VALUES (_next_graph_id('{self.graphname}', '{relationship}'), '{{source_id}}'::graphid, '{{destination_id}}'::graphid, agtype_build_map('mentions', 1, 'created', age_timestamp(), 'updated', age_timestamp()))
                    ON CONFLICT (start_id, end_id) DO UPDATE
                    SET properties = age_set_int8_prop(agtype_increase(e.properties, agtype_build_map('mentions', 1)), 'updated', age_timestamp()::bigint);
                """
                self.graph._query(sql, params=params)   

            else:
                # Build dynamic MERGE props for both source and destination
                source_props = ['name: "{source_name}"', 'user_id: "{user_id}"']
                dest_props = ['name: "{dest_name}"', 'user_id: "{user_id}"']
                if agent_id:
                    source_props.append('agent_id: "{agent_id}"')
                    dest_props.append('agent_id: "{agent_id}"')
                source_props_str = ", ".join(source_props) 
                dest_props_str = ", ".join(dest_props)  
                          
                params = {
                    "source_name": source,
                    "dest_name": destination,
                    "source_embedding": source_embedding,
                    "dest_embedding": dest_embedding,
                    "user_id": user_id,
                }
                
                if agent_id:
                    params["agent_id"] = agent_id
                    
                cypher = f"""
                MERGE (source {source_label} {{{{ {source_props_str} {source_extra_set} }}}})
                MERGE (destination {destination_label} {{{{ {dest_props_str} {destination_extra_set} }}}})                           
                MERGE (source)-[r:{relationship}]->(destination)
                RETURN source.name AS source, type(r) AS relationship, destination.name AS target,  id(source) as source_id, id(destination) as destination_id, id(r) as relationship_id
                """
                
                result = self.graph.query(cypher, params=params)
                                
                sql = f"""
                    UPDATE {self.graphname}."{source_table}"
                    SET properties = age_set_int8_prop(agtype_increase(properties, agtype_build_map('mentions', 1)), 'created', age_timestamp()::bigint),
                        {self.embedding_col} = '{{source_embedding}}'
                    WHERE id = '{result[0]["source_id"]}'::graphid;
                    UPDATE {self.graphname}."{destination_table}"
                    SET properties = age_set_int8_prop(agtype_increase(properties, agtype_build_map('mentions', 1)), 'created', age_timestamp()::bigint),
                        {self.embedding_col} = '{{dest_embedding}}'
                    WHERE id = '{result[0]["destination_id"]}'::graphid;
                    UPDATE {self.graphname}."{relationship}"
                    SET properties = age_set_int8_prop(agtype_increase(properties, agtype_build_map('mentions', 1)), 'created', age_timestamp()::bigint)
                    WHERE id = '{result[0]["relationship_id"]}'::graphid;
                """
                self.graph._query(sql, params=params)
                
            #cols = ['source', 'relationship', 'target']
            #_result = {k: result[k] for k in cols if k in result}                
            results.append(result)
        return results

    def _remove_spaces_from_entities(self, entity_list):
        for item in entity_list:
            item["source"] = item["source"].lower().replace(" ", "_")
            item["relationship"] = item["relationship"].lower().replace(" ", "_")
            item["destination"] = item["destination"].lower().replace(" ", "_")
        return entity_list

    def _search_source_node(self, source_embedding, filters, threshold=0.9):
        agent_filter = ""
        if filters.get("agent_id"):
            agent_filter = f"""
                AND ag_catalog.agtype_access_operator(properties, '"agent_id"'::agtype) = '"{{agent_id}}"'::agtype
            """

        cypher = f"""
            with t as (
            SELECT id, (1 - ({self.embedding_col} <=> '{{source_embedding}}')) as similarity
            FROM {self.graphname}."{self.node_table}"
            WHERE ag_catalog.agtype_access_operator(properties, '"user_id"'::agtype) = '"{{user_id}}"'::agtype {agent_filter}            
            )
            SELECT id 
            FROM t
            WHERE similarity > {{threshold}}
            ORDER BY similarity DESC
            LIMIT 1;
            """

        params = {
            "source_embedding": source_embedding,
            "user_id": filters["user_id"],
            "threshold": threshold
        }
        if filters.get("agent_id"):
            params["agent_id"] = filters["agent_id"]

        result = self.graph._query(cypher, params=params)
        return result

    def _search_destination_node(self, destination_embedding, filters, threshold=0.9):        
        agent_filter = ""
        if filters.get("agent_id"):
            agent_filter = f"""
                AND ag_catalog.agtype_access_operator(properties, '"agent_id"'::agtype) = '"{{agent_id}}"'::agtype
            """
            
        cypher = f"""
            with t as (
            SELECT id, (1 - ({self.embedding_col} <=> '{{destination_embedding}}')) as similarity
            FROM {self.graphname}."{self.node_table}"
            WHERE ag_catalog.agtype_access_operator(properties, '"user_id"'::agtype) = '"{{user_id}}"'::agtype {agent_filter}
            )
            SELECT id 
            FROM t
            WHERE similarity > {{threshold}}
            ORDER BY similarity DESC
            LIMIT 1;
            """

        params = {
            "destination_embedding": destination_embedding,
            "user_id": filters["user_id"],
            "threshold": threshold
        }
        if filters.get("agent_id"):
            params["agent_id"] = filters["agent_id"]

        result = self.graph._query(cypher, params=params)
        return result

    # Reset is not defined in base.py
    def reset(self):
        """Reset the graph by clearing all nodes and relationships."""
        logger.warning("Clearing graph...")
        cypher_query = """
        MATCH (n) DETACH DELETE n
        """
        return self.graph.query(cypher_query)
