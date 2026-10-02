from pathlib import Path

CWD = Path().cwd()
OUTPUT_DIR = CWD / "output/"
EXTRACT_DIR = CWD / "extract/"

configs = {
    "deepseek-model": "deepseek-v4-flash",
    "deepseek-weak-model": "deepseek-v4-pro",
    "MAX_RETRIES": 3,
    "sysprompt": r"""
        # 任务: 提取文本里面的关键词
        # 要求：
        - 注意精简，要提取关键信息，考试考点，不要遗漏有效信息，可能的考点。
        - 你的任务不是解释，而是高效提取信息，关键词，术语等
    """
}
