import re
from itertools import product

# Funkce pro načítání afixových pravidel
def load_affix_rules(affix_file):
    prefix_rules = {}
    suffix_rules = {}

    with open(affix_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # Přeskočit prázdné řádky nebo komentáře
            parts = line.split()
            if len(parts) < 3:
                continue  # Pokud řádek není platné pravidlo, přeskočte ho

            rule_type, flag, strip_chars, add_chars, *condition = parts

            if rule_type == 'PFX':  # Předpony
                if flag not in prefix_rules:
                    prefix_rules[flag] = []
                prefix_rules[flag].append((strip_chars, add_chars))
            elif rule_type == 'SFX':  # Přípony
                if flag not in suffix_rules:
                    suffix_rules[flag] = []
                suffix_rules[flag].append((strip_chars, add_chars))

    return prefix_rules, suffix_rules

# Funkce pro aplikaci přípon
def apply_suffix_rules(base_word, affix_flags, suffix_rules):
    generated_words = set()

    for flag in affix_flags:
        if flag in suffix_rules:
            for strip_chars, add_chars in suffix_rules[flag]:
                if base_word.endswith(strip_chars):
                    new_word = base_word[:-len(strip_chars)] + add_chars
                    generated_words.add(new_word)

    return generated_words

# Funkce pro aplikaci předpon
def apply_prefix_rules(base_word, affix_flags, prefix_rules):
    generated_words = set()

    for flag in affix_flags:
        if flag in prefix_rules:
            for strip_chars, add_chars in prefix_rules[flag]:
                if base_word.startswith(strip_chars):
                    new_word = add_chars + base_word[len(strip_chars):]
                    generated_words.add(new_word)

    return generated_words

# Funkce pro expanze variant v závorkách
def expand_variants(variant_string):
    # Zpracování variant ve formátu {a,b,c} na seznam kombinací
    match = re.match(r"^{(.*)}$", variant_string)
    if match:
        variants = match.group(1).split(',')
        return variants
    return [variant_string]

# Funkce pro zpracování souboru .cat
def process_cat_file(cat_file, affix_file, output_file):
    prefix_rules, suffix_rules = load_affix_rules(affix_file)
    words_set = set()

    with open(cat_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if '/' in line:
                base_word, affix_flags = line.split('/')
                base_word_variants = [base_word]  # Používáme základní slovo

                # Pokud je v základním slově expanze pro varianty, provedeme ji
                expanded_words = []
                for word_variant in base_word_variants:
                    expanded_words.append(expand_variants(word_variant))

                # Vygenerování všech kombinací variant
                all_combinations = set(map(''.join, product(*expanded_words)))

                # Pro každou kombinaci generuj varianty s předponami a příponami
                for variant in all_combinations:
                    # Generování variant podle přípon
                    suffix_generated_words = apply_suffix_rules(variant, affix_flags, suffix_rules)
                    # Generování variant podle předpon
                    prefix_generated_words = apply_prefix_rules(variant, affix_flags, prefix_rules)

                    # Spojení obou množin a přidání do výsledku
                    words_set.update(suffix_generated_words)
                    words_set.update(prefix_generated_words)

    # Uložení výsledků do souboru
    if words_set:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("\n".join(sorted(words_set)))
        print(f"✅ Uloženo: {output_file}")
    else:
        print("⚠️ Žádná slova nebyla vygenerována.")

# Testování pro konkrétní soubor
def process_all_cat_files():
    cat_files = [
        "cat/hovor.cat",  # Příklad souboru pro hovorová slova
        "cat/cislovk.cat"  # Příklad souboru pro číslovky
        # Přidejte další soubory, jak je uvedeno ve vašem zadání
    ]
    affix_file = "cs_affix.dat"  # Afixová pravidla
    for cat_file in cat_files:
        output_file = f"out/{cat_file.split('/')[-1].replace('.cat', '.txt')}"
        process_cat_file(cat_file, affix_file, output_file)

process_all_cat_files()
