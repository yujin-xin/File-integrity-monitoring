import hashlib
import os
import json
from colorama import Fore, Style, init
import sys
import time

init()

def hash_file(filename, algorithm='sha1'):
    """Hash a file - same as your original function"""
    hash_obj = hashlib.new(algorithm)

    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()
 

def color(text, textColor):
    colors = {
        'green': Fore.GREEN,
        'red': Fore.RED,
        'yellow': Fore.YELLOW
    }
    return f"{colors.get(textColor)}{text}{Style.RESET_ALL}"

def create_baseline(path):
    """Create initial snapshot of all files"""

    print("[Creating baseline snapshot...]")
    baseline = {}
    
    for root, dirs, files in os.walk(path):
            
        for file in files:
                
            filepath = os.path.join(root, file)
            
            # Get file info

            file_hash = hash_file(filepath)
            file_size = os.path.getsize(filepath)
            file_mtime = os.path.getmtime(filepath)
            
            if file_hash:  # Only add if hash succeeded
                baseline[filepath] = {
                    'hash': file_hash,
                    'size': file_size,
                    'mtime': file_mtime
                }
                print(f"   📄 {file} - recorded")

    
    # Save baseline to file
    with open('baseline.json', 'w') as f:
        json.dump(baseline, f, indent=2)
    
    print(f"Baseline created! {len(baseline)} files recorded")
    return baseline

def load_baseline():
    """Load baseline from file"""
    try:
        with open('baseline.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Note: No baseline found! Run with --baseline first")
        return None

def check_integrity(path):
    """Check files against baseline - the smart way!"""
    print("Checking file integrity...")
    
    prev_baseline = load_baseline()
    if not prev_baseline:
        return
    
    changes = []
    
    for root, dirs, files in os.walk(path):
            
        for file in files:
            

            filepath = os.path.join(root, file)
            if filepath not in prev_baseline:
                print(f"{filepath} has been removed")
            
            try:
                current_size = os.path.getsize(filepath)
                current_mtime = os.path.getmtime(filepath)
                
                if filepath in prev_baseline:
                    old_info = prev_baseline[filepath]

                    # Fast check: First check size and time (super fast!)
                    if (current_size != old_info['size'] or 
                        current_mtime != old_info['mtime']):
                        
                        # Only hash if size/time changed
                        print(f"   📄 {file} - size/time changed, hashing...")
                        current_hash = hash_file(filepath)
                        
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
                        print(f"   📄 {file} - unchanged")
                else:
                    # New file
                    changes.append({
                        'file': filepath,
                        'status': 'new'
                    })
                    
            except:
                print(f"   {file} - error checking")
    
    # Show results
    if changes:
        print(f"\nFound {len(changes)} changes:")
        for change in changes:
            if change['status'] == 'modified':
                print(color(f"   MODIFIED: {change['file']}", 'yellow'))
                print(f"   Old: {change['old_hash']} -> New: {change['new_hash']}")
            elif change['status'] == 'new':
                print(color(f"   NEW: {change['file']}", 'yellow'))
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
        print("Usage: python FIM.py <path> <option>")
        print("e.g: python FIM.py ./root --baseline")
        print("Options:")
        print("  --baseline   # Create initial snapshot")
        print("  --check      # Check for changes")
        print("  --tree       # Show directory tree")
        return
    
    # Get path and option from command line
    path = sys.argv[1]
    option = sys.argv[2]
    
    # Check if path exists
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist!")
        return
    
    # Execute based on option
    if option == '--baseline':
        create_baseline(path)
    elif option == '--check':
        check_integrity(path)
    elif option == '--tree':
        show_tree(path)
    else:
        print(f"Error: Unknown option '{option}'")
        print("Valid options: --baseline, --check, --tree")

if __name__ == "__main__":
    main()


#The goal is Dapat naka loop siya na naka monitor
#Dili append ang text sa console
#Dapat ma record japun bisag na detele ang file (No AI debug) (line 95)