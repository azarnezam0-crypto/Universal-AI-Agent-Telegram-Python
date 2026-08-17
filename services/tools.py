from typing import List
from typing import Any
from dataclasses import dataclass
import json
@dataclass
class A:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'A':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return A(_type, _description)

@dataclass
class AllowedDomains:
    type: str
    items: Items
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'AllowedDomains':
        _type = str(obj.get("type"))
        _items = Items.from_dict(obj.get("items"))
        _description = str(obj.get("description"))
        return AllowedDomains(_type, _items, _description)

@dataclass
class B:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'B':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return B(_type, _description)

@dataclass
class BashId:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'BashId':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return BashId(_type, _description)

@dataclass
class BlockedDomains:
    type: str
    items: Items
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'BlockedDomains':
        _type = str(obj.get("type"))
        _items = Items.from_dict(obj.get("items"))
        _description = str(obj.get("description"))
        return BlockedDomains(_type, _items, _description)

@dataclass
class C:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'C':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return C(_type, _description)

@dataclass
class CellId:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'CellId':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return CellId(_type, _description)

@dataclass
class CellType:
    type: str
    enum: List[str]
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'CellType':
        _type = str(obj.get("type"))
        _enum = [.from_dict(y) for y in obj.get("enum")]
        _description = str(obj.get("description"))
        return CellType(_type, _enum, _description)

@dataclass
class Command:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Command':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Command(_type, _description)

@dataclass
class Content:
    type: str
    description: str
    minLength: int

    @staticmethod
    def from_dict(obj: Any) -> 'Content':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        _minLength = int(obj.get("minLength"))
        return Content(_type, _description, _minLength)

@dataclass
class Description:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Description':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Description(_type, _description)

@dataclass
class EditMode:
    type: str
    enum: List[str]
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'EditMode':
        _type = str(obj.get("type"))
        _enum = [.from_dict(y) for y in obj.get("enum")]
        _description = str(obj.get("description"))
        return EditMode(_type, _enum, _description)

@dataclass
class Edits:
    type: str
    items: Items
    minItems: int
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Edits':
        _type = str(obj.get("type"))
        _items = Items.from_dict(obj.get("items"))
        _minItems = int(obj.get("minItems"))
        _description = str(obj.get("description"))
        return Edits(_type, _items, _minItems, _description)

@dataclass
class FilePath:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'FilePath':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return FilePath(_type, _description)

@dataclass
class Filter:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Filter':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Filter(_type, _description)

@dataclass
class Glob:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Glob':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Glob(_type, _description)

@dataclass
class HeadLimit:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'HeadLimit':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return HeadLimit(_type, _description)

@dataclass
class I:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'I':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return I(_type, _description)

@dataclass
class Id:
    type: str

    @staticmethod
    def from_dict(obj: Any) -> 'Id':
        _type = str(obj.get("type"))
        return Id(_type)

@dataclass
class Ignore:
    type: str
    items: Items
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Ignore':
        _type = str(obj.get("type"))
        _items = Items.from_dict(obj.get("items"))
        _description = str(obj.get("description"))
        return Ignore(_type, _items, _description)

@dataclass
class InputSchema:
    type: str
    properties: Properties
    required: List[str]
    additionalProperties: bool
    $schema: str

    @staticmethod
    def from_dict(obj: Any) -> 'InputSchema':
        _type = str(obj.get("type"))
        _properties = Properties.from_dict(obj.get("properties"))
        _required = [.from_dict(y) for y in obj.get("required")]
        _additionalProperties = 
        _$schema = str(obj.get("$schema"))
        return InputSchema(_type, _properties, _required, _additionalProperties, _$schema)

@dataclass
class Items:
    type: str
    properties: Properties
    required: List[str]
    additionalProperties: bool

    @staticmethod
    def from_dict(obj: Any) -> 'Items':
        _type = str(obj.get("type"))
        _properties = Properties.from_dict(obj.get("properties"))
        _required = [.from_dict(y) for y in obj.get("required")]
        _additionalProperties = 
        return Items(_type, _properties, _required, _additionalProperties)

@dataclass
class Limit:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Limit':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Limit(_type, _description)

@dataclass
class Multiline:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Multiline':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Multiline(_type, _description)

@dataclass
class N:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'N':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return N(_type, _description)

@dataclass
class NewSource:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'NewSource':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return NewSource(_type, _description)

@dataclass
class NewString:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'NewString':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return NewString(_type, _description)

@dataclass
class NotebookPath:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'NotebookPath':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return NotebookPath(_type, _description)

@dataclass
class Offset:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Offset':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Offset(_type, _description)

