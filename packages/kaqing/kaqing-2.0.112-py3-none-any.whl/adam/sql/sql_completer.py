from typing import Callable

import sqlparse
from sqlparse.sql import Statement, Token

from adam.sql.term_completer import TermCompleter
from adam.utils_repl.automata_completer import AutomataCompleter
from adam.sql.sql_state_machine import AthenaStateMachine, CqlStateMachine, SqlStateMachine
from adam.utils_repl.state_machine import State

__all__ = [
    "SqlCompleter",
]

def default_columns(_: list[str]):
    return 'id,x.,y.,z.'.split(',')

class SqlCompleter(AutomataCompleter[Token]):
    def tokens(self, text: str) -> list[Token]:
        tokens = []

        stmts = sqlparse.parse(text)
        if not stmts:
            tokens = []
        else:
            statement: Statement = stmts[0]
            tokens = statement.tokens

        return tokens

    def __init__(self,
                 tables: Callable[[], list[str]],
                 dml: str = None,
                 columns: Callable[[list[str]], list[str]] = default_columns,
                 partition_columns: Callable[[list[str]], list[str]] = lambda x: [],
                 table_props: Callable[[], dict[str,list[str]]] = lambda: [],
                 variant = 'sql',
                 debug = False):
        machine = SqlStateMachine(debug=debug)
        if variant == 'cql':
            machine = CqlStateMachine(debug=debug)
        elif variant == 'athena':
            machine = AthenaStateMachine(debug=debug)
        super().__init__(machine, dml, debug)

        self.tables = tables
        self.columns = columns
        self.partition_columns = partition_columns
        self.table_props = table_props
        self.variant = variant
        self.debug = debug

    def suggestions_completer(self, state: State, suggestions: str) -> list[str]:
        if not suggestions:
            return None

        terms = []
        for suggestion in suggestions.split(','):
            terms.extend(self._terms(state, suggestion))

        return TermCompleter(terms)

    def _terms(self, state: State, word: str) -> list[str]:
        terms = []

        if word == 'tables':
            terms.extend(self.tables())
        elif word == '`tables`':
            terms.append('tables')
        elif word == 'columns':
            terms.extend(self.columns([]))
        elif word == 'partition-columns':
            terms.extend(self.partition_columns([]))
        elif word == 'table-props':
            terms.extend(self.table_props().keys())
        elif word == 'table-prop-values':
            if 'last_name' in state.context and state.context['last_name']:
                terms.extend(self.table_props()[state.context['last_name']])
        elif word == 'single':
            terms.append("'")
        elif word == 'comma':
            terms.append(",")
        else:
            terms.append(word)

        return terms

    def completions_for_nesting(self):
        return {
            word : SqlCompleter(self.tables, word, columns=self.columns, partition_columns=self.partition_columns,
                                table_props=self.table_props, variant=self.variant)
            for word in self.machine.suggestions[''].strip(' ').split(',')
        }