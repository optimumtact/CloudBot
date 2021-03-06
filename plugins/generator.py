import json
import random
import re
import asyncio
import os

from cloudbot import hook

tense_map = {"root" : 0, "past" : 1, "present" : 2}
def lookup_verb(path, vocab):
    if not len(path) == 3:
        return 'The path length was not valid for a verb lookup'
    item = path[1]
    #figure out what index holds the tense we want (this data is laid out strangely if you ask me)
    tense_index = tense_map[path[2]]
    #pick a random verb (comes in a list with 3 tenses)
    choice = random.choice(vocab['verb'][item])
    #now get the tensed item from the list
    return choice[tense_index]

def lookup_noun(path, vocab):
    if not len(path) == 2:
        return 'Path length not valid for noun lookup'
    item = path[1]
    #pick random choice from nouns for given key
    return random.choice(vocab['noun'][item])

def lookup_simile(path, vocab):
    if not len(path) == 2:
        return 'Path length not valid for simile lookup'
    item = path[1]
    #pick random choice from nouns for given key
    return random.choice(vocab['simile'][item])

type_map = {"verb" : lookup_verb, "simile" : lookup_simile, "noun" : lookup_noun}
def lookup_replacement(path, vocab):
    type = path[0]
    #get parsing function for this type
    func = type_map[type]
    return func(path, vocab)
        
def parse_sentence(sentence, vocab):
    '''
    Parse sentence and generate final based on the vocabulary
    '''
    #find the first item to replace
    start_pos = sentence.find('[') 
    while start_pos > -1:
        #find first ] after the [
        end_pos = sentence.find(']', start_pos)
        #cut marker out (does not cut out ] or [)
        marker = sentence[start_pos+1:end_pos]
        #split to find appropriate lookup path
        marker_path = marker.split('-')
        replacement = lookup_replacement(marker_path, vocab)
        #slice in replacement
        sentence = sentence[:start_pos] + replacement + sentence[end_pos+1:]
        #find next [ (we start from start_pos to speed lookup slightly)
        start_pos = sentence.find('[', start_pos)
    return sentence

def generate_sentences(num):
        count = 0
        finals = []
        while len(finals) < num:
            sentence = random.choice(sentences)
            finals.append(parse_sentence(sentence, vocab))
        return finals



nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[\{\}]*$", re.I)


def is_valid(target):
    """ Checks if a string is a valid IRC nick. """
    if nick_re.match(target):
        return True
    else:
        return False


def is_self(conn, target):
    """ Checks if a string is "****self" or contains conn.name. """
    if re.search("(^..?.?.?self|{})".format(re.escape(conn.nick)), target, re.I):
        return True
    else:
        return False

@hook.on_start()
def load_vocab(bot):
    global vocab, sentences
    with open(os.path.join(bot.data_dir, 'sentences.json')) as f:
        sentences = json.load(f)
    with open(os.path.join(bot.data_dir, 'vocabulary.json')) as f:
        vocab = json.load(f)

@asyncio.coroutine
@hook.command
def erp(text, conn, nick, message):
    """<user> - badly erps with <user>"""
    target = text.strip()

    if not is_valid(target):
        return "I can't attack that."

    if is_self(conn, target):
        # user is trying to make the bot attack itself!
        target = nick

    # act out the message
    erp = " ".join(generate_sentences(1))
    phrase = "{user}: {erp}"
    message(phrase.format(user=target, erp = erp))
