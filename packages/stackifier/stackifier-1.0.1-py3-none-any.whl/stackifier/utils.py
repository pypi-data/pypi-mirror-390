from typing import List


def stackify_text(text: str, width: int = 50, char: str = "=") -> str:
    border = char * width
    padding = (width - len(text) - 2) // 2
    
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
        padding = (width - len(text) - 2) // 2
    
    line = f"{char}{' ' * padding}{text}{' ' * padding}{char}"
    
    if len(line) < width:
        line += char * (width - len(line))
    
    return f"{border}\n{line}\n{border}"


def create_ascii_stack(items: List[str], width: int = 30) -> str:
    if not items:
        return "Stack is empty!"
    
    lines = []
    lines.append("  " + "┌" + "─" * (width - 2) + "┐")
    
    for i, item in enumerate(reversed(items)):
        item_str = str(item)
        if len(item_str) > width - 4:
            item_str = item_str[:width - 7] + "..."
        
        padding = (width - len(item_str) - 4) // 2
        label = "TOP" if i == 0 else "   "
        line = f"{label}│ {' ' * padding}{item_str}{' ' * (width - len(item_str) - padding - 4)} │"
        lines.append(line)
        
        if i < len(items) - 1:
            lines.append("  " + "├" + "─" * (width - 2) + "┤")
    
    lines.append("  " + "└" + "─" * (width - 2) + "┘")
    
    return "\n".join(lines)
