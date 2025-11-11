from ui_tars.action_parser import parse_xml_action_v3
import json
input_text = """<seed:tool_call_never_used_51bce0c785ca2f68081bfa7d91973934>\n<function_never_used_51bce0c785ca2f68081bfa7d91973934=search_hotel>\n<parameter_never_used_51bce0c785ca2f68081bfa7d91973934=city>\n<text_never_used_51bce0c785ca2f68081bfa7d91973934>北京</text_never_used_51bce0c785ca2f68081bfa7d91973934>\n</parameter_never_used_51bce0c785ca2f68081bfa7d91973934>\n<parameter_never_used_51bce0c785ca2f68081bfa7d91973934=min_rating>\n<text_never_used_51bce0c785ca2f68081bfa7d91973934>4.5</text_never_used_51bce0c785ca2f68081bfa7d91973934>\n</parameter_never_used_51bce0c785ca2f68081bfa7d91973934>\n<parameter_never_used_51bce0c785ca2f68081bfa7d91973934=services>\n<list>\n<item><text_never_used_51bce0c785ca2f68081bfa7d91973934>机场接送服务</text_never_used_51bce0c785ca2f68081bfa7d91973934></item>\n</list>\n</parameter_never_used_51bce0c785ca2f68081bfa7d91973934>\n<parameter_never_used_51bce0c785ca2f68081bfa7d91973934=facilities>\n<list>\n<item><text_never_used_51bce0c785ca2f68081bfa7d91973934>室内游泳池</text_never_used_51bce0c785ca2f68081bfa7d91973934></item>\n<item><text_never_used_51bce0c785ca2f68081bfa7d91973934>健身房</text_never_used_51bce0c785ca2f68081bfa7d91973934></item>\n</list>\n</parameter_never_used_51bce0c785ca2f68081bfa7d91973934>\n</function_never_used_51bce0c785ca2f68081bfa7d91973934>\n</seed:tool_call_never_used_51bce0c785ca2f68081bfa7d91973934>"""

tool_schemas = [
    {
        "name": "search_hotel",
        "description": "根据用户指定的多维度条件，在全球范围内搜索和推荐酒店。",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "用户希望入住酒店所在的城市。"
                },
                "min_rating": {
                    "type": "number",
                    "description": "酒店的最低星级评价，用户期望的酒店评价不应低于此标准。"
                },
                "services": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "酒店必须提供的一系列服务。"
                },
                "facilities": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "酒店必须具备的一系列设施。"
                }
            },
            "required": ["city"]
        }
    }
]
    
parsed_toolcalls = parse_xml_action_v3(input_text, tool_schemas,)
print(parsed_toolcalls)
json.dump(parsed_toolcalls, open("1.json", "w"), indent=4)
import pdb;pdb.set_trace()