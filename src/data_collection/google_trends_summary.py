import pandas as pd
from typing import List, Dict


def summarize_trend_data(trend_df: pd.DataFrame, keyword: str) -> str:
    if trend_df.empty:
        return f"No trend data available for '{keyword}'."

    trend_df['date'] = pd.to_datetime(trend_df['date'])
    trend_df.set_index('date', inplace=True)

    max_value = trend_df[keyword].max()
    min_value = trend_df[keyword].min()
    mean_value = trend_df[keyword].mean()

    max_time = trend_df[keyword].idxmax().strftime('%Y-%m-%d %H:%M')
    min_time = trend_df[keyword].idxmin().strftime('%Y-%m-%d %H:%M')

    summary = (
        f"Search interest for '{keyword}' averaged {mean_value:.1f} over the selected period. "
        f"The peak occurred at {max_time} with a value of {max_value}, and the lowest point was at {min_time} with a value of {min_value}."
    )
    return summary


def summarize_region_data(region_df: pd.DataFrame, keyword: str, top_n: int = 5) -> str:
    if region_df.empty or keyword not in region_df.columns:
        return f"No regional interest data available for '{keyword}'."

    top_regions = region_df.sort_values(by=keyword, ascending=False).head(top_n)
    regions_list = top_regions['geoName'].tolist()

    summary = (
        f"The top {top_n} regions showing interest in '{keyword}' are: {', '.join(regions_list)}."
    )
    return summary


def generate_text_chunks(keywords: List[str],
                          trend_data_dict: Dict[str, pd.DataFrame],
                          region_data_dict: Dict[str, pd.DataFrame],
                          timeframe_label: str) -> List[Dict[str, str]]:
    """
    Returns a list of embeddable text chunks like:
    {
        'type': 'trend_summary',
        'keyword': 'Tesla',
        'timeframe': 'weekly',
        'summary': '...'
    }
    """
    chunks = []
    for keyword in keywords:
        trend_summary = summarize_trend_data(trend_data_dict.get(keyword, pd.DataFrame()), keyword)
        region_summary = summarize_region_data(region_data_dict.get(keyword, pd.DataFrame()), keyword)

        chunks.append({
            'type': 'trend_summary',
            'keyword': keyword,
            'timeframe': timeframe_label,
            'summary': trend_summary + ' ' + region_summary
        })
    return chunks