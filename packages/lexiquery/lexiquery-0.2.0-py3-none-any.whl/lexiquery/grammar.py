Boolean_Operators = {'AND', 'OR', 'NOT', 'XOR'}
Positional_Operators = {'NEAR', 'BEF', 'AFT'}
Match_Operators = {'ONLY', 'LIKE', 'STR', 'END', '*'}
Membership_Operators = {'IN', 'INOF'}
Length_Operators = {'LEN', 'SIZE'}

RESERVED_WORD = Boolean_Operators | Positional_Operators | Match_Operators | Membership_Operators | Length_Operators
NUMBER_TAG = '/'

GRAMMAR_ERROR = {
    'BO1': 'Boolean operators AND or OR must be surrounded by two expressions.',
    'BO2': 'Boolean operator NOT must be the first token in the subexpression.',
    'BO3': "Can't have subexpression before boolean operator NOT.",
    'BO4': 'Boolean operator NOT must be followed by an expression.',
    'BO5': 'Parentheses must wrap a complete subexpression and close properly.',
    'MO1': "Can't have expression before match operators (ONLY, LIKE, STR, END, '*').",
    'MO2': "The match operators (ONLY, LIKE, STR, END, '*') must be the only token in the minimal expression.",
    'PP1': 'The position operators (BEF, AFT, NEAR) must be surrounded by two minimal or wildcard expressions.',
    'PP2': 'Positional distance spec must be a positive integer, a range MIN-MAX, or * for unlimited distance.',
    'SO1': 'Set operators (IN, INOF) must directly follow a positional expression.',
    'LO1': 'Length operators (LEN, SIZE) must include an upper bound (/N) or range (/M-N).',
}
