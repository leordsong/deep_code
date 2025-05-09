import requests
import json
from typing import List

from openai import OpenAI

from utils.logger import logger



def reasoning_streaming_decode(completion, include_usage=False):
    """Decode the reasoning stream from the API response"""
    reasoning_content = ""  # Define the complete reasoning process
    answer_content = ""     # Define the complete reply
    is_answering = False   # Determine if the reasoning process has ended and the reply has started

    for chunk in completion:
        # 如果chunk.choices为空，则打印usage
        if not chunk.choices:
            if include_usage:
                logger.info(f'Usage: {chunk.usage}')
        else:
            delta = chunk.choices[0].delta
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content != None:
                reasoning_content += delta.reasoning_content
            else:
                # 开始回复
                if delta.content != "" and is_answering is False:
                    is_answering = True
                # 打印回复过程
                answer_content += delta.content

    return answer_content, reasoning_content

def build_single_round_messages(user_prompt, system_prompt=None, base64_image=None):
    messages = []
    if system_prompt is not None and len(system_prompt.strip()):
        messages.append({'role': 'system', 'content': system_prompt})
    if base64_image is not None:
        messages.append({'role': 'user', 'content': [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}, # base 64 image string
            },
            {"type": "text", "text": user_prompt},
        ]})
    else:
        messages.append({'role': 'user', 'content': user_prompt})
    return messages

