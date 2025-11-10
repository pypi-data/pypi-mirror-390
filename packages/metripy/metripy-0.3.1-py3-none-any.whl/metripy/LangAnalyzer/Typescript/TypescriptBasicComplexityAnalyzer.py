import re


class TypescriptBasicComplexityAnalzyer:
    def get_complexity(self, code: str, function_name: str) -> dict[str, int] | None:
        function_scope = self._extract_function(code, function_name)
        if not function_scope:
            return None
        (start_index, end_index, start_line, end_line) = function_scope
        function_code = code[start_index:end_index]

        complexity = self._determine_complexity(function_code)

        return {
            "start_line": start_line,
            "end_line": end_line,
            "complexity": complexity,
        }

    def _determine_complexity(self, function_code: str) -> int:
        complexity = 1

        # Keywords that increase complexity
        keywords = [
            r"\bif\b",
            r"\bfor\b",
            r"\bwhile\b",
            r"\bcase\b",
            r"\bcatch\b",
            r"\?\s*",
            r"\belse\s+if\b",
            r"\breturn\b.*\?",
            r"\bthrow\b.*\?",
            r"&&",
            r"\|\|",
        ]

        for keyword in keywords:
            matches = re.findall(keyword, function_code)
            complexity += len(matches)

        return complexity

    def _extract_function(
        self, code: str, function_name: str
    ) -> tuple[int, int, int, int] | None:
        # This pattern matches various JavaScript/TypeScript function declarations:
        # 1. Arrow functions:
        #    - With or without `export`
        #    - With or without `async`
        #    - With or without generics (`<T>`)
        #    - With or without return types (`: Type`)
        #    - With multiline or single-line parameters
        #    - Including curried arrow functions (arrow returning another arrow)
        # 2. Traditional functions:
        #    - With optional `export` and `async`
        # 3. Class methods:
        #    - With optional access modifiers (`public`, `private`, `protected`)
        #    - With optional `static` and `async`
        #    - With optional generics and return types
        # 4. Bare class methods (no modifiers)

        pattern = re.compile(
            rf"""
            (
                (export\s+)?(const|let|var)\s+{re.escape(function_name)}\s*
                (<[^>]*>)?\s*=\s*(async\s+)?\(\s*.*?\s*\)\s*
                (:\s*[^=]+)?\s*=>\s*
                (\s*\(\s*.*?\s*\)\s*=>)?\s*\{{?
            )
            |
            (
                (export\s+)?(async\s+)?function\s+{re.escape(function_name)}\s*
                \(\s*.*?\s*\)\s*\{{
            )
            |
            (
                (?:public|private|protected)?\s*
                (?:static\s+)?(?:async\s+)?{re.escape(function_name)}\s*
                (<[^>]+>)?\s*\(\s*.*?\s*\)\s*
                (:\s*[^\{{]+)?\s*\{{
            )
            |
            (
                {re.escape(function_name)}\s*\(\s*.*?\s*\)\s*\{{
            )
            """,
            re.MULTILINE | re.DOTALL | re.VERBOSE,
        )

        match = pattern.search(code)
        if not match:
            print(f"Function '{function_name}' not found.")
            return None

        start_index = match.start()
        start_line = code[:start_index].count("\n") + 1

        # Find the matching closing brace
        brace_count = 0
        i = match.end() - 1
        while i < len(code):
            if code[i] == "{":
                brace_count += 1
            elif code[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    end_index = i + 1
                    end_line = code[:end_index].count("\n") + 1
                    return (start_index, end_index, start_line, end_line)
            i += 1

        print(f"Function '{function_name}' seems to be incomplete or malformed.")
        return None
