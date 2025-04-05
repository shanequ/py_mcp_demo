"""
LLM App 

This is a LC agent that can use tools/resources and prompt from a MCP Server. 

Errors:

enum ErrorCode {
  // Standard JSON-RPC error codes
  ParseError = -32700,
  InvalidRequest = -32600,
  MethodNotFound = -32601,
  InvalidParams = -32602,
  InternalError = -32603
}


Read resource returns:

{
  contents: [
    {
      uri: string;        // The URI of the resource
      mimeType?: string;  // Optional MIME type

      // One of:
      text?: string;      // For text resources
      blob?: string;      // For binary resources (base64 encoded)
    }
  ]
}

"""


import asyncio
import json
import pprint

from contextlib import asynccontextmanager
from typing import Annotated, Any, List, AsyncGenerator, Tuple
from typing_extensions import TypedDict

from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langgraph.prebuilt import create_react_agent

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.shared.session import BaseSession

from dotenv import load_dotenv
load_dotenv()


class GraphState(TypedDict):
    messages: Annotated[List, add_messages]
    private_data: Any


def print_items(name: str, result: Any) -> None:
    """Print items with formatting.

    Args:
        name: Category name (tools/resources/prompts)
        result: Result object containing items list
    """
    print('', f'Available {name}:', sep='\n')
    items = getattr(result, name)
    if items:
        for item in items:
            print(' *', item)
    else:
        print('No items available')


async def stream_graph_updates(user_input: str, graph: Any):
    async for event in graph.astream(
            {'messages': [{'role': 'user', 'content': user_input}]}):
        for value in event.values():
            print('Assistant: ', value['messages'][-1].content)


#
# For version 3.12, Generator typing must include both yield and send types
# FOr version 3.13+, send type is optional.
#
@asynccontextmanager
async def connect_mcp_server(url: str) -> AsyncGenerator[BaseSession,  None]:
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # print('Connected to MCP server at', url)
            # print_items('tools', (await session.list_tools()))
            # print_items('resources', (await session.list_resources()))
            # print_items('prompts', (await session.list_prompts()))
            yield session


async def main():
    llm = ChatOpenAI(model='gpt-4o', temperature=0.2)

    # MCP server URL
    url = 'http://127.0.0.1:8080/sse'

    async with connect_mcp_server(url) as session:
        tools = await load_mcp_tools(session)

        graph = create_react_agent(llm, tools=tools)

        # list resources and prompts
        resources, prompts = await asyncio.gather(
            session.list_resources(),
            session.list_prompts()
        )

        # print(resources, prompts, sep='\n', end='\n----\n')
        # print()

        data = await session.read_resource('list://resources')
        pprint.pprint(json.loads(data.contents[0].text)['resources'])

        print()

        data = await session.read_resource('greeting://Shane')
        pprint.pp(data.contents[0].text)

        print('\n\n')
        print('Resource Templates:')
        resource_temp = await session.list_resource_templates()
        pprint.pp(resource_temp.resourceTemplates)

        while True:
            try:
                user_input = input('User: ')
                if user_input.lower() in ['q', 'quit', 'exit']:
                    print('Bye!')
                    break
                await stream_graph_updates(user_input, graph)
            except:
                user_input = 'What do you know about LangGraph?'
                print('User: ', user_input)
                await stream_graph_updates(user_input, graph)
                break


if __name__ == '__main__':
     asyncio.run(main())
