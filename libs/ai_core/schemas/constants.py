# --- Dataset and column standards ---
TEXT_COLUMN = "text"
CONVERSATIONS_COLUMN = "messages"  # read by sft trainer
INSTRUCTION_COLUMN = "instruction"
INPUT_COLUMN = "input"
OUTPUT_COLUMN = "completion"

DEFAULT_TEXT_FORMAT = "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{response}"
