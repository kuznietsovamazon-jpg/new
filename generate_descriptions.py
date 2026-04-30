import pandas as pd
import os
import re
import random
from nltk.tokenize import sent_tokenize
from nltk.corpus import wordnet
import nltk

# Ensure NLTK data is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

# --- Configuration ---
TARGET_DIR = r"C:\Users\User\Desktop\Description"
SKU_COL_CANDIDATES = ['Sku', 'sku', 'SKU', 'ASIN', 'Product ID', 'Item ID', 'Child ASIN', 'M-1800-BODY-PILLOWCASE-PARENT']
MAIN_DESC_COL_CANDIDATES = ['Description', 'Product Description', 'Item Description', 'Bullet Point 1', 'Feature 1', 'Title', 'Product Title', 'Luxury Iconic Body Pillow Cover ', 'Desccription']
NEW_DESC_COLS = ['Description1', 'Description2', 'Description3', 'Description4', 'Description5']
FORBIDDEN_WORDS = [
    'best', 'cheapest', 'guaranteed', 'amazing', 'incredible', 'fantastic', 'superb',
    'premium', 'luxury', 'free', 'sale', 'discount', 'deal', 'limited time', 'exclusive',
    '#1', 'top-rated', 'unbeatable', 'ultimate', 'revolutionary', 'state-of-the-art',
    'cutting-edge', 'miracle', 'magic', 'perfect', 'flawless', 'superior', 'highest quality',
    'phone number', 'address', 'email', 'website', 'url', 'link', 'free shipping', 'order here',
    'customers say', 'review', 'testimonial', 'leave a review', 'positive review', 'ad', 'advert',
    'promotional', 'time-sensitive', 'date', 'today only', 'FSA/HSA eligible', 'in stock',
    'new condition', 'price', 'available', 'buy now', 'shop now', 'click here', 'limited offer',
    'exclusive offer', 'get yours', 'order yours', 'act now', 'don\'t miss out', 'lowest price',
    'highest quality', 'best value', 'money-back guarantee', 'satisfaction guaranteed',
    'compare to', 'vs.', 'versus', 'similar to', 'like no other', 'unique', 'one of a kind',
    'patent pending', 'trademark', 'copyright', 'registered', 'all rights reserved',
    'contact us', 'call us', 'visit our website', 'follow us', 'social media', 'facebook',
    'instagram', 'twitter', 'youtube', 'pinterest', 'tiktok', 'snapchat', 'linkedin',
    'whatsapp', 'telegram', 'wechat', 'viber', 'skype', 'zoom', 'google meet', 'microsoft teams',
    'facetime', 'imessage', 'text us', 'message us', 'chat with us', 'email us', 'mail us',
    'send us', 'reach us', 'find us', 'locate us', 'our store', 'our brand', 'our company',
    'our product', 'our service', 'our team', 'our mission', 'our vision', 'our values',
    'our commitment', 'our promise', 'our guarantee', 'our policy', 'our terms', 'our conditions',
    'our privacy', 'our legal', 'our disclaimer', 'our copyright', 'our trademark', 'our patent',
    'our registered', 'our all rights reserved', 'our contact', 'our call', 'our visit',
    'our follow', 'our social', 'our facebook', 'our instagram', 'our twitter', 'our youtube',
    'our pinterest', 'our tiktok', 'our snapchat', 'our linkedin', 'our whatsapp', 'our telegram',
    'our wechat', 'our viber', 'our skype', 'our zoom', 'our google meet', 'our microsoft teams',
    'our facetime', 'our imessage', 'our text', 'our message', 'our chat', 'our email', 'our mail',
    'our send', 'our reach', 'our find', 'our locate'
]

# Regex patterns for prohibited content
PROHIBITED_PATTERNS = [
    re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'),  # Phone numbers (basic US format)
    re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),  # Email addresses
    re.compile(r'\b(?:https?://|www\.)\S+\b'),  # URLs
    re.compile(r'\$(?:\d{1,3}(?:,\d{3})*|\d+)(?:\.\d{2})?'), # Price patterns like $XX.XX or $X,XXX.XX
    re.compile(r'<\/?\w+[^>]*?>') # Basic HTML tags
]

# --- Helper Functions ---

