import json
import os
from typing import Any, Coroutine, List
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(api_key="sk-QgmAi4cJM9KY9DF9MOglTSfgjjpZBaTQ5Yfh5zgiuSsCdAJP", base_url="https://ai.tzpro.xyz/v1")

prompt = """
Please determine whether the following Twitter content is an advertisement and return the results in JSON format.

**Criteria for Judgment:** Content is considered "advertisement" if it promotes a product, service, or brand and has a clear marketing intention. Content is considered "not advertisement" if it does not contain obvious promotional intent and is more inclined towards personal opinions, information sharing, or daily communication.

**Carefully analyze the following elements to assist in your judgment:**

*   **Keywords:** Does the content contain obvious advertising and marketing keywords (e.g., purchase, promotion, discount, register now, free trial, investment, finance, exchange name, product name, etc.)?
*   **Links:** Does the content contain links to external websites, especially commercial websites, product pages, registration pages, or promotional campaign pages?
*   **Brand Identity:** Does the content mention specific brand names, company names, product names, or service names? Are brand-related Hashtags or user @ mentions used?
*   **Call to Action:** Does the content contain obvious calls to action, guiding users to take action (e.g., click the link, register, purchase, learn more, contact us, DM for consultation, etc.)?
*   **Tone and Purpose:** Does the tone of the content have a clear sales or promotional nature? Is the purpose of the content to promote a product, service, or brand?

**Instructions:**

1.  **Analyze the following list of Twitter content.**
2.  **For each piece of content, determine if it is an advertisement.**
3.  **Output the judgment results in JSON format as follows:**

```json
{
  "name": "response_class",
  "strict": true,
  "schema": {
    "type": "object",
    "properties": {
      "success": {
        "type": "boolean",
        "description": "Whether the API processed successfully."
      },
      "data": {
        "type": "object",
        "properties": {
          "ads": {
            "type": "array",
            "items": {
              "type": "string",
              "description": "Advertisment content here"
            }
          },
          "non-ads": {
            "type": "array",
            "items": {
              "type": "string",
              "description": "Non-advertisement content here"
            }
          }
        },
        "required": ["ads", "non-ads"]
      }
    },
    "required": ["success", "data"]
  }
}
"""


schema = """

"""


def stringSpliter(data_list, max_tokens=2048):
    """
    split_into_limited_strings
    :param data_list:
    :param max_tokens:
    :return:
    """
    result = []  # 用于存储最终的字符串
    current_string = ""  # 当前正在拼接的字符串

    for item in data_list:
        # 检查是否拼接当前项目后超出 token 限制
        if len(current_string) + len(item) + 1 > max_tokens:  # +1 是为了包括 '\n'
            result.append(current_string.strip())  # 保存当前字符串到结果列表
            current_string = ""  # 重置当前字符串

        # 拼接当前项目到当前字符串
        current_string += item + '\n'

    # 保存最后一个字符串（如果有内容）
    if current_string.strip():
        result.append(current_string.strip())

    return result


async def adBlockers(data: list) -> list[str | Any]:
    """
    adsBlockers function
    :param data:
    :return:
    """
    results = stringSpliter(data)
    for i in results:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"analyze the following context: {i}"},
            ],
            response_format={"type": "json_schema","json_schema":json.loads(schema)}
        )
        with open(os.path.join(os.path.dirname(__file__), "results.json"), "w") as file:
            file.write(completion.choices[0].message.content)
        parsed_response = completion.choices[0].message.content
        print(parsed_response)
    return results
