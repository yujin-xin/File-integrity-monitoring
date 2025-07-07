import hashlib
import os
import json
from colorama import Fore, Style, init
import sys

init()

def hash_file(filename, algorithm='sha1'):
    """Hash a file with specified algorithm"""
    hash_obj = hashlib.new(algorithm)

    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()

def color(text, textColor):
    colors = {
        'green': Fore.GREEN,
        'red': Fore.RED,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'cyan': Fore.CYAN
    }
    return f"{colors.get(textColor)}{text}{Style.RESET_ALL}"

def get_hash_algorithm():
    """Get hash algorithm from command line arguments"""
    if len(sys.argv) >= 4 and sys.argv[3] in ['sha1', 'sha256', 'sha512']:
        return sys.argv[3]
    return 'sha1'  # Default

def detect_hash_algorithm(hash_string):
    """Detect hash algorithm based on hash length"""
    hash_lengths = {
        40: 'sha1',      # SHA1 = 40 hex characters
        64: 'sha256',    # SHA256 = 64 hex characters
        128: 'sha512'    # SHA512 = 128 hex characters
    }
    return hash_lengths.get(len(hash_string), 'unknown')

def create_baseline(path, algorithm='sha1'):
    """Create initial snapshot of all files"""
    print(f"[Creating baseline snapshot with {algorithm.upper()}...]")
    baseline = {
        'metadata': {
            'hash_algorithm': algorithm,
            'created_at': str(os.path.getctime('.')),
            'version': '1.0'
        },
        'files': {}
    }
    
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            
            # Get file info
            try:
                file_hash = hash_file(filepath, algorithm)
                file_size = os.path.getsize(filepath)
                file_mtime = os.path.getmtime(filepath)
                
                if file_hash:  # Only add if hash succeeded
                    baseline['files'][filepath] = {
                        'hash': file_hash,
                        'size': file_size,
                        'mtime': file_mtime
                    }
                    print(f"   📄 {file} - recorded ({algorithm.upper()})")
            except Exception as e:
                print(f"   ❌ {file} - failed to hash: {e}")

    # Save baseline to file
    with open('baseline.json', 'w') as f:
        json.dump(baseline, f, indent=2)
    
    print(f"Baseline created! {len(baseline['files'])} files recorded using {algorithm.upper()}")
    return baseline

def load_baseline():
    """Load baseline from file"""
    try:
        with open('baseline.json', 'r') as f:
            baseline = json.load(f)
            
            # Handle old format (without metadata)
            if 'metadata' not in baseline:
                print(color("⚠️  Warning: Old baseline format detected. Hash algorithm unknown (assuming SHA1)", 'yellow'))
                return {
                    'metadata': {'hash_algorithm': 'sha1'},
                    'files': baseline
                }
            
            return baseline
    except FileNotFoundError:
        print("Note: No baseline found! Run with --baseline first")
        return None

