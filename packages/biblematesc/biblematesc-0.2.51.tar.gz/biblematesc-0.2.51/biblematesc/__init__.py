from agentmake import USER_OS, AGENTMAKE_USER_DIR, readTextFile, writeTextFile
from pathlib import Path
from biblematesc import config
from biblematesc.ui.selection_dialog import TerminalModeDialogs
import os, shutil, pprint
import warnings

# Filter out the specific RuntimeWarning from the 'agentmake' module
warnings.filterwarnings(
    "ignore", 
    message="coroutine '.*' was never awaited", 
    category=RuntimeWarning, 
    module='agentmake'
)

BIBLEMATE_USER_DIR = os.path.join(AGENTMAKE_USER_DIR, "biblemate")
if not os.path.isdir(BIBLEMATE_USER_DIR):
    Path(BIBLEMATE_USER_DIR).mkdir(parents=True, exist_ok=True)
CONFIG_FILE_BACKUP = os.path.join(BIBLEMATE_USER_DIR, "biblematesc.config")

# NOTE: When add a config item, update both `write_user_config` and `default_config`

def write_user_config():
    """Writes the current configuration to the user's config file."""
    configurations = f"""config.banner_title="{config.banner_title}"
config.agent_mode={config.agent_mode}
config.prompt_engineering={config.prompt_engineering}
config.auto_suggestions={config.auto_suggestions}
config.auto_tool_selection={config.auto_tool_selection}
config.max_steps={config.max_steps}
config.light={config.light}
config.web_browser={config.web_browser}
config.hide_tools_order={config.hide_tools_order}
config.skip_connection_check={config.skip_connection_check}
config.default_bible="{config.default_bible}"
config.default_commentary="{config.default_commentary}"
config.default_encyclopedia="{config.default_encyclopedia}"
config.default_lexicon="{config.default_lexicon}"
config.max_semantic_matches={config.max_semantic_matches}
config.max_log_lines={config.max_log_lines}
config.mcp_port={config.mcp_port}
config.mcp_timeout={config.mcp_timeout}
config.color_agent_mode="{config.color_agent_mode}"
config.color_partner_mode="{config.color_partner_mode}"
config.color_info_border="{config.color_info_border}"
config.embedding_model="{config.embedding_model}"
config.custom_input_suggestions={pprint.pformat(config.custom_input_suggestions)}
config.disabled_tools={pprint.pformat(config.disabled_tools)}"""
    writeTextFile(CONFIG_FILE_BACKUP, configurations)

# restore config backup after upgrade
default_config = '''config.banner_title=""
config.agent_mode=False
config.prompt_engineering=False
config.auto_suggestions=True
config.auto_tool_selection=False
config.max_steps=50
config.light=True
config.web_browser=False
config.hide_tools_order=True
config.skip_connection_check=False
config.default_bible="CUVs"
config.default_commentary="新英語譯本"
config.default_encyclopedia="ISB"
config.default_lexicon="Morphology"
config.max_semantic_matches=15
config.max_log_lines=2000
config.mcp_port=33333
config.mcp_timeout=9999999999
config.color_agent_mode="#FF8800"
config.color_partner_mode="#8000AA"
config.color_info_border="bright_blue"
config.embedding_model="paraphrase-multilingual"
config.custom_input_suggestions=[]
config.disabled_tools=['search_1_chronicles_only',
'search_1_corinthians_only',
'search_1_john_only',
'search_1_kings_only',
'search_1_peter_only',
'search_1_samuel_only',
'search_1_thessalonians_only',
'search_1_timothy_only',
'search_2_chronicles_only',
'search_2_corinthians_only',
'search_2_john_only',
'search_2_kings_only',
'search_2_peter_only',
'search_2_samuel_only',
'search_2_thessalonians_only',
'search_2_timothy_only',
'search_3_john_only',
'search_acts_only',
'search_amos_only',
'search_colossians_only',
'search_daniel_only',
'search_deuteronomy_only',
'search_ecclesiastes_only',
'search_ephesians_only',
'search_esther_only',
'search_exodus_only',
'search_ezekiel_only',
'search_ezra_only',
'search_galatians_only',
'search_genesis_only',
'search_habakkuk_only',
'search_haggai_only',
'search_hebrews_only',
'search_hosea_only',
'search_isaiah_only',
'search_james_only',
'search_jeremiah_only',
'search_job_only',
'search_joel_only',
'search_john_only',
'search_jonah_only',
'search_joshua_only',
'search_jude_only',
'search_judges_only',
'search_lamentations_only',
'search_leviticus_only',
'search_luke_only',
'search_malachi_only',
'search_mark_only',
'search_matthew_only',
'search_micah_only',
'search_nahum_only',
'search_nehemiah_only',
'search_numbers_only',
'search_obadiah_only',
'search_philemon_only',
'search_philippians_only',
'search_proverbs_only',
'search_psalms_only',
'search_revelation_only',
'search_romans_only',
'search_ruth_only',
'search_song_of_songs_only',
'search_titus_only',
'search_zechariah_only',
'search_zephaniah_only']'''

def load_config():
    """Loads the user's configuration from the config file."""
    if not os.path.isfile(CONFIG_FILE_BACKUP):
        exec(default_config, globals())
        write_user_config()
    else:
        exec(readTextFile(CONFIG_FILE_BACKUP), globals())
    # check if new config items are added
    changed = False
    for config_item in default_config[7:].split("\nconfig."):
        key, _ = config_item.split("=", 1)
        if not hasattr(config, key):
            exec(f"config.{config_item}", globals())
            changed = True
    if changed:
        write_user_config()

