import random
import nltk
from nltk.corpus import wordnet
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
import gensim.downloader

# --- Global Models (will be lazy-loaded) ---
glove_model = None
lemmatizer = WordNetLemmatizer()

# --- NLTK Data Management ---

def download_nltk_data():
    """
    Downloads all necessary NLTK data packages for the library to function.
    """
    print("autoINcorrect: Checking NLTK data...")
    packages = ['wordnet', 'averaged_perceptron_tagger', 'punkt']
    data_ready = True
    for package in packages:
        try:
            # A more robust check
            if package == 'punkt':
                 nltk.data.find(f"tokenizers/{package}")
            elif package == 'wordnet':
                nltk.data.find(f"corpora/{package}")
            elif package == 'averaged_perceptron_tagger':
                nltk.data.find(f"taggers/{package}")
        except LookupError:
            print(f"Downloading missing NLTK package: {package}...")
            nltk.download(package, quiet=True)
            data_ready = False
    
    if data_ready:
        print("autoINcorrect: NLTK data is ready.")
    else:
        print("autoINcorrect: All NLTK data has been downloaded.")

# --- Tier 1: "Fat Finger" Typographical Errors ---

# A dictionary mapping each key to its adjacent keys on a QWERTY keyboard
KEY_NEIGHBORS = {
    'q': ['w', 'a', 's','1'],
    'w': ['q', 'e', 'a', 's', 'd','2'],
    'e': ['w', 'r', 's', 'd', 'f','3'],
    'r': ['e', 't', 'd', 'f', 'g','4'],
    't': ['r', 'y', 'f', 'g', 'h','5'],
    'y': ['t', 'u', 'g', 'h', 'j','6'],
    'u': ['y', 'i', 'h', 'j', 'k','7'],
    'i': ['u', 'o', 'j', 'k', 'l','8'],
    'o': ['i', 'p', 'k', 'l','9'],
    'p': ['o', 'l','0'],
    'a': ['q', 'w', 's', 'z', 'x'],
    's': ['q', 'w', 'e', 'a', 'd', 'z', 'x', 'c'],
    'd': ['w', 'e', 'r', 's', 'f', 'x', 'c', 'v'],
    'f': ['e', 'r', 't', 'd', 'g', 'c', 'v', 'b'],
    'g': ['r', 't', 'y', 'f', 'h', 'v', 'b', 'n'],
    'h': ['t', 'y', 'u', 'g', 'j', 'b', 'n', 'm'],
    'j': ['y', 'u', 'i', 'h', 'k', 'n', 'm'],
    'k': ['u', 'i', 'o', 'j', 'l', 'm'],
    'l': ['i', 'o', 'p', 'k'],
    'z': ['a', 's', 'x'],
    'x': ['a', 's', 'd', 'z', 'c'],
    'c': ['s', 'd', 'f', 'x', 'v'],
    'v': ['d', 'f', 'g', 'c', 'b'],
    'b': ['f', 'g', 'h', 'v', 'n'],
    'n': ['g', 'h', 'j', 'b', 'm'],
    'm': ['h', 'j', 'k', 'n'],
}

def adjacent_swap(word):
  """
  Replaces a random character in a word with a keyboard-adjacent character.
  """
  if len(word) < 1:
    return word

  char_index = random.randint(0, len(word) - 1)
  char_to_swap = word[char_index].lower() 

  if char_to_swap in KEY_NEIGHBORS:
    neighbor = random.choice(KEY_NEIGHBORS[char_to_swap])
    
    if word[char_index].isupper():
        neighbor = neighbor.upper()
        
    new_word = word[:char_index] + neighbor + word[char_index + 1:]
    return new_word
  
  return word

def transpose(word):
  """
  Swaps two random adjacent characters in a word.
  """
  if len(word) < 2:
    return word

  char_index = random.randint(0, len(word) - 2)
  
  new_word = (
      word[:char_index] +
      word[char_index + 1] +
      word[char_index] +
      word[char_index + 2:]
  )
  
  return new_word