@dataclass
class OldString:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'OldString':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return OldString(_type, _description)

@dataclass
class OutputMode:
    type: str
    enum: List[str]
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'OutputMode':
        _type = str(obj.get("type"))
        _enum = [.from_dict(y) for y in obj.get("enum")]
        _description = str(obj.get("description"))
        return OutputMode(_type, _enum, _description)

@dataclass
class Path:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Path':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Path(_type, _description)

@dataclass
class Pattern:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Pattern':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Pattern(_type, _description)

@dataclass
class Plan:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Plan':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Plan(_type, _description)

@dataclass
class Prompt:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Prompt':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Prompt(_type, _description)

@dataclass
class Properties:
    description: Description
    prompt: Prompt
    subagent_type: SubagentType
    command: Command
    timeout: Timeout
    run_in_background: RunInBackground
    pattern: Pattern
    path: Path
    glob: Glob
    output_mode: OutputMode
    -B: B
    -A: A
    -C: C
    -n: N
    -i: I
    type: Type
    head_limit: HeadLimit
    multiline: Multiline
    ignore: Ignore
    plan: Plan
    file_path: FilePath
    offset: Offset
    limit: Limit
    old_string: OldString
    new_string: NewString
    replace_all: ReplaceAll
    edits: Edits
    content: Content
    notebook_path: NotebookPath
    cell_id: CellId
    new_source: NewSource
    cell_type: CellType
    edit_mode: EditMode
    url: Url
    todos: Todos
    query: Query
    allowed_domains: AllowedDomains
    blocked_domains: BlockedDomains
    bash_id: BashId
    filter: Filter
    shell_id: ShellId
    status: Status
    id: Id

    @staticmethod
    def from_dict(obj: Any) -> 'Properties':
        _description = Description.from_dict(obj.get("description"))
        _prompt = Prompt.from_dict(obj.get("prompt"))
        _subagent_type = SubagentType.from_dict(obj.get("subagent_type"))
        _command = Command.from_dict(obj.get("command"))
        _timeout = Timeout.from_dict(obj.get("timeout"))
        _run_in_background = RunInBackground.from_dict(obj.get("run_in_background"))
        _pattern = Pattern.from_dict(obj.get("pattern"))
        _path = Path.from_dict(obj.get("path"))
        _glob = Glob.from_dict(obj.get("glob"))
        _output_mode = OutputMode.from_dict(obj.get("output_mode"))
        _-B = B.from_dict(obj.get("-B"))
        _-A = A.from_dict(obj.get("-A"))
        _-C = C.from_dict(obj.get("-C"))
        _-n = N.from_dict(obj.get("-n"))
        _-i = I.from_dict(obj.get("-i"))
        _type = Type.from_dict(obj.get("type"))
        _head_limit = HeadLimit.from_dict(obj.get("head_limit"))
        _multiline = Multiline.from_dict(obj.get("multiline"))
        _ignore = Ignore.from_dict(obj.get("ignore"))
        _plan = Plan.from_dict(obj.get("plan"))
        _file_path = FilePath.from_dict(obj.get("file_path"))
        _offset = Offset.from_dict(obj.get("offset"))
        _limit = Limit.from_dict(obj.get("limit"))
        _old_string = OldString.from_dict(obj.get("old_string"))
        _new_string = NewString.from_dict(obj.get("new_string"))
        _replace_all = ReplaceAll.from_dict(obj.get("replace_all"))
        _edits = Edits.from_dict(obj.get("edits"))
        _content = Content.from_dict(obj.get("content"))
        _notebook_path = NotebookPath.from_dict(obj.get("notebook_path"))
        _cell_id = CellId.from_dict(obj.get("cell_id"))
        _new_source = NewSource.from_dict(obj.get("new_source"))
        _cell_type = CellType.from_dict(obj.get("cell_type"))
        _edit_mode = EditMode.from_dict(obj.get("edit_mode"))
        _url = Url.from_dict(obj.get("url"))
        _todos = Todos.from_dict(obj.get("todos"))
        _query = Query.from_dict(obj.get("query"))
        _allowed_domains = AllowedDomains.from_dict(obj.get("allowed_domains"))
        _blocked_domains = BlockedDomains.from_dict(obj.get("blocked_domains"))
        _bash_id = BashId.from_dict(obj.get("bash_id"))
        _filter = Filter.from_dict(obj.get("filter"))
        _shell_id = ShellId.from_dict(obj.get("shell_id"))
        _status = Status.from_dict(obj.get("status"))
        _id = Id.from_dict(obj.get("id"))
        return Properties(_description, _prompt, _subagent_type, _command, _timeout, _run_in_background, _pattern, _path, _glob, _output_mode, _-B, _-A, _-C, _-n, _-i, _type, _head_limit, _multiline, _ignore, _plan, _file_path, _offset, _limit, _old_string, _new_string, _replace_all, _edits, _content, _notebook_path, _cell_id, _new_source, _cell_type, _edit_mode, _url, _todos, _query, _allowed_domains, _blocked_domains, _bash_id, _filter, _shell_id, _status, _id)

