from camel.storages import Neo4jGraph
from camel.loaders import UnstructuredIO
from camel.agents import KnowledgeGraphAgent

def knowledge_graph_builder(text_input: str) -> None:
    r"""Build and store a knowledge graph from the provided text.

    This function processes the input text to create and extract nodes and relationships,
    which are then added to a Neo4j database as a knowledge graph.

    Args:
        text_input (str): The input text from which the knowledge graph is to be constructed.

    Returns:
        graph_elements: The generated graph element from knowlegde graph agent.
    """

    # Set Neo4j instance
    n4j = Neo4jGraph(
        url="neo4j+s://653e33c2.databases.neo4j.io",
        username="neo4j",
        password="ZQzOnxmr2mzWa-t5F9op-DwaNStb24KAt0EgFps0H7s",
    )

    # Initialize instances
    uio = UnstructuredIO()
    kg_agent = KnowledgeGraphAgent(model=mistral_large_2)

    # Create an element from the provided text
    element_example = uio.create_element_from_text(text=text_input, element_id="001")

    # Extract nodes and relationships using the Knowledge Graph Agent
    graph_elements = kg_agent.run(element_example, parse_graph_elements=True)

    # Add the extracted graph elements to the Neo4j database
    n4j.add_graph_elements(graph_elements=[graph_elements])

    return graph_elements