import re
import os
import matplotlib.pyplot as plt
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
    match = re.match(r"^{(.*)}$", variant_string)
    if match:
        variants = match.group(1).split(',')
        return variants
    return [variant_string]

# Funkce pro zpracování souboru .cat a sběr statistik délky slov
def process_cat_file(cat_file, affix_file, output_file, stats, length_stats, all_generated_words):
    prefix_rules, suffix_rules = load_affix_rules(affix_file)
    words_set = set()
    input_count = 0
    output_count = 0

    with open(cat_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            words = line.split()  # Rozdělení slov na více tvarů
            for word in words:
                if '/' in word:
                    input_count += 1
                    base_word, affix_flags = word.split('/', 1)
                    base_word_variants = [base_word]
                    expanded_words = []
                    for word_variant in base_word_variants:
                        expanded_words.append(expand_variants(word_variant))
                    all_combinations = set(map(''.join, product(*expanded_words)))
                    for variant in all_combinations:
                        suffix_generated_words = apply_suffix_rules(variant, affix_flags, suffix_rules)
                        prefix_generated_words = apply_prefix_rules(variant, affix_flags, prefix_rules)
                        words_set.update(suffix_generated_words)
                        words_set.update(prefix_generated_words)

    output_count = len(words_set)
    stats.append((cat_file.split('/')[-1], input_count, output_count))
    all_generated_words.update(words_set)

    # Výpočet délky slov pro každou kategorii
    word_lengths = [len(word) for word in words_set]
    if word_lengths:
        shortest_word = min(word_lengths)
        longest_word = max(word_lengths)
        avg_length = sum(word_lengths) / len(word_lengths)
    else:
        shortest_word = longest_word = avg_length = 0

    length_stats.append((cat_file.split('/')[-1], shortest_word, longest_word, avg_length, input_count, output_count))

    if words_set:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("\n".join(sorted(words_set)))
        print(f"✅ Uloženo: {output_file}")
    else:
        print("⚠️ Žádná slova nebyla vygenerována.")

    return stats, length_stats, all_generated_words

# Funkce pro zpracování všech .cat souborů a generování tabulky a grafu pro analýzu délky slov
def process_all_cat_files():
    cat_files = [
        "cat/hovor.cat",  # Příklad souboru pro hovorová slova
        "cat/cislovk.cat"  # Příklad souboru pro číslovky
        # Přidejte další soubory, jak je uvedeno ve vašem zadání
    ]
    affix_file = "cs_affix.dat"  # Afixová pravidla
    stats = []
    length_stats = []
    all_generated_words = set()

    for cat_file in cat_files:
        output_file = f"out/{cat_file.split('/')[-1].replace('.cat', '.txt')}"
        stats, length_stats, all_generated_words = process_cat_file(cat_file, affix_file, output_file, stats, length_stats, all_generated_words)

    # Celkový počet unikátních vygenerovaných slov
    total_unique_words = len(all_generated_words)
    print(f"Celkový počet unikátních vygenerovaných slov: {total_unique_words}")

    # Vytvoření tabulky pro délky slov
    print("\nTabulka délky slov:")
    print(f"{'Kategorie':<20} {'Vstupní počet':<15} {'Výstupní počet':<15} {'Nejkratší slovo':<20} {'Nejdelší slovo':<20} {'Průměrná délka':<20}")
    for category, shortest, longest, avg_length, input_count, output_count in length_stats:
        print(f"{category:<20} {input_count:<15} {output_count:<15} {shortest:<20} {longest:<20} {avg_length:<20.2f}")

    # Vytvoření grafu pro délku slov
    categories = [x[0] for x in length_stats]
    input_counts = [x[4] for x in length_stats]
    output_counts = [x[5] for x in length_stats]
    shortest_lengths = [x[1] for x in length_stats]
    longest_lengths = [x[2] for x in length_stats]
    avg_lengths = [x[3] for x in length_stats]

    fig, ax = plt.subplots(figsize=(12, 8))

    width = 0.25  # Šířka sloupce
    x = range(len(categories))

    ax.bar(x, input_counts, width, label='Vstupní počet', color='blue')
    ax.bar([i + width for i in x], output_counts, width, label='Výstupní počet', color='orange')

    ax.set_xlabel('Kategorie')
    ax.set_ylabel('Počet slov')
    ax.set_title('Počet vstupních a výstupních slov pro každou kategorii')
    ax.set_xticks([i + width / 2 for i in x])
    ax.set_xticklabels(categories, rotation=90)
    ax.legend()

    plt.tight_layout()
    plt.show()

    # Sloupcový graf pro délky
    fig, ax = plt.subplots(figsize=(12, 8))

    ax.bar(x, shortest_lengths, width, label='Nejkratší délka', color='green')
    ax.bar([i + width for i in x], longest_lengths, width, label='Nejdelší délka', color='red')
    ax.bar([i + width*2 for i in x], avg_lengths, width, label='Průměrná délka', color='blue')

    ax.set_xlabel('Kategorie')
    ax.set_ylabel('Délka slov')
    ax.set_title('Analýza délky slov pro každou kategorii')
    ax.set_xticks([i + width for i in x])
    ax.set_xticklabels(categories, rotation=90)
    ax.legend()

    plt.tight_layout()
    plt.show()

# Spuštění zpracování všech souborů pro analýzu délky slov
process_all_cat_files()