def clean_text(text):
    """Removes extra spaces, newlines, and cleans up text."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_synonyms(word):
    """Returns a list of synonyms for a given word using WordNet."""
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace('_', ' '))
    return list(synonyms)

def filter_forbidden_content(text):
    """Filters out forbidden words and patterns from the text."""
    text_lower = text.lower()
    
    # Filter forbidden words
    for forbidden in FORBIDDEN_WORDS:
        text = re.sub(r'\b' + re.escape(forbidden) + r'\b', '', text, flags=re.IGNORECASE)
    
    # Filter prohibited patterns
    for pattern in PROHIBITED_PATTERNS:
        text = pattern.sub('', text)
        
    text = re.sub(r'\s+', ' ', text).strip() # Clean up extra spaces after removal
    return text

def generate_variations(main_description, num_variations=5):
    """
    Generates variations of the main description.
    
    IMPORTANT LIMITATIONS:
    - This function provides *syntactic* variations (rephrasing, sentence order)
      rather than deep *semantic* diversity.
    - It does NOT use an advanced AI model (like an LLM) for creative generation.
    - It attempts to preserve core product information by keeping numbers and
      capitalized words (potential product names) intact.
    - Amazon policy adherence is limited to filtering a basic list of forbidden words
      and regex patterns. A comprehensive check against all Amazon policies is
      beyond this function's scope.
    - Manual review of generated descriptions is CRUCIAL for full compliance and accuracy.
    """
    if not isinstance(main_description, str) or not main_description.strip():
        return [""] * num_variations

    cleaned_desc = clean_text(main_description)
    
    # Apply initial filtering for forbidden content
    cleaned_desc = filter_forbidden_content(cleaned_desc)

    sentences = sent_tokenize(cleaned_desc)
    
    variations = []
    for i in range(num_variations):
        current_variation_sentences = list(sentences) # Start with original sentences
        
        # Strategy 1: Sentence reordering (for variations 0, 1)
        if i % 2 == 0: # Even variations: shuffle sentences
            random.shuffle(current_variation_sentences)
        
        # Strategy 2: Simple synonym replacement (for variations 2, 3)
        # This is very basic and uses a small, hardcoded set of replacements
        # or WordNet for common words.
        if i % 2 == 1: # Odd variations: attempt synonym replacement
            temp_sentences = []
            for sentence in current_variation_sentences:
                words = sentence.split()
                new_words = []
                for word in words:
                    # Avoid replacing numbers or words that look like product codes (all caps)
                    if word.isdigit() or (word.isupper() and len(word) > 1):
                        new_words.append(word)
                        continue
                    
                    # Basic synonym replacement for common adjectives/verbs
                    lower_word = word.lower()
                    if lower_word == 'soft':
                        new_words.append(random.choice(['gentle', 'plush', 'smooth']))
                    elif lower_word == 'durable':
                        new_words.append(random.choice(['resilient', 'sturdy', 'long-lasting']))
                    elif lower_word == 'comfortable':
                        new_words.append(random.choice(['cozy', 'snug', 'pleasant']))
                    elif lower_word == 'easy':
                        new_words.append(random.choice(['simple', 'effortless', 'straightforward']))
                    elif lower_word == 'great':
                        new_words.append(random.choice(['excellent', 'superb', 'wonderful']))
                    else:
                        # Try WordNet for other words, but be cautious not to change meaning
                        syns = get_synonyms(lower_word)
                        if syns and len(syns) > 1 and random.random() < 0.3: # 30% chance to replace
                            new_words.append(random.choice(syns))
                        else:
                            new_words.append(word)
                temp_sentences.append(" ".join(new_words))
            current_variation_sentences = temp_sentences
            
        # Reconstruct the description
        variation_text = " ".join(current_variation_sentences)
        
        # Apply filtering for forbidden content again after generation
        variation_text = filter_forbidden_content(variation_text)
                
        variations.append(variation_text)
        
    # Ensure we always return num_variations, even if some are empty or identical
    while len(variations) < num_variations:
        variations.append(cleaned_desc) # Fallback to original if generation fails
        
    return variations[:num_variations]


# --- Main Processing ---
def process_excel_files():
    excel_files = [f for f in os.listdir(TARGET_DIR) if f.endswith('.xlsx') and not f.startswith('~$')]
    
    if not excel_files:
        print(f"No Excel files found in {TARGET_DIR}")
        return

    print(f"Found {len(excel_files)} Excel files in {TARGET_DIR}. Processing...")

    for filename in excel_files:
        file_path = os.path.join(TARGET_DIR, filename)
        print(f"\nProcessing file: {filename}")

        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

        # Identify SKU column
        sku_col = None
        for col_candidate in SKU_COL_CANDIDATES:
            if col_candidate in df.columns:
                sku_col = col_candidate
                break
        
        if sku_col is None:
            print(f"Warning: Could not find a suitable SKU column in {filename}. Skipping file.")
            continue
        
        # Identify Main Description column
        main_desc_col = None
        for col_candidate in MAIN_DESC_COL_CANDIDATES:
            if col_candidate in df.columns:
                main_desc_col = col_candidate
                break
        
        if main_desc_col is None:
            print(f"Warning: Could not find a suitable main description column in {filename}. Skipping file.")
            continue

        # Ensure new description columns exist and are of string type
        for new_col in NEW_DESC_COLS:
            if new_col not in df.columns:
                df[new_col] = ""
            df[new_col] = df[new_col].astype(str)

        # Process each row
        for index, row in df.iterrows():
            main_description = row[main_desc_col]
            
            if pd.isna(main_description) or not str(main_description).strip():
                # If main description is empty, fill new description columns with empty strings
                for new_col in NEW_DESC_COLS:
                    df.at[index, new_col] = ""
                continue

            variations = generate_variations(str(main_description), len(NEW_DESC_COLS))
            
            for i, new_col in enumerate(NEW_DESC_COLS):
                df.at[index, new_col] = variations[i]
        
        # Save the modified DataFrame back to the original file
        try:
            df.to_excel(file_path, index=False)
            print(f"Successfully processed and saved {filename}")
        except Exception as e:
            print(f"Error saving {filename}: {e}")

if __name__ == "__main__":
    print("Starting description generation script...")
    process_excel_files()
    print("Script finished.")