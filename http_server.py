# basic import 
from mcp.server.fastmcp import FastMCP
import math

from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn


# instantiate an MCP server client
mcp = FastMCP('Hello World')

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return int(a + b)


# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return int(a - b)


# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return int(a * b)


#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    return float(a / b)


# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    return int(a ** b)


# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    return float(a ** 0.5)


# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    return float(a ** (1/3))


# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    return int(math.factorial(a))


# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    return float(math.log(a))


# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    return int(a % b)


# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    return float(math.sin(a))


@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    return float(math.cos(a))


# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    return float(math.tan(a))


# DEFINE RESOURCES
@mcp.resource('list://resources')
def list_resources() -> dict:
    """Return a list of all available resources in this server."""
    return {
        'resources': [
            {
                'uri': 'hello://world',
                'name': 'Hello World Message',
                'description': 'A simple hello world message',
                'mime_type': 'text/plain',
            },
            {
                'uri': 'greeting://{name}',
                'name': 'Personalized Greeting',
                'descriptiona': 'A personalized greeting message',
                'mime_type': 'text/plain',
                'parameters': [
                    {
                        'name': 'name',
                        'description': 'The name of the person to greet',
                        'type': 'string',
                        'required': True,
                    }
                ],
            },
        ]
    }


@mcp.resource(
        'greeting://{name}',  # URL
        # name
        # description
        # mime_type
    )
def get_greeting(name: str) -> str:
    """A personalized greeting for the given name."""
    return f'Hello {name}! Welcome to MCP.'


@mcp.resource('hello://world')
def hello_world() -> str:
    """A simple hello world message."""
    return 'Hello, World!'


@mcp.prompt()
def review_code(code: str) -> str:
    """Review code"""
    return f'Please review this code:\n\n{code}'


STDIO_SERVER = False
if __name__ == '__main__':
    if STDIO_SERVER:
        mcp.run(transport='stdio')
    else:  # http server
        app = Starlette(
            debug=False,
            routes=[
                Mount('/', app=mcp.sse_app()),
            ],
        )
        uvicorn.run(app, host='0.0.0.0', port=8080)
