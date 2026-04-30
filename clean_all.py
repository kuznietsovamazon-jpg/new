import os

def clean_files():
    target_files = ['app.py', 'database.py', 'keepa_client.py', 'ai_analyst.py']
    junk_string = "// la l'en_"
    
    for filename in target_files:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if junk_string in content:
                print(f"Cleaning {filename}...")
                new_content = content.replace(junk_string, "")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            else:
                print(f"{filename} is already clean.")

if __name__ == "__main__":
    clean_files()
