#!/usr/bin/env python3
"""
MCP Server for Logo Generation using stdio transport
This server provides logo generation capabilities using FAL AI with stdio protocol support.
"""

import asyncio
import os
import sys
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from tools.image_gen import generate_image
from tools.background_removal import remove_background
from tools.image_download import download_image_from_url
from tools.image_scaling import scale_image
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the server
server = Server("mcp-logo-gen-server")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources."""
    return []

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific resource."""
    raise ValueError(f"Unsupported resource: {uri}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """List available prompts."""
    return []

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
    """Get a specific prompt."""
    raise ValueError(f"Unknown prompt: {name}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="generate_image",
            description="Generate an image from a text prompt using FAL AI. For best results with logos and icons, use the format: '[subject], 2D flat design, [optional style details], white background'. Example: 'pine tree logo, 2D flat design, minimal geometric style, white background'",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Text prompt to generate the image. Recommended format: '[subject], 2D flat design, [optional style details], white background'",
                        "examples": [
                            "mountain peak logo, 2D flat design, minimalist geometric shapes, white background",
                            "coffee cup icon, 2D flat design, simple line art style, white background",
                            "fox mascot, 2D flat design, modern geometric shapes, white background"
                        ]
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use for generation",
                        "default": "fal-ai/ideogram/v2",
                        "enum": ["fal-ai/ideogram/v2"]
                    },
                    "aspect_ratio": {
                        "type": "string",
                        "description": "The aspect ratio of the generated image",
                        "default": "1:1",
                        "enum": ["10:16", "16:10", "9:16", "16:9", "4:3", "3:4", "1:1", "1:3", "3:1", "3:2", "2:3"]
                    },
                    "expand_prompt": {
                        "type": "boolean",
                        "description": "Whether to expand the prompt with MagicPrompt functionality",
                        "default": True
                    },
                    "style": {
                        "type": "string",
                        "description": "The style of the generated image",
                        "default": "auto",
                        "enum": ["auto", "general", "realistic", "design", "render_3D", "anime"]
                    },
                    "negative_prompt": {
                        "type": "string",
                        "description": "A negative prompt to avoid in the generated image",
                        "default": ""
                    }
                },
                "required": ["prompt"]
            }
        ),
        types.Tool(
            name="remove_background",
            description="Remove background from an image using FAL AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "Input image url"
                    },
                    "sync_mode": {
                        "type": "boolean",
                        "description": "If true, wait for the image to be generated and uploaded before returning",
                        "default": True
                    },
                    "crop_to_bbox": {
                        "type": "boolean",
                        "description": "If true, crop the result to a bounding box around the subject",
                        "default": False
                    }
                },
                "required": ["image_url"]
            }
        ),
        types.Tool(
            name="download_image",
            description="Download an image from a URL and save it locally",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "URL of the image to download"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to save the downloaded image",
                        "default": "downloads"
                    }
                },
                "required": ["image_url"]
            }
        ),
        types.Tool(
            name="scale_image",
            description="Scale an image to multiple sizes while preserving transparency",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to the input image to scale"
                    },
                    "sizes": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "description": "List of [width, height] pairs for desired output sizes",
                        "default": [[32, 32], [128, 128]]
                    }
                },
                "required": ["input_path"]
            }
        )
    ]

class ImageGenToolHandler:
    def validate_prompt(self, prompt: str) -> bool:
        """
        Validate that the prompt is not empty.
        """
        return bool(prompt and prompt.strip())

    async def handle(self, name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent]:
        prompt = arguments.get("prompt")
        if not prompt or not self.validate_prompt(prompt):
            return [types.TextContent(
                type="text", 
                text="Error: Prompt cannot be empty"
            )]
            
        result = await generate_image(
            prompt=prompt,
            model=arguments.get("model", "fal-ai/ideogram/v2"),
            aspect_ratio=arguments.get("aspect_ratio", "1:1"),
            expand_prompt=arguments.get("expand_prompt", True),
            style=arguments.get("style", "auto"),
            negative_prompt=arguments.get("negative_prompt", "")
        )
        if result.startswith("http"):
            return [types.TextContent(type="text", text=f"Generated image URL: {result}")]
        return [types.TextContent(type="text", text=result)]

class BackgroundRemovalToolHandler:
    async def handle(self, name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent]:
        result = await remove_background(
            arguments.get("image_url"),
            arguments.get("sync_mode", True),
            arguments.get("crop_to_bbox", False)
        )
        if result.startswith("http"):
            return [types.TextContent(type="text", text=f"Background removed image URL: {result}")]
        return [types.TextContent(type="text", text=result)]

class ImageDownloadToolHandler:
    async def handle(self, name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent]:
        result = await download_image_from_url(
            arguments.get("image_url"),
            arguments.get("output_dir", "downloads")
        )
        return [types.TextContent(type="text", text=result)]

class ImageScalingToolHandler:
    async def handle(self, name: str, arguments: dict | None) -> list[types.TextContent | types.ImageContent]:
        result = await scale_image(
            arguments.get("input_path"),
            arguments.get("sizes", [(32, 32), (128, 128)])
        )
        return [types.TextContent(type="text", text=result)]

tool_handlers = {
    "generate_image": ImageGenToolHandler(),
    "remove_background": BackgroundRemovalToolHandler(),
    "download_image": ImageDownloadToolHandler(),
    "scale_image": ImageScalingToolHandler()
}

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent]:
    """Handle tool execution requests."""
    if name in tool_handlers:
        return await tool_handlers[name].handle(name, arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Ensure FAL_KEY is set
    fal_key = os.getenv("FAL_KEY")
    if not fal_key:
        fal_key = os.getenv("FAL_API_KEY")
        if not fal_key:
            print("Error: Neither FAL_KEY nor FAL_API_KEY environment variables are set", file=sys.stderr)
            sys.exit(1)
        os.environ["FAL_KEY"] = fal_key

    # Create downloads directory if it doesn't exist
    downloads_dir = "downloads"
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)

    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-logo-gen-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())