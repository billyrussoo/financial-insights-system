from src.utils.prompt_utils import fill_prompt_template

def build_prompt(persona: dict, context: str, keyword: str, articles: list, stock_data: list) -> str:
    return fill_prompt_template(
        persona=persona,
        context=context,
        keyword=keyword,
        articles=articles,
        stock_data=stock_data
    )
