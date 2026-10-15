"""Adapter for a user-provisioned local model CLI. Does not execute generated C."""
import argparse
import json
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--command-json', required=True, help='JSON argv array for local inference CLI accepting stdin')
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--timeout', type=int, default=120)
args = parser.parse_args()
command = json.loads(args.command_json)
if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
    parser.error('command-json must be a nonempty array of strings')
source = (Path(__file__).parent / 'candidates/vulnerable.c').read_text()
prompt = '''Repair this synthetic C telemetry parser. Packet arguments are declared length, opcode, payload bytes.
Accept only unsigned decimal integers; length must equal actual payload count and be <=32;
opcode is 0..3 and bytes are 0..255. On success print OK:<length>, otherwise REJECT.
Preserve the CLI. Output only complete C source, no Markdown.\n''' + source
result = subprocess.run(command, input=prompt, text=True, capture_output=True,
                        timeout=args.timeout, check=True)
if not result.stdout.strip() or len(result.stdout.encode()) > 100_000:
    raise SystemExit('Empty or oversized candidate')
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(result.stdout)
args.output.with_suffix('.metadata.json').write_text(json.dumps({
    'command': command, 'timeout_seconds': args.timeout,
    'status': 'generated_unvalidated', 'offline_isolation': 'not_enforced_by_this_adapter',
    'note': 'Record model identity, weights checksum and quantization separately.'}, indent=2))
print('Candidate saved; unvalidated and not executed.')