@dataclass
class Query:
    type: str
    minLength: int
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Query':
        _type = str(obj.get("type"))
        _minLength = int(obj.get("minLength"))
        _description = str(obj.get("description"))
        return Query(_type, _minLength, _description)

@dataclass
class ReplaceAll:
    type: str
    default: bool
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'ReplaceAll':
        _type = str(obj.get("type"))
        _default = 
        _description = str(obj.get("description"))
        return ReplaceAll(_type, _default, _description)

@dataclass
class Root:
    tools: List[Tool]

    @staticmethod
    def from_dict(obj: Any) -> 'Root':
        _tools = [Tool.from_dict(y) for y in obj.get("tools")]
        return Root(_tools)

@dataclass
class RunInBackground:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'RunInBackground':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return RunInBackground(_type, _description)

@dataclass
class ShellId:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'ShellId':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return ShellId(_type, _description)

@dataclass
class Status:
    type: str
    enum: List[str]

    @staticmethod
    def from_dict(obj: Any) -> 'Status':
        _type = str(obj.get("type"))
        _enum = [.from_dict(y) for y in obj.get("enum")]
        return Status(_type, _enum)

@dataclass
class SubagentType:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'SubagentType':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return SubagentType(_type, _description)

@dataclass
class Timeout:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Timeout':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Timeout(_type, _description)

@dataclass
class Todos:
    type: str
    items: Items
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Todos':
        _type = str(obj.get("type"))
        _items = Items.from_dict(obj.get("items"))
        _description = str(obj.get("description"))
        return Todos(_type, _items, _description)

@dataclass
class Tool:
    name: str
    description: str
    input_schema: InputSchema

    @staticmethod
    def from_dict(obj: Any) -> 'Tool':
        _name = str(obj.get("name"))
        _description = str(obj.get("description"))
        _input_schema = InputSchema.from_dict(obj.get("input_schema"))
        return Tool(_name, _description, _input_schema)

@dataclass
class Type:
    type: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Type':
        _type = str(obj.get("type"))
        _description = str(obj.get("description"))
        return Type(_type, _description)

@dataclass
class Url:
    type: str
    format: str
    description: str

    @staticmethod
    def from_dict(obj: Any) -> 'Url':
        _type = str(obj.get("type"))
        _format = str(obj.get("format"))
        _description = str(obj.get("description"))
        return Url(_type, _format, _description)

# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)

"""Tool/function definitions the model can call during an agentic chat turn.

Each tool has:
  - a JSON-schema description (TOOL_DEFINITIONS) sent to the model, and
  - a python implementation in TOOL_REGISTRY (name -> callable(user, **args) -> str).

To add a new "skill", just append a definition here + a function — the model
will then be able to use it automatically, no new Telegram command needed.
"""
from services.router_client import web_search, web_fetch


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for up-to-date information, news, or any query. "
                "Returns a list of results with titles, URLs, and snippets."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."},
                    "max_results": {
                        "type": "integer",
                        "description": "Number of results to return (default 5).",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": (
                "Fetch the content of a web page URL and return it as markdown text. "
                "Use to read articles, documentation, or any webpage the user mentions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Full URL to fetch."},
                },
                "required": ["url"],
            },
        },
    },
]


def _web_search(user, query: str, max_results: int = 5) -> str:
    data = web_search(user, query, int(max_results))
    results = data.get("results") or []
    if not results:
        return "No results found."
    lines = []
    for i, r in enumerate(results[:8], 1):
        lines.append(f"{i}. {r.get('title', '')}\n{r.get('url', '')}\n{(r.get('snippet') or '').strip()}")
    return "\n\n".join(lines)


def _web_fetch(user, url: str) -> str:
    data = web_fetch(user, url, "markdown", 8000)
    content = data.get("content") or {}
    text = content.get("text") if isinstance(content, dict) else None
    if not text:
        text = data.get("content") or ""
    if not text:
        return "No content could be extracted from that URL."
    return f"Title: {data.get('title', '')}\n\n{text}"


TOOL_REGISTRY = {
    "web_search": _web_search,
    "web_fetch": _web_fetch,
}