def delete_char(word):
  """
  Deletes a random character from a word.
  """
  if len(word) < 2:
    return word

  char_index = random.randint(0, len(word) - 1)
  new_word = word[:char_index] + word[char_index + 1:]
  
  return new_word

def insert_char(word):
  """
  Inserts a random keyboard-adjacent character into a word.
  """
  if len(word) < 1:
    return word
    
  insert_index = random.randint(0, len(word) - 1)
  char_to_neighbor = word[insert_index].lower()

  if char_to_neighbor in KEY_NEIGHBORS:
    neighbor = random.choice(KEY_NEIGHBORS[char_to_neighbor])

    if word[insert_index].isupper():
        neighbor = neighbor.upper()
        
    new_word = word[:insert_index + 1] + neighbor + word[insert_index + 1:]
    return new_word

  return word

def run_fat_finger_module(word):
  """
  Selects one of the four typographical error functions based on
  a weighted probability and applies it to the given word.
  """
  error_functions = [
      adjacent_swap,
      transpose,
      delete_char,
      insert_char
  ]

  # [swap, transpose, delete, insert]
  weights = [0.4, 0.3, 0.2, 0.1]
  chosen_function = random.choices(error_functions, weights=weights, k=1)[0]

  # Call the chosen function with the word
  return chosen_function(word)

# --- Tier 2: "Brain Fart" Morphological/Homophone Errors ---

HOMOPHONES = {
    'group_1': {'their', 'there', 'they\'re'},
    'group_2': {'your', 'you\'re'},
    'group_3': {'its', 'it\'s'},
    'group_4': {'to', 'too', 'two'},
    'group_5': {'affect', 'effect'},
    'group_6': {'weather', 'whether'},
    'group_7': {'peace', 'piece'},
    'group_8': {'break', 'brake'},
    'group_9': {'buy', 'by', 'bye'},
}

HOMOPHONE_MAP = {}
for group_set in HOMOPHONES.values():
    for word in group_set:
        replacements = group_set - {word}
        HOMOPHONE_MAP[word] = list(replacements)


def replace_homophone(word):
  """
  Replaces a word with a random homophone, if one is found.
  Preserves the original capitalization.
  """
  word_lower = word.lower()

  if word_lower in HOMOPHONE_MAP:
    replacements = HOMOPHONE_MAP[word_lower]
    new_word = random.choice(replacements)

    if word.isupper():
      return new_word.upper()
    elif word.istitle(): 
      return new_word.capitalize()
    else:
      return new_word
      
  return word

