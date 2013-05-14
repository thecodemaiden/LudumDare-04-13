from game_constants import *

alias_dir = {"forward": DIR_FORWARD, "ahead": DIR_FORWARD, "back": DIR_BACKWARD, "behind": DIR_BACKWARD, "left": DIR_LEFT, "right": DIR_RIGHT, "up": DIR_UP, "down": DIR_DOWN, "north": DIR_NORTH, "n": DIR_NORTH, "south": DIR_SOUTH, "s": DIR_SOUTH, "east": DIR_EAST, "e": DIR_EAST, "west": DIR_WEST, "w": DIR_WEST}

ignore_words = ["the", "to", "at", "and"]

commands = ["wait", "look", "get", "take", "drop", "leave", "use", "push", "pull", "examine", "open", "close", "smell", "go", "move", "turn", "face"]

# parser
PARSE_SUBJECTS = "subjects"
PARSE_ACTION = "action"
PARSE_SUGGEST = "suggestion"

PARSE_START = "start"
PARSE_DONE = "done"
PARSE_ERROR = "error"

ACTION_WAIT = "wait"
ACTION_LOOK = "describe"
ACTION_EXAMINE = "examine"
ACTION_TAKE = "take"
ACTION_DROP = "drop"
ACTION_TURN = "turn"
ACTION_OPEN = "open"
ACTION_CLOSE = "close"
ACTION_PUSH = "push"
ACTION_PULL = "pull"
ACTION_MOVE = "move"
ACTION_USE = "use"

PARSE_USE_NOUN = "LOOKUP_N"
PARSE_USE_DIR = "LOOKUP_D"
PARSE_USE_ARG = "<insert>" #use whatever we resolved the word as as a subject
PARSE_UNCHANGED = "keep" # if we want to keep an action or subject the same
PARSE_IGNORE = "ignore" #eat the word and continue in the same state

PARSE_DIR = "expecting direction"
PARSE_ITEM = "expecting item"
PARSE_LOOK = "look expression"
PARSE_MOVE = "going somewhere"
PARSE_TURN = "reorienting player"
PARSE_EAT = "eat" # consume everything else - don't error - not player eat!
PARSE_ANY = "fallback"


# {state: {input:(output,next_state)} 
transitions = {}
transitions[PARSE_START] = {PARSE_USE_DIR:((PARSE_USE_DIR, ACTION_MOVE), PARSE_DONE),
                            "wait":((None, ACTION_WAIT), PARSE_DONE),
                            "look":((ENV_APPEAR, ACTION_EXAMINE), PARSE_LOOK),
                            "get": ((PARSE_ERROR, ACTION_TAKE), PARSE_ITEM),
                            "take":((PARSE_ERROR, ACTION_TAKE), PARSE_ITEM),
                            "drop":((PARSE_ERROR, ACTION_DROP), PARSE_ITEM),
                            "leave":((PARSE_ERROR, ACTION_DROP), PARSE_ITEM),
                            "use":((PARSE_ERROR, ACTION_USE), PARSE_ITEM),
                            "push":((PARSE_ERROR, ACTION_PUSH), PARSE_ITEM),
                            "pull":((PARSE_ERROR, ACTION_PULL), PARSE_ITEM),
                            "examine":((None, ACTION_EXAMINE), PARSE_LOOK),
                            "open":((PARSE_ERROR, ACTION_OPEN), PARSE_ITEM),
                            "close":((PARSE_ERROR, ACTION_CLOSE), PARSE_ITEM),
                            "smell":((ENV_SMELL, ACTION_EXAMINE), PARSE_DONE),
                            "go":((PARSE_ERROR, ACTION_MOVE), PARSE_MOVE),
                            "move":((PARSE_ERROR, ACTION_MOVE), PARSE_MOVE),
                            "face":((PARSE_ERROR, ACTION_TURN), PARSE_TURN),
                            "turn":((PARSE_ERROR, ACTION_TURN), PARSE_TURN)}

transitions[PARSE_MOVE] = {PARSE_USE_DIR:((PARSE_USE_DIR, ACTION_MOVE), PARSE_DONE)}
transitions[PARSE_LOOK] = {PARSE_USE_DIR:((PARSE_USE_DIR, ACTION_EXAMINE), PARSE_DONE),
                           PARSE_USE_NOUN:((PARSE_USE_NOUN, ACTION_EXAMINE), PARSE_DONE)}
# make lists of items
transitions[PARSE_ITEM] = {PARSE_USE_NOUN:((PARSE_USE_NOUN, PARSE_UNCHANGED), PARSE_ITEM)}
transitions[PARSE_TURN] = {PARSE_USE_DIR:((PARSE_USE_DIR, ACTION_TURN), PARSE_DONE)}

transitions[PARSE_EAT] = {PARSE_ANY:((PARSE_UNCHANGED, PARSE_UNCHANGED), PARSE_EAT)}

class ParserFSM(object):
    
    def __init__(self):
        self.state = PARSE_START
        self.output = {PARSE_SUBJECTS:[], PARSE_ACTION:None, PARSE_SUGGEST:""}
        self.consumed = []

    def consume(self, word):
        if self.state == PARSE_ERROR:
            return
        next_state = self.state
        word = word.lower()
        if word not in ignore_words:
            parse_dict = transitions[self.state]
            keyword = word
            if word in alias_dir:
                keyword = PARSE_USE_DIR
            elif word in object_names:
                keyword = PARSE_USE_NOUN
            elif keyword not in commands:
                keyword = PARSE_ANY
            try:
                state_info = parse_dict[keyword]
                next_state = state_info[1]
                state_subj = state_info[0][0]
                state_action = state_info[0][1]
                #print state_info
                if (state_action != PARSE_UNCHANGED):
                    self.output[PARSE_ACTION] = state_action
                if (state_subj != PARSE_UNCHANGED):
                    if state_subj == PARSE_USE_DIR:
                        dir = alias_dir[word]
                        self.output[PARSE_SUBJECTS] = dir 
                    elif state_subj == PARSE_USE_NOUN:
                        if word in object_names:
                            subjs = self.output[PARSE_SUBJECTS]
                            if isinstance(subjs, list):
                                subjs.append(word)
                            else:
                                self.output[PARSE_SUBJECTS] = [word]
                    else:
                        self.output[PARSE_SUBJECTS] = (state_subj)
            except (KeyError, TypeError):
                self.state = PARSE_ERROR #straight to error state, don't do transition

        if self.state != PARSE_DONE and self.state != PARSE_ERROR:
            self.consumed.append(word)
            self.state = next_state
        else:
            # we were done but still had more to consume, or other error
            self.output[PARSE_SUGGEST] = " ".join(self.consumed)
            self.output[PARSE_SUBJECTS] = PARSE_ERROR

