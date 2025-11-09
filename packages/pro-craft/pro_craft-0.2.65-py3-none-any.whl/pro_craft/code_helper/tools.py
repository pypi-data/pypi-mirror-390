from .codermanager import CoderTemplateManager
from typing import List, Dict, Any,Optional
import re

coder = CoderTemplateManager()

# --- 工具函数实现 ---

def search_template_by_text(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    根据自然语言查询在模板库中进行语义搜索（使用 Qdrant 向量检索），返回最相关的 `top_k` 个模板的摘要信息。
    """
    print("search_template_by_text")
    print(f"input & {type(query)} & query: {query} top:k {top_k} ")
    search_result = coder.search(
        text=query,
        limit=top_k,
        # query_filter=None # 可以在这里添加额外的过滤条件，例如根据语言、框架过滤
    )

    templates_summary = []
    for hit in search_result:
        # 在实际 Qdrant 中，hit.id 是模板的ID，hit.payload 包含其他元数据
        # 假设你的 Qdrant payload 中存储了 template_name 和 description
        templates_summary.append({
            'template_id': hit.payload.get("template_id"),
            'description': hit.payload.get('description', 'No description provided.'),
            'match_score': hit.score
        })
    print(f"output & {type(templates_summary)} & {templates_summary} ")
    return templates_summary

def get_template_details(template_id: str) -> Optional[Dict[str, Any]]: # template_id 根据你的模型是 Integer
    """
    根据 `template_id` 从数据库中获取模板的完整详细信息，包括模板代码、推断出的命名约定和使用建议。
    """
    print("get_template_details")
    print(f"input & {type(template_id)} & query: {template_id} ")
    template = coder.get_template_obj(template_id = template_id)
    if template:
        return {
            'template_id': template.template_id,
            'description': template.description,
            'template_code': template.template_code,
            'version': template.version,
        }
    print(f"output & {type(template)} & {template} ")
    return None


def ask_user_for_clarification(question: str) -> str:
    """
    当你对用户需求有疑问，或需要用户做选择（例如在多个匹配模板中选择一个）时，使用此工具向用户提问。
    """
    print("ask_user_for_clarification")
    print(f"input & {type(question)} & query: {question} ")
    print("\n--- Agent 需要你的帮助 ---")
    print(f"Agent: {question}")
    user_input = input("你的回答: ")
    print("-------------------------\n")
    print(f"output & {type(user_input)} & query: {user_input} ")
    return user_input


def generate_request_file(template_code: str, user_request_details: Dict[str, Any], naming_conventions: Optional[Dict[str, Any]] = None) -> str:
    """
    根据选定的模板代码、解析后的用户需求（结构化形式）和模板的命名约定，生成符合 `REQUEST_START/END` 格式的指令文件。
    `user_request_details` 应该是一个字典，键是 BLOCK/PLACEHOLDER 的名称，值是包含 '指令' 和 '约束/示例' 的字典。
    """
    print("generate_request_file")
    print(f"input & {type(template_code)} & template_code: {template_code} user_request_details: {user_request_details} naming_conventions: {naming_conventions}")

    request_parts = []

    request_parts.append("--- REQUEST_START ---")
    request_parts.append("template.py # 目标文件通常是这个，可以根据实际情况调整") # 假设一个通用文件名

    # 添加整体目标描述
    overall_goal = user_request_details.get("overall_goal", "完善代码模板以满足以下需求。")
    request_parts.append(f"\n**目标：** {overall_goal}\n")

    # 添加命名约定 (如果提供了)
    if naming_conventions:
        request_parts.append("**命名约定:**")
        for key, value in naming_conventions.items():
            request_parts.append(f"*   **{key}:** {value}")
        request_parts.append("") # 空行

    request_parts.append("**具体修改点：**\n")

    # 遍历模板代码，找到所有的 BLOCK 和 PLACEHOLDER
    # 然后根据 user_request_details 填充指令
    # 这是一个简化版本，实际可能需要更复杂的解析器来处理嵌套块或动态生成的块
    # 对于 MVP，我们可以假设 user_request_details 中包含了所有需要填充的块/占位符
    block_pattern = r"(BLOCK_START|PLACEHOLDER):\s*(\w+)"
    for match in re.finditer(block_pattern, template_code):
        block_type = match.group(1)
        block_name = match.group(2)

        if block_name in user_request_details:
            details = user_request_details[block_name]
            instruction = details.get("指令", "")
            constraint_example = details.get("约束/示例", "")

            request_parts.append(f"*   **{block_type}: {block_name}**")
            request_parts.append(f"    *   **指令：** {instruction}")
            if constraint_example:
                # 确保多行约束/示例能正确缩进
                formatted_ce = "\n".join([f"    *   **约束/示例：** {line}" if i == 0 else f"    *   {line}" for i, line in enumerate(str(constraint_example).splitlines())])
                request_parts.append(formatted_ce)
            request_parts.append("") # 空行

    request_parts.append("--- REQUEST_END ---")
    print(f"output & {type(request_parts)} & request_parts: {request_parts} ")

    result = "\n".join(request_parts)
    return result