def get_wordnet_pos(treebank_tag):
    """
    Converts NLTK's POS tag to a tag WordNet understands.
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN # Default to noun

def replace_morphological(word, pos_tag):
    """
    Replaces a word with a related word.
    accepts a pos_tag to find the right lemma.
    """
    wordnet_pos = get_wordnet_pos(pos_tag)

    synsets = wordnet.synsets(word, pos=wordnet_pos)
    if not synsets:
        return word

    related_lemmas = set()
    for syn in synsets:
        for lemma in syn.lemmas():
            related_lemmas.add(lemma.name())

    original_lower = word.lower()
    replacements = [
        lemma for lemma in related_lemmas 
        if lemma.lower() != original_lower and '_' not in lemma
    ]

    if replacements:
        new_word = random.choice(replacements)
        if word.isupper():
            return new_word.upper()
        elif word.istitle():
            return new_word.capitalize()
        else:
            return new_word
            
    return word

def run_brain_fart_module(word, pos_tag):
    """
    Selects one of the two cognitive error functions.
    """
    error_functions = [
        replace_homophone,
        replace_morphological 
    ]
    # You had [0.7, 0.3] in your code, so I'll keep that.
    weights = [0.7, 0.3] 
    
    chosen_function = random.choices(error_functions, weights=weights, k=1)[0]
    
    if chosen_function == replace_morphological:
        return chosen_function(word, pos_tag) # Pass the tag
    else:
        return chosen_function(word) # Homophone doesn't need it

# --- Tier 3: "Malapropism" Semantic Errors ---

def _load_glove_model():
    """
    Internal function to lazy-load the GloVe model.
    This ensures the model is only loaded when needed.
    """
    global glove_model
    if glove_model is None:
        print("autoINcorrect: Loading GloVe model (glove-wiki-gigaword-100)...")
        print("This may take a minute and requires internet.")
        try:
            glove_model = gensim.downloader.load('glove-wiki-gigaword-100')
            print("autoINcorrect: GloVe model loaded successfully.")
        except Exception as e:
            print(f"Error loading GloVe model: {e}")
            print("The 'malapropism' module will be disabled.")
            glove_model = {} # Set to empty dict to prevent re-tries
    return glove_model

def replace_semantic_neighbor(word, pos_tag):
    """
    Replaces a word with a semantically similar, root-sharing word.
    NOW ACCEPTS a pos_tag to find the right lemma.
    """
    # 1. Ensure model is loaded
    model = _load_glove_model()
    if not model: # If loading failed
        return word

    word_lower = word.lower()
    
    # 2. Convert tag and get the *correct* lemma.
    wordnet_pos = get_wordnet_pos(pos_tag)
    lemma = lemmatizer.lemmatize(word_lower, pos=wordnet_pos)

    # 3. Check if the lemma is in our model
    if lemma not in model:
        return word 

    try:
        # 4. Get neighbors of the LEMMA
        similar_words = model.most_similar(lemma, topn=10)
        
        # 5. Filter
        replacements = []
        for w_tuple in similar_words:
            w = w_tuple[0].lower() # Neighbor word
            if w.startswith(lemma) and w != word_lower:
                replacements.append(w)
        
        if replacements:
            # 6. Pick one and preserve case
            new_word = random.choice(replacements)
            
            if word.isupper():
                return new_word.upper()
            elif word.istitle():
                return new_word.capitalize()
            else:
                return new_word

        return word

    except Exception as e:
        # print(f"Error in replace_semantic_neighbor: {e}") # for debugging
        return word

def run_malapropism_module(word, pos_tag):
    """
    Selects one of the semantic error functions.
    """
    # Just call our final function and pass the tag
    return replace_semantic_neighbor(word, pos_tag)


# --- Format Corruption Module (Punctuation & Case) ---

PUNCTUATION_MARKS = {'.', ',', '!', '?', ';', ':'}
REPLACEMENT_PUNCTUATION = [',', '!', '?', ';'] 

def corrupt_format(text, 
                   add_rate=0.1, 
                   replace_rate=0.3, 
                   remove_rate=0.6, 
                   case_corruption_prob=0.5):
    """
    A standalone function to corrupt *both* punctuation AND case in a text.
    """

    words = word_tokenize(text)
    corrupted_words = []

    for word in words:
        if word in PUNCTUATION_MARKS:
            if random.random() < remove_rate:
                continue 
            elif random.random() < replace_rate:
                new_punct = random.choice(REPLACEMENT_PUNCTUATION)
                while new_punct == word: 
                    new_punct = random.choice(REPLACEMENT_PUNCTUATION)
                corrupted_words.append(new_punct)
            else:
                corrupted_words.append(word)
        else:
            # Apply Case Corruption
            new_chars = [
                char.lower() if char.isupper() and random.random() < case_corruption_prob else char
                for char in word
            ]
            corrupted_word = "".join(new_chars)
            
            # Append the (possibly case-corrupted) word
            corrupted_words.append(corrupted_word)

            # Apply Punctuation Addition
            if random.random() < add_rate:
                corrupted_words.append(random.choice(REPLACEMENT_PUNCTUATION))

    detokenizer = TreebankWordDetokenizer()
    final_text = detokenizer.detokenize(corrupted_words)

    return final_text


# --- Main Wrapper Functions ---

# Default distribution for word errors
DEFAULT_DISTRIBUTION = {
    'fat_finger': 0.4, 
    'brain_fart': 0.3, 
    'malapropism': 0.3 
}

def word_error(text, error_rate=0.15, distribution=None):
    """
    Intentionally introduces human-like errors into a text string.
    THIS VERSION ONLY AFFECTS WORDS, NOT PUNCTUATION.
    """
    if distribution is None:
        distribution = DEFAULT_DISTRIBUTION

    module_names = list(distribution.keys())
    module_weights = list(distribution.values())

    words = word_tokenize(text)
    tagged_words = pos_tag(words)

    corrupted_words = []

    for word, tag in tagged_words:
        # Skip punctuation
        if not word.isalnum():
            corrupted_words.append(word)
            continue 

        # Decide *if* we should apply an error
        if random.random() < error_rate:
            chosen_module = random.choices(module_names, weights=module_weights, k=1)[0]
            
            if chosen_module == 'fat_finger':
                corrupted_word = run_fat_finger_module(word)
            elif chosen_module == 'brain_fart':
                corrupted_word = run_brain_fart_module(word, tag)
            elif chosen_module == 'malapropism':
                corrupted_word = run_malapropism_module(word, tag)
            else:
                corrupted_word = word # Failsafe
                
            corrupted_words.append(corrupted_word)
        else:
            corrupted_words.append(word)

    detokenizer = TreebankWordDetokenizer()
    final_text = detokenizer.detokenize(corrupted_words)

    return final_text

def auto_incorrect(input_text,
                   # Parameters for word_error
                   error_rate=0.15,
                   distribution=None,

                   # Parameters for corrupt_format
                   add_rate=0.1,
                   replace_rate=0.3,
                   remove_rate=0.3,
                   case_corruption_prob=0.5):
  """
  Runs the input text through the full corruption chain.
  Allows tweaking all parameters or using the defaults.

  :param input_text: The string to corrupt.
  :param error_rate: (from word_error) Probability of corrupting a word.
  :param distribution: (from word_error) Dict of word error weights.
  :param add_rate: (from corrupt_format) Probability of adding punctuation.
  :param replace_rate: (from corrupt_format) Probability of replacing punctuation.
  :param remove_rate: (from corrupt_format) Probability of removing punctuation.
  :param case_corruption_prob: (from corrupt_format) Probability of flipping caps.
  """

  # Step 1: Apply word errors, passing the user's (or default) settings
  text_with_word_errors = word_error(
      input_text,
      error_rate=error_rate,
      distribution=distribution
  )

  # Step 2: Apply punctuation errors, passing the user's (or default) settings
  final_corrupted_text = corrupt_format(
      text_with_word_errors,
      add_rate=add_rate,
      replace_rate=replace_rate,
      remove_rate=remove_rate,
      case_corruption_prob=case_corruption_prob
  )

  return final_corrupted_text

# --- Example Usage (if run as a script) ---
if __name__ == "__main__":
    
    # Download NLTK data on first run
    download_nltk_data()
    
    my_text = "I am running a test on my banking application for its creative standards. It's a beautiful day to see if your function works correctly."
    
    print(f"\nOriginal Text:\n{my_text}\n")
    
    # --- Example 1: Calling with all default settings ---
    default_output = auto_incorrect(my_text)
    print(f"Fully Corrupted (Default Settings):\n{default_output}\n")
    
    # --- Example 2: Calling with custom, tweaked settings ---
    custom_distribution = {
        'fat_finger': 1.0,
        'brain_fart': 0.0,
        'malapropism': 0.0
    }
    
    tweaked_output = auto_incorrect(
        my_text,
        error_rate=0.3,
        distribution=custom_distribution,
        add_rate=0.1,
        remove_rate=0.6,
        replace_rate=0.3,
        case_corruption_prob=0.5 
    )
    
    print(f"Fully Corrupted (Aggressive Tweaked Settings):\n{tweaked_output}")