def check_integrity(path, algorithm='sha1'):
    """Check files against baseline - the smart way!"""
    print("Checking file integrity...")
    
    prev_baseline = load_baseline()
    if not prev_baseline:
        return
    
    # Check hash algorithm compatibility
    baseline_algorithm = prev_baseline['metadata']['hash_algorithm']
    if baseline_algorithm != algorithm:
        print(color(f"   Hash Algorithm Mismatch!", 'red'))
        print(color(f"   Baseline uses: {baseline_algorithm.upper()}", 'red'))
        print(color(f"   Current check uses: {algorithm.upper()}", 'red'))
        print(color(f"   Please recreate baseline with --baseline {algorithm} or use --check {baseline_algorithm}", 'red'))
        return
    
    print(f"Using {algorithm.upper()} hash algorithm (matches baseline)")
    
    changes = []
    current_files = set()  # Track all current files
    baseline_files = prev_baseline['files']
    
    # First pass: Check existing files (modified and new)
    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            current_files.add(filepath)  # Keep track of current files
            
            try:
                current_size = os.path.getsize(filepath)
                current_mtime = os.path.getmtime(filepath)
                
                if filepath in baseline_files:
                    old_info = baseline_files[filepath]

                    # Fast check: First check size and time instead of hashing directly
                    if (current_size != old_info['size'] or 
                        current_mtime != old_info['mtime']):
                        
                        # Only hash if size or time keys has been changed
                        print(f"   📄 {file} - size/time changed, hashing...")
                        current_hash = hash_file(filepath, algorithm)
                        
                        if current_hash != old_info['hash']:
                            changes.append({
                                'file': filepath,
                                'status': 'modified',
                                'old_hash': old_info['hash'][:8], #print 8 chars only
                                'new_hash': current_hash[:8] #print 8 chars only
                            })
                        else:
                            print(f"   📄 {file} - false alarm (same hash) - {color('mtime or filesize from baseline.json has been modified', 'red')}")
                    else:
                        print(f"   📄 {file} ({filepath}) - unchanged")
                else:
                    # New file
                    changes.append({
                        'file': filepath,
                        'status': 'new'
                    })
                    
            except Exception as e:
                print(f"    {file} - error checking: {e}")
    
    # Second pass: Check for deleted files
    baseline_file_paths = set(baseline_files.keys())
    deleted_files = baseline_file_paths - current_files
    
    for deleted_file in deleted_files:
        changes.append({
            'file': deleted_file,
            'status': 'deleted'
        })
    
    # Show results
    if changes:
        print(f"\nFound {len(changes)} changes:")
        for change in changes:
            if change['status'] == 'modified':
                print(color(f"   MODIFIED: {change['file']}", 'yellow'))
                print(f"   Old: {change['old_hash']} -> New: {change['new_hash']}")
            elif change['status'] == 'new':
                print(color(f"   NEW: {change['file']}", 'green'))
            elif change['status'] == 'deleted':
                print(color(f"   DELETED: {change['file']}", 'red'))
    else:
        print(color("No changes detected on each file content!", 'green'))

def show_tree(path):
    print("Root Directory:")
    
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        indent = "│   " * level
        print(f"{indent}📁 {os.path.basename(root)}/")
        
        sub_indent = "│   " * (level + 1)
        for file in files: 
            print(f"{sub_indent}📄 {file}")

def main():
    print("Simple File Integrity Monitor [Mart Eugen Gevero]")
    print("*" * 50)
    
    # Option selection
    if len(sys.argv) < 3:
        print("Usage: python FIM.py <path> <option> [hash_algorithm]")
        print("e.g: python FIM.py ./root --baseline sha256")
        print("Options:")
        print("  --baseline [sha1|sha256|sha512]  # Create initial snapshot (default: sha1)")
        print("  --check [sha1|sha256|sha512]     # Check for changes (default: sha1)")
        print("  --tree                           # Show directory tree")
        print("  --info                           # Show baseline information")
        return
    
    # Get path and option from command line
    path = sys.argv[1]
    option = sys.argv[2]
    algorithm = get_hash_algorithm()
    
    # Validate hash algorithm
    if algorithm not in ['sha1', 'sha256', 'sha512']:
        print(f"Error: Invalid hash algorithm '{algorithm}'")
        print("Valid algorithms: sha1, sha256, sha512")
        return
    
    # Check if path exists
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist!")
        return
    
    # Execute based on option
    if option == '--baseline':
        create_baseline(path, algorithm)
    elif option == '--check':
        check_integrity(path, algorithm)
    elif option == '--tree':
        show_tree(path)
    elif option == '--info':
        baseline = load_baseline()
        if baseline:
            print(color("Baseline Information:", 'cyan'))
            print(f"  Hash Algorithm: {baseline['metadata']['hash_algorithm'].upper()}")
            print(f"  Total Files: {len(baseline['files'])}")
            if 'created_at' in baseline['metadata']:
                print(f"  Created: {baseline['metadata']['created_at']}")
        else:
            print(color("No baseline found!", 'red'))
    else:
        print(f"Error: Unknown option '{option}'")
        print("Valid options: --baseline, --check, --tree, --info")

if __name__ == "__main__":
    main()