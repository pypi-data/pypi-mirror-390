"""
Quick fix script to repair syntax errors in agent files from update_agents_cai.py
"""

from pathlib import Path
import re

agents_dir = Path(__file__).parent / "src" / "alprina_cli" / "agents"

# List of agent files that may have the bug
agent_files = [
    "blue_teamer.py",
    "dfir.py",
    "network_analyzer.py",
    "reverse_engineer.py",
    "android_sast.py",
    "memory_analysis.py",
    "wifi_security.py",
    "replay_attack.py",
    "subghz_sdr.py",
    "retester.py",
    "mail.py",
    "guardrails.py"
]

def fix_agent_file(file_path: Path):
    """Fix syntax errors in an agent file."""
    if not file_path.exists():
        return False

    content = file_path.read_text()

    # Fix the duplicate """ after docstring in _mock_scan
    pattern = r'(def _mock_scan\(self.*?\n.*?""")\s*"""'
    fixed_content = re.sub(pattern, r'\1', content, flags=re.DOTALL)

    # Fix any incomplete _mock_scan implementations
    # Look for _mock_scan followed by leftover text and then _parse_cai_response
    pattern2 = r'(def _mock_scan\(.*?\n.*?""")\s*[A-Za-z].*?\n\s*(def _parse_cai_response)'

    if re.search(pattern2, fixed_content, re.DOTALL):
        # Need to add mock implementation
        replacement = r'''\1
        findings = []
        findings.append({
            "type": "Security Finding",
            "severity": "INFO",
            "title": "Mock scan result",
            "description": "This is a mock implementation. Enable CAI for real analysis.",
            "file": target,
            "line": 0,
            "confidence": 0.5
        })

        return {
            "agent": self.name,
            "type": self.agent_type,
            "target": target,
            "findings": findings,
            "summary": {
                "total_findings": len(findings),
                "cai_powered": False
            }
        }

    \2'''
        fixed_content = re.sub(pattern2, replacement, fixed_content, flags=re.DOTALL)

    if fixed_content != content:
        file_path.write_text(fixed_content)
        print(f"✅ Fixed {file_path.name}")
        return True
    else:
        print(f"  ⏭️  {file_path.name} - no changes needed")
        return False

def main():
    """Fix all agent files."""
    print("🔧 Fixing agent syntax errors...\n")

    fixed = 0
    skipped = 0

    for filename in agent_files:
        file_path = agents_dir / filename

        if not file_path.exists():
            print(f"  ⚠️  {filename} not found")
            skipped += 1
            continue

        if fix_agent_file(file_path):
            fixed += 1
        else:
            skipped += 1

    print(f"\n✅ Fixed {fixed} files, {skipped} skipped")

if __name__ == "__main__":
    main()