# load user config at startup
load_config()

# temporary config
config.current_prompt = ""
config.cancelled = False
config.last_multi_bible_selection = [config.default_bible]
config.last_bible_reference = ""
config.last_book = 43
config.last_chapter = 3
config.last_verse = 16
config.backup_required = False
config.export_item = ""
config.action_list = {
    # general
    ".translate": "把上一个回应内容翻译成简体中文",
    ".ideas": "构思输入点子",
    ".exit": "退出当前输入",
    # conversations
    ".new": "新对话",
    ".trim": "修剪对话",
    ".edit": "编辑对话",
    ".reload": "重新载入对话",
    ".import": "汇入对话",
    ".export": "汇出对话",
    ".backup": "备份对话",
    ".find": "搜寻对话",
    # UBA content
    ".bible": "开启圣经经文",
    ".chapter": "开启圣经单章内容",
    ".compare": "比较不同圣经版本的经文",
    ".comparechapter": "比较不同圣经版本的单章内容",
    ".xref": "开启串珠经文",
    ".treasury": "开启圣经知识宝库",
    ".commentary": "开启注释书",
    ".aicommentary": "开启AI注释",
    ".index": "开启经文研读索引",
    ".translation": "开启逐字、直译和动态译本",
    ".discourse": "开启语篇分析",
    ".morphology": "开启词形学数据",
    ".search": "搜寻圣经",
    ".dictionary": "搜寻词典",
    ".encyclopedia": "搜寻百科全书",
    ".lexicon": "搜寻词汇",
    ".parallel": "搜寻平行经文",
    ".promise": "搜寻圣经应许",
    ".topic": "搜寻圣经主题", # Changed from topic to focus for better context in Chinese
    ".name": "搜寻圣经人名",
    ".character": "搜寻圣经人物",
    ".location": "搜寻圣经地点",
    ".chronology": "开启圣经年表",
    ".defaultbible": "配置预设圣经版本",
    ".defaultcommentary": "配置预设注释书",
    ".defaultencyclopedia": "配置预设百科全书",
    ".defaultlexicon": "配置预设原文字典",
    # resource information
    ".tools": "列出可用工具",
    ".plans": "列出可用计划",
    ".resources": "列出 UniqueBible 资源",
    # configurations
    ".backend": "配置 AI 设定",
    ".steps": "配置允许的最大步骤数",
    ".matches": "配置最大语义搜索项数",
    ".mode": "配置AI模式",
    ".autosuggest": "切换自动输入建议",
    ".autoprompt": "切换自动优化输入内容",
    ".autotool": "在聊天模式中切换自动工具选用功能",
    ".light": "切换简化对话记录功能",
    # file access
    ".content": "显示当前目录内容",
    ".open": "开启文件或资料夹",
    ".download": "下载数据档案",
    # help
    ".help": "帮助资讯",
}

# copy etextedit plugins
ETEXTEDIT_USER_PULGIN_DIR = os.path.join(os.path.expanduser("~"), "etextedit", "plugins")
if not os.path.isdir(ETEXTEDIT_USER_PULGIN_DIR):
    Path(ETEXTEDIT_USER_PULGIN_DIR).mkdir(parents=True, exist_ok=True)
BIBLEMATE_ETEXTEDIT_PLUGINS = os.path.join(os.path.dirname(os.path.realpath(__file__)), "etextedit", "plugins")
for file_name in os.listdir(BIBLEMATE_ETEXTEDIT_PLUGINS):
    full_file_name = os.path.join(BIBLEMATE_ETEXTEDIT_PLUGINS, file_name)
    if file_name.endswith(".py") and os.path.isfile(full_file_name) and not os.path.isfile(os.path.join(ETEXTEDIT_USER_PULGIN_DIR, file_name)):
        shutil.copy(full_file_name, ETEXTEDIT_USER_PULGIN_DIR)

# constants
AGENTMAKE_CONFIG = {
    "stream": True,
    "print_on_terminal": False,
    "word_wrap": False,
}
OLLAMA_NOT_FOUND = "`Ollama` is not found! BibleMate AI uses `Ollama` to generate embeddings for semantic searches. You may install it from https://ollama.com/ so that you can perform semantic searches of the Bible with BibleMate AI."
BIBLEMATE_VERSION = readTextFile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "version.txt"))
BIBLEMATEDATA = os.path.join(BIBLEMATE_USER_DIR, "data")
if not os.path.isdir(BIBLEMATEDATA):
    Path(BIBLEMATEDATA).mkdir(parents=True, exist_ok=True)
BIBLEMATETEMP = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp")
if not os.path.isdir(BIBLEMATETEMP):
    Path(BIBLEMATETEMP).mkdir(parents=True, exist_ok=True)
DIALOGS = TerminalModeDialogs()

def fix_string(content):
    return content.replace(" ", " ").replace("‑", "-")

def list_dir_content(directory:str="."):
    directory = os.path.expanduser(directory.replace("%2F", "/"))
    if os.path.isdir(directory):
        folders = []
        files = []
        for item in sorted(os.listdir(directory)):
            if os.path.isdir(os.path.join(directory, item)):
                folders.append(f"📁 {item}")
            else:
                files.append(f"📄 {item}")
        return " ".join(folders) + ("\n\n" if folders and files else "") + " ".join(files)
    return "Invalid path!"

def request_chinese_response(prompt: str) -> str:
    return prompt + "\n\n# Response Language\n\nSimplified Chinese 简体中文\n\n请使用简体中文作所有回应，除了引用工具名称或希伯来语或希腊语，或我特别要求你使用英文除外。"